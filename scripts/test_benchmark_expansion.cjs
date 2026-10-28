const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {cases}=require('../data/benchmark-expansion.json');
const imports=require('../data/benchmark-video-imports.json');
const base=process.env.HERO_PREVIEW_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1000}});let played=0,missing=0;const errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  for(const c of cases){
   await p.goto(new URL(`tasks/${c.id}.html`,base).href);
   assert.equal(await p.locator('.workspace-sidebar .workspace-case-list a').count(),30);
   const initial=['easy','medium','hard'].find(l=>c.media[l]);
   assert.equal(await p.locator(`[data-panel="${initial}"]`).isVisible(),true,`${c.id} initial`);
   for(const level of ['easy','medium','hard']){
    await p.locator(`[data-level="${level}"]`).click();
    const panel=p.locator(`[data-panel="${level}"]`);await panel.waitFor({state:"visible"});assert.equal(await panel.isVisible(),true);
    if(!c.media[level]){
     missing++;assert.equal(await panel.locator('video').count(),0);assert.equal(await panel.locator('.demo-pending').isVisible(),true);continue;
    }
    const record=imports.find(i=>i.task===c.id&&i.level===level);
    const result=await panel.locator('video').evaluate(async v=>{
     v.muted=true;v.load();
     await new Promise((ok,fail)=>{if(v.readyState>=1)return ok();v.addEventListener('loadedmetadata',ok,{once:true});v.addEventListener('error',()=>fail(Error(v.error?.message)),{once:true});});
     await v.play();
     await new Promise((ok,fail)=>{if(v.readyState>=2)return ok();v.addEventListener('loadeddata',ok,{once:true});v.addEventListener('error',()=>fail(Error(v.error?.message)),{once:true});});
     v.pause();return {duration:v.duration,w:v.videoWidth,h:v.videoHeight,src:v.currentSrc};
    });
    assert.ok(Math.abs(result.duration-record.duration)<.1);assert.equal(result.w,record.width);assert.equal(result.h,record.height);assert.ok(result.src.endsWith(`/${c.id}/${level}.mp4`));played++;
    const range=await p.request.get(new URL(record.path,base).href,{headers:{Range:'bytes=0-1023'}});assert.equal(range.status(),206);assert.equal((await range.body()).length,1024);
   }
   const visibleVideo=await p.locator('[data-panel]:visible video').count();
   if(visibleVideo){await p.locator('[data-level="easy"]').click();await p.locator('[data-level="medium"]').click();assert.ok(await p.locator('[data-panel="easy"] video').evaluateAll(vs=>vs.every(v=>v.paused)));}
  }
  assert.equal(played,imports.length);assert.equal(missing,cases.length*3-imports.length);
  for(const width of [390,820,1440]){
   await p.setViewportSize({width,height:900});
   for(const id of ['CP08','CP09','E2']){
    await p.goto(new URL(`tasks/${id}.html`,base).href);assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${id} overflow ${width}`);
   }
  }
  await p.goto(new URL('tasks/E2.html#hard',base).href);await p.reload();assert.equal(await p.locator('[data-panel="hard"] .demo-pending').isVisible(),true);
  assert.deepEqual(errors,[]);console.log(`PASS: ${cases.length} new task pages; ${played} videos played at native dimensions; ${missing} honest pending panels; byte-range playback; difficulty/history and responsive layout`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
