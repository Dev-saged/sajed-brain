import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import brain_doctor  # noqa: E402
import brief  # noqa: E402
import crossref  # noqa: E402
import deps_radar  # noqa: E402
import install_project  # noqa: E402

TOML = '''[versions]
kotlin = "2.0.0"
compose-bom = "2024.06.00"
hilt = "2.51"
room = "2.7.0-alpha01"
[libraries]
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
lonely = { module = "x.y:z", version = "1.0.0" }
nobom = { module = "androidx.compose.ui:ui" }
[plugins]
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
'''

META = {
    "androidx/room/room-runtime": ["2.6.1", "2.7.0-alpha01", "2.7.0-alpha03", "2.7.0-beta01"],
    "com/google/dagger/hilt-android": ["2.51", "2.51.1", "2.52", "2.53-rc1"],
    "androidx/compose/compose-bom": ["2024.06.00", "2024.09.03"],
    "x/y/z": ["1.0.0", "1.0.1"],
    "org/jetbrains/kotlin/android/org.jetbrains.kotlin.android.gradle.plugin": ["2.0.0", "2.0.21", "3.0.0"],
}


def fake_fetch(url):
    for key, versions in META.items():
        if f"/{key}/maven-metadata.xml" in url:
            xml = "".join(f"<version>{v}</version>" for v in versions)
            return f"<metadata><versioning><versions>{xml}</versions></versioning></metadata>"
    return None


class DepsTests(unittest.TestCase):
    def test_version_ordering_and_bump(self):
        self.assertGreater(deps_radar.vkey("2.7.0"), deps_radar.vkey("2.7.0-rc1"))
        self.assertGreater(deps_radar.vkey("2.7.0-rc1"), deps_radar.vkey("2.7.0-beta2"))
        self.assertGreater(deps_radar.vkey("1.10.0"), deps_radar.vkey("1.9.9"))
        self.assertEqual(deps_radar.bump("2.51", "2.51.1"), "patch")
        self.assertEqual(deps_radar.bump("2.51", "2.52"), "minor")
        self.assertEqual(deps_radar.bump("2.0.0", "3.0.0"), "major")

    def test_rows_and_apply(self):
        d = pathlib.Path(tempfile.mkdtemp()) / "libs.versions.toml"
        d.write_text(TOML, encoding="utf-8")
        rows = {r["key"]: r for r in deps_radar.run(d, fetch=fake_fetch)}
        self.assertEqual(rows["room"]["latest"], "2.7.0-beta01")     # قناة pre تبقى ضمن pre
        self.assertEqual(rows["hilt"]["latest"], "2.52")             # يتجاهل rc
        self.assertEqual(rows["kotlin"]["bump"], "major")
        self.assertEqual(rows["lonely"]["bump"], "patch")
        self.assertNotIn("nobom", rows)
        self.assertEqual(deps_radar.apply(d, list(rows.values())), 3)  # room + hilt + compose-bom
        text = d.read_text(encoding="utf-8")
        self.assertIn('hilt = "2.52"', text)
        self.assertIn('kotlin = "2.0.0"', text)                       # major لا يُطبَّق
        self.assertIn("T2", deps_radar.to_markdown(list(rows.values())))

    def test_unreachable_is_graceful(self):
        d = pathlib.Path(tempfile.mkdtemp()) / "libs.versions.toml"
        d.write_text(TOML, encoding="utf-8")
        rows = deps_radar.run(d, fetch=lambda u: None)
        self.assertTrue(all(r["bump"] == "?" for r in rows))
        self.assertIn("لم يُتحقق", deps_radar.to_markdown(rows))


class BriefTests(unittest.TestCase):
    def test_arabic_task_pulls_relevant_chunks_within_budget(self):
        out = brief.brief("أضف وحدة ديون جديدة مع Room migration", project="qayd", budget=1800)
        self.assertIn("migration", out)
        self.assertIn("Balance", out)
        self.assertLessEqual(len(out), 2600)

    def test_irrelevant_task_is_small(self):
        self.assertLessEqual(len(brief.brief("zzzz qqqq")), 10)


class DoctorTests(unittest.TestCase):
    def test_real_repo_has_no_errors(self):
        errors, _ = brain_doctor.check()
        self.assertEqual(errors, [], errors)

    def test_detects_missing_workflow_and_bad_rule(self):
        d = pathlib.Path(tempfile.mkdtemp())
        (d / ".github/workflows").mkdir(parents=True)
        (d / "rules").mkdir()
        (d / "README.md").write_text("run `brain-update.yml` and `features/none.md`", encoding="utf-8")
        (d / "rules/guards.json").write_text(json.dumps([{"id": "a", "severity": "warn", "tier": "T0",
                                                          "pattern": "(", "message": "m", "source": "s"}]))
        (d / "rules/deprecated.json").write_text("[]")
        errors, warns = brain_doctor.check(d)
        self.assertTrue(any("brain-update.yml" in e for e in errors))
        self.assertTrue(any("regex" in e for e in errors))
        self.assertTrue(any("features/none.md" in w for w in warns))

    def test_secret_in_brain_is_error(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for sub in (".github/workflows", "rules"):
            (d / sub).mkdir(parents=True)
        (d / "README.md").write_text("x", encoding="utf-8")
        (d / "rules/guards.json").write_text("[]")
        (d / "rules/deprecated.json").write_text("[]")
        (d / "mistakes.md").write_text("- [2026-01-01] ghp_" + "a" * 36, encoding="utf-8")
        errors, _ = brain_doctor.check(d)
        self.assertTrue(any("سر ظاهر" in e for e in errors))


class CrossrefTests(unittest.TestCase):
    def test_shared_and_drift(self):
        idx = pathlib.Path(tempfile.mkdtemp())
        row = lambda n, h, loc: f"{n}\tfun\tpublic\t{loc}\t1\ttop\t12\t{h}\n"
        for proj, lines in {"qayd": row("formatMoney", "aaa", "A.kt:1") + row("parse", "p1", "B.kt:2"),
                            "barq": row("formatMoney", "aaa", "C.kt:3") + row("parse", "p2", "D.kt:4")}.items():
            (idx / proj).mkdir()
            (idx / proj / "symbol-index.tsv").write_text(lines, encoding="utf-8")
        shared, drift = crossref.analyse(crossref.load(idx))
        self.assertEqual([g[0]["name"] for g in shared], ["formatMoney"])
        self.assertEqual([g[0]["name"] for g in drift], ["parse"])


class InstallAndHooksTests(unittest.TestCase):
    def setUp(self):
        self.p = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=self.p, check=True)
        (self.p / ".claude").mkdir()
        (self.p / ".claude/settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}}))
        (self.p / "CLAUDE.md").write_text("# قيد\nقواعد قائمة\n", encoding="utf-8")

    def test_install_is_idempotent_and_preserves_existing(self):
        install_project.install(self.p)
        install_project.install(self.p)
        cfg = json.loads((self.p / ".claude/settings.json").read_text())
        self.assertEqual(cfg["permissions"]["allow"], ["Bash(ls)"])
        self.assertEqual(len(cfg["hooks"]["Stop"]), 1)
        md = (self.p / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("قواعد قائمة", md)
        self.assertEqual(md.count("brain:begin"), 1)
        for rel in ("docs/repo-map.md", ".claude/session-handoff.md", ".githooks/commit-msg", ".github/workflows/scout.yml"):
            self.assertTrue((self.p / rel).exists(), rel)
        hp = subprocess.run(["git", "config", "core.hooksPath"], cwd=self.p, capture_output=True, text=True).stdout.strip()
        self.assertEqual(hp, ".githooks")

    def hook(self, *args, stdin=""):
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.p)}
        return subprocess.run([sys.executable, str(ROOT / "templates/claude/brain_hooks.py"), *args],
                              input=stdin, capture_output=True, text=True, env=env)

    def test_commit_msg_strips_tool_trailers_and_rejects_emoji(self):
        msg = self.p / "MSG"
        msg.write_text("fix: round debt totals\n\nCo-Authored-By: Claude <x@y>\nClaude-Session: https://x\n")
        self.assertEqual(self.hook("commit-msg", str(msg)).returncode, 0)
        self.assertEqual(msg.read_text(), "fix: round debt totals\n")
        msg.write_text("feat: add screen \U0001F680\n")
        self.assertEqual(self.hook("commit-msg", str(msg)).returncode, 1)
        msg.write_text("x" * 80 + "\n")
        self.assertEqual(self.hook("commit-msg", str(msg)).returncode, 1)

    def test_stop_blocks_until_handoff_fresh(self):
        install_project.install(self.p)
        subprocess.run(["git", "add", "-A"], cwd=self.p, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base"], cwd=self.p, check=True)
        self.assertEqual(self.hook("stop", stdin="{}").returncode, 0)          # لا تغييرات
        src = self.p / "A.kt"
        src.write_text("fun a() = 1\n")
        handoff = self.p / ".claude/session-handoff.md"
        os.utime(handoff, (src.stat().st_mtime - 50,) * 2)
        blocked = self.hook("stop", stdin="{}")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("session-handoff", blocked.stderr)
        self.assertEqual(self.hook("stop", stdin='{"stop_hook_active": true}').returncode, 0)
        os.utime(handoff, (src.stat().st_mtime + 50,) * 2)
        self.assertEqual(self.hook("stop", stdin="{}").returncode, 0)

    def test_learn_without_gh_prints_ready_line(self):
        r = self.hook("learn", "--file", "mistakes.md", "--text", "#room migration مُعدّلة")
        self.assertEqual(r.returncode, 0)
        self.assertIn("- [", r.stdout)
        self.assertIn("mistakes.md", r.stdout)


if __name__ == "__main__":
    unittest.main()
