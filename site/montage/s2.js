const {record}=require('./lib');const {build}=require('./seed');
(async()=>{
 await record('ov_photo',build({photo:'photo_cran.jpg'}),async p=>{
  await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(500);
  const cam=p.locator('.exo-section').first().locator('[data-role="name-thumb"]').first();
  await cam.scrollIntoViewIfNeeded();await p.waitForTimeout(700);await cam.tap();await p.waitForTimeout(2600);
 });
 await record('ov_couleurs',build(),async p=>{
  await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(700);
  const w=p.locator('[data-role="randomize-colors"]');const bb=await w.boundingBox();
  for(let i=0;i<4;i++){await p.touchscreen.tap(bb.x+bb.width/2,bb.y+bb.height/2);await p.waitForTimeout(650);}
  await p.waitForTimeout(500);
 });
})();
