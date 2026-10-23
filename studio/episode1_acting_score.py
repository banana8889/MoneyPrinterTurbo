"""Deterministic, original Starwood Episode 1 actor-performance score.

Turns the actual measured 351.3492-second, 84-line synthetic voice-timing
receipt into directed skeleton, eyeline, expression and listener reactions.
This score is consumed by Blender's *original biped* Luma/Pip armatures, not
the previously rejected quadruped reference demo.

Crucial: measured timings establish dialogue beats but not human-quality
voices or phoneme alignment. Mouth OPEN/CLOSE animation is only approximate
until actual licensed WAV and per-speaker Rhubarb cues are supplied.
This score does NOT represent a rendered or cinema-approved episode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from studio.episode1_measured_voice_timing import measured_voices

ACTORS = ("luma", "pip")
EMOTION_POSE = {
    "wonder": {"brow_up": .80, "worry": .0, "smile": .12, "head_pitch": -.07,
               "reach": .30, "torso_lean": .07},
    "curious": {"brow_up": .46, "worry": .05, "smile": .13, "head_pitch": .09,
                "reach": .23, "torso_lean": .08},
    "concern": {"brow_up": .08, "worry": .70, "smile": 0, "head_pitch": .09,
                "reach": -.05, "torso_lean": -.06},
    "gentle": {"brow_up": .22, "worry": 0, "smile": .65, "head_pitch": .035,
               "reach": .23, "torso_lean": .025},
    "excited": {"brow_up": .84, "worry": 0, "smile": .81, "head_pitch": -.1,
                "reach": .67, "torso_lean": .13},
    "urgent": {"brow_up": .54, "worry": .63, "smile": 0, "head_pitch": .03,
               "reach": .25, "torso_lean": .14},
    "hopeful": {"brow_up": .37, "worry": 0, "smile": .82, "head_pitch": -.05,
                "reach": .44, "torso_lean": .07},
}


def story(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("version") != 1 or d.get("episode") != 1:
        raise ValueError("Only exact original first-episode source is supported")
    return d


def clip(name, actor, start, end, emotion, line_number, mode):
    if not 0 <= start < end <= 352:
        raise ValueError("Invalid timed performance clip")
    look = ("luma" if actor == "pip" else "pip")
    base = EMOTION_POSE[emotion]
    if mode == "listen":
        # Actors react and maintain attention, not freeze like static puppets.
        base = {**base, "brow_up": min(.48, base["brow_up"]*.50),
                "worry": base["worry"]*.5,
                "smile": base["smile"]*.35,
                "reach": 0.0, "torso_lean": .02}
    if mode == "narrated":
        base = {**base, "brow_up": .2, "worry": .10,
                "smile": .1, "reach": 0.0, "torso_lean": .025}
    return {
        "name": name, "actor": actor, "mode": mode,
        "line_number": line_number, "emotion": emotion,
        "start": round(start, 4), "end": round(end, 4),
        "look_at": look if mode != "narrated" else "story_clue",
        "bone_pose": {
            "head_pitch": round(base["head_pitch"], 3),
            "head_yaw": (-.17 if actor == "luma" else .17) if mode == "listen" else 0,
            "spine_lean": round(base["torso_lean"], 3),
            "upper_arm_L": round(base["reach"], 3) if actor == "luma" else 0,
            "upper_arm_R": round(base["reach"], 3) if actor == "pip" else 0,
            "tail_sway": .09 if mode != "narrated" else .04,
        },
        "face_pose": {"BrowsUp": round(base["brow_up"], 3),
                      "Worry": round(base["worry"], 3),
                      "Smile": round(base["smile"], 3)},
        # Must never be described as lip-synced until actual phonemes loaded.
        "mouth_pose": "AWAITING_REAL_PHONEMES" if mode == "speak" else "CLOSED",
    }


def build(script: dict) -> dict:
    original = measured_voices(script)
    lines=script["lines"]
    if len(original)!=len(lines) or len(original)!=84:
        raise RuntimeError("Canonical measured dialogue mismatch")
    controls={actor: [] for actor in ACTORS}
    shots=[]
    act_coverage={}
    for n,(spoken,line) in enumerate(zip(original,lines),start=1):
        start=float(spoken["start"])
        end=float(spoken["end"])
        who=spoken["speaker"]
        emotion=spoken["emotion"]
        if spoken["text"]!=line["text"] or spoken["act"]!=line["act"]:
            raise ValueError("Voice receipt script drift")
        for actor in ACTORS:
            mode=("narrated" if who=="narrator" else
                  "speak" if who==actor else "listen")
            controls[actor].append(clip(
                f"{actor}_line_{n:03d}",actor,start,end,emotion,n,mode
            ))
        act_coverage.setdefault(line["act"], []).append(n)
    if sorted(act_coverage)!=list(range(1,8)):
        raise ValueError("Missing dramatic act")
    # Choose edits at natural acting units (no automatic cut every sentence).
    last_cut_time=-100.0
    for n,spoken in enumerate(original,start=1):
        act=spoken["act"]
        new_act=n==1 or original[n-2]["act"]!=act
        elapsed=float(spoken["start"])-last_cut_time
        if new_act or elapsed>=8.75:
            focus=spoken["speaker"] if spoken["speaker"] in ACTORS else "ensemble"
            framing=("establishing" if new_act else
                     "luma_medium" if focus=="luma" else
                     "pip_medium" if focus=="pip" else "two_shot")
            shots.append({"start":spoken["start"],"act":act,"line_number":n,
                          "framing":framing, "focus":focus, "rendered":False})
            last_cut_time=float(spoken["start"])
    # Verify continuity of the full original voice timeline, not just counts.
    for a,b in zip(original,original[1:]):
        if not .15<=round(b["start"]-a["end"],4)<=.40:
            raise RuntimeError("Measured actor timeline overlap or anomalous gap")
    last_end=original[-1]["end"]
    if abs(last_end-351.3492)>0.0002:
        raise RuntimeError("Whole original episode dialogue duration drift")
    script_bytes=json.dumps(
        [{"actor":v["speaker"],"text":v["text"]} for v in lines],
        ensure_ascii=False,sort_keys=True
    ).encode("utf-8")
    return {
        "schema":"STARWOOD_ORIGINAL_BIPED_PERFORMANCE_V1",
        "episode":1, "speaker_identity":["luma","pip","narrator"],
        "source_dialogue_sha256":hashlib.sha256(script_bytes).hexdigest(),
        "act_count":7,"dialogue_lines":len(original),
        "measured_timeline_seconds":last_end,
        "scene_fps":24,"original_actor_armatures":list(ACTORS),
        "actor_controls":controls,
        "camera_cuts":shots,
        "phonemes_from_original_recording":False,
        "body_acting_visual_qa":"NOT_REVIEWED",
        "stage_source":"studio/anthro_hero_factory.py",
        "voice_acting_human_approved":False,
        "scene_renders":0,"film_ready":False,
        "caveats":["Procedural body/face poses require visual acting review",
                   "Must align actual licensed WAV+Rhubarb mouth cues before publishing",
                   "Do not treat rigidly bone-parented components as skinned character meshes",
                   "Motion is directed but not performance-captured or professionally hand-animated"],
    }


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--story",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    opt=p.parse_args(argv)
    score=build(story(opt.story))
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(score,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"lines":score["dialogue_lines"],
                      "actor_performances":sum(len(x) for x in score["actor_controls"].values()),
                      "camera_cuts":len(score["camera_cuts"]),
                      "measured_seconds":score["measured_timeline_seconds"],
                      "film_ready":False}))


if __name__=="__main__":
    main()
