const {chromium}=require('playwright-core');const fs=require('fs');const path=require('path');const {execSync}=require('child_process');
const RIPPLE=`(()=>{const st=document.createElement('style');st.textContent='@keyframes rp{0%{transform:translate(-50%,-50%) scale(.3);opacity:.9}100%{transform:translate(-50%,-50%) scale(1.6);opacity:0}}.rp{position:fixed;width:56px;height:56px;border-radius:50%;background:rgba(255,255,255,.55);border:3px solid rgba(255,255,255,.9);pointer-events:none;z-index:2147483647;animation:rp .55s ease-out forwards}';document.documentElement.appendChild(st);
const mk=(x,y)=>{const d=document.createElement('div');d.className='rp';d.style.left=x+'px';d.style.top=y+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),600)};
addEventListener('touchstart',e=>{const t=e.touches[0];mk(t.clientX,t.clientY)},{capture:true,passive:true});})()`;
async function record(name,state,actions,opts={}){
  const dir=path.resolve('rec_'+name);fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir);
  const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
  const ctx=await br.newContext({viewport:{width:360,height:780},deviceScaleFactor:3,hasTouch:true,isMobile:true});const p=await ctx.newPage();
  await p.addInitScript(([s])=>{localStorage.setItem('OVERBOLT_LICENSE_OK','1');if(s)localStorage.setItem('muscleman_state_v1_6',JSON.stringify(s));},[state]);
  p.on('pageerror',e=>console.log('ERR',e.message));p.on('dialog',d=>d.accept());
  await p.goto('file:///home/user/OVERBOLT/index.html');await p.waitForTimeout(900);
  await p.addStyleTag({content:'#floatTimer .fc-close{display:none!important}.ver{display:none!important}'});
  await p.evaluate(RIPPLE);
  const cdp=await ctx.newCDPSession(p);const frames=[];let n=0;
  cdp.on('Page.screencastFrame',async f=>{const i=n++;fs.writeFileSync(`${dir}/f${String(i).padStart(5,'0')}.jpg`,Buffer.from(f.data,'base64'));frames.push(f.metadata.timestamp);try{await cdp.send('Page.screencastFrameAck',{sessionId:f.sessionId})}catch(e){}});
  await cdp.send('Page.startScreencast',{format:'jpeg',quality:92,maxWidth:1080,maxHeight:2340,everyNthFrame:1});
  await p.waitForTimeout(400);
  await actions(p);
  await cdp.send('Page.stopScreencast');await p.waitForTimeout(200);await br.close();
  // liste ffmpeg à durées variables
  let list='';for(let i=0;i<frames.length;i++){const d=i<frames.length-1?Math.max(0.001,frames[i+1]-frames[i]):0.15;list+=`file 'f${String(i).padStart(5,'0')}.jpg'\nduration ${d.toFixed(4)}\n`}
  list+=`file 'f${String(frames.length-1).padStart(5,'0')}.jpg'\n`;fs.writeFileSync(dir+'/list.txt',list);
  execSync(`ffmpeg -v error -y -f concat -safe 0 -i ${dir}/list.txt -vf "fps=30,scale=1080:-2,format=yuv420p" -c:v libx264 -crf 18 ${name}.mp4`);
  console.log(name,frames.length,'images ->',name+'.mp4');
}
module.exports={record};
