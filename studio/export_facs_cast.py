"""Export licensed, time-aligned dialogue and facial cues to a local Godot 4.6 project.

Scene playback uses *real* facial blend shapes and WAV files, not random mouth
flapping. Works with any rig mapped to existing blend shape names, including
the MIT/CC0 VitruvianGodot reference; output files stay local/private.

Usage:
python studio/export_facs_cast.py \
 --cast-report out/scene1_audio/cast_report.json \
 --cues-dir out/scene1_lipsync \
 --godot-project path/to/godot_project \
 --out-dir studio_cast

Do not mark animation as publication-ready merely because exports succeed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile


CUES = set("ABCDEFGHX")
SPEAKERS = {"luma", "pip", "narrator"}
ALLOWED_EMOTIONS = {"wonder", "concern", "curious", "gentle", "excited", "urgent", "hopeful", None}


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected JSON record")
    return data


def validate_cast_and_cues(cast_path: Path, cues_dir: Path):
    cast = read_json(cast_path)
    lines = cast.get("lines")
    if not isinstance(lines, list) or len(lines) < 3:
        raise ValueError("Cast must include at least three spoken lines")
    speakers = set()
    prev = -1.
    sources = {}
    for i, line in enumerate(lines):
        speaker = line.get("speaker")
        if speaker not in SPEAKERS:
            raise ValueError(f"Invalid speaker {speaker!r}")
        if line.get("emotion") not in ALLOWED_EMOTIONS:
            raise ValueError("Unknown emotion")
        begin = line.get("start_seconds")
        end = line.get("end_seconds")
        duration = line.get("duration_seconds")
        if any(not isinstance(v, (int, float)) or not math.isfinite(v)
               for v in (begin, end, duration)):
            raise ValueError("Non-numeric or invalid line timestamp")
        if begin < prev - 0.002 or end <= begin or abs(end - begin - duration) > .04:
            raise ValueError("Overlapping/invalid line timestamp")
        prev = end
        wav = Path(line.get("audio", ""))
        # CI artifact extraction changes the root: safely recover same-folder WAV
        # by basename, never trusting the archived absolute runner path.
        if not wav.is_file():
            wav = cast_path.parent / wav.name
        if not wav.is_file() or wav.suffix.lower() != ".wav":
            raise FileNotFoundError(f"Missing recorded WAV line {i+1}: {wav}")
        if not line.get("text", "").strip():
            raise ValueError("Empty spoken text")
        speakers.add(speaker)
        sources[i] = wav
    if len(speakers) < 2:
        raise ValueError("Requires more than one actor")
    cues = {}
    for speaker in sorted(speakers - {"narrator"}):
        fp = cues_dir / f"{speaker}_cues.json"
        c = read_json(fp).get("mouthCues")
        if not isinstance(c, list) or len(c) < 4:
            raise ValueError(f"No usable real phonemes for {speaker}")
        prev_cue_end = 0.
        for cue in c:
            a, b, v = cue.get("start"), cue.get("end"), cue.get("value")
            if v not in CUES:
                raise ValueError("Unknown phoneme shape")
            if any(not isinstance(t,(int,float)) or not math.isfinite(t) for t in (a,b)):
                raise ValueError("Nonfinite phoneme time")
            if a < prev_cue_end - .005 or b <= a or a < 0:
                raise ValueError("Invalid or overlapping mouth cues")
            prev_cue_end = b
        if prev_cue_end > cast["duration_seconds"] + .08:
            raise ValueError("Mouth cues exceed scene duration")
        cues[speaker] = c
    return cast, lines, cues, sources


def export_cast(cast_path: Path, cues_dir: Path, project: Path, out_dir: str = "studio_cast"):
    if not project.is_dir() or not (project / "project.godot").is_file():
        raise ValueError("Destination must be a Godot project")
    if Path(out_dir).is_absolute() or ".." in Path(out_dir).parts or out_dir in ("", "."):
        raise ValueError("Destination must be a safe project-relative folder")
    cast, lines, cues, wav_sources = validate_cast_and_cues(cast_path, cues_dir)
    dest = project / out_dir
    dest.mkdir(parents=True, exist_ok=True)
    exported = []
    for i, line in enumerate(lines):
        wav = wav_sources[i]
        digest = hashlib.sha256(wav.read_bytes()).hexdigest()
        name = f"line_{i+1:03d}_{line['speaker']}_{digest[:12]}.wav"
        target = dest / name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Existing sound was modified; refusing to overwrite")
        if not target.exists():
            with tempfile.NamedTemporaryFile(prefix="._",dir=dest,delete=False) as tmp:
                temp=Path(tmp.name)
            try:
                shutil.copy2(wav, temp)
                os.replace(temp, target)
            finally:
                temp.unlink(missing_ok=True)
        exported.append({
            "speaker": line["speaker"], "emotion": line.get("emotion"),
            "text": line["text"],
            "start": round(float(line["start_seconds"]),4),
            "end": round(float(line["end_seconds"]),4),
            "audio": f"res://{out_dir}/{name}",
            "source_sha256": digest,
        })
    manifest = {
        "version": 1,
        "source": "offline-open-weight-voices+Rhubarb",
        "duration_seconds": round(float(cast["duration_seconds"]),4),
        "lines": exported,
        "cues": cues,
        "release_gate": {
            "voice_acting": "NOT_VERIFIED_BY_LISTENING",
            "cinematic_performance": "NOT_VERIFIED",
            "film_ready": False,
        },
    }
    tmp = dest / "._scene_cast"
    tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),encoding="utf-8")
    os.replace(tmp, dest / "scene_cast.json")
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cast-report",required=True,type=Path)
    p.add_argument("--cues-dir",required=True,type=Path)
    p.add_argument("--godot-project",required=True,type=Path)
    p.add_argument("--out-dir",default="studio_cast")
    args = p.parse_args()
    m = export_cast(args.cast_report,args.cues_dir,args.godot_project,args.out_dir)
    print(json.dumps({"lines":len(m["lines"]),"speakers":sorted(m["cues"]),
                      "duration_seconds":m["duration_seconds"],"film_ready":False}))


if __name__ == "__main__":
    main()
