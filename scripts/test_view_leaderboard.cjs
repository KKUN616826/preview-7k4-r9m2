/* Homepage board regression; standalone behavior is covered by test_leaderboard_explorer.cjs. */
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
(async () => {
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 const base=process.env.HERO_PREVIEW_URL||'http://127.0.0.1:8765/';
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*.mp4',r=>r.abort());
  await page.goto(base,{waitUntil:'domcontentloaded'});
  const board=page.locator('.view-leaderboard');
  const data=JSON.parse(await board.locator('#viewLeaderboardData').textContent());
  for(const view of data.views){
   await board.locator(`[data-board-view="${view.key}"]`).click();
   assert.equal(await board.getAttribute('data-view'),view.key);
   assert.deepEqual(await board.locator('.board-task-links a').allTextContents(),view.tasks);
   for(const paradigm of ['all',...Object.keys(data.paradigms)]){
    await board.locator('#board-paradigm').selectOption(paradigm);
    const expected=data.models.filter(m=>paradigm==='all'||m.paradigm===paradigm);
    assert.equal(await board.locator('tbody tr:visible').count(),expected.length);
    for(const model of expected){
     const row=board.locator(`tr[data-model-id="${model.id}"]`);
     const result=model.results[view.key];
     assert.equal(await row.locator('td').nth(2).textContent(),result.score==null?'—':result.score.toFixed(2));
    }
   }
  }
  await board.locator('#board-paradigm').selectOption('all');
  await board.locator('#model-search').fill('no matching model');
  assert.equal(await board.locator('.board-empty').isVisible(),true);
  await board.locator('#model-search').fill('');
  for(const width of [320,390,820,1440,1920]){
   await page.setViewportSize({width,height:1000});
   await board.scrollIntoViewIfNeeded();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  }
  await page.setViewportSize({width:1440,height:1000});
  await board.locator('[data-board-view="mind"]').focus();
  await page.keyboard.press('ArrowRight');
  assert.equal(await board.getAttribute('data-view'),'act');
  await board.locator('[data-board-view="coupling"]').click();
  await board.locator('#board-paradigm').selectOption('coding');
  await board.locator('#model-search').fill('gpt');
  await page.locator('.full-leader-link a').click();
  await page.waitForURL('**/leaderboard.html?**');
  assert.equal(await page.locator('[data-rank-view="coupling"]').getAttribute('aria-pressed'),'true');
  assert.equal(await page.locator('#lb-paradigm').inputValue(),'coding');
  assert.equal(await page.locator('#lb-search').inputValue(),'gpt');
  assert.equal(await page.locator('.lb-result:not([hidden])').count(),1);
  assert.deepEqual(errors,[]);
  console.log('PASS: unchanged homepage results, filters, keyboard, responsive layout and standalone handoff');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
