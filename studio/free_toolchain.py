"""Free-first technical director for MoneyPrinterTurbo (October 2026).

Ranks audited GitHub tools by distinct production tasks and actual available
hardware. It never downloads models, spends money, starts cloud instances,
publishes content, or pretends installed tools create film-quality acting.

Usage:
    python -m studio.free_toolchain inventory
    python -m studio.free_toolchain select --vram 0
    python -m studio.free_toolchain select --vram 24
    python -m studio.free_toolchain diagnose --vram 0

All GPU thresholds are coarse planning *floors*, not benchmark guarantees.
Commercial permission is different for code, weights and input assets.
"""
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

LicenseStatus = Literal["permissive", "conditional", "needs_review", "not_commercial"]
Readiness = Literal["verified_in_project", "screened_not_integrated", "experimental"]


@dataclass(frozen=True)
class Candidate:
    name: str
    repo: str
    task: str
    code_license: str
    model_license: str
    commercial: LicenseStatus
    gpu_gb_floor: float
    ranking: int
    readiness: Readiness
    requires_executable: str = ""
    restrictions: str = ""

    @property
    def url(self):
        return self.repo if self.repo.startswith("https://") else "https://github.com/" + self.repo


# Code/weight grants describe different artifacts. CPU-available does not mean
# CPU-speed-real-time. GPU VRAM values are rough model-dependent floors, not
# recommendations for final production quality.
TOOLS = (
    Candidate("Blender", "blender/blender", "character_animation",
              "GPL-3.0", "none", "permissive", 0, 99,
              "verified_in_project", "blender", "Assets and render time remain separate."),
    Candidate("Godot", "godotengine/godot", "realtime_previsualization",
              "MIT", "none", "permissive", 0, 85,
              "verified_in_project", "godot", "Used with CC0 reference, NOT original hero cast."),
    Candidate("Blender Studio Pipeline", "https://projects.blender.org/studio/blender-studio-tools",
              "shot_asset_management", "GPL-3.0", "none", "permissive", 0, 100,
              "screened_not_integrated", "", "Upstream authoritative source is Blender Projects, not GitHub mirror."),
    Candidate("OpenUSD", "PixarAnimationStudios/OpenUSD", "scene_interchange",
              "Apache-2.0", "none", "permissive", 0, 80,
              "screened_not_integrated"),
    Candidate("OpenColorIO", "AcademySoftwareFoundation/OpenColorIO", "color_grading",
              "BSD-3-Clause", "none", "permissive", 0, 95,
              "screened_not_integrated"),
    Candidate("OpenImageDenoise", "RenderKit/oidn", "render_denoising",
              "Apache-2.0", "none", "permissive", 0, 90,
              "screened_not_integrated", "", "May be bundled in Blender."),
    Candidate("FFmpeg", "FFmpeg/FFmpeg", "video_mastering",
              "LGPL/GPL per build", "none", "conditional", 0, 99,
              "verified_in_project", "ffmpeg", "Confirm actual encoder flags for commercial distribution."),
    Candidate("VitruvianGodot reference", "ibrews/VitruvianGodot", "face_performance_reference",
              "MIT", "CC0 facial assets; Adobe terms for some body animations",
              "conditional", 0, 85, "verified_in_project", "",
              "A proof-of-concept HUMAN actor; not licensed original Luma/Pip"),
    Candidate("Tripo Face Rig", "mdj128/facial-animation", "facial_rig",
              "MIT", "user-provided assets", "permissive", 0, 76,
              "screened_not_integrated", "blender",
              "Requires artist-prepared mouth, eyes, jaw, teeth, and tongue."),
    Candidate("SkinTokens", "VAST-AI-Research/SkinTokens", "automatic_skinning",
              "MIT", "MIT (VAST-AI/SkinTokens checkpoint card)", "permissive", 14, 95,
              "screened_not_integrated", "", "Automatic rigging does not generate convincing acting."),
    Candidate("UniRig", "VAST-AI-Research/UniRig", "automatic_skinning",
              "MIT", "checkpoint separately review", "needs_review", 8, 84,
              "screened_not_integrated"),
    Candidate("MMPose", "open-mmlab/mmpose", "motion_estimation",
              "Apache-2.0", "checkpoint separately review", "needs_review", 8, 86,
              "screened_not_integrated", "",
              "Requires motion retargeting and subject rights."),
    Candidate("Rhubarb Lip Sync", "DanielSWolf/rhubarb-lip-sync", "phoneme_timing",
              "MIT", "none", "permissive", 0, 94,
              "verified_in_project", "rhubarb",
              "Phonemes alone cannot convey emotion."),
    Candidate("Chatterbox Multilingual V3", "resemble-ai/chatterbox", "expressive_dialogue",
              "MIT", "MIT (ResembleAI/chatterbox official model card)", "permissive", 0, 96,
              "screened_not_integrated", "",
              "CPU possible in principle, throughput and voice expressiveness unbenchmarked."),
    Candidate("Qwen3-TTS", "QwenLM/Qwen3-TTS", "expressive_dialogue",
              "Apache-2.0", "Apache-2.0 (Qwen3-TTS 1.7B Base)", "permissive", 0, 93,
              "screened_not_integrated", "",
              "10-language focus; evaluate English voices separately."),
    Candidate("CosyVoice 3", "QwenAudio/CosyVoice", "expressive_dialogue",
              "Apache-2.0", "check model-specific terms", "needs_review", 0, 90,
              "screened_not_integrated", "",
              "Model deployment may need substantial RAM/GPU; no quality proof yet."),
    Candidate("Voicebox", "jamiepine/voicebox", "voice_cast_editor",
              "MIT", "TTS backend dependent", "conditional", 0, 89,
              "screened_not_integrated", "",
              "Local multi-track voice studio is UI; not a quality-certified voice model."),
    Candidate("Kokoro", "hexgrad/kokoro", "expressive_dialogue",
              "Apache-2.0", "Apache-2.0 (Kokoro 82M)", "permissive", 0, 78,
              "verified_in_project", "",
              "Actual Kokoro synthetic audio verified, NOT approved as human-quality acting."),
    Candidate("Whisper.cpp", "ggml-org/whisper.cpp", "dialogue_transcription_qa",
              "MIT", "checkpoint varies", "needs_review", 0, 84,
              "screened_not_integrated", "",
              "ASR intelligibility does not establish natural voice acting."),
    Candidate("Wan2.2", "Wan-Video/Wan2.2", "optional_video_enhancement",
              "Apache-2.0", "Apache-2.0 stated for official model family",
              "permissive", 24, 89, "screened_not_integrated",
              "", "Character drift requires reference, frame and identity checks."),
    Candidate("LTX 2.5", "Lightricks/LTX-2", "optional_video_enhancement",
              "LTX-2.x Community", "LTX-2.x Community",
              "conditional", 32, 93, "experimental", "",
              "Revenue >=USD 10m/year requires commercial agreement; usage restrictions."),
    Candidate("HunyuanVideo 1.5", "Tencent-Hunyuan/HunyuanVideo-1.5",
              "optional_video_enhancement", "Tencent Community", "Tencent Community",
              "conditional", 14, 86, "experimental", "",
              "Special territory and scale terms; not blanket commercial clearance."),
    Candidate("ComfyUI", "Comfy-Org/ComfyUI", "optional_model_workflows",
              "GPL-3.0", "per node and checkpoint", "conditional", 0, 90,
              "screened_not_integrated", "", "Disable partner paid nodes and hosted services."),
    Candidate("TRELLIS.2", "microsoft/TRELLIS.2", "mesh_generation",
              "MIT", "MIT model; dependencies separate", "conditional", 24, 93,
              "screened_not_integrated", "", "nvdiffrast/nvdiffrec licensing must be reviewed."),
    Candidate("Hunyuan3D 2.1", "Tencent-Hunyuan/Hunyuan3D-2.1", "mesh_generation",
              "Tencent Community", "Tencent Community", "conditional", 29, 87,
              "experimental", "", "Territory restrictions; GPU for shape+texture."),
    Candidate("TripoSR", "VAST-AI-Research/TripoSR", "mesh_generation",
              "MIT repository", "checkpoint-specific", "needs_review", 6, 79,
              "screened_not_integrated"),
    Candidate("Real-ESRGAN", "xinntao/Real-ESRGAN", "upscaling",
              "BSD-3-Clause code", "model weights vary", "needs_review", 4, 86,
              "screened_not_integrated"),
    Candidate("REAL Video Enhancer", "sovcha/real-video-enhancer", "upscaling",
              "code/license confirm", "model weights vary", "needs_review", 4, 83,
              "screened_not_integrated", "",
              "Upscaling cannot create missing character animation; verify all models."),
    Candidate("ACE-Step", "ACE-Step/ACE-Step", "original_music",
              "Apache-2.0", "review exact music checkpoint and output terms",
              "needs_review", 0, 84, "screened_not_integrated"),
    Candidate("LivePortrait", "KwaiVGI/LivePortrait", "optional_face_motion",
              "project terms check", "model checkpoints check", "needs_review", 12, 70,
              "experimental", "", "2D facial animation not full 3D acting; no identity guarantee."),
    Candidate("MuseTalk", "TMElyralab/MuseTalk", "optional_face_motion",
              "MIT code", "weights/dependency licenses must be confirmed",
              "needs_review", 8, 76, "screened_not_integrated", "",
              "2D talking-avatar approach, not whole-body cinematic acting."),
    # 2026 frontier review: CODE license and MODEL WEIGHTS licenses are separate.
    # VRAM floors are *planning approximations*; upstream requires much more
    # compute in some configurations (Wan-Animate-2 reference: 8x A800).
    Candidate("SCAIL-2", "zai-org/SCAIL-2", "character_motion_transfer",
              "Apache-2.0", "checkpoint terms awaiting independent verification",
              "needs_review", 24, 98, "screened_not_integrated", "",
              "2026 animal-driving / multi-reference character motion, not run locally."),
    Candidate("Wan-Animate-2", "Wan-Video/Wan-Animate-2",
              "character_motion_transfer", "Apache-2.0",
              "official checkpoint license and dependencies to reconfirm",
              "needs_review", 80, 100, "screened_not_integrated", "",
              "2026-08-07. Official setup tuned for 8x A800 720p or 2x A800 480p."),
    Candidate("Stable Video Infinity 2.0 Pro", "vita-epfl/Stable-Video-Infinity",
              "longform_temporal_consistency", "MIT",
              "SVI LoRA + upstream Wan weights separately licensed",
              "needs_review", 48, 100, "screened_not_integrated", "",
              "2026 long cartoon and multi-shot continuation; supported branch svi_wan22."),
    Candidate("CineCrew FilmDSL", "Ironieser/CineCrew",
              "film_orchestration", "Apache-2.0",
              "LLM/image/video provider licenses vary",
              "conditional", 0, 99, "screened_not_integrated", "",
              "Default README config points at PAID LLM API; must use local inference only."),
    Candidate("LongCat Video Avatar 1.5", "meituan-longcat/LongCat-Video",
              "multi_speaker_video", "MIT repository code",
              "check exact 1.5 model weights and voice/asset rights",
              "needs_review", 80, 98, "screened_not_integrated", "",
              "2026-05-21 multi-stream audio, animals and continued clips; multiple GPU official."),
    Candidate("ShotStream", "KlingAIResearch/ShotStream",
              "streaming_multishot_video", "license not established",
              "checkpoint terms not established",
              "needs_review", 48, 82, "experimental", "",
              "ECCV 2026 reference implementation with original internal data gap."),
    Candidate("LiveAvatar", "Alibaba-Quark/LiveAvatar",
              "streaming_audio_avatar", "Apache-2.0",
              "model checkpoints/dependencies separately reviewed",
              "needs_review", 48, 88, "screened_not_integrated", "",
              "Cartoon styles, but 45fps claim on multi-H800 hardware, not ordinary PC."),
    Candidate("Memento", "ernie-research/Memento",
              "longform_temporal_consistency", "code license not found",
              "checkpoint permissions need proof",
              "needs_review", 48, 83, "experimental", "",
              "2026 autoregressive visual identity memory across shots."),
    Candidate("StoryMem", "Kevin-thu/StoryMem",
              "longform_temporal_consistency", "S-Lab noncommercial",
              "S-Lab noncommercial", "not_commercial", 48, 92,
              "experimental", "", "Exclude from monetized children show without paid licence."),
    Candidate("WanGP local model manager", "DeepBeepMeep/Wan2GP",
              "local_generation_management", "repo license to verify",
              "selected models have individual licenses", "needs_review", 12, 87,
              "screened_not_integrated", "",
              "2026 updated local frontend with SCAIL-2/Wan Animate; no paid API fallback."),
    Candidate("vsim Film3D CPU", "kunalkushwaha/vsim", "cpu_3d_film_render",
              "MIT", "MIT rabbit; Fox rig CC-BY attribution",
              "permissive", 0, 96, "verified_in_project", "node",
              "Full seven-act docs native-validated; paid AI API not required for deterministic rendering. Original hero-quality IP not yet complete."),
    Candidate("GVHMR", "zju3dv/GVHMR", "motion_estimation",
              "research-only", "research-only", "not_commercial", 8, 90,
              "experimental", "", "Excluded from revenue-generating film pipeline."),
)


def validate_registry() -> None:
    assert len(TOOLS) >= 25
    keys = [(x.task, x.name) for x in TOOLS]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate tool name and task")
    for t in TOOLS:
        if not t.name or not t.repo or not 0 <= t.ranking <= 100:
            raise ValueError("Invalid registry entry")
        if t.gpu_gb_floor < 0 or not t.code_license or not t.model_license:
            raise ValueError("Missing resource or license information")
        if not t.url.startswith("https://"):
            raise ValueError("Invalid source URL")


def evaluate(tool: Candidate, vram: float, *, allow_conditional=False,
             allow_review=False, available_only=False) -> dict:
    reasons = []
    if tool.commercial == "not_commercial":
        reasons.append("excluded: noncommercial license")
    elif tool.commercial == "conditional" and not allow_conditional:
        reasons.append("conditional license requires explicit approval")
    elif tool.commercial == "needs_review" and not allow_review:
        reasons.append("weights/asset terms not yet commercially verified")
    if tool.gpu_gb_floor > vram:
        reasons.append(f"requires >= {tool.gpu_gb_floor:g}GB GPU; detected {vram:g}GB")
    if available_only and tool.requires_executable and not shutil.which(tool.requires_executable):
        reasons.append(f"not installed: {tool.requires_executable}")
    return {"name": tool.name, "task": tool.task, "url": tool.url, "ready": not bool(reasons),
            "integrated_and_previously_verified": tool.readiness == "verified_in_project",
            "reasons": reasons, "commercial_policy": tool.commercial,
            "readiness": tool.readiness, "gpu_gb_floor": tool.gpu_gb_floor,
            "ranking": tool.ranking}


def select(vram: float, *, allow_conditional=False, allow_review=False,
           available_only=False) -> dict:
    validate_registry()
    if not 0 <= vram <= 192:
        raise ValueError("VRAM value should be between 0GB and 192GB")
    grouped = {}
    blocked = {}
    for t in TOOLS:
        result = evaluate(t, vram, allow_conditional=allow_conditional,
                          allow_review=allow_review, available_only=available_only)
        if result["ready"]:
            if t.task not in grouped or t.ranking > grouped[t.task]["ranking"]:
                grouped[t.task] = result
        else:
            blocked.setdefault(t.task, []).append(result)
    return {"vram_gb": vram, "commercial_opt_in": allow_conditional,
            "unverified_models_opt_in": allow_review,
            "selected": {k: v for k,v in sorted(grouped.items())},
            "blocked": {k: sorted(v, key=lambda x: -x["ranking"])
                        for k,v in sorted(blocked.items())},
            "production_ready": False,
            "notes": "Selection means technically/licensing-eligible candidate only; not installed, integrated, cinematic or approved."}


def diagnosis(vram: float) -> dict:
    s=select(vram, available_only=True)
    needed = ("character_animation", "automatic_skinning", "expressive_dialogue",
              "phoneme_timing", "color_grading", "video_mastering")
    return {
        "vram_gb": vram,
        "required_stages": list(needed),
        "available_stages": sorted(set(needed).intersection(s["selected"])),
        "missing_or_blocked": [x for x in needed if x not in s["selected"]],
        "release_allowed": False,
        "reason": "No test can certify Spielberg-level acting, licensed original characters or a complete finished episode."
    }


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("operation", choices=["inventory","select","diagnose"])
    p.add_argument("--vram", type=float, default=0)
    p.add_argument("--allow-conditional", action="store_true")
    p.add_argument("--allow-unverified-models", action="store_true")
    p.add_argument("--installed-only", action="store_true")
    args=p.parse_args(argv)
    if args.operation == "inventory":
        validate_registry()
        data=[{**asdict(t), "url":t.url} for t in TOOLS]
    elif args.operation=="diagnose":
        data=diagnosis(args.vram)
    else:
        data=select(args.vram, allow_conditional=args.allow_conditional,
                    allow_review=args.allow_unverified_models,
                    available_only=args.installed_only)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
