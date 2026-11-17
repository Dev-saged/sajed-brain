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
import guard_suggest  # noqa: E402
import journal_digest  # noqa: E402
from scoutlib import cli, findings  # noqa: E402


class GuardSuggestTests(unittest.TestCase):
    def test_pattern_catches_bad_variants_not_good(self):
        e = guard_suggest.make_entry("no-global-prefs", "getSharedPreferences(name, 0)", "استخدم EncryptedSharedPreferences",
                                     good="EncryptedSharedPreferences.create(ctx)")
        import re
        pat = re.compile(e["pattern"])
        self.assertTrue(pat.search("val p = getSharedPreferences(name,0)"))
        self.assertTrue(pat.search("getSharedPreferences( name , 0 )"))
        self.assertFalse(pat.search("EncryptedSharedPreferences.create(ctx)"))

    def test_numbers_generalised_and_string_scope_raw(self):
        e = guard_suggest.make_entry("no-http", 'url = "http://api"', "HTTP ممنوع")
        self.assertEqual(e["scope"], "raw")
        e2 = guard_suggest.make_entry("no-delay-500", "delay(500)", "ثابت مدة")
        import re
        self.assertTrue(re.search(e2["pattern"], "delay(750)"))

    def test_rejects_bad_id_good_overlap_and_duplicates(self):
        with self.assertRaises(ValueError):
            guard_suggest.make_entry("X", "a", "m")
        with self.assertRaises(ValueError):
            guard_suggest.make_entry("overlap-case", "foo(1)", "m", good="foo(2)")
        d = pathlib.Path(tempfile.mkdtemp()) / "guards.json"
        d.write_text((ROOT / "rules/guards.json").read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaises(ValueError):
            guard_suggest.add_entry({"id": "icon-pack"}, d)

    def test_added_guard_is_live_in_scout_and_file_stays_valid(self):
        d = pathlib.Path(tempfile.mkdtemp())
        g = d / "guards.json"
        g.write_text((ROOT / "rules/guards.json").read_text(encoding="utf-8"), encoding="utf-8")
        before = len(json.loads(g.read_text(encoding="utf-8")))
        guard_suggest.add_entry(guard_suggest.make_entry("no-thread-sleep", "Thread.sleep(1000)", "استخدم delay"), g)
        rules = json.loads(g.read_text(encoding="utf-8"))
        self.assertEqual(len(rules), before + 1)
        src = cli.Src("fun w() { Thread.sleep(250) }\n", cli.lex("fun w() { Thread.sleep(250) }\n"))
        hits = findings.apply_rules({"A.kt": src}, rules, only={"no-thread-sleep"})
        self.assertEqual(len(hits), 1)

    def test_cli_exit_codes(self):
        self.assertEqual(guard_suggest.main(["--id", "ok-guard", "--bad", "foo(1)", "--message", "m"]), 0)
        self.assertEqual(guard_suggest.main(["--id", "BAD", "--bad", "foo(1)", "--message", "m"]), 1)


class DoctorGuardLinkTests(unittest.TestCase):
    def test_unguarded_and_dangling(self):
        d = pathlib.Path(tempfile.mkdtemp())
        for sub in (".github/workflows", "rules"):
            (d / sub).mkdir(parents=True)
        (d / "README.md").write_text("x", encoding="utf-8")
        (d / "rules/guards.json").write_text("[]")
        (d / "rules/deprecated.json").write_text("[]")
        (d / "mistakes.md").write_text("- [2026-11-17] @qayd #room بلا حارس\n- [2026-11-17] @qayd #x guard:ghost\n"
                                       "- [2026-11-17] @qayd #y noguard\n- سطر قديم بلا تاريخ\n", encoding="utf-8")
        _, warns = brain_doctor.check(d)
        self.assertTrue(any("بلا حارس" in w for w in warns))
        self.assertTrue(any("ghost" in w for w in warns))
        self.assertFalse(any("#y" in w or "قديم" in w for w in warns))


JOURNAL = """- [2026-10-02] @qayd ✓ #room migration نجحت من أول مرة
- [2026-10-03] @qayd ✗ #ksp فشل البناء بعد ترقية hilt
- [2026-10-09] @qayd ✗ #ksp تعارض نسخ
- [2026-10-11] @barq ✗ #ksp نفس المشكلة
- [2026-10-12] @barq ✗ #compose recomposition زائدة
سطر عشوائي
"""


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.d = pathlib.Path(tempfile.mkdtemp())
        (self.d / "journal").mkdir()
        (self.d / "journal/2026-10.md").write_text(JOURNAL, encoding="utf-8")
        (self.d / "journal/2026-11.md").write_text("- [2026-11-02] @qayd ✓ #x ok\n", encoding="utf-8")

    def test_digest_compresses_only_past_months(self):
        import datetime
        done = journal_digest.run(self.d, today=datetime.date(2026, 11, 17))
        self.assertEqual(done, ["2026-10"])
        digest = (self.d / "journal/digest.md").read_text(encoding="utf-8")
        self.assertIn("## 2026-10", digest)
        self.assertIn("5 تسجيلاً (✓ 1 / ✗ 4)", digest)
        self.assertIn("#ksp×3", digest)
        self.assertNotIn("#compose×", digest)
        self.assertTrue((self.d / "journal/archive/2026-10.md").exists())
        self.assertTrue((self.d / "journal/2026-11.md").exists())
        self.assertEqual(journal_digest.run(self.d, today=datetime.date(2026, 11, 17)), [])

    def test_rerun_replaces_section_not_duplicates(self):
        import datetime
        journal_digest.run(self.d, today=datetime.date(2026, 12, 1))
        (self.d / "journal/archive/2026-10.md").rename(self.d / "journal/2026-10.md")
        journal_digest.run(self.d, today=datetime.date(2026, 12, 1))
        self.assertEqual((self.d / "journal/digest.md").read_text(encoding="utf-8").count("## 2026-10"), 1)


class HookLearnTests(unittest.TestCase):
    def hook(self, *args):
        p = pathlib.Path(tempfile.mkdtemp())
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(p), "PATH": "/nonexistent"}
        return subprocess.run([sys.executable, str(ROOT / "templates/claude/brain_hooks.py"), *args],
                              capture_output=True, text=True, env=env)

    def test_journal_line_and_target(self):
        r = self.hook("learn", "--file", "journal", "--fail", "--text", "#ksp فشل البناء")
        self.assertIn("journal/", r.stdout)
        self.assertIn("✗ #ksp", r.stdout)

    def test_bad_snippet_adds_guard_marker_and_fallback_command(self):
        r = self.hook("learn", "--file", "mistakes.md", "--text", "no-sleep خطأ", "--bad", "Thread.sleep(1)", "--id", "no-thread-sleep")
        self.assertIn("guard:no-thread-sleep", r.stdout)
        self.assertIn("guard_suggest.py --id no-thread-sleep", r.stdout)

    def test_bad_without_latin_id_fails(self):
        r = self.hook("learn", "--file", "mistakes.md", "--text", "خطأ عربي فقط", "--bad", "x(1)")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
