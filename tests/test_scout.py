import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scoutlib import cli, findings as F, symbols  # noqa: E402
from scoutlib.lexer import lex  # noqa: E402

LEDGER = '''package com.qayd.debts

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.material.icons.Icons
import kotlin.collections.List
import com.qayd.util.Money as M
import android.util.Log

private const val UNUSED_LIMIT = 40

data class Debt(val id: Long, val amount: Long)

class DebtRepository {
    private val cache = mutableMapOf<Long, Debt>()
    private fun neverCalled(x: Int): Int {
        return x * 2
    }
    fun total(debts: List<Debt>): Long {
        var sum = 0L
        for (d in debts) {
            sum += d.amount
        }
        val label = "رصيد الديون الكلي"
        println(label)
        return sum
    }
    fun totalCopy(debts: List<Debt>): Long {
        var sum = 0L
        for (d in debts) {
            sum += d.amount
        }
        val label = "رصيد الديون الكلي"
        println(label)
        return sum
    }
    fun load(id: Long): Debt? {
        try {
            return cache[id]
        } catch (e: Exception) {
        }
        return null
    }
}

@Composable
fun DebtScreen(repo: DebtRepository) {
    var count by remember { mutableStateOf(0) }
    val color = Color(0xFF112233)
    // TODO اربط الشاشة
    Text("رصيد الديون الكلي $count")
    Text("رصيد الديون الكلي")
}

@Preview
@Composable
fun DebtScreenPreview() {}
'''


def project(files):
    d = pathlib.Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


def scan(d, *extra):
    out = d / "docs"
    code = cli.run([str(d), "--out", str(out), *extra])
    data = json.loads((out / "scout.json").read_text(encoding="utf-8"))
    return code, data["findings"], out


class LexerTests(unittest.TestCase):
    def test_comments_and_strings_blanked_lines_kept(self):
        lx = lex('val a = "x // not comment" // real\n/* multi\nline */ val b = 1\n')
        self.assertNotIn("real", lx.code)
        self.assertNotIn("multi", lx.code)
        self.assertEqual(lx.code.count("\n"), 3)
        self.assertEqual(lx.strings[0][1], "x // not comment")

    def test_templates_collected(self):
        self.assertEqual(lex('val s = "a $x ${y.z}"').templates, ["x", "y"])


class SymbolTests(unittest.TestCase):
    def test_members_only_and_scope(self):
        syms = symbols.extract("A.kt", lex(LEDGER))
        names = {s.name: s for s in syms}
        self.assertIn("DebtRepository", names)
        self.assertIn("neverCalled", names)
        self.assertEqual(names["neverCalled"].vis, "private")
        self.assertNotIn("sum", names)       # محلي داخل دالة
        self.assertNotIn("label", names)
        self.assertEqual(names["DebtScreenPreview"].annos, ("Preview", "Composable"))

    def test_constructor_params_not_symbols(self):
        syms = symbols.extract("A.kt", lex("class A(\n    val x: Int,\n    val y: Int,\n) {\n    val z = 1\n}\n"))
        self.assertEqual({s.name for s in syms}, {"A", "z"})


class RegressionTests(unittest.TestCase):
    def test_companion_members_indexed(self):
        syms = symbols.extract("V.kt", lex("class V {\n    companion object {\n        const val TAG = \"v\"\n    }\n}\n"))
        self.assertIn("TAG", {s.name for s in syms})

    def test_report_groups_by_tier(self):
        d = project({"V.kt": "class Vault {\n    private val gone = 1\n    fun pub() {}\n}\n"})
        _, found, out = scan(d)
        report = (out / "scout-report.md").read_text(encoding="utf-8")
        self.assertIn("## dead-symbol (1) — T0", report)
        self.assertIn("— T2", report)
        self.assertEqual(sorted(f["tier"] for f in found if f["rule"] == "dead-symbol"), ["T0", "T2", "T2"])


class ScoutTests(unittest.TestCase):
    def setUp(self):
        self.d = project({"app/src/main/java/com/qayd/Ledger.kt": LEDGER,
                          "app/src/main/AndroidManifest.xml": '<application android:allowBackup="true" />'})
        self.code, self.found, self.out = scan(self.d)
        self.rules = {f["rule"] for f in self.found}

    def test_dead_private_symbols(self):
        dead = {f["text"] for f in self.found if f["rule"] == "dead-symbol"}
        self.assertIn("neverCalled", dead)
        self.assertIn("UNUSED_LIMIT", dead)
        self.assertNotIn("DebtScreenPreview", dead)     # Preview مستثنى
        self.assertNotIn("DebtRepository", dead)

    def test_unused_imports_but_not_delegates(self):
        imps = {f["text"] for f in self.found if f["rule"] == "unused-import"}
        self.assertIn("import android.util.Log", imps)
        self.assertIn("import com.qayd.util.Money as M", imps)
        self.assertNotIn("import androidx.compose.runtime.getValue", imps)
        self.assertNotIn("import androidx.compose.runtime.mutableStateOf", imps)

    def test_guards(self):
        for rule in ("swallowed-exception", "hex-color-outside-brand", "todo-left", "debug-output",
                     "icon-pack", "allow-backup"):
            self.assertIn(rule, self.rules, rule)

    def test_duplicates(self):
        self.assertIn("dup-body", self.rules)
        self.assertIn("dup-string", self.rules)

    def test_outputs(self):
        tsv = (self.out / "symbol-index.tsv").read_text(encoding="utf-8")
        self.assertIn("DebtRepository\tclass\tpublic\tapp/src/main/java/com/qayd/Ledger.kt:", tsv)
        self.assertTrue((self.out / "scout-report.md").exists())
        self.assertTrue((self.out / "scout-history.tsv").exists())
        self.assertEqual(self.code, 0)


class SecretsAndGateTests(unittest.TestCase):
    def test_secret_masked_and_gate_fails(self):
        key = "AIza" + "A" * 35
        d = project({"A.kt": f'val k = "{key}"\n'})
        code, found, out = scan(d, "--fail-on", "error")
        self.assertEqual(code, 1)
        hit = [f for f in found if f["rule"] == "secret-key"]
        self.assertTrue(hit)
        self.assertEqual(hit[0]["text"], "***")
        self.assertNotIn(key, (out / "scout-report.md").read_text(encoding="utf-8"))
        self.assertNotIn(key, (out / "scout.json").read_text(encoding="utf-8"))

    def test_material_you_guard_respects_optin(self):
        bad = project({"Theme.kt": "val s = dynamicLightColorScheme(ctx)\n"})
        ok = project({"Theme.kt": "val s = if (BrandConfig.dynamicColor) dynamicLightColorScheme(ctx) else brand\n"})
        self.assertIn("material-you-default", {f["rule"] for f in scan(bad)[1]})
        self.assertNotIn("material-you-default", {f["rule"] for f in scan(ok)[1]})

    def test_apply_imports_rewrites_only_unused(self):
        d = project({"A.kt": "import a.b.Used\nimport a.b.Gone\nfun x() = Used()\n"})
        cli.run([str(d), "--apply-imports", "--no-write"])
        text = (d / "A.kt").read_text(encoding="utf-8")
        self.assertIn("import a.b.Used", text)
        self.assertNotIn("Gone", text)


class MigrationGuardTests(unittest.TestCase):
    def test_edited_migration_is_error(self):
        d = project({"db/Migration1_2.kt": "val a = 1\n", "Other.kt": "val b = 1\n"})
        run = lambda *c: subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *c], cwd=d,
                                        check=True, capture_output=True)
        run("init", "-q")
        run("add", "-A")
        run("commit", "-qm", "base")
        (d / "db/Migration1_2.kt").write_text("val a = 2\n")
        (d / "Other.kt").write_text("val b = 2\n")
        _, found, _ = scan(d, "--base", "HEAD")
        edited = [f for f in found if f["rule"] == "migration-edited"]
        self.assertEqual([f["path"] for f in edited], ["db/Migration1_2.kt"])


class WhereTests(unittest.TestCase):
    def test_where_lists_decl_and_refs(self):
        d = project({"A.kt": "fun helper() = 1\n", "B.kt": "fun use() = helper()\n"})
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cli.run([str(d), "--where", "helper"])
        self.assertIn("decl  fun public A.kt:1", buf.getvalue())
        self.assertIn("ref   B.kt x1", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
