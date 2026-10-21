"""Validate genuine CPU 3D seven-act storyboard without rendering mock film."""
import json
import tempfile
import unittest
from pathlib import Path
from studio.vsim_cpu_episode import build, read_story, line_timing, generate

SCRIPT = Path(__file__).resolve().parents[2]/"studio"/"season1_episode1_full.json"


class VsimCPUFilmTests(unittest.TestCase):
    def test_all_original_acts_export_and_actor_id_stays_locked(self):
        with tempfile.TemporaryDirectory() as d:
            rec=build(SCRIPT,d)
            self.assertEqual(len(rec["acts"]),7)
            self.assertTrue(rec["all_seven_acts_compiled"])
            self.assertFalse(rec["film_ready"])
            self.assertGreater(sum(x["duration_seconds"] for x in rec["acts"]),300)
            for i in range(1,8):
                p=Path(d)/f"starwood_act{i}.film3d.json"
                self.assertTrue(p.exists())
                film=json.loads(p.read_text())
                self.assertEqual(film["version"],"film3d-1")
                self.assertEqual(film["fps"],24)
                self.assertEqual({c["id"]:c["character"] for c in film["actors"]},
                                 {"luma":"fox","pip":"rabbit"})
                self.assertTrue(len(film["beats"])>=2)
                self.assertEqual(film["beats"][0]["start"],0.0)
                prev=0.0
                for beat,shot in zip(film["beats"],film["camera"]):
                    self.assertEqual(beat["start"],prev)
                    self.assertEqual(shot["at"],prev)
                    self.assertAlmostEqual(shot["dur"],beat["end"]-beat["start"],places=3)
                    self.assertNotIn("narration",beat)
                    for action in beat["actions"]:
                        self.assertIn(action["actor"],{"luma","pip"})
                    prev=beat["end"]
                self.assertLess(prev,90.0)

    def test_always_uses_real_skeletal_clip_types(self):
        story=read_story(SCRIPT)
        timelines,_=line_timing(story)
        scene,receipt=generate(story,timelines,1)
        animations=[a for b in scene["beats"] for a in b["actions"]]
        self.assertTrue(any(a["do"]=="play" and a["clip"]=="Survey" for a in animations))
        self.assertTrue(any(a["do"]=="play" and a["clip"]=="idle" for a in animations))
        self.assertTrue(any(a["do"]=="move" and a["gait"]=="walk" for a in animations))
        self.assertFalse(receipt["film_ready"])

    def test_full_cast_report_is_timestamp_authority(self):
        story=read_story(SCRIPT)
        recs=[]
        t=0.0
        for line in story["lines"]:
            recs.append({"speaker":line["speaker"],"text":line["text"],
                         "start_seconds":t,"end_seconds":t+3})
            t+=3.1
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"cast_report.json"
            p.write_text(json.dumps({"lines":recs,"duration_seconds":t,"approval":False}))
            out=build(SCRIPT,Path(d)/"movie",cast_report=p)
            self.assertFalse(out["acts"][0]["estimated_voice_timing"])
            self.assertFalse(out["film_ready"])

    def test_missing_or_mismatched_voice_receipt_is_blocked(self):
        story=read_story(SCRIPT)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            p.write_text(json.dumps({"lines":[{"speaker":"luma","text":"bad"}]}))
            with self.assertRaises(ValueError):
                line_timing(story,p)

    def test_technical_slices_never_claim_completed_act(self):
        with tempfile.TemporaryDirectory() as d:
            rec=build(SCRIPT,d,act=3,technical_seconds=4.5)
            self.assertEqual(len(rec["acts"]),1)
            self.assertTrue(rec["acts"][0]["technical_cut"])
            self.assertAlmostEqual(rec["acts"][0]["duration_seconds"],4.5)
            self.assertFalse(rec["all_seven_acts_compiled"])


if __name__=="__main__":
    unittest.main()
