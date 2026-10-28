# STARWOOD Learned Engine V1.1 — verified first fully neural CPU video (2026-10-28)

## A real new scene, NOT compositing previous footage

- First fully local, **freshly generated** video shot successfully ran on a free 4-core **Linux ARM64 CPU**, approximately 8GB system RAM and **no CUDA / no GPU**, based on **Wan2.1 T2V 1.3B Q4** + UMT5-XXL-Q4 + Wan VAE, inference code compiled from MIT-licensed [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp).
- Prompt: a brand-new woodland workshop scene featuring **Tiko**, a cocoa-brown hedgehog inventor with copper goggles and mint vest, discovering a magical compass. **No existing STARWOOD video/images were passed into the model**.
- Parameters: **320×192**, 9 true model-generated frames at 12fps, 6 Euler steps, seed 12871, sampled diffusion and VAE decoded. No interpolation or static-image padding to fabricate length.
- Console measured: learned conditioning ~47.81s; sampling ~115.38s; video generation total ~254.40s. Peak memory measured in /proc as approximately **6.93GB RSS**.
- Actual MP4 independently requested/converted and decoded: https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_TIKO_FRESH_NEURAL_WAN21_CPU_2026-10-28.mp4
- MP4: 99,407 bytes, SHA-256 `44328c183cdb9dc89ef3d1d80cefad8fe8361ade27202454893ff746284752f3`, nine frames; sampled grayscale adjacent-frame mean pixel absolute difference ~6.92/255, demonstrating frame changes but **not proving natural high-quality acting**.
- **Visual quality failed the user's cinema target**: at 320×192 and 6 steps the image is indistinct/blurry and nowhere near the Kandinsky 6 STARWOOD reference. Do NOT claim it matches.
- This is the first genuine CPU-only local-model inference proof in the project; it does not imply a viable commercial episode or 3 episodes/day. Text-to-video model is open and local; still huge (~4.73GB of downloaded weights) and CPU compute expensive.

## Important V1 correctness bug fixed
The previous orchestrator incorrectly equated Hugging Face **Xet hash** (ETag from HEAD) with the **LFS SHA-256** of model bytes. It caused false checksum mismatch after perfectly valid downloads. The authentic hashes were verified against repository tree LFS OIDs AND measured from all downloaded bytes:
- generator 816,061,024 bytes: `82788a4a3ce6e206edd3e8e5fe512b2a75344a3d272d80f07cd4e48b60b7aaf7`
- text encoder 3,655,145,312 bytes: `17cf97a5bbbc60a646d6105b832b6f657ce904a8a1ad970e4b59df0c67584a40`
- VAE 253,815,318 bytes: `2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b`

An updated distribution, `STARWOOD_LEARNED_CPU_V1_1_VERIFIED_LFS.zip`, was built in the active conversation container with corrected model hashes, current CPU flags, original STARWOOD V3 story, installer, licensing notice and **15/15 offline tests passing**. The distribution ZIP does not bundle the ~4.73GB weights.

## Next experimental gate
A separate experimental **448×256 9-frame, 18-step** CPU job was submitted on the same engine to compare appearance and memory usage; its quality/performance is not known in this receipt and should be separately verified. More detail requires compute/memory and a stronger visual model. The current small quantized Wan model quality is **not competitive with the true Kandinsky video**. No episodes published or falsely declared complete.

## Source repos and licensing
- MIT [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp)
- Apache-2.0 [Wan2.1 T2V 1.3B GGUF](https://huggingface.co/off-grid-ai/Wan2.1-T2V-1.3B-GGUF)
- [Model companions](https://huggingface.co/off-grid-ai/Video-Companions-GGUF)

All independent camera/director scripts are separate from the upstream third-party engine. No subscriptions, purchased GPU, or paid video API used.
