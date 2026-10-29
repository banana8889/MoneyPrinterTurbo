# Three Series Factory — independent local generation, 2026-10-27

## Strategic target (not yet demonstrated)
User wants at least **three COMPLETE seven-minute original episodes daily**, one for each separate series: STARWOOD (family fantasy), RIVER ZERO (non-graphic young-adult thriller), ORBIT NINE (science-fiction mystery). Stage YouTube full videos and vertical teasers for short-video networks once quality and account authorization allow; avoid paid video APIs. Do not announce launch readiness until actual throughput and audio/actor quality are proved.

## Work completed in this session
An independent **single-file Python orchestration factory** was created in the current ChatGPT conversation as `THREE_SERIES_FACTORY.py`, delivered in the downloadable `THREE_SERIES_SELF_HOSTED_FACTORY_2026-10-27.zip`. It was NOT committed as source to this GitHub repository; do not imply the ZIP is in the repo. Package also includes `STARWOOD_Studio.py` as an experimental CPU-only Wan2.1 fallback, English/Hebrew README, Linux bootstrap scripts, Windows ASCII-CRLF BAT diagnostics/CPU loop, offline tests, audit receipt, and prepared daily SQLite manifest.

- 3 original series with 7-act outlines and cast bibles.
- 84 target model-generated shots per episode; **252 scheduled shots**, target about 21 minutes total output.
- Real local Wan2.2 TI2V-5B CLI subprocess backend (`generate.py --task ti2v-5B --size 1280*704 --frame_num 121 ... --image PREVIOUS_FRAME`), no paid video API. Clone GitHub code and download official checkpoint ONCE to a user-owned worker; then offline inference can be self-hosted.
- SQLite WAL task ledger and resume, per-shot hash and FFmpeg technical QA, 3-series fair queue, measured render-cost receipts, strict assembly and no premature publishing.
- Local speech/voice track, cinematic character consistency and media release approval **not verified or built into final movie release**; any assembled footage would be blocked by `PUBLISH_GATE.json`.
- Social title/caption/format drafts for three series; **no accounts connected and no publishing**.
- 6 unit tests passed (incl. 252 tasks, idempotence, non-fake QA, Windows batch CRLF and failure to assemble when 0/84 real clips exist).
- Current available execution environment: FFmpeg yes, GPU no, Wan2.2 source/weights no, Diffusers dependency no; run ends BLOCKED_NO_REAL_INFERENCE without pretending it generated movies.

## Real media available before this session
STARWOOD Episode 1: three connected AI-generated shots ~15 seconds (NOT a complete episode):
https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4

## Required proof before owner creates social accounts
1. Model/checkpoint locally installed and run on a machine with enough compute; Wan2.2 5B official 24GB GPU/CPU-offload configuration.
2. One real 7-minute episode successfully made with continuous character identity, dialogue, legally usable sound and acceptable artistic quality.
3. Benchmark actual render throughput to demonstrate three *full* episodes per day.
4. Prepare user-authorized platform upload flows and correct AI-generated/child-audience labeling. TikTok Direct Post public publishing requires audited developer integration; Instagram requires appropriate professional authorization.

### Upstream docs
- Wan2.2 official CLI: https://github.com/Wan-Video/Wan2.2
- Checkpoint: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B
- Local expressive voice candidate: https://github.com/resemble-ai/chatterbox
- Local CPU TTS alternative: https://github.com/OHF-Voice/piper1-gpl

The user explicitly requested no paid video services and as few manual tasks as possible. No scheduling in ChatGPT was created because no working persistent GPU instance was available and a scheduled chat cannot render these videos.
