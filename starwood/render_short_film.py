#!/usr/bin/env python3
import math,struct,subprocess,urllib.request,wave
from pathlib import Path

ROOT=Path("starwood_output")
ROOT.mkdir(exist_ok=True)
BASE="https://4ba96fba-a38a-45c1-8374-7d1c4ff561f9.sandbox.floot.app/_cdn/static/"
CLIPS=[
("STARWOOD_Kandinsky6_Lite_2026-10-26.mp4","לומה גילתה ביער שביל שאיש לא הכיר."),
("STARWOOD_Kandinsky6_Shot02_2026-10-26.mp4","בקצה השביל חיכה פיפ, חבר שלא ראתה זמן רב."),
("STARWOOD_EP01_SHOT_005_REAL_KANDINSKY_2026-10-29.mp4","פתאום נצנץ אור מוזר בין העצים."),
("STARWOOD_EP01_SHOT005_KANDINSKY_2026-11-04.mp4","העששית ריחפה, כאילו ניסתה לומר להם משהו."),
("STARWOOD_EP1_Scene03_2026-10-27.mp4","הם הקשיבו. האור הבהב שלוש פעמים."),
("STARWOOD_CPU_FILMGRAMMAR_REAL_SOURCE_REEDIT_11s_2026-10-28.mp4","צעד אחר צעד, שני החברים התקדמו בעקבות הסימן."),
("STARWOOD_NIVI_NEW_CHARACTER_CPU_v03_2026-10-28.mp4","בין הפרחים הופיעה שומרת אור קטנה."),
("STARWOOD_HEBREW_PROMPT_TO_VIDEO_DEMO_2026-11-03.mp4","היא הצביעה אל היער העתיק, כאילו זכרה סוד."),
("STARWOOD_KKRIEGER_CPU_MOTION_STUDY_2026-11-02.mp4","הרוח התעוררה, והשביל השתנה לנגד עיניהם."),
("STARWOOD_PRO_RIG_FOREST_CPU_2026-11-01.mp4","לומה עצרה. הפעם הם כבר לא פחדו."),
("STARWOOD_Kandinsky6_TwoShots_10s_2026-10-26.mp4","פיפ חייך: את התשובה מוצאים כשצועדים יחד."),
("STARWOOD_EP1_ThreeScenes_15s_2026-10-27.mp4","והעששית? היא האירה להם את הדרך הביתה.")
]

def cmd(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL)

def ass(text,title=False):
    kind="Title" if title else "Caption"
    return "\n".join([
        "[Script Info]","ScriptType: v4.00+","PlayResX: 960","PlayResY: 540",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Caption,Noto Sans Hebrew,38,&H00FFF9ED,&H00FFFFFF,&H00201911,&H93000000,-1,0,0,0,100,100,0,0,1,3,1,2,45,45,33,1",
        "Style: Title,Noto Sans Hebrew,70,&H00FFF4D4,&H00FFFFFF,&H00241713,&H98000000,-1,0,0,0,100,100,0,0,1,3,2,5,40,40,50,1",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        "Dialogue: 0,0:00:00.25,0:00:20.00,"+kind+",,0,0,0,,"+text
    ])+"\n"

def prepare(filename,i):
    path=ROOT/("source_%02d.mp4"%i)
    if not path.exists():
        req=urllib.request.Request(BASE+filename,headers={"User-Agent":"STARWOOD-Film-Builder/1.0"})
        with urllib.request.urlopen(req,timeout=60) as response:
            data=response.read(40_000_000)
        if len(data)<40000 or data[4:8]!=b"ftyp":
            raise ValueError("Source is missing or protected: "+filename)
        path.write_bytes(data)
    return path

def make_title(text,name,length):
    captions=ROOT/(name+".ass");captions.write_text(ass(text,True),encoding="utf-8")
    out=ROOT/(name+".mp4")
    cmd(["ffmpeg","-nostdin","-y","-loglevel","error","-f","lavfi","-i",
         "color=c=0x0a1c2b:s=960x540:r=24:d="+str(length),"-vf",
         "noise=alls=5:allf=t+u,subtitles="+str(captions),
         "-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(out)])
    return out

def soundtrack(duration):
    path=ROOT/"starwood_original_score.wav"
    rate=32000
    notes=[220.0,261.63,329.63,392.0,293.66,349.23,440.0,392.0]
    n=math.ceil(duration*rate)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        values=bytearray(n*2)
        seed=123456;wind=0.0
        for i in range(n):
            t=i/rate
            k=int(t//5)%len(notes)
            root=notes[k]/2
            v=.05*math.sin(2*math.pi*root*t)+.035*math.sin(2*math.pi*root*1.5*t)+.024*math.sin(2*math.pi*root*2*t)
            beat=t%5
            v+=.08*math.exp(-beat*2)*(math.sin(2*math.pi*notes[k]*t)+.3*math.sin(2*math.pi*notes[k]*2.006*t))
            bell=t%7
            v+=.035*math.exp(-bell*3.0)*math.sin(2*math.pi*(660+110*(k%4))*t)
            seed=(1664525*seed+1013904223)&0xffffffff
            wind=wind*.9994+(seed/4294967295-.5)*.0007
            v+=wind*.4
            fade=max(0.0,min(1.0,t/3,(duration-t)/4))
            struct.pack_into("<h",values,i*2,round(max(-1,min(1,v*fade))*27000))
        w.writeframes(values)
    return path

def main():
    parts=[make_title("סטארווד\\Nסוד העששית","opening",5)]
    for i,(filename,caption) in enumerate(CLIPS):
        src=prepare(filename,i)
        sub=ROOT/("shot_%02d.ass"%i);sub.write_text(ass(caption),encoding="utf-8")
        out=ROOT/("shot_%02d.mp4"%i)
        cmd(["ffmpeg","-nostdin","-y","-loglevel","error","-i",str(src),
             "-vf","scale=960:540:force_original_aspect_ratio=increase,crop=960:540,setsar=1,setpts=(PTS-STARTPTS)/0.88,fps=24,subtitles="+str(sub),
             "-an","-c:v","libx264","-threads","2","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(out)])
        parts.append(out)
    parts.append(make_title("הסוף\\Nהסוד הבא מחכה ביער","ending",7))
    manifest=ROOT/"parts.txt"
    manifest.write_text("".join("file '"+str(p.resolve())+"'\n" for p in parts),encoding="utf-8")
    visual=ROOT/"visuals.mp4"
    cmd(["ffmpeg","-nostdin","-y","-loglevel","error","-f","concat","-safe","0","-i",str(manifest),
         "-an","-c:v","copy",str(visual)])
    sec=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(visual)]).decode().strip())
    if not 75<=sec<=130:raise RuntimeError("Unexpected duration "+str(sec))
    sound=soundtrack(sec+.1)
    out=ROOT/"STARWOOD_THE_LANTERN_SIGNAL_COMPLETE_SHORT.mp4"
    cmd(["ffmpeg","-nostdin","-y","-loglevel","error","-i",str(visual),"-i",str(sound),
         "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-ac","2","-shortest",
         "-movflags","+faststart",str(out)])
    cmd(["ffmpeg","-nostdin","-v","error","-i",str(out),"-f","null","-"])
    print("FILM_COMPLETE",out,round(sec,2),out.stat().st_size)

if __name__=="__main__":main()
