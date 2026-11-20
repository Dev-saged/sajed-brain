#!/usr/bin/env python3
"""فيديو كلام ساجد ← نص حرفي ← ريل بهويته وأجواء متحركة.

1) python3 talk.py transcribe my-video.mp4 work/        ← work/transcript.txt + words.json
2) اكتب talk.json (انظر talk.example.json) بعد قراءة transcript.txt فقط
3) python3 talk.py render talk.json out.mp4 [--preview]

قواعد ساجد مفروضة هنا: النص حرفي (لا حذف كلمات)، كل لغة بخطها، صوت طبيعي، كابشن أسفل بلا صندوق.
"""
import argparse
import datetime
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parent
BRAIN = ROOT.parent
GAP = 0.6
PAD = 0.15
PROMPT = "Hi guys، الأجواء very fantastic اليوم. English words stay in English: guys, very, fantastic, creative, okay, nice, app."
AUDIO = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
VIDEO = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30"]
ARABIC = re.compile(r"[؀-ۿ]")
LATIN = re.compile(r"[A-Za-z]")
# كلمات تُطلق أجواءً تلقائياً حين لا يحدد talk.json قائمة fx
FX_CUES = {
    "rain": ("مطر", "ماطر", "الماطرة", "شتا", "شتاء", "rain"),
    "steam": ("شاي", "قهوة", "كاسة", "فنجان", "tea", "coffee"),
    "fire": ("نار", "دفا", "دفء", "حطب", "fire"),
    "sparkle": ("يارب", "رب", "ربنا", "الله", "دعاء", "نتمنى", "يحقق"),
}

import compose  # noqa: E402

spec = importlib.util.spec_from_file_location("render", ROOT / "templates" / "render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def arabizi() -> dict:
    p = BRAIN / "rules" / "arabizi.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def core(word: str) -> str:
    return word.strip("،.؟!,?")


def to_script(word: str, table: dict) -> str:
    """يستبدل لبّ الكلمة مع إبقاء علامات الترقيم (للتعريب العكسي وتصحيحات السمع)."""
    c = core(word)
    return word.replace(c, table[c]) if c in table else word


def transcribe(src: pathlib.Path, work: pathlib.Path, model: str, lang: str) -> None:
    import wave
    import numpy as np
    from faster_whisper import WhisperModel

    work.mkdir(parents=True, exist_ok=True)
    wav = work / "voice.wav"
    # التنظيف هنا للتفريغ فقط؛ صوت الفيديو النهائي لا يُعالج
    ff("-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-af", "highpass=f=80,afftdn=nf=-25,loudnorm", str(wav))
    with wave.open(str(wav)) as f:
        audio = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
    m = WhisperModel(model, device="auto", compute_type="int8")
    segs, _ = m.transcribe(audio, language=lang, initial_prompt=PROMPT, word_timestamps=True, vad_filter=True)
    table, words, lines = arabizi(), [], []
    for s in segs:
        ws = [{"w": to_script(w.word.strip(), table), "s": round(w.start, 3), "e": round(w.end, 3)} for w in s.words or [] if w.word.strip()]
        words += ws
        lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] {' '.join(w['w'] for w in ws)}")
    (work / "words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    (work / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(work / "transcript.txt", f"({len(words)} كلمة)")


def auto_keep(words: list) -> list:
    """مقاطع الكلام بعد حذف الصمت الطويل فقط — لا تُحذف أي كلمة."""
    spans = []
    for w in words:
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


def validate(cfg: dict, words: list, keep: list) -> None:
    """يمنع تكرار أخطاء سابقة قبل أي رندر."""
    errs = []
    spoken = {core(w["w"]) for w in words}
    for k, v in cfg.get("fixes", {}).items():
        if k not in spoken and not cfg.get("part"):
            errs.append(f"fixes: «{k}» غير موجودة في التفريغ")
        if LATIN.search(k) and ARABIC.search(v):
            errs.append(f"fixes: «{k}» إنجليزية ولا تُكتب بحروف عربية «{v}»")
        if "ڤ" in v:
            errs.append(f"fixes: «{v}» تعريب لكلمة إنجليزية — اكتبها بالإنجليزي")
    dropped = [w["w"] for w in words if retime(w["s"], keep) is None or retime(w["e"], keep) is None]
    if dropped and not cfg.get("approved_cuts"):
        errs.append("keep يحذف كلمات منطوقة (النص حرفي): " + " ".join(dropped[:20])
                    + " — احذف القص أو أضف approved_cuts بموافقة ساجد")
    if "hook" in cfg:
        errs.append("hook (مقدمة terminal) أُلغي — استخدم title من المحتوى")
    if errs:
        raise SystemExit("\n".join(errs))


def auto_fx(words: list, keep: list) -> list:
    fx = []
    for w in words:
        word = core(w["w"]).lower()
        for kind, cues in FX_CUES.items():
            if any(c in word for c in cues):
                t = retime(w["s"], keep)
                if t is None:
                    continue
                last = next((f for f in reversed(fx) if f["type"] == kind), None)
                if last and t - last["to"] < 3:
                    last["to"] = t + 3
                else:
                    fx.append({"type": kind, "from": max(0, t - 0.4), "to": t + 3})
    return fx


def plan(cfg: dict, base: pathlib.Path) -> dict:
    work = (base / cfg["work"]).resolve()
    words = json.loads((work / "words.json").read_text(encoding="utf-8"))
    keep = cfg.get("keep") or auto_keep(words)
    if cfg.get("part"):
        # مقطع تجريبي من الفيديو (زمن المصدر): ما خارجه ليس حذفاً لكلام
        a, b = cfg["part"]
        keep = [[max(s, a), min(e, b)] for s, e in keep if e > a and s < b]
        words = [w for w in words if w["s"] >= a and w["e"] <= b]
        inside = lambda x: a <= x.get("at", x.get("from", a)) and x.get("to", x.get("at", a)) <= b
        cfg = {**cfg, **{k: [x for x in cfg.get(k, []) if inside(x)] for k in ("cards", "pops", "fx", *SPANS) if k in cfg}}
    validate(cfg, words, keep)
    fixes = cfg.get("fixes", {})
    out = []
    for w in words:
        s, e = retime(w["s"], keep), retime(w["e"], keep)
        if s is not None and e is not None:
            out.append({"w": to_script(w["w"], fixes), "s": round(s, 3), "e": round(e, 3)})
    rt = lambda t: retime(t, keep)
    fx = [{**f, **{k: rt(f[k]) for k in ("from", "to", "at") if k in f}} for f in cfg["fx"]] if "fx" in cfg else auto_fx(words, keep)
    bounds, acc = [], 0.0
    for s, e in keep:
        bounds.append((acc, acc + e - s))
        acc += e - s
    return {
        "work": work,
        "keep": keep,
        "words": out,
        "pops": [p for p in ({"at": rt(p["at"]), "text": p["text"]} for p in cfg.get("pops", [])) if p["at"] is not None],
        "zooms": [z for z in ((rt(a), rt(b)) for a, b in cfg.get("zooms", [])) if None not in z],
        "fx": [f for f in fx if None not in (f.get("from", 0), f.get("to", 0), f.get("at", 0))],
        "bounds": bounds,
        "duration": round(acc, 3),
        **timeline(cfg, rt, base),
    }


SPANS = ("frames", "behind", "spotlight", "ui", "phones")


def timeline(cfg: dict, rt, base: pathlib.Path) -> dict:
    """البطاقات وعناصر الموشن بزمن الفيديو بعد القص، مع رفض أي عنصر يقع في جزء محذوف أو ناقص."""
    errs, out = [], {}
    cards = []
    for c in cfg.get("cards", []):
        at = rt(c["at"])
        if at is None:
            errs.append(f"cards: الزمن {c['at']} في جزء محذوف")
            continue
        if c.get("type") not in ("typo", "icon", "prop", "image"):
            errs.append(f"cards: النوع {c.get('type')} غير معروف (typo/icon/prop/image)")
        if c.get("style") == "3d":
            errs.append("cards: style 3d (إيموجي) ممنوع — أيقونات تصميم فقط")
        if c.get("type") in ("icon", "prop"):
            # الأيقونة: اسم ملف أو كلمة عربية/إنجليزية تُحل من مكتبة assets
            # أيقونة تصميم (Phosphor) — الإيموجي ممنوع بقرار ساجد
            path = compose.resolve_icon(c.get("icon") or c.get("text", ""), "fill" if c.get("style") == "fill" else "icon")
            c = {**c, "svg": compose.svg_markup(path)}
        if c.get("type") == "image":
            src = (base / c["src"]).resolve()
            if not src.is_file():
                errs.append(f"cards: الصورة غير موجودة {src}")
            c = {**c, "src": src.as_uri()}
        cards.append({**c, "at": at})
    out["cards"] = cards
    for key in SPANS:
        items = []
        for x in cfg.get(key, []):
            a, b = rt(x["from"]), rt(x["to"])
            if a is None or b is None:
                errs.append(f"{key}: الفترة {x['from']}–{x['to']} تقع في جزء محذوف")
                continue
            if key == "phones":
                src = (base / x["src"]).resolve()
                if not src.is_file():
                    errs.append(f"phones: الصورة غير موجودة {src}")
                x = {**x, "src": src.as_uri()}
            items.append({**x, "from": a, "to": b})
        out[key] = items
    if errs:
        raise SystemExit("\n".join(errs))
    return out


def peak_gain(src: pathlib.Path) -> float:
    r = subprocess.run(["ffmpeg", "-i", str(src), "-af", "volumedetect", "-vn", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"max_volume: (-?[\d.]+) dB", r.stderr)
    return max(0.0, -1.5 - float(m.group(1))) if m else 0.0


def beats(p: dict, gap: float = 0.18, min_len: float = 2.2, max_len: float = 4.5) -> list:
    """مقاطع الإيقاع (عريض/قريب): تنكسر عند الوقفات ونهايات الجمل، بين min_len وmax_len."""
    ws, cuts = p["words"], [0.0]
    for prev, w in zip(ws, ws[1:]):
        span = w["s"] - cuts[-1]
        if span >= min_len and (w["s"] - prev["e"] >= gap or prev["w"][-1:] in ".؟!?،" or span >= max_len):
            cuts.append(w["s"])
    cuts.append(p["duration"])
    return [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]


def cut_source(src: pathlib.Path, p: dict, out: pathlib.Path, grade: str) -> None:
    keep, parts, labels = p["keep"], [], []
    for i, (s, e) in enumerate(keep):
        parts.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    # إيقاع عريض ↔ قريب عند كل قطع (مرجع ذهبي) + دفع بطيء داخل كل مقطع + دفعة في اللحظات المحددة
    alt = "+".join(f"0.2*between(t,{a:.3f},{b:.3f})" for i, (a, b) in enumerate(beats(p)) if i % 2) or "0"
    drift = "+".join(f"0.05*between(t,{a:.3f},{b:.3f})*(t-{a:.3f})/{max(b - a, 0.1):.3f}" for a, b in p["bounds"]) or "0"
    push = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in p["zooms"]) or "0"
    z = f"(1+{alt}+{drift}+0.08*gt({push},0))"
    gain = peak_gain(src)
    fc = ";".join(parts) + f";{''.join(labels)}concat=n={len(keep)}:v=1:a=1[cv][ca];" \
        f"[cv]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920," \
        f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame,crop=1080:1920,setsar=1,{grade}[vo];" \
        f"[ca]volume={gain:.2f}dB[ao]"
    ff("-i", str(src), "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]", *VIDEO, *AUDIO, str(out))


def with_silence(src: pathlib.Path, out: pathlib.Path) -> None:
    ff("-i", str(src), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
       "-map", "0:v", "-map", "1:a", "-c:v", "copy", *AUDIO, str(out))


def mood_of(cfg: dict, p: dict) -> tuple:
    name = cfg.get("mood") or compose.detect_mood(p["words"], (cfg.get("cover") or cfg.get("title") or {}).get("text", ""))
    if name not in compose.MOODS:
        raise SystemExit(f"mood: {name} غير معروف ({'/'.join(compose.MOODS)})")
    return name, compose.MOODS[name]


def overlay_data(cfg: dict, p: dict, tokens: dict) -> dict:
    name, m = mood_of(cfg, p)
    return {"tokens": tokens, "words": p["words"], "pops": p["pops"], "fx": p["fx"], "mood": {**m, "name": name},
            "emphasis": cfg.get("emphasis", []), "keywords": cfg.get("keywords", []), "kashida": cfg.get("kashida", True),
            "duration": p["duration"], **{k: p[k] for k in ("cards", *SPANS)}}


def cover_data(cfg: dict, data: dict) -> dict:
    t = cfg.get("cover") or cfg.get("title") or {}
    return {"mood": data["mood"], "title": t.get("text", ""), "sub": t.get("sub", ""), "kashida": cfg.get("kashida", True),
            "byline": "ساجد العبادلة · من غزة"}


def extract_frames(video: pathlib.Path, folder: pathlib.Path) -> list:
    folder.mkdir(parents=True, exist_ok=True)
    ff("-i", str(video), "-q:v", "2", str(folder / "%05d.jpg"))
    return sorted(folder.glob("*.jpg"))


def do_render(cfg_path: pathlib.Path, out: pathlib.Path, preview: bool, part=None) -> None:
    from playwright.sync_api import sync_playwright

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if part:
        cfg = {**cfg, "part": part, "outro": False, "no_archive": True}
    base = cfg_path.parent
    src = (base / cfg["source"]).resolve()
    p = plan(cfg, base)
    tokens = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    icons = json.loads((ROOT / "icons" / "platforms.json").read_text(encoding="utf-8"))
    data = overlay_data(cfg, p, tokens)
    grade = data["mood"]["grade"]

    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        br = pw.chromium.launch()
        cut_source(src, p, td / "cut.mp4", grade)
        frames = extract_frames(td / "cut.mp4", td / "src")
        span = lambda k: [(x["from"], x["to"]) for x in p[k]]
        if preview:
            marks = [1.2] + [x["at"] + 0.9 for x in p["cards"][:3]] + [(x["from"] + x["to"]) / 2 for k in SPANS for x in p[k][:1]]
            cut_r = [(m - 0.1, m + 0.1) for m in marks if any(a <= m <= b for a, b in span("behind"))]
            face_r = [(m - 0.1, m + 0.1) for m in marks]
            all_frames = frames
            cutouts, faces = compose.vision(all_frames, cut_r, face_r, td / "cut")
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.add_init_script("window.__TALK = " + json.dumps(data, ensure_ascii=False))
            pg.goto((HERE / "talk.html").as_uri())
            pg.wait_for_function("window.__ready && document.fonts.status === 'loaded'")
            for n, m in enumerate(marks):
                i = min(len(all_frames) - 1, int(m * compose.FPS))
                c = cutouts.get(i)
                pg.evaluate("([ms, f, c, face]) => window.__seek(ms, f, c, face)", [m * 1000, all_frames[i].as_uri(), c.as_uri() if c else None, faces.get(i)])
                shot = out.with_name(f"{out.stem}-{n}.jpg")
                pg.screenshot(path=str(shot), type="jpeg", quality=88)
                print(shot)
            cover = out.with_name(out.stem + "-غلاف.jpg")
            compose.make_cover(br, cover_data(cfg, data), frames[compose.best_cover_frame(frames)], td, cover)
            print(cover)
            print(f"مدة {p['duration']}ث · بطاقات {len(p['cards'])} · أجواء {[f['type'] for f in p['fx']]} · مزاج {data['mood']['name']}")
            br.close()
            return
        # الوجه في كل الإطارات: الإضاءة تتبعه
        cutouts, faces = compose.vision(frames, span("behind"), [(0, p["duration"])], td / "cut")
        compose.composite(br, data, frames, cutouts, faces, td / "out")
        ff("-i", str(td / "cut.mp4"), "-vn", "-c:a", "pcm_s16le", str(td / "voice.wav"))
        music = (base / cfg["music"]).resolve() if cfg.get("music") else None
        compose.mix_audio(td / "voice.wav", compose.sfx_events(p, cfg), music, p["duration"], td / "mix.m4a")
        cover = out.with_name(out.stem + "-غلاف.jpg")
        compose.make_cover(br, cover_data(cfg, data), frames[compose.best_cover_frame(frames)], td, cover)
        print(cover)
        ff("-framerate", "30", "-i", str(td / "out" / "%05d.jpg"), "-i", str(td / "mix.m4a"),
           "-map", "0:v", "-map", "1:a", *VIDEO, "-c:a", "copy", "-shortest", str(td / "talk.mp4"))
        order = [td / "talk.mp4"]
        if cfg.get("outro", True):
            brand = {"tokens": tokens, "icons": icons, "content": {"headline": "", "demo": {}, "durations": {"outro": 4}},
                     "assets": {"portrait": (ROOT / tokens["identity"]["portrait"]).as_uri(), "screenshot": None}}
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.add_init_script("window.__BRAND = " + json.dumps(brand, ensure_ascii=False))
            render.film(pg, "outro", td / "outro-v.mp4", 30)
            with_silence(td / "outro-v.mp4", td / "outro.mp4")
            order.append(td / "outro.mp4")
        br.close()
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
    d = p["duration"]
    marks = [1.2, d / 2, d + 3.7 if cfg.get("outro", True) else d - 0.5]
    inputs = sum((["-ss", f"{m:.2f}", "-i", str(video)] for m in marks), [])
    ff(*inputs, "-filter_complex", "[0:v][1:v][2:v]hstack=3,scale=540:-2", "-frames:v", "1", "-q:v", "4", str(folder / "sheet.jpg"))
    index = render.LIBRARY / "index.md"
    text = index.read_text(encoding="utf-8") if index.exists() else render.INDEX_HEAD
    head = (cfg.get("cover") or cfg.get("title") or {}).get("text", video.stem).replace("\n", " ")
    index.write_text(text + render.index_line(date, video.stem, {"headline": head, "format": cfg.get("format", "كلام")}), encoding="utf-8")
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
    r.add_argument("--part", help="مقطع تجريبي بزمن المصدر مثل 12-42 (بلا خاتمة)")
    a = ap.parse_args()
    if a.cmd == "transcribe":
        transcribe(pathlib.Path(a.video).resolve(), pathlib.Path(a.work).resolve(), a.model, a.lang)
    else:
        do_render(pathlib.Path(a.talk).resolve(), pathlib.Path(a.out).resolve(), a.preview,
                  [float(x) for x in a.part.split("-")] if a.part else None)


if __name__ == "__main__":
    main()
