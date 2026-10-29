"""Free-first cast dialogue renderer (Kokoro 82M, Apache-2.0 model weights).

The audio production manifest is intentionally explicit: a dramatic serial does
not become a finished episode merely because synthetic speech was generated.
No cloud API, paid TTS provider, voice cloning or publishing.

Run locally with:
  python studio/cast_audio.py render --script studio/season1_scene1.json \
         --out storage/studio_audio/scene1 --engine kokoro

Inspect produced WAV files by ear and mark APPROVED after an actor-like listen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ALLOWED_VOICES = {
    "luma": "af_heart",     # English, soft and adventurous
    "pip": "am_michael",    # English, warm, curious
    "narrator": "bf_emma",  # English, intimate storytelling
}
MAX_LINES = 120
MAX_LINE_CHARS = 380


def read_script(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("version") != 1:
        raise ValueError("Script must be version 1 JSON")
    lines = obj.get("lines")
    if not isinstance(lines, list) or not 1 <= len(lines) <= MAX_LINES:
        raise ValueError("Script lines must be a nonempty list of at most 120 entries")
    speaker_set = set()
    for n, line in enumerate(lines):
        if not isinstance(line, dict):
            raise ValueError(f"Line {n}: must be a record")
        speaker, text = line.get("speaker"), line.get("text")
        if speaker not in ALLOWED_VOICES:
            raise ValueError(f"Line {n}: unapproved speaker")
        if not isinstance(text, str) or not 2 <= len(text.strip()) <= MAX_LINE_CHARS:
            raise ValueError(f"Line {n}: text length not acceptable")
        if re.search(r"[\x00-\x08\x0b-\x1f]", text):
            raise ValueError(f"Line {n}: control characters forbidden")
        speaker_set.add(speaker)
        if line.get("emotion") not in (
            None, "wonder", "concern", "curious", "gentle", "excited", "urgent", "hopeful"
        ):
            raise ValueError(f"Line {n}: emotion must be from approved vocabulary")
    if len(speaker_set) < 2:
        raise ValueError("A dramatic scene requires at least two voice identities")
    if len(lines) < 3:
        raise ValueError("Dramatic scene requires at least three spoken lines")
    return obj


def trim_fade(audio, sample_rate: int):
    """Trim long dead air with short safe fade-out; preserve dialogue pauses."""
    import numpy as np
    data = np.asarray(audio, dtype="float32").reshape(-1)
    if data.size < round(sample_rate * 0.20):
        raise RuntimeError("Unusable near-empty TTS audio")
    if not np.isfinite(data).all():
        raise RuntimeError("NaN/Inf TTS audio")
    if float(np.max(np.abs(data))) < .002:
        raise RuntimeError("Silent TTS audio")
    # Don't normalize clipped audio and pretend it is usable.
    if float(np.mean(np.abs(data) >= .995)) > .002:
        raise RuntimeError("Clipped TTS audio")
    # Keep modest silence before/after each utterance, never remove pauses inside.
    active = np.flatnonzero(np.abs(data) > .009)
    if active.size < sample_rate // 25:
        raise RuntimeError("Insufficient voiced samples")
    edge = round(sample_rate * .12)
    begin = max(0, int(active[0]) - edge)
    end = min(data.size, int(active[-1]) + edge)
    data = data[begin:end].copy()
    nfade = min(round(sample_rate * .012), len(data) // 4)
    if nfade:
        data[:nfade] *= np.linspace(0.0, 1.0, nfade, dtype="float32")
        data[-nfade:] *= np.linspace(1.0, 0.0, nfade, dtype="float32")
    return data


def wav_info(path: Path) -> dict:
    import numpy as np
    import soundfile as sf
    samples, rate = sf.read(path, dtype="float32", always_2d=False)
    if samples.ndim != 1:
        raise RuntimeError(f"Expected mono dialogue: {path.name}")
    duration = len(samples) / rate
    rms = float(np.sqrt(np.mean(np.square(samples, dtype="float64"))))
    peak = float(np.max(np.abs(samples)))
    if not .20 <= duration <= 35.0 or rms < .006 or peak < .04:
        raise RuntimeError(f"Invalid dialogue loudness/duration: {path.name}")
    if peak > 1.001:
        raise RuntimeError(f"Digital clipping: {path.name}")
    return {"duration_seconds": round(duration, 4), "sample_rate": int(rate),
            "rms": round(rms, 5), "peak": round(peak, 5)}


def load_model():
    # No paid provider or remote inference API; Kokoro downloads free public
    # Apache-licensed weights on first use into the local Hugging Face cache.
    from kokoro import KPipeline
    return {"a": KPipeline(lang_code="a"), "b": KPipeline(lang_code="b")}


def synthesize(model, line: dict):
    import numpy as np
    voice = ALLOWED_VOICES[line["speaker"]]
    pipeline = model[voice[0]]
    emotion = line.get("emotion", "curious")
    # Understated prosody avoids metallic robotic or overhyped TTS.
    pace = {"gentle": 0.90, "concern": 0.91, "wonder": 0.92,
            "curious": .96, "excited": .99, "urgent": 1.03, "hopeful": .94}.get(emotion, .96)
    pieces = []
    for _, _, audio in pipeline(line["text"], voice=voice, speed=pace, split_pattern=r"\n+"):
        arr = np.asarray(audio, dtype="float32").flatten()
        if len(arr):
            pieces.append(arr)
    if not pieces:
        raise RuntimeError(f"No audio returned for {line['speaker']}")
    return trim_fade(np.concatenate(pieces), 24000), 24000


def render(script_path: Path, out: Path, engine: str = "kokoro", model=None) -> dict:
    import soundfile as sf
    obj = read_script(script_path)
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    model = load_model() if model is None else model
    records = []
    previous_end = 0.0
    # Entire voice sequence is cached by line hash; no duplication or gratuitous
    # download/re-generation on repeat. Simple text+voice+emotion identity.
    for n, line in enumerate(obj["lines"]):
        voice = ALLOWED_VOICES[line["speaker"]]
        digest = hashlib.sha256(json.dumps([line, voice, engine], sort_keys=True).encode()).hexdigest()[:16]
        dest = out / f"line_{n+1:03d}_{digest}.wav"
        if dest.exists():
            try:
                info = wav_info(dest)
            except Exception:
                dest.unlink()
            else:
                pass
        if not dest.exists():
            audio, rate = synthesize(model, line)
            fd, temporary = tempfile.mkstemp(dir=out, suffix=".wav")
            os.close(fd)
            try:
                sf.write(temporary, audio, rate, subtype="PCM_16")
                info = wav_info(Path(temporary))
                os.replace(temporary, dest)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        info = wav_info(dest)
        start = round(previous_end + (0.25 if n > 0 else .0), 4)
        previous_end = start + info["duration_seconds"]
        records.append({"line": n + 1, "speaker": line["speaker"], "voice": voice,
                        "text": line["text"], "emotion": line.get("emotion"),
                        "audio": str(dest), "start_seconds": start,
                        "end_seconds": round(previous_end, 4),
                        **info})
    report = {"version": 1, "engine": engine,
              "provider": "local Kokoro open-weights (not paid API)",
              "rendered": len(records), "duration_seconds": round(previous_end, 4),
              "cast": sorted(set(row["speaker"] for row in records)),
              "lines": records, "subjective_acting_quality": "NOT_REVIEWED",
              "approval": False, "suitable_for_publication": False,
              "notes": "Must audition emotional naturalness and character consistency; quantitative checks alone do not certify believable acting."}
    tmp = out / ".cast_report.tmp"
    tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, out / "cast_report.json")
    return report


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["validate", "render"])
    p.add_argument("--script", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("storage/studio_audio"))
    args = p.parse_args(argv)
    if args.command == "validate":
        data = read_script(args.script)
        print(json.dumps({"valid": True, "lines": len(data["lines"]),
                          "speakers": sorted(set(x["speaker"] for x in data["lines"]))}))
    else:
        result = render(args.script, args.out)
        print(json.dumps({key: result[key] for key in ("rendered", "duration_seconds", "cast", "approval")}))


if __name__ == "__main__":
    main()
