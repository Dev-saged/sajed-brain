#!/usr/bin/env python3
"""يبني مكتبة الأصول المفهرسة في assets/ من مصادر مجانية (يُعاد تشغيله لتحديثها):
- icons/   Phosphor (MIT) بوزنين duotone وfill — 1500+ أيقونة خطية
- icons3d/ Fluent Emoji 3D من Microsoft (MIT) — 1500+ مجسم ثلاثي الأبعاد مفرغ (WebP شفاف 256px)
- sfx/     SFX Kit (CC0) — 320 مؤثراً صوتياً بنقطة تزامن لكل صوت
- index.json فهرس موحّد: اسم، وصف، وسوم إنجليزية، كلمات عربية (CLDR + ar-concepts.json)
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


def build_icons3d(tmp: pathlib.Path, rev) -> list:
    pkg = npm_unpack("@lobehub/fluent-emoji-3d", tmp)
    cldr = npm_unpack("cldr-annotations-full", tmp, ["package/annotations/ar/", "package/annotations/en/"])
    ann = {lang: json.loads((cldr / "annotations" / lang / "annotations.json").read_text(encoding="utf-8"))["annotations"]["annotations"] for lang in ("ar", "en")}
    (OUT / "icons3d").mkdir(parents=True, exist_ok=True)
    entries, used = [], set()
    for f in sorted((pkg / "assets").glob("*.webp")):
        cps = f.stem.lower().split("-")
        if SKIN & set(cps) or not all(re.fullmatch(r"[0-9a-f]{2,6}", c) and int(c, 16) < 0x110000 for c in cps):
            continue
        ch = "".join(chr(int(c, 16)) for c in cps)
        key = ch.replace("️", "")
        en = ann["en"].get(key) or ann["en"].get(ch)
        if not en:
            continue
        name = slug(en["tts"][0])
        if not name or name in used:
            continue
        used.add(name)
        shutil.copyfile(f, OUT / "icons3d" / f"{name}.webp")
        ar = ann["ar"].get(key) or ann["ar"].get(ch) or {"default": [], "tts": []}
        terms = [name, *en.get("default", [])]
        entries.append({"id": name, "type": "icon3d", "file": f"icons3d/{name}.webp", "emoji": ch,
                        "en": terms, "ar": sorted(set(ar.get("tts", []) + ar.get("default", [])) | set(arabic_for(terms, rev)))})
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


def main() -> None:
    rev = concepts()
    for d in ("icons", "icons3d", "sfx"):
        shutil.rmtree(OUT / d, ignore_errors=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        entries = build_icons(tmp, rev) + build_icons3d(tmp, rev) + build_sfx(tmp, rev)
    (OUT / "index.json").write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    counts = {}
    for e in entries:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    print("✓ assets:", counts)


if __name__ == "__main__":
    main()
