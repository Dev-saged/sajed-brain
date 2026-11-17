#!/usr/bin/env python3
"""يثبّت طبقة الدماغ في مشروع: خطافات Claude، commit-msg، scout.yml، وملفات الذاكرة الناقصة. آمن للتكرار.
install_project.py <path-to-project>"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "templates"
BLOCK = re.compile(r"<!-- brain:begin -->.*?<!-- brain:end -->\n?", re.S)

STUBS = {
    "docs/repo-map.md": "# repo-map\n_تحت 5KB، بلا كود_\n\n## الميزات (ميزة → ملف → رمز)\n\n## القرارات\n\n## أخطاء محلولة\n\n## مشاكل مفتوحة\n",
    ".claude/session-handoff.md": "# session-handoff\n_≤25 سطراً، يُعاد كتابته كل جلسة_\n\n## الحالة\nمشروع جديد على طبقة الدماغ.\n\n## الخطوة التالية\nاقرأ CLAUDE.md ثم docs/repo-map.md وحدّد أول مهمة.\n",
}


def merge_settings(dest):
    new = json.loads((T / "claude" / "settings.json").read_text(encoding="utf-8"))
    cur = json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {}
    hooks = cur.setdefault("hooks", {})
    for event, entries in new["hooks"].items():
        have = {h["command"] for e in hooks.get(event, []) for h in e.get("hooks", [])}
        hooks.setdefault(event, []).extend(e for e in entries if e["hooks"][0]["command"] not in have)
    dest.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def install(project):
    p = pathlib.Path(project).resolve()
    done = []

    def put(rel, text=None, src=None, mode=None):
        dest = p / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src:
            shutil.copyfile(src, dest)
        else:
            dest.write_text(text, encoding="utf-8")
        if mode:
            dest.chmod(mode)
        done.append(rel)

    put(".claude/brain_hooks.py", src=T / "claude" / "brain_hooks.py", mode=0o755)
    (p / ".claude").mkdir(exist_ok=True)
    merge_settings(p / ".claude" / "settings.json")
    done.append(".claude/settings.json")
    put(".githooks/commit-msg", src=T / "git-hooks" / "commit-msg", mode=0o755)
    put(".github/workflows/scout.yml", src=T / "workflows" / "scout.yml")

    block = (T / "project-claude-md.md").read_text(encoding="utf-8")
    cmd = p / "CLAUDE.md"
    if not cmd.exists():
        put("CLAUDE.md", f"# {p.name}\n\n{block}")
    else:
        text = cmd.read_text(encoding="utf-8")
        cmd.write_text(BLOCK.sub(block, text) if BLOCK.search(text) else text.rstrip() + "\n\n" + block, encoding="utf-8")
        done.append("CLAUDE.md")
    for rel, text in STUBS.items():
        if not (p / rel).exists():
            put(rel, text)

    if (p / ".git").exists():
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=p, check=False)
    return done


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for rel in install(sys.argv[1]):
        print("✓", rel)


if __name__ == "__main__":
    main()
