"""إصلاحات آلية 1:1 (rules/fixes.json): تُطبَّق على الكود الفعلي فقط (لا تعليقات/نصوص) وتضبط الـimports."""
import fnmatch
import json
import pathlib
import re
from collections import Counter

from .findings import HEADER_LINES, IDENT, RULES_DIR
from .lexer import lex

IMPORT_LINE = re.compile(r"^import[ \t]+.+$", re.M)


def load_fixes():
    return json.loads((RULES_DIR / "fixes.json").read_text(encoding="utf-8"))


def project_ok(root, cond):
    if not cond:
        return True
    for rel in cond["files"]:
        p = pathlib.Path(root) / rel
        if p.exists() and any(s in p.read_text(encoding="utf-8", errors="replace") for s in cond["any"]):
            return True
    return False


def ensure_import(raw, imp):
    if re.search(rf"^import[ \t]+{re.escape(imp)}[ \t]*$", raw, re.M):
        return raw
    last = None
    for last in IMPORT_LINE.finditer(raw):
        pass
    if last:
        return raw[:last.end()] + f"\nimport {imp}" + raw[last.end():]
    pkg = re.search(r"^package[ \t]+.+$", raw, re.M)
    return raw[:pkg.end()] + f"\n\nimport {imp}" + raw[pkg.end():] if pkg else f"import {imp}\n\n" + raw


def drop_import(raw, imp):
    name = imp.rsplit(".", 1)[-1]
    body = HEADER_LINES.sub("", lex(raw).code)
    if name in set(IDENT.findall(body)):
        return raw
    return re.sub(rf"^import[ \t]+{re.escape(imp)}[ \t]*\n?", "", raw, flags=re.M)


def fix_text(rel, raw, rules, root):
    counts = Counter()
    for r in rules:
        if not any(fnmatch.fnmatch(pathlib.PurePosixPath(rel).name, g) for g in r.get("files", ["*.kt"])):
            continue
        if r.get("only_if_file_contains") and not any(s in raw for s in r["only_if_file_contains"]):
            continue
        if any(s in raw for s in r.get("unless_file_contains_any", [])):
            continue
        if not project_ok(root, r.get("requires_project_contains")):
            continue
        pat = re.compile(r["pattern"], re.M)
        text = lex(raw).code if r.get("scope", "code") == "code" else raw
        spans = [(m.start(), m.end(), m.expand(r["replace"])) for m in pat.finditer(text)]
        if not spans:
            continue
        for s, e, rep in reversed(spans):
            raw = raw[:s] + rep + raw[e:]
        counts[r["id"]] += len(spans)
        for imp in r.get("imports", []):
            raw = ensure_import(raw, imp)
        for imp in r.get("drop_imports", []):
            raw = drop_import(raw, imp)
    return raw, counts


def apply_fixes(root, files, rules=None):
    rules = rules if rules is not None else load_fixes()
    total = Counter()
    for rel, src in files.items():
        new, counts = fix_text(rel, src.raw, rules, root)
        if counts:
            (pathlib.Path(root) / rel).write_text(new, encoding="utf-8")
            total += counts
    return total
