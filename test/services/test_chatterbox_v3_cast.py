"""Safe free voice casting test without downloading pretrained weights."""
import json
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    np = None
    sf = None

from studio.chatterbox_v3_cast import rights_receipts,render


class FakeAudioTensor:
    def __init__(self,array):
        self.array=array
    def detach(self):
        return self
    def cpu(self):
        return self
    def numpy(self):
        return self.array


class FakeV3:
    sr=24000
    def generate(self,text,language_id,audio_prompt_path):
        assert language_id=="en"
        assert Path(audio_prompt_path).is_file()
        t=np.arange(2*self.sr)/self.sr
        return FakeAudioTensor((.15*np.sin(2*np.pi*210*t)).astype("float32"))


@unittest.skipUnless(np is not None and sf is not None,"numpy and soundfile needed")
class ChatterboxCastTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.entries=[]
        for n,speaker in enumerate(("luma","pip","narrator")):
            t=np.arange(4*22050)/22050
            samples=(.12*np.sin(2*np.pi*(190+55*n)*t)).astype("float32")
            p=self.root/(speaker+".wav")
            sf.write(p,samples,22050)
            self.entries.append({"speaker":speaker,"wav":str(p),
                                 "rights":"owned_original_recording",
                                 "commercial_allowed":True})
        self.rights=self.root/"permission.json"
        self.rights.write_text(json.dumps({"version":1,"voices":self.entries}))
        story={"version":1,"lines":[{"speaker":"narrator","text":"Tonight, the sky changed.","emotion":"wonder"},
                                     {"speaker":"luma","text":"Where did that star go?","emotion":"curious"},
                                     {"speaker":"pip","text":"We should find out together.","emotion":"gentle"}]}
        self.script=self.root/"story.json"
        self.script.write_text(json.dumps(story))

    def test_unique_cast_rights_required(self):
        ref=rights_receipts(self.rights)
        self.assertEqual(set(ref),{"luma","pip","narrator"})

    def test_reject_unauthorized_voice(self):
        self.entries[0]["commercial_allowed"]=False
        self.rights.write_text(json.dumps({"version":1,"voices":self.entries}))
        with self.assertRaises(PermissionError):
            rights_receipts(self.rights)

    def test_reject_shared_voice_for_two_roles(self):
        self.entries[1]["wav"]=self.entries[0]["wav"]
        self.rights.write_text(json.dumps({"version":1,"voices":self.entries}))
        with self.assertRaisesRegex(ValueError,"Distinct"):
            rights_receipts(self.rights)

    def test_fake_local_model_preserves_real_cast_output_contract(self):
        receipt=render(self.script,self.rights,self.root/"dialogue",model=FakeV3())
        self.assertEqual(receipt["rendered"],3)
        self.assertFalse(receipt["approval"])
        self.assertFalse(receipt["suitable_for_publication"])
        self.assertEqual(receipt["human_voice_naturalness"],"NOT_AUDITIONED")
        self.assertTrue(all(Path(x["audio"]).is_file() for x in receipt["lines"]))
        self.assertEqual(len(set(x["voice_reference_sha256"] for x in receipt["lines"])),3)
        self.assertTrue((self.root/"dialogue"/"cast_report.json").is_file())
        self.assertLess(receipt["lines"][0]["end_seconds"],receipt["lines"][1]["start_seconds"])


if __name__=="__main__":
    unittest.main()
