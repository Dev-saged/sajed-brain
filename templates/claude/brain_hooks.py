#!/usr/bin/env python3
"""خطافات الدماغ لكل مشروع. تُنسخ إلى .claude/brain_hooks.py عبر scripts/install_project.py.
boot        SessionStart: يطبع الدماغ + الدستور + handoff + آخر commits + ملخص scout
stop        Stop: يمنع الإنهاء إن تغيّر الكود ولم يُحدَّث handoff
learn       يرسل سطر تعلّم للدماغ (gh workflow) أو يطبع السطر الجاهز؛ --bad ينشئ حارساً مقترحاً؛ --file journal --ok|--fail ليومية الجلسة
scout       يشغّل الماسح من نسخة محلية مخبّأة للدماغ
commit-msg  يزيل ذيول الأدوات ويرفض emoji/عناوين طويلة"""
import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

BRAIN_REPO = "Dev-saged/sajed-brain"
RAW = f"https://raw.githubusercontent.com/{BRAIN_REPO}/main/"
ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
CACHE = ROOT / ".claude" / ".brain-cache"
TOKEN = os.environ.get("BRAIN_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
TRAILER = re.compile(r"(?im)^(?:co-authored-by:.*(?:claude|anthropic|copilot|gpt|openai|gemini).*|claude-session:.*|"
                     r".*generated (?:with|by) .*|.*\U0001F916.*)\n?")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐]")


def fetch(name):
    req = urllib.request.Request(RAW + name, headers={"Authorization": f"token {TOKEN}"} if TOKEN else {})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            text = r.read().decode("utf-8")
        (CACHE / name).parent.mkdir(parents=True, exist_ok=True)
        (CACHE / name).write_text(text, encoding="utf-8")
        return text
    except Exception:
        cached = CACHE / name
        return cached.read_text(encoding="utf-8") if cached.exists() else ""


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=15).stdout
    except (subprocess.SubprocessError, OSError):
        return ""


def recent_failures(limit=5):
    month = datetime.date.today().strftime("%Y-%m")
    text = fetch(f"journal/{month}.md")
    mine = [ln for ln in text.splitlines() if f"@{ROOT.name} " in ln and "✗" in ln]
    return mine[-limit:]


def boot():
    parts = [fetch("README.md"), fetch("CHARTER.md")]
    for rel in (".claude/session-handoff.md",):
        p = ROOT / rel
        parts.append(f"## {rel}\n{p.read_text(encoding='utf-8')}" if p.exists() else f"## {rel}\n(مفقود — أنشئه قبل أي عمل)")
    parts.append("## git log\n" + (git("log", "--oneline", "-15") or "(لا تاريخ)"))
    fails = recent_failures()
    if fails:
        parts.append("## تعثّرات سابقة في هذا المشروع (journal)\n" + "\n".join(fails))
    report = ROOT / "docs" / "scout-report.md"
    if report.exists():
        parts.append("## scout (أعلى التقرير)\n" + "\n".join(report.read_text(encoding="utf-8").splitlines()[:30]))
    print("\n\n".join(p for p in parts if p))
    return 0


def changed_paths():
    out = git("status", "--porcelain")
    paths = [ln[3:].split(" -> ")[-1].strip('"') for ln in out.splitlines()]
    return [p for p in paths if not p.startswith((".claude/", "docs/"))]


def stop():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}
    if payload.get("stop_hook_active"):
        return 0
    changed = [ROOT / p for p in changed_paths() if (ROOT / p).exists()]
    if not changed:
        return 0
    handoff = ROOT / ".claude" / "session-handoff.md"
    if handoff.exists() and handoff.stat().st_mtime >= max(p.stat().st_mtime for p in changed):
        return 0
    print("قبل الإنهاء: (1) أعد كتابة .claude/session-handoff.md (≤25 سطراً: الحالة، القرارات، المشاكل، الخطوة التالية) "
          "(2) سطران في docs/repo-map.md (3) أي قرار/خطأ/نمط جديد أرسله: "
          "python3 .claude/brain_hooks.py learn --file mistakes.md --text '#وسم نص' [--bad 'كود خاطئ' --message '...'] "
          "(4) يومية: learn --file journal --ok|--fail --text '#وسم ما نجح/فشل'", file=sys.stderr)
    return 2


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:30].strip("-") if len(s) >= 3 else ""


def run_gh(workflow, fields):
    cmd = ["gh", "workflow", "run", workflow, "--repo", BRAIN_REPO]
    for k, v in fields.items():
        cmd += ["-f", f"{k}={v}"]
    subprocess.run(cmd, check=True, capture_output=True, timeout=30)


def learn(argv):
    ap = argparse.ArgumentParser(prog="learn")
    ap.add_argument("--file", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--bad")
    ap.add_argument("--good", default="")
    ap.add_argument("--id")
    ap.add_argument("--severity", default="warn")
    ap.add_argument("--message")
    ap.add_argument("--ok", action="store_true")
    ap.add_argument("--fail", action="store_true")
    a = ap.parse_args(argv)
    today = datetime.date.today()
    target, text = a.file, a.text
    if target == "journal":
        target = f"journal/{today:%Y-%m}.md"
        text = ("✗ " if a.fail else "✓ ") + text
    guard_id = a.id or slug(a.text) if a.bad else ""
    if a.bad and not guard_id:
        print("--id مطلوب (slug لاتيني) لتوليد الحارس", file=sys.stderr)
        return 1
    if guard_id:
        text += f" guard:{guard_id}"
    line = f"- [{today.isoformat()}] @{ROOT.name} {text}"
    jobs = [("brain-update.yml", {"file": target, "action": "append", "content": line})]
    if guard_id:
        jobs.append(("brain-guard.yml", {"id": guard_id, "bad": a.bad, "good": a.good,
                                         "message": a.message or a.text, "severity": a.severity}))
    try:
        for wf, fields in jobs:
            run_gh(wf, fields)
        print(f"أُرسل إلى {target}: {line}" + (f"\nحارس مقترح (PR): {guard_id}" if guard_id else ""))
    except (subprocess.SubprocessError, OSError):
        print(f"gh غير متاح — أضف يدوياً إلى {target}:\n{line}")
        if guard_id:
            print(f"وللحارس: python3 scripts/guard_suggest.py --id {guard_id} --bad '{a.bad}' --message '{a.message or a.text}' --add")
    return 0


def scout(argv):
    brain = pathlib.Path.home() / ".cache" / "sajed-brain"
    url = f"https://github.com/{BRAIN_REPO}.git"
    extra = ["-c", f"http.extraheader=Authorization: token {TOKEN}"] if TOKEN else []
    try:
        if (brain / ".git").exists():
            subprocess.run(["git", *extra, "-C", str(brain), "pull", "-q", "--ff-only"], check=True, timeout=60)
        else:
            brain.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", *extra, "clone", "--depth", "1", "-q", url, str(brain)], check=True, timeout=120)
    except (subprocess.SubprocessError, OSError):
        if not (brain / "scripts" / "scout.py").exists():
            print("تعذّر جلب الدماغ — لا نسخة مخبّأة", file=sys.stderr)
            return 1
    return subprocess.run([sys.executable, str(brain / "scripts" / "scout.py"), str(ROOT), *argv]).returncode


def commit_msg(argv):
    path = pathlib.Path(argv[0])
    text = path.read_text(encoding="utf-8")
    clean = TRAILER.sub("", text).rstrip() + "\n"
    if clean != text:
        path.write_text(clean, encoding="utf-8")
    subject = clean.splitlines()[0] if clean.strip() else ""
    problems = []
    if len(subject) > 72:
        problems.append(f"العنوان {len(subject)} حرفاً (>72)")
    if EMOJI.search(clean):
        problems.append("emoji ممنوع")
    if problems:
        print("commit مرفوض: " + "، ".join(problems), file=sys.stderr)
        return 1
    return 0


def main():
    cmd, rest = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    handlers = {"boot": lambda: boot(), "stop": lambda: stop(), "learn": lambda: learn(rest),
                "scout": lambda: scout(rest), "commit-msg": lambda: commit_msg(rest)}
    if cmd not in handlers:
        print(__doc__)
        return 1
    return handlers[cmd]()


if __name__ == "__main__":
    sys.exit(main())
