"""Install two-actor Godot ensemble and preserve upstream CC0 project.

Requires studio/export_facs_cast.py applied to complete offline voice/Rhubarb
records. No paid API, no cron, no publishing or user-visible partials.
"""
import argparse
import json
from pathlib import Path


def install(project: Path, driver: Path, director: Path):
    if not (project / "project.godot").is_file():
        raise ValueError("Not a Godot project")
    for path in [project / "scenes" / "vitruvian_cinematic.tscn",
                 project / "scenes" / "vitruvian_cinematic.gd",
                 project / "vitruvian_head.glb",
                 project / "vitruvian_body.glb",
                 driver, director]:
        if not path.is_file() or not path.stat().st_size:
            raise FileNotFoundError(f"Real skeleton/FACS rig or source missing: {path}")
    cast_path = project / "studio_cast" / "scene_cast.json"
    if not cast_path.is_file():
        raise FileNotFoundError("Create the offline three-voice cast manifest first")
    cast = json.loads(cast_path.read_text(encoding="utf-8"))
    speakers = {l.get("speaker") for l in cast.get("lines", [])}
    if not {"luma", "pip", "narrator"} <= speakers:
        raise ValueError("Full three-voice script with both rigged actors required")
    if cast.get("duration_seconds", 0) < 10:
        raise ValueError("Coherent story excerpt is required")
    if cast.get("release_gate", {}).get("film_ready"):
        raise ValueError("Cast metadata cannot self-certify a finished film")
    dest = project / "studio_cast"
    for path, name, expected in [
        (driver, "godot_facs_cast.gd", "_drive_visemes"),
        (director, "godot_ensemble_director.gd", "_direct_camera"),
    ]:
        text_data = path.read_text(encoding="utf-8")
        if expected not in text_data:
            raise ValueError(f"Missing real animation facility {expected}")
        target = dest / name
        if target.is_file() and target.read_text(encoding="utf-8") != text_data:
            raise RuntimeError(f"Cannot overwrite different production script: {target}")
        target.write_text(text_data, encoding="utf-8")
    stage = '''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://studio_cast/godot_ensemble_director.gd" id="1_ensemble"]

[node name="StarwoodTwoActorStory" type="Node3D"]
script = ExtResource("1_ensemble")
manifest_path = "res://studio_cast/scene_cast.json"
'''
    file = dest / "starwood_duo_scene.tscn"
    file.write_text(stage, encoding="utf-8")
    record = {
        "stage": str(file), "actors": ["luma", "pip"], "narrator": True,
        "real_skeletal_models": True, "real_facs_face_required": True,
        "speech_aligned": True, "dialogue_lines": len(cast["lines"]),
        "duration_seconds": cast["duration_seconds"],
        "film_release_pass": False,
        "qualifications": "Visual inspection and human listening remain necessary",
    }
    (dest / "starwood_duo_scene.receipt.json").write_text(
        json.dumps(record, indent=2), encoding="utf-8")
    return record


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--driver", type=Path, default=Path("studio/godot_facs_cast.gd"))
    p.add_argument("--director", type=Path, default=Path("studio/godot_ensemble_director.gd"))
    opts = p.parse_args()
    print(json.dumps(install(opts.project, opts.driver, opts.director)))


if __name__ == "__main__":
    main()
