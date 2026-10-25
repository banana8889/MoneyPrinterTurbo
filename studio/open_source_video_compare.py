"""Offline video QA for Starwood: no paid APIs, model downloads or publishing."""
import argparse,csv,json,shutil,statistics,subprocess
from pathlib import Path
W,H,SR=96,54,4
def run(cmd,timeout=180):
    return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=timeout).stdout
def probe(path):
    data=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]))
    v=next((s for s in data["streams"] if s["codec_type"]=="video"),None)
    a=next((s for s in data["streams"] if s["codec_type"]=="audio"),None)
    if not v: raise ValueError("No video stream")
    n,d=map(int,v.get("avg_frame_rate","0/1").split("/"))
    return {"duration_s":float(v.get("duration") or data["format"].get("duration") or 0),
      "width":int(v["width"]),"height":int(v["height"]),"fps":round(n/d if d else 0,3),
      "codec":v.get("codec_name"),"audio":bool(a),"audio_codec":a.get("codec_name") if a else None,
      "bytes":path.stat().st_size}
def frames(path):
    raw=run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-i",str(path),
      "-vf",f"fps={SR},scale={W}:{H}:flags=area,format=gray","-an","-f","rawvideo","-pix_fmt","gray","pipe:1"])
    size=W*H
    return [raw[i:i+size] for i in range(0,len(raw),size) if len(raw[i:i+size])==size]
def analyze(name,path):
    r=probe(path); fs=frames(path)
    if len(fs)<2: raise ValueError("Cannot decode at least two frames")
    levels=[sum(f)/len(f) for f in fs]
    changes=[sum(abs(a-b) for a,b in zip(fs[i],fs[i-1]))/(W*H) for i in range(1,len(fs))]
    motion=statistics.mean(changes)
    stalled=sum(x<0.6 for x in changes)/len(changes)
    dark=sum(x<12 for x in levels)/len(levels)
    r.update({"model":name,"sampled_frames":len(fs),"frame_delta":round(motion,3),
      "stalled_fraction":round(stalled,3),"dark_fraction":round(dark,3),
      "mean_luma":round(statistics.mean(levels),2),
      "resolution_pass":r["width"]>=1920 and r["height"]>=1080,
      "fps_pass":r["fps"]>=24,"motion_pass":motion>=1.1 and stalled<=0.25,
      "darkness_pass":dark<=0.25,"duration_pass":r["duration_s"]>=4.5,
      "cinematic_quality_verified":False,"identity_consistency_verified":False,
      "dialogue_quality_verified":False})
    r["technical_pass"]=all(r[k] for k in ("fps_pass","motion_pass","darkness_pass","duration_pass"))
    r["release_pass"]=False
    r["quality_note"]="Technical gate only. Human artistic review and identity verification required."
    return r
def main():
    p=argparse.ArgumentParser()
    p.add_argument("clips",nargs="*",help="MODEL=/path/to/clip.mp4")
    p.add_argument("--out",default="starwood_video_report")
    args=p.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"): p.error("FFmpeg required")
    output=Path(args.out);output.mkdir(parents=True,exist_ok=True);results=[]
    for item in args.clips:
        if "=" not in item:p.error("Expected MODEL=/path/to/clip.mp4")
        name,filename=item.split("=",1)
        try:
            r=analyze(name,Path(filename).resolve(strict=True))
            print(f"{name}: sampled={r['sampled_frames']}, technical_pass={r['technical_pass']}")
        except (ValueError,OSError,subprocess.SubprocessError,json.JSONDecodeError) as e:
            r={"model":name,"error":str(e),"technical_pass":False,"release_pass":False}
            print(f"{name}: ERROR {e}")
        results.append(r)
    (output/"results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    fields=("model","duration_s","width","height","fps","audio","frame_delta","stalled_fraction","dark_fraction","technical_pass","error")
    with (output/"results.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(results)
    with (output/"results.md").open("w",encoding="utf-8") as file:
        file.write("# Starwood open-source film comparison\n\nMeasured decoded video only. This cannot certify cinematic quality.\n\n")
        file.write("| Model | Seconds | Pixels | FPS | Audio | Motion Δ | Stalled | Dark | Technical |\n|---|---:|---|---:|---|---:|---:|---:|---|\n")
        for r in results:
            file.write(f"| {r['model']} | {r.get('duration_s','—')} | {r.get('width','—')}x{r.get('height','—')} | {r.get('fps','—')} | {r.get('audio','—')} | {r.get('frame_delta','—')} | {r.get('stalled_fraction','—')} | {r.get('dark_fraction','—')} | {'PASS' if r['technical_pass'] else 'FAIL'} |\n")
        file.write("\nFull episode, actor identity, emotional voices and professional visual quality: NOT VERIFIED.\n")
    return 0 if results and all("error" not in x for x in results) else 1
if __name__=="__main__":raise SystemExit(main())
