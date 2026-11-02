"""Offline tests for pipeline/auto_edit.py rules (synthetic ffmpeg media; no provider calls)."""
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    from . import auto_edit
except ImportError:
    import auto_edit


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


class AutoEditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        # 12 s render with hard cuts at 4 s and 8 s (three flat colours)
        cls.board = root / "board.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=red:s=320x180:r=24:d=4", "-f", "lavfi", "-i", "color=c=green:s=320x180:r=24:d=4",
               "-f", "lavfi", "-i", "color=c=blue:s=320x180:r=24:d=4", "-filter_complex", "[0][1][2]concat=n=3:v=1:a=0[v]",
               "-map", "[v]", "-pix_fmt", "yuv420p", str(cls.board))
        # dialogue render: line spoken 0.5-2.0 s, then EN2 repeats it 2.6-4.1 s; approved line is 1.5 s of speech
        cls.render = root / "dialogue.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=gray:s=320x180:r=24:d=5", "-f", "lavfi",
               "-i", "sine=f=300:d=5,volume='if(between(t,0.5,2.0)+between(t,2.6,4.1),1,0)':eval=frame",
               "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(cls.render))
        cls.approved = root / "approved.mp3"
        ffmpeg("-f", "lavfi", "-i", "sine=f=300:d=1.5", str(cls.approved))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def pace(self, starts, lengths, protect=False, drop=()):
        return auto_edit.pace_narration(starts, lengths, self.board, protect, 2.0, {}, drop)

    def test_short_shot_is_merged_into_a_neighbour_with_footage(self):
        S, L, V, notes = self.pace([0.0, 4.05, 8.05], [3.0, 1.0, 3.0])
        self.assertEqual(len(L), 2)
        self.assertAlmostEqual(sum(L), 7.0, places=6)
        self.assertTrue(all(v >= auto_edit.MIN_SPEED for v in V))
        self.assertIn("dropped", notes[0])

    def test_short_line_plays_as_one_narration_panel_not_the_handoff(self):
        S, L, V, notes = self.pace([0.0, 4.05, 8.05], [1.0, 1.0, 1.0], protect=True)
        self.assertEqual((S, L), ([0.0], [3.0]))
        self.assertIn("narration panel 1", notes[0])

    def test_last_shot_before_dialogue_is_kept(self):
        S, L, V, notes = self.pace([0.0, 4.05, 8.05], [3.5, 3.0, 1.2], protect=True)
        self.assertEqual(len(L), 3)

    def test_flagged_shot_is_dropped_and_its_time_spread(self):
        S, L, V, notes = self.pace([0.0, 4.05, 8.05], [2.5, 3.0, 2.0], protect=True, drop=[3])
        self.assertEqual(len(L), 2)
        self.assertAlmostEqual(sum(L), 7.5, places=6)
        self.assertTrue(any("flagged" in n for n in notes))

    def test_dialogue_keeps_one_spoken_copy_of_the_line(self):
        t0, t1, d, repeat = auto_edit.dialogue_trim(self.render, self.approved)
        self.assertTrue(repeat)
        self.assertAlmostEqual(t0, 0.5 - auto_edit.LEAD, delta=0.15)
        self.assertLess(t1, 2.6)          # the repeat starting at 2.6 s is cut
        self.assertGreater(t1, 2.0)       # the first copy is complete

    def test_push_in_frames_the_speaker_side(self):
        left, right = auto_edit.push_crop("kamala", 1.15), auto_edit.push_crop("ravi", 1.15)
        self.assertIn(":0:", left)
        self.assertNotIn(":0:", right)


if __name__ == "__main__":
    unittest.main()
