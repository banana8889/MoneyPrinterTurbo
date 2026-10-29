# Starwood temporal restoration experiment, MIT, original CPU algorithm.
import cv2,numpy as np,sys,json
from pathlib import Path
src,dst=sys.argv[1:3]
cap=cv2.VideoCapture(src)
if not cap.isOpened(): raise RuntimeError("cannot decode real Wan MP4")
fps=cap.get(cv2.CAP_PROP_FPS) or 12
frames=[]
while True:
 ok,f=cap.read()
 if not ok:break
 frames.append(f)
cap.release()
assert len(frames)==9,len(frames)
def gray(x): return cv2.cvtColor(x,cv2.COLOR_BGR2GRAY)
def metrics(x):
 y=gray(x).astype(np.float32)
 grad=np.abs(y[:,1:]-y[:,:-1]).mean()+np.abs(y[1:]-y[:-1]).mean()
 edge=((np.abs(y[1:]-y[:-1,:])[:,:-1]+np.abs(y[:,1:]-y[:,:-1])[1:])>25).mean()
 return [float(grad),float(edge)]
ref=metrics(frames[0])[0]
output=[frames[0].copy()]; diag=[]
for i in range(1,len(frames)):
 current=frames[i].astype(np.float32);prev=frames[i-1];restored=output[-1]
 g0=gray(prev);g1=gray(frames[i])
 flow=cv2.calcOpticalFlowFarneback(g1,g0,None,.5,3,21,4,5,1.2,0)
 flowback=cv2.calcOpticalFlowFarneback(g0,g1,None,.5,3,21,4,5,1.2,0)
 h,w=g0.shape
 xy=np.stack(np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32)),axis=-1)
 xy+=flow
 back=cv2.remap(flowback,xy[...,0],xy[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
 warp=cv2.remap(restored,xy[...,0],xy[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
 warpedprev=cv2.remap(prev,xy[...,0],xy[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
 fb=np.linalg.norm(flow+back,axis=2)
 difference=np.mean(np.abs(warpedprev-current),axis=2)
 conf=np.exp(-.65*fb)*np.maximum(0,1.-difference/34.)
 conf*=((xy[...,0]>3)&(xy[...,0]<w-4)&(xy[...,1]>3)&(xy[...,1]<h-4)).astype(np.float32)
 detail=np.clip(warp-cv2.GaussianBlur(warp,(0,0),1.0),-28.,28.)
 localdetail=np.clip(current-cv2.GaussianBlur(current,(0,0),1.0),-28.,28.)
 ratio=float(np.clip(ref/max(metrics(frames[i])[0],1),1,2.7))
 # Two sources of detail: tracked earlier fine texture and currently observed edges.
 result=current+detail*(conf[...,None]*.55)+localdetail*(ratio-1)*.92
 result=np.clip(result,0,255).astype(np.uint8)
 output.append(result)
 diag.append(dict(frame=i,ratio=ratio,confidence=float(conf.mean()),original=metrics(frames[i]),restored=metrics(result)))
h,w=frames[0].shape[:2]
proc=cv2.VideoWriter(dst,cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h))
if not proc.isOpened():raise RuntimeError("opencv encoder unavailable")
for f in output:proc.write(f)
proc.release()
assert Path(dst).stat().st_size>20000
lowfreq=float(np.mean([np.mean(np.abs(cv2.GaussianBlur(a.astype(np.float32),(0,0),3)-cv2.GaussianBlur(b.astype(np.float32),(0,0),3))) for a,b in zip(frames,output)]))
print(json.dumps({'original':list(map(metrics,frames)),'repaired':list(map(metrics,output)),'lowfreqMAE':lowfreq,'diagnostics':diag,'source':src,'output':dst}))
[exit code 0]