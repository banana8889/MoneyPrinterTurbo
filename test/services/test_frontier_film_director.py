"""Tests for the 2026 character-motion / temporal-story continuity director.

No model checkpoints, video rendering or paid API calls during tests.
"""
import json
import tempfile
import unittest
from pathlib import Path

from studio.frontier_film_director import (
    ENGINE_SOURCES, _unique_seed, compile_film, validate_asset_book,
)
from studio.film_shot_planner import load_script

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "studio" / "season1_episode1_full.json"


class FrontierDirectorTests(unittest.TestCase):
    def setUp(self):
        self.script = load_script(SCRIPT)

    def test_original_episode_is_full_and_contiguous(self):
        f = compile_film({}, self.script)
        self.assertEqual(f["execution"]["count_shots"], 41)
        self.assertEqual(len(f["clips"]), 41)
        self.assertEqual({s["act"] for s in f["clips"]}, set(range(1, 8)))
        self.assertGreater(len(f["segments"]), 60)
        self.assertGreater(f["meta"]["duration_seconds_estimated"], 400)
        self.assertEqual(f["execution"]["rendered_shots"], 0)
        self.assertFalse(f["memory"]["film_ready"])
        self.assertFalse(f["meta"]["commercial_publish_authorized"])

    def test_all_segments_have_unique_seeds_and_valid_five_second_windows(self):
        f = compile_film({}, self.script)
        seeds = [s["seed"] for s in f["segments"]]
        self.assertEqual(len(set(seeds)), len(seeds))
        for s in f["segments"]:
            self.assertGreater(s["end"], s["start"])
            self.assertLessEqual(s["end"] - s["start"], 5.001)
            self.assertFalse(s["render_ready"])
            self.assertIn("luma.licensed_original_reference_and_rig",
                          s["missing_inputs"])
            self.assertIn("local_gpu_inference_capacity", s["missing_inputs"])
            self.assertIn("model_weights_and_upstream_model_licenses_reviewed",
                          s["missing_inputs"])

    def test_every_shot_has_original_identity_refs_and_memory(self):
        film = compile_film({}, self.script)
        self.assertEqual(
            set(film["assets"]["characters"]), {"char_luma", "char_pip"}
        )
        self.assertGreaterEqual(len(film["assets"]["locations"]), 5)
        self.assertEqual(film["memory"]["motion_history_frames"], 5)
        for s in film["segments"]:
            self.assertEqual(
                set(s["character_identity_refs"]), {"char_luma", "char_pip"}
            )
            self.assertIn(s["scenario_ref"], film["assets"]["locations"])
            self.assertTrue(s["seed"])

    def test_every_continuation_links_to_correct_prior_segment(self):
        film = compile_film({}, self.script)
        by_id = {s["id"]: s for s in film["segments"]}
        for shot in film["clips"]:
            self.assertTrue(shot["segments"])
            for i, sid in enumerate(shot["segments"]):
                s = by_id[sid]
                expected = shot["segments"][i-1] if i else None
                self.assertEqual(s["continuation"]["previous_segment"], expected)
                self.assertEqual(
                    s["continuation"]["mode"],
                    "storyboard_keyframe" if i == 0 else "previous_5_motion_frames"
                )

    def test_2026_models_not_auto_run_on_cpu(self):
        f = compile_film({}, self.script, gpu_count=0, vram_gb=0)
        self.assertFalse(f["execution"]["monetary_actions_permitted"])
        self.assertEqual(f["execution"]["state"], "BLOCKED_PREPRODUCTION")
        self.assertEqual(f["execution"]["verified_running_engines"], [])
        self.assertIn("wan_animate_2", ENGINE_SOURCES)
        self.assertIn("scail2", ENGINE_SOURCES)
        self.assertIn("svi_wan22", ENGINE_SOURCES)

    def test_no_external_paid_llm_api_even_with_other_assets(self):
        with self.assertRaises(PermissionError):
            validate_asset_book({"endpoints": ["https://api.openai.com/v1"]})
        with self.assertRaises(PermissionError):
            validate_asset_book({"endpoints": ["https://api.fal.ai"]})
        self.assertEqual(
            validate_asset_book({"endpoints": ["http://127.0.0.1:8000"]})
            ["endpoints"][0],
            "http://127.0.0.1:8000",
        )

    def test_unlicensed_character_assets_are_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            image = Path(d, "luma.png")
            rig = Path(d, "luma.blend")
            image.write_bytes(b"fake image placeholder")  # only rights check
            rig.write_bytes(b"fake rig placeholder")
            with self.assertRaises(PermissionError):
                validate_asset_book({
                    "characters": {
                        "luma": {
                            "reference_image": str(image), "rig_scene": str(rig),
                            "owner_rights_confirmed": False
                        }
                    }
                })

    def test_invalid_hardware_is_rejected(self):
        for value in (-1, float("nan"), 500):
            with self.assertRaises(ValueError):
                compile_film({}, self.script, vram_gb=value)
        with self.assertRaises(ValueError):
            compile_film({}, self.script, gpu_count=-1)

    def test_no_reuse_of_original_copyrighted_cartoon_names(self):
        f = compile_film({}, self.script)
        characters = str(f["assets"]["characters"]).lower()
        self.assertNotIn("tom and jerry", characters)
        self.assertNotIn("harry potter", characters)

    def test_seeds_are_deterministic_for_restarts(self):
        self.assertEqual(_unique_seed(1, 1, 0), _unique_seed(1, 1, 0))
        self.assertNotEqual(_unique_seed(1, 1, 0), _unique_seed(1, 1, 1))


if __name__ == "__main__":
    unittest.main()
