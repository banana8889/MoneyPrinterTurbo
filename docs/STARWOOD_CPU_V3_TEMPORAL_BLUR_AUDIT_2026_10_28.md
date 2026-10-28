# STARWOOD Learned CPU V3 — temporal-degradation gate (2026-10-28)

The user noticed that the beginning of our truly neural Wan2.1 CPU test looks sharper than its ending. We directly measured **each of the nine real video frames** of both runs, rather than inferring quality from first/last snapshots.

## Real output evidence
- Prior 6-step 320x192/9f CPU run (0.75s): detected edge fraction at first/last frame **11.26% / 1.83%**. Average first-three to last-three edge retention **0.1984**, gradient retention **0.6022**.
- Prior 18-step 448x256/9f CPU run (0.75s): detected edge fraction first/last **5.07% / 1.14%**. First-three to last-three edge retention **0.2703**, gradient retention **0.7444**.
- Thus **both are flagged REJECT_TEMPORAL_SHARPNESS_LOSS** by the new fixed diagnostic. Motion/content/encoding can influence a gradient metric; it does **not** prove the VAE is the unique root cause.
- The Wan2.1 T2V causal 3D VAE has temporal factor 4 and a separately coded first frame (length 4n+1). A relevant independent issue reports high quality of first decoded frame followed by distortion: https://github.com/Wan-Video/Wan2.1/issues/393 . This is a debugging hypothesis, not a fixed upstream bug with a proven resolution.
- Official docs: https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/wan.md

## New original code (in current conversation downloadable artifact only)
`STARWOOD_LEARNED_CPU_V3_TEMPORAL_GATE_2026-10-28.zip` includes:
- V2's local Wan1.3B Q4 inference app now with `starwood_temporal_qa.py` automatic real-MP4 QA. Individual frame edge density, gradient and adjacent delta measured using ffmpeg; false positives under scene cuts marked inconclusive rather than approved.
- Original AB plan `starwood_ab_temporal.py`: baseline 160x160 VAE tiling; one-factor `--vae-conv-direct` on; one-factor larger 256x256 VAE tile. All other conditions fixed (model, seed, shot, prompt, steps, resolution). **These A/B neural inference runs have NOT been executed**, and their effect on quality remains unproven.
- Inference config SHA now includes CFG, VAE tiling and convolution option, preventing incorrect reuse of cached output. Prior samples are not approved merely because they pass technical decoding.
- 23/23 local CPU/offline unit+regression tests passed. One synthetic video intentionally loses temporal sharpness and is rejected; it is explicitly not new model-generated footage.
- 84 storyboard shots and original STARWOOD children's cast preserved. No zombies/horror crossover.
- All code and README remain in the ZIP linked in conversation, **NOT uploaded as source files to this GitHub branch**.
- The current container lacks installed model weights, so it cannot rerun neural inference right now. No new AI-generated frames were claimed in this turn.

## Objective status
Model running on CPU: PROVED in previous run. High-quality extended video on CPU: NOT PROVED. Quality defect detected: YES. Defect fixed by decoder option: NOT YET TESTED. Three seven-minute episodes per day: NOT PROVED. Do not distribute the failed video as a completed STARWOOD scene.

Prior real samples:
- https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_TIKO_WAN21_Q4_TRUE_CPU_9FRAMES_2026-10-28.mp4
- https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_TIKO_WAN21_Q4_TRUE_CPU_448_18STEPS_2026-10-28.mp4
