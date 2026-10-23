"""Animate *real* Blender facial shape keys from Rhubarb mouth cues.

An open-source offline phonetic cue sequence drives a rigged character's
existing shape keys; it never substitutes camera zooms or random mouth motion.

Only applies to user-owned / properly licensed blend files with at least
four distinct professionally modeled viseme shapes. It cannot invent a rig.
For offline cue extraction use DanielSWolf/rhubarb-lip-sync (MIT code).

Example (inside Blender):
  blender -b shot.blend --python studio/apply_visemes.py -- \
    --mesh CHARACTER_HEAD --cues speaker01_mouth.json \
    --map studio/viseme_map_example.json --out shot_voiced.blend --offset 12.5
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path

PHONEMES = {"A", "B", "C", "D", "E", "F", "G", "H", "X"}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", required=True)
    parser.add_argument("--cues", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--fps", type=int, default=24)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def read_cues(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    cues = data.get("mouthCues")
    if not isinstance(cues, list) or not cues:
        raise ValueError("Rhubarb mouthCues missing or empty")
    previous = 0.0
    result = []
    for cue in cues:
        start, end, mouth = cue.get("start"), cue.get("end"), cue.get("value")
        if not isinstance(mouth, str) or mouth not in PHONEMES:
            raise ValueError("Unknown mouth pose")
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (start, end)):
            raise ValueError("Invalid mouth cue timing")
        if start < 0 or end <= start or start < previous - .005:
            raise ValueError("Overlapping, negative or out-of-order phoneme cues")
        previous = end
        result.append((float(start), float(end), mouth))
    return result


def read_mapping(path, cue_values):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Mouth mapping must be a dictionary")
    if not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k,v in data.items()):
        raise ValueError("Mouth mapping contains invalid shape-key names")
    if "X" in data and data["X"]:
        raise ValueError("The neutral X pose must not override an active mouth key")
    used = {p for _, _, p in cue_values if p != "X"}
    if not used <= set(data):
        raise ValueError(f"Missing required viseme mapping: {sorted(used-set(data))}")
    # A usable facial rig must have at least four independently sculpted mouth poses.
    if len(set(data[v] for v in used)) < 4:
        raise ValueError("At least four distinct facial shape keys required")
    return data


def build_curves(cues, mapping, offset, fps, shape_keys, scene):
    if offset < 0 or not math.isfinite(offset) or fps < 24:
        raise ValueError("Invalid face animation offset / frame rate")
    available = {k.name: k for k in shape_keys.key_blocks}
    for name in set(mapping.values()):
        if name not in available:
            raise ValueError(f"Rig lacks facial shape key: {name}")
    shapes = {name for name in mapping.values()}
    first = max(1, round(offset*fps)+1)
    last = round((offset+cues[-1][1])*fps)+1
    if last > scene.frame_end:
        raise ValueError("Dialogue would exceed shot duration; no silent truncation")
    # Validate everything before adding keys. No destructive edits to existing
    # expressions, body motion, or rigs; intended for new scene/shape tracks.
    for name in shapes:
        if not 0 <= available[name].value <= 1:
            raise ValueError(f"Invalid shape key baseline: {name}")
    # Determine sample time events with neutral between mouth changes and ease in
    #/out over one to two frames. Multiple cues may share a frame; latest cue wins.
    samples = {frame: None for frame in range(first, last+1)}
    for frame in samples:
        t = (frame-1)/fps-offset
        active = next(((a,b,p) for a,b,p in cues if a <= t < b), None)
        weights = {name: 0.0 for name in shapes}
        if active and active[2] != "X":
            a,b,p = active
            ramp = .06
            weight = min(1.0, max(0.0,(t-a)/ramp),max(0.0,(b-t)/ramp))
            weights[mapping[p]] = min(1.0, weight)
        samples[frame] = weights
    for frame, values in samples.items():
        for name, val in values.items():
            key_block = available[name]
            key_block.value = val
            key_block.keyframe_insert(data_path="value",frame=frame,
                                      group="MPT_Offline_Phoneme_Dialogue")
    scene.frame_set(first)
    return {"frames_keyed": len(samples), "start_frame": first,
            "end_frame": last, "viseme_shapes": sorted(shapes),
            "mouth_cues": len(cues), "max_dialogue_seconds": round(cues[-1][1],3)}


def main():
    import bpy
    args = parse_args()
    if not args.cues.is_file() or not args.map.is_file():
        raise FileNotFoundError("Missing mouth cues or mapping file")
    cues = read_cues(args.cues)
    mapping = read_mapping(args.map, cues)
    ob = bpy.data.objects.get(args.mesh)
    if not ob or ob.type != "MESH" or not ob.data.shape_keys:
        raise RuntimeError("Facial-animation target must be a mesh with real shape keys")
    scene = bpy.context.scene
    if scene.render.fps != args.fps:
        raise ValueError("Facial frame rate differs from actual scene rate")
    result = build_curves(cues, mapping, args.offset, args.fps, ob.data.shape_keys, scene)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out.resolve()))
    args.out.with_suffix(".visemes.json").write_text(json.dumps({
        "status": "phonetic_lip_sync_only", "emotion_and_eye_acting": "NOT_VERIFIED",
        "voice_quality": "NOT_VERIFIED", "film_ready": False, **result}, indent=2),
        encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
