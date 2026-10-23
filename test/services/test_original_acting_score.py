"""Integrity tests for exact original 84-line, 5m51s two-actor performance."""
import json
import tempfile
import unittest
from pathlib import Path

from studio.episode1_acting_score import build,story
from studio.episode1_measured_voice_timing import VERIFIED_TOTAL

SRC=Path(__file__).resolve().parents[2]/"studio"/"season1_episode1_full.json"


class OriginalActingScoreTests(unittest.TestCase):
    def test_full_measured_dialogue_not_fabricated(self):
        score=build(story(SRC))
        self.assertEqual(score["dialogue_lines"],84)
        self.assertAlmostEqual(score["measured_timeline_seconds"],VERIFIED_TOTAL,places=4)
        self.assertEqual(score["act_count"],7)
        self.assertFalse(score["voice_acting_human_approved"])
        self.assertFalse(score["film_ready"])

    def test_both_independently_acting_casts_each_receive_all_84_beats(self):
        score=build(story(SRC))
        for actor in ("luma","pip"):
            clips=score["actor_controls"][actor]
            self.assertEqual(len(clips),84)
            self.assertEqual([x["line_number"] for x in clips],list(range(1,85)))
            self.assertEqual({x["act"] for x in clips},set(range(1,8)))
            self.assertTrue(all(x["bone_pose"] and x["face_pose"] for x in clips))
            self.assertGreaterEqual(sum(x["mode"]=="speak" for x in clips),10)
            self.assertGreaterEqual(sum(x["mode"]=="listen" for x in clips),10)
            self.assertGreaterEqual(sum(x["mode"]=="narrated" for x in clips),10)

    def test_genuine_listener_reaction_not_freezing(self):
        score=build(story(SRC))
        for idx,(a,b) in enumerate(zip(score["actor_controls"]["luma"],
                                       score["actor_controls"]["pip"])):
            self.assertEqual(a["line_number"],b["line_number"])
            self.assertEqual(a["start"],b["start"])
            self.assertEqual(a["end"],b["end"])
            if a["mode"]=="speak":
                self.assertEqual(b["mode"],"listen")
                self.assertGreaterEqual(b["face_pose"]["BrowsUp"],0)
                self.assertNotEqual(a["look_at"],b["look_at"])
            if b["mode"]=="speak":
                self.assertEqual(a["mode"],"listen")

    def test_mouth_cannot_claim_real_lipsync_without_cues(self):
        s=build(story(SRC))
        self.assertFalse(s["phonemes_from_original_recording"])
        self.assertEqual(s["scene_renders"],0)
        for actor in ("luma","pip"):
            for beat in s["actor_controls"][actor]:
                self.assertEqual(beat["mouth_pose"],
                                 "AWAITING_REAL_PHONEMES" if beat["mode"]=="speak" else "CLOSED")

    def test_story_motivated_camera_and_no_jump_cut_per_word(self):
        s=build(story(SRC))
        cameras=s["camera_cuts"]
        self.assertLess(len(cameras),60)
        self.assertGreater(len(cameras),18)
        self.assertEqual({x["act"] for x in cameras},set(range(1,8)))
        self.assertEqual(cameras[0]["framing"],"establishing")
        for a,b in zip(cameras,cameras[1:]):
            self.assertGreater(b["start"],a["start"])
        self.assertTrue(all(x["rendered"] is False for x in cameras))

    def test_cannot_fake_dialogue_source_or_reuse_timing(self):
        src=story(SRC)
        src["lines"][3]["text"]="A changed phrase"
        with self.assertRaisesRegex(ValueError,"script changed"):
            build(src)

    def test_output_serializes_consistent_actors(self):
        s=build(story(SRC))
        text=json.dumps(s,ensure_ascii=False)
        x=json.loads(text)
        self.assertEqual(len(x["actor_controls"]["luma"]),84)
        self.assertTrue(x["source_dialogue_sha256"])
        self.assertFalse(x["film_ready"])


if __name__=="__main__":
    unittest.main()
