# STARWOOD — season 1 production bible (candidate)

Status: creative proposal and proof-of-concept; not user-approved, not yet full quality.
Date: 2026-10-14. Producer: MoneyPrinterTurbo free-first branch.

## Series promise
Original serialized, family-safe 3D mystery-adventure with lovable recognizable characters, heart, vivid cinematic color, organic voice acting and meaningful episode-to-episode continuity. Watch in 16:9; cut 9:16 vertical trailers. English pilot with optional multilingual dubbing, not auto-translated without speech QA. Target age bracket remains to be settled; script must be suitable for a young general audience.

## Character canon
- **Luma**: curious copper-orange young fox, turquoise scarf, fast thinker but impatient, slightly oversized ears, rounded nose and expressive eyes; wants to find who is taking the stars. Stable colors orange / cream / teal.
- **Pip**: thoughtful turquoise rabbit, gold neck ribbon, big ears, loyal friend; notices patterns and tiny clues, solves puzzles without humiliating anyone. Stable colors teal / cream / gold.
- **Echo**: luminous, mysterious Star Keeper; conveyed initially as golden light and musical motif, revealed as an ally after conflict is understood. Not a rip-off of an existing character or franchise.
- **Locations**: Starwood forest, moonlit lantern glade, Observatory Hill, Forgotten River, Whispering Archive.
- Reuse **the same character rigs and voice identities**, proportions, facial controls, accessories and look-dev across every shot. Do not rely on text-to-video alone to maintain identity.

## Season outline (8 × 4–8 min)
1. **The Missing Star** — a familiar constellation loses one light; a drifting lantern reveals a map fragment and a hint that someone is trying to save the stars, not steal them. Cliffhanger: another star blinks out, and the map points under the forest.
2. **The Path That Moves** — the friends find a trail that changes with their choices; empathy, not speed, reveals the right route. Cliffhanger: a footprint where none should be.
3. **The River of Yesterday** — a reflection shows events from the past; Luma's mistaken conclusion threatens her friendship with Pip. Cliffhanger: a recorded voice asks them not to trust the lantern.
4. **The Whispering Archive** — the friends learn why Echo hides; information is fragmented; truth comes from assembling evidence. Cliffhanger: Starwood's clock stops.
5. **The Silent Hour** — time seems stalled but the pair discover the cause is a special sky event, not magic punishment. Cliffhanger: their map changes.
6. **The Broken Constellation** — they restore a piece but disagree on whom to help first. Cliffhanger: Echo's source is located.
7. **The Keeper's Secret** — Echo is trying to shield the sky from a spreading shadow; the friends must choose cooperation over blame. Cliffhanger: one light remains.
8. **Light Belongs to Everyone** — collaboration returns the stars; satisfying finale, gentle teaser that a new season's mystery has started.

## Pilot sample (26s concept, not commercial deliverable)
0–5.5s: moonlit cinematic establishing shot of Starwood. Caption: "In Starwood, every star has a name."
5.5–10s: one light vanishes from the sky. Caption: "But tonight, one star is missing."
10–16s: camera tracks toward Luma and Pip. Luma: "Pip... do you see that light?"
16–21s: lantern floats from darkness. Pip: "I think it is calling us!"
21–26s: lantern glows, a hidden shape begins to emerge. Caption: "The lantern knows a secret..."
Audio recorded as human expressive voice only when real high-quality licensed TTS or professional voice tracks are available; never substitute metallic speech.

## Episode 1 (5–6 min beats)
00:00–00:18 Cold open: one star vanishes while the characters watch; a brief unanswerable question.
00:18–01:10 Morning emotional baseline: friendship, forest routines, small funny mistake, audience learns character strengths.
01:10–02:00 Discovery: the lantern signals a pattern; they choose to investigate, encountering a harmless setback.
02:00–03:05 Discovery and problem-solving: Pip notices a pattern in the stars; Luma rushes and learns to listen.
03:05–04:20 Turning point: footsteps lead to an empty clearing; clue overturns their first guess.
04:20–05:15 Payoff: they find the first map fragment and help a shy forest animal whose clue seemed unimportant.
05:15–05:40 Meaningful cliffhanger: lantern displays the symbol of another star, and the forest floor begins to light up.
05:40–05:50 Short credit/end cue; never mislead about a real-world emergency or manipulate children into excessive use.

## Story quality guardrails
- Strong opening and coherent cause/effect rather than jump cuts and synthetic repetition.
- End with a true narrative question, not a false urgency/scare tactic or direct pressure to keep watching.
- Character learns something specific each episode; appropriate positive social themes; no copyrighted characters or voice replicas.
- Consistent names, appearance, geography, timeline, established clues, scene continuity and soundtrack leitmotifs.
- The project needs measured retention/completion/repeat viewing from genuine authorized publishing accounts; do not invent numbers.
- Mark Made-for-Kids correctly and respect platform ad restrictions. Sustainable value comes from original IP and audience trust.

## Free-first render stack / constraints
- Deterministic rigging/rendering: Blender (GPL) with original 3D assets; fallback VTK software-rendered proof when Blender is absent, without passing the fallback off as professional quality.
- Human-like TTS candidate: Chatterbox (MIT code). Distinguish code and model-weights licenses. Need local inference hardware, provider availability and voice reference rights verified before using.
- Lip sync: Rhubarb (MIT) + rig blendshapes; voice timing and natural expression from recorded speech.
- Edit/captions/mux: local FFmpeg and MoneyPrinterTurbo pipeline; ComfyUI/Wan optional **after** hardware + model-weight license verification.
- Do not use paid APIs, partner nodes, hosted GPU credits or social posting without explicit authorization.
- Current host: CPU VTK render produced a true 3D still, no Blender/GPU located; full movie-quality voice+episode not verified.
- Rendering loops are time-consuming on current CPU; measure frame times before committing to episode duration.

## Proof required before promotion
1. Verifiable playable video file with 3D geometry and temporal motion (not a static-image fake).
2. Three stable character reference views and identical rigs across ≥3 separated scenes.
3. A real human-like voice track with consent/licensing, no robotic speech, aligned mouth shapes.
4. Completed ≥60s coherent narrative sample with scene continuity and independently inspected audio.
5. Completed 4–8-minute episode and platform-safe compliance assessment.
6. Authenticated real-world retention and production cost measurements.
