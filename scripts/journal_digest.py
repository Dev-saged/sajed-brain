#!/usr/bin/env python3
"""يضغط يوميات الأشهر المنتهية: journal/YYYY-MM.md → قسم في journal/digest.md والأصل إلى journal/archive/.
سطر اليومية: - [YYYY-MM-DD] @مشروع ✓|✗ نص #وسم"""
import argparse
import datetime
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINE = re.compile(r"^- \[(\d{4}-\d{2}-\d{2})\] @(\S+) (✓|✗) (.+)$")
TAG = re.compile(r"#[\w\-]+")
MAX_FAILS = 15
RECURRING = 3


def parse(text):
    return [m.groups() for m in map(LINE.match, text.splitlines()) if m]


def section(month, entries):
    ok = [e for e in entries if e[2] == "✓"]
    fails = [e for e in entries if e[2] == "✗"]
    projects = Counter(e[1] for e in entries)
    tags = Counter(t for e in fails for t in TAG.findall(e[3]))
    out = [f"## {month}",
           f"- {len(entries)} تسجيلاً (✓ {len(ok)} / ✗ {len(fails)}) · " + "، ".join(f"{p} {n}" for p, n in projects.most_common())]
    recurring = [f"{t}×{n}" for t, n in tags.most_common() if n >= RECURRING]
    if recurring:
        out.append("- مرشّحة لحارس/خطأ دائم (تكررت في الإخفاقات): " + "، ".join(recurring))
    if fails:
        out.append("- إخفاقات:")
        out += [f"  - [{d}] @{p} {t}" for d, p, _, t in fails[:MAX_FAILS]]
        if len(fails) > MAX_FAILS:
            out.append(f"  - … و{len(fails) - MAX_FAILS} أخرى في الأرشيف")
    return "\n".join(out) + "\n"


def run(root=ROOT, today=None):
    today = today or datetime.date.today()
    current = today.strftime("%Y-%m")
    jdir = pathlib.Path(root) / "journal"
    done = []
    for f in sorted(jdir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9].md")) if jdir.exists() else []:
        month = f.stem
        if month >= current:
            continue
        entries = parse(f.read_text(encoding="utf-8"))
        digest = jdir / "digest.md"
        text = digest.read_text(encoding="utf-8") if digest.exists() else "# يوميات مضغوطة\n\n"
        text = re.sub(rf"## {month}\n.*?(?=\n## |\Z)", "", text, flags=re.S).rstrip() + "\n\n" + section(month, entries)
        digest.write_text(text, encoding="utf-8")
        (jdir / "archive").mkdir(exist_ok=True)
        f.rename(jdir / "archive" / f.name)
        done.append(month)
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    done = run(a.root)
    print(f"journal: ضُغط {len(done)} شهر" + (f" ({', '.join(done)})" if done else ""))


if __name__ == "__main__":
    main()
