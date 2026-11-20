#!/usr/bin/env python3
"""«رتّب الدماغ» — أمر واحد دوري يفلتر ويرتّب ويعيد بناء الخريطة:
1) فهرس الجلسات sessions/index.md + سطر يومية لكل جلسة جديدة  2) ضغط يوميات الأشهر المنتهية (journal_digest)
3) فهرس المحادثات المستوردة إن وُجدت  4) الخريطة index/MAP.md  5) فحص السلامة (doctor) والاختبارات
6) تقرير: ملفات مكررة العنوان، روابط مكسورة، ملفات يتيمة، جلسات بلا قرارات — لينظّفها Claude بعد موافقة ساجد.
python3 scripts/brain_tidy.py"""
import collections
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SESS = ROOT / "sessions"
JOURNAL = ROOT / "journal"


def run(*a) -> str:
    r = subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else f"{a[0]}: ✓"


def meta(f: pathlib.Path) -> dict:
    m = re.match(r"---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S)
    return dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l) if m else {}


def sessions() -> list:
    if not SESS.exists():
        return []
    files = sorted(f for f in SESS.glob("*.md") if f.name != "index.md")
    rows, logged = [], set()
    JOURNAL.mkdir(exist_ok=True)
    for j in JOURNAL.glob("*.md"):
        logged |= set(re.findall(r"\(sessions/([^)]+)\)", j.read_text(encoding="utf-8")))
    warn = []
    for f in files:
        m = meta(f)
        rows.append(f"- {m.get('date', f.stem[:10])} · @{m.get('project', 'عام')} · [{m.get('title', f.stem)}]({f.name})")
        if "## القرارات" not in f.read_text(encoding="utf-8"):
            warn.append(f"جلسة بلا قسم قرارات: {f.name}")
        if f.name not in logged:
            month = JOURNAL / f"{m.get('date', f.stem[:10])[:7]}.md"
            ok = "✗" if m.get("status") == "fail" else "✓"
            with month.open("a", encoding="utf-8") as fh:
                fh.write(f"- [{m.get('date', f.stem[:10])}] @{m.get('project', 'عام')} {ok} {m.get('title', f.stem)} (sessions/{f.name})\n")
    (SESS / "index.md").write_text("# سجل الجلسات\n_كل جلسة عمل تُكتب هنا عند نهايتها ثم تُرفع. «رتّب الدماغ» يعيد بناء هذا الفهرس._\n\n"
                                   + "\n".join(reversed(rows)) + "\n", encoding="utf-8")
    return warn


def duplicates() -> list:
    titles = collections.defaultdict(list)
    for f in ROOT.rglob("*.md"):
        if any(p in f.parts for p in (".git", "chats", "index", "node_modules")):
            continue
        first = next((l for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), "")
        if first:
            titles[first.strip().lower()].append(str(f.relative_to(ROOT)))
    return [f"عنوان مكرر «{t[2:]}»: {', '.join(v)}" for t, v in titles.items() if len(v) > 1]


def stats() -> None:
    """كتلة إحصاءات حية في README بين علامتين — تُحدَّث تلقائياً فلا تتقادم الأرقام."""
    import datetime
    import json
    idx = json.loads((ROOT / "assets" / "index.json").read_text(encoding="utf-8"))
    count = collections.Counter(e["type"] for e in idx)
    sess = sorted(f for f in SESS.glob("20*.md")) if SESS.exists() else []
    block = (f"<!-- stats:start -->\n_مولّد تلقائياً بـbrain_tidy — {datetime.date.today()}_ · "
             f"أيقونات تصميم {count.get('icon', 0)} · مؤثرات صوتية {count.get('sfx', 0)} · خطوط {count.get('font', 0)} · "
             f"موسيقى {count.get('music', 0)} · صور {count.get('image', 0)} · جلسات {len(sess)}"
             + (f" · آخر جلسة `sessions/{sess[-1].name}`" if sess else "") + "\n<!-- stats:end -->")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    if "<!-- stats:start -->" in text:
        text = re.sub(r"<!-- stats:start -->.*?<!-- stats:end -->", block, text, flags=re.S)
    else:
        lines = text.splitlines()
        lines.insert(2, block)
        text = "\n".join(lines) + "\n"
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    report = sessions()
    stats()
    print(run("scripts/journal_digest.py"))
    if (ROOT / "chats").exists():
        print("chats: موجودة — فهرسها في chats/index.md")
    print(run("scripts/brain_map.py"))
    print(run("scripts/brain_doctor.py"))
    t = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=ROOT, capture_output=True, text=True)
    print("tests:", (t.stderr.strip().splitlines() or ["?"])[-1])
    report += duplicates()
    print("\n".join(["— تقرير الترتيب —", *report]) if report else "— لا شيء يحتاج تنظيفاً —")


if __name__ == "__main__":
    main()
