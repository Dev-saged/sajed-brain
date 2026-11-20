"""مُركِّب فيديو الكلام v2: مزاج من المحتوى (ألوان + خطوط + درجة لونية)، رؤية (فصل الشخص + الوجه)،
مؤثرات صوتية حقيقية من مكتبة assets/sfx، تركيب كل إطار في talk.html، وصورة غلاف مصممة."""
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BRAIN = HERE.parent.parent
ASSETS = BRAIN / "assets"
MODELS = HERE / "models"
FPS = 30
sys.path.insert(0, str(ASSETS))

import find as assetfind  # noqa: E402

# كل مزاج: لوحة ألوان + خط عناوين + درجة لونية للفيديو. الكابشن دائماً IBM Plex Sans Arabic.
MOODS = {
    "cozy": {"bg": ["#2a3a44", "#0b1418"], "accent": "#F0A848", "accent2": "#A9CFE0", "title": "El Messiri",
             "grade": "colorbalance=rs=-0.04:bs=0.05:rh=0.06:gh=0.02:bh=-0.05,eq=contrast=1.07:saturation=1.05",
             "cues": ["مطر", "ماطر", "شتا", "شاي", "قهوة", "نار", "دفا", "بيت", "صباح", "أجواء", "كشك", "رغيف"]},
    "spiritual": {"bg": ["#4a1424", "#12050a"], "accent": "#E8C77E", "accent2": "#F3E3C3", "title": "Aref Ruqaa Ink",
                  "grade": "colorbalance=rs=0.07:gs=-0.04:bs=0.02:rh=0.04:bh=-0.02,eq=contrast=1.1:saturation=1.02:brightness=-0.02",
                  "cues": ["الله", "ربنا", "يارب", "رب", "دعاء", "الدعوات", "نتمنى", "يحفظ", "صلاة", "الحمد", "إن شاء"]},
    "tech": {"bg": ["#164b4c", "#051617"], "accent": "#D4A64A", "accent2": "#7FD6CF", "title": "Noto Kufi Arabic",
             "grade": "colorbalance=rs=-0.06:gs=0.01:bs=0.07:rh=0.05:gh=0.01:bh=-0.04,eq=contrast=1.08:saturation=1.06",
             "cues": ["تطبيق", "برمجة", "كود", "موقع", "ذكاء", "app", "تحديث", "جوال", "أداة", "نظام", "بيانات"]},
    "energy": {"bg": ["#262019", "#0b0907"], "accent": "#FF8A3D", "accent2": "#FFD08A", "title": "Lalezar",
               "grade": "eq=contrast=1.14:saturation=1.12,colorbalance=rm=0.04:bm=-0.04",
               "cues": ["نجاح", "هدف", "قوة", "تحدي", "فلوس", "مال", "ربح", "استثمار", "شغل", "إنجاز"]},
    "hope": {"bg": ["#1d3d16", "#08160a"], "accent": "#E5CD82", "accent2": "#B9E08F", "title": "Reem Kufi",
             "grade": "colorbalance=gm=0.03:rh=0.04:bh=-0.04,eq=contrast=1.06:saturation=1.08",
             "cues": ["أمل", "بكرا", "حلم", "طبيعة", "شجر", "ربيع", "بداية", "فرح"]},
    "serious": {"bg": ["#2a2d33", "#0c0d10"], "accent": "#D6E0EA", "accent2": "#9AA6B2", "title": "Noto Kufi Arabic",
                "grade": "eq=contrast=1.1:saturation=0.82",
                "cues": ["حزن", "صعب", "حرب", "خوف", "وجع", "فقد", "قصف", "نزوح"]},
}

# أحداث الموشن ← مؤثر من المكتبة (assets/sfx) مع إزاحة نقطة التزامن
SFX_FOR = {"card": "whoosh-medium-soft", "prop": "pop-medium-in", "typo": "impact-medium-soft", "frame": "whoosh-medium-medium",
           "pill": "swish-soft", "behind": "reverse-whoosh-short-soft", "spotlight": "shimmer-medium-sparkle",
           "phone": "swipe-medium-soft", "pop": "pop-small-in", "start": "shimmer-short-soft"}


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def detect_mood(words: list, headline: str = "") -> str:
    """العنوان (الغلاف) يحمل فكرة الفيديو فيُوزن ثلاثة أضعاف الكلام."""
    text = " ".join(w["w"] for w in words) + (" " + headline) * 3
    scores = {m: sum(text.count(c) for c in v["cues"]) for m, v in MOODS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "tech"


def resolve_icon(q: str, kind: str = "icon3d") -> pathlib.Path:
    """اسم ملف أو كلمة عربية/إنجليزية ← أفضل أصل من المكتبة."""
    direct = ASSETS / ("icons3d" if kind == "icon3d" else "icons/duotone") / (f"{q}.webp" if kind == "icon3d" else f"{q}.svg")
    if direct.is_file():
        return direct
    hit = assetfind.find(q, kind, 1)
    if not hit:
        raise SystemExit(f"لا أصل يطابق «{q}» ({kind}) — جرّب: python3 assets/find.py \"{q}\"")
    return pathlib.Path(hit[0]["path"])


def sfx_catalog() -> dict:
    return {e["id"]: e for e in json.loads((ASSETS / "index.json").read_text(encoding="utf-8")) if e["type"] == "sfx"}


def sfx_events(p: dict, cfg: dict) -> list:
    """(زمن البدء، مسار، مستوى) — تُزاح بنقطة التزامن لتلتقي ذروة الصوت بالحركة."""
    if cfg.get("sfx") is False:
        return []
    cat, ev = sfx_catalog(), []
    add = lambda t, key, vol=0.5: ev.append((t, key, vol))
    for c in p["cards"]:
        add(c["at"], {"prop": "prop", "typo": "typo"}.get(c["type"], "card"), 0.55)
    for x in p["frames"]:
        add(x["from"], "frame")
    for x in p["ui"]:
        for i, _ in enumerate(x.get("items", [])):
            add(x["from"] + 0.15 + i * 0.22, "pill", 0.35)
    for key, name in (("behind", "behind"), ("spotlight", "spotlight"), ("phones", "phone")):
        for x in p[key]:
            add(x["from"], name)
    for x in p["pops"]:
        add(x["at"], "pop")
    out, last = [], -1.0
    for t, key, vol in sorted(ev):
        s = cat[SFX_FOR[key]]
        start = max(0.0, t - s["sync"])
        if start - last > 0.1:
            out.append((start, ASSETS / s["file"], vol))
            last = start
    return out


def mix_audio(voice: pathlib.Path, events: list, music, duration: float, out: pathlib.Path) -> None:
    inputs, filters, labels = ["-i", str(voice)], [], []
    for i, (t, path, vol) in enumerate(events, start=1):
        inputs += ["-i", str(path)]
        ms = int(t * 1000)
        filters.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    base = "[0:a]"
    if music:
        m = len(events) + 1
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        # الموسيقى تنخفض تلقائياً حين يتكلم ساجد
        filters += [f"[{m}:a]aresample=48000,volume=0.16,atrim=0:{duration:.2f},afade=t=out:st={max(0, duration - 1.5):.2f}:d=1.5[mu]",
                    "[0:a]asplit=2[v1][v2]", "[mu][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck]"]
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


class Vision:
    """فصل الشخص (MediaPipe) وكشف الوجه — محلياً بلا إنترنت."""

    def __init__(self):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision as mv
        self.mp = mp
        self.seg = mv.ImageSegmenter.create_from_options(mv.ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path=str(MODELS / "selfie_segmenter.tflite")), output_confidence_masks=True))
        self.det = mv.FaceDetector.create_from_options(mv.FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=str(MODELS / "face_detector.tflite"))))

    def cutout(self, frame: pathlib.Path, out: pathlib.Path) -> pathlib.Path:
        import numpy as np
        from PIL import Image
        m = self.seg.segment(self.mp.Image.create_from_file(str(frame))).confidence_masks[0].numpy_view().squeeze()
        rgb = np.asarray(Image.open(frame).convert("RGB"))
        alpha = (np.clip((m - 0.35) / 0.3, 0, 1) * 255).astype("uint8")
        Image.fromarray(np.dstack([rgb, alpha])).save(out, compress_level=1)
        return out

    def face(self, frame: pathlib.Path):
        d = self.det.detect(self.mp.Image.create_from_file(str(frame))).detections
        if not d:
            return None
        b, s = d[0].bounding_box, d[0].categories[0].score
        return {"cx": b.origin_x + b.width / 2, "cy": b.origin_y + b.height / 2, "w": b.width, "score": s}

    def close(self):
        self.seg.close()
        self.det.close()


def vision(frames: list, cut_ranges: list, face_ranges: list, outdir: pathlib.Path):
    cut_idx, face_idx = needed_frames(cut_ranges, len(frames)), needed_frames(face_ranges, len(frames))
    if not cut_idx and not face_idx:
        return {}, {}
    v, cutouts, faces, last = Vision(), {}, {}, None
    outdir.mkdir(parents=True, exist_ok=True)
    for i in sorted(cut_idx | face_idx):
        if i in cut_idx:
            cutouts[i] = v.cutout(frames[i], outdir / f"{i:05d}.png")
        if i in face_idx and (i % 3 == 0 or last is None):
            cur = v.face(frames[i])
            if cur:
                last = cur if last is None else {k: last[k] * 0.6 + cur[k] * 0.4 for k in ("cx", "cy", "w")}
        if i in face_idx and last:
            faces[i] = last
    v.close()
    return cutouts, faces


def best_cover_frame(frames: list) -> int:
    """أفضل إطار للغلاف: وجه واضح وكبير وحاد، بعيداً عن البداية والنهاية."""
    import numpy as np
    from PIL import Image, ImageFilter
    v, best, best_i = Vision(), -1.0, len(frames) // 3
    for i in range(int(len(frames) * 0.1), int(len(frames) * 0.9), 15):
        f = v.face(frames[i])
        if not f:
            continue
        g = np.asarray(Image.open(frames[i]).convert("L").resize((270, 480)).filter(ImageFilter.FIND_EDGES), dtype=float)
        s = f["score"] * (f["w"] / 1080) * (g.var() ** 0.5)
        if s > best:
            best, best_i = s, i
    v.close()
    return best_i


def make_cover(br, data: dict, frame: pathlib.Path, outdir: pathlib.Path, out: pathlib.Path) -> None:
    """غلاف مصمم: الشخص مفرغ فوق خلفية المزاج، وعنوان ضخم خلفه، وتوقيع ساجد."""
    v = Vision()
    cut = v.cutout(frame, outdir / "cover-cut.png")
    face = v.face(frame)
    v.close()
    pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.add_init_script("window.__COVER = " + json.dumps({**data, "frame": frame.as_uri(), "cut": cut.as_uri(), "face": face}, ensure_ascii=False))
    pg.goto((HERE / "cover.html").as_uri())
    pg.wait_for_function("window.__ready === true && document.fonts.status === 'loaded'")
    pg.screenshot(path=str(out), type="jpeg", quality=93)
    pg.close()


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


def svg_markup(path: pathlib.Path) -> str:
    return re.sub(r"<\?xml[^>]*>", "", path.read_text(encoding="utf-8"))
