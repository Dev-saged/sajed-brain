#!/usr/bin/env python3
"""يبني فيلم ساجد من script.json + لقطات حقيقية.
python3 film.py <voiceDir|-> <out.mp4> [--preview]
voiceDir: مجلد ملفات wav من voice.py. '-' = فيلم صامت بتوقيت افتراضي."""
import json, pathlib, shutil, subprocess, sys, wave
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FPS = 30
TMP = pathlib.Path("/tmp/film"); FR = TMP / "frames"; REC = TMP / "rec"


def voice_len(d, i):
    if d == "-": return [6.0, 9.0, 8.0, 8.0, 4.5, 6.0][i]
    with wave.open(f"{d}/{i}.wav" if False else f"{d}/v{i+1}.wav") as w: return w.getnframes() / w.getframerate()


def timeline(vd):
    voice = [voice_len(vd, i) for i in range(6)]
    durs = [v + .5 for v in voice]; durs[-1] += .4
    starts = [sum(durs[:i]) for i in range(6)]
    return {"voice": voice, "durs": durs, "starts": starts, "total": sum(durs)}


def brand(tl):
    tokens = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    icons = json.loads((ROOT / "icons" / "platforms.json").read_text(encoding="utf-8"))
    lines = [s["text"].replace("…", "").replace(":", "") for s in json.loads((HERE / "script.json").read_text(encoding="utf-8"))]
    REC.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(HERE / "footage/control-room.mp4"), "-q:v", "3", str(REC / "%03d.jpg")], check=True)
    n = len(list(REC.glob("*.jpg")))
    return {"tokens": tokens, "icons": icons, "timeline": tl, "lines": lines,
            "assets": {"portrait": (ROOT / tokens["identity"]["portrait"]).as_uri(),
                       "covers": (HERE / "footage/blog-covers.jpg").as_uri(),
                       "frames": REC.as_uri() + "/%03d.jpg", "frameCount": n, "fps": 15}}


def worker(args):
    from playwright.sync_api import sync_playwright
    b, idx = args
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--allow-file-access-from-files"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.add_init_script("window.__BRAND = " + json.dumps(b, ensure_ascii=False))
        pg.goto((HERE / "film.html").as_uri())
        pg.wait_for_function("window.__ready")
        pg.evaluate("window.__ready()")
        for i in idx:
            pg.evaluate(f"window.__seek({i / FPS})")
            pg.screenshot(path=f"{FR}/{i:05d}.jpg", type="jpeg", quality=92)
        br.close()


def audio(tl, vd, out_wav):
    ev = []  # (وقت، نوع)
    for i, s in enumerate(tl["starts"]):
        if i: ev.append((s - .05, "w"))
    s4 = tl["starts"][3]
    ev += [(s4 + .5 + i * 1.4 + .3, "t") for i in range(5)]
    s1 = tl["starts"][0]
    ev += [(s1 + 1 + .05 * k + .0, "k") for k in range(0, 26, 2)]
    inp, fl, mix = [], [], []
    k = 0
    def add(src, delay, vol, post=""):
        nonlocal k
        inp.extend(["-f", "lavfi", "-t", "1.2", "-i", src] if src.startswith(("sine", "anoise")) else ["-i", src])
        ms = int(delay * 1000)
        fl.append(f"[{k}:a]{post}volume={vol},adelay={ms}|{ms}[e{k}]"); mix.append(f"[e{k}]"); k += 1
    for t, kind in ev:
        if kind == "w": add("anoisesrc=d=0.7:c=pink:a=0.5", max(0, t), 0.55, "lowpass=f=3000,highpass=f=300,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.45,")
        elif kind == "t": add("sine=f=1650:d=0.12", t, 0.35, "afade=t=out:st=0.02:d=0.1,")
        else: add("sine=f=2300:d=0.03", t, 0.12, "afade=t=out:st=0.01:d=0.02,")
    if vd != "-":
        for i, s in enumerate(tl["starts"]):
            add(f"{vd}/v{i+1}.wav", s + .25, 1.9, "aresample=44100,")
        vo = "".join(f"[e{n}]" for n in range(k - 6, k))
    bed = "sin(2*PI*55*t)*0.4+sin(2*PI*82.4*t)*0.3+sin(2*PI*164.8*t)*(0.1+0.08*sin(2*PI*0.2*t))"
    inp.extend(["-f", "lavfi", "-t", f"{tl['total']:.2f}", "-i", f"aevalsrc='{bed}':s=44100"])
    bedi = k
    fl.append(f"[{bedi}:a]lowpass=f=700,volume=0.35,afade=t=in:d=2,afade=t=out:st={tl['total']-2.5:.2f}:d=2.5[bed]")
    if vd != "-":
        fl.append(f"{vo}amix=inputs=6:normalize=0,asplit=2[vo][sc]")
        fl.append("[bed][sc]sidechaincompress=threshold=0.02:ratio=9:attack=20:release=450[bd]")
        sfx = "".join(m for m in mix[:-6]); fl.append(f"{sfx}amix=inputs={k-6}:normalize=0[sx]")
        fl.append("[bd][vo][sx]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]")
    else:
        fl.append("".join(mix) + f"amix=inputs={k}:normalize=0[sx]"); fl.append("[bed][sx]amix=inputs=2:normalize=0[a]")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-filter_complex", ";".join(fl), "-map", "[a]", "-t", f"{tl['total']:.2f}", str(out_wav)], capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg audio: " + r.stderr[:500])


def main():
    vd, out = sys.argv[1], pathlib.Path(sys.argv[2]).resolve()
    preview = "--preview" in sys.argv
    tl = timeline(vd); b = brand(tl)
    shutil.rmtree(FR, ignore_errors=True); FR.mkdir(parents=True)
    total = int(tl["total"] * FPS)
    if preview:
        idx = [int((s + d * .6) * FPS) for s, d in zip(tl["starts"], tl["durs"])]
        worker((b, idx))
        for i in idx: shutil.copy(FR / f"{i:05d}.jpg", out.with_name(f"{out.stem}-{i}.jpg")); print(out.with_name(f"{out.stem}-{i}.jpg"))
        return
    idx = list(range(total)); n = 3
    with ThreadPoolExecutor(n) as ex: list(ex.map(worker, [(b, idx[k::n]) for k in range(n)]))
    wav = TMP / "mix.wav"; audio(tl, vd, wav)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/%05d.jpg", "-i", str(wav),
                    "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", str(out)], check=True)
    print(out, round(tl["total"], 1), "s")


if __name__ == "__main__":
    main()
