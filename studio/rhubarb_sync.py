"""Create speaker-specific Rhubarb phoneme timelines from locally rendered speech.

Usage:
  python studio/rhubarb_sync.py --cast-report out/scene1_audio/cast_report.json \
    --rhubarb /path/to/rhubarb --out out/scene1_lipsync

Rhubarb is open source (MIT); no cloud or paid API is used. The generated
speaker JSON files can drive independently rigged characters via
studio/apply_visemes.py.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

PHONEMES = set("ABCDEFGHX")


def load_cast(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("approval") is True:
        # Never treat TTS success as proof of human-quality sound.
        if data.get("subjective_acting_quality") != "APPROVED_BY_LISTENING":
            raise ValueError("Cast approval without listening evidence is invalid")
    records = data.get("lines")
    if not isinstance(records, list) or not records:
        raise ValueError("No valid lines in cast report")
    previous = -1.
    for rec in records:
        file = Path(rec["audio"])
        if not file.is_file():
            raise FileNotFoundError(file)
        begin, end = rec["start_seconds"], rec["end_seconds"]
        if not (math.isfinite(begin) and math.isfinite(end) and
                begin >= previous and end > begin):
            raise ValueError("Invalid or overlapping cast timestamps")
        if abs(end - begin - rec["duration_seconds"]) > .03:
            raise ValueError("Cast duration and timestamps disagree")
        previous = end
    return records


def rhubarb_cues(binary: Path, path: Path):
    cmd = [str(binary), "-f", "json", "--extendedShapes", "GH", str(path)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, encoding="utf-8", timeout=150, check=False)
    if proc.returncode:
        raise RuntimeError(f"Offline Rhubarb failed: {proc.stderr[-300:]}")
    obj = json.loads(proc.stdout)
    cues = obj.get("mouthCues")
    if not cues:
        raise ValueError("Rhubarb found no audible phoneme cues")
    for cue in cues:
        if cue["value"] not in PHONEMES:
            raise ValueError(f"Unsupported Rhubarb mouth shape: {cue['value']}")
        if cue["start"] < 0 or cue["end"] <= cue["start"]:
            raise ValueError("Malformed Rhubarb cue")
    return cues


def build(cast_report: Path, binary: Path, out: Path) -> dict:
    records = load_cast(cast_report)
    out.mkdir(parents=True, exist_ok=True)
    speakers = {}
    for rec in records:
        cues = rhubarb_cues(binary, Path(rec["audio"]))
        offset = float(rec["start_seconds"])
        translated = []
        for cue in cues:
            translated.append({
                "start": round(offset + cue["start"], 4),
                "end": round(offset + cue["end"], 4),
                "value": cue["value"],
            })
        # Leave silent gaps between the lines of the same character; Rhubarb
        # interprets each phrase locally, not as one unbroken performance.
        speakers.setdefault(rec["speaker"], []).extend(translated)
    results = {}
    for speaker, cues in speakers.items():
        prev = 0.0
        checked = []
        for cue in sorted(cues, key=lambda x: x["start"]):
            if cue["start"] < prev - .005:
                raise ValueError(f"Overlapping phonemes for speaker {speaker}")
            if cue["start"] > prev + .005 and prev > 0:
                checked.append({"start": round(prev,4), "end": cue["start"], "value": "X"})
            checked.append(cue)
            prev = cue["end"]
        output = out / (speaker + "_cues.json")
        output.write_text(json.dumps({"mouthCues": checked, "metadata": {
            "source": "local Rhubarb; free phoneme alignment",
            "not_expressive_facial_acting": True,
            "actor": speaker
        }}, indent=2), encoding="utf-8")
        results[speaker] = str(output)
    manifest = {"status": "READY_FOR_RIGGED_FACE_NOT_FILM_RELEASE",
                "source_cast_report_sha256": hashlib.sha256(cast_report.read_bytes()).hexdigest(),
                "speaker_cues": results}
    (out/"cues_manifest.json").write_text(json.dumps(manifest, indent=2),
                                            encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cast-report", type=Path, required=True)
    p.add_argument("--rhubarb", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if not a.rhubarb.is_file():
        p.error("Offline Rhubarb executable not found")
    print(json.dumps(build(a.cast_report, a.rhubarb, a.out)))


if __name__ == "__main__":
    main()
