"""2026 frontier cinematic director for the original Starwood series.

Adapt concepts (NOT import drop-in APIs) from:
  - CineCrew FilmDSL (global meta / assets / memory / clips)
  - Stable Video Infinity 2.0 Pro (unique seeds, 5 motion frames)
  - SCAIL-2 (animal / multi-reference driven motion)
  - Wan-Animate-2 (reference image + actual performance driving video)
  - LongCat-Video-Avatar-1.5 (multi-speaker sound-driven clips)

Pre-production is free, offline, stdlib-only and **does not generate video**.
It refuses unlicensed actors, invented input frames or hidden paid APIs.
Use the GPU/source licensing gates before executing any candidate engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from studio.film_shot_planner import load_script, make_shot_plan

ENGINE_SOURCES = {
    "svi_wan22": {
        "repo": "vita-epfl/Stable-Video-Infinity",
        "branch": "svi_wan22", "role": "long_form_film_continuation",
        "rights": "UNVERIFIED_DEPENDENT_WEIGHTS",
        "gpu": "WAN 14B model; VRAM/quantization must be benchmarked",
    },
    "scail2": {
        "repo": "zai-org/SCAIL-2", "branch": "wan-scail2",
        "role": "animal_and_human_motion_transfer",
        "rights": "UNVERIFIED_DEPENDENT_WEIGHTS",
        "gpu": "CUDA required; profile inferences and weights before execution",
    },
    "wan_animate_2": {
        "repo": "Wan-Video/Wan-Animate-2", "branch": "main",
        "role": "end_to_end_character_driven_performance",
        "rights": "WEIGHT_CHECKPOINT_REVIEW_REQUIRED",
        "gpu": "Official: 8x A800 at 720p; 2x A800 at 480p",
    },
    "longcat_avatar_1_5": {
        "repo": "meituan-longcat/LongCat-Video", "branch": "main",
        "role": "multi_stream_audio_driven_character_video",
        "rights": "CHECK_EXACT_1_5_MODEL_AND_INPUT_AUDIO_RIGHTS",
        "gpu": "Official multi-GPU inference, not tested on free CPU",
    },
    "blender_master": {
        "repo": "blender/blender", "branch": "main",
        "role": "deterministic_original_rig_animation_and_master",
        "rights": "GPL_SOFTWARE; ALL_ASSETS_SEPARATELY_LICENCED",
        "gpu": "CPU rendering possible but final film time unknown",
    },
}
FORBIDDEN_ENDPOINTS = ("api.openai.com", "fal.ai", "replicate.com", "runwayml.com")
REQUIRED_CHARACTERS = {
    "luma": {"species": "original anthropomorphic fox", "signature": "copper-orange fur, cream muzzle, turquoise scarf", "style": "original 3D feature family animation"},
    "pip": {"species": "original anthropomorphic rabbit", "signature": "turquoise fur, cream muzzle, small gold ribbon", "style": "original 3D feature family animation"},
}
CLIP_SECONDS = 5.0
REQUIRED_ASSET_FIELDS = ("reference_image", "rig_scene", "owner_rights_confirmed")


def _unique_seed(episode: int, shot: int, segment: int) -> int:
    seed = hashlib.sha256(f"Starwood:{episode}:{shot}:{segment}:film2026".encode()).digest()
    return int.from_bytes(seed[:4], "big") % (2**31 - 1) + 1


def validate_asset_book(book: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(book, dict):
        raise ValueError("Asset book must be an object")
    actors = book.get("characters", {})
    if not isinstance(actors, dict):
        raise ValueError("characters must be an object")
    for name in actors:
        if name not in REQUIRED_CHARACTERS:
            raise ValueError("Unknown character asset must not silently join cast")
        rec = actors[name]
        if not isinstance(rec, dict):
            raise ValueError("Invalid character asset")
        for field in REQUIRED_ASSET_FIELDS:
            if field not in rec:
                raise ValueError(f"{name} missing required field: {field}")
        if rec["owner_rights_confirmed"] is not True:
            raise PermissionError(f"{name} reference / 3D rig rights NOT CLEARED")
        for field in ("reference_image", "rig_scene"):
            item = Path(rec[field])
            if not item.is_file():
                raise FileNotFoundError(f"{name} missing actual licensed {field}: {item}")
    audio = book.get("dialogue_audio", {})
    if not isinstance(audio, dict):
        raise ValueError("dialogue_audio must be an object")
    for speaker, record in audio.items():
        if speaker not in (*REQUIRED_CHARACTERS, "narrator"):
            raise ValueError("Unknown speaker")
        if not isinstance(record, dict) or record.get("licensed") is not True:
            raise PermissionError(f"{speaker} voice has no explicit commercial permission")
        if not Path(record.get("path", "")).is_file():
            raise FileNotFoundError(f"{speaker} voice file not available")
    for url in book.get("endpoints", []):
        if not isinstance(url, str) or not url.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise PermissionError("Only manually configured localhost inference; no hosted paid API")
        if any(host in url for host in FORBIDDEN_ENDPOINTS):
            raise PermissionError("Paid API endpoint forbidden")
    return book


def _describe_frame(shot: dict, identities: dict, dialogue: list) -> str:
    actors = [
        f"{who} ({rec['species']}; {rec['signature']})"
        for who, rec in identities.items()
    ]
    emotions = sorted({d["emotion"] for d in dialogue if d["speaker"] != "narrator"})
    blocking = "; ".join(
        f"{p['actor']}: {p['body_animation']} / {p['eyeline']}"
        for p in shot["blocking"] if p["actor"] != "narrator"
    )
    return (
        "Original cinematic three-dimensional family adventure set in "
        + shot["location"].replace("_", " ") + ". "
        + "The original recurring characters: " + "; ".join(actors) + ". "
        + "Intended shot " + shot["framing"].replace("_", " ") + ", "
        + "motivated camera, physically plausible weight/eye contact, "
        + "rich coherent lighting and expressive purposeful blocking. "
        + "Acting: " + blocking + ". "
        + "Emotion: " + ", ".join(emotions) + ". "
        + "Identity and wardrobe must match authorized reference assets. "
        + "No static poses, slide transitions or arbitrary camera zooms."
    )


def compile_film(book: dict[str, Any], script: dict[str, Any],
                 *, vram_gb: float = 0, gpu_count: int = 0) -> dict[str, Any]:
    if not isinstance(vram_gb, (int, float)) or not math.isfinite(vram_gb) or not 0 <= vram_gb <= 192:
        raise ValueError("Invalid per-device VRAM")
    if not isinstance(gpu_count, int) or not 0 <= gpu_count <= 32:
        raise ValueError("Invalid GPU count")
    validate_asset_book(book)
    plan = make_shot_plan(script)
    identity = REQUIRED_CHARACTERS
    by_line = {item["line_number"]: item for item in plan["timeline"]}
    shots = []
    segments = []
    for shot in plan["shots"]:
        dialogue = [by_line[i] for i in shot["line_numbers"]]
        actor_speech = {line["speaker"] for line in dialogue if line["speaker"] != "narrator"}
        description = _describe_frame(shot, identity, dialogue)
        # SVI-film uses LAST FIVE MOTION FRAMES, not a one-frame image,
        # for continuation. A new shot starts from its own identity-keyframe.
        shot_segments = []
        duration = float(shot["end"] - shot["start"])
        for index in range(max(1, math.ceil(duration / CLIP_SECONDS))):
            start = shot["start"] + index * CLIP_SECONDS
            end = min(start + CLIP_SECONDS, shot["end"])
            seg_id = f"ep{script['episode']:02d}_sh{shot['shot']:03d}_seg{index+1:02d}"
            speech = [d for d in dialogue if d["start"] < end and d["end"] > start]
            # Audio/model selection depends on ACTUAL recorded commercial
            # media and user-owned reference motion—not a made-up path.
            missing = []
            for who in ("luma", "pip"):
                if who not in book.get("characters", {}):
                    missing.append(f"{who}.licensed_original_reference_and_rig")
            for who in {d["speaker"] for d in speech}:
                if who not in book.get("dialogue_audio", {}):
                    missing.append(f"{who}.authorized_recorded_audio")
            if not book.get("performance_video") or not Path(str(book.get("performance_video", ""))).is_file():
                missing.append("licensed_directing_video_or_animal_motion")
            if not book.get("weights_cleared"):
                missing.append("model_weights_and_upstream_model_licenses_reviewed")
            if gpu_count == 0 or vram_gb == 0:
                missing.append("local_gpu_inference_capacity")
            if not book.get("final_art_quality_review"):
                missing.append("independent_visual_character_motion_review")

            engine_candidates = (
                ["longcat_avatar_1_5", "scail2", "wan_animate_2"]
                if len(actor_speech) >= 2 else
                ["scail2", "wan_animate_2", "svi_wan22"]
                if actor_speech else
                ["svi_wan22", "blender_master"]
            )
            seed = _unique_seed(script["episode"], shot["shot"], index)
            segment = {
                "id": seg_id, "shot_id": shot["shot"], "act": shot["act"],
                "start": round(start, 3), "end": round(end, 3), "seed": seed,
                "character_identity_refs": ["char_luma", "char_pip"],
                "scenario_ref": "loc_" + shot["location"],
                "continuation": {
                    "mode": "storyboard_keyframe" if index == 0 else "previous_5_motion_frames",
                    "reference_required": True,
                    "previous_segment": shot_segments[-1] if index else None,
                    "model_family": "SVI-2.0-Pro/Wan2.2 only when verified",
                },
                "engine_candidates": engine_candidates,
                "render_prompts": {
                    "positive": description,
                    "negative": "identity drift, different character face, changing clothes, incorrect species, frozen doll, floating limbs, flicker, low-quality voice",
                },
                "dialogue_line_ids": [d["line_number"] for d in speech],
                "render_ready": False,
                "missing_inputs": sorted(set(missing)),
                "output_path": None,
            }
            shot_segments.append(seg_id)
            segments.append(segment)
        shots.append({
            "shot_id": shot["shot"], "act": shot["act"], "location_ref": "loc_" + shot["location"],
            "framing": shot["framing"], "camera_motion": shot["camera_motion"],
            "narrative": {"lines": dialogue, "acting": shot["blocking"], "purpose": shot["editorial_purpose"]},
            "segments": shot_segments,
            "review": {"identity": "NOT_REVIEWED", "acting": "NOT_REVIEWED",
                       "audio": "NOT_REVIEWED", "cinematic": "NOT_REVIEWED",
                       "film_ready": False},
        })
    seeds = [s["seed"] for s in segments]
    if len(seeds) != len(set(seeds)):
        raise RuntimeError("Repeated seeds on 2026 continuation clips")
    if len(shots) != len(plan["shots"]):
        raise RuntimeError("Lost film shots")
    return {
        "format": "MPT_FILMDSL_STYLE_V1 (inspired by CineCrew, not CineCrew-import compatible)",
        "meta": {"series":script["series"], "episode":script["episode"],
                 "title": script["title"], "fps":24, "resolution":[1920,1080],
                 "duration_seconds_estimated":plan["story_duration_seconds"],
                 "content_origin": "original", "commercial_publish_authorized": False,
                 "all_prompts_contained_in_repository": True,
                 "paid_api_calls": False},
        "assets": {
            "characters": {
                "char_"+name: {**value, "actual_rig_supplied":name in book.get("characters", {})}
                for name,value in identity.items()
            },
            "locations": {"loc_"+v:{"look_locked":False,"set_design_missing":True}
                          for v in sorted(set(s["location_ref"][4:] for s in shots))},
        },
        "memory": {"character_identity_lock":True,"outfit_lock":True,
                   "asset_rights_required":True,"motion_history_frames":5,
                   "film_ready": False, "generated_video_count":0},
        "clips": shots,
        "segments": segments,
        "sources": ENGINE_SOURCES,
        "execution": {
            "state":"BLOCKED_PREPRODUCTION",
            "count_shots":len(shots), "count_segments":len(segments),
            "rendered_shots":0, "verified_running_engines":[],
            "local_gpu_count":gpu_count, "per_device_vram_gb":vram_gb,
            "license_gate":"FAIL_CLOSED",
            "monetary_actions_permitted":False,
            "next_gate":"licensed original character reference+rig+performance media+weights+GPU benchmark",
        },
    }


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("script",type=Path)
    p.add_argument("--assets",type=Path)
    p.add_argument("--gpu-count",type=int,default=0)
    p.add_argument("--vram-gb",type=float,default=0)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    assets=json.loads(args.assets.read_text(encoding="utf-8")) if args.assets else {"characters":{}}
    manifest=compile_film(assets,load_script(args.script),
                          vram_gb=args.vram_gb,gpu_count=args.gpu_count)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"shots":len(manifest["clips"]),
                      "segments":len(manifest["segments"]),
                      "actually_rendered":0,"video_ready":False,
                      "film_duration_seconds_estimated":manifest["meta"]["duration_seconds_estimated"]}))


if __name__=="__main__":
    main()
