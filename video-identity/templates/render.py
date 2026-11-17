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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("out")
    ap.add_argument("--preview", action="store_true")
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


if __name__ == "__main__":
    sys.exit(main())
