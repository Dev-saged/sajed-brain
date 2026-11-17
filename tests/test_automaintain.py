import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import auto_maintain  # noqa: E402

TOML = '[versions]\nhilt = "2.51"\nkotlin = "2.0.0"\n[libraries]\nhilt = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }\n[plugins]\nkp = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }\n'
META = {"com/google/dagger/hilt-android": ["2.51", "2.52"],
        "org/jetbrains/kotlin/android/org.jetbrains.kotlin.android.gradle.plugin": ["2.0.0", "3.0.0"]}


def fetch(url):
    for k, vs in META.items():
        if f"/{k}/maven-metadata.xml" in url:
            return "<m><versioning><versions>" + "".join(f"<version>{v}</version>" for v in vs) + "</versions></versioning></m>"
    return None


def repo(files):
    d = pathlib.Path(tempfile.mkdtemp())
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    run = lambda *c: subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *c], cwd=d, check=True, capture_output=True)
    run("init", "-q"), run("add", "-A"), run("commit", "-qm", "base")
    return d


class AutoMaintainTests(unittest.TestCase):
    def test_changes_produce_body_with_tiers(self):
        d = repo({"A.kt": "import a.Gone\nfun t(s: String) = s.toLowerCase()\n", "gradle/libs.versions.toml": TOML})
        body = d / "pr.md"
        auto_maintain.main([str(d), "--body", str(body)], fetch=fetch)
        text = body.read_text(encoding="utf-8")
        self.assertIn("fix-lowercase: 1", text)
        self.assertIn("أُزيلت 1", text)
        self.assertIn("hilt: 2.51 ← 2.52", text)
        self.assertIn("kotlin: 2.0.0 ← 3.0.0 (major)", text)         # مؤجّلة
        self.assertIn('kotlin = "2.0.0"', (d / "gradle/libs.versions.toml").read_text())
        self.assertNotIn("Claude", text)

    def test_clean_project_is_noop(self):
        d = repo({"A.kt": "fun t() = 1\n"})
        body = d / "pr.md"
        auto_maintain.main([str(d), "--body", str(body)], fetch=fetch)
        self.assertFalse(body.exists())

    def test_brain_checkout_dir_is_ignored(self):
        d = repo({"A.kt": "fun t() = 1\n"})
        (d / ".brain").mkdir()
        (d / ".brain/x.txt").write_text("x")
        self.assertEqual(auto_maintain.git_changed(d), [])


if __name__ == "__main__":
    unittest.main()
