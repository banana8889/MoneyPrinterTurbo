"""Proof that commercial-license and GPU gates do not silently turn on paid tools."""
import unittest

from studio import free_toolchain as t


class ToolchainPolicyTests(unittest.TestCase):
    def test_registry_is_broad_and_unique(self):
        t.validate_registry()
        self.assertGreaterEqual(len(t.TOOLS), 30)
        self.assertEqual(len({(x.task,x.name) for x in t.TOOLS}),len(t.TOOLS))

    def test_cpu_profile_never_claims_generated_film(self):
        out=t.select(0)
        self.assertFalse(out["production_ready"])
        self.assertNotIn("mesh_generation",out["selected"])
        self.assertNotIn("automatic_skinning",out["selected"])
        self.assertNotIn("optional_video_enhancement",out["selected"])

    def test_unverified_weights_are_blocked_by_default(self):
        out=t.select(192)
        self.assertEqual(out["selected"]["character_animation"]["name"],"Blender")
        self.assertNotIn("automatic_skinning",out["selected"])
        self.assertEqual(out["selected"]["expressive_dialogue"]["name"],"Kokoro")

    def test_noncommercial_tool_never_unlocks_even_with_overrides(self):
        v=next(x for x in t.TOOLS if x.name=="GVHMR")
        self.assertFalse(t.evaluate(v,192,allow_conditional=True,allow_review=True)["ready"])

    def test_ltx_license_needs_opt_in(self):
        v=next(x for x in t.TOOLS if x.name=="LTX 2.5")
        self.assertFalse(t.evaluate(v,48)["ready"])
        self.assertFalse(t.evaluate(v,24,allow_conditional=True)["ready"])
        self.assertTrue(t.evaluate(v,48,allow_conditional=True)["ready"])

    def test_blender_studio_upstream_not_fake_github_repo(self):
        x=next(x for x in t.TOOLS if x.name=="Blender Studio Pipeline")
        self.assertEqual(x.url,"https://projects.blender.org/studio/blender-studio-tools")

    def test_not_installed_is_explicit_blocker(self):
        v=next(x for x in t.TOOLS if x.name=="Blender")
        from unittest.mock import patch
        with patch.object(t.shutil,"which",return_value=None):
            checked=t.evaluate(v,0,available_only=True)
        self.assertFalse(checked["ready"])
        self.assertIn("not installed",checked["reasons"][0])

    def test_invalid_vram_rejected(self):
        for v in (-1,300):
            with self.assertRaises(ValueError):
                t.select(v)

    def test_diagnosis_cannot_self_certify_spielberg_quality(self):
        out=t.diagnosis(128)
        self.assertFalse(out["release_allowed"])
        self.assertGreaterEqual(len(out["required_stages"]),6)


if __name__=="__main__":
    unittest.main()
