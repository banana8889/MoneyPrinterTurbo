"""Narrative/shot sequencing production tests — no downloadable models."""
import unittest
from pathlib import Path

from studio.film_shot_planner import load_script, make_shot_plan, estimate_timeline

STORY = Path(__file__).resolve().parents[2] / "studio" / "season1_episode1_full.json"


class FilmStoryPlannerTest(unittest.TestCase):
    def test_seven_act_full_episode(self):
        script=load_script(STORY)
        out=make_shot_plan(script)
        self.assertEqual(len(out["timeline"]),84)
        self.assertGreater(out["story_duration_seconds"],240)
        self.assertLess(out["story_duration_seconds"],480)
        self.assertFalse(out["film_ready"])
        self.assertEqual({x["act"] for x in out["shots"]},set(range(1,8)))
        self.assertGreater(len(out["shots"]),20)
        self.assertLess(len(out["shots"]),80)

    def test_original_actors_and_camera_story_clips(self):
        out=make_shot_plan(load_script(STORY))
        self.assertEqual(out["render_fps"],24)
        self.assertEqual(out["target_resolution"],[1920,1080])
        self.assertTrue(any(x["framing"]=="wide_reveal" for x in out["shots"]))
        self.assertTrue(any("reaction" in x["framing"] for x in out["shots"]))
        self.assertTrue(all(x["render_status"]=="NOT_RENDERED" for x in out["shots"]))
        self.assertTrue(any("ORIGINAL" in m for m in out["missing_for_release"]))

    def test_no_camera_time_backwards(self):
        plan=make_shot_plan(load_script(STORY))
        for prev,next_shot in zip(plan["shots"],plan["shots"][1:]):
            self.assertLessEqual(prev["end"],next_shot["start"]+0.005)

    def test_no_rapid_aggressive_cut_every_line(self):
        plan=make_shot_plan(load_script(STORY))
        self.assertLess(len(plan["shots"]),len(plan["timeline"]))

    def test_invalid_canon_is_blocked(self):
        script=load_script(STORY)
        script["lines"][0]["act"]=99
        with self.assertRaises(ValueError):
            make_shot_plan(script)

    def test_audio_duration_source_is_explicitly_estimated(self):
        plan=make_shot_plan(load_script(STORY))
        self.assertTrue(all(x["estimated"] for x in plan["timeline"]))
        self.assertFalse(plan["film_ready"])

    def test_director_rejects_unreasonable_speech_pacing(self):
        with self.assertRaises(ValueError):
            estimate_timeline(load_script(STORY),wpm=300)


if __name__=="__main__":
    unittest.main()
