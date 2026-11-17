#!/usr/bin/env python3
"""فحص سلامة الدماغ: روابط README، workflows المذكورة، حجم README، صحة القواعد، صيغة السجل، تكرار، أسرار."""
import argparse
import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scoutlib import cli, findings  # noqa: E402

README_WARN, README_ERR = 6000, 8000
LEDGER_FILES = ("mistakes.md", "ideas.md", "preferences.md")
ENTRY = re.compile(r"^- \[\d{4}-\d{2}-\d{2}\]")
REQUIRED = {"id", "severity", "tier", "pattern", "message", "source"}


def check(root=ROOT):
    errors, warns = [], []
    readme = (root / "README.md").read_text(encoding="utf-8")

    size = len(readme.encode("utf-8"))
    if size > README_ERR:
        errors.append(f"README.md {size}B > {README_ERR}B — يُجلب كل جلسة، انقل التفاصيل لملفات فرعية")
    elif size > README_WARN:
        warns.append(f"README.md {size}B > {README_WARN}B")

    for target in sorted(set(re.findall(r"`((?:features|projects|docs)/[\w\-./]+\.md)`", readme))):
        if not (root / target).exists():
            warns.append(f"README يشير إلى {target} وهو غير موجود")

    wf = {p.name for p in (root / ".github" / "workflows").glob("*.yml")}
    for name in sorted(set(re.findall(r"\b(brain-[\w\-]+\.yml)\b", readme))):
        if name not in wf:
            errors.append(f"README يستدعي {name} وهو غير موجود في .github/workflows")

    for name in ("guards.json", "deprecated.json"):
        try:
            rules = json.loads((root / "rules" / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"rules/{name}: {e}")
            continue
        ids = Counter(r.get("id") for r in rules)
        for r in rules:
            if REQUIRED - r.keys():
                errors.append(f"rules/{name}: {r.get('id')} ينقصه {sorted(REQUIRED - r.keys())}")
                continue
            try:
                re.compile(r["pattern"])
            except re.error as e:
                errors.append(f"rules/{name}: {r['id']} regex غير صالح: {e}")
        errors += [f"rules/{name}: id مكرر {i}" for i, n in ids.items() if n > 1]

    for name in LEDGER_FILES:
        p = root / name
        if not p.exists():
            continue
        lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip().startswith("- [")]
        warns += [f"{name}: صيغة غير قياسية: {ln[:50]}" for ln in lines if not ENTRY.match(ln)]
        warns += [f"{name}: سطر مكرر: {ln[:50]}" for ln, n in Counter(lines).items() if n > 1]

    rule_ids = set()
    for name in ("guards.json", "deprecated.json"):
        f = root / "rules" / name
        if f.exists():
            try:
                rule_ids |= {r.get("id") for r in json.loads(f.read_text(encoding="utf-8"))}
            except json.JSONDecodeError:
                pass
    mistakes = root / "mistakes.md"
    if mistakes.exists():
        for ln in mistakes.read_text(encoding="utf-8").splitlines():
            if not ENTRY.match(ln.strip()):
                continue
            gid = re.search(r"\bguard:([\w\-]+)", ln)
            if gid and gid.group(1) not in rule_ids:
                warns.append(f"mistakes.md: الحارس {gid.group(1)} غير موجود (PR معلّق؟)")
            elif not gid and "noguard" not in ln:
                warns.append(f"mistakes.md: خطأ بلا حارس (أضف guard:<id> أو noguard): {ln[:50]}")

    md = {p.relative_to(root).as_posix(): cli.Src(p.read_text(encoding="utf-8"), None)
          for p in root.rglob("*") if p.suffix in (".md", ".json", ".yml", ".py")
          and ".git" not in p.parts and "tests" not in p.parts}
    leaks = findings.apply_rules(md, findings.load_rules(), only={"secret-key", "secret-assignment"},
                                 globs=["*.md", "*.json", "*.yml", "*.py"])
    errors += [f"سر ظاهر في {f['path']}:{f['line']}" for f in leaks]
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    errors, warns = check()
    for e in errors:
        print("ERROR", e)
    if not a.quiet:
        for w in warns:
            print("warn ", w)
    print(f"doctor: {len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
