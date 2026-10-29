# October 19, 2026 — Frontier animation research correction

**Status:** research complete for the specified selection round; 2026-era code integrated at the planning/validation layer. **No frontier GPU model rendered locally, and no film passed artistic review.**

## Why the previous recommendation was obsolete

The earlier stack centered on Blender + generic Wan 2.2 motion augmentation and missed production-relevant projects released between March and September 2026. We have now verified **2026-specific official GitHub repositories, weights-release announcements, README constraints, and available LICENSE texts** for a targeted new set. This does not prove that every project or any generated footage achieves top-tier studio quality. Model quality varies from demo to production.

## Highest-impact 2026 additions

| Rank | Model / project and official repo | Verified release/features | License/compute/business gate | Decision |
|---|---|---|---|---|
| 1 | **SCAIL-2** — https://github.com/zai-org/SCAIL-2 | Source+weights released June 9, 2026; June 13 multi-reference; August 6 training code; end-to-end character animation, including animals and replacement | Apache-2.0 code. Independently verify exact checkpoint/dependency terms and available GPU. | PRIORITY MOTION ENGINE to pilot with **original licensed** fox/rabbit and licensed reference performances |
| 2 | **Stable Video Infinity 2.0 / Pro** — https://github.com/vita-epfl/Stable-Video-Infinity | ICLR 2026, May 27 EverAnimate; SVI-Tom (cartoon), SVI-Film (multi-shot), SVI-Talk (audio), SVI 2.0 Pro via `svi_wan22` branch; demonstrations of 8–14 minute videos | MIT repository; inherited Wan base checkpoints and SVI adapters each need commercial permission verification; large 14B video GPU. No copyright reuse of Tom/Jerry or showcase figures | PRIORITY LONG-FORM CONTINUITY, retaining **last five motion frames** for SVI-Film windows |
| 3 | **Wan-Animate-2** — https://github.com/Wan-Video/Wan-Animate-2 | August 7, 2026 open inference scripts + base/distilled weights; identity-preserving animated character from image+driving video, text viewpoint controls | Apache-2.0 code. **Official examples tuned for 8 × A800 at 720p or 2 × A800 at 480p**, NOT a cheap single-GPU claim. Weight/dependency checks before monetization | HIGH-QUALITY CHALLENGER, not default on unverified hardware |
| 4 | **CineCrew** — https://github.com/Ironieser/CineCrew | September 2026 release, ECCV 2026; FilmDSL `{meta,assets,memory,clips[]}`; assets, staging, continuity, structured critique/repair | Apache-2.0 code, but sample config defaults to **paid LLM gpt-5/OpenAI API**. Must replace with local compatible providers, prohibit outbound billing | ADOPT FILMDSL **CONCEPT** and deterministic local compiler, NOT the paid default app |
| 5 | **LongCat-Video-Avatar-1.5** — https://github.com/meituan-longcat/LongCat-Video | May 21, 2026; audio-driven multi-stream dialogue, long-video continuations, animals/stylized actors | MIT code; actual 1.5 weights/other inputs must be checked separately; official multi-GPU examples. Low-VRAM RTX4090 PR #115 still OPEN as of review; do not treat unmerged PR as supported release | DIALOGUE VIDEO challenger; no presumed single-GPU compatibility |
| 6 | **ShotStream** — https://github.com/KlingAIResearch/ShotStream | March 27, 2026 inference+training code/checkpoints, ECCV 2026, shot-streaming | License file absent in examined upstream; repository itself cautions that demo prompts differ from internal training data | EXPERIMENTAL only pending license and reproduction |
| 7 | **LiveAvatar** — https://github.com/Alibaba-Quark/LiveAvatar | ECCV 2026 spotlight; long streaming talking/cartoon avatar; reports 45 FPS on multi-H800 | Apache code; published optimized 48GB/multi-H800 runtime, not proof of consumer availability | POTENTIAL dialogue-specific fallback, not full-body film engine |
| 8 | **StoryMem** — https://github.com/Kevin-thu/StoryMem | Long-video multi-shot memory conditioned diffusion, looks relevant | **S-Lab 1.0 non-commercial license**, specifically requires contact for commercial use | EXCLUDED from monetized production |
| 9 | **Memento** — https://github.com/ernie-research/Memento | Cross-shot memory for consistent stories | No LICENSE at examined expected path; checkpoint permissions unclear | RESEARCH ONLY until permissions proven |
| 10 | **ShotDirector** — https://github.com/UknowSth/ShotDirector | CVPR 2026 camera and editing transitions | Github TODO still shows inference code/checkpoint release unfinished | WATCH / DO NOT INTEGRATE claims |
| 11 | **SCAIL-2 Low-VRAM / WanGP** — https://github.com/DeepBeepMeep/Wan2GP | Current local GUI runner with character motion options | UI license and loaded model licenses independent; GPU and quality not yet benchmarked | Candidate for hardware-constrained evaluation |

## Architecture change delivered in this revision

- [studio/free_toolchain.py](../studio/free_toolchain.py) now adds **10 more 2026-era candidates** to the previous 32-tool registry. Models with unverified weights, non-commercial licensing, or infeasible GPUs are not auto-runnable.
- [studio/frontier_film_director.py](../studio/frontier_film_director.py) now compiles the entire original seven-act screenplay and 41-shot camera plan into a **CineCrew-inspired internal manifest** containing stable cast sheets, locations, persona constraints, exact dialogue line references, emotional acting, scene memory, engine candidates and safe negative prompts. **This is NOT claimed to import directly into CineCrew**, whose schema and powered services differ.
- It splits the full episode into **105 distinct continuation segments** with **deterministically unique seeds**, and correctly plans previous **five motion frames** within one shot for SVI. Each new shot begins from an original identity-locked storyboard image; no copied copyrighted example frames.
- No render job is marked ready until ORIGINAL LICENSED references, actual driving motion files, permissioned audio, checkpoint/dependency licensing, local GPU capacity, and human visual review exist. Even with files present, the compiler emits a PREPRODUCTION state, not fictitious success.
- [test_frontier_film_director.py](../test/services/test_frontier_film_director.py) + [frontier-cinema-2026.yml](../.github/workflows/frontier-cinema-2026.yml) run **offline code-only CI**, with no cron, web API, paid inference or publicity.

**Verified outcome:** GitHub Actions [run 39292789541](https://github.com/banana8889/MoneyPrinterTurbo/actions/runs/39292789541) completed successfully: **10/10 tests**, **41 shots**, **105 continuity segments**, **0 rendered films**, **0 paid API calls**. This is a meaningful planning/integrity upgrade, not a finished animated movie.

## Next engineering gate

1. Obtain **original, cinema-quality hero character reference images** and rights-cleared motion-driving performances. Avoid adopting copyrighted cartoon demonstration assets or voice replicas.
2. Benchmark SCAIL-2 on actual accessible VRAM and original pair of characters; separately trial SVI Pro on long-form consistency; evaluate Wan-Animate-2 only on realistically supported multi-GPU hardware.
3. Verify licensing of all dependency checkpoints, and document reproducible GPU+wall-time requirements instead of inventing performance numbers.
4. Produce, **internally review**, rework and reject shots until character motion, expressions, identity, voice, staging and sound pass the agreed feature-quality standard.
5. Assemble original **4–8-minute** film at professionally mastered quality and show the user **only after** the finished output passes narrative/visual/audio review.

**User constraints retained:** no scheduling, no paid subscriptions or credit usage, no public posting, no preview of partial/poor videos, do not remove other MoneyPrinterTurbo functionality, keep PR draft and main branch untouched.

## Source verification list
Official GitHub README/LICENSE: Wan-Animate-2, SCAIL-2, Stable-Video-Infinity, CineCrew, LongCat-Video, StoryMem, ShotStream, LiveAvatar, Memento, ShotDirector. Date and availability are snapshots as of October 19, 2026.
