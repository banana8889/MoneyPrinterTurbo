# MicroFabric Director 1.0 — clean-room implementation (2026-10-27)

## Confirmed implementation
An original Python control-plane was created and tested in this ChatGPT run; downloadable in the conversation as `MICROFABRIC_SELF_HOSTED_DIRECTOR_2026-10-27.zip`. The ZIP contains `MICROFABRIC_DIRECTOR.py`, `MICROFABRIC_LOCAL_RENDER.py`, tests, license, factory, and all three series' plans. **The source files themselves have not yet been committed into GitHub, and the original factory is not yet automatically wired to the new adapter**.

- **39 simultaneous numeric control dimensions**: 13 for each of two protagonists plus 13 scene/camera/environment values. The controls are quantized to four bits each and packed in a 20-byte payload; an integrity-checked capsule is 31 bytes.
- 252 capsules for three series take **7,818 bytes** (including transport header). The full manifest with prompts, identity hashes and ancestry records takes **708,063 bytes**. Neither is a compressed video file or a quantized neural model.
- Deterministic scene plans, 4-bit codec and CRC32, identity-hash lock, SHA-256 parent chain, cache-key invalidation when model/scene/reference/character changes.
- Standalone local Wan2.2 TI2V-5B adapter with previous-real-MP4 reference; self-hosted inference only. Safe exit if no local GPU or checkpoint. Cache objects are checked against stored receipts, SHA-256 and FFmpeg quality gate before reuse.
- **Eight offline integration tests passed**. 252 scenes compiled, checked and serialized. The local inference doctor found ffmpeg/ffprobe, but **no GPU**, **no checkpoint weights**, **no official Wan source installed**. A real render attempt returned `BLOCKED_NO_REAL_INFERENCE` with exit code 2; no sample MP4 was forged. Shot 2 preparation without a real predecessor video correctly failed.

## Legal boundaries
MicroFabric director/adapter are original, offered as MIT-licensed source, not copied implementations of external models. The candidate self-hosted model is upstream [Wan2.2 TI2V-5B](https://github.com/Wan-Video/Wan2.2) and its weights, separately released under Apache-2.0; applicable license notices and exact checkpoint verification remain required. Do not assume all video models or voice models have the same license.

## Next evidence gate
Run an actual 121-frame scene on independently controlled compute, verify genuine visually stable identity, model output audio and realistic movement, measure render speed/VRAM, then wire the proven adapter to the three-series scheduler. Three complete episodes per day remain a **target, not verified throughput**. The actual three-shot Kandinsky production proof from the prior turn remains a 15-second film:
https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4

No paid video services, purchased credits, recurring jobs, or social publishing were used for this implementation.
