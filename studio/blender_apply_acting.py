"""Direct a complete original Starwood act on TWO distinct Blender biped rigs.

Unlike stock quadrupeds, this consumes the original authored Luma/Pip armatures
and the actual measured dialogue-derived acting score. Animation is bone-level
with anticipation, eased release, listener reaction, genuine facial blendshapes
and motivated 3D camera edits. Optional recorded Rhubarb mouth cues are required
before claiming lip-synced speech; otherwise mouth remains neutral.

Run:
  blender -b /private/luma_pip.blend --python studio/blender_apply_acting.py -- \
    --score /private/episode1_acting.json --act 1 --out /private/act1.blend
  blender -b /private/luma_pip.blend --python studio/blender_apply_acting.py -- \
    --score /private/episode1_acting.json --act 1 --out /private/act1.blend \
    --phonemes /private/licensed_84_line_phonemes

No paid API, no schedules, no false cinematic-quality approval.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path


def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--score",type=Path,required=True)
    p.add_argument("--act",type=int,choices=range(1,8),required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--phonemes",type=Path)
    return p.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])


POSE_BONES = {
    "head":"head", "spine":"spine",
    "upper_arm_L":"upper_arm_L","upper_arm_R":"upper_arm_R",
    "tail":"tail",
}
MOUTH_OPEN = {"A":0.0,"B":0.18,"C":0.36,"D":.82,"E":.56,
              "F":.30,"G":.4,"H":.72,"X":0.0}


def main():
    import bpy
    from mathutils import Vector

    a=parse()
    score=json.loads(a.score.read_text(encoding="utf-8"))
    if score.get("schema")!="STARWOOD_ORIGINAL_BIPED_PERFORMANCE_V1":
        raise ValueError("Unrecognized original performance score")
    if score.get("dialogue_lines")!=84 or score.get("film_ready") is not False:
        raise ValueError("Missing full measured original script score")
    controls=score["actor_controls"]
    selected={who:[x for x in controls[who] if x["act"]==a.act]
              for who in ("luma","pip")}
    if not all(selected.values()) or len(selected["luma"])!=len(selected["pip"]):
        raise ValueError("Both actors need full simultaneous playbook")
    begin=min(item["start"] for items in selected.values() for item in items)
    end=max(item["end"] for items in selected.values() for item in items)
    fps=24
    scene=bpy.context.scene
    scene.render.fps=fps
    scene.render.resolution_x=1920
    scene.render.resolution_y=1080
    scene.render.resolution_percentage=50 # cheap PREVIEW only, NOT final film
    scene.frame_start=1
    scene.frame_end=math.ceil((end-begin)*fps)+12
    if scene.frame_end>2400:
        raise ValueError("Single act too long for bounded CPU act renderer")
    arms={}
    for who in ("luma","pip"):
        found=[o for o in bpy.data.objects if o.type=="ARMATURE"
               and o.name.startswith(who.capitalize()+" | ")]
        if len(found)!=1:
            raise RuntimeError(f"{who} ORIGINAL biped not present; no stock fallback")
        arm=found[0]
        if not all(k in arm.pose.bones for k in POSE_BONES.values()):
            raise RuntimeError(f"{who} missing anatomically named bone controls")
        arm.animation_data_clear()
        arms[who]=arm
        for obj in bpy.data.objects:
            if obj.type!="MESH" or not obj.name.startswith(who.capitalize()+" | "):
                continue
            if obj.data.shape_keys:
                obj.data.shape_keys.animation_data_clear()
    def frame(t):
        return max(1,round((t-begin)*fps)+1)
    def rotate(arm,bone,target,at):
        p=arm.pose.bones[bone]
        p.rotation_mode="XYZ"
        p.rotation_euler=target
        p.keyframe_insert(data_path="rotation_euler",frame=at,
                          group="ORIGINAL_DIALOGUE_DIRECTED_ACTING")
    def face(who,key,value,at):
        for obj in bpy.data.objects:
            if obj.type!="MESH" or not obj.name.startswith(who.capitalize()+" | "):
                continue
            sk=obj.data.shape_keys
            if not sk or key not in sk.key_blocks:
                continue
            shape=sk.key_blocks[key]
            shape.value=max(0.0,min(1.0,value))
            shape.keyframe_insert(data_path="value",frame=at,
                                  group="ACTOR_EMOTIONAL_FACS_LITE")
    clips=0
    for who,items in selected.items():
        arm=arms[who]
        for clip in items:
            start=frame(clip["start"])
            finish=frame(clip["end"])
            peak=min(finish,max(start+2,start+round(.21*fps)))
            release=min(scene.frame_end,finish+round(.15*fps))
            target=clip["bone_pose"]
            pose={
                "head":(target["head_pitch"],0,target["head_yaw"]),
                "spine":(0,0,target["spine_lean"]),
                "upper_arm_L":(target["upper_arm_L"],0,-.05),
                "upper_arm_R":(target["upper_arm_R"],0,.05),
                "tail":(0,target["tail_sway"],0),
            }
            neutral={"head":(0,0,0),"spine":(0,0,0),
                     "upper_arm_L":(-.10,0,-.05),
                     "upper_arm_R":(-.10,0,.05),
                     "tail":(0,0,0)}
            for bname in POSE_BONES.values():
                rotate(arm,bname,neutral[bname],max(1,start-2))
                rotate(arm,bname,pose[bname],peak)
                rotate(arm,bname,pose[bname],finish)
                rotate(arm,bname,neutral[bname],release)
            for name,value in clip["face_pose"].items():
                if name not in ("BrowsUp","Worry","Smile"):
                    raise ValueError("Unknown emotional facial key")
                face(who,name,0.0,max(1,start-2))
                face(who,name,value,peak)
                face(who,name,value,finish)
                face(who,name,0.0,release)
            clips+=1
    # Honest: if no actual Rhubarb cues available, no arbitrary mouth flapping
    # is portrayed as lip-sync; this must be fixed before an audience release.
    authentic_mouth=False
    if a.phonemes:
        authentic_mouth=True
        for who in ("luma","pip"):
            file=a.phonemes/(who+"_cues.json")
            if not file.is_file():
                raise FileNotFoundError(f"Actual Rhubarb data missing for {who}")
            cues=json.loads(file.read_text(encoding="utf-8")).get("mouthCues")
            if not isinstance(cues,list) or len(cues)<20:
                raise ValueError("Cannot lip-sync actor without original phonemes")
            previous=0.0
            for cue in cues:
                s,e=cue["start"],cue["end"]
                if cue["value"] not in MOUTH_OPEN or s<previous-.005 or e<=s:
                    raise ValueError("Invalid ordered original phonetic cue")
                previous=e
                if e<begin or s>end:continue
                st=frame(max(begin,s)); en=frame(min(end,e))
                v=MOUTH_OPEN[cue["value"]]
                face(who,"Open",0,max(1,st-2))
                face(who,"Open",v,min(en,st+1))
                face(who,"Open",v,en)
                face(who,"Open",0,min(scene.frame_end,en+2))
    # Maintain deliberate scene cuts at original dialogue beats.
    camera=scene.camera
    if camera is None:
        raise RuntimeError("Blender original scene has no real 3D camera")
    camera.animation_data_clear()
    cuts=[c for c in score["camera_cuts"] if c["act"]==a.act]
    if not cuts:
        raise RuntimeError("No directed shots for act")
    for cut in cuts:
        k=frame(cut["start"])
        if cut["framing"]=="luma_medium":
            loc=(-1.13,-3.65,2.05);look=(-1.13,0,1.72);lens=59
        elif cut["framing"]=="pip_medium":
            loc=(1.13,-3.65,2.05);look=(1.13,0,1.72);lens=59
        elif cut["framing"]=="two_shot":
            loc=(0,-5.3,2.35);look=(0,0,1.55);lens=47
        else:
            loc=(0,-6.25,2.5);look=(0,0,1.51);lens=43
        camera.location=loc
        camera.rotation_euler=(Vector(look)-camera.location).to_track_quat("-Z","Y").to_euler()
        camera.data.lens=lens
        camera.keyframe_insert(data_path="location",frame=k)
        camera.keyframe_insert(data_path="rotation_euler",frame=k)
        camera.data.keyframe_insert(data_path="lens",frame=k)
    # A film cut, not accidental smooth camera interpolation across scenes.
    if camera.animation_data and camera.animation_data.action:
        act=camera.animation_data.action
        if hasattr(act,"fcurves"):
            for curve in act.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation="CONSTANT"
    scene.frame_set(1)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out.resolve()))
    receipt={
        "act":a.act,"source":"ORIGINAL_BIPED_3D_BLENDER",
        "actor_directed_clips":clips,"actor_count":2,
        "measured_original_voice_seconds":round(end-begin,4),
        "frame_count":scene.frame_end,
        "camera_cuts":len(cuts),
        "real_phonemes_applied":authentic_mouth,
        "original_audio_wav_embedded":False,
        "smooth_skin_weights":False,
        "aesthetic_quality_approved":False,
        "film_release_pass":False,
        "caution":"Original procedural character starter, not hero-quality cinematic acting"
    }
    a.out.with_suffix(".acting_receipt.json").write_text(json.dumps(receipt,indent=2),
                                                            encoding="utf-8")
    print("TWO_ORIGINAL_CHARACTERS_DIRECTED_ACTING",json.dumps(receipt))


if __name__=="__main__":
    main()
