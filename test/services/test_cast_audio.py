"""Production voice-engine checks; no online model download during unit tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio import cast_audio as m

FIXTURE = {
    "version": 1,
    "series": "Starwood",
    "lines": [
        {"speaker": "narrator", "emotion": "wonder", "text": "The lights went out."},
        {"speaker": "luma", "emotion": "curious", "text": "Pip, where are you?"},
        {"speaker": "pip", "emotion": "gentle", "text": "I am right beside you."},
    ],
}


class CastAudioTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "scene.json"
        self.path.write_text(json.dumps(FIXTURE), encoding="utf-8")

    def test_manifest_has_three_distinct_voices(self):
        result = m.read_script(self.path)
        self.assertEqual(len(result["lines"]), 3)
        self.assertEqual(len({m.ALLOWED_VOICES[x["speaker"]] for x in result["lines"]}), 3)

    def test_unknown_speaker_fails_closed(self):
        obj = copy.deepcopy(FIXTURE)
        obj["lines"][1]["speaker"] = "unlicensed_clone"
        self.path.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "speaker"):
            m.read_script(self.path)

    def test_emotion_validation_fails_closed(self):
        obj = copy.deepcopy(FIXTURE)
        obj["lines"][1]["emotion"] = "rage"
        self.path.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "emotion"):
            m.read_script(self.path)

    def test_empty_text_fails_closed(self):
        obj = copy.deepcopy(FIXTURE)
        obj["lines"][2]["text"] = " "
        self.path.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "length"):
            m.read_script(self.path)

    def test_not_enough_speakers_fails(self):
        obj = copy.deepcopy(FIXTURE)
        for item in obj["lines"]:
            item["speaker"] = "luma"
        self.path.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "two"):
            m.read_script(self.path)

    def test_low_rms_rejected(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy not present in minimal environment")
        samples = np.zeros(24000)
        with self.assertRaisesRegex(RuntimeError, "Silent"):
            m.trim_fade(samples, 24000)

    def test_approval_is_never_inferred_from_audio_created(self):
        try:
            import numpy as np
            import soundfile
        except ImportError:
            self.skipTest("soundfile/numpy unavailable")
        def fake(model, line):
            t = np.arange(24000 * 2) / 24000.
            return (0.12 * np.sin(2 * np.pi * 190 * t)).astype("float32"), 24000
        with patch.object(m, "synthesize", new=fake):
            result = m.render(self.path, Path(self.tmp.name) / "audio", model=object())
        self.assertEqual(result["rendered"], 3)
        self.assertFalse(result["approval"])
        self.assertEqual(result["subjective_acting_quality"], "NOT_REVIEWED")
        self.assertTrue(Path(self.tmp.name, "audio", "cast_report.json").is_file())
        self.assertLess(result["lines"][0]["end_seconds"],
                        result["lines"][1]["start_seconds"])
        self.assertLess(result["lines"][1]["end_seconds"],
                        result["lines"][2]["start_seconds"])


if __name__ == "__main__":
    unittest.main()
