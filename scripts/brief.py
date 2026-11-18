#!/usr/bin/env python3
"""موجز مهمة: يختار من الدماغ فقط المقاطع ذات الصلة بالمهمة ضمن ميزانية أحرف (اقتصاد توكنز).
brief.py --task "أضف وحدة ديون مع Room migration" [--project qayd] [--budget 2500]"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ["preferences.md", "mistakes.md", "ideas.md", "projects/index.md"]
# كل ملفات المعرفة تُبحث، بلا حدود حجم
KNOWLEDGE_DIRS = ["features", "playbooks", "video-identity", "docs"]
TOKEN = re.compile(r"[a-zA-Z0-9]{3,}|[؀-ۿ]{3,}")
DIACRITICS = re.compile(r"[ً-ْـ]")
STOP = {"the", "and", "for", "with", "that", "this", "من", "إلى", "على", "في", "مع", "عن", "هذا", "هذه"}


def norm(tok):
    tok = DIACRITICS.sub("", tok.lower())
    return tok[2:] if tok.startswith("ال") and len(tok) > 4 else tok


def tokens(text):
    return {norm(t) for t in TOKEN.findall(text)} - STOP


def synonyms():
    p = ROOT / "rules" / "synonyms.json"
    groups = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    return [{norm(w) for w in g} for g in groups]


def expand(toks, groups):
    out = set(toks)
    for g in groups:
        if g & toks:
            out |= g
    return out


def chunks(root):
    files = [root / s for s in SOURCES] + [f for d in KNOWLEDGE_DIRS for f in sorted((root / d).rglob("*.md")) if "library" not in f.parts]
    for f in files:
        if not f.exists():
            continue
        rel = f.relative_to(root).as_posix()
        for part in re.split(r"\n(?=## )", f.read_text(encoding="utf-8")):
            part = part.strip()
            if not part:
                continue
            if rel == "mistakes.md" or rel == "ideas.md":
                head, *items = re.split(r"\n(?=- )", part)
                for it in items:
                    yield rel, f"{head.splitlines()[0]}\n{it.strip()}"
            else:
                yield rel, part


def brief(task, project="", budget=2500, root=ROOT):
    want = expand(tokens(task), synonyms())
    scored = []
    for rel, text in chunks(root):
        ctoks = tokens(text) | ({norm(rel.split("/")[-1][:-3])} if rel.startswith("features/") else set())
        score = len(want & ctoks) * 2
        if project and project.lower() in text.lower():
            score += 3
        if rel == "mistakes.md":
            score += 1
        if score >= 3:
            scored.append((score, -len(text), rel, text))
    scored.sort(reverse=True)
    out, used = [], 0
    for score, _, rel, text in scored:
        if used + len(text) > budget:
            continue
        out.append(f"<!-- {rel} · {score} -->\n{text}")
        used += len(text)
    return "\n\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--project", default="")
    ap.add_argument("--budget", type=int, default=2500)
    a = ap.parse_args()
    print(brief(a.task, a.project, a.budget) or "لا مقاطع ذات صلة")


if __name__ == "__main__":
    main()
