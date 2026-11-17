import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent / "video-identity"
spec = importlib.util.spec_from_file_location("render", ROOT / "templates" / "render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class VideoIdentityTest(unittest.TestCase):
    def test_tokens_complete(self):
        t = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
        for k in ("bgDark", "bgLight", "ink", "accent", "mute", "line", "numbers", "inkOnLight"):
            self.assertIn(k, t["color"])
        self.assertTrue((ROOT / t["identity"]["portrait"]).is_file())

    def test_icons_have_handles(self):
        icons = json.loads((ROOT / "icons" / "platforms.json").read_text(encoding="utf-8"))["icons"]
        self.assertEqual(len(icons), 6)
        for v in icons.values():
            self.assertTrue(v["handle"] and v["d"])

    def test_example_loads(self):
        brand = render.load_brand(ROOT / "templates" / "content.example.json")
        self.assertTrue(brand["assets"]["portrait"].startswith("file://"))

    def test_fonts_exist(self):
        css = (ROOT / "templates" / "fonts.css").read_text(encoding="utf-8")
        for name in __import__("re").findall(r"url\(fonts/([^)]+)\)", css):
            self.assertTrue((ROOT / "templates" / "fonts" / name).is_file(), name)

    def test_validate_rejects(self):
        with self.assertRaises(SystemExit):
            render.validate({"headline": "x"})
        with self.assertRaises(SystemExit):
            render.validate({"headline": "x", "demo": {"before": {}, "after": {"ratio": 2}, "headline": "", "caption": ""}})


if __name__ == "__main__":
    unittest.main()
