# STARWOOD — Fair, free open-source video benchmark

All tools must receive the same text and reference image (if reference input is supported). Only use locally executed, rights-cleared checkpoints. Never use paid endpoints, hosted inference, subscriptions or API keys.

## Common 5–8 second shot (English)
Create a polished 16:9 cinematic family animation with soft realistic lighting and dense enchanted forest at blue hour. The same two ORIGINAL anthropomorphic animal characters throughout: Luma, a warm-eyed young red fox with natural rounded fur, a turquoise scarf, articulated arms and legs; Pip, a small cream rabbit with gentle violet eyes, plum bow tie and articulated paws. A single unbroken medium two-shot. Luma spots the North Lantern star flickering, smoothly turns her eyes and head to Pip. Pip turns to the sky, takes a physically grounded step, blinks and looks worried. Natural motion with foot contact, subtle acting, refined fur, rounded geometry, stable faces and clothing, clear depth, realistic materials and soft global illumination. Delicate camera dolly and controlled parallax. Avoid low-poly facets, grain, slide motion, still-frame panning, abrupt appearance changes, extra limbs, duplications, on-screen text, logos and watermarks. Use the same two characters, expressions and actions in every candidate.

Optional synchronized English speech, only for systems supporting text+audio generation:
Luma: "Pip. Wake up. The North Lantern is flickering."
Pip: "Stars twinkle, Luma. That's what stars do. Unless... wait."
The two voices must sound distinct and believable, with mouth timing and forest ambience.

## Fixed conditions
- Same prompt, aspect 16:9, seed 20261025 when supported, native maximum feasible resolution, 24 fps target.
- Record exact GitHub code SHA, model checkpoint SHA, code/weights licenses, GPU model, VRAM, wall-clock time, peak memory, output size, and zero paid service calls.
- Create a minimum of three independent generations per model to assess identity and image variability; do not select only the best image as the test outcome.
- Decode outputs with \`python -m studio.open_source_video_compare MODEL=/path/to/file.mp4 --out /tmp/starwood_results\`.
- Judge ACTUAL output blind on acting, original character continuity, smooth fur, focus, story comprehensibility, camera work, speech/audio and remaining defects (0–5 each). Do not convert QA diagnostics into an unsupported "Spielberg-quality" score.
- Do not call an experiment completed merely because syntax, imports, a GitHub Action, a CPU build, or a black-frame control passed.
- Never change main, schedule jobs, spend money or publish rejected/partial videos.

## Eligibility
Kandinsky 6 (MIT program source; checkpoint license must be checked); Wan2.2 TI2V 5B (Apache-2.0 program source, confirm checkpoint); SVI (MIT program source with independent base-model/adapters license verification); Helios (check weights); ChangJi (orchestration engine only, open local backends).
