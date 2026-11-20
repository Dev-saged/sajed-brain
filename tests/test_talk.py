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

    def test_timeline_rejects_cut_time_and_unknown_type(self):
        with self.assertRaises(SystemExit):
            plan({"keep": [[0.0, 2.0], [3.9, 4.6]], "approved_cuts": "ok", "cards": [{"at": 3.0, "type": "typo", "text": "x"}]})
        with self.assertRaises(SystemExit):
            plan({"cards": [{"at": 1.5, "type": "video", "text": "x"}]})
        p = plan({"cards": [{"at": 1.5, "type": "icon", "icon": "heart", "text": "قلب"}], "frames": [{"from": 0.2, "to": 1.8, "title": "t"}]})
        self.assertEqual(len(p["cards"]), 1)
        self.assertEqual(len(p["frames"]), 1)

    def test_sfx_from_library_with_sync(self):
        p = plan({"cards": [{"at": 1.5, "type": "typo", "text": "x"}], "frames": [{"from": 0.2, "to": 1.8, "title": "t"}]})
        ev = talk.compose.sfx_events(p, {})
        self.assertEqual(len(ev), 2)
        for start, path, _ in ev:
            self.assertTrue(path.is_file())
            self.assertGreaterEqual(start, 0)
        self.assertEqual(talk.compose.sfx_events(p, {"sfx": False}), [])
        cat = talk.compose.sfx_catalog()
        self.assertTrue(set(talk.compose.SFX_FOR.values()) <= set(cat))

    def test_icons_resolve_from_arabic(self):
        self.assertEqual(talk.compose.resolve_icon("كاسة شاي").stem, "coffee")
        self.assertEqual(talk.compose.resolve_icon("قلب", "fill").parent.name, "fill")
        p = plan({"cards": [{"at": 1.5, "type": "prop", "icon": "قلب"}]})
        self.assertIn("<svg", p["cards"][0]["svg"])
        with self.assertRaises(SystemExit):
            plan({"cards": [{"at": 1.5, "type": "icon", "icon": "قلب", "style": "3d"}]})

    def test_mood_from_content(self):
        self.assertEqual(talk.compose.detect_mood([{"w": "مطر"}, {"w": "شاي"}]), "cozy")
        self.assertEqual(talk.compose.detect_mood([{"w": "x"}]), "tech")
        for m in talk.compose.MOODS.values():
            self.assertEqual(len(m["bg"]), 2)

    def test_example_valid_keys(self):
        ex = json.loads((ROOT / "talk.example.json").read_text(encoding="utf-8"))
        self.assertNotIn("hook", ex)
        for k in ("source", "work", "cover"):
            self.assertIn(k, ex)


if __name__ == "__main__":
    unittest.main()
