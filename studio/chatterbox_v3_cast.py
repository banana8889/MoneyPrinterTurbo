"""Optional free Chatterbox Multilingual V3 casting for original/authorized voices.

Uses ResembleAI/chatterbox MIT-licensed open weights locally, not an API.
ACTOR-SPECIFIC, CONSENTED voice references are mandatory, with separate WAV
recordings for each of Luma, Pip, Narrator (no celebrity/identifiable cloning).

Install on an adequately powered LOCAL machine:
    pip install chatterbox-tts soundfile numpy
    python studio/chatterbox_v3_cast.py \
        --script studio/season1_episode1_full.json \
        --voice-rights path/to/private_voice_rights.json \
        --out storage/original_cast_episode1 --device cuda

Rights file format:
{
  "version": 1,
  "voices": [
    {"speaker":"luma","wav":"/path/private/luma_authorized.wav",
     "rights":"owned_original_recording","commercial_allowed":true},
    {"speaker":"pip","wav":"/path/private/pip_authorized.wav",
     "rights":"owned_original_recording","commercial_allowed":true},
    {"speaker":"narrator","wav":"/path/private/narrator_authorized.wav",
     "rights":"explicitly_licensed_recording","commercial_allowed":true}
  ]
}
Rights files and reference audio must NEVER be committed to a public repo.
Audio is automatically marked NOT APPROVED pending independent human listening.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

CAST = {"luma", "pip", "narrator"}
RIGHTS = {"owned_original_recording", "explicitly_licensed_recording"}
ENGINE = "chatterbox_multilingual_v3"


def rights_receipts(path: Path) -> dict:
    import soundfile as sf
    import numpy as np

    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("version")!=1 or not isinstance(data.get("voices"),list):
        raise ValueError("Versioned signed-source voice rights records are required")
    result={}
    digests=set()
    for rec in data["voices"]:
        speaker=rec.get("speaker")
        if speaker not in CAST or speaker in result:
            raise ValueError("Invalid or repeated cast voice")
        if rec.get("rights") not in RIGHTS or rec.get("commercial_allowed") is not True:
            raise PermissionError("Reference voice lacks explicit commercial rights clearance")
        name=Path(str(rec.get("wav",""))).expanduser()
        if not name.is_file() or name.suffix.lower()!=".wav":
            raise FileNotFoundError(f"Actor voice recording missing for {speaker}")
        audio,sr=sf.read(name,dtype="float32",always_2d=False)
        if audio.ndim !=1 or sr<16000 or not 3 <= len(audio)/sr <= 45:
            raise ValueError("Reference must be mono, 3-45 seconds at 16kHz+")
        if float(np.sqrt(np.mean(audio.astype("float64")**2)))<0.009:
            raise ValueError("Reference must contain audible human speech")
        h=hashlib.sha256(name.read_bytes()).hexdigest()
        if h in digests:
            raise ValueError("Distinct cast voices must not use one shared reference")
        digests.add(h)
        result[speaker]={"path":name.resolve(),"sha256":h,"rights":rec["rights"]}
    if set(result)!=CAST:
        raise ValueError("Exactly three separately authorized original cast recordings required")
    return result


def model_load(device="cpu"):
    if device not in ("cpu","cuda"):
        raise ValueError("No paid inference endpoint or invalid runtime allowed")
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    return ChatterboxMultilingualTTS.from_pretrained(device=device,t3_model="v3")


def generate(model, text, actor_ref):
    import numpy as np
    # Official V3 API; never send voice references over the network to APIs.
    result=model.generate(text, language_id="en", audio_prompt_path=str(actor_ref))
    audio=np.asarray(result.detach().cpu().numpy(),dtype="float32").reshape(-1)
    rate=int(model.sr)
    if rate<16000 or not np.isfinite(audio).all() or len(audio)<rate//4:
        raise RuntimeError("Chatterbox returned invalid short/nonfinite speech")
    return audio,rate


def render(script_path:Path,voice_rights_path:Path,out:Path,device="cpu",model=None):
    import soundfile as sf
    from studio.cast_audio import read_script, trim_fade, wav_info

    data=read_script(script_path)
    refs=rights_receipts(voice_rights_path)
    out=out.expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)
    m=model_load(device) if model is None else model
    lines=[]
    end=0.
    for i,row in enumerate(data["lines"]):
        actor=row["speaker"]
        ref=refs[actor]
        h=hashlib.sha256(json.dumps(
            [ENGINE,row,ref["sha256"]],sort_keys=True).encode()).hexdigest()[:20]
        name=out/f"line_{i+1:03d}_{h}.wav"
        if not name.exists():
            arr,rate=generate(m,row["text"],ref["path"])
            arr=trim_fade(arr,rate)
            with tempfile.NamedTemporaryFile(prefix="._voice_",suffix=".wav",
                                             dir=out,delete=False) as f:
                temp=Path(f.name)
            try:
                sf.write(temp,arr,rate,subtype="PCM_16")
                wav_info(temp)
                os.replace(temp,name)
            finally:
                temp.unlink(missing_ok=True)
        info=wav_info(name)
        start=end+(.22 if i else 0.0)
        end=start+info["duration_seconds"]
        lines.append({"line":i+1,"speaker":actor,"voice":actor,
                      "text":row["text"],"emotion":row.get("emotion"),
                      "voice_reference_sha256":ref["sha256"],
                      "audio":str(name),"start_seconds":round(start,4),
                      "end_seconds":round(end,4),**info})
    receipt={"version":1,"engine":ENGINE,"provider":"MIT locally executed open weights",
             "rendered":len(lines),"duration_seconds":round(end,4),
             "cast":sorted(refs),"lines":lines,"voice_rights_checked":True,
             "human_voice_naturalness":"NOT_AUDITIONED",
             "subjective_acting_quality":"NOT_REVIEWED",
             "approval":False,"suitable_for_publication":False,
             "notes":"Technical audio only. Voice, accent, dialogue intent, identity and face performance must be reviewed by listening."}
    temp=out/".cast_report_partial"
    temp.write_text(json.dumps(receipt,indent=2,ensure_ascii=False),encoding="utf-8")
    os.replace(temp,out/"cast_report.json")
    return receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--script",required=True,type=Path)
    p.add_argument("--voice-rights",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--device",choices=["cpu","cuda"],default="cpu")
    args=p.parse_args()
    receipt=render(args.script,args.voice_rights,args.out,args.device)
    print(json.dumps({"engine":ENGINE,"lines":receipt["rendered"],
                      "film_ready":False,"approved":False}))


if __name__=="__main__":
    main()
