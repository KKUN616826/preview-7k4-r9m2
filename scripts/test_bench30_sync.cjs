const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const {chromium}=require('playwright');
const records=require('../data/benchmark-video-imports.json');
const base=process.env.HERO_PREVIEW_URL||'http://127.0.0.1:8765/';
(async()=>{
 assert.equal(records.length,90);
 for(const r of records)assert.equal(crypto.createHash('sha256').update(fs.readFileSync(r.path)).digest('hex'),r.source_sha256);
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE});
 try{
  const page=await browser.newPage({viewport:{width:1366,height:768}});const errors=[];page.on('pageerror',e=>errors.push(e.message));const overflow=[];
  for(const task of [...new Set(records.map(r=>r.task))]){
   await page.goto(new URL(`tasks/${task}.html`,base).href);
   for(const r of records.filter(r=>r.task===task)){
    await page.locator(`[data-level="${r.level}"]`).click();
    const panel=page.locator(`[data-panel="${r.level}"]`);await panel.waitFor({state:'visible'});
    assert.equal((await panel.locator('.instruction p').textContent()).trim(),r.instruction,`${task}/${r.level} instruction`);
    const video=panel.locator('video');assert.equal(await video.count(),1);
    const actual=await video.evaluate(async v=>{
     v.muted=true;v.load();await new Promise((ok,fail)=>{v.addEventListener('loadedmetadata',ok,{once:true});v.addEventListener('error',()=>fail(Error(v.error?.message)),{once:true});});
     await v.play();v.pause();return{width:v.videoWidth,height:v.videoHeight,duration:v.duration,src:v.currentSrc};
    });
    assert.equal(actual.width,r.width);assert.equal(actual.height,r.height);assert.ok(Math.abs(actual.duration-r.duration)<.1);assert.ok(actual.src.endsWith(r.path));
    const response=await page.request.get(new URL(r.path,base).href,{headers:{Range:'bytes=0-1023'}});assert.equal(response.status(),206);assert.equal((await response.body()).length,1024);
    const footer=await page.locator('.task-footer').boundingBox();if(footer.y+footer.height>768)overflow.push(`${task}/${r.level}`);
   }
   console.log('PASS',task,'all three videos/instructions');
  }
  assert.deepEqual(errors,[]);console.log('First-screen overflow:',JSON.stringify(overflow));console.log('PASS all 90 source hashes, playback, instructions and byte ranges');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
