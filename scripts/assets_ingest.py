#!/usr/bin/env python3
"""يفهرس ما يرفعه ساجد في assets/incoming/<نوع>/ (من Drive «sajed-brain مكتبة المونتاج» أو مباشرة للريبو).
الأنواع: fonts · icons · sfx · music · text-motion · transitions · refs · images (صور أبطال المشاهد)
لكل ملف سطر في assets/incoming/meta.json: {"اسم الملف": {"ar": ["كلمات"], "desc": "وصف عربي", "mood": "cozy"}}
يُكتب الوصف بعد مشاهدة/سماع الملف. بعدها:
python3 scripts/assets_ingest.py        ← يحوّل وينقل ويضيف للفهرس ويُفرغ incoming
"""
import json
import pathlib
import re
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
IN = ASSETS / "incoming"
FONTS = ROOT / "video-identity" / "templates" / "fonts"
REFS = ROOT / "video-identity" / "references" / "motion" / "inbox"
AUDIO = {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".aac"}
VIDEO = {".mp4", ".mov", ".webm", ".mkv", ".gif", ".json", ".lottie"}


def slug(s: str) -> str:
    return re.sub(r"[^\w]+", "-", s.lower()).strip("-")


def ff(*args) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def duration(path: pathlib.Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 2)
    except ValueError:
        return 0.0


def ingest_one(kind: str, f: pathlib.Path, meta: dict) -> dict:
    m = meta.get(f.name, {})
    sid = slug(f.stem)
    base = {"id": f"u-{sid}", "ar": m.get("ar", []), "en": [sid], "desc": m.get("desc", ""), "source": "sajed"}
    ext = f.suffix.lower()
    if kind == "fonts" and ext in {".ttf", ".otf", ".woff", ".woff2"}:
        dest = FONTS / f"{sid}{'.woff2' if ext == '.woff2' else ext}"
        shutil.copyfile(f, dest)
        return {**base, "type": "font", "file": str(dest.relative_to(ROOT)), "family": m.get("family", f.stem)}
    if kind == "icons" and ext == ".svg":
        dest = ASSETS / "icons" / "custom" / f"{sid}.svg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        svg = re.sub(r'fill="#[0-9a-fA-F]{3,6}"', 'fill="currentColor"', f.read_text(encoding="utf-8"))
        dest.write_text(svg, encoding="utf-8")
        return {**base, "type": "icon", "file": str(dest.relative_to(ASSETS))}
    if kind in ("sfx", "music") and ext in AUDIO:
        dest = ASSETS / kind / "custom" / f"{sid}.ogg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        ff("-i", str(f), "-c:a", "libvorbis", "-q:a", "5", str(dest))
        return {**base, "type": kind, "file": str(dest.relative_to(ASSETS)), "duration": duration(dest),
                "sync": m.get("sync", 0.0), "mood": m.get("mood"), "category": "custom"}
    if kind == "images" and ext in {".png", ".jpg", ".jpeg", ".webp"}:
        dest = ASSETS / "images" / f"{sid}.webp"
        dest.parent.mkdir(parents=True, exist_ok=True)
        ff("-i", str(f), "-vf", "scale='min(1600,iw)':-2", "-q:v", "85", str(dest))
        return {**base, "type": "image", "file": str(dest.relative_to(ASSETS))}
    if kind in ("text-motion", "transitions", "refs") and ext in VIDEO:
        REFS.mkdir(parents=True, exist_ok=True)
        if ext in {".mp4", ".mov", ".webm", ".mkv"}:
            # المستودع خفيف: 1080 بالارتفاع الأقصى، H.264، بلا تكبير
            dest = REFS / f"{kind}-{sid}.mp4"
            ff("-i", str(f), "-vf", "scale='min(1080,iw)':-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-c:a", "aac", "-b:a", "128k", str(dest))
        else:
            dest = REFS / f"{kind}-{sid}{ext}"
            shutil.copyfile(f, dest)
        return {**base, "type": kind, "file": str(dest.relative_to(ROOT))}
    raise ValueError(f"نوع غير مدعوم: {kind}/{f.name}")


def main() -> None:
    meta_path = IN / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    index = json.loads((ASSETS / "index.json").read_text(encoding="utf-8"))
    known = {e["id"] for e in index}
    added, missing = [], []
    for folder in sorted(p for p in IN.iterdir() if p.is_dir()) if IN.exists() else []:
        for f in sorted(folder.iterdir()):
            if not f.is_file():
                continue
            if f.name not in meta:
                missing.append(f"{folder.name}/{f.name}")
                continue
            e = ingest_one(folder.name, f, meta)
            if e["id"] not in known:
                index.append(e)
                known.add(e["id"])
            added.append(e["id"])
            f.unlink()
    (ASSETS / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    for name in added:
        meta.pop(next((k for k in meta if slug(pathlib.Path(k).stem) == name[2:]), ""), None)
    if IN.exists():
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"✓ أُضيف {len(added)}" + (f" · بلا وصف (أضفه في meta.json): {', '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
