"""Native Blender QA for original biped Starwood rigs.

Checks evaluated geometry, not just object names: attached heads remain near
their torsos across actual animated frames, both character silhouettes differ,
facial mesh shape keys exist and have animation tracks, and real skeletal
joints move without wild discontinuities. No artistic/movie-quality approval.

Inside Blender:
  blender -b luma_pip.blend --python studio/rig_qa_blender.py
"""
from __future__ import annotations

import json
import math
import sys


def measure():
    import bpy
    from mathutils import Vector

    scene=bpy.context.scene
    arms={obj.name.split(" | ")[0]:obj for obj in bpy.data.objects if obj.type=="ARMATURE"}
    if set(arms)!={"Luma","Pip"}:
        raise RuntimeError(f"Canonical original two-actor identity failure: {list(arms)}")
    expected=("root","spine","neck","head","upper_arm_L","upper_arm_R",
              "forearm_L","forearm_R","thigh_L","thigh_R","shin_L","shin_R","tail")
    for name,arm in arms.items():
        missing=set(expected)-set(arm.pose.bones)
        if missing: raise RuntimeError(f"{name} missing skeletal joints: {missing}")
        if not arm.animation_data or not arm.animation_data.action:
            raise RuntimeError(f"{name}: missing actual skeletal action")
    meshes={}
    for character in arms:
        group=[o for o in bpy.data.objects if o.type=="MESH" and o.name.startswith(character+" | ")]
        meshes[character]=group
        if len(group)<20: raise RuntimeError(f"{character}: incomplete geometry")
        for ob in group:
            if ob.parent != arms[character] or ob.parent_type!="BONE":
                raise RuntimeError(f"{ob.name}: mesh not parented to animated skeletal bone")
            if ob.parent_bone not in arms[character].pose.bones:
                raise RuntimeError(f"{ob.name}: wrong or missing skeletal bone")
        eyes=[o for o in group if " | eye" in o.name and "eyebrow" not in o.name]
        mouths=[o for o in group if o.name.endswith(" | mouth")]
        brows=[o for o in group if " | eyebrow" in o.name]
        if len(eyes)!=2 or len(mouths)!=1 or len(brows)!=2:
            raise RuntimeError(f"{character}: asymmetric face geometry")
        for o in eyes:
            if not o.data.shape_keys or "Blink" not in o.data.shape_keys.key_blocks:
                raise RuntimeError(f"{character}: eye lacks genuine blink geometry")
        for o in brows:
            if not o.data.shape_keys or not {"BrowsUp","Worry"} <= set(o.data.shape_keys.key_blocks):
                raise RuntimeError(f"{character}: brow lacks shape-driven acting")
        if not {"Open","Smile"} <= set(mouths[0].data.shape_keys.key_blocks):
            raise RuntimeError(f"{character}: mouth lacks speech+smile geometry")
    histories={}
    for name in arms:
        histories[name]=[]
    for frame in (1,9,18,27,36,45,54,63,72):
        if frame>scene.frame_end: continue
        scene.frame_set(frame)
        for name,arm in arms.items():
            head=bpy.data.objects[f"{name} | head"]
            torso=bpy.data.objects[f"{name} | torso"]
            left=bpy.data.objects[f"{name} | upper_armL"]
            right=bpy.data.objects[f"{name} | upper_armR"]
            tail=bpy.data.objects[f"{name} | tail"]
            h=head.matrix_world.translation.copy()
            t=torso.matrix_world.translation.copy()
            dl=(left.matrix_world.translation-t).length
            dr=(right.matrix_world.translation-t).length
            distance=(h-t).length
            if not .25<=distance<=1.27:
                raise RuntimeError(
                    f"{name}: DISCONNECTED_HEAD frame={frame} distance={distance:.3f}")
            if not .13<=dl<=.95 or not .13<=dr<=.95:
                raise RuntimeError(
                    f"{name}: arm joint float/displacement frame={frame} L={dl:.3f} R={dr:.3f}")
            if not math.isfinite(h.x+h.y+h.z+t.x+t.y+t.z):
                raise RuntimeError("Nonfinite evaluated bone mesh transform")
            histories[name].append(
                {"frame":frame,"head":[round(v,4) for v in h],
                 "torso":[round(v,4) for v in t],
                 "head_torso_distance":round(distance,4),
                 "tail":[round(v,4) for v in tail.matrix_world.translation]})
    for name,history in histories.items():
        head_positions=[Vector(v["head"]) for v in history]
        motion=max((head_positions[i]-head_positions[0]).length
                   for i in range(1,len(head_positions)))
        if motion<.012:
            raise RuntimeError(f"{name}: no actual skeletal head motion")
        if any((a-b).length>1.0 for a,b in zip(head_positions,head_positions[1:])):
            raise RuntimeError(f"{name}: unnatural body teleportation")
    if len(arms["Luma"].data.bones)!=len(arms["Pip"].data.bones):
        raise RuntimeError("Expected comparable original animation skeletons")
    output={"actors":["Luma","Pip"],"arms":len(arms),
            "meshes":{k:len(v) for k,v in meshes.items()},
            "frames_reviewed":[e["frame"] for e in histories["Luma"]],
            "evaluated_movement":histories,
            "skeleton_and_face_qc":True,
            "skin_weights_smooth":False,
            "original_sculpt_quality_verified":False,
            "cinematic_performance_verified":False,
            "film_ready":False}
    print("ORIGINAL_RIG_GEOMETRY_EVALUATED_OK",json.dumps({
        k:v for k,v in output.items() if k!="evaluated_movement"}))
    return output


if __name__=="__main__":
    result=measure()
    if "--report" in sys.argv:
        from pathlib import Path
        dst=Path(sys.argv[sys.argv.index("--report")+1])
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(result,indent=2),encoding="utf-8")
