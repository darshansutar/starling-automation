import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from . import locked_workflow as locked_workflow_module
    from .locked_workflow import (
        LOCK_PATH,
        LockedProductionController,
        load_workflow_lock,
        validate_locked_prompt,
    )
    from .runtime import PipelineError, Project
except ImportError:
    import locked_workflow as locked_workflow_module
    from locked_workflow import LOCK_PATH, LockedProductionController, load_workflow_lock, validate_locked_prompt
    from runtime import PipelineError, Project


class LockedWorkflowTests(unittest.TestCase):
    def test_lock_has_non_negotiable_media_contracts(self):
        lock = load_workflow_lock()
        rules = set(lock["hard_rules"])
        self.assertIn("narration_requires_labelled_storyboard_1x2_or_1x3", rules)
        self.assertIn("narration_audio_is_external_and_never_sent_to_en2", rules)
        self.assertIn("dialogue_uses_exactly_one_clean_scene_and_matching_approved_audio", rules)
        self.assertIn("dialogue_camera_is_pixel_locked_for_the_entire_spoken_line", rules)
        self.assertIn("dialogue_camera_motion_or_reframing_is_a_blocking_failure", rules)
        self.assertIn("narration_storyboard_is_the_per_shot_composition_authority", rules)
        self.assertIn("narration_reference_sheets_are_identity_and_material_only_never_scenes", rules)
        self.assertIn("narration_final_shot_must_match_the_final_storyboard_panel", rules)
        self.assertIn("unknown_submission_outcomes_cannot_be_retried", rules)
        self.assertTrue(lock["render_defaults"]["quality"])
        self.assertEqual(lock["render_defaults"]["batch_size"], 10)

    def test_unreviewed_lock_edit_fails_closed(self):
        changed = LOCK_PATH.read_text(encoding="utf-8") + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "workflow_lock.json")
            path.write_text(changed, encoding="utf-8")
            with patch.object(locked_workflow_module, "LOCK_PATH", path):
                with self.assertRaises(PipelineError):
                    load_workflow_lock()

    def test_controller_cannot_override_locked_render_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            Project(tmp, create=True, title="Lock fixture").close()
            controller = LockedProductionController(tmp)
            with self.assertRaises(PipelineError):
                controller.prepare_render(
                    "clip1",
                    {"quality": False, "width": 1344, "height": 768},
                    "narration",
                )
            controller.close()

    def test_dialogue_rejects_prompt_without_static_camera_lock(self):
        payload = {
            "prompt": "subject_definitions:\nx\nsummary:\nx\nretention_analysis:\nx\ndetailed_description:\nx\noverall_soundscape:\nx",
            "duration": 5, "width": 1344, "height": 768, "quality": True,
            "refs": ["scene"], "ref_audios": ["speech"],
        }
        with self.assertRaisesRegex(PipelineError, "static tripod"):
            validate_locked_prompt(payload["prompt"], "dialogue")

    def test_narration_rejects_prompt_without_storyboard_authority(self):
        payload = {
            "prompt": "subject_definitions:\nx\nsummary:\nx\nretention_analysis:\nx\ndetailed_description:\nx\noverall_soundscape:\nx",
            "duration": 8, "width": 1344, "height": 768, "quality": True,
            "refs": ["board"],
        }
        with self.assertRaisesRegex(PipelineError, "per-shot storyboard composition"):
            validate_locked_prompt(payload["prompt"], "narration")


if __name__ == "__main__":
    unittest.main()

