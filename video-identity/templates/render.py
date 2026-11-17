#!/usr/bin/env python3
"""يركّب فيديو بهوية ساجد من content.json واحد.

python3 video-identity/templates/render.py content.json out.mp4 [--preview]
--preview: يحفظ لقطات PNG عند أزحم لحظة في كل مشهد بدل الفيديو.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SCENES = ("hook", "demo", "outro")
REQUIRED = {"headline": str, "demo": dict}
DEMO_REQUIRED = ("before", "after", "headline", "caption")


def load_brand(content_path: pathlib.Path) -> dict:
    tokens = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    icons = json.loads((ROOT / "icons" / "platforms.json").read_text(encoding="utf-8"))
    content = json.loads(content_path.read_text(encoding="utf-8"))
    validate(content)
    shot = content["demo"].get("screenshot")
    shot_path = (content_path.parent / shot).resolve() if shot else None
    if shot_path and not shot_path.is_file():
        raise SystemExit(f"screenshot غير موجود: {shot_path}")
    return {
        "tokens": tokens,
        "icons": icons,
        "content": content,
        "assets": {
            "portrait": (ROOT / tokens["identity"]["portrait"]).as_uri(),
            "screenshot": shot_path.as_uri() if shot_path else None,
        },
    }


def validate(content: dict) -> None:
    for key, kind in REQUIRED.items():
        if not isinstance(content.get(key), kind):
            raise SystemExit(f"content.json: الحقل {key} مفقود أو بنوع خاطئ")
    demo = content["demo"]
    missing = [k for k in DEMO_REQUIRED if k not in demo]
    if missing:
        raise SystemExit(f"content.json: demo ينقصه {', '.join(missing)}")
    ratio = demo["after"].get("ratio", 1)
    if not 0 < ratio <= 1:
        raise SystemExit("content.json: demo.after.ratio بين 0 و1")


def film(page, scene: str, out: pathlib.Path, fps: int) -> None:
    page.goto((HERE / "video.html").as_uri() + f"?scene={scene}")
    page.wait_for_function("document.fonts.status === 'loaded' && window.__duration")
    page.evaluate("document.fonts.ready")
    dur = page.evaluate("window.__duration")
    frames = int(dur / 1000 * fps)
    tmp = out.with_name(out.stem + ".part.mp4")
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps),
         "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", str(tmp)],
        stdin=subprocess.PIPE,
    )
    for i in range(frames):
        page.evaluate(f"window.__seek({i * 1000 / fps})")
        enc.stdin.write(page.screenshot(type="jpeg", quality=92))
    enc.stdin.close()
    if enc.wait() != 0:
        raise SystemExit(f"ffmpeg فشل في مشهد {scene}")
    tmp.rename(out)


LIBRARY = ROOT / "library"
INDEX_HEAD = "# مكتبة فيديوهات ساجد\n_سطر لكل فيديو. اقرأ هذا الفهرس فقط؛ افتح مجلد فيديو عند الحاجة لتكراره أو التعلّم منه._\n\n| التاريخ | المجلد | الصيغة | الخطّاف | النتيجة |\n|---|---|---|---|---|\n"


def index_line(date: str, slug: str, content: dict) -> str:
    hook = " ".join(content["headline"].replace("[", "").replace("]", "").replace("{", "").replace("}", "").split())
    cell = lambda s: str(s).replace("|", "/")
    return f"| {date} | `{date}-{slug}` | {cell(content.get('format', '-'))} | {cell(hook)} | — |\n"


def archive(content_path: pathlib.Path, content: dict, video: pathlib.Path) -> pathlib.Path:
    """يحفظ ما يكفي لإعادة إنتاج الفيديو والتعلّم منه: المحتوى + لقطة مصغّرة + سطر فهرس."""
    date = __import__("datetime").date.today().isoformat()
    folder = LIBRARY / f"{date}-{video.stem}"
    folder.mkdir(parents=True, exist_ok=True)
    saved = json.loads(json.dumps(content))
    shot = content["demo"].get("screenshot")
    if shot:
        src = (content_path.parent / shot).resolve()
        dst = folder / ("screenshot" + src.suffix)
        shutil.copyfile(src, dst)
        saved["demo"]["screenshot"] = dst.name
    (folder / "content.json").write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    d = {"hook": 3.5, "demo": 5, "outro": 4.5, **content.get("durations", {})}
    marks = [d["hook"] - 0.3, d["hook"] + d["demo"] - 0.3, sum(d[s] for s in SCENES) - 0.3]
    inputs = sum((["-ss", f"{m:.2f}", "-i", str(video)] for m in marks), [])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
                    "[0:v][1:v][2:v]hstack=3,scale=540:-2", "-frames:v", "1", "-q:v", "4",
                    str(folder / "sheet.jpg")], check=True)
    index = LIBRARY / "index.md"
    text = index.read_text(encoding="utf-8") if index.exists() else INDEX_HEAD
    index.write_text(text + index_line(date, video.stem, content), encoding="utf-8")
    return folder


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--no-archive", action="store_true", help="لا تحفظ في library/")
    args = ap.parse_args()

    brand = load_brand(pathlib.Path(args.content).resolve())
    v = brand["tokens"]["video"]
    out = pathlib.Path(args.out).resolve()
    if not args.preview and not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg غير مثبت")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        browser = pw.chromium.launch(args=["--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": v["width"], "height": v["height"]}, device_scale_factor=1)
        page.add_init_script("window.__BRAND = " + json.dumps(brand, ensure_ascii=False))
        parts = []
        for scene in SCENES:
            if args.preview:
                page.goto((HERE / "video.html").as_uri() + f"?scene={scene}")
                page.wait_for_function("document.fonts.status === 'loaded' && window.__duration")
                page.evaluate("window.__seek(window.__duration - 200)")
                shot = out.with_name(f"{out.stem}-{scene}.png")
                page.screenshot(path=str(shot))
                print(shot)
                continue
            part = pathlib.Path(td) / f"{scene}.mp4"
            film(page, scene, part, v["fps"])
            parts.append(part)
        browser.close()
        if args.preview:
            return
        lst = pathlib.Path(td) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
        tmp = out.with_name(out.stem + ".part.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(lst), "-c", "copy", str(tmp)], check=True)
        tmp.rename(out)
    print(out)
    if not args.no_archive:
        print(archive(pathlib.Path(args.content).resolve(), brand["content"], out))


if __name__ == "__main__":
    sys.exit(main())
