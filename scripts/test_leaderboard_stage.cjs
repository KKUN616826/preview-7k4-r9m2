const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const data=require('../data/leaderboard-results.json');
const base=process.env.HERO_PREVIEW_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});const errors=[],bad=[],requests=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)bad.push(r.url());});p.on('request',r=>requests.push(r.url()));
  await p.goto(new URL('leaderboard.html',base).href);await p.evaluate(()=>document.fonts.ready);
  assert.ok(!requests.some(url=>/three|stage-scene/.test(url)),'no WebGL dependency');
  assert.equal(await p.locator('.lb-stage canvas').count(),0);
  const stage=await p.locator('.lb-stage').boundingBox();assert.ok(stage.y>=88,'desktop overview begins below navigation');
  const scene=await p.locator('.lb-stage-world').boundingBox(),panels=await p.locator('.lb-stage-boards').boundingBox();
  assert.ok(panels.y>=scene.y+scene.height,'ranking panels never cover the campus');
  assert.ok(await p.locator('.lb-stage-art').evaluate(img=>img.complete&&img.naturalWidth>0));
  for(const v of data.views){
   await p.locator(`.lb-stage-tabs [data-stage-select="${v.key}"]`).click();
   assert.equal(await p.locator('.lb-stage').getAttribute('data-current-view'),v.key);
   const leaders=data.models.filter(m=>m.results[v.key].score!=null).sort((a,b)=>b.results[v.key].score-a.results[v.key].score).slice(0,3);
   for(let i=0;i<3;i++){
    const label=p.locator(`[data-podium-rank="${i+1}"]`);
    assert.equal(await label.locator('.lb-podium-name').innerText(),leaders[i].name);
    assert.equal(await label.locator('strong').innerText(),leaders[i].results[v.key].score.toFixed(2));
   }
   assert.equal(await p.locator('.lb-result:not([hidden])').first().getAttribute('data-model'),leaders[0].id);
   assert.equal(await p.locator(`[data-rank-view="${v.key}"]`).getAttribute('aria-pressed'),'true');
  }
  await p.locator('#lb-search').fill('no match');
  await p.locator('.lb-stage-board[data-board-view="act"] [data-stage-model="pi05"]').click();
  assert.equal(await p.locator('#detail-pi05').isVisible(),true);assert.equal(await p.locator('#lb-search').inputValue(),'');
  assert.ok(new URL(p.url()).searchParams.get('model')==='pi05');
  await p.goBack();assert.equal(await p.locator('#detail-pi05').isVisible(),false);
  await p.goto(new URL('leaderboard.html?view=act',base).href);assert.equal(await p.locator('.lb-podium-rank-1 .lb-podium-name').innerText(),'π0.5');
  await p.locator('[data-rank-view="coupling"]').click();assert.equal(await p.locator('.lb-stage').getAttribute('data-current-view'),'coupling');
  for(const width of [320,390,820,1024,1440,1920,2910]){
   await p.setViewportSize({width,height:900});await p.goto(new URL('leaderboard.html?view=coupling',base).href);
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'page overflow '+width);
   const world=await p.locator('.lb-stage-world').boundingBox();assert.ok(world.x+world.width<=width,'scene fits '+width);
   if(width>850){assert.ok(Math.abs(world.width-width)<2,'artwork fills desktop width '+width);assert.ok(Math.abs(world.width/world.height-1983/793)<.01,'full image aspect ratio '+width);assert.equal(await p.locator('.lb-stage-metric').evaluate(e=>getComputedStyle(e).position),'absolute','metric occupies no layout space');}
   for(const r of await p.locator('.lb-podium-label').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON())))assert.ok(r.left>=world.x&&r.right<=world.x+world.width,'podium labels fit '+width);
   assert.equal(await p.locator('.lb-stage-board[data-board-view="coupling"] ol').isVisible(),true);
   if(width===390){await p.locator('.lb-board-title[data-stage-select="act"]').click();assert.equal(await p.locator('.lb-stage-board[data-board-view="act"] ol').isVisible(),true);}
  }
  assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);
  console.log('PASS: static artwork, real top-three scores, hero/table synchronization, model details, URL/history, no Three.js, first-screen desktop fit and six responsive widths');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
