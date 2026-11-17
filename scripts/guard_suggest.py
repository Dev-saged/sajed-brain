#!/usr/bin/env python3
"""يولّد حارساً (regex) من مثال الكود الخاطئ، ويتحقق أنه يلتقط المثال ولا يلتقط المثال الصحيح، ثم يضيفه إلى rules/guards.json.
guard_suggest.py --id slug --bad 'val balance: Long' [--good '...'] --message '...' [--severity warn] [--tier T1] [--add]"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUARDS = ROOT / "rules" / "guards.json"
SPLIT = re.compile(r"(\s+|[(){}\[\],.:;=<>+\-*/!?&|@])")
SLUG = re.compile(r"^[a-z][a-z0-9\-]{2,40}$")


def build_pattern(bad):
    toks = [t for t in SPLIT.split(bad.strip()) if t]
    parts, prev_word, gap = [], False, False
    for tok in toks:
        if tok.isspace():
            gap = True
            continue
        word = bool(re.fullmatch(r"\w+(?:\.\d+)?", tok))
        if parts:
            parts.append(r"\s+" if (word and prev_word and gap) else r"\s*")
        parts.append(r"\d+(?:\.\d+)?" if re.fullmatch(r"\d+(?:\.\d+)?", tok) else re.escape(tok))
        prev_word, gap = word, False
    return "".join(parts)


def make_entry(gid, bad, message, severity="warn", tier="T1", good=None, source="mistakes.md", files=None):
    if not SLUG.match(gid):
        raise ValueError(f"id غير صالح: {gid} (أحرف صغيرة وشرطات، 3-41)")
    pattern = build_pattern(bad)
    pat = re.compile(pattern)
    if not pat.search(bad):
        raise ValueError("الـregex المولَّد لا يلتقط المثال الخاطئ نفسه")
    if good and pat.search(good):
        raise ValueError("الـregex يلتقط المثال الصحيح أيضاً — أضف سياقاً أدق في --bad")
    entry = {"id": gid, "severity": severity, "tier": tier,
             "scope": "raw" if re.search(r"[\"']", bad) else "code",
             "pattern": pattern, "message": message, "source": source}
    if files:
        entry["files"] = files
    return entry


def add_entry(entry, path=GUARDS):
    text = path.read_text(encoding="utf-8")
    ids = {r["id"] for r in json.loads(text)}
    if entry["id"] in ids:
        raise ValueError(f"الحارس موجود: {entry['id']}")
    body = text.rstrip()
    assert body.endswith("]")
    new = body[:-1].rstrip() + ",\n  " + json.dumps(entry, ensure_ascii=False) + "\n]\n"
    json.loads(new)
    path.write_text(new, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--bad", required=True)
    ap.add_argument("--good")
    ap.add_argument("--message", required=True)
    ap.add_argument("--severity", default="warn", choices=["error", "warn", "info"])
    ap.add_argument("--tier", default="T1", choices=["T0", "T1", "T2", "T3"])
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--add", action="store_true")
    a = ap.parse_args(argv)
    try:
        entry = make_entry(a.id, a.bad, a.message, a.severity, a.tier, a.good, files=a.files)
        if a.add:
            add_entry(entry)
    except ValueError as e:
        print(f"خطأ: {e}", file=sys.stderr)
        return 1
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
