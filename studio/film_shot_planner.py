"""Professional shot/acting decision list from the original full-episode script.

This is a camera/actor planning compiler, not a video generator. It replaces
random one-line jump-cuts with continuous 3D *performances* and motivated edits,
and produces machine-readable requirements for original rigged hero characters.

Can run on CPU without APIs:
  python studio/film_shot_planner.py studio/season1_episode1_full.json \
      --out out/episode1_shot_plan.json

A shot plan cannot certify imagery, natural dialogue, performance or marketability.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SPEAKERS = {"luma", "pip", "narrator"}
EMOTIONS = {"wonder", "concern", "curious", "gentle", "excited", "urgent", "hopeful"}
SHOT_CHOICES = ("establishing", "two_shot", "luma_medium", "pip_medium",
                "over_shoulder_luma", "over_shoulder_pip", "insert_lantern",
                "reaction_luma", "reaction_pip", "wide_reveal")
LOCATION_BY_ACT = {
    1: "starwood_starfield_glade",
    2: "starwood_bridge_trail",
    3: "starwood_starfield_glade",
    4: "hidden_moth_clearing",
    5: "hidden_moth_clearing",
    6: "whispering_oak",
    7: "underground_starlight_river",
}
MAJOR_CLUES = {"northern star", "lantern", "map", "moth", "shield", "underground river",
               "door", "second star", "blue", "knocks", "star"}


def load_script(path: Path):
    script=json.loads(path.read_text(encoding="utf-8"))
    lines=script.get("lines")
    if script.get("version") != 1 or not isinstance(lines,list) or len(lines)<25:
        raise ValueError("Needs complete original episode, not a trailer")
    required={"luma","pip","narrator"}
    if set(x.get("speaker") for x in lines)!=required:
        raise ValueError("Exactly three canon speaking identities required")
    acts=sorted({x.get("act") for x in lines})
    if acts!=list(range(1,8)):
        raise ValueError("Expected all seven canonical dramatic acts")
    if len(script.get("acts",[]))!=7:
        raise ValueError("Seven act continuity notes required")
    for i,line in enumerate(lines):
        if line["speaker"] not in SPEAKERS or line.get("emotion") not in EMOTIONS:
            raise ValueError(f"Invalid actor emotion in line {i+1}")
        if not line["text"].strip() or len(line["text"])>380:
            raise ValueError(f"Invalid spoken text in line {i+1}")
        if line["act"] not in LOCATION_BY_ACT:
            raise ValueError("Missing act location")
    return script


def estimate_timeline(script, wpm=150, pause_seconds=.13):
    if not 110 <= wpm <= 200:
        raise ValueError("Words/minute should reflect acting, not fast advertising")
    if not 0 <= pause_seconds <= .6:
        raise ValueError("Unrealistic speech pause")
    result=[]
    t=0.0
    prev_act=0
    for i,line in enumerate(script["lines"]):
        words=len(line["text"].split())
        if line["act"]!=prev_act:
            t+=.75 if prev_act else 0
            prev_act=line["act"]
        length=(words*60.0/wpm)+(0.22 if line["emotion"] in ("wonder","concern","gentle") else .08)
        start=t
        end=start+length
        result.append({"line_index":i,"line_number":i+1,"act":line["act"],
                       "start":round(start,3),"end":round(end,3),
                       "speaker":line["speaker"],"emotion":line["emotion"],
                       "text":line["text"],"estimated":True})
        t=end+pause_seconds
    duration=round(t,3)
    if not 240 <= duration <= 480:
        raise ValueError(f"Story duration {duration:.1f}s outside 4–8 minute episode goal")
    return duration, result


def shot_type(index:int, act:int, speaker:str, line:dict, last_kind:str):
    text=line["text"].lower()
    if index == 0:
        return "establishing"
    if act == 7 and ("door" in text or "stars" in text) and speaker=="narrator":
        return "wide_reveal"
    if ("lantern" in text or "map" in text) and speaker=="narrator" and index%5==0:
        return "insert_lantern"
    if speaker == "narrator":
        return "two_shot" if last_kind!="two_shot" else "establishing"
    kinds=(("luma_medium","over_shoulder_pip","reaction_pip") if speaker=="luma" else
           ("pip_medium","over_shoulder_luma","reaction_luma"))
    chosen=kinds[index%len(kinds)]
    if chosen==last_kind:
        chosen=kinds[(index+1)%len(kinds)]
    return chosen


def get_acting(speaker, emotion, act):
    # Every beat has intent, eyeline and a bone-level performance request.
    arc = {
        "wonder": ("gaze_at_clue","eyes_widen_then_settle","curious_reach"),
        "concern": ("look_to_partner","brows_draw_in","weighted_step_back"),
        "curious": ("eyes_to_detail","one_brow_lift","lean_and_point"),
        "gentle": ("look_to_partner","soft_smile","offer_open_palm"),
        "excited": ("face_forward","smile_eyes","anticipation_then_bounce"),
        "urgent": ("look_to_partner","breath_catch","hold_ground_pose"),
        "hopeful": ("partner_then_goal","soft_smile","shared_forward_step"),
    }
    eye, face, body=arc[emotion]
    if speaker=="narrator":
        return {"actor":"narrator","body_animation":"none","facial":None,
                "eyeline":None,"voice_intent":emotion}
    return {"actor":speaker,"body_animation":body, "facial":face,
            "eyeline":eye,"voice_intent":emotion,
            "reference_rig":"ORIGINAL_CHARACTER_REQUIRED",
            "physical_contact":"verify foot-ground weight and believable reach"}


def make_shot_plan(script, wpm=150):
    if any(line.get('act') not in LOCATION_BY_ACT for line in script['lines']):
        raise ValueError('Unknown act / location: canonical seven-act continuity broken')
    duration, timeline=estimate_timeline(script,wpm)
    # Arrange shots at line starts, but ensure no audience-fatiguing flash cuts;
    # consolidate consecutive lines in the same act until at least 5s.
    shots=[]
    current=None
    line_by_index={x["line_index"]:x for x in timeline}
    for t in timeline:
        source=script["lines"][t["line_index"]]
        act=t["act"]
        speaker=t["speaker"]
        same_act=current is not None and current["act"]==act
        elapsed_before_line=(t["start"]-current["start"]) if current else 0
        # Trigger justified new shots when speaker changes after 5s, or an
        # act boundary, or a reveal. Avoid 1-frame camera changes.
        threshold=(7.0 if source["emotion"]=="urgent" else 8.25)
        new_shot = (current is None or not same_act or
                    (elapsed_before_line>=threshold and
                     (speaker!=current["last_speaker"] or elapsed_before_line>=14.5)))
        if new_shot:
            k=shot_type(t["line_index"],act,speaker,source,shots[-1]["framing"] if shots else "")
            current={"shot":len(shots)+1,"act":act,"location":LOCATION_BY_ACT[act],
                     "framing":k,"camera_motion":"locked_or_motivated_track",
                     "start":t["start"],"end":t["end"],"line_numbers":[t["line_number"]],
                     "last_speaker":speaker,"blocking":[get_acting(speaker,source["emotion"],act)],
                     "continuity":{"characters":"identity_stable", "wardrobe":"canonical",
                                   "world_space":"persistent_across_cuts"},
                     "render_status":"NOT_RENDERED",
                     "editorial_purpose":source.get("beat","").strip()}
            shots.append(current)
        else:
            current["end"]=t["end"]
            current["line_numbers"].append(t["line_number"])
            current["last_speaker"]=speaker
            current["blocking"].append(get_acting(speaker,source["emotion"],act))
    if len(shots)<20 or len(shots)>90:
        raise ValueError("Implausible storyboard coverage/cutting rate")
    for i,shot in enumerate(shots):
        if shot["end"]<=shot["start"]:
            raise ValueError("Non-positive camera shot")
        if i and shot["start"]<shots[i-1]["end"]-0.005:
            raise ValueError("Overlapping shot time")
        shot.pop("last_speaker")
    return {
        "type":"MOVIE_PRODUCTION_PLAN_NOT_A_FILM",
        "film_ready":False, "version":1,
        "series":script["series"], "episode":script["episode"],
        "story_duration_seconds":duration,
        "render_fps":24, "target_resolution":[1920,1080],
        "shots":shots, "timeline":timeline,
        "missing_for_release":[
            "finished licensed ORIGINAL rigged fox/rabbit characters",
            "recorded and human-reviewed distinct expressive voices",
            "mocap/hand-keyed believable full-body acting and FACS face",
            "motivated 3D environments, lighting, materials and camera staging",
            "real feature-quality rendered shots and score",
            "completed 4-8 minute final audio/video master",
            "independent full-motion and narrative quality approval",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("script",type=Path)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--words-per-minute",type=float,default=150)
    a=p.parse_args()
    plan=make_shot_plan(load_script(a.script),a.words_per_minute)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"original_lines":len(plan["timeline"]),
                      "dramatically_motivated_camera_shots":len(plan["shots"]),
                      "estimated_duration_seconds":plan["story_duration_seconds"],
                      "film_ready":plan["film_ready"],
                      "output":str(a.out)}))


if __name__=="__main__":
    main()
