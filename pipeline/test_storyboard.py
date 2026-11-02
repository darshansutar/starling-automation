"""Offline tests for the fixed-format storyboard compositor and image checks."""
import contextlib
import io
import json
import random
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

import storyboard
from storyboard import StoryboardError, check_image, compose, verify_board


def noisy(path, size, seed=1):
    rnd = random.Random(seed)
    w, h = size
    im = Image.new("RGB", size)
    im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)) for _ in range(w * h)])
    im.save(path)
    return path


@unittest.skipIf(Image is None, "Pillow is not installed")
class StoryboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for n in (1, 2, 3):
            noisy(self.root / f"shot{n}.png", (1536, 1024), seed=n)

    def tearDown(self):
        self.temp.cleanup()

    def spec(self, **changes):
        spec = {"out": "board.png", "shots": [
            {"shot": 1, "image": "shot1.png", "start": 0.0, "end": 4.0, "camera": "slow push in", "action": "Savitribai waits"},
            {"shot": 2, "image": "shot2.png", "start": 4.0, "end": 8.0, "camera": "static", "action": "Sarah approaches"},
            {"shot": 3, "image": "shot3.png", "start": 8.0, "end": 12.0, "camera": "static", "action": "They face each other"},
        ]}
        spec.update(changes)
        return spec

    def test_compose_produces_fixed_layout_and_passes_verification(self):
        record = compose(self.spec(), self.root)
        board = self.root / "board.png"
        with Image.open(board) as im:
            self.assertEqual(im.size, (1024, 1536))
            self.assertEqual(im.getpixel((5, 466)), storyboard.IVORY)
            self.assertEqual(im.getpixel((5, 1534)), storyboard.IVORY)
        self.assertEqual([b["picture"] for b in record["boxes"]],
                         [[0, 0, 1024, 464], [0, 512, 1024, 976], [0, 1024, 1024, 1488]])
        self.assertEqual(record["cut_times"], [4.0, 8.0])
        self.assertEqual(record["captions"][0], "SHOT 1  |  0.00-4.00 s  |  SLOW PUSH IN  |  SAVITRIBAI WAITS")
        self.assertEqual(record["caption_font_px"], [24, 24, 24])
        self.assertTrue((self.root / "board.layout.json").is_file())
        self.assertTrue(verify_board(board)["verified"])

    def test_spec_rules(self):
        four = self.spec(); four["shots"] = four["shots"] + [dict(four["shots"][2], shot=4, start=12.0, end=14.0)]
        two_short = self.spec(); two_short["shots"] = two_short["shots"][:2]; two_short["shots"][1]["end"] = 5.0
        gap = self.spec(); gap["shots"][1]["start"] = 4.5
        short = self.spec(); short["shots"][2]["end"] = 9.0
        long = self.spec(); long["shots"][2]["end"] = 15.5
        long_caption = self.spec(); long_caption["shots"][0]["action"] = "word " * 60
        for name, spec, message in (("four shots", four, "1, 2 or 3"), ("two short", two_short, "6-15"), ("gap", gap, "exactly where"),
                                    ("short", short, "10-15"), ("long", long, "10-15"),
                                    ("caption", long_caption, "too long")):
            with self.subTest(name), self.assertRaisesRegex(StoryboardError, message):
                compose(spec, self.root)

    def test_undersized_source_is_rejected_not_upscaled(self):
        noisy(self.root / "small.png", (800, 450))
        spec = self.spec(); spec["shots"][0]["image"] = "small.png"
        with self.assertRaisesRegex(StoryboardError, "at least 1024"):
            compose(spec, self.root)

    def test_damaged_images_are_rejected(self):
        whole = (self.root / "shot1.png").read_bytes()
        (self.root / "truncated.png").write_bytes(whole[: len(whole) // 2])
        with self.assertRaisesRegex(StoryboardError, "truncated"):
            check_image(self.root / "truncated.png")
        half = Image.open(self.root / "shot1.png").copy()
        half.paste((128, 128, 128), (0, 600, 1536, 1024))  # grey lower part, as in a half-loaded image
        half.save(self.root / "half.png")
        with self.assertRaisesRegex(StoryboardError, "half-loaded"):
            check_image(self.root / "half.png")
        Image.new("RGB", (1536, 1024), (120, 120, 120)).save(self.root / "blank.png")
        with self.assertRaises(StoryboardError):
            check_image(self.root / "blank.png")

    def test_verify_rejects_drawn_board_with_wrong_strips(self):
        noisy(self.root / "drawn.png", (1024, 1536), seed=9)
        with self.assertRaisesRegex(StoryboardError, "ivory"):
            verify_board(self.root / "drawn.png")

    def test_cli_reports_errors_as_json(self):
        spec = self.spec(); spec["shots"] = spec["shots"][:2]; spec["shots"][1]["end"] = 5.0
        path = self.root / "spec.json"; path.write_text(json.dumps(spec), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(storyboard.main(["compose", str(path)]), 1)
        self.assertIn("6-15", out.getvalue())

    def test_one_and_two_shot_boards(self):
        two = self.spec(); two["shots"] = two["shots"][:2]
        record = compose(two, self.root)
        self.assertEqual(record["format"], "storyboard_1x2_fixed")
        self.assertEqual((record["width"], record["height"]), (1024, 1024))
        self.assertEqual(record["cut_times"], [4.0])
        self.assertEqual(verify_board(self.root / "board.png")["shot_count"], 2)
        one = self.spec(out="one.png"); one["shots"] = [dict(one["shots"][0], end=5.0)]
        record = compose(one, self.root)
        self.assertEqual((record["format"], record["height"], record["cut_times"]), ("storyboard_1x1_fixed", 512, []))
        self.assertTrue(verify_board(self.root / "one.png")["verified"])


if __name__ == "__main__":
    unittest.main()
