import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent / "video-identity" / "talk"
spec = importlib.util.spec_from_file_location("talk", ROOT / "talk.py")
talk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(talk)

WORDS = [
    {"w": "أهلاً", "s": 0.5, "e": 0.9},
    {"w": "يعني", "s": 1.0, "e": 1.3},
    {"w": "اليوم", "s": 1.4, "e": 1.8},
    {"w": "تطبيق", "s": 4.0, "e": 4.5},
]


class TalkTest(unittest.TestCase):
    def test_auto_keep_drops_silence_and_fillers(self):
        keep = talk.auto_keep(WORDS)
        self.assertEqual(len(keep), 2)
        self.assertAlmostEqual(keep[1][0], 3.88)

    def test_retime(self):
        keep = [[0.0, 2.0], [4.0, 5.0]]
        self.assertEqual(talk.retime(4.5, keep), 2.5)
        self.assertIsNone(talk.retime(3.0, keep))

    def test_plan_applies_fixes_and_removes_fillers(self):
        with tempfile.TemporaryDirectory() as td:
            work = pathlib.Path(td) / "work"
            work.mkdir()
            (work / "words.json").write_text(json.dumps(WORDS, ensure_ascii=False), encoding="utf-8")
            p = talk.plan({"work": "work", "fixes": {"اليوم": "النهارده"}, "pops": [{"at": 4.2, "text": "x"}]}, pathlib.Path(td))
        texts = [w["w"] for w in p["words"]]
        self.assertNotIn("يعني", texts)
        self.assertIn("النهارده", texts)
        self.assertEqual(len(p["pops"]), 1)
        self.assertGreater(p["duration"], 0)

    def test_example_has_required_keys(self):
        ex = json.loads((ROOT / "talk.example.json").read_text(encoding="utf-8"))
        for k in ("source", "work", "hook"):
            self.assertIn(k, ex)


if __name__ == "__main__":
    unittest.main()
