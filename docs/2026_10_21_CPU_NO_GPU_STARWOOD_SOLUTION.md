# Starwood — practical no-GPU production path (21 October 2026)

## The actual solution and proof

A verified **CPU-only, no paid API, no subscription** pipeline exists now in the development branch. No scheduled tasks, automatic uploads to streaming sites, cryptocurrency mining or paid external compute are needed.

- [vsim Film3D](https://github.com/kunalkushwaha/vsim) is an MIT source renderer supporting a non-image fake but real **skinned 3D fox and rabbit, skeletal locomotion, camera/lighting, deterministic film documents**, and an optional Blender Cycles higher-quality render.
- Its precise reference commit is \`3f97faf85e46d2f9a122b0a8b8d3ccc0af598f91\`. Pin this: no unchecked floating dependency or secretly changed design.
- The public GitHub Actions repository uses standard Ubuntu CPU runners, which [GitHub says are free for public repositories](https://docs.github.com/en/actions/reference/runners/github-hosted-runners). Standard Linux runners have 4 CPUs and 16GB RAM; this is **not** an unlimited guarantee of GPU, throughput or storage.
- [studio/vsim_cpu_episode.py](../studio/vsim_cpu_episode.py) compiles all seven acts from the already-written original 84-line Starwood episode into independently renderable native Film3D documents. Actual poses/3D locomotion and scene props, not slides.
- [test_vsim_cpu_episode.py](../test/services/test_vsim_cpu_episode.py) validates separate identities, movement clips, seven-act continuity, and the absence of low-quality auto-robotic espeak narration. When a voice receipt is provided, the compiler uses actual timing and refuses speaker/line mismatches.
- [starwood-cpu-3d.yml](../.github/workflows/starwood-cpu-3d.yml) installs the *pinned* free engine, FFmpeg, checks native scene schemas, renders actual 3D frames and enforces the moving-image QC. It is triggered by code change or a one-off manual request — **not a scheduled job**.

## Verified milestones, not marketing statements

1. [Film3D native schema run 39576944868](https://github.com/banana8889/MoneyPrinterTurbo/actions/runs/39576944868) initially failed **only** strict JavaScript floating-point equality for adjacent camera timestamps; fixed by binary-exact 1/16-second timecodes.
2. [First real CPU movie run 39577117971](https://github.com/banana8889/MoneyPrinterTurbo/actions/runs/39577117971) **rendered 108 actual frames** (960x540, 24 fps, 4.5 seconds, 54.3 seconds wall-time), but **FAILED** pixel-motion gate. We rejected it.
3. [Next corrected CPU movie 39577559592](https://github.com/banana8889/MoneyPrinterTurbo/actions/runs/39577559592) **SUCCEEDED** after actual skeletal actor motion increased: 108 frames, 960x540, 24 fps, about 90.2 seconds of CPU runner time, sustained grayscale pixel-change=0.5172, fraction above gate 0.50. This is real moving 3D at zero CUDA use. It passed the *technical* frame-motion gate.
4. We **privately reviewed** internal frames. Artistic quality remains **REJECTED**: native fox/rabbit models are not original hero-quality film characters, visible proportions/scales are too small, night lighting too dark, camera too far, and giant title/caption overlays look amateurish. Next commit hides these overlays, changes night to lit dusk for early acts, and makes actors easier to see. Actual QA must be rerun; no release claimed before visual inspection.
5. [Full episode voice run 39403889703](https://github.com/banana8889/MoneyPrinterTurbo/actions/runs/39403889703) already **SUCCEEDED**: 84 original TTS lines / 3 cast voices / **351.3492 seconds** of synthetic spoken content, and **2,250** total Rhubarb mouth-cue intervals. Natural acting quality was not approved and these are not feature-ready performances.

## The real remaining production gap

This solution **removes the compute blocker for reproducible technical 3D animation**, but it does not itself meet a feature-film look or original intellectual-property design.

Remaining film-quality gates:
- Truly original high-quality anthropomorphic Luma & Pip character designs, professional anatomy and performance rigs. A CC-BY fox glTF plus MIT procedural rabbit serve only as **technical reference actors**, not final visual identity or final licensed IP.
- Expressive dialogue with three original/consented commercially cleared voices, independent human audition, accurate lip-sync, nuanced face and hands, and intentional motion and character psychology.
- Shot-specific artistic assets and lighting, continuity, expressive camera direction, real staged interactions, score and mixing.
- All seven rendered acts (4–8 min in total) and one professionally mastered 16:9 1080p+ video with 24fps and completed soundtrack, review of both spoken plot and visible action, and independent aesthetic critique.
- GPU-intensive SCAIL-2/Wan-Animate-2 can still add high-quality motion if access to a properly licensed 8GB+ GPU quantized setup becomes real. Never assume that a Colab/Kaggle free quota is permanent or that GitHub standard runners have GPUs.

## Licensing and costs

- vsim core and generated rabbit: MIT source. GLTF sample Fox by PixelMannen CC0 but rig/animations by tomkranis and conversion by Asobo/scurest **CC BY 4.0 credit required**. Detailed original credits: https://github.com/kunalkushwaha/vsim/blob/main/packages/assets/library/CREDITS.md
- FFmpeg build license/encoder terms still apply for redistribution. No paid APIs, no cloud GPUs provisioned.
- Rigs from Blender Studio such as professional [Bunny v2](https://studio.blender.org/characters/5d4046ba8bcf3aae3bb20ff7/v2/) and [Rain v3](https://studio.blender.org/characters/rain/v3/) are potentially useful **CC BY** foundations but require version-specific evaluation, original redesign, proper credits and access verification; never claim installed or original creation from their unmodified models.
- No schedule, no background promises, no unfinished video shown to the user, and no release until cinematic quality can be demonstrated.

**Technical progress has evidence; artistic achievement remains unverified.**
