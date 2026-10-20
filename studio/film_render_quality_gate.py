"""Technical QC for a *rendered* film clip, not a cinematic quality score.

No static slide or audio-only output may pass as an animation milestone.
Requires real video pixels, actual H.264/AAC or MJPEG/WAV media data, correctly
paced frames, and evidence of pixel motion in several interior windows.
Movement may come from camera/editing, so this is only one of several gates.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path


def probe(path: Path) -> dict:
    args = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of",
            "json", str(path)]
    try:
        o = json.loads(subprocess.check_output(args, text=True, timeout=35))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
        raise RuntimeError("Video/codec probe failed") from err
    tracks = o.get("streams", [])
    visual = next((v for v in tracks if v.get("codec_type") == "video"), None)
    if visual is None:
        raise RuntimeError("No video stream")
    return {"width": int(visual["width"]), "height": int(visual["height"]),
            "frames": int(visual.get("nb_frames", 0) or 0),
            "fps": visual.get("avg_frame_rate", "0/1"),
            "duration": float(o["format"].get("duration") or visual.get("duration") or 0),
            "has_audio": any(t.get("codec_type") == "audio" for t in tracks),
            "codec": visual.get("codec_name", "unknown"),
            "bytes": path.stat().st_size}


def frames(path: Path, width=128, height=72, fps=6):
    from subprocess import PIPE
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-an",
           "-vf", f"fps={fps},scale={width}:{height}:flags=fast_bilinear,format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    cp = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, timeout=110, check=True)
    frame_bytes = width * height
    if len(cp.stdout) < 2 * frame_bytes or len(cp.stdout) % frame_bytes:
        raise RuntimeError("Decoded video doesn't have enough complete frames")
    import numpy as np
    return np.frombuffer(cp.stdout, dtype="uint8").reshape(-1, height, width)


def inspect(path: Path, minimum_seconds=1.2, minimum_motion=.5, minimum_fps=24.0) -> dict:
    import numpy as np
    path=path.expanduser().resolve()
    if not path.is_file() or path.stat().st_size < 10000:
        raise ValueError("Rendered media not found or unreasonably tiny")
    meta=probe(path)
    if meta["width"]<320 or meta["height"]<180:
        raise RuntimeError("Render resolution below even internal QA level")
    if abs(meta["width"] * 9 - meta["height"] * 16) > 0.01 * meta["height"] * 16:
        raise RuntimeError("Unexpected aspect ratio; a 16:9 cinematic output is required")
    fps_num, fps_den=map(int,meta["fps"].split("/"))
    if not 8 <= minimum_fps <= 120:
        raise ValueError("Invalid raw-frame QA threshold")
    if fps_den <= 0 or fps_num/fps_den < minimum_fps - .1:
        raise RuntimeError(
            f"Raw clip FPS {fps_num}/{fps_den} below required {minimum_fps}; "
            "do not report it as 24fps mastered footage"
        )
    if meta["duration"] < minimum_seconds:
        raise RuntimeError("The supposed animated scene is too short")
    frame_stack=frames(path)
    if float(np.mean(frame_stack)) < 8.0:
        raise RuntimeError("Likely black or unlit footage")
    # Grayscale frame-to-frame absolute pixel movement. A scene cut will show
    # a large spike; require activity across sustained intervals, not one cut.
    changes=np.abs(np.diff(frame_stack.astype("float32"),axis=0)).mean(axis=(1,2))
    # Exclude the largest 15% of changes, usually camera hard-cuts.
    baseline=np.sort(changes)[:max(1,int(len(changes)*.85))]
    sustained = float(np.mean(baseline))
    different = float(np.mean(changes>minimum_motion))
    if sustained < minimum_motion or different < .20:
        raise RuntimeError("Nearly static footage: no sustained pixel movement")
    return {**meta, "gray_mean": round(float(np.mean(frame_stack)),2),
            "sampled_frames": len(frame_stack),
            "sustained_pixel_motion": round(sustained,4),
            "changed_frame_fraction": round(different,4),
            "verified_actual_render": True,
            "unmastered_native_fps": round(fps_num/fps_den, 4),
            "verified_skeletal_performance": False,
            "verified_emotional_acting": False,
            "verified_character_design": False,
            "cinematic_release_pass": False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("video",type=Path)
    p.add_argument("--min-seconds", type=float, default=1.2)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    record=inspect(a.video, a.min_seconds)
    payload=json.dumps(record,indent=2)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(payload,encoding="utf-8")
    print(payload)


if __name__=="__main__":
    main()
