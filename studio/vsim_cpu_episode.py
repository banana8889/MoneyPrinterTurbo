"""Turn Starwood EP1 into *actual renderable* vsim Film3D acts (CPU-first).

Based on the verified MIT vsim Film3D schema and native animated fox/rabbit
cast. Each act is a self-contained <=90s real 3D scene, so it can be rendered
independently on free GitHub Actions CPUs. Frames are not a comic slideshow:
fox Walk/Survey/Run and rabbit idle/walk/run are skeletal clips.
Native VSIM narrator defaults to robotic espeak; omit narration entirely and
use independently recorded/licensed original dialogue from cast report during
the final offline audio-compositing phase.

Upstream source commit pinned by CI; Fox third-party glTF CC-BY requires the
original Khronos sample rigging/animation credit, rabbit is MIT vsim original.
These are NON-FINAL reference characters, not a cinematic release.

Usage:
  python -m studio.vsim_cpu_episode --script studio/season1_episode1_full.json \
    --out /tmp/starwood_vsim --act 1 [--cast-report /private/cast_report.json]
  python -m studio.vsim_cpu_episode --script ... --out ... [--cast-report ...]
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

ACT_LOOK = {1:"dusk",2:"autumn",3:"dusk",4:"dusk",5:"dusk",6:"dusk",7:"night"}
ACT_WEATHER = {1:"fireflies",2:"leaves",3:"fireflies",4:"fireflies",
               5:"fireflies",6:"fireflies",7:"fireflies"}
VALID_EMOTION = {"wonder","curious","concern","gentle","excited","urgent","hopeful"}
POS = {"luma":[-2.2,0.0],"pip":[2.1,0.3]}
CODEC_CREDITS = {
  "engine":"vsim (c) 2026 vsim contributors, MIT",
  "fox":"Fox model PixelMannen CC0; rig+animation @tomkranis CC BY 4.0; conversion AsoboStudio/scurest CC BY 4.0",
  "rabbit":"vsim original regenerated rigged animal, MIT",
  "limits":"Fox and rabbit are rigged but NOT original professional Starwood designs or emotive facial performers"
}

def read_story(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    lines=obj.get("lines")
    if obj.get("version")!=1 or not isinstance(lines,list) or len(lines)<40:
        raise ValueError("Full seven-act screenplay required")
    if sorted({l.get("act") for l in lines})!=list(range(1,8)):
        raise ValueError("Need seven consecutive acts")
    if set(l["speaker"] for l in lines)!={"luma","pip","narrator"}:
        raise ValueError("Need both hero characters and narrator")
    if any(l.get("emotion") not in VALID_EMOTION for l in lines):
        raise ValueError("Unsupported acting direction")
    return obj

def line_timing(story,cast=None,wpm=150):
    """Use *actual* synthesis receipts whenever present; else estimated ONLY."""
    if cast is not None:
        record=json.loads(Path(cast).read_text(encoding="utf-8"))
        rows=record.get("lines",[])
        if len(rows)!=len(story["lines"]) or record.get("approval") is True:
            # Technical cast data cannot assert subjective acting approval.
            raise ValueError("Cast report must match complete source and remain unreviewed")
        mapped=[]
        for source, spoken in zip(story["lines"],rows):
            if source["speaker"]!=spoken["speaker"] or source["text"]!=spoken["text"]:
                raise ValueError("Recorded cast identity/text mismatch")
            a,b=float(spoken["start_seconds"]),float(spoken["end_seconds"])
            if not 0<=a<b or not math.isfinite(b):
                raise ValueError("Invalid measured audio interval")
            mapped.append({"start":a,"end":b,"speaker":source["speaker"],
                           "text":source["text"],"emotion":source["emotion"],"act":source["act"]})
        if record["duration_seconds"]<mapped[-1]["end"]-0.03:
            raise ValueError("Spoken timeline truncation")
        return mapped,False
    # First use the 84 actual recorded Kokoro timings from our successful
    # original EP1 speech run, not the old 430s word-count estimate. This
    # baseline is still synthetic/NOT human-quality approved.
    if story.get("episode") == 1 and len(story.get("lines", [])) == 84:
        from studio.episode1_measured_voice_timing import measured_voices
        return measured_voices(story), False
    from studio.film_shot_planner import estimate_timeline
    _, est=estimate_timeline(story,wpm=wpm)
    return [{"start":v["start"],"end":v["end"],"act":v["act"],
             "text":v["text"],"speaker":v["speaker"],"emotion":v["emotion"]}
            for v in est],True

def tree_props(act):
    # Real geometry: no empty scene, flat shape slides or external paid images.
    props=[]
    for i,(x,z,height) in enumerate([(-8,-7,4),(-5,-9,3.4),(6,-8,4.8),(9,-5,3.3),(-10,3,2.6)]):
        props.append({"kind":"tree","id":f"tree{i}","x":x,"z":z,"height":height,
                      "variant":"broadleaf" if i%2 else "conifer"})
    props.extend([{"kind":"bush","id":"bush","x":-6,"z":2,"radius":.8},
                  {"kind":"rock","id":"rock","x":7,"z":2,"radius":.5},
                  {"kind":"flowers","id":"wildflowers","x":4,"z":3,"radius":1.1}])
    if act in (3,4,5,6,7):
        props.append({"kind":"lantern","id":"northlantern","x":0,"z":-1})
    if act in (4,5,7):
        props.append({"kind":"pond","id":"pond","x":3,"z":-4,"radius":1.7})
    return props

def beats_for_act(story,timeline,act,technical_seconds=None):
    rows=[t for t in timeline if t["act"]==act]
    if not rows:
        raise ValueError("No act dialogue")
    t0=rows[0]["start"];end=rows[-1]["end"]
    if not 0<end-t0<89:
        raise ValueError(f"Act {act} exceeds native 90-second film3d schema")
    if technical_seconds is not None:
        if not .5<=technical_seconds<=15:
            raise ValueError("Technical test span must be between 0.5 and 15s")
        end=min(end,t0+technical_seconds)
    # Film3D's upstream validator uses STRICT JS float equality for camera
    # segment chaining; quantize to binary-exact 1/16-second timecodes.
    # Avoid the 31.560000000000002 vs 31.56 failure of decimal floats.
    tick=lambda x:round(x*16)/16
    duration=tick(end-t0)
    # Beats are contiguous with no duplicate camera paths and no hard cut
    # every utterance. Let actors perform for 8-13 seconds between edits.
    boundaries=[0.0]
    for row in rows:
        s=tick(max(0,min(duration,row["start"]-t0)))
        if s-boundaries[-1]>=9 and duration-s>=2.5:
            boundaries.append(s)
    boundaries.append(duration)
    if any(b<=a for a,b in zip(boundaries,boundaries[1:])):
        raise ValueError("Film beats must be positive and contiguous")
    beats=[];camera=[]
    pos={"luma":list(POS["luma"]),"pip":list(POS["pip"])}
    for i,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
        dialogue=[r for r in rows if r["start"]-t0 < b and r["end"]-t0 > a]
        speaking=next((r["speaker"] for r in dialogue if r["speaker"]!="narrator"),"luma" if i%2==0 else "pip")
        emo=next((r["emotion"] for r in dialogue if r["speaker"]==speaking),"curious")
        partner="pip" if speaking=="luma" else "luma"
        actions=[]
        actions.append({"do":"face","actor":speaking,"to":pos[partner],"at":0,"dur":.6})
        actions.append({"do":"face","actor":partner,"to":pos[speaking],"at":.1,"dur":.6})
        # Single real path-based gait, not position teleportation.
        # Vary by emotional intent but keep silhouettes in stage coordinates.
        if (i+act)%3==0 and b-a>=3.5:
            old=pos[speaking]
            target=[round(max(-3.2,min(3.2,old[0]+(1.75 if speaking=="luma" else -1.75))),2),old[1]]
            actions.append({"do":"move","actor":speaking,"to":target,
                            "at":1.0,"dur":min(2.4,b-a-1.2),"gait":"walk"})
            pos[speaking]=target
        else:
            actions.append({"do":"play","actor":speaking,
                            "clip":"Survey" if speaking=="luma" else "idle",
                            "at":0.7,"dur":max(0.25,b-a-.9)})
        actions.append({"do":"play","actor":partner,
                        "clip":"idle" if partner=="pip" else "Survey",
                        "at":0,"dur":max(.2,b-a-.3)})
        beats.append({"id":f"beat{i+1}","start":a,"end":b,
                      
                      "actions":actions})
        kind="wide" if i==0 or i%4==3 else "close" if i%4==2 else "follow"
        cam={"at":a,"dur":b-a,"shot":kind,
             "target":speaking if kind!="wide" else [0,0,0],
             "angle":(-18 if i%2==0 else 20),"fov":40 if kind=="wide" else 36}
        if kind=="wide":
            cam.update({"distance":5.8,"height":1.8})
        elif kind=="close":
            cam.update({"distance":2.8,"height":1.2})
        else:
            cam.update({"distance":3.4,"height":1.4})
        camera.append(cam)
    return beats,camera,duration,t0

def generate(story,timeline,act,technical_seconds=None):
    beats,camera,duration,offset=beats_for_act(story,timeline,act,technical_seconds)
    if not beats or duration>90:
        raise ValueError("No renderable act")
    doc={"version":"film3d-1","title":"",
         "fps":24,"set":ACT_LOOK[act],"weather":ACT_WEATHER[act],
         "props":tree_props(act),
         "actors":[{"id":"luma","character":"fox","x":POS["luma"][0],"z":POS["luma"][1],"facing":POS["pip"]},
                   {"id":"pip","character":"rabbit","x":POS["pip"][0],"z":POS["pip"][1],"facing":POS["luma"]}],
         "beats":beats,"camera":camera}
    return doc,{"act":act,"duration_seconds":duration,
                "source_audio_offset_seconds":round(offset,4),"estimated_voice_timing":technical_seconds is None and not False,
                "native_3d_body_animation":True, "original_studio_quality_characters":False,
                "natural_acted_dialogue":False,"film_ready":False}

def build(script,output,act=None,cast_report=None,technical_seconds=None):
    story=read_story(script)
    timeline,estimated=line_timing(story,cast_report)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for a in ([act] if act else range(1,8)):
        if a not in ACT_LOOK:
            raise ValueError("Act number 1-7")
        doc,rec=generate(story,timeline,a,technical_seconds)
        rec["estimated_voice_timing"]=estimated
        rec["technical_cut"]=technical_seconds is not None
        scene=output/f"starwood_act{a}.film3d.json"
        scene.write_text(json.dumps(doc,indent=2,ensure_ascii=False),encoding="utf-8")
        summaries.append(rec)
    receipt={"state":"STAGE_READY_NOT_CINEMATIC_FILM",
             "engine":"vsim","renderer_license":"MIT",
             "assets_credits":CODEC_CREDITS,"acts":summaries,
             "all_seven_acts_compiled":len(summaries)==7,
             "has_hero_grade_original_characters":False,
             "human_voice_acting_approved":False,
             "measured_voice_baseline_not_human_quality":not estimated,
             "film_ready":False}
    (output/"stage_receipt.json").write_text(json.dumps(receipt,indent=2),
                                               encoding="utf-8")
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--script",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--cast-report",type=Path)
    p.add_argument("--act",type=int,choices=range(1,8))
    p.add_argument("--technical-seconds",type=float)
    a=p.parse_args()
    r=build(a.script,a.out,a.act,a.cast_report,a.technical_seconds)
    print(json.dumps({"acts":len(r["acts"]),
                      "duration":sum(x["duration_seconds"] for x in r["acts"]),
                      "film_ready":False,"engine":"vsim CPU Film3D"}))

if __name__=="__main__":
    main()
