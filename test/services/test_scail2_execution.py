"""Tests for real 2026 SCAIL-2 local renderer; no paid providers or GPU used."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from studio import scail2_execution as impl
from studio.frontier_film_director import compile_film
from studio.film_shot_planner import load_script

EP = Path(__file__).resolve().parents[2] / "studio" / "season1_episode1_full.json"


class ScailExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        film = compile_film({}, load_script(EP))
        self.segment = next(s for s in film["segments"] if "scail2" in s["engine_candidates"])
        self.id = self.segment["id"]
        self.film_path = self.root/"compiled_film.json"
        self.film_path.write_text(json.dumps(film))
        repo = self.root/"official-scail2"
        repo.mkdir()
        (repo/"generate.py").write_text("print('mock upstream only')\n")
        model = self.root/"model"
        model.mkdir()
        weights = model/"scail.safetensors"
        weights.write_bytes(b"model checkpoint fixture")
        assets = self.root/"assets"
        assets.mkdir()
        for name in ("image.png", "reference_mask.png", "drive.mp4", "drive_mask.mp4"):
            (assets/name).write_bytes(b"original rights-cleared fixture, not real film")
        self.ledger = {
            "version": 1, "explicit_local_gpu_inference_authorized": True,
            "model": {
                "repo_dir": str(repo), "checkpoint_dir": str(model),
                "scail_weights": str(weights), "source_commit": "1"*40,
                "code_rights_checked": True,
                "weights_commercial_rights_checked": True,
            },
            "characters": {
                "luma": {"image":str(assets/"image.png"),
                         "mask_image":str(assets/"reference_mask.png"),
                         "original_rights_confirmed":True},
                "pip": {"image":str(assets/"image.png"),
                        "mask_image":str(assets/"reference_mask.png"),
                        "original_rights_confirmed":True},
            },
            "performances": {
                self.id: {
                    "actor":"luma", "driving_video": str(assets/"drive.mp4"),
                    "driving_mask_video":str(assets/"drive_mask.mp4"),
                    "rights_cleared": True,
                }
            },
        }
        self.ledger_path = self.root/"private-rights.json"
        self._save()

    def _save(self):
        self.ledger_path.write_text(json.dumps(self.ledger))

    def _plan(self, segment_id=None):
        return impl.plan(self.film_path, self.ledger_path,
                         self.id if segment_id is None else segment_id,
                         self.root/"outputs")

    def test_uses_exact_actual_upstream_scail2_cli(self):
        p = self._plan()
        argv = p["argv"]
        self.assertEqual(argv[1], str(self.root/"official-scail2"/"generate.py"))
        for flag in ("--image", "--mask_image", "--pose", "--mask_video",
                     "--scail_path", "--ckpt_dir", "--base_seed",
                     "--segment_len", "--segment_overlap", "--save_file"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--model")+1], "SCAIL-14B")
        self.assertEqual(p["segment"], self.id)
        self.assertEqual(len(p["provenance"]), 5)
        self.assertFalse(p["cinematic_release_pass"])

    def test_rejects_missing_or_unauthorized_weights(self):
        self.ledger["model"]["weights_commercial_rights_checked"] = False
        self._save()
        with self.assertRaises(PermissionError):
            self._plan()

    def test_no_imaginary_motion_or_hidden_asset(self):
        self.ledger["performances"] = {}
        self._save()
        with self.assertRaises(PermissionError):
            self._plan()

    def test_non_original_actor_or_identity_is_rejected(self):
        self.ledger["performances"][self.id]["actor"] = "disney_character"
        self._save()
        with self.assertRaises(ValueError):
            self._plan()

    def test_incorrect_checkpoint_format_is_rejected(self):
        self.ledger["model"]["scail_weights"] = str(self.root/"assets"/"image.png")
        self._save()
        with self.assertRaises(ValueError):
            self._plan()

    def test_no_execution_without_local_gpu_even_with_input_files(self):
        p = self._plan()
        with patch.object(impl, "detected_gpu_mib", side_effect=RuntimeError("no GPU")):
            with self.assertRaises(RuntimeError):
                impl.execute(p, runner=lambda *a, **k: self.fail("must not execute"))

    def test_valid_mocked_backend_never_claims_finished_cinema(self):
        p = self._plan()
        def fake_runner(argv, **kwargs):
            self.assertEqual(kwargs["cwd"], p["cwd"])
            self.assertFalse(kwargs.get("shell", False))
            Path(p["output"]).parent.mkdir(parents=True,exist_ok=True)
            Path(p["output"]).write_bytes(b"fake bytes"*2000)
            return SimpleNamespace(returncode=0, stderr="")
        def fake_qc(path, minimum_seconds):
            self.assertEqual(str(path), p["output"])
            self.assertEqual(minimum_seconds, 1.0)
            return {"verified_actual_render":True, "changed_frame_fraction":.7}
        with patch.object(impl, "detected_gpu_mib", return_value=49152):
            result = impl.execute(p, runner=fake_runner, inspect_video=fake_qc)
        self.assertTrue(result["technical_render_pass"])
        self.assertFalse(result["cinematic_release_pass"])
        self.assertEqual(result["character_identity_qa"],"NOT_REVIEWED")
        self.assertTrue(Path(p["output"]).with_suffix(".receipt.json").is_file())

    def test_rejects_undecoded_output_and_never_writes_success_receipt(self):
        p = self._plan()
        def runner(argv, **kwargs):
            Path(p["output"]).parent.mkdir(parents=True, exist_ok=True)
            Path(p["output"]).write_bytes(b"fake bytes"*2000)
            return SimpleNamespace(returncode=0, stderr="")
        with patch.object(impl, "detected_gpu_mib", return_value=49000):
            with self.assertRaises(RuntimeError):
                impl.execute(p, runner=runner,
                             inspect_video=lambda *a,**k: {"verified_actual_render":False})
        self.assertFalse(Path(p["output"]).with_suffix(".receipt.json").exists())

    def test_unsafe_segment_id_never_resolves_paths(self):
        with self.assertRaises(ValueError):
            self._plan("../../outside")

    def test_gpu_probe_has_no_paid_fallback(self):
        with patch.object(impl.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "no paid fallback"):
                impl.detected_gpu_mib()


if __name__ == "__main__":
    unittest.main()
