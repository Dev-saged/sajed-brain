import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "import_chats.py"


class ImportChatsTest(unittest.TestCase):
    def test_import_masks_secrets_and_dedupes(self):
        conv = [{"uuid": "c1", "name": "تجربة", "created_at": "2026-11-20T10:00:00Z", "chat_messages": [
            {"sender": "human", "text": "مفتاحي ghp_abcdefghijklmnop123"}, {"sender": "assistant", "text": "تم"}]}]
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "scripts").mkdir()
            (root / "scripts" / "import_chats.py").write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
            src = root / "conversations.json"
            src.write_text(json.dumps(conv, ensure_ascii=False), encoding="utf-8")
            for _ in range(2):
                subprocess.run([sys.executable, str(root / "scripts" / "import_chats.py"), str(src)], check=True, capture_output=True)
            files = [f for f in (root / "chats").rglob("*.md") if f.name != "index.md"]
            self.assertEqual(len(files), 1)
            text = files[0].read_text(encoding="utf-8")
            self.assertNotIn("ghp_", text)
            self.assertIn("[محجوب]", text)


if __name__ == "__main__":
    unittest.main()
