"""قواعد الفحص والمحلّلات. كل نتيجة dict موحّد: rule/severity/tier/path/line/message/text."""
import fnmatch
import json
import pathlib
import re
import subprocess
from collections import Counter, defaultdict

RULES_DIR = pathlib.Path(__file__).resolve().parents[2] / "rules"
DEFAULT_GLOBS = ["*.kt", "*.java", "*.kts"]
IDENT = re.compile(r"[A-Za-z_]\w*")
IMP = re.compile(r"^import[ \t]+([\w.]+?)(\.\*)?(?:[ \t]+as[ \t]+(\w+))?[ \t]*$", re.M)
HEADER_LINES = re.compile(r"^(?:import|package)\s.*$", re.M)
IMPLICIT = {
    "getValue", "setValue", "provideDelegate", "invoke", "plus", "minus", "times", "div", "rem",
    "compareTo", "contains", "get", "set", "iterator", "next", "hasNext", "unaryMinus", "not",
    "inc", "dec", "rangeTo", "equals", "component1", "component2", "component3", "component4",
}
EXEMPT_ANNOS = {
    "Preview", "PreviewLightDark", "PreviewScreenSizes", "Test", "Before", "After", "Provides",
    "Binds", "Inject", "HiltAndroidApp", "AndroidEntryPoint", "HiltViewModel", "Entity", "Dao",
    "Database", "Serializable", "JvmStatic", "SerializedName", "Parcelize", "TypeConverter",
    "Query", "Insert", "Update", "Delete", "Module", "InstallIn", "Composable.Preview",
    "JavascriptInterface", "Keep", "SuppressLint",
}
TEST_PARTS = ("/test/", "/androidTest/", "/testFixtures/")
TOKEN_FILES = ("Theme", "Dimens", "Spacing", "Motion", "BrandConfig", "Tokens")
NUMERIC = [
    (re.compile(r"\b(\d+(?:\.\d+)?)\.dp\b"), "dp"),
    (re.compile(r"\b(\d+(?:\.\d+)?)\.sp\b"), "sp"),
    (re.compile(r"durationMillis\s*=\s*(\d+)"), "ms"),
    (re.compile(r"\bdelay\((\d+)"), "ms"),
]


def finding(rule, sev, tier, path, line, msg, text=""):
    return {"rule": rule, "severity": sev, "tier": tier, "path": path,
            "line": line, "message": msg, "text": text}


def load_rules():
    rules = []
    for name in ("guards.json", "deprecated.json"):
        rules += json.loads((RULES_DIR / name).read_text(encoding="utf-8"))
    return rules


def _matches(pat, text, multiline):
    if multiline:
        for m in pat.finditer(text):
            yield text.count("\n", 0, m.start()) + 1
    else:
        for i, line in enumerate(text.split("\n"), 1):
            if pat.search(line):
                yield i


def apply_rules(files, rules, disabled=(), only=None, globs=None):
    out = []
    for r in rules:
        if r["id"] in disabled or (only and r["id"] not in only):
            continue
        pat = re.compile(r["pattern"], re.S | re.M if r.get("multiline") else 0)
        for rel, src in files.items():
            name = pathlib.PurePosixPath(rel).name
            if not any(fnmatch.fnmatch(name, g) for g in (globs or r.get("files", DEFAULT_GLOBS))):
                continue
            if any(x in "/" + rel for x in r.get("exclude", [])):
                continue
            raw = src.raw
            if r.get("only_if_file_contains") and not any(s in raw for s in r["only_if_file_contains"]):
                continue
            if r.get("unless_file_contains_any") and any(s in raw for s in r["unless_file_contains_any"]):
                continue
            use_code = r.get("scope", "code") == "code" and src.lexed
            text = src.lexed.code if use_code else raw
            raw_lines = raw.split("\n")
            for hit, ln in enumerate(_matches(pat, text, r.get("multiline"))):
                if hit >= 50:
                    break
                snippet = "***" if r.get("mask") else raw_lines[ln - 1].strip()[:120]
                out.append(finding(r["id"], r["severity"], r["tier"], rel, ln, r["message"], snippet))
    return out


def unused_imports(rel, src):
    if not rel.endswith(".kt"):
        return []
    body = HEADER_LINES.sub("", src.lexed.code)
    used = set(IDENT.findall(body)) | set(src.lexed.templates)
    out = []
    for m in IMP.finditer(src.raw):
        if m.group(2):
            continue
        name = m.group(3) or m.group(1).rsplit(".", 1)[-1]
        if name not in used and name not in IMPLICIT:
            out.append((src.raw.count("\n", 0, m.start()) + 1, m.group(0)))
    return out


def dead_symbols(syms, refs):
    decls = Counter(s.name for s in syms)
    out = []
    for s in syms:
        if any(p in "/" + s.path for p in TEST_PARTS) or len(s.name) < 3:
            continue
        if {"override", "abstract", "expect", "actual", "operator"} & set(s.mods):
            continue
        if s.scope == "iface" or set(s.annos) & EXEMPT_ANNOS or s.name in {"main", "Companion"}:
            continue
        if refs[s.name] - decls[s.name] > 0:
            continue
        high = s.vis == "private"
        note = "خاص بلا أي استخدام" if high else "عام بلا مراجع — تأكد من غياب reflection/DI/serialization"
        out.append(finding("dead-symbol", "warn", "T0" if high else "T2", s.path, s.line,
                           f"{s.kind} {s.name}: {note}", s.name))
    return out


def dup_strings(files):
    seen = defaultdict(list)
    for rel, src in files.items():
        if not src.lexed or not rel.endswith((".kt", ".java")) or any(t in rel for t in TOKEN_FILES):
            continue
        for ln, text in src.lexed.strings:
            if len(text) >= 6 and "\n" not in text and text.strip():
                seen[text].append((rel, ln))
    out = []
    for text, locs in seen.items():
        if len(locs) >= 3:
            rel, ln = locs[0]
            out.append(finding("dup-string", "info", "T1", rel, ln,
                               f"نص مكرر {len(locs)} مرات في {len({p for p, _ in locs})} ملف — اجمعه في ثابت واحد",
                               text[:60]))
    return out


def dup_numbers(files):
    seen = defaultdict(list)
    for rel, src in files.items():
        if not src.lexed or not rel.endswith(".kt") or any(t in rel for t in TOKEN_FILES):
            continue
        for pat, unit in NUMERIC:
            for m in pat.finditer(src.lexed.code):
                seen[(unit, m.group(1))].append((rel, src.lexed.code.count("\n", 0, m.start()) + 1))
    out = []
    for (unit, val), locs in seen.items():
        if len(locs) >= 6:
            rel, ln = locs[0]
            out.append(finding("token-candidate", "info", "T1", rel, ln,
                               f"{val}{unit} مكرر {len(locs)} مرة — حوّله إلى token في Dimens/Motion", f"{val}{unit}"))
    return out


def dup_bodies(syms):
    groups = defaultdict(list)
    for s in syms:
        if s.hash and not any(p in "/" + s.path for p in TEST_PARTS):
            groups[s.hash].append(s)
    out = []
    for g in groups.values():
        if len(g) >= 2:
            names = ", ".join(f"{s.name}@{s.path}:{s.line}" for s in g[:4])
            out.append(finding("dup-body", "warn", "T1", g[0].path, g[0].line,
                               f"{len(g)} دوال بجسم متطابق — استخرجها لدالة واحدة", names))
    return out


def long_functions(syms, limit=80):
    return [finding("long-function", "info", "T1", s.path, s.line, f"{s.name}: {s.size} سطراً — قسّمها", s.name)
            for s in syms if s.size > limit and not any(p in "/" + s.path for p in TEST_PARTS)]


def migration_edits(root, base):
    try:
        diff = subprocess.run(["git", "diff", "--name-status", base], cwd=root, capture_output=True,
                              text=True, timeout=30, check=True).stdout
    except (subprocess.SubprocessError, OSError):
        return []
    out = []
    for line in diff.splitlines():
        status, _, path = line.partition("\t")
        if status[:1] in ("M", "D") and re.search(r"(?i)migration", path) and path.endswith((".kt", ".java", ".sql", ".json")):
            out.append(finding("migration-edited", "error", "T3", path, 1,
                               "تعديل/حذف migration قديمة ممنوع — أضف migration جديدة", status))
    return out
