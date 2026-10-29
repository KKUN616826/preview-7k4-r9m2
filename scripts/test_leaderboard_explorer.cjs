const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {chromium} = require('playwright');
const data = require('../data/leaderboard-results.json');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
const shots = process.env.LEADERBOARD_SCREENSHOTS;

(async () => {
  const old = execFileSync('git', ['show', 'checkpoint-before-leaderboard:leaderboard.html'], {cwd:path.join(__dirname,'..'), encoding:'utf8'});
  const snapshot = JSON.parse(old.match(/<script[^>]*id="viewLeaderboardData"[^>]*>(.*?)<\/script>/s)[1]);
  assert.deepEqual(data.models, snapshot.models, 'Preserve every reported value, missing value, model and demo link');
  const homepage=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
  const originalHomepage=execFileSync('git',['show','HEAD:index.html'],{cwd:path.join(__dirname,'..'),encoding:'utf8'});
  const homePayload=s=>JSON.parse(s.match(/<script[^>]*id="viewLeaderboardData"[^>]*>(.*?)<\/script>/s)[1]);
  assert.deepEqual(homePayload(homepage),homePayload(originalHomepage),'Homepage result snapshot remains unchanged');
  const browser = await chromium.launch({headless:true, ...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(new URL('leaderboard.html',base).href);
    const firstId=()=>page.locator('.lb-result:not([hidden])').first().getAttribute('data-model');
    assert.equal(await page.locator('.lb-filters, #lb-search, #lb-metric').count(),0);
    assert.equal(await page.locator('.lb-result:not([hidden])').count(),7);
    assert.equal(await firstId(),'astra');
    await page.locator('#lb-pending').click();
    assert.equal(await page.locator('.lb-result:not([hidden])').count(),16);
    assert.ok((await page.locator('.lb-unreported .lb-rank').allTextContents()).every(s=>s==='—'));
    await page.locator('#lb-pending').click();
    const details=page.locator('.lb-result[data-model="astra"] .lb-model-button');
    await details.click();
    assert.equal(await page.locator('#detail-astra').isVisible(),true);
    assert.equal(await details.evaluate(el=>el===document.activeElement),true);
    await page.reload();
    assert.equal(await page.locator('#detail-astra').isVisible(),true);
    await page.locator('[data-rank-view="act"]').click();
    assert.equal(await firstId(),'pi05');
    await page.goBack();
    assert.equal(await page.locator('#detail-astra').isVisible(),true);
    for(const view of data.views) for(const metric of ['score','success']) {
      await page.goto(new URL(`leaderboard.html?view=${view.key}&metric=${metric}`,base).href);
      const expected=data.models.filter(m=>m.results[view.key][metric]!=null).sort((a,b)=>b.results[view.key][metric]-a.results[view.key][metric]).map(m=>m.id);
      const actual=await page.locator('.lb-result:not([hidden])').evaluateAll(rows=>rows.map(r=>r.dataset.model));
      assert.deepEqual(actual,expected);
      await page.locator(`[data-sort-view="${view.key}"][data-sort-metric="${metric}"]`).click();
      assert.equal(await page.locator(`[data-sort-cell="${view.key}-${metric}"]`).getAttribute('aria-sort'),'ascending');
    }
    for(const width of [320,390,820,1024,1440,1920]) {
      await page.setViewportSize({width,height:1000});
      await page.goto(new URL('leaderboard.html#results',base).href);
      await page.evaluate(()=>document.fonts.ready);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`page overflow ${width}`);
      assert.equal(await page.locator('.lb-result:not([hidden]) td[data-group="act"]').first().isVisible(),false);
      await page.locator('[data-rank-view="act"]').click();
      assert.equal(await page.locator('.lb-result:not([hidden]) td[data-group="act"]').first().isVisible(),true);
      if(shots && [390,1440].includes(width)) {
        fs.mkdirSync(shots,{recursive:true});
        await page.locator('#results').screenshot({path:path.join(shots,`leaderboard-${width}.png`)});
      }
      console.log('PASS responsive',width);
    }
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(new URL('leaderboard.html',base).href);
    await page.locator('.lb-stage-tabs [data-stage-select="act"]').click();
    await page.locator('.lb-stage-full').click();
    assert.equal(await page.locator('[data-rank-view="act"]').getAttribute('aria-pressed'),'true');
    assert.deepEqual(errors,[]);
    console.log('PASS: preserved data, pending rows, sorting, details, history, stage navigation and no browser errors');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exit(1)});
