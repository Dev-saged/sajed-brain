"""استخراج الرموز (class/fun/val) من كود Kotlin المجرّد مع النطاق وبصمة الجسم."""
import hashlib
import re
from collections import namedtuple

Sym = namedtuple("Sym", "name kind vis path line scope annos mods hash size")

MODS = {
    "public", "private", "internal", "protected", "override", "open", "abstract", "final",
    "sealed", "data", "enum", "annotation", "inline", "value", "suspend", "operator", "infix",
    "tailrec", "external", "const", "lateinit", "expect", "actual", "companion", "inner",
}
VIS = ("private", "protected", "internal")
ANNO = re.compile(r"@(?:\w+:)?([\w.]+)(?:\([^)]*\))?\s*")
WORD = re.compile(r"(\w+)\s+")
HEAD = re.compile(r"(class|interface|object|fun|val|var)\b\s*(.*)")
SIG_END = re.compile(r"\s*(?::[^{=\n]*)?\s*([{=])")


def _name(kw, rest):
    if kw in ("class", "interface", "object"):
        m = re.match(r"(\w+)", rest)
        if m:
            return m.group(1)
        return "Companion" if kw == "object" and rest.strip() in ("", "{") else None
    if kw == "fun":
        head = rest.split("(", 1)
        if len(head) < 2:
            return None
        w = re.findall(r"\w+", head[0])
        return w[-1] if w else None
    if rest.startswith("("):
        return None
    w = re.findall(r"\w+", re.split(r"[:=]|\bby\b|\{", rest, maxsplit=1)[0])
    return w[-1] if w else None


def parse_line(s):
    annos = []
    while s.startswith("@"):
        m = ANNO.match(s)
        if not m:
            break
        annos.append(m.group(1))
        s = s[m.end():]
    mods = []
    while True:
        m = WORD.match(s)
        if not (m and m.group(1) in MODS):
            break
        mods.append(m.group(1))
        s = s[m.end():]
    m = HEAD.match(s)
    if not m:
        return annos, s, None
    kw, rest = m.groups()
    if kw == "fun" and rest.startswith("interface"):
        kw, rest = "interface", rest[9:].lstrip()
    name = _name(kw, rest)
    return annos, s, ((kw, mods, name) if name else None)


def _body_info(code, start):
    p = code.find("(", start)
    if p < 0:
        return "", 0
    depth, j = 0, p
    while j < len(code):
        c = code[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    m = SIG_END.match(code, j + 1)
    if not m or m.group(1) != "{":
        return "", 0
    k, depth = m.end() - 1, 0
    for q in range(k, len(code)):
        c = code[q]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                inner = code[k + 1:q]
                body = re.sub(r"\s+", " ", inner).strip()
                digest = hashlib.sha1(body.encode()).hexdigest()[:10] if len(body) >= 80 else ""
                return digest, inner.count("\n") + 1
    return "", 0


def extract(path, lx):
    code = lx.code
    lines = code.split("\n")
    offs = [0]
    for ln in lines:
        offs.append(offs[-1] + len(ln) + 1)
    syms, stack, buf = [], [], []
    pend, age, paren = None, 0, 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s:
            annos, rest, d = parse_line(s)
            if d is None:
                buf = buf + annos if (annos and not rest) else []
            else:
                kw, mods, name = d
                member = all(k in ("class", "iface") for k in stack)
                if paren == 0 and member:
                    vis = next((v for v in VIS if v in mods), "public")
                    h, size = ("", 0)
                    if kw == "fun":
                        h, size = _body_info(code, offs[i] + len(line) - len(line.lstrip()))
                    syms.append(Sym(name, kw, vis, path, i + 1, stack[-1] if stack else "top",
                                    tuple(buf + annos), tuple(mods), h, size))
                    pend = {"interface": "iface", "class": "class", "object": "class", "fun": "fun"}.get(kw)
                    age = 0
                buf = []
        for ch in line:
            if ch == "{":
                stack.append(pend or "other")
                pend = None
            elif ch == "}":
                if stack:
                    stack.pop()
            elif ch == "(":
                paren += 1
            elif ch == ")":
                paren = max(0, paren - 1)
        if pend:
            age += 1
            if age > 6 or (paren == 0 and "{" not in line and not line.rstrip().endswith(",")):
                pend = None
    return syms
