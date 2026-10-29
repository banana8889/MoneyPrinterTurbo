# STARWOOD Learned CPU 1.2 — persistent backend / QA (2026-10-29)

## Scope
User wants original children's STARWOOD with Luma/Pip/Tiko and new characters. Do **not** substitute zombie/RIVER ZERO content or reused Kandinsky footage for a genuinely new scene. K6 original ~15 seconds remains the visual quality bar.

## Concrete work now
- Diagnosed prior 448×256 18-step experiment was LOST on an ephemeral Floot worker reset before saving; it is **not evidence of success**.
- On a fresh 8GiB RAM / four-core ARM64 worker installed Git and CMake, cloned upstream `stable-diffusion.cpp`, recompiled the actual CPU Wan inference backend at source commit `77b72a2efed78f55de26892c7e909cee001e8b83`.
- CPU binary built (41,217,336 bytes), `--help` confirmed Wan video flags and persistent cloud storage upload re-downloaded and SHA256 **verified**: `3ae77b4d902fc94cfd70409625ac13165a7ae09c129fc14f40143515387ee4cc`.
- Public download for the pinned Linux ARM64 binary (MIT upstream): https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/starwood_sdcli_arm64_cpu_77b72a2e_2026-10-29
- All three model files downloaded and SHA256 verified against real Hugging Face LFS oids (not Xet ETags):
  - WAN 1.3B Q4 816061024 B: `82788a4a3ce6e206edd3e8e5fe512b2a75344a3d272d80f07cd4e48b60b7aaf7`
  - UMT5XXL Q4 3655145312 B: `17cf97a5bbbc60a646d6105b832b6f657ce904a8a1ad970e4b59df0c67584a40`
  - Wan VAE 253815318 B: `2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b`
- Original `starwood_learned.py` revised to **1.2**: fixes unsafe cache reuse when CFG/steps/profile changes, validates exact model frame count and dimensions; adds `cpu_cinema_test` (448×256, 9 frames, 18 steps).
- Standalone original CPU technical visual diagnostic (`starwood_quality_gate.py`) measures Laplacian, temporal pixel difference, luminance and refuses automatic artistic quality approval. Sharpness alone was observed to be an **unreliable substitute** for human evaluation because pixel noise may inflate it.
- New Linux ARM64 bootstrap with verified downloaded pretrained weights and resumable ranges. 22/22 tests passed including 15 regression tests.
- Downloadable ZIP of genuine Python source, tests and docs delivered in ChatGPT: `STARWOOD_LEARNED_CPU_V1_2_PERSISTENT_QA_2026-10-29.zip`.

## Ongoing evidence gate
A NEW genuine local CPU inference for **original Tiko workshop scene** at 448×256, nine frames, 18 Euler steps, is running on the current Floot ARM64 worker and is not yet complete at this receipt. Previous verified 320×192 nine-frame six-step test video exists, but LOOKED VERY BLURRY AND FAILED ARTISTIC STANDARD:
https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_TIKO_FRESH_NEURAL_WAN21_CPU_2026-10-28.mp4

Reference, still unbeaten:
https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4

**Do not claim** full episode, artistically approved film, background persistence, 3 episodes/day or Kandinsky-grade quality yet. No social publishing. All inference is local CPU; initial one-time binary/weights download uses HTTPS but no hosted inference.
