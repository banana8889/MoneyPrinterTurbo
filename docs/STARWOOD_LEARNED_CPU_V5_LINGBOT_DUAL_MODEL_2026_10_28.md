# STARWOOD Learned CPU V5 — dual-model cinematic generation attempt (2026-10-28)

## Genuine progress in this turn
Original, MIT-licensed *model-control source* and a tested release ZIP were generated in the active ChatGPT conversation:
`STARWOOD_LEARNED_CPU_V5_DUAL_MODEL_2026-10-28.zip` (37,868 bytes; ZIP CRC/integrity verified),
`STARWOOD_LEARNED_CPU_V5.py` (18,891 bytes; SHA-256 `33637019671af9130dd58d8fad8e198bcfe2f54981c3e01f2aa16f2c3779acf2`).
**The actual source code and ZIP are attached to this conversation, not committed to GitHub**; this repository entry is the production receipt.

- NEW candidate model: **LingBot Video Dense 1.3B Q4**, which performs actual trained text-to-video/image-to-video inference with upstream `stable-diffusion.cpp`, rather than recycling old frames. Generator 778,380,448B + Qwen3VL-4B-Instruct Q4 text encoder 2,497,281,664B + Wan2.1 video VAE 253,815,318B = **3,529,477,430 bytes** on disk (RAM requirements higher). All three are separately licensed; Apache-2.0 upstream licensing/notice retained.
- Existing **Wan2.1 T2V 1.3B Q4** retained as controlled alternative/baseline. No claim that LingBot is already better: none has been evaluated on the same new scene yet.
- **Important real bug repaired**: Hugging Face CDN HEAD ETags differ from SHA256 for these mirrored files, and the prior bootstrap incorrectly treated ETags as true file hashes. The bootstrap now retrieves the model publisher's `SHA256SUMS` manifest and checks every full download, writing a local integrity receipt. The actual LingBot hashes were independently checked against publisher sums in the accessible network worker.
- Shot 14 (introducing **Tiko the hedgehog**) now supports **single-subject acting closeup** instead of three crowded protagonists competing for identity; option `--composition full` restores ensemble framing. Prompt has a structured LingBot cinematic scene/camera/actor/action object.
- The same original STARWOOD children's seven-act story and all 84 shots are preserved; no zombie/RIVER ZERO content.
- Inference and performance outputs are strict: missing trained weights or actual executable -> `NOT_RENDERED`; no fake MP4s. Real FFmpeg checks, temporal gradient QA and SHA256 provenance are required before a shot can be reviewed. **23/23 offline unit tests passed**. ZIP contains Linux backend installer, Windows batch launcher, complete source, cast, story and third-party notices.
- Current container (CPU, approximately 6GB RAM) does not have any local model weights and has no direct public network access; backup ARM VM's free build-action quota was exhausted during this session after source/model discovery, before a full LingBot inference. **No new high-quality cinematic video was made** in this turn. Prior actual 9-frame low-quality Wan clips remain available in earlier receipts; zero high-quality self-hosted clips certified.

## Model sources
https://huggingface.co/off-grid-ai/LingBot-Video-Dense-1.3B-GGUF
https://huggingface.co/off-grid-ai/Video-Companions-GGUF
https://github.com/leejet/stable-diffusion.cpp
https://huggingface.co/off-grid-ai/Wan2.1-T2V-1.3B-GGUF

## Target and gate
Quality target: *better than the original three genuine Kandinsky STARWOOD shots*, with natural acting, recurring visual character identity, stable scene lighting, voice, motion and whole-episode editing. Compare actual new model renders to the baseline and reject underperforming candidates. **Three complete seven-minute episodes per day remains a strategic target, not measured production throughput**. No paid render services or social posting.
