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
    {"w": "Hi", "s": 0.2, "e": 0.4},
    {"w": "guys،", "s": 0.4, "e": 0.8},
    {"w": "يعني", "s": 1.0, "e": 1.3},
    {"w": "شاي", "s": 1.4, "e": 1.8},
    {"w": "نار", "s": 4.0, "e": 4.5},
]


def plan(cfg):
    with tempfile.TemporaryDirectory() as td:
        work = pathlib.Path(td) / "work"
        work.mkdir()
        (work / "words.json").write_text(json.dumps(WORDS, ensure_ascii=False), encoding="utf-8")
        return talk.plan({"work": "work", **cfg}, pathlib.Path(td))


class TalkTest(unittest.TestCase):
    def test_auto_keep_cuts_silence_only(self):
        keep = talk.auto_keep(WORDS)
        self.assertEqual(len(keep), 2)
        self.assertTrue(all(talk.retime(w["s"], keep) is not None for w in WORDS))

    def test_verbatim_fillers_stay(self):
        texts = [w["w"] for w in plan({})["words"]]
        self.assertIn("يعني", texts)

    def test_dropping_words_is_refused(self):
        with self.assertRaises(SystemExit):
            plan({"keep": [[3.9, 4.6]]})
        self.assertEqual(len(plan({"keep": [[3.9, 4.6]], "approved_cuts": "ساجد وافق"})["words"]), 1)

    def test_english_never_arabized(self):
        with self.assertRaises(SystemExit):
            plan({"fixes": {"Hi": "هاي"}})
        with self.assertRaises(SystemExit):
            plan({"fixes": {"شاي": "ڤيري"}})

    def test_terminal_hook_rejected(self):
        with self.assertRaises(SystemExit):
            plan({"hook": {"headline": "x"}})

    def test_auto_fx_from_meaning(self):
        kinds = [f["type"] for f in plan({})["fx"]]
        self.assertIn("steam", kinds)
        self.assertIn("fire", kinds)

    def test_arabizi_to_english_script(self):
        self.assertEqual(talk.to_script("فانتاستيك،", {"فانتاستيك": "fantastic"}), "fantastic،")

    def test_example_valid_keys(self):
        ex = json.loads((ROOT / "talk.example.json").read_text(encoding="utf-8"))
        self.assertNotIn("hook", ex)
        for k in ("source", "work", "title"):
            self.assertIn(k, ex)


if __name__ == "__main__":
    unittest.main()
