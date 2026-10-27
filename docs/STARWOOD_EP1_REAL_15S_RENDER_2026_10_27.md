# STARWOOD Episode 1 — genuine third-scene render and 15s cut (2026-10-27)

## Actual, verified result
- 3 original Kandinsky 6 Lite generated shots, roughly 5.06 seconds each, 864×480, 24 fps, H.264 video + AAC audio.
- **[Play latest three-scene combined MP4](https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4)**
- This run verified the returned media: HTTP 200, `video/mp4`, **2,023,848 bytes**, SHA-256 `d000024f06f4e2fd2335890a9a5422d099a39a11b485d26fbd881f14acc9cbf4`.
- **[Third shot only](https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_Scene03_2026-10-27.mp4)** — actual image-conditioned Kandinsky 6 Lite inference from last real frame of shot 2. Model reported 121 frames at 24 FPS and about 75 seconds on a free GPU. Third shot contains a small floating golden lantern; same fox Luma with turquoise scarf and rabbit Pip.
- Shot 3 FFmpeg checks: 20 grayscale frames sampled at 4 fps, mean luma 62.198/255, average adjacent frame difference 13.898/255, static fraction 0 at threshold 0.6.
- Combined result was assembled and decoded with FFmpeg without an error.
- The separate free-plan STARWOOD screening project's default video was updated to this new 15s cut. Its page typecheck passed. Existing wallet project and main branch unchanged.
- **Not a full episode.** The episode script has 7 dramatic acts; no additional shots were rendered or approved here.
- Attempted generation of shot 4 with the final frame of shot 3 as reference. The free ZeroGPU service rejected it: `135s requested vs. 103s left`; daily limit, no fourth shot generated. This is external quota, not a pipeline success or inference error in scene 4.
- No paid video service or purchased compute was used. No ongoing job/automation was created.

## Quality gate
The saved three-scene clip is an actual AI render, not a slide show. It is still technical/creative progress only: identity continuity over full episode, correct synced spoken dialogue, full soundtrack, and feature-film-grade acting remain unverified. Do not describe this as a completed seven-minute episode.

## Production continuation
Next story event: mysterious engraved symbols inside the lantern, including a star, a tree and two paw prints. Start from the actual last frame of third scene; only append new media after real inference and visual QA. Do not silently reuse stale frames or pad a video to claim target duration.
