// SPDX-License-Identifier: MIT
// STARWOOD Nivi Sprite Actor v0.3 — deterministic independent CPU actor animation.
// Reuses existing cinematographic source; invents Nivi's new flight only.
// Usage: node nivi_engine.mjs <ffmpeg-path> <input-real-shot.mp4> <output.mp4>
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
const [ff, src, out] = process.argv.slice(2);
if (!ff || !src || !out) throw new Error('Usage: node nivi_engine.mjs ffmpeg input.mp4 output.mp4');
const W = 864, H = 480, FPS = 24, FRAMES = 121;
const state = { actor: 'nivi', stage: 'STARWOOD enchanted glade', color: '#8BDDFE', dimensions: 13, q4: [13,4,12,11,8,7,11,6,15,13,9,7,12] };
function pose(t) {
  const e = t*t*(3-2*t);
  return {
    x: 682 - 176*e + 8*Math.sin(t*11),
    y: 262 - 93*Math.sin(Math.PI*t) + 9*Math.sin(t*17),
    scale: 1.50 + .45*Math.sin(Math.PI*t),
    wing: Math.sin(2*Math.PI*t*51),
    glow: .86 + .14*Math.sin(t*37),
    facing: Math.cos(t*8)
  };
}
const args=['-nostdin','-hide_banner','-loglevel','error','-y',
  '-f','rawvideo','-pixel_format','rgba','-video_size',W+'x'+H,'-framerate',String(FPS),'-i','pipe:0',
  '-i',src,'-filter_complex','[1:v]format=yuv420p[bg];[0:v]format=yuva420p[fg];[bg][fg]overlay=shortest=1:format=auto,format=yuv420p[v]',
  '-map','[v]','-map','1:a:0?','-c:v','libx264','-preset','veryfast','-crf','17',
  '-c:a','copy','-movflags','+faststart',out];
const ffproc=spawn(ff,args,{stdio:['pipe','ignore','pipe']});
let stderr='';ffproc.stderr.on('data',c=>{stderr+=(c+'').slice(0,1000)});
const result=once(ffproc,'close');
function frame(i) {
 const img=Buffer.alloc(W*H*4);
 const t=i/(FRAMES-1), P=pose(t);
 function composite(x,y,r,g,b,a) {
   x=Math.round(x); y=Math.round(y);
   if(x<0||x>=W||y<0||y>=H||a<=0) return;
   const k=(y*W+x)*4, old=img[k+3]/255, aa=Math.min(.995,a/255);
   const total=aa + old*(1-aa);
   if (total<=0) return;
   img[k]=Math.round((r*aa+img[k]*old*(1-aa))/total);
   img[k+1]=Math.round((g*aa+img[k+1]*old*(1-aa))/total);
   img[k+2]=Math.round((b*aa+img[k+2]*old*(1-aa))/total);
   img[k+3]=Math.round(total*255);
 }
 function ellipse(cx,cy,rx,ry,ang,c,alpha,edge=0) {
   const cosine=Math.cos(ang),sine=Math.sin(ang),r=Math.ceil(Math.max(rx,ry)*1.6);
   for(let y=Math.max(0,Math.floor(cy-r));y<Math.min(H,Math.ceil(cy+r));y++)
     for(let x=Math.max(0,Math.floor(cx-r));x<Math.min(W,Math.ceil(cx+r));x++){
       const dx=x-cx,dy=y-cy,u=(dx*cosine+dy*sine)/rx,v=(-dx*sine+dy*cosine)/ry,k=u*u+v*v;
       if(k>1)continue;
       const edgeAlpha = edge ? Math.max(0,Math.min(1,(1-k)*10)) : Math.max(0,Math.min(1,(1-k)*12));
       const light=(.68 + .32*Math.max(0,-u-v)/1.5);
       composite(x,y,Math.round(c[0]*light),Math.round(c[1]*light),Math.round(c[2]*light),alpha*edgeAlpha);
     }
 }
 // Soft moving ambient glow and light spill.
 for(let k=6;k>=1;k--){
   const radius=14+k*12;
   const x0=Math.max(0,Math.floor(P.x-radius)),x1=Math.min(W,Math.ceil(P.x+radius));
   const y0=Math.max(0,Math.floor(P.y-radius)),y1=Math.min(H,Math.ceil(P.y+radius));
   const radius2=radius*radius;
   for(let y=y0;y<y1;y+=2)for(let x=x0;x<x1;x+=2){
     const d2=(x-P.x)**2+(y-P.y)**2;
     if(d2>radius2)continue;
     const a=12*P.glow*(1-d2/radius2)*(.45+ .11*k);
     for(let yy=0;yy<2;yy++)for(let xx=0;xx<2;xx++)composite(x+xx,y+yy,69,190,250,a);
   }
 }
 // Sparks are old positions along this genuinely new motion trajectory.
 for(let j=1;j<=13;j++){
    const tt=Math.max(0,t-j/105),old=pose(tt),v=(1-j/14);
    const qx=old.x+Math.sin(i*.31+j*2.6)*j*.55, qy=old.y+Math.cos(i*.23+j*1.7)*j*.46;
    ellipse(qx,qy,1.1+j*.07,1.0+j*.04,0,[154,227,255],120*v*v);
 }
 // Animated, translucent, high-frequency iridescent moth wings (behind torso).
 const flap=Math.sin(t*2*Math.PI*49);
 const wingSize=(14 + 7*Math.abs(flap))*P.scale;
 ellipse(P.x-10*P.scale,P.y-7*P.scale,wingSize,5.7*P.scale,-.50-.34*flap,[170,228,247],100);
 ellipse(P.x+10*P.scale,P.y-7*P.scale,wingSize,5.7*P.scale,.50+.34*flap,[162,205,250],110);
 ellipse(P.x-12*P.scale,P.y-2*P.scale,11*P.scale,3*P.scale,.44,[126,204,244],87);
 ellipse(P.x+12*P.scale,P.y-2*P.scale,11*P.scale,3*P.scale,-.44,[130,215,244],90);
 // Volumetric tiny luminous body, face forward, animated pulse.
 ellipse(P.x,P.y+3*P.scale,7.5*P.scale,11*P.scale,0,[65,112,209],238);
 ellipse(P.x-1.2*P.scale,P.y+0*P.scale,5*P.scale,7.4*P.scale,0,[125,191,249],197);
 ellipse(P.x,P.y+9*P.scale,4*P.scale,5*P.scale,0,[151,252,240],182+45*P.glow);
 // Two small bright eyes, catchlights and antenna tips.
 ellipse(P.x-2.4*P.scale,P.y-2*P.scale,1.6*P.scale,2.0*P.scale,0,[25,44,84],230);
 ellipse(P.x+2.5*P.scale,P.y-2*P.scale,1.6*P.scale,2.0*P.scale,0,[25,44,84],230);
 ellipse(P.x-2.7*P.scale,P.y-2.9*P.scale,.55,.70,0,[255,255,255],230);
 ellipse(P.x+2.2*P.scale,P.y-2.9*P.scale,.55,.70,0,[255,255,255],230);
 ellipse(P.x-5*P.scale,P.y-11*P.scale,1.2,1.7,0,[212,249,255],180);
 ellipse(P.x+5*P.scale,P.y-11*P.scale,1.2,1.7,0,[212,249,255],180);
 return img;
}
for(let i=0;i<FRAMES;i++){
 const fr=frame(i);
 if(!ffproc.stdin.write(fr))await once(ffproc.stdin,'drain');
}
ffproc.stdin.end();
const [code]=await result;
if(code!==0 || !fs.existsSync(out) || fs.statSync(out).size < 50000)
 throw Error('FFmpeg failed '+code+' '+stderr.slice(-1600));
console.log(JSON.stringify({status:'RENDERED_NEW_ACTOR_ON_CPU',name:state.actor,frames:FRAMES,
dimensions:state.dimensions,q4:state.q4,video:out,bytes:fs.statSync(out).size,
sourcePixelsReused:true,novelActorMotion:true,newMainCharacterActing:false,
modelInference:false}));
[exit code 0]