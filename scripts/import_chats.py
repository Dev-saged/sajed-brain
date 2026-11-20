#!/usr/bin/env python3
"""يستورد تصدير بيانات claude.ai (Settings ← Privacy ← Export data) إلى الدماغ ليصبح قابلاً للبحث بـbrief.py.
python3 scripts/import_chats.py <export.zip | conversations.json>
لكل محادثة: chats/YYYY/MM/<التاريخ>-<العنوان>.md (كلام ساجد كاملاً + أول 400 حرف من كل رد) و chats/index.md.
المحادثات الموجودة لا تُكرَّر (بالمعرّف). لا أسرار: الأسطر التي تشبه مفاتيح/توكنات تُحجب."""
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "chats"
SECRET = re.compile(r"(ghp_|github_pat_|sk-|AIza|xox[bp]-|-----BEGIN|AKIA)[\w\-]{8,}")


def load(path: pathlib.Path) -> list:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.endswith("conversations.json"))
            return json.loads(z.read(name).decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def text_of(msg: dict) -> str:
    if msg.get("text"):
        return msg["text"]
    return "\n".join(c.get("text", "") for c in msg.get("content", []) if c.get("type") == "text")


def slug(s: str) -> str:
    return re.sub(r"[^\w؀-ۿ]+", "-", s).strip("-")[:60] or "بلا-عنوان"


def clean(s: str) -> str:
    return SECRET.sub("[محجوب]", s).strip()


def main() -> None:
    convs = load(pathlib.Path(sys.argv[1]))
    OUT.mkdir(exist_ok=True)
    seen = {m.group(1) for f in OUT.rglob("*.md") for m in [re.search(r"^id: (\S+)", f.read_text(encoding="utf-8"), re.M)] if m}
    new = 0
    for c in convs:
        cid = c.get("uuid", "")
        msgs = c.get("chat_messages", [])
        if not msgs or cid in seen:
            continue
        date = (c.get("created_at") or "0000-00-00")[:10]
        title = c.get("name") or text_of(msgs[0])[:50]
        lines = [f"---\nid: {cid}\ndate: {date}\ntitle: {clean(title)}\nmessages: {len(msgs)}\n---", f"# {clean(title)}"]
        for m in msgs:
            t = clean(text_of(m))
            if not t:
                continue
            if m.get("sender") == "human":
                lines.append(f"\n**ساجد:** {t}")
            else:
                lines.append(f"\n> {t[:400].replace(chr(10), ' ')}{'…' if len(t) > 400 else ''}")
        dest = OUT / date[:4] / date[5:7] / f"{date}-{slug(title)}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        new += 1
    rows = []
    for f in sorted(OUT.rglob("*.md")):
        if f.name == "index.md":
            continue
        head = f.read_text(encoding="utf-8").split("---")[1]
        meta = dict(l.split(": ", 1) for l in head.strip().splitlines() if ": " in l)
        rows.append(f"- {meta.get('date')} · [{meta.get('title')}]({f.relative_to(OUT)}) · {meta.get('messages')} رسالة")
    (OUT / "index.md").write_text("# كل محادثات ساجد مع Claude (مستوردة)\n_يُحدَّث بـscripts/import_chats.py. ابحث بـ`python3 scripts/brief.py --task \"...\"`._\n\n" + "\n".join(reversed(rows)) + "\n", encoding="utf-8")
    print(f"✓ محادثات جديدة: {new} · المجموع: {len(rows)}")


if __name__ == "__main__":
    main()
