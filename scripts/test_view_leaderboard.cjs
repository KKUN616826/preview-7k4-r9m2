/* Homepage leaderboard preview regression; full results have their own interaction suite. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/leaderboard-results.json'),'utf8'));
 const views=['mind','act','coupling'];
 const reported=data.models.filter(m=>views.every(v=>m.results[v].score!=null));
 const expectedOrder=view=>[...reported].sort((a,b)=>b.results[view].score-a.results[view].score).map(m=>m.name);
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const base=process.env.HERO_PREVIEW_URL||'http://127.0.0.1:8765/';
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base,{waitUntil:'load'});
  const preview=page.locator('#top-ten.home-leaderboard');await preview.scrollIntoViewIfNeeded();
  assert.equal(await page.locator('.view-leaderboard').count(),0);
  const ranked=async()=>(await preview.locator('tbody tr').evaluateAll(rows=>rows.map(r=>r.dataset)));
  assert.equal((await ranked()).length,reported.length,'one row per model with reported scores');
  for(const view of views){
   await preview.locator(`[data-hl-view="${view}"]`).click();
   assert.equal(await preview.locator(`[data-hl-view="${view}"]`).getAttribute('aria-pressed'),'true');
   const scores=(await ranked()).map(d=>Number(d[view]));
   assert.deepEqual(scores,[...scores].sort((a,b)=>b-a),`rows ranked by ${view}`);
   const shown=await preview.locator('tbody th').evaluateAll(cells=>cells.map(c=>[...c.querySelector('.hl-model').childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim()));
   assert.deepEqual(shown,expectedOrder(view),`model order for ${view}`);
  }
  assert.equal(await preview.locator('a[href="leaderboard.html"]').count(),1);
  for(const width of [320,390,700,1024,1920]){
   await page.setViewportSize({width,height:900});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'overflow at '+width);
   assert.equal(await preview.locator('a[href="leaderboard.html"]').isVisible(),true);
   const scoreColumns=await preview.locator('tbody tr:first-child td.hl-score').evaluateAll(cells=>cells.filter(c=>getComputedStyle(c).display!=='none').length);
   assert.ok(scoreColumns>=1,'at least one score column visible at '+width);
  }
  await preview.locator('a[href="leaderboard.html"]').click();await page.waitForURL('**/leaderboard.html');
  assert.equal(await page.locator('.lb-table').count(),1);
  assert.deepEqual(errors,[]);
  console.log('PASS: homepage leaderboard preview ranks every reported model by suite, fits all widths and links to the standalone leaderboard');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
