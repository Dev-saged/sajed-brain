#!/usr/bin/env python3
"""يجلب كل الخطوط العربية المجانية المهمة (Google Fonts عبر Fontsource، رخصة OFL) إلى قوالب الفيديو،
ويسجّلها في fonts.css وفي assets/index.json بوصف عربي للأسلوب حتى تُختار بالمعنى.
python3 scripts/fonts_build.py   (يتطلب npm)"""
import json
import pathlib
import re
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "video-identity" / "templates" / "fonts"
CSS = ROOT / "video-identity" / "templates" / "fonts.css"
INDEX = ROOT / "assets" / "index.json"

# slug: (الاسم، أسلوب عربي، أوزان)
FAMILIES = {
    "amiri": ("Amiri", ["نسخ", "كلاسيكي", "قرآني", "ديني", "فخم"], [400, 700]),
    "noto-naskh-arabic": ("Noto Naskh Arabic", ["نسخ", "قراءة", "رسمي"], [400, 700]),
    "scheherazade-new": ("Scheherazade New", ["نسخ", "تقليدي", "ديني"], [400, 700]),
    "lateef": ("Lateef", ["نسخ", "ناعم"], [400, 700]),
    "markazi-text": ("Markazi Text", ["نسخ", "صحفي", "تحريري"], [400, 700]),
    "aref-ruqaa": ("Aref Ruqaa", ["رقعة", "يدوي", "تراثي"], [400, 700]),
    "noto-kufi-arabic": ("Noto Kufi Arabic", ["كوفي", "تقني", "عناوين"], [400, 700, 900]),
    "kufam": ("Kufam", ["كوفي", "هندسي", "حديث"], [400, 700]),
    "reem-kufi": ("Reem Kufi", ["كوفي", "هندسي", "أنيق"], [400, 700]),
    "cairo": ("Cairo", ["حديث", "واجهات", "عناوين"], [400, 700, 900]),
    "tajawal": ("Tajawal", ["حديث", "نظيف", "واجهات"], [400, 700, 900]),
    "almarai": ("Almarai", ["حديث", "نظيف", "سعودي"], [400, 700, 800]),
    "readex-pro": ("Readex Pro", ["حديث", "تقني", "قراءة"], [400, 700]),
    "rubik": ("Rubik", ["حديث", "مدور", "ودود"], [400, 700, 900]),
    "mada": ("Mada", ["حديث", "خفيف"], [400, 700, 900]),
    "harmattan": ("Harmattan", ["نسخ", "بسيط"], [400, 700]),
    "zain": ("Zain", ["حديث", "أنيق", "عرض"], [400, 700, 800]),
    "beiruti": ("Beiruti", ["حديث", "قوي", "عناوين"], [400, 700, 900]),
    "lemonada": ("Lemonada", ["مدور", "مرح", "ودود"], [400, 700]),
    "baloo-bhaijaan-2": ("Baloo Bhaijaan 2", ["مدور", "مرح", "أطفال"], [400, 700, 800]),
    "marhey": ("Marhey", ["مرح", "يدوي", "عرض"], [400, 700]),
    "rakkas": ("Rakkas", ["عرض", "سينمائي", "عناوين ضخمة"], [400]),
    "jomhuria": ("Jomhuria", ["عرض", "ضخم", "ملصقات"], [400]),
    "katibeh": ("Katibeh", ["عرض", "يدوي", "تراثي"], [400]),
    "mirza": ("Mirza", ["نسخ", "عرض", "أدبي"], [400, 700]),
    "blaka": ("Blaka", ["عرض", "قوطي", "فني"], [400]),
    "vibes": ("Vibes", ["عرض", "مرح", "شبابي"], [400]),
    "playpen-sans-arabic": ("Playpen Sans Arabic", ["يدوي", "أطفال", "ودود"], [400, 700]),
    "handjet": ("Handjet", ["رقمي", "بكسل", "تقني"], [400, 700]),
    "noto-sans-arabic": ("Noto Sans Arabic", ["حديث", "محايد", "قراءة"], [400, 700, 900]),
    "qahiri": ("Qahiri", ["كوفي", "تراثي", "عرض"], [400]),
    "badeen-display": ("Badeen Display", ["عرض", "ضخم", "عناوين"], [400]),
    "ruwudu": ("Ruwudu", ["نسخ", "أدبي"], [400, 700]),
}


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout


def main() -> None:
    FONTS.mkdir(parents=True, exist_ok=True)
    css = CSS.read_text(encoding="utf-8")
    index = [e for e in json.loads(INDEX.read_text(encoding="utf-8")) if e.get("type") != "font" or e.get("source") == "sajed"]
    added, failed = 0, []
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for slug, (name, tags, weights) in FAMILIES.items():
            try:
                tgz = sh("npm", "pack", "-s", f"@fontsource/{slug}", cwd=td).strip().splitlines()[-1]
            except subprocess.CalledProcessError:
                failed.append(name)
                continue
            with tarfile.open(td / tgz) as tf:
                files = {pathlib.Path(m.name).name: m for m in tf.getmembers() if m.name.endswith(".woff2")}
                got = []
                for w in weights:
                    for sub in ("arabic", "latin"):
                        fn = f"{slug}-{sub}-{w}-normal.woff2"
                        if fn not in files:
                            continue
                        (FONTS / fn).write_bytes(tf.extractfile(files[fn]).read())
                        got.append(fn)
                        rng = "U+0600-06FF,U+0750-077F,U+0870-089F,U+08A0-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FEFF" if sub == "arabic" else "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2212,U+FEFF,U+FFFD"
                        rule = f"@font-face{{font-family:'{name}';font-weight:{w};font-display:block;src:url(fonts/{fn}) format('woff2');unicode-range:{rng}}}"
                        if f"url(fonts/{fn})" not in css:
                            css += rule + "\n"
            if any("-arabic-" in g for g in got):
                index.append({"id": f"font-{slug}", "type": "font", "family": name, "file": f"video-identity/templates/fonts/{slug}-arabic-{weights[0]}-normal.woff2",
                              "weights": weights, "en": [slug, name.lower()], "ar": tags, "desc": "، ".join(tags)})
                added += 1
            else:
                failed.append(name)
            (td / tgz).unlink()
    CSS.write_text(css, encoding="utf-8")
    INDEX.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"✓ خطوط: {added}" + (f" · لم تتوفر: {', '.join(failed)}" if failed else ""))


if __name__ == "__main__":
    main()
