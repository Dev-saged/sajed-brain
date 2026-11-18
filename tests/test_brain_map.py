import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import brain_map  # noqa: E402


class BrainMapTest(unittest.TestCase):
    def test_links_related_broken_orphans(self):
        with tempfile.TemporaryDirectory() as td:
            r = pathlib.Path(td)
            (r / "features").mkdir()
            (r / "README.md").write_text("# الدماغ\nمدخل\n- `features/room.md`\n- `features/missing.md`\n", encoding="utf-8")
            (r / "features" / "room.md").write_text("# قاعدة البيانات\nRoom migrations append only\n## الجداول\n", encoding="utf-8")
            (r / "features" / "sync.md").write_text("# مزامنة\nRoom migrations sync pulse\n", encoding="utf-8")
            info, out_links, in_links, related, broken, orphans = brain_map.build(r)
        self.assertIn("features/room.md", out_links["README.md"])
        self.assertEqual(broken, [("README.md", "features/missing.md")])
        self.assertEqual(orphans, ["features/sync.md"])
        self.assertIn("features/sync.md", related["features/room.md"])
        self.assertEqual(info["features/room.md"][2], ["الجداول"])

    def test_real_brain_has_no_broken_links(self):
        self.assertEqual(brain_map.build()[4], [])


if __name__ == "__main__":
    unittest.main()
