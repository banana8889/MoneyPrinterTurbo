"""Offline, license-safe FACS cast transfer tests (no paid tools or network)."""
import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

from studio.export_facs_cast import export_cast, validate_cast_and_cues
from studio.install_facs_actor import install


DRIVER = Path(__file__).resolve().parents[2] / "studio" / "godot_facs_cast.gd"


class FACSPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.root = root
        self.cast_dir = root/"recorded"
        self.cast_dir.mkdir()
        self.cues_dir = root/"cues"
        self.cues_dir.mkdir()
        self.project = root/"godot"
        (self.project/"scenes").mkdir(parents=True)
        (self.project/"project.godot").write_text('config_version=5\n',encoding="utf-8")
        (self.project/"scenes"/"vitruvian_cinematic.tscn").write_text(
            '[gd_scene load_steps=2 format=3]\n'
            '[ext_resource type="Script" path="res://scenes/vitruvian_cinematic.gd" id="1"]\n'
            '[node name="Actor" type="Node3D"]\nscript=ExtResource("1")\n',encoding="utf-8")
        (self.project/"scenes"/"vitruvian_cinematic.gd").write_text(
            'extends Node3D\nvar face_mi\nvar bshapes={}\n',encoding="utf-8")
        self.lines=[]
        for i, name in enumerate(("narrator","luma","pip","luma","pip")):
            fn=self.cast_dir/f"line_{i+1:03d}.wav"
            with wave.open(str(fn),"wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(24000)
                samples=bytearray()
                for n in range(6000):
                    s=int(4200*math.sin(2*math.pi*200*n/24000))
                    samples.extend(s.to_bytes(2,"little",signed=True))
                wav.writeframes(bytes(samples))
            self.lines.append({"speaker":name,"emotion":"curious",
                              "start_seconds":i*0.5,"end_seconds":i*0.5+0.25,
                              "duration_seconds":0.25,"text":"Hello, there.","audio":f"/old-runner/absolute/{fn.name}"})
        self.cast_path=self.cast_dir/"cast_report.json"
        self.cast_path.write_text(json.dumps({"version":1,"lines":self.lines,
                                             "duration_seconds":2.5,
                                             "approval":False}),encoding="utf-8")
        for speaker in ("luma","pip"):
            offset=0.5 if speaker=="luma" else 1.
            cues=[{"start":round(offset+0.035*i,4),
                   "end":round(offset+0.035*(i+1),4),
                   "value":x} for i,x in enumerate("ABCDEFX")]
            (self.cues_dir/f"{speaker}_cues.json").write_text(
                json.dumps({"mouthCues":cues}),encoding="utf-8")

    def test_offline_export_works_from_moved_github_artifact(self):
        m=export_cast(self.cast_path,self.cues_dir,self.project)
        self.assertEqual(len(m["lines"]),5)
        self.assertEqual(set(m["cues"]),{"luma","pip"})
        self.assertFalse(m["release_gate"]["film_ready"])
        for line in m["lines"]:
            self.assertTrue(line["audio"].startswith("res://studio_cast/"))
            self.assertTrue((self.project/line["audio"].removeprefix("res://")).is_file())

    def test_install_uses_real_stage_and_does_not_patch_original(self):
        export_cast(self.cast_path,self.cues_dir,self.project)
        original=(self.project/"scenes"/"vitruvian_cinematic.tscn").read_text()
        a=install(self.project,DRIVER,"luma")
        b=install(self.project,DRIVER,"pip")
        self.assertEqual(a["phonemes"],7)
        self.assertEqual(b["phonemes"],7)
        self.assertFalse(a["film_quality_passed"])
        self.assertEqual(original,(self.project/"scenes"/"vitruvian_cinematic.tscn").read_text())
        self.assertTrue((self.project/"studio_cast"/"starwood_actor_luma.tscn").is_file())
        self.assertTrue((self.project/"studio_cast"/"starwood_actor_pip.tscn").is_file())

    def test_invalid_phoneme_fails_closed(self):
        path=self.cues_dir/"pip_cues.json"
        j=json.loads(path.read_text())
        j["mouthCues"][0]["value"]="UNKNOWN"
        path.write_text(json.dumps(j))
        with self.assertRaisesRegex(ValueError,"phoneme"):
            validate_cast_and_cues(self.cast_path,self.cues_dir)

    def test_overlapping_cast_timestamps_fails_closed(self):
        obj=json.loads(self.cast_path.read_text())
        obj["lines"][2]["start_seconds"]=0.51
        self.cast_path.write_text(json.dumps(obj))
        with self.assertRaisesRegex(ValueError,"Overlapping"):
            validate_cast_and_cues(self.cast_path,self.cues_dir)

    def test_no_static_character_fallback(self):
        export_cast(self.cast_path,self.cues_dir,self.project)
        (self.project/"scenes"/"vitruvian_cinematic.gd").unlink()
        with self.assertRaises(FileNotFoundError):
            install(self.project,DRIVER,"luma")

    def test_export_blocks_traversal(self):
        with self.assertRaisesRegex(ValueError,"safe"):
            export_cast(self.cast_path,self.cues_dir,self.project,"../../tmp")

    def test_no_self_certification(self):
        export_cast(self.cast_path,self.cues_dir,self.project)
        receipt=install(self.project,DRIVER,"luma")
        self.assertFalse(receipt["film_quality_passed"])
        self.assertTrue(receipt["real_facs_rig_required"])


if __name__=="__main__":
    unittest.main()
