const fs=require('fs');
const img=f=>'data:image/jpeg;base64,'+fs.readFileSync(f).toString('base64');
function mkExo(id,name,photo){return {id,name,photo:photo||'',detail1:'',detail2:'',restBetweenExercises:90}}
function mkRow(id,charges,reps,validated){return {exerciseId:id,series:charges.map((c,i)=>({charge:String(c),reps:String(reps),rest:i===3?60:120,validated:!!validated,chargeAuto:true,repsAuto:true,restAuto:true}))}}
function week(n,start,rows,locked,done){return {label:'Semaine '+n,rows,startDate:start,locked:!!locked,session:{startAt:done?start+'T18:00:00.000Z':null,endAt:done?start+'T19:05:00.000Z':null,lastActivityAt:null}}}
function day(exos,weeks){return {subtitle:'',nextExoId:exos.length,exercises:exos,archivedExercises:[],weeks,warmup:{done:false}}}
function build(opts={}){
  const photo=opts.photo?img(opts.photo):'';
  const e1=[mkExo('ex1','Développé incliné machine',photo),mkExo('ex2','Écarté poulie vis-à-vis'),mkExo('ex3','Élévation latérale')];
  const w=(n,start,locked,done,v)=>week(n,start,[mkRow('ex1',[56+n*2,56+n*2,58+n*2,58+n*2],11,v),mkRow('ex2',[36+n,36+n,38+n,38+n],14,v),mkRow('ex3',[10,10,12,12],13,v)],locked,done);
  const d1=day(e1,[w(1,'2026-09-28',true,true,true),w(2,'2026-10-05',true,true,true),w(3,'2026-10-12',true,true,true),w(4,'2026-10-19',false,false,false)]);
  const e2=[mkExo('ex1','Presse à cuisses'),mkExo('ex2','Hack squat')];
  const w2=(n,start,locked,v)=>week(n,start,[mkRow('ex1',[120+n*5,120+n*5,125+n*5,125+n*5],12,v),mkRow('ex2',[40+n*2,40+n*2,44+n*2,44+n*2],10,v)],locked,v);
  const d2=day(e2,[w2(1,'2026-09-29',true,true),w2(2,'2026-10-06',true,true),w2(3,'2026-10-13',true,true),w2(4,'2026-10-20',false,false)]);
  return {currentDay:'Séance 1',dayOrder:['Séance 1','Séance 2','Séance 3','Séance 4'],days:{'Séance 1':d1,'Séance 2':d2,'Séance 3':day([],[week(1,'2026-10-19',[],false)]),'Séance 4':day([],[week(1,'2026-10-19',[],false)])},
   settings:Object.assign({theme:'dark',language:'fr',colorPrincipal:'#2af5e0',colorWarmup:'#ff8a3d',colorSerie:'#2af5e0',colorAddRemove:'#2af5e0',colorValid:'#ff2d95',haloIntensity:3,colorIntensity:3,bgAlpha:3,warmupMinutes:5,autoWeeks:false,alarmVariant:'classique'},opts.settings||{})};
}
module.exports={build};
