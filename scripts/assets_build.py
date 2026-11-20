#!/usr/bin/env python3
"""يبني مكتبة الأصول المفهرسة في assets/ من مصادر مجانية (يُعاد تشغيله لتحديثها):
- icons/   Phosphor (MIT) duotone وfill + Hugeicons (MIT) + MingCute (Apache-2.0) — أيقونات تصميم
- sfx/     SFX Kit (CC0) — 320 مؤثراً صوتياً بنقطة تزامن لكل صوت
- index.json فهرس موحّد: اسم، وصف، وسوم إنجليزية، كلمات عربية (ar-concepts.json)
لا إيموجي إطلاقاً (قرار ساجد 2026-11-20).
python3 scripts/assets_build.py
يتطلب: npm, node, git, ffmpeg"""
import json
import pathlib
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
SKIN = {"1f3fb", "1f3fc", "1f3fd", "1f3fe", "1f3ff"}
SFX_AR = {
    "whooshes": ["انتقال", "حركة", "هواء"], "swishes-and-zips": ["دخول", "خروج", "ظهور نص"], "swipes": ["سحب", "شاشة", "تطبيق"],
    "reverse-whooshes": ["تشويق", "تجميع"], "risers-and-fallers": ["تشويق", "صعود", "هبوط"], "impacts": ["ضربة", "تأكيد"],
    "cinematic-hits": ["ضربة سينمائية", "ذروة"], "booms-and-bass": ["انفجار", "ضربة عميقة"], "pops": ["ظهور", "فقاعة", "نقرة"],
    "shimmers": ["لمعة", "سحر", "بريق"], "interface": ["واجهة", "نقرة", "زر"], "notifications": ["إشعار", "تنبيه", "نجاح"],
    "digital": ["رقمي", "تقنية"], "data": ["بيانات", "معالجة"], "keyboard": ["كتابة", "لوحة مفاتيح"], "writing-and-drawing": ["كتابة", "قلم", "رسم"],
    "logo-stings": ["شعار", "افتتاحية", "خاتمة"], "mechanical": ["ميكانيكي", "آلة"], "foley": ["حركة طبيعية"], "everyday-props": ["أغراض"],
    "shape-changes": ["تحول شكل"], "tones": ["نغمة"], "money": ["مال", "فلوس", "دفع"], "appear-and-vanish": ["ظهور", "اختفاء"],
    "time": ["وقت", "ساعة"], "bounce-spin-zoom": ["ارتداد", "دوران", "زوم"], "phone": ["هاتف", "جوال", "رنين"], "celebration": ["احتفال", "نجاح", "فرح"],
}


def sh(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def npm_unpack(pkg: str, dest: pathlib.Path, members=None) -> pathlib.Path:
    name = sh("npm", "pack", "-s", pkg, cwd=dest).strip().splitlines()[-1]
    target = dest / pkg.replace("/", "_")
    with tarfile.open(dest / name) as tf:
        sel = [m for m in tf.getmembers() if members is None or any(m.name.startswith(x) for x in members)]
        tf.extractall(target, members=sel, filter="data")
    return target / "package"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def concepts():
    data = json.loads((OUT / "ar-concepts.json").read_text(encoding="utf-8"))
    rev = {}
    for ar, ens in data.items():
        if ar == "_":
            continue
        for en in ens:
            rev.setdefault(en, set()).add(ar)
    return rev


def arabic_for(terms, rev) -> list:
    out = set()
    for t in terms:
        for part in {t, *t.split("-")}:
            out |= rev.get(part, set())
    return sorted(out)


def build_icons(tmp: pathlib.Path, rev) -> list:
    pkg = npm_unpack("@phosphor-icons/core", tmp)
    meta = json.loads(sh("node", "-e", "import('./dist/index.mjs').then(m=>console.log(JSON.stringify(m.icons)))", cwd=pkg))
    entries = []
    for w in ("duotone", "fill"):
        (OUT / "icons" / w).mkdir(parents=True, exist_ok=True)
    for ic in meta:
        n = ic["name"]
        for w in ("duotone", "fill"):
            src = pkg / "assets" / w / f"{n}-{w}.svg"
            if src.exists():
                shutil.copyfile(src, OUT / "icons" / w / f"{n}.svg")
        terms = [n, *ic.get("tags", []), *ic.get("categories", [])]
        entries.append({"id": n, "type": "icon", "file": f"icons/duotone/{n}.svg", "en": terms, "ar": arabic_for(terms, rev)})
    return entries


def build_sfx(tmp: pathlib.Path, rev) -> list:
    sh("git", "clone", "-q", "--depth", "1", "https://github.com/wyzowl/sfx-kit", str(tmp / "sfx-kit"))
    data = json.loads((tmp / "sfx-kit" / "sounds.json").read_text(encoding="utf-8"))["sounds"]
    entries = []
    for s in data:
        dest = OUT / "sfx" / s["category"] / f"{s['id']}.ogg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "sfx-kit" / s["file"]), "-c:a", "libvorbis", "-q:a", "5", str(dest))
        terms = [s["id"], s["category"], *s.get("tags", [])]
        entries.append({"id": s["id"], "type": "sfx", "file": f"sfx/{s['category']}/{s['id']}.ogg", "category": s["category"],
                        "desc": s["description"], "use_for": s.get("use_for", []), "avoid_for": s.get("avoid_for", []),
                        "duration": s["duration"], "sync": s.get("sync", {}).get("at", 0.0),
                        "en": terms, "ar": sorted(set(SFX_AR.get(s["category"], [])) | set(arabic_for(terms, rev)))})
    return entries


KENNEY_AR = {"click": ["نقرة", "زر"], "mouseclick": ["نقرة"], "mouserelease": ["نقرة"], "rollover": ["مرور", "تحويم"], "switch": ["مفتاح", "تبديل"],
             "toggle": ["تبديل"], "tick": ["تكة", "عداد"], "select": ["اختيار"], "confirmation": ["تأكيد", "نجاح"], "error": ["خطأ", "تنبيه"],
             "question": ["سؤال"], "open": ["فتح", "ظهور"], "close": ["إغلاق", "اختفاء"], "maximize": ["تكبير", "ظهور"], "minimize": ["تصغير", "اختفاء"],
             "drop": ["إسقاط"], "glass": ["زجاج", "لمعة"], "glitch": ["تشويش", "رقمي"], "scratch": ["خدش"], "scroll": ["تمرير"], "back": ["رجوع"],
             "bong": ["رنة"], "pluck": ["نقرة وتر"]}


def build_kenney(tmp: pathlib.Path, rev) -> list:
    """Kenney Interface Sounds + UI Audio (CC0) — نقرات وأصوات واجهة لعناصر UI والكتابة."""
    entries = []
    for repo in ("kenney-interface-sounds", "kenney-ui-audio"):
        sh("git", "clone", "-q", "--depth", "1", f"https://github.com/Calinou/{repo}", str(tmp / repo))
        for f in sorted((tmp / repo).rglob("*")):
            if f.suffix.lower() not in (".wav", ".ogg"):
                continue
            base = re.sub(r"[_\d]+$", "", f.stem)
            sid = f"kenney-{slug(f.stem)}"
            dest = OUT / "sfx" / "interface-kenney" / f"{sid}.ogg"
            dest.parent.mkdir(parents=True, exist_ok=True)
            sh("ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-c:a", "libvorbis", "-q:a", "5", str(dest))
            dur = float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dest)).strip() or 0)
            entries.append({"id": sid, "type": "sfx", "file": f"sfx/interface-kenney/{sid}.ogg", "category": "interface-kenney",
                            "desc": f"Kenney UI sound: {base}", "use_for": [], "avoid_for": [], "duration": round(dur, 3), "sync": 0.0,
                            "en": [sid, base, "ui", "interface"], "ar": sorted(set(KENNEY_AR.get(base, ["واجهة"])) | set(arabic_for([base], rev)))})
    return entries


ICONIFY = {"hugeicons": "MIT", "mingcute": "Apache-2.0"}


def build_iconify(tmp: pathlib.Path, rev) -> list:
    """مجموعات أيقونات تصميم حديثة (Iconify JSON): Hugeicons (خطية حديثة) وMingCute (مصمتة وخطية)."""
    entries = []
    for name, lic in ICONIFY.items():
        pkg = npm_unpack(f"@iconify-json/{name}", tmp)
        data = json.loads((pkg / "icons.json").read_text(encoding="utf-8"))
        w, h = data.get("width", 24), data.get("height", 24)
        out = OUT / "icons" / name
        out.mkdir(parents=True, exist_ok=True)
        for icon, body in data["icons"].items():
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {body.get("width", w)} {body.get("height", h)}">{body["body"]}</svg>'
            (out / f"{icon}.svg").write_text(svg, encoding="utf-8")
            terms = [icon, *[t for t in icon.split("-") if not t.isdigit()]]
            entries.append({"id": f"{name}-{icon}", "type": "icon", "set": name, "license": lic, "file": f"icons/{name}/{icon}.svg",
                            "en": terms, "ar": arabic_for(terms, rev)})
    return entries


def main() -> None:
    rev = concepts()
    for d in ("icons", "sfx"):
        shutil.rmtree(OUT / d, ignore_errors=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        entries = build_icons(tmp, rev) + build_sfx(tmp, rev) + build_kenney(tmp, rev) + build_iconify(tmp, rev)
    (OUT / "index.json").write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    counts = {}
    for e in entries:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    print("✓ assets:", counts)


if __name__ == "__main__":
    main()
