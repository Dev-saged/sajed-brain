import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import motion_refs  # noqa: E402


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg غير مثبت")
class MotionRefsTest(unittest.TestCase):
    def test_analyze_writes_sheet_metrics_and_pending_note(self):
        with tempfile.TemporaryDirectory() as td:
            td = pathlib.Path(td)
            clip = td / "clip.mp4"
            # مشهدان مختلفا اللون = قطع واحد
            subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=red:s=360x640:d=2",
                            "-f", "lavfi", "-i", "color=c=blue:s=360x640:d=2", "-filter_complex", "[0][1]concat=n=2",
                            "-pix_fmt", "yuv420p", str(clip)], check=True)
            old = motion_refs.MOTION
            motion_refs.MOTION = td / "motion"
            try:
                d = motion_refs.analyze(clip, "t-clip")
                self.assertTrue((td / "motion" / "refs" / "t-clip" / "sheet.jpg").is_file())
            finally:
                motion_refs.MOTION = old
        self.assertEqual(len(d["cuts"]), 1)
        self.assertEqual(d["motion"], "ثابت")
        self.assertIn(motion_refs.PENDING, motion_refs.note_line(d))

    def test_sample_times_cover_shots(self):
        t = motion_refs.sample_times(10, [2, 5], n=12)
        self.assertEqual(len(t), 12)
        self.assertTrue(all(0 < x < 10 for x in t))

    def test_drive_link_id(self):
        m = motion_refs.DRIVE.search("https://drive.google.com/file/d/1hBGFlOEqEIahDshKqLKXngQTTvWNTC_h/view")
        self.assertEqual(m.group(1), "1hBGFlOEqEIahDshKqLKXngQTTvWNTC_h")


if __name__ == "__main__":
    unittest.main()
