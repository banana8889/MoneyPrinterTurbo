"""Protect the real 3D cast ensemble from turning back into still images."""
import json
import unittest
from pathlib import Path

from studio.export_facs_cast import export_cast
from studio.install_ensemble import install
from test.services.test_facs_pipeline import FACSPipelineTests

STUDIO = Path(__file__).resolve().parents[2] / "studio"


class EnsembleTests(FACSPipelineTests):
    def setUp(self):
        super().setUp()
        # A cast excerpt long enough for real shared scene blocking.
        r=json.loads(self.cast_path.read_text(encoding="utf-8"))
        r["duration_seconds"] = 12.0
        self.cast_path.write_text(json.dumps(r),encoding="utf-8")
        for name in ("vitruvian_head.glb", "vitruvian_body.glb"):
            (self.project/name).write_bytes(b"glTF" + b"\x00"*24)

    def test_ensemble_install_requires_audio_real_facs_and_two_actors(self):
        m=export_cast(self.cast_path,self.cues_dir,self.project)
        r=install(self.project,STUDIO/"godot_facs_cast.gd",
                  STUDIO/"godot_ensemble_director.gd")
        self.assertEqual(r["actors"],["luma","pip"])
        self.assertTrue(r["real_skeletal_models"])
        self.assertTrue(r["speech_aligned"])
        self.assertFalse(r["film_release_pass"])
        scene=self.project/"studio_cast"/"starwood_duo_scene.tscn"
        self.assertIn("godot_ensemble_director.gd",scene.read_text())

    def test_real_character_mesh_is_required(self):
        export_cast(self.cast_path,self.cues_dir,self.project)
        (self.project/"vitruvian_head.glb").unlink()
        with self.assertRaises(FileNotFoundError):
            install(self.project,STUDIO/"godot_facs_cast.gd",
                    STUDIO/"godot_ensemble_director.gd")

    def test_no_fake_one_character_story(self):
        m=export_cast(self.cast_path,self.cues_dir,self.project)
        dest=self.project/"studio_cast"/"scene_cast.json"
        m["lines"]=[v for v in m["lines"] if v["speaker"] != "pip"]
        dest.write_text(json.dumps(m),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"three-voice"):
            install(self.project,STUDIO/"godot_facs_cast.gd",
                    STUDIO/"godot_ensemble_director.gd")


if __name__ == "__main__":
    unittest.main()
