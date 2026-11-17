"""دمج نتائج detekt (SARIF) لرفع دقة "الميت": private يؤكده detekt = T0 مؤكَّد، وما لا يؤكده يُخفَّض إلى T1."""
import json
import pathlib

from .findings import finding

DEAD_RULES = {"UnusedPrivateMember", "UnusedPrivateProperty", "UnusedPrivateClass", "UnusedPrivateFunction"}


def parse_sarif(text):
    out = []
    for run in json.loads(text).get("runs", []):
        for res in run.get("results", []):
            rule = res.get("ruleId", "").split(".")[-1].split("/")[-1]
            msg = res.get("message", {}).get("text", "")
            for loc in res.get("locations", []):
                phys = loc.get("physicalLocation", {})
                uri = phys.get("artifactLocation", {}).get("uri", "")
                out.append((rule, uri, phys.get("region", {}).get("startLine", 1), msg))
    return out


def relativize(uri, known):
    path = uri.replace("file://", "").lstrip("/") if uri.startswith("file:") else uri
    for rel in known:
        if path == rel or path.endswith("/" + rel):
            return rel
    return None


def merge(found, ext, known_paths):
    dead_hits, extra = set(), []
    for rule, uri, line, msg in ext:
        rel = relativize(uri, known_paths)
        if not rel:
            continue
        if rule in DEAD_RULES:
            dead_hits.add((rel, line))
        elif rule == "UnusedImports":
            extra.append(finding("unused-import", "info", "T0", rel, line, "import غير مستخدم (detekt)", msg[:80]))
    out, seen = [], {(f["path"], f["line"]) for f in found if f["rule"] in ("dead-symbol", "unused-import")}
    for f in found:
        if f["rule"] == "dead-symbol" and f["tier"] == "T0":
            if (f["path"], f["line"]) in dead_hits:
                f = {**f, "message": f["message"] + " — مؤكَّد بـdetekt"}
            else:
                f = {**f, "tier": "T1", "message": f["message"] + " — لم يؤكده detekt (راجع قبل الحذف)"}
        out.append(f)
    for (rel, line) in sorted(dead_hits - seen):
        out.append(finding("dead-symbol", "warn", "T0", rel, line, "رمز private غير مستخدم — اكتشفه detekt فقط", ""))
    out += [f for f in extra if (f["path"], f["line"]) not in seen]
    return out


def load(path):
    p = pathlib.Path(path)
    return parse_sarif(p.read_text(encoding="utf-8")) if p.exists() else None
