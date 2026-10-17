"""Checks for the standalone original educational shorts worker."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import kids_autonomy as mod


class KidsAutonomyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state_path = Path(self.temp.name) / "state.json"

    def test_initial_plan_does_not_claim_observed_success(self):
        state = mod.load(self.state_path)
        self.assertEqual(len(mod.ranked(state)), 8)
        self.assertTrue(all(row["evidence_score"] is None for row in mod.ranked(state)))
        self.assertTrue(all(row["views"] == 0 for row in mod.ranked(state)))

    def test_cumulative_feedback_reorders_similar_topics(self):
        state = mod.load(self.state_path)
        state["items"]["color-mixing"]["status"] = "created"
        mod.save(self.state_path, state)
        mod.feedback("color-mixing", self.state_path, 1000, 950, 120)
        after = mod.ranked(mod.load(self.state_path))
        self.assertEqual(after[0]["id"], "rain-journey")
        with self.assertRaisesRegex(ValueError, "cumulative"):
            mod.feedback("color-mixing", self.state_path, 10, 9, 5)

    def test_no_analytics_for_uncreated_video(self):
        with self.assertRaisesRegex(ValueError, "created"):
            mod.feedback("shape-mystery", self.state_path, 100, 50, 8)

    def test_invalid_metrics_are_rejected(self):
        state = mod.load(self.state_path)
        state["items"]["shape-mystery"]["status"] = "created"
        mod.save(self.state_path, state)
        with self.assertRaisesRegex(ValueError, "Invalid analytics"):
            mod.feedback("shape-mystery", self.state_path, 10, 11, 0)

    def test_atomic_state_survives_reloading(self):
        state = mod.load(self.state_path)
        mod.save(self.state_path, state)
        self.assertEqual(mod.load(self.state_path)["version"], 1)
        self.assertEqual(len(mod.load(self.state_path)["items"]), 8)

    def test_produce_disables_upload_before_cli_and_blocks_duplicates(self):
        class ProcessResult:
            returncode = 0
            stderr = ""
            stdout = ""
        video = Path(self.temp.name) / "video.mp4"
        video.write_bytes(b"file")
        output = {"task_id": "abcd", "result": {"videos": [str(video)]}}
        response = ProcessResult()
        response.stdout = json.dumps(output) + "\n"
        with patch.object(mod, "draw_cards", return_value=[Path(self.temp.name) / "frame.png"]):
            with patch.object(mod.subprocess, "run", return_value=response) as run:
                result = mod.produce("shape-mystery", self.state_path)
        self.assertFalse(result["published"])
        command = run.call_args.args[0]
        self.assertIn('config.app["upload_post_auto_upload"]=False', command[2])
        self.assertIn("--video-source", command)
        self.assertIn("local", command)
        self.assertIn("--video-script", command)
        self.assertNotIn("--confirm-wavespeed-charge", command)
        self.assertEqual(mod.load(self.state_path)["items"]["shape-mystery"]["status"], "created")
        with self.assertRaisesRegex(ValueError, "already"):
            mod.produce("shape-mystery", self.state_path)

    def test_failed_render_records_failure_not_success(self):
        class ProcessResult:
            returncode = 1
            stderr = "not enough media"
            stdout = ""
        with patch.object(mod, "draw_cards", return_value=[Path(self.temp.name) / "frame.png"]):
            with patch.object(mod.subprocess, "run", return_value=ProcessResult()):
                with self.assertRaisesRegex(RuntimeError, "Video pipeline failed"):
                    mod.produce("shape-mystery", self.state_path)
        item = mod.load(self.state_path)["items"]["shape-mystery"]
        self.assertEqual(item["status"], "failed")
        self.assertEqual(item["video_paths"], [])


if __name__ == "__main__":
    unittest.main()
