"""Install a single performing actor scene into licensed CC0/MIΤ Godot 4.6 stage.

This creates *new* scene resources and copies the standalone script; upstream
VitruvianGodot production files stay unchanged and attributed. Input bundle
from studio/export_facs_cast.py must exist.

Usage:
  python studio/install_facs_actor.py --project path/to/VitruvianGodot/godot_project \
     --driver studio/godot_facs_cast.gd --speaker luma

It creates studio_cast/starwood_actor_luma.tscn; to compose multi-shot/multi-actor
sequences, use separate camera-directed takes and edit, or a proper multi-rig scene.
This is NOT a finished film.
"""
from __future__ import annotations
import argparse
import json
import shutil
from pathlib import Path

LICENSE = (
    "VitruvianGodot code © Agile Lens MIT; CC0 base character and FACS morphs "
    "from CharMorph / Olaf Delgado-Friedrichs & Sean Buckley. "
    "Movement tracks may include Mixamo animations (Adobe terms; audit for "
    "intended use). Original upstream: https://github.com/ibrews/VitruvianGodot\n"
)


def install(project: Path, driver: Path, speaker: str):
    if speaker not in ("luma", "pip"):
        raise ValueError("Only known speaking characters may be installed")
    if not driver.is_file():
        raise FileNotFoundError(driver)
    if not (project / "project.godot").is_file():
        raise ValueError("Missing Godot project")
    original = project / "scenes" / "vitruvian_cinematic.gd"
    base = project / "scenes" / "vitruvian_cinematic.tscn"
    if not original.is_file() or not base.is_file():
        raise FileNotFoundError("Missing CC0 Godot FACS stage; do not use static placeholders")
    manifest = project / "studio_cast" / "scene_cast.json"
    if not manifest.is_file():
        raise FileNotFoundError("Create the licensed local studio_cast manifest first")
    parsed = json.loads(manifest.read_text(encoding="utf-8"))
    if not parsed.get("cues", {}).get(speaker):
        raise ValueError("Actor has no recorded phoneme track")
    if parsed.get("release_gate", {}).get("film_ready") is True:
        raise ValueError("A cast transfer cannot certify film quality")
    script = driver.read_text(encoding="utf-8")
    if "extends Node" not in script or "_drive_visemes" not in script:
        raise ValueError("Expected a real GDScript facial-animation driver")
    target = project / "studio_cast"
    target.mkdir(exist_ok=True)
    output_driver = target / "godot_facs_cast.gd"
    if output_driver.exists() and output_driver.read_text(encoding="utf-8") != script:
        raise RuntimeError("Existing cast script differs; do not overwrite unrelated changes")
    output_driver.write_text(script, encoding="utf-8")
    base_text = base.read_text(encoding="utf-8")
    if 'path="res://scenes/vitruvian_cinematic.gd"' not in base_text:
        raise ValueError("Upstream stage script changed; refusing blind scene patching")
    scene = f'''[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scenes/vitruvian_cinematic.gd" id="1_cine"]
[ext_resource type="Script" path="res://studio_cast/godot_facs_cast.gd" id="2_act"]

[node name="Starwood_{speaker}" type="Node3D"]
script = ExtResource("1_cine")

[node name="LiveFace_{speaker}" type="Node" parent="."]
script = ExtResource("2_act")
speaker = "{speaker}"
manifest_path = "res://studio_cast/scene_cast.json"
'''
    scene_path = target / f"starwood_actor_{speaker}.tscn"
    scene_path.write_text(scene, encoding="utf-8")
    (target / "CREDITS.txt").write_text(LICENSE, encoding="utf-8")
    result = {
        "scene": str(scene_path.resolve()),
        "character": speaker,
        "real_facs_rig_required": True,
        "voice_input_ready": True,
        "phonemes": len(parsed["cues"][speaker]),
        "film_quality_passed": False,
    }
    (target / f"starwood_actor_{speaker}.receipt.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--driver", type=Path, default=Path("studio/godot_facs_cast.gd"))
    p.add_argument("--speaker", required=True, choices=["luma", "pip"])
    opts = p.parse_args()
    print(json.dumps(install(opts.project,opts.driver,opts.speaker)))


if __name__ == "__main__":
    main()
