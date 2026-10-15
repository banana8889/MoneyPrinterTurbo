"""Free-first skeletal character motion proof for MoneyPrinterTurbo.

Designed for Blender 3.6+ (bundled Python): no paid AI providers, no voice synthesis.
This is a MOTION TEST with a credited third-party reference rig, NOT the original
cinematic Luma/Pip characters or a production-quality series.

Example:
  blender -b -t 4 --python studio/rigged_pilot.py -- --smoke --out out/rigged_motion.mp4
  blender -b -t 4 --python studio/rigged_pilot.py -- --out out/rigged_motion.mp4

Source model: Khronos Fox (CC BY 4.0 rig / animations; CC0 model).
Credits: PixelMannen; tomkranis; AsoboStudio; scurest.
https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/Fox
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import urllib.request
from pathlib import Path

import bpy
from mathutils import Vector

ASSET_URL = (
    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/"
    "main/Models/Fox/glTF-Binary/Fox.glb"
)
ATTRIBUTION = (
    "Fox model: PixelMannen (CC0); rigging and animations: tomkranis (CC BY 4.0); "
    "glTF conversion: AsoboStudio and scurest (CC BY 4.0). "
    "Source: https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/Fox\n"
)


def arguments():
    p = argparse.ArgumentParser(description="Create a bone-animated 3D motion proof without subscriptions")
    p.add_argument("--out", default="out/rigged_motion.mp4")
    p.add_argument("--asset", help="local verified rigged .glb asset (defaults to the Khronos Fox)")
    p.add_argument("--smoke", action="store_true", help="low resolution, short render; never use as final video")
    p.add_argument("--seconds", type=int, default=10)
    p.add_argument("--fps", type=int, default=24)
    opts = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = p.parse_args(opts)
    if not 2 <= a.seconds <= 30 or not 24 <= a.fps <= 60:
        p.error("--seconds must be 2..30 and fps 24..60")
    return a


def material(name, color, roughness=0.7, emission=None, intensity=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = intensity
    return mat


def add_mesh(name, kind, location, scale, mat):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=location)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=9, location=location)
    else:
        bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def point_camera(camera, at):
    direction = Vector(at) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def key(obj, frame, location=None, rotation=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def light(name, location, color, energy, size):
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy, data.shape, data.size, data.color = energy, "DISK", size, color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    point_camera(obj, (0, 0, 1))
    return obj


def download_asset(cache):
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.is_file() and cache.stat().st_size > 10000:
        return cache
    request = urllib.request.Request(ASSET_URL, headers={"User-Agent": "MPT-Free-First-Rigging/1.0"})
    with urllib.request.urlopen(request, timeout=45) as resp:
        data = resp.read(20_000_001)
    if not 10_000 <= len(data) <= 20_000_000 or data[:4] != b"glTF":
        raise RuntimeError("Unexpected asset payload; refusing to import")
    cache.write_bytes(data)
    return cache


def rigged_fox(asset):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(asset))
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not imported:
        raise RuntimeError("Asset contains no imported objects")
    armatures = [obj for obj in imported if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError("Imported character has no skeletal armature; stop: no fake motion")

    mover = bpy.data.objects.new("FOX_MOTION_ROOT", None)
    bpy.context.collection.objects.link(mover)
    roots = [obj for obj in imported if obj.parent is None]
    for obj in roots:
        matrix = obj.matrix_world.copy()
        obj.parent = mover
        obj.matrix_world = matrix

    # Asset size varies by exporter; set a stable height in Blender meters.
    points = [obj.matrix_world @ Vector(corner)
              for obj in imported if obj.type == "MESH"
              for corner in obj.bound_box]
    if not points:
        raise RuntimeError("Imported asset has no renderable mesh")
    min_z, max_z = min(v.z for v in points), max(v.z for v in points)
    extent = max_z - min_z
    if extent <= 0.001:
        raise RuntimeError("Imported 3D model has invalid height")
    mover.scale = (1.5 / extent,) * 3
    mover.location.z = -min_z * mover.scale.z

    candidates = list(bpy.data.actions)
    actions = {}
    for word in ("survey", "walk", "run"):
        matching = [act for act in candidates if word in act.name.lower()]
        if not matching:
            raise RuntimeError(f"Expected skeletal '{word}' cycle missing: {[x.name for x in candidates]}")
        actions[word] = matching[0]

    skeleton = armatures[0]
    skeleton.animation_data_create()
    if skeleton.animation_data.action is not None:
        skeleton.animation_data.action = None
    # Import-time glTF action tracks may already be present. Remove them so there
    # is exactly one directed clip per scene, not several incompatible blends.
    for track in list(skeleton.animation_data.nla_tracks):
        skeleton.animation_data.nla_tracks.remove(track)
    return mover, skeleton, actions


def timeline(mover, armature, actions, end):
    sections = [
        ("survey", 1, max(2, round(end * 0.27))),
        ("walk", max(2, round(end * 0.27)) + 1, max(4, round(end * 0.69))),
        ("run", max(4, round(end * 0.69)) + 1, end),
    ]
    for name, start, finish in sections:
        action = actions[name]
        track = armature.animation_data.nla_tracks.new()
        track.name = f"PERFORMANCE_{name.upper()}"
        strip = track.strips.new(name=name, start=int(start), action=action)
        length = max(1.0, float(action.frame_range[1] - action.frame_range[0]))
        strip.scale = max(1.0, finish - start + 1) / length
        strip.extrapolation = "NOTHING"
        strip.blend_type = "REPLACE"
        # Clamp the action to the assigned shot interval; don't leave a static
        # character or conflicting clips in another section.
        strip.action_frame_start = action.frame_range[0]
        strip.action_frame_end = action.frame_range[1]
        strip.mute = False
        strip.frame_end = finish + 1

    # Real articulated action above, world path below. Both must exist.
    p1, p2 = sections[0][2], sections[1][2]
    key(mover, 1, (0.0, 0.0, mover.location.z), (0, 0, 0))
    key(mover, p1, (0.0, 0.0, mover.location.z), (0, 0, -0.05))
    key(mover, p2, (0.6, 1.7, mover.location.z), (0, 0, -0.08))
    key(mover, end, (1.4, 4.7, mover.location.z), (0, 0, 0.13))
    for fcurve in (mover.animation_data.action.fcurves
                   if mover.animation_data and mover.animation_data.action else []):
        for pt in fcurve.keyframe_points:
            pt.interpolation = "BEZIER"
    return sections


def build_forest():
    ground = material("Forest ground", (0.07, 0.16, 0.13), roughness=0.9)
    bark = material("Tree bark", (0.13, 0.10, 0.11), roughness=0.93)
    leaves = material("Canopy pine", (0.03, 0.22, 0.19), roughness=0.9)
    moss = material("Moss", (0.16, 0.36, 0.25), roughness=0.85)
    gold = material("Lantern gold", (0.94, 0.69, 0.21), emission=(1.0, 0.7, 0.2), intensity=1.8)
    add_mesh("FOREST_FLOOR", "cube", (0, 2, -0.32), (40, 40, 0.3), ground)
    random.seed(451)
    for n in range(24):
        x = random.choice((-1, 1)) * random.uniform(3.5, 11)
        y = random.uniform(-11, 15)
        trunk = add_mesh(f"TREE_{n}_TRUNK", "cone", (x, y, 2), (0.37, 0.37, 3), bark)
        add_mesh(f"TREE_{n}_CROWN", "sphere", (x, y, 4.7), (1.1, 1.1, 1.7), leaves)
    for n in range(35):
        x, y = random.uniform(-7, 7), random.uniform(-8, 13)
        if abs(x) < 1.8:
            continue
        add_mesh(f"MOSS_{n}", "sphere", (x, y, 0.06), (.15, .15, .07), moss)
    lantern = add_mesh("MYSTERY_LANTERN", "sphere", (-1.7, 2.3, 2.25),
                       (.18, .18, .18), gold)
    lantern.keyframe_insert(data_path="location", frame=1)
    lantern.location.z += .4
    lantern.keyframe_insert(data_path="location", frame=120)
    return lantern


def measure_skeletal_motion(scene, armature, sections):
    """Prove that the pose skeleton articulates, independently of root/camera motion."""
    start, end = int(sections[1][1]), int(sections[1][2])
    if end - start < 3:
        raise RuntimeError("Walk action interval too short to verify skeletal animation")
    scene.frame_set(start + 1)
    first = {bone.name: bone.matrix.copy() for bone in armature.pose.bones}
    scene.frame_set(min(start + 7, end - 1))
    maximum = 0.0
    for bone in armature.pose.bones:
        before = first[bone.name]
        translation = (bone.matrix.translation - before.translation).length
        rotation = before.to_quaternion().rotation_difference(
            bone.matrix.to_quaternion()).angle
        maximum = max(maximum, translation, rotation)
    if maximum < 0.002:
        raise RuntimeError(
            "No measurable skeletal articulation; camera/root movement is not a valid substitute"
        )
    scene.frame_set(1)
    return round(maximum, 5)


def camera_animation(end):
    camera_data = bpy.data.cameras.new("CINEMA_CAMERA")
    camera = bpy.data.objects.new("CINEMA_CAMERA", camera_data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    camera_data.type = "PERSP"
    camera_data.lens = 35
    # Three motivated shots: establish / follow / discover, not random zooms.
    shots = [
        (1, (10, -13, 4.5), (0, 1, 1.2)),
        (round(end * .27), (9, -11, 4.0), (0, 1.1, 1.2)),
        (round(end * .27) + 1, (8, -10, 4.0), (0, 2.1, 1.2)),
        (round(end * .69), (8, -8, 4.0), (.5, 3.2, 1.2)),
        (round(end * .69) + 1, (7, -7, 4.0), (.8, 4, 1.2)),
        (end, (6, -5, 4.0), (1.4, 6, 1.2)),
    ]
    for frame, position, target in shots:
        camera.location = position
        point_camera(camera, target)
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    return camera


def setup_render(scene, args, out):
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 6 if args.smoke else 32
    scene.cycles.use_denoising = not args.smoke  # Ubuntu apt Blender is built without OIDN
    scene.render.resolution_x = 640 if args.smoke else 1920
    scene.render.resolution_y = 360 if args.smoke else 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = args.fps
    scene.frame_start = 1
    scene.frame_end = (2 if args.smoke else args.seconds) * args.fps
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.filepath = str(out)


def main():
    args = arguments()
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = out.parent / "assets" / "Khronos_Fox_CC-BY.glb"
    asset = Path(args.asset).expanduser().resolve() if args.asset else download_asset(cache)
    if not asset.is_file():
        raise FileNotFoundError(f"Asset not found: {asset}")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    world = bpy.data.worlds.new("Starwood twilight")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.025, 0.045, 0.11, 1)
    bg.inputs["Strength"].default_value = .5
    scene = bpy.context.scene
    setup_render(scene, args, out)
    build_forest()
    mover, armature, actions = rigged_fox(asset)
    sections = timeline(mover, armature, actions, scene.frame_end)
    bone_motion_delta = measure_skeletal_motion(scene, armature, sections)
    camera_animation(scene.frame_end)
    light("Moonlight / motivated key", (0, 2, 9), (0.52, 0.75, 1), 1200, 7)
    light("Warm lantern / fill", (-1.8, 2, 3), (1, .64, .34), 550, 4)
    light("Rim light", (4, 6, 8), (.8, .8, 1), 700, 5)
    scene.view_settings.view_transform = "AgX" if "AgX" in [
        x.name for x in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items
    ] else "Standard"
    bpy.ops.wm.save_as_mainfile(filepath=str(out.with_suffix(".blend")))
    bpy.ops.render.render(animation=True)
    if not out.is_file() or out.stat().st_size <= 1000:
        raise RuntimeError("Blender returned without a usable video file")
    report = {
        "status": "motion_proof_only",
        "video": str(out),
        "has_actual_armature": True,
        "measured_skeletal_motion_delta": bone_motion_delta,
        "animation_actions": sorted(actions),
        "timeline_sections": sections,
        "fps": scene.render.fps,
        "frames": scene.frame_end,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "input_model_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
        "human_dialogue": False,
        "original_characters": False,
        "cinematic_release_pass": False,
        "limitations": "Reference model test. No acting/facial rig, real voice, high-end scene art or story continuity.",
    }
    out.with_suffix(".report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    out.with_suffix(".CREDITS.txt").write_text(ATTRIBUTION, encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
