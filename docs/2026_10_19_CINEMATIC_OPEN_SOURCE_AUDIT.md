# MoneyPrinterTurbo — 2026-10-19 GitHub cinematic production audit

Status: research and verified code integration only; no cinematic release, no schedules, no paid tools.

## Decision
Building a film-quality episodic studio requires original consistent rigged characters, directed motion, expressive facial acting, naturally performed dialogue, physically believable scene design, controlled lighting and sound, and real independent end-to-end film review. No video model alone maintains long-form character continuity. We screened 32 distinct repositories/candidates; this is a bounded survey, not literally all of GitHub.

## Selected permanent foundation
- Blender (https://github.com/blender/blender): primary rigged character performance, scene design and final feature renderer. GPL program; check character/asset licenses separately.
- Blender Studio pipeline (https://projects.blender.org/studio/blender-studio-tools): shot/asset management, professional workflow. The official upstream is Blender Projects, NOT an official GitHub mirror; production-tested but not yet installed into our project.
- Godot (https://github.com/godotengine/godot): inexpensive realtime previs and FACS/animation technical tests already verified in this project. NOT final film art quality.
- OpenColorIO (https://github.com/AcademySoftwareFoundation/OpenColorIO), OpenImageDenoise (https://github.com/RenderKit/oidn), FFmpeg (https://github.com/FFmpeg/FFmpeg): image consistency, denoising, mastering; film color and mix remain unverified.
- Rhubarb (https://github.com/DanielSWolf/rhubarb-lip-sync): offline licensed actor lip-timing; prior 339 real phoneme cues already verified.

## New first-choice upgrades after research
- Original character modeling: TRELLIS.2 (https://github.com/microsoft/TRELLIS.2), MIT core but separate third-party dependency rights and approximately 24GB GPU. Screened; cannot run on verified current CPU-only setup.
- Automatic rigging: SkinTokens (https://github.com/VAST-AI-Research/SkinTokens), MIT code and MIT official model checkpoints, approximately 14GB VRAM; not run on current hardware. Fallback UniRig (https://github.com/VAST-AI-Research/UniRig) ~8GB.
- Acting/motion: MMPose (https://github.com/open-mmlab/mmpose), licensed pose estimation with original recordings and expert retarget/keyframe polish, not whole-character acting by itself.
- Face articulation: Tripo Face Rig (https://github.com/mdj128/facial-animation) and real 3D FACS blendshape controls; unlike flat mouth flapping, the model requires an artist-prepared anatomical head.
- Distinct voices: Chatterbox Multilingual V3 (https://github.com/resemble-ai/chatterbox) is preferred candidate for high-quality local dialogue. Official GitHub and ResembleAI model MIT; still needs 3 authorized distinct reference recordings and actual listening review. Qwen3-TTS 1.7B Base (https://github.com/QwenLM/Qwen3-TTS) is an Apache2 backup, CosyVoice 3 (https://github.com/QwenAudio/CosyVoice) another candidate.
- Optional cinematic video embellishment: Wan2.2 (https://github.com/Wan-Video/Wan2.2) says Apache-2.0 official family but needs powerful GPU and identity verification before adding to character-bearing shots.

## Conditional/excluded candidates
- LTX-2.5 (https://github.com/Lightricks/LTX-2): August 2026 custom community license, commercial paid-license requirement at >=USD10m annual revenue plus other restrictions; do not use as an unconditionally free commercial asset.
- HunyuanVideo 1.5 (https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5) / Hunyuan3D 2.1 (https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1): Tencent community territory/commercial restrictions and significant GPU needs; not default.
- GVHMR (https://github.com/zju3dv/GVHMR): research/nonprofit license; excluded from monetized production.
- MuseTalk (https://github.com/TMElyralab/MuseTalk), LivePortrait (https://github.com/KwaiVGI/LivePortrait): possible face-based supplements; 2D talking-head videos are NOT cinematic whole-body 3D animation.
- Real-ESRGAN (https://github.com/xinntao/Real-ESRGAN), REAL Video Enhancer (https://github.com/sovcha/real-video-enhancer) and Practical-RIFE (https://github.com/hzwer/Practical-RIFE): improve existing good footage, cannot create missing motion and may cause frame artifacts.
- ACE-Step (https://github.com/ACE-Step/ACE-Step): original music candidate; separate checkpoint/output/license review.
- Kitsu (https://github.com/cgwire/kitsu), Flamenco (https://flamenco.blender.org), OpenUSD (https://github.com/PixarAnimationStudios/OpenUSD): studio-scale coordination and interchange later, not the main quality bottleneck.

## IMPLEMENTED in MoneyPrinterTurbo this round
1. studio/free_toolchain.py: offline machine-readable 32-tool registry; Python CLI inventory/select/diagnose; commercial and checkpoint restrictions, GPU floor checks, feature ranking, integration-status tags. No paid API.
2. studio/chatterbox_v3_cast.py: local MIT Chatterbox V3 option, three independently licensed voice references required, separate actor waveforms, repeatable output with real timing, compatibility with existing Rhubarb, no artificial film approval. Backend not run because authorized original voice references and capable model runtime have not been verified.
3. studio/film_shot_planner.py: compiles seven-act, 84-line original Episode One screenplay into camera shots, motivated blocking/eyelines, chronological act locations, actor identity requirements and estimated time, without falsely claiming to have recorded or rendered these shots.
4. Unit tests and on-change (NOT scheduled) GitHub Actions: test_free_toolchain.py, test_chatterbox_v3_cast.py, test_film_shot_planner.py, cinematic-toolchain-audit.yml. Tests actively reject unapproved voice cloning, fake GPU readiness, invalid act/story coverage and excessive cutting.

## HARD release blockers
- Original hero-grade sculpted fox and rabbit models and rigged independent character looks; reference humans in prior proofs are unacceptable.
- Subtle weighted physical character acting, eyebrow/eye/lip performance, camera and world continuity, commercial asset and voice rights.
- Human-reviewed expressive dialogue and score, actual 4–8 minute professionally mastered 1080p+ footage, strong cliffhanger and independent cinematic critique.
- No verified suitable GPU available in the current execution environment; GPU-specific tools are only screened, not installed/benchmarked.

Policy: user does not want partial video previews or scheduling; do not show any unfinished clip or start reminders. No payments, subscriptions, or publishing. Preserve existing functions, leave main branch unchanged and PR as draft. The full tool registry linked above is the detailed source of truth; code/license/weight permissions must be reevaluated for commercial releases.