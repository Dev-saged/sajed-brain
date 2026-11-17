#!/usr/bin/env python3
"""فيديو كلام ساجد ← نص ← ريل بهويته.

1) python3 talk.py transcribe my-video.mp4 work/        ← work/transcript.txt + words.json
2) اكتب talk.json (انظر talk.example.json) بعد قراءة transcript.txt فقط
3) python3 talk.py render talk.json out.mp4 [--preview]
"""
import argparse
import datetime
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FILLERS = {"يعني", "اممم", "امم", "ااه", "آآ", "ااا", "إيه", "ايه", "uh", "um", "umm", "emm"}
GAP = 0.6
PAD = 0.12
AUDIO = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
VIDEO = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30"]

spec = importlib.util.spec_from_file_location("render", ROOT / "templates" / "render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def transcribe(src: pathlib.Path, work: pathlib.Path, model: str, lang: str) -> None:
    from faster_whisper import WhisperModel

    work.mkdir(parents=True, exist_ok=True)
    wav = work / "voice.wav"
    # تنظيف خفيف للصوت قبل التفريغ
    ff("-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-af", "highpass=f=80,afftdn=nf=-25,loudnorm", str(wav))
    import wave
    import numpy as np

    # نمرّر الصوت مصفوفةً لتجنّب تعارض نسخ PyAV
    with wave.open(str(wav)) as f:
        audio = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
    m = WhisperModel(model, device="auto", compute_type="int8")
    segs, _ = m.transcribe(audio, language=lang, word_timestamps=True, vad_filter=True)
    words, lines = [], []
    for s in segs:
        lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
        words += [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for w in s.words or [] if w.word.strip()]
    (work / "words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    (work / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(work / "transcript.txt", f"({len(words)} كلمة)")


def auto_keep(words: list) -> list:
    """مقاطع الكلام بعد حذف الصمت الطويل والكلمات الحشو."""
    spans = []
    for w in words:
        if w["w"].strip("،.؟!,?") in FILLERS:
            continue
        s, e = max(0, w["s"] - PAD), w["e"] + PAD
        if spans and s - spans[-1][1] < GAP:
            spans[-1][1] = e
        else:
            spans.append([s, e])
    return spans


def retime(t: float, keep: list):
    """زمن المصدر ← زمن الفيديو بعد القص؛ None لو داخل جزء محذوف."""
    acc = 0.0
    for s, e in keep:
        if s <= t <= e:
            return acc + t - s
        acc += e - s
    return None


def plan(cfg: dict, base: pathlib.Path) -> dict:
    work = (base / cfg["work"]).resolve()
    words = json.loads((work / "words.json").read_text(encoding="utf-8"))
    keep = cfg.get("keep") or auto_keep(words)
    fixes = cfg.get("fixes", {})
    out = []
    for w in words:
        s, e = retime(w["s"], keep), retime(w["e"], keep)
        if s is None or e is None or w["w"].strip("،.؟!,?") in FILLERS:
            continue
        out.append({"w": fixes.get(w["w"], w["w"]), "s": round(s, 3), "e": round(e, 3)})
    pops = [{"at": retime(p["at"], keep), "text": p["text"]} for p in cfg.get("pops", [])]
    zooms = [(retime(a, keep), retime(b, keep)) for a, b in cfg.get("zooms", [])]
    return {
        "work": work,
        "keep": keep,
        "words": out,
        "pops": [p for p in pops if p["at"] is not None],
        "zooms": [z for z in zooms if None not in z],
        "duration": round(sum(e - s for s, e in keep), 3),
    }


def cut_source(src: pathlib.Path, keep: list, zooms: list, out: pathlib.Path) -> None:
    parts, labels = [], []
    for i, (s, e) in enumerate(keep):
        parts.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    z = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in zooms) or "0"
    # قصّ عمودي ثم دفعة زوم 12% في اللحظات المحددة
    fc = ";".join(parts) + f";{''.join(labels)}concat=n={len(keep)}:v=1:a=1[cv][ca];" \
        f"[cv]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920," \
        f"crop=w='iw/(1+0.12*gt({z},0))':h='ih/(1+0.12*gt({z},0))',scale=1080:1920,setsar=1[vo];" \
        f"[ca]highpass=f=80,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5[ao]"
    ff("-i", str(src), "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]", *VIDEO, *AUDIO, str(out))


def overlay_frames(page, data: dict, folder: pathlib.Path) -> None:
    page.add_init_script("window.__TALK = " + json.dumps(data, ensure_ascii=False))
    page.goto((HERE / "talk.html").as_uri())
    page.wait_for_function("window.__ready && document.fonts.status === 'loaded'")
    for i in range(int(data["duration"] * 30)):
        page.evaluate(f"window.__seek({i * 1000 / 30})")
        page.screenshot(path=str(folder / f"{i:05d}.png"), omit_background=True)


def with_silence(src: pathlib.Path, out: pathlib.Path) -> None:
    ff("-i", str(src), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
       "-map", "0:v", "-map", "1:a", "-c:v", "copy", *AUDIO, str(out))


def do_render(cfg_path: pathlib.Path, out: pathlib.Path, preview: bool) -> None:
    from playwright.sync_api import sync_playwright

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base = cfg_path.parent
    src = (base / cfg["source"]).resolve()
    p = plan(cfg, base)
    tokens = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    icons = json.loads((ROOT / "icons" / "platforms.json").read_text(encoding="utf-8"))
    hook = cfg["hook"]
    brand = {
        "tokens": tokens, "icons": icons,
        "content": {**hook, "demo": {}, "durations": {"hook": cfg.get("hook_seconds", 3), "outro": 4}},
        "assets": {"portrait": (ROOT / tokens["identity"]["portrait"]).as_uri(), "screenshot": None},
    }
    talk = {"tokens": tokens, "words": p["words"], "pops": p["pops"], "emphasis": cfg.get("emphasis", []), "duration": p["duration"]}

    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        br = pw.chromium.launch()
        vp = {"width": 1080, "height": 1920}
        if preview:
            pg = br.new_page(viewport=vp)
            pg.add_init_script("window.__TALK = " + json.dumps(talk, ensure_ascii=False))
            pg.goto((HERE / "talk.html").as_uri())
            pg.wait_for_function("window.__ready && document.fonts.status === 'loaded'")
            mid = p["words"][len(p["words"]) // 2]["s"] + 0.1 if p["words"] else 1
            pg.evaluate(f"window.__seek({mid * 1000})")
            pg.screenshot(path=str(out.with_suffix(".png")), omit_background=True)
            print(out.with_suffix(".png"), f"مدة الكلام بعد القص {p['duration']}ث من {len(p['keep'])} مقطع")
            br.close()
            return
        cut_source(src, p["keep"], p["zooms"], td / "cut.mp4")
        frames = td / "ov"
        frames.mkdir()
        overlay_frames(br.new_page(viewport=vp), talk, frames)
        ff("-i", str(td / "cut.mp4"), "-framerate", "30", "-i", str(frames / "%05d.png"),
           "-filter_complex", "[0:v][1:v]overlay=0:0:eof_action=pass[v]", "-map", "[v]", "-map", "0:a",
           *VIDEO, "-c:a", "copy", str(td / "talk.mp4"))
        seq = []
        for scene in ("hook", "outro") if cfg.get("outro", True) else ("hook",):
            pg = br.new_page(viewport=vp)
            pg.add_init_script("window.__BRAND = " + json.dumps(brand, ensure_ascii=False))
            render.film(pg, scene, td / f"{scene}-v.mp4", 30)
            with_silence(td / f"{scene}-v.mp4", td / f"{scene}.mp4")
            seq.append(td / f"{scene}.mp4")
        br.close()
        order = [seq[0], td / "talk.mp4", *seq[1:]]
        lst = td / "list.txt"
        lst.write_text("".join(f"file '{x}'\n" for x in order), encoding="utf-8")
        tmp = out.with_name(out.stem + ".part.mp4")
        ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(tmp))
        tmp.rename(out)
    print(out)
    if not cfg.get("no_archive"):
        print(archive(cfg_path, cfg, p, out))


def archive(cfg_path: pathlib.Path, cfg: dict, p: dict, video: pathlib.Path) -> pathlib.Path:
    date = datetime.date.today().isoformat()
    folder = render.LIBRARY / f"{date}-{video.stem}"
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cfg_path, folder / "talk.json")
    shutil.copyfile(p["work"] / "transcript.txt", folder / "transcript.txt")
    hook_s = cfg.get("hook_seconds", 3)
    marks = [hook_s - 0.3, hook_s + p["duration"] / 2, hook_s + p["duration"] + 3.7]
    inputs = sum((["-ss", f"{m:.2f}", "-i", str(video)] for m in marks), [])
    ff(*inputs, "-filter_complex", "[0:v][1:v][2:v]hstack=3,scale=540:-2", "-frames:v", "1", "-q:v", "4", str(folder / "sheet.jpg"))
    index = render.LIBRARY / "index.md"
    text = index.read_text(encoding="utf-8") if index.exists() else render.INDEX_HEAD
    index.write_text(text + render.index_line(date, video.stem, {"headline": cfg["hook"]["headline"], "format": cfg.get("format", "كلام")}), encoding="utf-8")
    return folder


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcribe")
    t.add_argument("video")
    t.add_argument("work")
    t.add_argument("--model", default="large-v3-turbo", help="small أسرع، large-v3-turbo أدق للعربي")
    t.add_argument("--lang", default="ar")
    r = sub.add_parser("render")
    r.add_argument("talk")
    r.add_argument("out")
    r.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    if a.cmd == "transcribe":
        transcribe(pathlib.Path(a.video).resolve(), pathlib.Path(a.work).resolve(), a.model, a.lang)
    else:
        do_render(pathlib.Path(a.talk).resolve(), pathlib.Path(a.out).resolve(), a.preview)


if __name__ == "__main__":
    main()
