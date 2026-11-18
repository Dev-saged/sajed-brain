#!/usr/bin/env python3
"""خريطة الدماغ: يقرأ كل ملفات المعرفة ويربطها ببعض ← index/MAP.md.
لكل ملف: عنوانه، وصفه، أقسامه، ما يشير إليه، من يشير إليه، وأقرب 3 ملفات له بالمعنى.
يكشف الروابط المكسورة والملفات اليتيمة. بلا قيود حجم.
python3 scripts/brain_map.py [--check]"""
import argparse
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from brief import tokens  # noqa: E402

SKIP = {".git", "library", "journal", "__pycache__", "fonts", "index", "templates", "tests"}
REF = re.compile(r"(?<![\w\u0600-\u06FF])((?:\.?[A-Za-z0-9_\-]+/)*[A-Za-z0-9_\-]+\.(?:md|json))")
# ملفات تولّدها workflows أو تعيش داخل المشاريع لا في الدماغ
EXTERNAL = ("index/", "journal/", ".claude/", "docs/code-index.md", "work/")


def knowledge_files(root=ROOT):
    for f in sorted(root.rglob("*.md")):
        rel = f.relative_to(root)
        if not SKIP & set(rel.parts[:-1]) and not rel.parts[0].startswith("."):
            yield f


def describe(text):
    title, desc, heads = "", "", []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# ") and not title:
            title = s[2:].strip()
        elif s.startswith("## "):
            heads.append(s[3:].strip())
        elif s and not desc and title and not s.startswith(("#", "|", "-", "```")):
            desc = s.strip("_> ").strip()
    return title, desc[:160], heads


def resolve(ref, src, root):
    for base in (src.parent, src.parent.parent, root):
        p = (base / ref).resolve()
        if p.is_file() and root in p.parents:
            return p.relative_to(root).as_posix()
    hits = [f for f in root.rglob(pathlib.Path(ref).name) if f.as_posix().endswith("/" + ref) and ".git" not in f.parts]
    return hits[0].relative_to(root).as_posix() if len(hits) == 1 else None


def build(root=ROOT):
    files = list(knowledge_files(root))
    info, toks, out_links, broken = {}, {}, defaultdict(set), []
    for f in files:
        rel = f.relative_to(root).as_posix()
        text = f.read_text(encoding="utf-8")
        info[rel] = describe(text)
        toks[rel] = tokens(text)
        for ref in set(REF.findall(text)):
            if "/" not in ref and not (f.parent / ref).exists() and not (root / ref).exists():
                continue
            target = resolve(ref, f, root)
            if target and target != rel:
                out_links[rel].add(target)
            elif not target and "/" in ref and not ref.startswith(EXTERNAL):
                broken.append((rel, ref))
    in_links = defaultdict(set)
    for src, tgts in out_links.items():
        for t in tgts:
            in_links[t].add(src)
    related = {}
    for a in info:
        scores = []
        for b in info:
            if a != b and toks[a] and toks[b]:
                j = len(toks[a] & toks[b]) / len(toks[a] | toks[b])
                scores.append((j, b))
        related[a] = [b for j, b in sorted(scores, reverse=True)[:3] if j > 0.05]
    orphans = [r for r in info if r not in in_links and r not in ("README.md", "CLAUDE.md")]
    return info, out_links, in_links, related, broken, orphans


def render(data):
    info, out_links, in_links, related, broken, orphans = data
    groups = defaultdict(list)
    for rel in info:
        groups[rel.split("/")[0] if "/" in rel else "/"].append(rel)
    lines = ["# خريطة الدماغ (مولّدة — لا تُعدَّل يدوياً)",
             "_`python3 scripts/brain_map.py` يعيد بناءها يومياً. ابحث هنا عن الملف المناسب ثم افتحه وحده._", "",
             f"**{len(info)} ملف معرفة** · روابط مكسورة: {len(broken)} · ملفات يتيمة: {len(orphans)}", ""]
    for g in sorted(groups):
        lines.append(f"## {'الجذر' if g == '/' else g}")
        for rel in groups[g]:
            title, desc, heads = info[rel]
            lines.append(f"- **`{rel}`** — {title or rel}" + (f": {desc}" if desc else ""))
            if heads:
                lines.append(f"  - أقسام: {' · '.join(heads[:12])}")
            if out_links.get(rel):
                lines.append(f"  - يشير إلى: {', '.join(sorted(out_links[rel]))}")
            if in_links.get(rel):
                lines.append(f"  - يُشار إليه من: {', '.join(sorted(in_links[rel]))}")
            if related.get(rel):
                lines.append(f"  - قريب منه: {', '.join(related[rel])}")
        lines.append("")
    if broken:
        lines.append("## روابط مكسورة")
        lines += [f"- `{s}` ← `{r}`" for s, r in broken]
        lines.append("")
    if orphans:
        lines.append("## ملفات لا يشير إليها أحد (اربطها من README أو ملف قريب)")
        lines += [f"- `{o}`" for o in orphans]
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="فشل إن وُجدت روابط مكسورة")
    a = ap.parse_args()
    data = build()
    out = ROOT / "index" / "MAP.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(data[0])} ملف، {len(data[4])} رابط مكسور، {len(data[5])} يتيم")
    if a.check and data[4]:
        sys.exit(1)


if __name__ == "__main__":
    main()
