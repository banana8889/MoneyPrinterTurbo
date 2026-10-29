# STARWOOD — verified no-cost open model inference (26 October 2026)

**Status: two real open-model inference jobs executed. This is not a completed or approved episode. No paid APIs, GPU purchase, subscription, or payment method was used.**

## Trial A — LTX-Video distilled (original scene)
- Public existing Hugging Face ZeroGPU Space: `Lightricks/ltx-video-distilled`.
- Result: an actual generated MP4 (not a slideshow constructed in code).
- Persisted GitHub copy (development branch only): [STARWOOD_LTX_2026-10-26_2s.mp4](../studio/renders/STARWOOD_LTX_2026-10-26_2s.mp4).
- Video file size: **55,409 bytes**; generated 2-second test.
- Offline frame sampling at 4 FPS: 8 frames; mean frame delta **1.1987** grayscale levels/255; near-static sampled pairs **28.6%**.
- Independent contact-sheet inspection: flat vector-like cartoon rather than requested cinematic 3D; weak acting/motion. **REJECT as series quality**.
- No proof of consistent characters, expressive voices or cinema-grade visuals.

## Trial B — Kandinsky 6 Lite distilled (original scene)
- Public free ZeroGPU Space: `hugging-apps/kandinsky-6-lite-distill-5s`.
- **Successful real GPU inference**: request reported 71.1 seconds GPU duration on NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 2g.48gb; peak allocated 46.4 GiB. These times are the provider's report, not a local benchmark.
- Confirmed actual persisted MP4 H.264 + AAC, **864×480, 24 FPS, 121 video frames, duration 5.06 sec**, 44.1 kHz stereo audio.
- Exact size **576,459 bytes**, SHA-256 `1fe68d50adf0b759a6572cb863afe09872a7547406a0191a4922be20b3dae653`.
- Persisted media on dedicated **free** STARWOOD screening project (not in the wallet project): [Open actual MP4](https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_Kandinsky6_Lite_2026-10-26.mp4).
- Verified end-to-end externally accessible file with HTTP 200, video/mp4, 576459 bytes and exact SHA-256 above.
- FFmpeg sampled 20 grayscale frames at 4 FPS; mean brightness **58.845**/255, average frame difference **9.054**/255; static pair fraction **0%** for threshold delta <0.6.
- Visual contact-sheet shows recognizably volumetric, stylized 3D fox and rabbit and discernible action, **noticeably better than LTX**.
- This is **only a 5-second proof**. Dialogue intelligibility, expressive acting quality, lip synchronization, continuity across shots, and 4–8 minute episode **not verified**; do not promote to finished film.
- Hosted media storage is in a separately created Floot **Free** plan project; **not published** publicly as an app, no billing enabled. Video model itself is Kandinsky 6, open-source, not a paid generation provider.

## Safety and repository integrity
- Main branch unchanged.
- Only draft branch `autonomy-kids-v1` receives benchmark evidence; completed LTX clip stored there.
- No automatic schedule created; no public distribution or marketing.
- This report distinguishes real generated-video evidence from runbook/planning/tests. `CINEMATIC_QUALITY_STANDARD.md` remains the quality gate.

## Next quality gate
Independent shot-to-shot character identity validation with prior-frame continuation, clear natural spoken dialogue and 1080p finishing; ultimately deliver a 4–8-minute authored episode. The current 5-second result must not be represented as meeting that gate.
