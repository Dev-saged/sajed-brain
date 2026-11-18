"""مُركِّب فيديو الكلام: رؤية (فصل الشخص + الوجه)، مؤثرات صوتية مولّدة، وتركيب كل إطار في talk.html."""
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
MODELS = HERE / "models"
ICONS = HERE / "icons"
FPS = 30

# درجات لونية للمزاج (ffmpeg)
GRADES = {
    "teal": "colorbalance=rs=-0.06:gs=0.01:bs=0.07:rh=0.05:gh=0.01:bh=-0.04,eq=contrast=1.08:saturation=1.06",
    "wine": "colorbalance=rs=0.08:gs=-0.05:bs=0.02:rh=0.04:bh=-0.02,eq=contrast=1.1:saturation=1.04:brightness=-0.02",
    "amber": "colorbalance=rm=0.06:gm=0.02:bm=-0.06:rh=0.05:bh=-0.05,eq=contrast=1.07:saturation=1.1",
    "natural": "eq=contrast=1.05:saturation=1.08",
}

# مؤثرات صوتية مولّدة رقمياً (بلا ملفات ولا تراخيص)
SFX = {
    "whoosh": ("anoisesrc=d=0.5:c=pink:a=0.6", "highpass=f=250,lowpass=f=4200,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.3,volume=0.55"),
    "pop": ("aevalsrc='0.6*sin(2*PI*(700+900*t)*t)*exp(-28*t)':d=0.18", "volume=0.6"),
    "impact": ("aevalsrc='0.9*sin(2*PI*55*t)*exp(-6*t)+0.25*(random(0)*2-1)*exp(-30*t)':d=0.7", "lowpass=f=2500,volume=0.7"),
    "shimmer": ("aevalsrc='0.18*(sin(2*PI*1760*t)+sin(2*PI*2349*t)+sin(2*PI*2637*t))*(0.5+0.5*sin(2*PI*9*t))*exp(-2.5*t)':d=1.0", "afade=t=in:d=0.05,volume=0.45"),
    "riser": ("aevalsrc='0.3*sin(2*PI*(180+700*t/1.2)*t)+0.12*(random(0)*2-1)*t/1.2':d=1.2", "highpass=f=120,afade=t=in:d=0.9,afade=t=out:st=1.1:d=0.1,volume=0.4"),
}


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def icons_markup(names) -> dict:
    out = {}
    for n in names:
        p = ICONS / f"{n}.svg"
        if not p.is_file():
            raise SystemExit(f"أيقونة غير موجودة: {n} — المتاح: {', '.join(sorted(x.stem for x in ICONS.glob('*.svg')))}")
        out[n] = p.read_text(encoding="utf-8")
    return out


def sfx_events(p: dict, cfg: dict) -> list:
    """أحداث صوتية من خط الزمن: (زمن، نوع)."""
    if cfg.get("sfx") is False:
        return []
    ev = []
    if cfg.get("title"):
        ev += [(0.0, "impact"), (0.15, "shimmer")]
    for c in p["cards"]:
        ev.append((max(0, c["at"] - 0.2), "whoosh"))
        ev.append((c["at"] + 0.05, "impact" if c["type"] == "typo" else "shimmer"))
    for key in ("frames", "phones", "ui", "behind"):
        ev += [(max(0, x["from"] - 0.25), "whoosh") for x in p[key]]
    ev += [(x["from"], "shimmer") for x in p["spotlight"]]
    ev += [(x["at"], "pop") for x in p["pops"]]
    ev.sort()
    kept = []
    for t, k in ev:
        if not kept or t - kept[-1][0] > 0.12:
            kept.append((t, k))
    return kept


def mix_audio(voice: pathlib.Path, events: list, music, duration: float, out: pathlib.Path, work: pathlib.Path) -> None:
    inputs, filters, labels = ["-i", str(voice)], [], []
    for name, (src, fx) in SFX.items():
        if any(k == name for _, k in events):
            ff("-f", "lavfi", "-i", src, "-af", fx, "-ar", "48000", "-ac", "2", str(work / f"{name}.wav"))
    for i, (t, k) in enumerate(events, start=1):
        inputs += ["-i", str(work / f"{k}.wav")]
        ms = int(t * 1000)
        filters.append(f"[{i}:a]adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    n = len(events)
    base = "[0:a]"
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        m = n + 1
        # الموسيقى تنخفض تلقائياً حين يتكلم ساجد
        filters.append(f"[{m}:a]volume=0.18,atrim=0:{duration:.2f},afade=t=out:st={max(0, duration - 1.5):.2f}:d=1.5[mu]")
        filters.append("[0:a]asplit=2[v1][v2]")
        filters.append("[mu][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck]")
        base = "[v1]"
        labels.append("[duck]")
    if not labels:
        ff("-i", str(voice), "-c:a", "aac", "-b:a", "192k", str(out))
        return
    filters.append(f"{base}{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    ff(*inputs, "-filter_complex", ";".join(filters), "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out))


def needed_frames(ranges: list, total: int) -> set:
    s = set()
    for a, b in ranges:
        s.update(range(max(0, int((a - 0.5) * FPS)), min(total, int((b + 0.5) * FPS) + 1)))
    return s


def vision(frames: list, cut_ranges: list, face_ranges: list, outdir: pathlib.Path):
    """قصّ الشخص (PNG شفاف) للنص خلفه، وموضع الوجه لحلقة الضوء — فقط للإطارات المطلوبة."""
    cut_idx, face_idx = needed_frames(cut_ranges, len(frames)), needed_frames(face_ranges, len(frames))
    if not cut_idx and not face_idx:
        return {}, {}
    import mediapipe as mp
    import numpy as np
    from PIL import Image
    from mediapipe.tasks.python import BaseOptions, vision as mv

    seg = mv.ImageSegmenter.create_from_options(mv.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=str(MODELS / "selfie_segmenter.tflite")), output_confidence_masks=True)) if cut_idx else None
    det = mv.FaceDetector.create_from_options(mv.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=str(MODELS / "face_detector.tflite")))) if face_idx else None
    cutouts, faces, last = {}, {}, None
    outdir.mkdir(parents=True, exist_ok=True)
    for i in sorted(cut_idx | face_idx):
        img = mp.Image.create_from_file(str(frames[i]))
        if i in cut_idx:
            m = seg.segment(img).confidence_masks[0].numpy_view().squeeze()
            rgb = np.asarray(Image.open(frames[i]).convert("RGB"))
            alpha = (np.clip((m - 0.35) / 0.3, 0, 1) * 255).astype("uint8")
            p = outdir / f"{i:05d}.png"
            Image.fromarray(np.dstack([rgb, alpha])).save(p, compress_level=1)
            cutouts[i] = p
        if i in face_idx and (i % 3 == 0 or last is None):
            d = det.detect(img).detections
            if d:
                b = d[0].bounding_box
                cur = {"cx": b.origin_x + b.width / 2, "cy": b.origin_y + b.height / 2, "w": b.width}
                last = cur if last is None else {k: last[k] * 0.6 + cur[k] * 0.4 for k in cur}
        if i in face_idx and last:
            faces[i] = last
    for m in (seg, det):
        if m:
            m.close()
    return cutouts, faces


def composite(br, data: dict, frames: list, cutouts: dict, faces: dict, outdir: pathlib.Path) -> None:
    pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.add_init_script("window.__TALK = " + json.dumps(data, ensure_ascii=False))
    pg.goto((HERE / "talk.html").as_uri())
    pg.wait_for_function("window.__ready && document.fonts.status === 'loaded'")
    outdir.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(frames):
        cut = cutouts.get(i)
        pg.evaluate("([ms, f, c, face]) => window.__seek(ms, f, c, face)",
                    [i * 1000 / FPS, f.as_uri(), cut.as_uri() if cut else None, faces.get(i)])
        pg.screenshot(path=str(outdir / f"{i:05d}.jpg"), type="jpeg", quality=92)
    issues = sorted(set(pg.evaluate("window.__issues")))
    pg.close()
    if issues:
        raise SystemExit("مشاكل عرض (لن يُسلَّم فيديو معيب):\n" + "\n".join(issues[:15]))
