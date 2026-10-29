# STARWOOD Learned Generator CPU V1 — verified development receipt (2026-10-28)

Goal from user: stop substituting reused K6 shots or cheap procedural animation for genuinely new cinema-quality animation. Adapt proven open code and weights to independent CPU inference without remote generation quotas.

## What was built and tested now
- Original single-file Python orchestration source `starwood_learned.py` plus Windows one-click setup (upstream CPU binary and three weight files), Linux source build, original STARWOOD v3 cast/story, unit tests, license, readme.
- 84 **unique new-shot prompts** compiled from the user's original STARWOOD Episode 1 v3, cast lock, identity and provenance hashes, six-byte Q4 director control per shot, no arbitrary fixed 2-character limit.
- Real pretrained-video-generation architecture: **Wan2.1 T2V 1.3B Q4 GGUF** driven through **stable-diffusion.cpp** (MIT), all inference intended to be local. MODEL generation is not a collage, optical-flow interpolator or API call.
- Public download sources (MIT/Apache-2.0): https://github.com/leejet/stable-diffusion.cpp ; https://huggingface.co/off-grid-ai/Wan2.1-T2V-1.3B-GGUF ; https://huggingface.co/off-grid-ai/Video-Companions-GGUF . Preserve upstream license notices.
- The actual CPU Windows backend release ZIP was downloaded and inspected on a connected machine: ~18,080,575 bytes and SHA256 `f0f76c8176a90cafc431ca7d5049cbe8c5cea61ca7cb92b78e07361d41d8fb21`; contains sd-cli.exe plus needed DLLs. Installer pins exactly this artifact.
- All three pretrained weight file endpoints were reachable and exact sizes verified: 816,061,024 B generation DiT; 3,655,145,312 B UMT5 XXL encoder; 253,815,318 B VAE (~4.73GB total). Installation checks SHA256 of model weights before inference.
- 10/10 offline tests passed. Freshly extracted release ZIP passed script smoke tests. Scene 14 (Tiko hedgehog introduced beside Luma and Pip) has a unique original prompt, no old film inputs.
- Actual local inference attempt **returned code 2: BLOCKED_MISSING_LOCAL_MODEL_OR_BACKEND**. The current ChatGPT execution host has 5.8GiB system RAM, no locally installed GGUF weights/compiled sd-cli and no direct outbound network. Another available ARM VM has ~8GiB RAM but no compiler toolchain installed; apt failed under namespace sandbox restrictions. **No new AI video was created, no output claimed**.
- Output is in conversation artifact `STARWOOD_LEARNED_GENERATOR_CPU_V1_2026-10-28.zip`; it is NOT committed as source to this GitHub repo. This document is the repository receipt.

## Current capability boundaries
Code and model selection are real, but end-to-end learned-video generation on weak CPU is NOT verified. Text encoder alone uses ~3.65GB in weight storage; activations/runtime add memory pressure. No benchmark showing quality equal to K6, no new full character acting, no verified synchronized voice, and no three seven-minute episodes/day. CPU local inference has no arbitrary provider quota, but compute, memory and power still limit daily throughput.

## Next evidence gate
Provision local model files and C++ binary with integrity verification in hardware permitting 8GiB+ RAM (16GiB preferred); produce a genuinely new 9/17/33-frame STARWOOD shot from the trained network; inspect appearance, dynamic action and actor identities and compare to K6. Until then the pipeline must not invent an MP4 or label a planned shot as complete.
