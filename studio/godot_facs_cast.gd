extends Node
## Reusable Godot 4.6 actor driver for *real* FACS facial blendshapes.
## Attach as child of the VitruvianGodot cinematic actor root (CC0 model).
## Works with any properly rigged actor exposing face_mi and bshapes.
## Input from studio/export_facs_cast.py. No random mouth flapping.
## This is an acting pipeline component, NOT a certification of film quality.

@export_enum("luma", "pip") var speaker: String = "luma"
@export_file("*.json") var manifest_path: String = "res://studio_cast/scene_cast.json"
@export var max_viseme_weight: float = 0.84
@export var enable_audio: bool = true

var _actor: Node = null
var _face: MeshInstance3D = null
var _shape_index: Dictionary = {}
var _cues: Array = []
var _lines: Array = []
var _cursor: int = 0
var _last_played: int = -1
var _elapsed: float = 0.0
var _ready_to_act: bool = false
var _audio: AudioStreamPlayer
var _validated_shapes: Dictionary = {}

const VISEMES := {
    "A": "",    # lips closed
    "B": "p_b_m", # bilabial closure
    "C": "ey_eh_uh_04",
    "D": "aa_02",
    "E": "ow_08",
    "F": "f_v_18",
    "G": "f_v_18",
    "H": "aa_02",
    "X": "",   # relaxed silence
}
const VARIANTS := {
    "p_b_m": ["p_b_m_19", "p_b_m_20", "p_b_m", "Lips_Together"],
    "ey_eh_uh_04": ["ey_eh_uh_04", "ey_eh_uh", "Eh"],
    "aa_02": ["aa_02", "aa", "Mouth_Large_Opened"],
    "ow_08": ["ow_08", "ow", "O"],
    "f_v_18": ["f_v_18", "f_v", "Lips_Bite"],
}
const EXPRESSION := {
    "wonder": {"Eyebrows_Raised_Left": 0.38, "Eyebrows_Raised_Right": 0.38},
    "concern": {"Thinking": 0.26, "Eyebrows_Raised_Left": 0.20},
    "curious": {"Eyebrows_Raised_Left": 0.24, "Eyebrows_Raised_Right": 0.18},
    "gentle": {"Happy": 0.24},
    "excited": {"Happy": 0.55, "Eyebrows_Raised_Left": 0.24, "Eyebrows_Raised_Right": 0.24},
    "urgent": {"Scared": 0.24, "Eyebrows_Raised_Left": 0.35},
    "hopeful": {"Happy": 0.37},
}

func _ready() -> void:
    # Child _ready runs before parent _ready; defer discovery until actor is built.
    call_deferred("_bind_actor")

func _bind_actor() -> void:
    _actor = get_parent()
    if _actor == null or not (_actor.get("face_mi") is MeshInstance3D):
        push_error("Actor has no rigged facial MeshInstance3D (face_mi); no fake motion")
        return
    # Disable the upstream reel's independent placeholder speech player: one
    # actor must never speak both its stock demo WAV and the new dialogue.
    var demo_voice: Variant = _actor.get("_speech_player")
    if demo_voice is AudioStreamPlayer:
        demo_voice.stop()
        demo_voice.queue_free()
        _actor.set("_speech_player", null)
    _face = _actor.get("face_mi") as MeshInstance3D
    if _face.mesh == null or _face.get_blend_shape_count() < 8:
        push_error("Professional actor facial blend shapes are missing")
        return
    for i in range(_face.get_blend_shape_count()):
        _shape_index[String(_face.mesh.get_blend_shape_name(i))] = i
    var resolved: int = 0
    for source_name in VARIANTS:
        for alternate in VARIANTS[source_name]:
            if _shape_index.has(alternate):
                _validated_shapes[source_name] = alternate
                resolved += 1
                break
    if resolved < 4:
        push_error("Actor requires at least 4 real mouth shapes; only found: " + str(_validated_shapes))
        return
    if not FileAccess.file_exists(manifest_path):
        push_error("Missing licensed offline cast manifest: " + manifest_path)
        return
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
    if typeof(parsed) != TYPE_DICTIONARY:
        push_error("Invalid cast manifest")
        return
    var cast_data: Dictionary = parsed
    if int(cast_data.get("version", 0)) != 1 or not cast_data.has("cues") or not cast_data.has("lines"):
        push_error("Unsupported cast manifest")
        return
    var cue_map: Dictionary = cast_data["cues"]
    if not cue_map.has(speaker) or not cue_map[speaker] is Array:
        push_error("No phonemes recorded for actor " + speaker)
        return
    _cues = cue_map[speaker]
    if _cues.size() < 4:
        push_error("Not enough speech phonemes")
        return
    var prev_end: float = 0.0
    for cue in _cues:
        if not cue is Dictionary or not VISEMES.has(str(cue.get("value", ""))):
            push_error("Unexpected face phoneme")
            return
        var begin: float = float(cue.get("start", -1))
        var finish: float = float(cue.get("end", -1))
        if begin < prev_end - 0.006 or begin < 0 or finish <= begin:
            push_error("Facial cue timeline is invalid")
            return
        prev_end = finish
    for record in cast_data["lines"]:
        if str(record.get("speaker", "")) == speaker:
            _lines.append(record)
    if _lines.is_empty():
        push_error("No spoken lines for actor " + speaker)
        return
    _audio = AudioStreamPlayer.new()
    _audio.name = "LicensedOfflineDialogue"
    add_child(_audio)
    if _actor.get("DUR") != null:
        _actor.set("DUR", maxf(float(_actor.get("DUR")), float(cast_data.get("duration_seconds", 0.0)) + 1.0))
    _ready_to_act = true
    print("[starwood] FACS bound: ", speaker, " shapes=", resolved, " cues=", _cues.size(), " lines=", _lines.size())

func _process(delta: float) -> void:
    if not _ready_to_act:
        return
    _elapsed += delta
    var t: float = _elapsed
    if _actor != null and _actor.get("_t") != null:
        t = float(_actor.get("_t"))
    if _cursor >= _cues.size() and _last_played >= _lines.size() - 1:
        return
    _drive_voice(t)
    _drive_visemes(t)

func _drive_voice(t: float) -> void:
    if not enable_audio:
        return
    for i in range(_last_played + 1, _lines.size()):
        var line: Dictionary = _lines[i]
        if t + 0.005 < float(line["start"]):
            break
        var path: String = str(line["audio"])
        if not path.begins_with("res://studio_cast/") or not path.ends_with(".wav"):
            push_error("Unlicensed or unexpected audio path rejected: " + path)
            _last_played = i
            continue
        if not ResourceLoader.exists(path):
            push_error("Missing local imported WAV: " + path)
            _last_played = i
            continue
        _audio.stop()
        _audio.stream = load(path) as AudioStream
        if _audio.stream == null:
            push_error("WAV import returned no audio stream: " + path)
        else:
            # If frame playback skipped exact cue start, seek into audio. This
            # retains audio/performance sync when captures lag or resume.
            var seek: float = maxf(0.0, t - float(line["start"]))
            _audio.play(seek)
        _last_played = i

func _active_line(t: float) -> Dictionary:
    for line in _lines:
        if t >= float(line["start"]) and t < float(line["end"]):
            return line
    return {}

func _shape(name: String, value: float) -> void:
    if _shape_index.has(name):
        _face.set_blend_shape_value(int(_shape_index[name]), clampf(value, 0.0, 1.0))

func _drive_visemes(t: float) -> void:
    # Parent can animate idle eyes/brows; reset only phoneme/jaw shapes here.
    while _cursor < _cues.size() and float(_cues[_cursor]["end"]) <= t:
        _cursor += 1
    var mouth: String = "X"
    var strength: float = 0.0
    if _cursor < _cues.size():
        var cue: Dictionary = _cues[_cursor]
        var begin: float = float(cue["start"])
        var finish: float = float(cue["end"])
        if t >= begin and t < finish:
            mouth = str(cue["value"])
            var ramp: float = 0.055
            strength = clampf(minf((t-begin)/ramp, (finish-t)/ramp), 0.0, 1.0)
    for name in _validated_shapes.values():
        _shape(str(name), 0.0)
    if mouth != "X" and mouth != "A":
        var mapped: String = str(VISEMES[mouth])
        if _validated_shapes.has(mapped):
            _shape(str(_validated_shapes[mapped]), max_viseme_weight * strength)
    _shape("Mouth_Large_Opened", (0.12 if mouth in ["C","E","F"] else 0.30) * strength)
    var line: Dictionary = _active_line(t)
    if not line.is_empty():
        var e: String = str(line.get("emotion","curious"))
        if EXPRESSION.has(e):
            for name in EXPRESSION[e]:
                _shape(name, float(EXPRESSION[e][name]))
    # Normal eye movement and head/body acting remain delegated to the
    # professional character stage. Phonemes alone do NOT pass the film gate.
