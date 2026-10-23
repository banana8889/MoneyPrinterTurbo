# CINEMATIC QUALITY STANDARD — MoneyPrinterTurbo
Edition 2026-10-15 · Free-first, evidence-based · Status: **TARGET ONLY; NO CINEMATIC RELEASE VERIFIED**

## Promise / interpretation
User requests quality **at least comparable to a top-tier Steven Spielberg-directed film**. This is an *aspiration for storytelling and production quality*, not a claim that software or generated footage can equal that standard, and not an instruction to imitate any protected work, existing character, film, music or identifiable actor's voice. Our studio must strive for coherent storytelling, expressive acting, nuanced cinematography, sophisticated lighting, and emotionally persuasive sound design. Do not render a low-grade proof and label it cinematic.

## Real film-production approach
Story and direction → character / world design → final rigged 3D characters → animatic → key poses and motion capture / hand-keyed refinement → facial performance and expressive authorized voices → Blender character animation & lighting → sound score and mix → beauty render + color pipeline → edited 16:9 episode and 9:16 marketing clips → reviewer gate → optional permitted publication → genuine audience metrics.

A single text-to-video generative model, slideshow, lip-only model, or third-party rigged demo **cannot substitute** for genuine character animation, scene continuity, story direction and final rendering.

## Verified GitHub tool shortlist (2026-10-15)
Paths are repository homepages. LICENSE here means **software code** unless weights also separately checked; art and voice rights must be checked too.

| Production function | Candidate / GitHub | Verified benefit | Policy & caveat | Adoption |
|---|---|---|---|---|
| Master 3D stage, character acting, lighting, Cycles rendering, editing | Blender https://github.com/blender/blender | Free complete 3D pipeline; GPLv3 source | Character design, acting and expensive rendering require real work / hardware | **PRIMARY** |
| Production-tested methodology | Blender Studio https://studio.blender.org/tools/ | Free/open Blender-centered pipeline developed through open movies | Studio documentation / tools are not a film generator, CloudRig official distribution is not GitHub-first | **PRODUCTION PROCESS** |
| AI-generated 3D skeletons and skinning | SkinTokens https://github.com/VAST-AI-Research/SkinTokens | Successor to UniRig; repo MIT; official docs demand NVIDIA GPU >=14GB VRAM | Check checkpoint license and deform quality on original characters; does not produce acting | **PREFERRED EXPERIMENT if capable GPU** |
| Lighter automatic rigging fallback | UniRig https://github.com/VAST-AI-Research/UniRig | Repo MIT; official docs require CUDA >=8GB for generation | Check weights and model compatibility, manually correct feet/eyes/faces | **FALLBACK** |
| Motion keypoint extraction / performance references | MMPose https://github.com/open-mmlab/mmpose | Apache-2.0 code, 2D/3D pose estimation | Not itself an animation rig/retargeting tool; capture consent and output/dependency licenses matter | **RESEARCH / PROTOTYPE** |
| Do not adopt for monetized motion pipeline | GVHMR https://github.com/zju3dv/GVHMR | Effective 3D recovery research | Repository LICENSE explicitly says research, education and nonprofit only, no commercial use without agreement | **EXCLUDED** |
| Offline/local multi-character speech studio | Voicebox https://github.com/jamiepine/voicebox | MIT; multi-voice story editor; supports Chatterbox, Qwen, Kokoro etc | Validate model/voice licenses separately and actual acting/naturalness | **PREFERRED VOICE ORCHESTRATOR** |
| Expressive local TTS | Chatterbox https://github.com/resemble-ai/chatterbox | MIT code, expressive speech model | Human QA: timing, emphasis, laughter, line continuity, no unlicensed voice cloning | **VOICE ENGINE CANDIDATE** |
| Free facial lip markers | Rhubarb Lip Sync https://github.com/DanielSWolf/rhubarb-lip-sync | Maps audio to phonemes/mouth cues | Works as helper to facial rig, not emotional acting | **OPTIONAL** |
| Cinematic color | OpenColorIO https://github.com/AcademySoftwareFoundation/OpenColorIO | BSD-3-Clause code; motion-picture color management / VFX | Use ACES/appropriate OCIO view transforms; consistency across shots | **FINISHING** |
| Denoising | OpenImageDenoise https://github.com/RenderKit/oidn | CPU/GPU rendering denoise in open-source film stack | Verify exact current repo/licenses and technical compatibility; Blender may bundle OIDN | **RENDER FINISHING** |
| Multi-asset scene interchange | OpenUSD https://github.com/PixarAnimationStudios/OpenUSD | Versioned scene composition / scene interchange standard | Adds complexity if one-machine Blender files are sufficient; defer until scale warrants | **OPTIONAL LATER** |
| Source footage based image/video generation | Wan 2.2 https://github.com/Wan-Video/Wan2.2 | Open weights and model code for optional visual augmentations | Hardware/weights licensing/identity drift: avoid using it for recurring character core shots | **OPTIONAL AFTER RIGGED BASE** |
| Node orchestrator | ComfyUI https://github.com/Comfy-Org/ComfyUI | Local workflows | Force offline / paid-partner nodes disabled; image/video models require GPU and weights licenses | **OPTIONAL** |

### New "missing paid capability" workflow
1. Search currently maintained GitHub alternatives before external spending.
2. Choose 2–3 concrete candidate repos; inspect exact release, LICENSE, model-weights license, quality demos, GPU/VRAM and required assets.
3. Pilot with a tiny **same-script same-shot** workload, local only, no paid APIs. Compare cost, human perceptual rating, subject continuity, motion mechanics, lip/voice quality.
4. Promote only if the result improves real cinematic quality. If no suitable local GPU, flag the **hardware blocker**; never secretly substitute a paid provider or claim it ran.
5. Log chosen repo and exact commit/hash in the tool manifest upon integration. Research is not integration.

## Release quality gates (pass/fail and evidence)
Each shot should be reviewed **at normal playback speed**, not assessed from still images.

- **Story & direction:** original hook, clear objectives/stakes, cause/effect, character-specific choices, emotional payoff, fair cliffhanger. Human-relevant coherent 5–8-minute episode; no unnecessary padding or dark/manipulative traps for kids.
- **Distinct original characters:** clean silhouette, stable proportions, consistent clothing/materials/eyes/voice 100% of shots, controlled changes only for in-story reasons.
- **Animation & acting:** real articulating rigs (pelvis/spine/head/limbs/eyes), believable weight, foot-ground contact, gesture anticipation/follow-through, interaction and eye-line continuity; no slides/AI morphs masquerading as walking.
- **Facial acting and speech:** distinct authorized voices, convincing emotions and pauses; semantic/phoneme synchronization and face/eyes/brows/blinks; no metallic voice.
- **Cinematography:** intentional shot size, staging, motivated camera, depth, blocking, continuity, consistent visual grammar; no random zooms to hide lack of motion.
- **Lighting and finishing:** controlled reflections/shadow contact, image coherence, consistent scene atmosphere, final grade, no jitter or flicker, music/SFX/dialogue mix with intelligibility and no clipping.
- **Technical delivery:** aspire to 1920×1080 / 24fps or better, H.264/AAC viewing copy, inspect fps, duration, black frames, render crashes, clipping, A/V drift.
- **Independent review:** compare at least one exemplar sequence against comparable original/licensed family animated shorts for specific rubrics, obtain a reviewer judgment and fix major deficiencies, not arbitrary "Spielberg%" numbers.
- **Monetization compliance:** child-directed content classification and privacy; copyrighted characters/voice/music/graphics excluded; no false claims of views, success or revenue.

## Stop gates, not endless tests
A) 3-character visual reference / look & voice casting sample (non-publishable).
B) 10–15s **continuous rigged** performance with feet, eyes and meaningful reaction, no static frames.
C) 60–90s dialogue + staged story + full facial acting + score.
D) One 5–8-minute episode, coherent edit, scored review gate; then public trailer.
E) Publish *only after owner authorizes* account access, measure real retention and iterate.

Every gate produces **viewable video and plain-Hebrew outcome**, not just code; only essential tests to block poor output. No batch growth until step D passes.

## Implementation reality as of 2026-10-15
- Previous 640×360 12fps concept: **FAILED cinematic standard**.
- A public Khronos test character with existing skeletal walk/run actions has been identified and an interactive HTML motion explorer was created. That is a *technical* rig demo, not Luma/Pip original acting.
- No final original character models, high-quality voice performances or full movie-quality episode verified.
- No dedicated local NVIDIA GPU with suitable VRAM verified in the current working environment. SkinTokens >=14GB and UniRig >=8GB CUDA requirements thus currently unresolved.
- This document improves tool selection and release discipline; it **does not certify a film**.
