#!/usr/bin/env python3
"""ابحث في مكتبة الأصول بالعربي أو الإنجليزي — بلا قراءة الفهرس كاملاً.
python3 assets/find.py قلب                 ← أفضل الأيقونات/المجسمات/الأصوات
python3 assets/find.py "كاسة شاي" --type icon -n 3
python3 assets/find.py انتقال --type sfx
الأنواع: icon (Phosphor + ما رفعه ساجد) · sfx · music · font (لا إيموجي إطلاقاً)"""
import argparse
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
DIAC = re.compile(r"[ً-ْـ]")


def norm(s: str) -> str:
    """توحيد العربي: بلا تشكيل/تطويل، الألفات والتاء المربوطة والياء، وبلا (ال) و(و) في البداية."""
    s = DIAC.sub("", s.lower().strip())
    s = re.sub("[إأآٱ]", "ا", s).replace("ة", "ه").replace("ى", "ي")
    for p in ("وال", "بال", "فال", "لل", "ال", "و"):
        if s.startswith(p) and len(s) - len(p) >= 2:
            return s[len(p):]
    return s


def score(entry: dict, words: list) -> float:
    total = 0.0
    ar = [norm(x) for x in entry.get("ar", [])]
    en = [x.lower() for x in entry.get("en", [])]
    for w in words:
        best = 0.0
        for a in ar:
            if a == w:
                best = max(best, 10)
            elif w in a.split():
                best = max(best, 7)
            elif len(w) > 2 and (a.startswith(w) or w.startswith(a)):
                best = max(best, 4)
        for e in en:
            if e == w:
                best = max(best, 9 if e == en[0] else 6)
            elif len(w) > 2 and w in e:
                best = max(best, 3)
        total += best
    return total


def targets(words: list) -> set:
    """الكلمات العربية ← أسماء إنجليزية مقصودة (ar-concepts.json) لتقديم الأيقونة الأدق."""
    con = json.loads((HERE / "ar-concepts.json").read_text(encoding="utf-8"))
    out = set()
    for ar, ens in con.items():
        if ar != "_" and norm(ar) in words:
            out |= set(ens)
    return out


def find(query: str, kind: str = None, n: int = 5) -> list:
    entries = json.loads((HERE / "index.json").read_text(encoding="utf-8"))
    words = [norm(w) for w in query.split() if w.strip()]
    tg = targets(words) | set(words)
    boost = lambda e: 12 if e["id"] in tg else 4 if tg & set(e["id"].split("-")) else 0
    # ما رفعه ساجد يتقدّم عند التطابق
    mine = lambda e: 5 if e.get("source") == "sajed" else 0
    ranked = sorted(((score(e, words) + boost(e) + mine(e) * (score(e, words) > 0), e) for e in entries if not kind or e["type"] == kind), key=lambda x: (-x[0], len(x[1]["id"])))
    root = lambda f: (HERE.parent if f.startswith("video-identity/") else HERE) / f
    return [dict(e, score=s, path=str(root(e["file"]))) for s, e in ranked[:n] if s > 0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--type", choices=["icon", "sfx", "music", "font", "image", "text-motion", "transitions", "refs"])
    ap.add_argument("-n", type=int, default=5)
    a = ap.parse_args()
    for r in find(a.query, a.type, a.n):
        extra = f" · {r['desc']}" if r["type"] == "sfx" else f" · {' '.join(r['ar'][:5])}"
        print(f"{r['score']:>4.0f}  {r['type']:<6} {r['id']:<34} {r['file']}{extra}")


if __name__ == "__main__":
    main()
