"""Real local SCAIL-2 renderer for one ORIGINAL licensed Starwood segment.

Integrates actual upstream zai-org/SCAIL-2/generate.py CLI (June 2026).
No downloads, billing, paid APIs or fabricated rendered footage.

A private, uncommitted ledger must include:
  version: 1
  explicit_local_gpu_inference_authorized: true
  model: {repo_dir, checkpoint_dir, scail_weights, source_commit,
          code_rights_checked: true, weights_commercial_rights_checked: true}
  characters: {luma: {image, mask_image, original_rights_confirmed: true}, ...}
  performances: {ep01_sh001_seg01: {actor: luma, driving_video,
                 driving_mask_video, rights_cleared: true}, ...}

Usage:
 python -m studio.scail2_execution plan --film plan.json --ledger private.json \
     --segment ep01_sh001_seg01 --out out/segments
 python -m studio.scail2_execution execute --film plan.json --ledger private.json \
     --segment ep01_sh001_seg01 --out out/segments

Execution requires real locally installed model weights, CUDA GPU, rights
receipts, real motion files and an independently decoded moving-film check.
Technical output is NOT approved human-quality acting or a finished film.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = "zai-org/SCAIL-2"
SCHEMA = "MPT_FILMDSL_STYLE_V1 (inspired by CineCrew, not CineCrew-import compatible)"
SEGMENT = re.compile(r"ep[0-9]{2}_sh[0-9]{3}_seg[0-9]{2}\Z")
VRAM_MIB_FLOOR = 24000  # Conservative screening floor; not a performance guarantee.


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected source record object")
    return data


def must_file(obj, name):
    value = obj.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing local file reference: " + name)
    path = Path(value).expanduser().resolve()
    if not path.is_file() or path.stat().st_size < 1:
        raise FileNotFoundError("Source file absent/empty: " + str(path))
    return path


def granted(obj, field):
    if obj.get(field) is not True:
        raise PermissionError("Explicit source/asset license gate failed: " + field)


def sha256(path):
    hashvalue = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            hashvalue.update(chunk)
    return hashvalue.hexdigest()


def plan(film_path, ledger_path, segment_id, output_dir):
    if not SEGMENT.fullmatch(segment_id):
        raise ValueError("Unsafe segment identifier")
    film, ledger = load(film_path), load(ledger_path)
    if film.get("format") != SCHEMA or ledger.get("version") != 1:
        raise ValueError("Unsupported original cinematic source format")
    match = [v for v in film.get("segments", []) if v.get("id") == segment_id]
    if len(match) != 1:
        raise ValueError("Segment must occur exactly once in canonical story")
    segment = match[0]
    if "scail2" not in segment.get("engine_candidates", []):
        raise ValueError("SCAIL-2 is not applicable to this story segment")
    start, end = float(segment["start"]), float(segment["end"])
    if not math.isfinite(start) or not math.isfinite(end) or not 0 < end-start <= 5.01:
        raise ValueError("Invalid scene duration")
    seed = segment["seed"]
    if not isinstance(seed, int) or not 1 <= seed < 2**31:
        raise ValueError("Invalid deterministic generation seed")
    prompt = segment["render_prompts"].get("positive")
    if not isinstance(prompt, str) or not 25 <= len(prompt) <= 6000:
        raise ValueError("Scene must have grounded character and action prompt")
    model = ledger.get("model", {})
    granted(model, "code_rights_checked")
    granted(model, "weights_commercial_rights_checked")
    commit = model.get("source_commit", "")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Pinned official upstream Git SHA required")
    repo = Path(model.get("repo_dir", "")).expanduser().resolve()
    script = repo/"generate.py"
    if not script.is_file():
        raise FileNotFoundError("Real installed SCAIL-2 generate.py is required")
    ckpt = Path(model.get("checkpoint_dir", "")).expanduser().resolve()
    if not ckpt.is_dir() or not any(ckpt.iterdir()):
        raise FileNotFoundError("No local model checkpoint data")
    weights = must_file(model, "scail_weights")
    if weights.suffix != ".safetensors":
        raise ValueError("Require official safetensors-format motion model")
    perf = ledger.get("performances", {}).get(segment_id, {})
    granted(perf, "rights_cleared")
    actor = perf.get("actor")
    if actor not in {"luma", "pip"}:
        raise ValueError("Only original licensed fox/rabbit characters")
    char = ledger.get("characters", {}).get(actor, {})
    granted(char, "original_rights_confirmed")
    reference = must_file(char, "image")
    reference_mask = must_file(char, "mask_image")
    driving = must_file(perf, "driving_video")
    driving_mask = must_file(perf, "driving_mask_video")
    if reference.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("Original reference must be PNG/JPEG")
    if driving.suffix.lower() not in {".mp4", ".mov", ".avi"}:
        raise ValueError("Motion driving source must be actual movie file")
    granted(ledger, "explicit_local_gpu_inference_authorized")
    dest = Path(output_dir).expanduser().resolve() / (segment_id+".mp4")
    args = [
        sys.executable, str(script), "--model", "SCAIL-14B",
        "--ckpt_dir", str(ckpt), "--scail_path", str(weights),
        "--image", str(reference), "--mask_image", str(reference_mask),
        "--pose", str(driving), "--mask_video", str(driving_mask),
        "--target_w", "896", "--target_h", "512", "--segment_len", "81",
        "--segment_overlap", "5", "--base_seed", str(seed),
        "--prompt", prompt, "--save_file", str(dest),
    ]
    sources = {"character_image": reference, "character_mask": reference_mask,
               "driving_video": driving, "driving_mask": driving_mask, "weights": weights}
    return {"segment": segment_id, "actor": actor, "upstream": SOURCE,
            "source_commit": commit, "cwd": str(repo), "argv": args,
            "output": str(dest), "provenance": {k: sha256(v) for k,v in sources.items()},
            "technical_render_pass": False, "cinematic_release_pass": False}


def verify_model_source(spec):
    """Require pinned upstream commit and expected public original repository."""
    repo = Path(spec["cwd"])
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True,
            timeout=20).strip().lower()
        remote = subprocess.check_output(
            ["git", "-C", str(repo), "remote", "get-url", "origin"],
            text=True, timeout=20).strip().lower()
        dirty = subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"],
            text=True, timeout=20).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("Cannot verify actual SCAIL-2 source checkout") from error
    if not remote.rstrip("/").removesuffix(".git").endswith(
        ("github.com/zai-org/scail-2", "github.com:zai-org/scail-2")
    ):
        raise PermissionError("Installed source is not the official SCAIL-2 remote")
    if commit != spec["source_commit"]:
        raise RuntimeError("Source checkout SHA differs from licensed model receipt")
    if dirty:
        raise RuntimeError("Local SCAIL-2 source has unrecorded modifications")
    return commit


def detected_gpu_mib():
    nvidia = shutil.which("nvidia-smi")
    if not nvidia:
        raise RuntimeError("CUDA-capable GPU absent; no paid fallback")
    raw = subprocess.check_output(
        [nvidia, "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
        text=True, timeout=20)
    memory = [int(v.strip()) for v in raw.splitlines() if v.strip()]
    if not memory or max(memory) < VRAM_MIB_FLOOR:
        raise RuntimeError("Verified CUDA GPU needs >=24GB screening VRAM; no bypass")
    return max(memory)


def execute(spec, *, timeout_seconds=7200, runner=None, inspect_video=None):
    if not 15 <= timeout_seconds <= 28800:
        raise ValueError("Local GPU timeout must be 15-28800 seconds")
    verify_model_source(spec)
    gpu = detected_gpu_mib()
    output = Path(spec["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    if runner is None:
        runner = subprocess.run
    if inspect_video is None:
        from studio.film_render_quality_gate import inspect
        inspect_video = inspect
    result = runner(spec["argv"], cwd=spec["cwd"], timeout=timeout_seconds,
                    capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError("Local SCAIL-2 failed: "+(result.stderr or "")[-900:])
    if not output.is_file() or output.stat().st_size < 10000:
        raise RuntimeError("Model produced no real, playable movie file")
    # SCAIL-2 native generation is commonly ~16fps; this gate verifies
    # genuine moving pixels, NOT a 24fps mastered film (a later distinct gate).
    qc = inspect_video(output, minimum_seconds=1.0, minimum_fps=15.9)
    if not qc.get("verified_actual_render"):
        raise RuntimeError("Decoded moving-frame quality gate did not pass")
    receipt = {
        "segment": spec["segment"], "gpu_mib": gpu, "video_sha256": sha256(output),
        "source_commit": spec["source_commit"], "model": SOURCE,
        "technical_render_pass": True, "actual_frame_evidence": qc,
        "character_identity_qa": "NOT_REVIEWED", "acting_qa": "NOT_REVIEWED",
        "voice_qa": "NOT_REVIEWED", "cinematic_release_pass": False,
    }
    tmp = output.with_suffix(".tmp_receipt")
    tmp.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    tmp.replace(output.with_suffix(".receipt.json"))
    return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["plan", "execute"])
    p.add_argument("--film", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--segment", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    spec = plan(a.film, a.ledger, a.segment, a.out)
    if a.action == "plan":
        # Do not leak private paths or local dialogue in generated CI logs.
        print(json.dumps({"segment": spec["segment"], "actor": spec["actor"],
                          "engine": SOURCE, "inputs_verified": True,
                          "film_ready": False, "executed": False}))
    else:
        receipt = execute(spec)
        print(json.dumps({"segment": receipt["segment"],
                          "technical_render_pass": receipt["technical_render_pass"],
                          "cinematic_release_pass": False}))


if __name__ == "__main__":
    main()
