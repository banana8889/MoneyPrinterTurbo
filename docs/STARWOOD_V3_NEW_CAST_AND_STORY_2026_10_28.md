# STARWOOD v3 — New cast and revised children's story (2026-10-28)

The production focus remains **STARWOOD only**. This is the successor to the original "Missing Star" cinematic sample, not the unrelated teen/zombie project.

## Creative change
**Episode 1: The Star That Forgot Its Song** (Hebrew: הכוכב ששכח את השיר). Luma the orange fox (turquoise scarf) and Pip the cream rabbit (plum bow) still discover the missing North Star and the hovering golden lantern. They learn the starlights were not stolen; they were being sheltered from a cold wind. New friends make different contributions to recover the forest's lost melody, rather than defeating a conventional villain. Another lantern blinks in the final seconds to start the next episode.

## Four new original roles
- **Tiko** — cocoa-brown young hedgehog inventor, mint vest, copper goggles, brass compass listening to music; first staged shot 14.
- **Vela** — young tawny owl cartographer, silver wing feather tips, blue map satchel; first staged shot 26.
- **Nivi** — periwinkle-blue firefly communicating with pulses of light, no voiced mouth; first staged shot 9.
- **Ruma** — shy lavender mist creature with golden eyes, initially suspected, actually protects starlight; first staged shot 49.

## Engine evidence and delivery
- Original 7-act screenplay with **84 distinct visual beats** and short lines; ten persistent STARWOOD cast identities total.
- New **STARWOOD_V3_ENGINE.py** builds a signed scene manifest and 4-bit MicroFabric Ensemble v2 stage-state capsules. **6,079-byte packed controls** for all 84 beats (not images/model weights). Per-scene exclusive on-screen casting; camera descriptions; continuity checks for new character introductions.
- 15 new tests passed; 30 existing core regression tests also passed. Windows CRLF launch script and interactive offline-readable storyboard built.
- Local inference was genuinely attempted and returned `BLOCKED_NO_REAL_INFERENCE` (no CUDA GPU, model source or weights); **no newly generated AI video**. This release is a working story/director integration, not a completed episode or approved character performance.
- ZIP with complete new source, editable cast file, episode JSON and receipts delivered in the ChatGPT conversation as `STARWOOD_V3_NEW_CAST_AND_STORY_2026-10-28.zip`. **The ZIP itself and Python source have not been committed to GitHub**, only this production receipt.

Visual quality gate: footage containing new characters must meet or exceed the pre-existing real Kandinsky 6 Lite STARWOOD baseline, with stable appearances across shots, film-quality motion and appropriate dialogue. The verified 15s baseline remains: https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4
