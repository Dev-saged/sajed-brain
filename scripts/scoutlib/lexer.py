"""تجريد التعليقات ومحتوى النصوص من Kotlin/Java مع حفظ أرقام الأسطر."""
import bisect
import re
from dataclasses import dataclass, field

TPL = re.compile(r"\$\{?([A-Za-z_]\w*)")
SPECIAL = re.compile(r"//|/\*|\"|'")
CHAR = re.compile(r"'(?:\\u[0-9a-fA-F]{4}|\\.|[^'\\\n])'")


@dataclass
class Lexed:
    code: str
    strings: list = field(default_factory=list)
    templates: list = field(default_factory=list)


def _blank(seg):
    return re.sub(r"[^\n]", " ", seg)


def lex(src):
    out, strings, tpl = [], [], []
    newlines = [m.start() for m in re.finditer("\n", src)]
    n, i = len(src), 0

    def line(p):
        return bisect.bisect_left(newlines, p) + 1

    while i < n:
        m = SPECIAL.search(src, i)
        if not m:
            out.append(src[i:])
            break
        out.append(src[i:m.start()])
        i = m.start()
        tok = m.group()
        if tok == "//":
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif tok == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(_blank(src[i:j]))
            i = j
        elif tok == '"':
            if src.startswith('"""', i):
                j = src.find('"""', i + 3)
                body = src[i + 3:n if j < 0 else j]
                end = n if j < 0 else j + 3
                out.append('"""' + _blank(body) + ('"""' if j >= 0 else ""))
            else:
                j = i + 1
                while j < n and src[j] not in '"\n':
                    j += 2 if src[j] == "\\" else 1
                j = min(j, n)
                closed = j < n and src[j] == '"'
                body = src[i + 1:j]
                end = j + 1 if closed else j
                out.append('"' + _blank(body) + ('"' if closed else ""))
            strings.append((line(i), body))
            tpl += TPL.findall(body)
            i = end
        else:
            cm = CHAR.match(src, i)
            if cm:
                out.append("'" + " " * (cm.end() - i - 2) + "'")
                i = cm.end()
            else:
                out.append("'")
                i += 1
    return Lexed("".join(out), strings, tpl)
