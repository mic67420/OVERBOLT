const { chromium } = require('../pw/node_modules/playwright-core');const fs=require('fs');const path=require('path');
(async()=>{const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await br.newPage({viewport:{width:720,height:1280}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+path.resolve('intro.html'));await p.waitForTimeout(400);
const FPS=30,TOTAL=4.8,n=Math.round(FPS*TOTAL);const only=process.argv[2]?process.argv[2].split(',').map(Number):null;
for(let i=0;i<n;i++){ if(only&&!only.includes(i))continue; await p.evaluate(t=>window.draw(t),i/FPS);await p.locator('#c').screenshot({path:`frames/f${String(i).padStart(4,'0')}.png`});}
console.log('erreurs',errs.join('|')||'aucune','frames',n);await br.close();})();
