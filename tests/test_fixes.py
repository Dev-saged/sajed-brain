import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scoutlib import cli, external, fixes  # noqa: E402

KT = '''package com.x.ui

import androidx.compose.material3.Divider
import androidx.compose.material3.Text
import androidx.compose.runtime.collectAsState

fun title(s: String): String {
    // old: s.toLowerCase()
    val note = "call .toUpperCase() later"
    return s.toLowerCase().capitalize() + note
}

fun rows() {
    Divider(thickness = 1.dp)
    val a = flow.collectAsState()
}
'''


def project(files):
    d = pathlib.Path(tempfile.mkdtemp())
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return d


class FixTests(unittest.TestCase):
    def test_code_only_rewrites_and_imports(self):
        d = project({"app/A.kt": KT})
        stats = cli.maintain(d, imports=False)
        out = (d / "app/A.kt").read_text(encoding="utf-8")
        self.assertIn("s.lowercase().replaceFirstChar { it.uppercase() }", out)
        self.assertIn("// old: s.toLowerCase()", out)            # تعليق لم يُمس
        self.assertIn('"call .toUpperCase() later"', out)        # نص لم يُمس
        self.assertIn("HorizontalDivider(thickness = 1.dp)", out)
        self.assertIn("import androidx.compose.material3.HorizontalDivider", out)
        self.assertNotIn("import androidx.compose.material3.Divider\n", out)
        self.assertIn(".collectAsState()", out)                  # بلا lifecycle-runtime-compose لا تغيير
        self.assertEqual(stats["fixes"]["fix-lowercase"], 1)

    def test_dependency_gated_fix(self):
        d = project({"app/A.kt": KT, "gradle/libs.versions.toml": 'lifecycle-runtime-compose = "x"\n'})
        cli.maintain(d, imports=False)
        out = (d / "app/A.kt").read_text(encoding="utf-8")
        self.assertIn("flow.collectAsStateWithLifecycle()", out)
        self.assertIn("import androidx.lifecycle.compose.collectAsStateWithLifecycle", out)
        self.assertNotIn("import androidx.compose.runtime.collectAsState\n", out)

    def test_idempotent_and_m2_divider_untouched(self):
        d = project({"A.kt": KT, "B.kt": "import androidx.compose.material.Divider\nimport androidx.compose.material3.Text\nfun f() { Divider() }\n",
                     "build.gradle.kts": "repositories {\n    jcenter()\n    mavenCentral()\n}\n"})
        cli.maintain(d, imports=False)
        self.assertEqual(cli.maintain(d, imports=False)["fixes"], {})
        self.assertIn("Divider()", (d / "B.kt").read_text(encoding="utf-8"))
        self.assertNotIn("HorizontalDivider", (d / "B.kt").read_text(encoding="utf-8"))
        self.assertEqual((d / "build.gradle.kts").read_text(encoding="utf-8"), "repositories {\n    mavenCentral()\n}\n")

    def test_maintain_removes_unused_imports(self):
        d = project({"A.kt": "import a.Used\nimport a.Gone\nfun f() = Used()\n"})
        self.assertEqual(cli.maintain(d, fix=False)["imports"], 1)

    def test_fix_rules_are_valid(self):
        for r in fixes.load_fixes():
            self.assertTrue({"id", "tier", "pattern", "replace"} <= r.keys(), r["id"])


SARIF = {"runs": [{"results": [
    {"ruleId": "detekt.style.UnusedPrivateMember", "message": {"text": "x"},
     "locations": [{"physicalLocation": {"artifactLocation": {"uri": "file:///w/app/V.kt"}, "region": {"startLine": 4}}}]},
    {"ruleId": "detekt.style.UnusedPrivateProperty", "message": {"text": "y"},
     "locations": [{"physicalLocation": {"artifactLocation": {"uri": "app/V.kt"}, "region": {"startLine": 9}}}]},
]}]}


class DetektTests(unittest.TestCase):
    def setUp(self):
        self.d = project({"app/V.kt": "class Vault {\n    private val gone = 1\n    private fun alsoGone() {}\n    private val other = 2\n}\n"})

    def scan(self, *extra):
        out = self.d / "docs"
        cli.run([str(self.d), "--out", str(out), *extra])
        return json.loads((out / "scout.json").read_text(encoding="utf-8"))["findings"]

    def dead(self, found):
        return {f["text"] or f["line"]: f for f in found if f["rule"] == "dead-symbol"}

    def test_without_report_all_private_are_t0(self):
        dead = self.dead(self.scan())
        self.assertEqual({f["tier"] for f in dead.values() if f["text"] in ("gone", "alsoGone", "other")}, {"T0"})

    def test_report_confirms_and_downgrades(self):
        sarif = self.d / "d.sarif"
        sarif.write_text(json.dumps({"runs": [{"results": [
            {"ruleId": "detekt.style.UnusedPrivateProperty", "message": {"text": "m"},
             "locations": [{"physicalLocation": {"artifactLocation": {"uri": "file:///w/app/V.kt"}, "region": {"startLine": 2}}}]}]}]}))
        dead = self.dead(self.scan("--detekt-report", str(sarif)))
        self.assertEqual(dead["gone"]["tier"], "T0")
        self.assertIn("مؤكَّد", dead["gone"]["message"])
        self.assertEqual(dead["alsoGone"]["tier"], "T1")      # لم يؤكده detekt
        self.assertIn("لم يؤكده", dead["alsoGone"]["message"])

    def test_detekt_only_findings_added_and_foreign_paths_ignored(self):
        found = external.merge([], external.parse_sarif(json.dumps(SARIF)), {"app/V.kt"})
        self.assertEqual({(f["path"], f["line"]) for f in found}, {("app/V.kt", 4), ("app/V.kt", 9)})
        self.assertEqual(external.merge([], external.parse_sarif(json.dumps(SARIF)), {"other/W.kt"}), [])

    def test_missing_report_is_ignored(self):
        self.assertIsNone(external.load(self.d / "nope.sarif"))


if __name__ == "__main__":
    unittest.main()
