#!/usr/bin/env python3
"""مكتبة مراجع الموشن: يحلل كل فيديو مرجعي جديد مرة واحدة ويحفظ خلاصته ليقرأها Claude بدل الفيديو.

المصادر: ملفات في references/motion/inbox/ أو روابط (Google Drive أو مباشرة) سطراً سطراً في references/motion/links.txt
الناتج لكل مرجع: references/motion/refs/<slug>/sheet.jpg (لقطات من كل مشهد) + analysis.json
+ سطر في references/motion/notes.md بالقياسات وعلامة "⏳ يحتاج تفسير" حتى يكتب Claude التقنية بكلمات.
python3 scripts/motion_refs.py [--keep-source]"""
import argparse
import datetime
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOTION = ROOT / "video-identity" / "references" / "motion"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
PENDING = "⏳ يحتاج تفسير"
NOTES_HEAD = ("# ملاحظات مراجع الموشن\n"
              "_سطر لكل فيديو مرجعي. القياسات تُكتب آلياً؛ Claude يستبدل \"⏳ يحتاج تفسير\" بالتقنية وطريقة تطبيقها بهويتنا "
              "بعد النظر إلى `refs/<slug>/sheet.jpg` فقط. المصطلحات من `LEXICON.md`._\n\n"
              "| المرجع | المدة | قطعات/10ث | الحركة | الألوان | التقنية والتطبيق عندنا |\n|---|---|---|---|---|---|\n")
DRIVE = re.compile(r"(?:/d/|id=)([\w-]{20,})")


def run(*args) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True).stderr


def probe(path: pathlib.Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    num, den = (s.get("r_frame_rate") or "30/1").split("/")
    return {"width": s["width"], "height": s["height"], "fps": round(int(num) / max(1, int(den)), 2),
            "duration": round(float(j["format"]["duration"]), 2)}


def cuts(path: pathlib.Path, threshold: float = 0.32) -> list:
    log = run("ffmpeg", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-")
    return [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", log)]


def motion_energy(path: pathlib.Path) -> float:
    """متوسط فرق الإطارات المتتالية (0–255) على نسخة صغيرة رمادية بمعدل 5 إطارات/ث."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", "fps=5,scale=32:56,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = 32 * 56
    frames = [raw[i:i + n] for i in range(0, len(raw) - n + 1, n)]
    if len(frames) < 2:
        return 0.0
    diffs = [sum(abs(a - b) for a, b in zip(f1, f2)) / n for f1, f2 in zip(frames, frames[1:])]
    return round(sum(diffs) / len(diffs), 1)


def palette(sheet: pathlib.Path, k: int = 5) -> list:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(sheet), "-vf", "scale=48:-1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    buckets = {}
    for i in range(0, len(raw) - 2, 3):
        key = tuple(c // 32 * 32 + 16 for c in raw[i:i + 3])
        buckets[key] = buckets.get(key, 0) + 1
    top = sorted(buckets.items(), key=lambda kv: -kv[1])[:k]
    return ["#%02X%02X%02X" % c for c, _ in top]


def sample_times(duration: float, cut_list: list, n: int = 12) -> list:
    """منتصف كل مشهد (حتى n)، أو توزيع متساوٍ لو المشاهد قليلة."""
    edges = [0.0] + cut_list + [duration]
    mids = [round((a + b) / 2, 2) for a, b in zip(edges, edges[1:]) if b - a > 0.15]
    if len(mids) >= n:
        step = len(mids) / n
        return [mids[int(i * step)] for i in range(n)]
    return [round(duration * (i + 0.5) / n, 2) for i in range(n)]


def contact_sheet(path: pathlib.Path, times: list, out: pathlib.Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(times):
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(path), "-frames:v", "1",
                            "-vf", "scale=240:-2,pad=240:427:(ow-iw)/2:(oh-ih)/2", f"{td}/{i:02d}.jpg"], check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "1", "-i", f"{td}/%02d.jpg",
                        "-vf", "tile=6x2:padding=6:color=0x111111", "-frames:v", "1", "-q:v", "4", str(out)], check=True)


def pace_label(per10: float) -> str:
    return "هادئ" if per10 < 1.5 else "متوسط" if per10 < 4 else "سريع"


def motion_label(e: float) -> str:
    return "ثابت" if e < 4 else "متوسط" if e < 12 else "عنيف"


def analyze(path: pathlib.Path, slug: str) -> dict:
    info = probe(path)
    cl = cuts(path)
    folder = MOTION / "refs" / slug
    folder.mkdir(parents=True, exist_ok=True)
    contact_sheet(path, sample_times(info["duration"], cl), folder / "sheet.jpg")
    per10 = round(len(cl) / max(info["duration"], 0.1) * 10, 1)
    energy = motion_energy(path)
    data = {**info, "slug": slug, "cuts": cl, "cuts_per_10s": per10, "pace": pace_label(per10),
            "avg_shot": round(info["duration"] / (len(cl) + 1), 2), "motion_energy": energy,
            "motion": motion_label(energy), "palette": palette(folder / "sheet.jpg"),
            "analyzed": datetime.date.today().isoformat(), "interpretation": None}
    (folder / "analysis.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def note_line(d: dict) -> str:
    return (f"| `{d['slug']}` | {d['duration']}ث | {d['cuts_per_10s']} ({d['pace']}) | {d['motion']} ({d['motion_energy']}) "
            f"| {' '.join(d['palette'][:4])} | {PENDING} |\n")


def fetch(url: str, dest: pathlib.Path) -> pathlib.Path:
    m = DRIVE.search(url)
    if m:
        url = f"https://drive.usercontent.google.com/download?id={m.group(1)}&export=download&confirm=t"
    with urllib.request.urlopen(url, timeout=300) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return dest


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", name.lower()).strip("-")[:40]
    return f"{datetime.date.today().isoformat()}-{s or 'ref'}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-source", action="store_true", help="لا تحذف الفيديو من inbox بعد التحليل")
    a = ap.parse_args()
    inbox = MOTION / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    done_path = MOTION / "processed.json"
    done = json.loads(done_path.read_text(encoding="utf-8")) if done_path.exists() else {}
    notes = MOTION / "notes.md"
    text = notes.read_text(encoding="utf-8") if notes.exists() else NOTES_HEAD
    if "| المرجع |" not in text:
        text = NOTES_HEAD
    new = 0
    with tempfile.TemporaryDirectory() as td:
        jobs = [(f.name, f, None) for f in sorted(inbox.iterdir()) if f.suffix.lower() in VIDEO_EXT and f.name not in done]
        links = MOTION / "links.txt"
        if links.exists():
            for line in links.read_text(encoding="utf-8").splitlines():
                url = line.strip()
                if url and not url.startswith("#") and url not in done:
                    jobs.append((url, None, url))
        for key, path, url in jobs:
            try:
                if url:
                    m = DRIVE.search(url)
                    path = fetch(url, pathlib.Path(td) / f"{m.group(1) if m else 'ref'}.mp4")
                slug = slugify(path.stem)
                d = analyze(path, slug)
            except (subprocess.CalledProcessError, OSError, KeyError, ValueError) as e:
                print(f"✗ {key}: {e}")
                continue
            text += note_line(d)
            done[key] = slug
            new += 1
            print(f"✓ {key} ← refs/{slug}")
            if path.parent == inbox and not a.keep_source:
                path.unlink()
    notes.write_text(text, encoding="utf-8")
    done_path.write_text(json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending = text.count(PENDING)
    print(f"مراجع جديدة: {new} · بانتظار تفسير Claude: {pending}")


if __name__ == "__main__":
    main()
