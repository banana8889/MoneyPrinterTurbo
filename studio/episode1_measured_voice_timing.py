"""Frozen *measured* EP1 synthetic-voice timecodes from 20 Oct 2026 CI.

This is a reproducible time-basis from successful original 84-utterance Kokoro
cast generation (run 39403889703), NOT a natural performance or approved voice.
Source generated WAVs have not been imported to Git; only durations. All
subsequent character audio must be re-recorded and re-timed upon final casting.

84 voices / 3 speaking identities, 330.5992s speech + 83*0.25s pause =
351.3492s total. The script checks exact original speaker/text sequence by
reconstructing it directly from the canonical screenplay.
"""
from __future__ import annotations

SOURCE_RUN = "https://github.com/banana8889/MoneyPrinterTurbo/actions/runs/39403889703"
VOICE_ENGINE = "kokoro_82m_original_cast_not_human_approved"
GAP = 0.25
VERIFIED_TOTAL = 351.3492
CANONICAL_DIALOGUE_FNV1A_32 = 0xea0948e4
DURATIONS = tuple(float(x) for x in """
5.636 2.7676 5.6895 5.4099 2.3668 3.0215 5.661 5.379 3.7558 4.1784
3.8053 5.2923 3.0699 2.5443 4.8216 2.4093 3.7427 4.8597 2.8469 1.4487
5.6622 3.713 5.0105 4.6245 3.029 3.5168 5.0992 2.0997 4.0854 4.4122
5.7657 4.3222 2.7558 5.7663 3.1937 2.4654 4.0324 2.8677 3.7814 6.2025
3.1768 4.7769 1.5783 5.4097 3.6104 3.5532 4.6879 2.9921 5.2894 2.8664
2.1875 4.638 1.6098 5.9135 2.7117 5.7923 5.7982 3.0361 5.1878 5.2399
5.6202 4.3524 4.5843 2.7858 2.4927 4.2099 2.0732 4.3106 4.8899 2.9655
1.1568 6.1531 5.0263 2.6157 3.4545 6.3708 2.1945 3.8465 2.912 4.9559
2.7983 5.602 1.7603 2.3003
""".split())


def measured_voices(story):
    """Create dialogue alignment source from EXACT original 84-line story."""
    if story.get("version") != 1 or story.get("episode") != 1:
        raise ValueError("Baseline only covers original Starwood Episode 1")
    lines = story.get("lines", [])
    if len(lines) != len(DURATIONS):
        raise ValueError("Different screenplay may not reuse obsolete audio timings")
    # Detect rewritten script with same line count; otherwise measured timing
    # would silently drift from recorded speech. FNV-1a is a drift checksum,
    # not a security signature or rights-clearance proof.
    checksum=2166136261
    for line in lines:
        for ch in f"{line['speaker']}\t{line['text']}\n":
            checksum=((checksum ^ ord(ch)) * 16777619) & 0xffffffff
    if checksum != CANONICAL_DIALOGUE_FNV1A_32:
        raise ValueError("Original episode script changed; rerecord/re-align its actual voices")
    current = 0.0
    timeline = []
    for i, (line, duration) in enumerate(zip(lines, DURATIONS)):
        if line["speaker"] not in {"luma", "pip", "narrator"}:
            raise ValueError("Unrecognized original vocal identity")
        if not line["text"].strip():
            raise ValueError("Missing original screenplay line")
        start = round(current, 4)
        end = round(start + duration, 4)
        timeline.append({"start":start,"end":end,"act":line["act"],
                         "speaker":line["speaker"],"emotion":line["emotion"],
                         "text":line["text"]})
        current = end + (GAP if i<len(lines)-1 else 0)
    if abs(timeline[-1]["end"] - VERIFIED_TOTAL) > .0002:
        raise RuntimeError("Baseline audio checksum/duration drift")
    return timeline
