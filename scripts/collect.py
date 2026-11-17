#!/usr/bin/env python3
"""يجمع حالة كل المشاريع في index/: scout + deps + لوحة HEALTH.md + CROSS.md. يحتاج GH_PAT في البيئة."""
import base64
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import crossref  # noqa: E402


def clone(repo, dest, token):
    auth = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    subprocess.run(["git", "-c", f"http.extraheader=Authorization: Basic {auth}", "clone", "--depth", "50", "-q",
                    f"https://github.com/{repo}.git", str(dest)], check=True, timeout=300)


def health_row(name, out):
    data = json.loads((out / "scout.json").read_text(encoding="utf-8"))
    f = data["findings"]
    errors = sum(x["severity"] == "error" for x in f)
    dead = sum(x["rule"] == "dead-symbol" for x in f)
    deps = out / "deps-report.md"
    behind = max(0, deps.read_text(encoding="utf-8").count("\n| ") - 2) if deps.exists() else 0
    return f"| {name} | {data['score']} | {errors} | {dead} | {behind} |"


def main():
    token = os.environ.get("GH_PAT")
    if not token:
        sys.exit("GH_PAT غير مضبوط")
    projects = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
    rows = ["# لوحة الصحة", "", "| المشروع | النتيجة | أخطاء | ميت | اعتماديات متأخرة |", "|---|---|---|---|---|"]
    for p in projects:
        out = ROOT / "index" / p["name"]
        out.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            try:
                clone(p["repo"], tmp, token)
            except (subprocess.SubprocessError, OSError):
                rows.append(f"| {p['name']} | غير متاح | | | |")
                continue
            subprocess.run([sys.executable, str(ROOT / "scripts" / "scout.py"), tmp, "--out", str(out)], check=True)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "deps_radar.py"), tmp, "--out", str(out)], check=False)
        rows.append(health_row(p["name"], out))
    (ROOT / "index" / "HEALTH.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    crossref.main()


if __name__ == "__main__":
    main()
