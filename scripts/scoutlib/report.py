"""مخرجات الماسح: فهرس TSV قابل للـgrep، تقرير markdown، JSON، وسجل اتجاه الصحة."""
import datetime
import json
import pathlib
from collections import Counter

SEV_ORDER = {"error": 0, "warn": 1, "info": 2}
TIER_NOTE = {"T0": "نفّذ فوراً", "T1": "نفّذ ثم اذكر", "T2": "اقترح وانتظر", "T3": "ممنوع"}
PER_RULE = 25


def score(findings):
    c = Counter(f["severity"] for f in findings)
    dead = sum(f["rule"] == "dead-symbol" for f in findings)
    imps = sum(f["rule"] == "unused-import" for f in findings)
    return max(0, round(100 - 10 * c["error"] - min(c["warn"], 40) - 0.3 * min(dead, 60) - 0.2 * min(imps, 50)))


def write_index(out, syms, refs):
    rows = [f"{s.name}\t{s.kind}\t{s.vis}\t{s.path}:{s.line}\t{max(0, refs[s.name] - 1)}\t{s.scope}\t{s.size}\t{s.hash}"
            for s in sorted(syms, key=lambda s: (s.path, s.line))]
    (out / "symbol-index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_report(out, name, findings, nsyms):
    by_rule = {}
    for f in sorted(findings, key=lambda f: (SEV_ORDER[f["severity"]], f["rule"], f["tier"], f["path"], f["line"])):
        by_rule.setdefault((f["rule"], f["tier"]), []).append(f)
    s = score(findings)
    c = Counter(f["severity"] for f in findings)
    lines = [f"# Scout — {name}", "",
             f"النتيجة: **{s}/100** · أخطاء {c['error']} · تحذيرات {c['warn']} · ملاحظات {c['info']} · رموز {nsyms}", ""]
    for (rule, _), items in by_rule.items():
        head = items[0]
        lines += [f"## {rule} ({len(items)}) — {head['tier']} {TIER_NOTE[head['tier']]}", f"{head['message']}", ""]
        for f in items[:PER_RULE]:
            tail = f" — `{f['text']}`" if f["text"] else ""
            lines.append(f"- {f['path']}:{f['line']}{tail}")
        if len(items) > PER_RULE:
            lines.append(f"- … و{len(items) - PER_RULE} أخرى في scout.json")
        lines.append("")
    if not findings:
        lines.append("لا ملاحظات.")
    (out / "scout-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "scout.json").write_text(json.dumps({"score": s, "findings": findings}, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
    return s, c


def write_history(out, score_value, counts, findings, nsyms):
    path = out / "scout-history.tsv"
    today = datetime.date.today().isoformat()
    dead = sum(f["rule"] == "dead-symbol" for f in findings)
    row = f"{today}\t{score_value}\t{counts['error']}\t{counts['warn']}\t{dead}\t{nsyms}"
    old = [ln for ln in path.read_text(encoding="utf-8").splitlines() if not ln.startswith(today)] if path.exists() else []
    path.write_text("\n".join(old + [row]) + "\n", encoding="utf-8")


def ensure_dir(p):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)
    return pathlib.Path(p)
