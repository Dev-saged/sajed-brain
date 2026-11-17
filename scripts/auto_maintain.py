#!/usr/bin/env python3
"""صيانة أسبوعية آمنة لمشروع: إصلاحات 1:1 + imports + ترقيات patch/minor، ثم يكتب نص الـPR.
auto_maintain.py <project> [--body FILE] [--no-deps] [--note TEXT]
يطبع changed=true|false (لـGITHUB_OUTPUT). T2 (major، حذف عام) لا يُمس ويُذكر في النص فقط."""
import argparse
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import deps_radar  # noqa: E402
from scoutlib import cli  # noqa: E402


def git_changed(root):
    out = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True).stdout
    return [p for p in (ln[3:] for ln in out.splitlines()) if not p.startswith(".brain")]


def upgrade_deps(root, fetch=deps_radar.fetch_text):
    toml = pathlib.Path(root) / "gradle" / "libs.versions.toml"
    if not toml.exists():
        return [], []
    rows = deps_radar.run(toml, fetch=fetch)
    deps_radar.apply(toml, rows)
    done = [f"{r['key']}: {r['current']} ← {r['latest']}" for r in rows if r["ref"] and r["bump"] in ("patch", "minor")]
    held = [f"{r['key']}: {r['current']} ← {r['latest']} (major)" for r in rows if r["bump"] == "major"]
    return done, held


def body(stats, deps_done, deps_held, files, note=""):
    lines = ["## صيانة أسبوعية آلية", "", "كل البنود أدناه T0/T1 (آمنة ومحدّدة). المراجعة: build + tests خضراء قبل الدمج.", ""]
    if stats["fixes"]:
        lines += ["### إصلاحات API"] + [f"- {rule}: {n}" for rule, n in sorted(stats["fixes"].items())] + [""]
    if stats["imports"]:
        lines += [f"### imports غير مستخدمة", f"- أُزيلت {stats['imports']}", ""]
    if deps_done:
        lines += ["### ترقيات (patch/minor)"] + [f"- {d}" for d in deps_done] + [""]
    if deps_held:
        lines += ["### مؤجّلة (T2 — بموافقة)"] + [f"- {d}" for d in deps_held] + [""]
    lines += [f"الملفات المتأثرة: {len(files)}"]
    if note:
        lines += ["", note]
    return "\n".join(lines) + "\n"


def main(argv=None, fetch=deps_radar.fetch_text):
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--body")
    ap.add_argument("--no-deps", action="store_true")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.project).resolve()
    stats = cli.maintain(root)
    done, held = ([], []) if a.no_deps else upgrade_deps(root, fetch)
    files = git_changed(root)
    changed = bool(files)
    if a.body and changed:
        pathlib.Path(a.body).write_text(body(stats, done, held, files, a.note), encoding="utf-8")
    print(f"changed={'true' if changed else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
