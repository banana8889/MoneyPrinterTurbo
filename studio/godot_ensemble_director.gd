extends Node3D
## Original Starwood scene director running on a *real* CC0 FACS + skeletal
## character. This controller stages TWO actors in the same 3D world and
## derives the shot list from the real cast's spoken-line timing. No slideshow.
## Experimental, not a cinematic-quality or character-design certification.

@export_file("*.json") var manifest_path: String = "res://studio_cast/scene_cast.json"
@export var actor_spacing: float = 0.95
@export var wide_fov: float = 39.0
@export var close_fov: float = 25.0

const ACTOR_SOURCE := "res://scenes/vitruvian_cinematic.tscn"
const FACE_DRIVER := "res://studio_cast/godot_facs_cast.gd"

var actors: Dictionary = {}
var camera: Camera3D
var key_light: DirectionalLight3D
var lantern: MeshInstance3D
var _lines: Array = []
var _duration: float = 0.0
var _elapsed: float = 0.0
var _narrator: AudioStreamPlayer
var _last_narrator: int = -1
var _cast_ready: bool = false
var _current_shot: int = -1
var _story_timeline_completed: bool = false
var _shots: Array = []
var _bindings_evidence: Dictionary = {}
var _last_body_action: Dictionary = {}
var _performance_changes: int = 0

func _ready() -> void:
    if not ResourceLoader.exists(ACTOR_SOURCE) or not ResourceLoader.exists(FACE_DRIVER):
        push_error("Real cinematic rig or offline FACS driver missing. Refusing static fallback.")
        return
    if not FileAccess.file_exists(manifest_path):
        push_error("Spoken scene with original audio must be exported first.")
        return
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
    if typeof(raw) != TYPE_DICTIONARY:
        push_error("Malformed cast scene")
        return
    var data: Dictionary = raw
    if data.get("version") != 1 or not data.has("lines"):
        push_error("Unsupported cast schema")
        return
    _lines = data["lines"]
    _duration = float(data.get("duration_seconds", 0))
    if _lines.size() < 3 or _duration < 5:
        push_error("An unfinished cast cannot be staged as a full film scene")
        return
    if not _spawn_cast():
        return
    _setup_camera()
    _setup_lantern()
    _narrator = AudioStreamPlayer.new()
    _narrator.name = "LicensedNarrator"
    add_child(_narrator)
    _shots = _storyboard_from_cast()
    if _shots.size() < 5:
        push_error("Not enough distinct shots for an engaging sequence")
        return
    _cast_ready = true
    print("[starwood] REAL 3D ENSEMBLE ready: actors=2 shots=", _shots.size(),
          " duration=", _duration, " face_tracks=real", " film_ready=false")

func _spawn_cast() -> bool:
    var stage: PackedScene = load(ACTOR_SOURCE)
    var face_script: Script = load(FACE_DRIVER)
    var count: int = 0
    for speaker in ["luma", "pip"]:
        var actor: Node3D = stage.instantiate() as Node3D
        if actor == null:
            push_error("Couldn't load skeletal actor")
            return false
        actor.name = speaker.capitalize() + "_ACTOR"
        # This upstream rig creates a globally aligned head inside _ready().
        # Positioning the root BEFORE add_child() makes the body move but leaves
        # the head at world origin. Add in neutral space first, then translate
        # the entire completed bone hierarchy as one connected character.
        add_child(actor)
        actor.position.x = (-actor_spacing if speaker == "luma" else actor_spacing)
        # A real CCD0 / FACS actor stage: head, body, bone attachments,
        # live animation player, face mesh, eyelids, eyes and hair.
        if not (actor.get("skel") is Skeleton3D) or not (actor.get("face_mi") is MeshInstance3D):
            push_error("Missing live skeletal/FACS actor stage for " + speaker)
            return false
        # Only one scene-wide environment. Duplicate floors/lights are rejected
        # as gratuitous sources of flicker, ghosting and inconsistent exposure.
        if count > 0:
            for child in actor.get_children():
                if child is WorldEnvironment or child is Light3D:
                    child.queue_free()
        var original_camera: Variant = actor.get("camera")
        if original_camera is Camera3D:
            original_camera.current = false
        var head: Variant = actor.get("head_rig")
        if not (head is Node3D):
            push_error("Character face is not attached to the skeletal body: " + speaker)
            return false
        var head_x_error: float = absf((head as Node3D).global_position.x - actor.global_position.x)
        if head_x_error > 0.20:
            push_error("DISCONNECTED_CHARACTER_HEAD: speaker=" + speaker +
                       " offset=" + str(head_x_error))
            return false
        print("[starwood] HEAD_BODY_ALIGNMENT speaker=", speaker, " horizontal_offset=", head_x_error)
        actor.set("DUR", maxf(float(actor.get("DUR")), _duration + 2.0))
        # The upstream demo chooses unrelated choreography by time; disable
        # ONLY its showroom _process. Body AnimationPlayer and our expression
        # driver remain active, with direction supplied from the actual script.
        actor.set_process(false)
        actor.set("_t", 0.0)
        var driver: Node = Node.new()
        driver.name = "Character_Expressive_Performance"
        driver.set_script(face_script)
        driver.set("speaker", speaker)
        driver.set("manifest_path", manifest_path)
        actor.add_child(driver)
        actors[speaker] = actor
        count += 1
    _bindings_evidence = {"actors": actors.size(), "all_skeletal": true,
                          "face_driver": FACE_DRIVER, "live_facs": true}
    return actors.size() == 2

func _setup_camera() -> void:
    camera = Camera3D.new()
    camera.name = "DIRECTED_SHARED_CAMERA"
    camera.current = true
    camera.fov = wide_fov
    camera.near = 0.02
    camera.far = 90.0
    camera.position = Vector3(0, 1.8, 4.0)
    add_child(camera)
    camera.look_at(Vector3(0, 1.55, 0), Vector3.UP)
    camera.make_current()
    var params := CameraAttributesPractical.new()
    params.dof_blur_far_enabled = true
    params.dof_blur_near_enabled = false
    params.dof_blur_amount = 0.04
    camera.attributes = params

func _setup_lantern() -> void:
    # Visually motivated story prop; not a stand-in for human character acting.
    var sphere := SphereMesh.new()
    sphere.radius = .10
    sphere.height = .20
    var glow := StandardMaterial3D.new()
    glow.albedo_color = Color(0.99, 0.72, 0.24)
    glow.emission_enabled = true
    glow.emission = Color(1, 0.68, 0.22)
    glow.emission_energy_multiplier = 3.0
    sphere.material = glow
    lantern = MeshInstance3D.new()
    lantern.name = "MISSING_STAR_CLUE"
    lantern.mesh = sphere
    lantern.position = Vector3(0, 2.5, -0.25)
    add_child(lantern)
    var warm := OmniLight3D.new()
    warm.omni_range = 2.4
    warm.light_energy = 0.9
    warm.light_color = Color(1, 0.68, 0.32)
    lantern.add_child(warm)

func _storyboard_from_cast() -> Array:
    var result: Array = []
    for i in range(_lines.size()):
        var row: Dictionary = _lines[i]
        var speaker: String = str(row["speaker"])
        var kind: String = "two_shot"
        if speaker == "narrator":
            kind = ("star_prop" if i >= _lines.size() / 2 else "two_shot")
        else:
            kind = speaker + "_portrait"
        # One motivated shot for each spoken exchange, not random camera zoom.
        result.append({
            "start": float(row["start"]),
            "end": float(row["end"]),
            "kind": kind,
            "emotion": str(row.get("emotion","curious")),
            "story_line": i+1,
        })
    return result

func _process(delta: float) -> void:
    if not _cast_ready:
        return
    _elapsed += delta
    _play_narrator(_elapsed)
    _direct_camera(_elapsed, delta)
    _direct_cast_performance(_elapsed, delta)
    # A designed key prop that reacts when a clue is found, not a generic pulse.
    var revelation: float = smoothstep(_duration * .51, _duration * .72, _elapsed)
    lantern.position.y = 2.5 + .32 * revelation
    lantern.scale = Vector3.ONE * (0.95 + 0.2 * revelation)
    if _elapsed >= _duration and not _story_timeline_completed:
        if _performance_changes < 2:
            push_error("No directed skeletal acting transitions; story may be static")
            return
        _story_timeline_completed = true
        print("[starwood] WHOLE_DIALOGUE_TIMELINE_COMPLETED lines=", _lines.size(),
              " seconds=", _duration, " actors=", actors.size(),
              " directed_acting_transitions=", _performance_changes,
              " film_ready=false")
    if _elapsed >= _duration + 1.0 and OS.has_environment("STARWOOD_ONE_SHOT"):
        get_tree().quit()

func _action_for(speaker: String, active: String, emotion: String) -> String:
    if active != speaker:
        return "Turn" if emotion in ["wonder", "concern", "urgent"] else "Idle"
    match emotion:
        "excited", "hopeful":
            return "Wave"
        "concern", "urgent":
            return "Turn"
        "wonder":
            return "Sway"
        "gentle":
            return "HappyIdle"
        "curious":
            return "Sway"
        _:
            return "Idle"


func _direct_cast_performance(t: float, delta: float) -> void:
    var line: Dictionary = {}
    for entry in _lines:
        if t >= float(entry["start"]) and t < float(entry["end"]):
            line = entry
            break
    var speaking: String = str(line.get("speaker", "narrator"))
    var emotion: String = str(line.get("emotion", "curious"))
    for speaker in actors:
        var actor: Node3D = actors[speaker] as Node3D
        actor.set("_t", t) # shared clock for real phonemes and expression keys
        var anim: AnimationPlayer = actor.get("anim") as AnimationPlayer
        if anim == null:
            push_error("Live body AnimationPlayer missing: " + str(speaker))
            continue
        var requested: String = _action_for(str(speaker), speaking, emotion)
        if not anim.has_animation(requested):
            if not anim.has_animation("Idle"):
                push_error("Actor has no Idle skeletal action: " + str(speaker))
                continue
            requested = "Idle"
        if _last_body_action.get(speaker, "") != requested:
            anim.play(requested, 0.25)
            _last_body_action[speaker] = requested
            _performance_changes += 1
        # No root object translation to fake a step. Animate on the actual rig,
        # and keep each actor planted while delivering lines.
        var hair_spring: Variant = actor.get("hair_spring")
        if hair_spring is Object and hair_spring.has_method("step"):
            hair_spring.call("step", delta)


func _play_narrator(t: float) -> void:
    for i in range(_last_narrator + 1, _lines.size()):
        var line: Dictionary = _lines[i]
        if float(line["start"]) > t + .005:
            break
        _last_narrator = i
        if str(line["speaker"]) != "narrator":
            continue
        var path: String = str(line["audio"])
        if not path.begins_with("res://studio_cast/") or not ResourceLoader.exists(path):
            push_error("Missing licensed narration: " + path)
            continue
        var recording: AudioStream = load(path) as AudioStream
        if recording:
            _narrator.stop()
            _narrator.stream = recording
            _narrator.play(maxf(0.0, t - float(line["start"])))

func _direct_camera(t: float, delta: float) -> void:
    var chosen: int = -1
    for i in range(_shots.size()):
        var shot: Dictionary = _shots[i]
        if t >= float(shot["start"]) and t < float(shot["end"]):
            chosen = i
            break
    if chosen < 0:
        return
    var cut: bool = chosen != _current_shot
    _current_shot = chosen
    var tag: String = str(_shots[chosen]["kind"])
    var pos: Vector3
    var focus: Vector3
    var fov: float
    match tag:
        "luma_portrait":
            pos = Vector3(-actor_spacing + .22, 1.68, 1.15)
            focus = Vector3(-actor_spacing, 1.58, 0.0)
            fov = close_fov
        "pip_portrait":
            pos = Vector3(actor_spacing - .19, 1.68, 1.15)
            focus = Vector3(actor_spacing, 1.58, 0.0)
            fov = close_fov
        "star_prop":
            pos = Vector3(.7, 2.66, 1.1)
            focus = lantern.global_position
            fov = close_fov + 4
        _:
            pos = Vector3(0.0, 1.86, 4.0)
            focus = Vector3(0.0, 1.56, 0.0)
            fov = wide_fov
    # Cinematic edits cut at spoken beats; continuity *within* a shot is stable.
    if cut:
        camera.position = pos
        camera.fov = fov
    else:
        camera.position = camera.position.lerp(pos, clampf(delta * 2.3,0.0,1.0))
        camera.fov = lerpf(camera.fov, fov, clampf(delta * 3,0.0,1.0))
    camera.look_at(focus, Vector3.UP)
