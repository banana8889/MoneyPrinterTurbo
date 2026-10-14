# Free-First Production Policy — MoneyPrinterTurbo Episodic Studio

Updated: 2026-10-14

## Mission
Produce a recurring original 3D animated children/family series with cinematic, colorful consistent characters, believable expressive voices, continuity between episodes, engaging but age-appropriate cliffhangers, and full-length episodes. Preserve existing MoneyPrinterTurbo functions.

## Non-negotiable cost gate
- Before proposing or integrating any paid API, video model, TTS, voice cloning, music, image, hosting, editing, rendering, scheduling, publishing, or analytics provider, inspect current free/local alternatives (prefer maintained official GitHub repositories).
- Default to no paid provider, no subscriptions, no paid API credentials, no premium cloud compute, and no hidden remote calls.
- Never infer "GitHub-hosted" equals free to operate. Verify runtime/GPU needs and *separately* the code, weights, assets, datasets and commercial-use licenses.
- Compare alternatives on measured fidelity, character/voice consistency, temporal coherence, throughput, local hardware feasibility, costs including electricity, provenance and commercial terms. A free tool is not automatically better.
- Do not silently swap to paid nodes if the local model fails; fail with a specific hardware/model blocker. Monetary actions need explicit user authorization.
- Restrict any production storyboard/character/voice reference to original or licensed inputs. Never imitate identifiable people's voices without permission.
- Publish only via channels the user explicitly connects and authorizes, observing any kid-directed content flags and platform policies. Never claim analytics or revenue without actual data.

## Verified free-first candidates

| Function | First candidate | Repo | Licensing / practical notes |
| --- | --- | --- | --- |
| Fully consistent recurring 3D characters/scenes | Blender | https://github.com/blender/blender | GPL-3; use owned/commercially licensed assets; traditional deterministic 3D rendering |
| Video enhancement / animation | Wan 2.2 TI2V-5B & Wan2.2-Animate | https://github.com/Wan-Video/Wan2.2 | Apache-2.0 repo; 5B designed for consumer RTX 4090-class hardware; inspect each weight license |
| Local image/video orchestration | ComfyUI | https://github.com/Comfy-Org/ComfyUI | GPL-3; use --offline and disable paid Partner Nodes |
| Original concept art / character sheets | Z-Image family | https://github.com/Tongyi-MAI/Z-Image | Apache-2.0 repo; Z-Image-Turbo docs mention 16GB GPU |
| Human-like expressive narration and dialogue | Chatterbox Multilingual | https://github.com/resemble-ai/chatterbox | MIT code; supports Hebrew and English, local inference and emotion controls; verify voice references |
| Lighter voice fallback | Kokoro | https://github.com/hexgrad/kokoro | Apache-2.0; verify model checkpoints; different voice quality/hardware trade-off |
| Deterministic 3D mouth shapes from recorded speech | Rhubarb Lip Sync | https://github.com/DanielSWolf/rhubarb-lip-sync | MIT; facial blend-shapes or rig animation in Blender |
| Optional face-based AI animation | Wan Animate / MuseTalk | https://github.com/Wan-Video/Wan2.2 and https://github.com/TMElyralab/MuseTalk | Optional, verify model dependencies/weights and consistency |
| Original instrumental soundtrack | ACE-Step | https://github.com/ace-step/ACE-Step | Apache-2.0 code, independently verify exact model weights/assets before commercial output |
| Local story generation / episodic memory | Ollama / llama.cpp | https://github.com/ollama/ollama and https://github.com/ggml-org/llama.cpp | Check selected LLM weights license (not inherited from the runner) |
| Rendering / edit / muxing | FFmpeg + existing MoneyPrinterTurbo | https://github.com/FFmpeg/FFmpeg and this repository | Already integrated media pipeline, check codec-specific licenses |

## Not automatically free for unrestricted monetization
- LTX-2/LTX-2.x: https://github.com/Lightricks/LTX-2 — special community license, paid commercial license in some revenue circumstances; do not treat as Apache/MIT.
- HunyuanVideo-1.5: https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5 — territory and commercial terms; check before any use.
- FLUX [dev]: non-commercial model weights; do not use for monetized content by default.
- ComfyUI paid partner nodes and hosted cloud endpoints must remain disabled by default.
- Cloud GPU, electricity, hardware, music/asset purchases, hosting, and publishing integrations may incur costs independently of source-code licenses.

## Recommended staged architecture
1. **Story bible:** season arc, 3 distinct named original characters, relationships, goals, weaknesses, episode outline, scene requirements, attention/age appropriateness.
2. **Asset bible:** one canonical Blender rig per character; palette, height, shape keys, clothing, scale, continuity references; no prompt-only identity.
3. **Voices:** dedicated licensed Chatterbox voice for each character, expressive delivery, stable audio tracks, voice QA, Rhubarb-driven mouth animation.
4. **Rendering:** Blender makes all deterministic core story shots; AI image/video is optional for complex scenery/transitions and cannot be the only continuity mechanism.
5. **Assembly:** reuse MoneyPrinterTurbo/FFmpeg for sound, music, cuts, subtitles, and mastering, export actual playable 16:9 episodes plus 9:16 trailers.
6. **Verification:** first 60-90-second scene, then 4-8-minute episode 1; require stable model, continuous story, natural voice, synced lips, clear narrative, rights clearance.
7. **Feedback:** after user approves a publishing connection, record *real* views/retention/return rate and adjust next scripts. Do not invent retention success or virality.

## Environment limitations observed 2026-10-14
- Working environment has ffmpeg and Python/Pillow but no detected Blender binary or NVIDIA GPU utility; GPU availability not proven.
- High-quality local diffusion is **not proven runnable** in this environment. Do not imply server-side continuous local rendering has been deployed.
- Full-length 3D film production has NOT been verified; previous simplistic local shorts are not a finished 3D episodic series.

## Next operational gate
Inspect actual available GPU/VRAM and whether Blender can run on the selected machine, then create an owned 3D character rig and original expressive speech. Render and inspect one 60-90s coherent story scene before batch production. Explicitly reject paid fallbacks.
