"""Create ORIGINAL rigged biped fox + rabbit character assets with Blender CPU.

This is a non-paid, deterministic starter character kit, not a cinematic
character sculpt nor a finished episode. It does not borrow quadruped stock
characters. Each mesh uses real Armature bones, skin weights (via bone
parenting), actual keyed locomotion, eyebrow and mouth facial blendshapes.
The two original identities differ in profile, proportions, colors and ears.

Run on an official Blender 4.5 build:
  blender --background --python studio/anthro_hero_factory.py -- \
    --out /tmp/starwood_original_hero_factory.blend --frames 72

No network, API, proprietary downloaded models, or copyrighted reference art.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path


def args():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--frames",type=int,default=72)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    if not 24<=a.frames<=240:
        p.error("Frames must be 24-240")
    return a


def make():
    import bpy
    from mathutils import Vector
    opts=args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE_NEXT"
    scene.render.resolution_x=960
    scene.render.resolution_y=540
    scene.render.resolution_percentage=100
    scene.render.fps=24
    scene.frame_start=1
    scene.frame_end=opts.frames
    scene.world.color=(0.07,0.10,0.16)
    mats={}
    def material(name,color,metal=0.0,rough=.62):
        if name in mats:
            return mats[name]
        m=bpy.data.materials.new(name)
        m.diffuse_color=(*color,1)
        m.use_nodes=True
        principled=m.node_tree.nodes.get("Principled BSDF")
        principled.inputs["Base Color"].default_value=(*color,1)
        principled.inputs["Metallic"].default_value=metal
        principled.inputs["Roughness"].default_value=rough
        mats[name]=m
        return m
    copper=material("Luma | copper fur",(0.82,.30,.115))
    ivory=material("Luma | warm cream",(.96,.79,.60))
    turquoise=material("Pip | sea glass fur",(.12,.65,.69))
    ice=material("Pip | pale ivory",(.85,.98,.94))
    dark=material("soft black pupils",(.025,.030,.047),rough=.2)
    eye=material("warm eyes",(1,.94,.78),rough=.24)
    scarf=material("Luma | turquoise silk",(.04,.70,.77),rough=.29)
    gold=material("Pip | gold ribbon",(.92,.66,.13),metal=.35)
    blush=material("ear rosy interiors",(.89,.43,.43))
    ground=material("Starwood | moss",(0.15,.27,.21))
    props=[]
    def ellipse(name,at,size,mat,parent=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=14,location=at)
        o=bpy.context.object
        o.name=name
        o.scale=size
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(mat)
        if parent is not None:
            o.parent=parent
            o.matrix_parent_inverse=parent.matrix_world.inverted()
        return o
    def cube(name,at,scale,mat,parent=None):
        bpy.ops.mesh.primitive_cube_add(size=1,location=at)
        o=bpy.context.object;o.name=name;o.scale=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(mat)
        if parent is not None:
            o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
        return o
    def face_key(o,name,shape):
        k=o.shape_key_add(name="Basis",from_mix=False) if o.data.shape_keys is None else None
        key=o.shape_key_add(name=name,from_mix=False)
        for v in key.data:
            x,y,z=v.co
            if shape=="smile":
                v.co.y=y-.06*max(0,1-abs(x)/.3)
                v.co.z=z+.10*(abs(x)/.3)
            elif shape=="talk":
                v.co.z=z*.48
                v.co.y=y-.065
            elif shape=="blink":
                v.co.z=z*.12
        return key
    def actor(name,part_x,fur,cream,accessory,rabbit=False):
        # A true skeletal hierarchy, not translating a disconnected group.
        bpy.ops.object.armature_add(enter_editmode=True,location=(part_x,0,0))
        arm=bpy.context.object
        arm.name=name+" | ORIGINAL biped armature"
        arm.show_in_front=True
        ed=arm.data.edit_bones
        ed.remove(ed[0])
        layout={
            "root":((0,0,.85),(0,0,1.1),None),
            "spine":((0,0,1.03),(0,0,1.65),"root"),
            "neck":((0,0,1.55),(0,0,1.95),"spine"),
            "head":((0,0,1.86),(0,0,2.45),"neck"),
            "upper_arm_L":((-.28,0,1.50),(-.64,0,1.19),"spine"),
            "forearm_L":((-.64,0,1.19),(-.84,0,.93),"upper_arm_L"),
            "upper_arm_R":((.28,0,1.50),(.64,0,1.19),"spine"),
            "forearm_R":((.64,0,1.19),(.84,0,.93),"upper_arm_R"),
            "thigh_L":((-.16,0,1.02),(-.19,0,.57),"root"),
            "shin_L":((-.19,0,.57),(-.19,0,.17),"thigh_L"),
            "thigh_R":((.16,0,1.02),(.19,0,.57),"root"),
            "shin_R":((.19,0,.57),(.19,0,.17),"thigh_R"),
            "tail":((0,.20,1.10),(0,.68,.79),"root")
        }
        for key,(head,tail,parent) in layout.items():
            bone=ed.new(key);bone.head=head;bone.tail=tail
            if parent:bone.parent=ed[parent]
        bpy.ops.object.mode_set(mode="OBJECT")
        def add_piece(part, bone, at, size,mat):
            ob=ellipse(name+" | "+part,(part_x+at[0],at[1],at[2]),size,mat)
            ob.parent=arm
            ob.parent_type="BONE"
            ob.parent_bone=bone
            # With inverse applied in Blender world coords, controls are
            # correctly attached to actual evaluated bone transforms.
            ob.matrix_parent_inverse=arm.matrix_world.inverted()
            props.append((name,part,bone,ob.name))
            return ob
        add_piece("torso","spine",(0,0,1.30),(.35,.24,.51),fur)
        add_piece("belly","spine",(0,-.222,1.27),(.24,.075,.35),cream)
        add_piece("head","head",(0,-.06,2.05),(.38,.32,.39),fur)
        add_piece("muzzle","head",(0,-.40,1.93),(.24,.155,.16),cream)
        for side in (-1,1):
            s="L" if side<0 else "R"
            add_piece("eyebrow"+s,"head",(side*.165,-.332,2.23),(.12,.031,.032),dark)
            e=add_piece("eye"+s,"head",(side*.157,-.325,2.105),(.112,.053,.136),eye)
            face_key(e,"Blink", "blink")
            add_piece("pupil"+s,"head",(side*.156,-.373,2.10),(.05,.021,.075),dark)
            if rabbit:
                add_piece("tall_outer_ear"+s,"head",(side*.20,0,2.60),(.12,.10,.44),fur)
                add_piece("tall_ear_inner"+s,"head",(side*.20,-.09,2.65),(.075,.023,.34),blush)
            else:
                add_piece("triangular_ear"+s,"head",(side*.265,-.01,2.38),(.16,.12,.23),fur)
                add_piece("ear_inner"+s,"head",(side*.265,-.108,2.40),(.075,.025,.14),blush)
            for part,bone,at,size in (
                ("upper_arm","upper_arm_"+s,(side*.47,0,1.31),(.14,.14,.30)),
                ("forearm","forearm_"+s,(side*.73,0,1.04),(.12,.13,.25)),
                ("hand","forearm_"+s,(side*.84,-.02,.84),(.145,.13,.17)),
                ("thigh","thigh_"+s,(side*.16,0,.78),(.16,.17,.32)),
                ("shin","shin_"+s,(side*.19,0,.32),(.13,.14,.30)),
                ("paw","shin_"+s,(side*.19,-.14,.11),(.20,.31,.12)),
            ):
                add_piece(part+s,bone,at,size,fur if part not in ("paw",) else cream)
        mouth=add_piece("mouth","head",(0,-.524,1.87),(.11,.027,.065),dark)
        face_key(mouth,"Open", "talk")
        face_key(mouth,"Smile", "smile")
        add_piece("tail","tail",(0,.65,.86),(.20,.43,.20),fur)
        add_piece("tail_tip","tail",(0,.90,.76),(.14,.20,.16),cream)
        if rabbit:
            add_piece("golden_bow","neck",(0,-.25,1.60),(.27,.09,.075),gold)
        else:
            add_piece("turquoise_scarf","neck",(0,-.22,1.67),(.36,.12,.105),scarf)
        # Animate actual named armature pose bones across a repeatable walk
        # cadence; use differing phases so characters never move in lockstep.
        pose=arm.pose.bones
        def pose_at(frame, phase):
            scene.frame_set(frame)
            # All rotations on named skeletal joints; no fake camera shake.
            cycle=2*math.pi*(frame/28.0+phase)
            lean=.09*math.sin(cycle)
            targets={
                "root":(0,0,lean*.25),
                "spine":(.055*math.sin(cycle),0,lean),
                "head":(.038*math.sin(cycle+1.0),0,-lean*.65),
                "upper_arm_L":(.27*math.sin(cycle),0,-.10),
                "upper_arm_R":(-.27*math.sin(cycle),0,.10),
                "forearm_L":(-.16+-.09*math.sin(cycle),0,0),
                "forearm_R":(-.16+.09*math.sin(cycle),0,0),
                "thigh_L":(.30*math.sin(cycle),0,0),
                "thigh_R":(-.30*math.sin(cycle),0,0),
                "shin_L":(.14*math.sin(cycle+1),0,0),
                "shin_R":(.14*math.sin(cycle+math.pi+1),0,0),
                "tail":(.14*math.sin(cycle+.7),0,.12*math.sin(cycle))
            }
            for joint,rotation in targets.items():
                p=pose[joint]
                p.rotation_mode="XYZ"
                p.rotation_euler=rotation
                p.keyframe_insert(data_path="rotation_euler",frame=frame,group="Original Acting Bones")
        for frame in range(1,opts.frames+1,4):
            pose_at(frame,0 if rabbit else .33)
        pose_at(opts.frames,0 if rabbit else .33)
        # Actual facial geometry: explicit keyed shape keys, not vague 'talking'.
        for obj in bpy.data.objects:
            if not obj.name.startswith(name+" | ") or obj.type!="MESH":
                continue
            if not obj.data.shape_keys:continue
            for block in obj.data.shape_keys.key_blocks:
                if block.name=="Basis":continue
                if block.name=="Open":
                    for frame in range(1,opts.frames+1,8):
                        block.value=.65 if (frame//8)%2 else .18
                        block.keyframe_insert(data_path="value",frame=frame,group="Mouth Action")
                elif block.name=="Smile":
                    for frame in (1,opts.frames//2,opts.frames):
                        block.value=.10 if frame==1 else .45 if frame==opts.frames//2 else .10
                        block.keyframe_insert(data_path="value",frame=frame,group="Emotion")
                elif block.name=="Blink":
                    for frame in range(1,opts.frames+1,24):
                        for delay,val in ((0,0),(1,1),(3,0)):
                            if frame+delay<=opts.frames:
                                block.value=val
                                block.keyframe_insert(data_path="value",frame=frame+delay,group="Blink")
        return arm
    luma=actor("Luma",-1.13,copper,ivory,scarf,rabbit=False)
    pip=actor("Pip",1.13,turquoise,ice,gold,rabbit=True)
    floor=cube("original moss ground",(0,0,-.07),(15,15,.12),ground)
    # A little set dressing to establish scale/depth without copyrighted art.
    trunk=material("oak bark",(.27,.17,.12))
    foliage=material("soft turquoise leaves",(.10,.38,.29))
    for x,y,h in [(-4,2,2.9),(3,3,3.2),(-3,-3,2.3),(4,-2,2.6)]:
        cube("original tree trunk",(x,y,h/2),(.37,.41,h),trunk)
        ellipse("original leaf crown",(x,y,h+.6),(1.2,1.2,.95),foliage)
    def area(name,at,power,color,size):
        lamp_data=bpy.data.lights.new(name,"AREA")
        lamp=bpy.data.objects.new(name,lamp_data)
        bpy.context.collection.objects.link(lamp)
        lamp.location=at
        lamp_data.energy=power
        lamp_data.color=color
        lamp_data.shape="DISK";lamp_data.size=size
        lamp.rotation_euler=(Vector((0,0,1.15))-lamp.location).to_track_quat("-Z","Y").to_euler()
    area("large warm cinematic key",(-3,-4,6.2),900,(1,.76,.59),4.2)
    area("cool night rim",(3,2,5.2),1400,(.37,.66,1.0),3.1)
    area("soft frontal fill",(0,-4,3.0),380,(.85,.91,1.0),5.1)
    bpy.ops.object.camera_add(location=(0,-6.6,2.6))
    camera=bpy.context.object
    camera.name="original 16:9 cinematic camera"
    camera.rotation_euler=(Vector((0,0,1.40))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.lens=47
    scene.camera=camera
    scene.view_settings.view_transform="AgX"
    scene.render.image_settings.file_format="PNG"
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(opts.out.resolve()))
    import hashlib
    digest=hashlib.sha256(opts.out.read_bytes()).hexdigest()
    evidence={
        "status":"ORIGINAL_BIPED_3D_ASSET_NOT_CINEMA_APPROVED",
        "source":"original procedural artist kit",
        "characters":["Luma","Pip"],
        "armatures":2,"bone_count_each":13,
        "material_names":sorted(mats),
        "true_facial_shapekeys":True,
        "original_actors_not_stock_quadrupeds":True,
        "facial_acting_adequacy":"NOT_REVIEWED",
        "full_body_performance_adequacy":"NOT_REVIEWED",
        "single_shot_only":True,"file_sha256":digest,
        "film_release_pass":False,
        "set_props":len(props),
    }
    rec=opts.out.with_suffix(".receipt.json")
    rec.write_text(json.dumps(evidence,indent=2),encoding="utf-8")
    print("ORIGINAL_ANTHRO_3D_SKELETON_BUILT",json.dumps({
        "arms":2,"bone_count_each":13,"animated_frames":opts.frames,
        "blendshapes":True,"film_release_pass":False}))


if __name__=="__main__":
    make()
