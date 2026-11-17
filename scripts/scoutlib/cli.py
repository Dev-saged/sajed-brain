"""واجهة الماسح: scout.py <project> [--out DIR] [--base REF] [--apply-imports] [--where NAME]."""
import argparse
import fnmatch
import json
import os
import pathlib
import sys
from collections import Counter, namedtuple

from . import findings as F
from . import report, symbols
from .lexer import lex

Src = namedtuple("Src", "raw lexed")
SKIP_DIRS = {".git", ".gradle", "build", ".idea", "node_modules", "secrets", ".claude", ".brain", "docs"}
READ_EXT = {".kt", ".java", ".kts", ".xml", ".pro", ".toml", ".gradle", ".json", ".properties", ".md", ".yml"}
LEX_EXT = {".kt", ".java", ".kts"}
MAX_BYTES = 1_500_000


def load_cfg(root):
    p = root / ".brain-scout.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def collect(root, cfg):
    files = {}
    ignore = cfg.get("ignore", [])
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            p = pathlib.Path(dirpath) / n
            rel = p.relative_to(root).as_posix()
            if p.suffix not in READ_EXT or any(fnmatch.fnmatch(rel, g) for g in ignore):
                continue
            try:
                if p.stat().st_size > MAX_BYTES:
                    continue
                raw = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            files[rel] = Src(raw, lex(raw) if p.suffix in LEX_EXT else None)
    return files


def build_refs(files):
    total, per_file = Counter(), {}
    for rel, src in files.items():
        if src.lexed:
            c = Counter(F.IDENT.findall(src.lexed.code)) + Counter(src.lexed.templates)
        elif rel.endswith((".xml", ".pro", ".toml", ".gradle", ".json", ".properties")):
            c = Counter(F.IDENT.findall(src.raw))
        else:
            continue
        per_file[rel] = c
        total += c
    return total, per_file


def apply_imports(root, files, unused):
    changed = 0
    for rel, items in unused.items():
        lines = files[rel].raw.split("\n")
        drop = {ln - 1 for ln, _ in items}
        (root / rel).write_text("\n".join(l for i, l in enumerate(lines) if i not in drop), encoding="utf-8")
        changed += len(drop)
    return changed


def where(name, syms, per_file):
    for s in syms:
        if s.name == name:
            print(f"decl  {s.kind} {s.vis} {s.path}:{s.line} scope={s.scope}")
    users = sorted((rel, c[name]) for rel, c in per_file.items() if c[name])
    for rel, n in users:
        print(f"ref   {rel} x{n}")
    if not users:
        print("لا مراجع")


def run(argv=None):
    ap = argparse.ArgumentParser(prog="scout")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--out")
    ap.add_argument("--base")
    ap.add_argument("--apply-imports", action="store_true")
    ap.add_argument("--where")
    ap.add_argument("--fail-on", choices=["error", "warn", "never"], default="never")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)

    root = pathlib.Path(a.path).resolve()
    cfg = load_cfg(root)
    files = collect(root, cfg)
    syms = [s for rel, src in sorted(files.items()) if rel.endswith(".kt") for s in symbols.extract(rel, src.lexed)]
    refs, per_file = build_refs(files)

    if a.where:
        where(a.where, syms, per_file)
        return 0

    disabled = set(cfg.get("disable", []))
    found = F.apply_rules(files, F.load_rules(), disabled)
    unused = {rel: u for rel, src in files.items() if (u := F.unused_imports(rel, src))}
    found += [F.finding("unused-import", "info", "T0", rel, ln, "import غير مستخدم", txt)
              for rel, items in unused.items() for ln, txt in items]
    found += F.dead_symbols(syms, refs) + F.dup_strings(files) + F.dup_numbers(files)
    found += F.dup_bodies(syms) + F.long_functions(syms)
    if a.base:
        found += F.migration_edits(root, a.base)
    found = [f for f in found if f["rule"] not in disabled]

    if a.apply_imports:
        n = apply_imports(root, files, unused)
        found = [f for f in found if f["rule"] != "unused-import"]
        print(f"أُزيلت {n} imports غير مستخدمة")

    if not a.no_write:
        out = report.ensure_dir(a.out or root / "docs")
        report.write_index(out, syms, refs)
        s, counts = report.write_report(out, root.name, found, len(syms))
        report.write_history(out, s, counts, found, len(syms))
        print(f"scout {root.name}: {s}/100 · errors={counts['error']} warns={counts['warn']} symbols={len(syms)}")
    sev = {f["severity"] for f in found}
    if (a.fail_on == "error" and "error" in sev) or (a.fail_on == "warn" and sev & {"error", "warn"}):
        return 1
    return 0


def main():
    sys.exit(run())
