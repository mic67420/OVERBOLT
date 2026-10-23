const {record}=require('./lib');const {build}=require('./seed');
(async()=>{
 await record('ov_valider',build({photo:'photo_cran.jpg'}),async p=>{
  await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(500);
  const vb=p.locator('.exo-section').first().locator('.validate-btn:not(.done)');
  const n=await vb.count();console.log('boutons non validés',n);
  // dernière semaine = colonne la plus à droite : on prend le dernier groupe
  const last=p.locator('.exo-section').first().locator('.week-group').last().locator('.validate-btn').first();
  await last.scrollIntoViewIfNeeded();await p.waitForTimeout(500);
  await last.tap();await p.waitForTimeout(2200);
 });
})();
