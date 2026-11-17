import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import kit  # noqa: E402
from scoutlib import cli  # noqa: E402

MONEY = '''package com.{p}.util

import java.text.DecimalFormat
import kotlin.math.abs

fun formatMoney(minor: Long, symbol: String): String {{
    val fmt = DecimalFormat("#,##0.00")
    val sign = if (minor < 0) "-" else ""
    val major = abs(minor) / 100.0
    return sign + fmt.format(major) + " " + symbol
}}

fun usesProject(x: Long): String {{
    val fmt = DecimalFormat("#,##0.00")
    val sign = if (x < 0) "-" else ""
    return sign + fmt.format(abs(x)) + formatMoney(x, "ر") + helperOnlyHere(x)
}}

private fun helperOnlyHere(x: Long) = x.toString()

@Deprecated("x")
fun annotatedFun(minor: Long, symbol: String): String {{
    val fmt = DecimalFormat("#,##0.00")
    val sign = if (minor < 0) "-" else ""
    val major = abs(minor) / 100.0
    return sign + fmt.format(major) + " " + symbol
}}
'''
ANDROID = '''package com.{p}.util

import android.content.Context

fun shared(ctx: Context, a: Int): String {{
    val first = ctx.getString(a)
    val second = ctx.getString(a + 1)
    val third = ctx.getString(a + 2)
    return first + second + third + "نهاية"
}}
'''
CALLER_SAME = "package com.{p}.util\n\nfun show() = formatMoney(5, \"ر\")\n"
CALLER_OTHER = "package com.{p}.ui\n\nimport com.{p}.util.formatMoney\nimport java.util.Date\n\nfun row() = formatMoney(1, \"ر\")\n"


def make_project(base, name):
    d = base / name
    files = {
        "app/src/main/java/util/Money.kt": MONEY.format(p=name),
        "app/src/main/java/util/Ctx.kt": ANDROID.format(p=name),
        "app/src/main/java/util/Show.kt": CALLER_SAME.format(p=name),
        "app/src/main/java/ui/Row.kt": CALLER_OTHER.format(p=name),
        "gradle/libs.versions.toml": '[versions]\nkotlin = "2.1.0"\n\n[libraries]\nx = { module = "a:b", version = "1" }\n',
        "app/build.gradle.kts": "plugins {}\n\ndependencies {\n    implementation(libs.x)\n}\n",
    }
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return d


class KitTests(unittest.TestCase):
    def setUp(self):
        self.base = pathlib.Path(tempfile.mkdtemp())
        self.projects = self.base / "projects"
        self.index = self.base / "index"
        for name in ("qayd", "barq"):
            d = make_project(self.projects, name)
            cli.run([str(d), "--out", str(self.index / name)])
        self.out = self.base / "sajed-kit"
        self.manifest, self.skipped = kit.extract(self.index, self.projects, self.out)

    def test_extract_is_conservative(self):
        self.assertEqual([m["name"] for m in self.manifest], ["formatMoney"])
        reasons = dict(self.skipped)
        self.assertIn("android.content.Context", reasons["shared"])      # import غير مسموح
        self.assertNotIn("usesProject", {m["name"] for m in self.manifest})

    def test_android_and_dependent_functions_not_extracted(self):
        text = "\n".join(p.read_text(encoding="utf-8") for p in (self.out / "src/main/kotlin/dev/saged/kit").glob("*.kt"))
        self.assertIn("fun formatMoney(", text)
        self.assertNotIn("android", text)
        self.assertNotIn("usesProject", text)
        self.assertNotIn("helperOnlyHere", text)
        self.assertIn("package dev.saged.kit", text)
        self.assertIn("import java.text.DecimalFormat", text)
        self.assertIn("import kotlin.math.abs", text)

    def test_module_files(self):
        for rel in ("settings.gradle.kts", "build.gradle.kts", "VERSION", "README.md", "kit-manifest.json",
                    ".github/workflows/publish.yml"):
            self.assertTrue((self.out / rel).exists(), rel)
        m = json.loads((self.out / "kit-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({o["project"] for o in m[0]["origins"]}, {"qayd", "barq"})

    def test_adopt_rewrites_project(self):
        d = self.projects / "qayd"
        r = kit.adopt(d, self.out / "kit-manifest.json", "0.1.0", d / "pr.md")
        self.assertEqual(r["removed"], ["formatMoney"])
        money = (d / "app/src/main/java/util/Money.kt").read_text(encoding="utf-8")
        self.assertNotIn("fun formatMoney", money)
        self.assertIn("fun usesProject", money)                       # بقية الملف سليمة
        self.assertIn("import dev.saged.kit.formatMoney", money)      # استدعاء داخلي في نفس الملف
        show = (d / "app/src/main/java/util/Show.kt").read_text(encoding="utf-8")
        self.assertIn("import dev.saged.kit.formatMoney", show)       # نفس الـpackage
        row = (d / "app/src/main/java/ui/Row.kt").read_text(encoding="utf-8")
        self.assertIn("import dev.saged.kit.formatMoney", row)
        self.assertNotIn("com.qayd.util.formatMoney", row)
        self.assertNotIn("import java.util.Date", row)     # unused في ملف مُعدَّل ← يُنظَّف (T0)
        toml = (d / "gradle/libs.versions.toml").read_text(encoding="utf-8")
        self.assertIn('sajed-kit = "0.1.0"', toml)
        self.assertIn('module = "dev.saged:kit"', toml)
        self.assertIn("implementation(libs.sajed.kit)", (d / "app/build.gradle.kts").read_text(encoding="utf-8"))
        self.assertIn("خطوات يدوية", (d / "pr.md").read_text(encoding="utf-8"))

    def test_adopt_is_idempotent(self):
        d = self.projects / "barq"
        kit.adopt(d, self.out / "kit-manifest.json", "0.1.0")
        again = kit.adopt(d, self.out / "kit-manifest.json", "0.1.0")
        self.assertEqual(again["removed"], [])
        self.assertEqual((d / "app/build.gradle.kts").read_text(encoding="utf-8").count("libs.sajed.kit"), 1)

    def test_file_deleted_when_only_function_removed(self):
        d = self.base / "solo"
        (d / "src").mkdir(parents=True)
        (d / "src/Only.kt").write_text(
            "package com.solo\n\nimport java.text.DecimalFormat\nimport kotlin.math.abs\n\n" + MONEY.split("fun usesProject")[0].split("abs\n\n", 1)[1].format(), encoding="utf-8")
        manifest = self.base / "m.json"
        manifest.write_text(self.out.joinpath("kit-manifest.json").read_text(encoding="utf-8"))
        kit.adopt(d, manifest, "0.1.0")
        self.assertFalse((d / "src/Only.kt").exists())


class GradleCompileTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gradle") and shutil.which("java"), "gradle/java غير متاحين")
    def test_generated_module_compiles(self):
        base = pathlib.Path(tempfile.mkdtemp())
        for name in ("qayd", "barq"):
            d = make_project(base / "projects", name)
            cli.run([str(d), "--out", str(base / "index" / name)])
        out = base / "kit"
        kit.extract(base / "index", base / "projects", out)
        r = subprocess.run(["gradle", "build", "-q", "--no-daemon"], cwd=out, capture_output=True, text=True, timeout=600)
        if "Could not resolve" in r.stderr or "UnknownHost" in r.stderr or "timed out" in r.stderr:
            self.skipTest("لا وصول لشبكة Gradle: " + r.stderr[:120])
        self.assertEqual(r.returncode, 0, r.stderr[-800:])


if __name__ == "__main__":
    unittest.main()
