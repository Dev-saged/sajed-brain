#!/usr/bin/env python3
"""خطافات الدماغ لكل مشروع. تُنسخ إلى .claude/brain_hooks.py عبر scripts/install_project.py.
boot        SessionStart: يطبع الدماغ + الدستور + handoff + آخر commits + ملخص scout
stop        Stop: يمنع الإنهاء إن تغيّر الكود ولم يُحدَّث handoff
learn       يرسل سطر تعلّم للدماغ (gh workflow) أو يطبع السطر الجاهز
scout       يشغّل الماسح من نسخة محلية مخبّأة للدماغ
commit-msg  يزيل ذيول الأدوات ويرفض emoji/عناوين طويلة"""
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
        CACHE.mkdir(parents=True, exist_ok=True)
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


def boot():
    parts = [fetch("README.md"), fetch("CHARTER.md")]
    for rel in (".claude/session-handoff.md",):
        p = ROOT / rel
        parts.append(f"## {rel}\n{p.read_text(encoding='utf-8')}" if p.exists() else f"## {rel}\n(مفقود — أنشئه قبل أي عمل)")
    parts.append("## git log\n" + (git("log", "--oneline", "-15") or "(لا تاريخ)"))
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
          "python3 .claude/brain_hooks.py learn --file mistakes.md --text '#وسم نص'", file=sys.stderr)
    return 2


def learn(argv):
    opts = dict(zip(argv[::2], argv[1::2]))
    target, text = opts.get("--file"), opts.get("--text")
    if not target or not text:
        print("الاستخدام: learn --file <mistakes.md|ideas.md|preferences.md|features/x.md> --text '...'", file=sys.stderr)
        return 1
    project = ROOT.name
    line = f"- [{datetime.date.today().isoformat()}] @{project} {text}"
    cmd = ["gh", "workflow", "run", "brain-update.yml", "--repo", BRAIN_REPO,
           "-f", f"file={target}", "-f", "action=append", "-f", f"content={line}"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        print(f"أُرسل إلى {target}: {line}")
        return 0
    except (subprocess.SubprocessError, OSError):
        print(f"gh غير متاح — أضف يدوياً إلى {target}:\n{line}")
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
