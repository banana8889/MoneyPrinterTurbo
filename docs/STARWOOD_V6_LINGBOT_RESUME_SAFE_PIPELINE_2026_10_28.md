# STARWOOD CPU V6 — improved LingBot local generation pipeline (2026-10-28)

User asks to keep developing truly new children's animation, cinematic quality **better than the original Kandinsky STARWOOD sample**, with no hosted inference quota and without a powerful GPU.

## Current, verified
- Reviewed real V5 Python implementation and upstream stable-diffusion.cpp LingBot official documentation (structured Qwen3VL prompt + -M vid_gen / --llm / -i image conditioning).
- Created original `starwood_learned_v6.py` and a 15-file downloadable ZIP in the ChatGPT conversation: `STARWOOD_LEARNED_CPU_V6_RESUMABLE_AND_LINGBOT_2026-10-28.zip`, SHA-256 `d62b0d56c024968f18b75bf35c096d27bb16451fee7f734dd62c8030abc50b25`. Source file SHA-256 `0d32d49f4a3115c7d9ac3b0082a44d4e7086f4d5b4bae74a89db188ff17d6139`. **This is an artifact in the conversation, NOT source code committed in this repo.**
- Correctly restarted and securely resumed large weight downloads with HTTP Range, Content-Range checks, fsync, exact size and genuine publisher SHA256; kept incomplete .partial for later runs. Avoids expensive full redownloads after interruption.
- Simplified repeated LingBot structured video caption, used structured `universal_negative` without accidentally negating CGI/3D aesthetics; preserved 84 unique STARWOOD action prompts.
- Cache/release identifier now accounts for prompt SHA, negative SHA, model weights, backend binary SHA, image reference, VAE config, shot/cast/story and seed; no false reuse after prompt/weight changes.
- Added verified Windows CPU backend installer using pinned official stable-diffusion.cpp x64 CPU ZIP SHA-256 `f0f76c8176a90cafc431ca7d5049cbe8c5cea61ca7cb92b78e07361d41d8fb21`. ASCII CRLF launcher, Linux clone/build/download shell script.
- 23 existing V5 tests + 13 new V6 offline tests = **36/36 PASS**; real range-resume, corrupt/wrong-range rejection, no fake movie creation, preservation of cast and separate model CLIs. ZIP CRC verified. No new neural inference footage generated here.

## Accuracy and remaining evidence
The earlier Wan2.1 Q4 CPU proof (2 clips, 9 frames, 320x192 and 448x256 respectively) was **real but visually rejected**. LingBot Q4 **has NOT yet completed live inference in this session**: this container has no model weights or sd-cli executable and just 4GiB effective memory, while the separate 8GiB Floot VM has a usage limit and its model files are not persistent. The LingBot package is an experimentally integrated generation route, not proven cinematic quality; **no new STARWOOD high-quality scene or 3 completed episodes/day**.

Original visual target remains Kandinsky 6 Lite 15s STARWOOD baseline:
https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4

Source references:
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/lingbot_video.md
- https://huggingface.co/off-grid-ai/LingBot-Video-Dense-1.3B-GGUF
- https://huggingface.co/off-grid-ai/Video-Companions-GGUF

Development priority: **live new high-quality frame inference and real continuity**, not more stylized CGI/old-video recomposition. Test candidate against original film visually before calling it better. No actual model inference or publication was performed in this latest turn.
