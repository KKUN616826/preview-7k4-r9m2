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
    assert.equal(await page.locator('.lb-stage-board').count(),0);
    assert.equal(await page.locator('.lb-result').count(),16);
    assert.equal(await firstId(),'astra');
    assert.equal(await page.locator('.lb-result').first().locator('.lb-number').count(),6);
    assert.match(await page.locator('#lb-status-line').textContent(),/16 entries · 7 reported/);

    await page.locator('[data-rank-view="act"]').click();
    assert.equal(await firstId(),'pi05');
    await page.locator('[data-sort-view="act"][data-sort-metric="score"]').click();
    assert.equal(await firstId(),'xvla');
    assert.equal(await page.locator('[data-sort-cell="act-score"]').getAttribute('aria-sort'),'ascending');
    assert.equal(await page.locator('.lb-result:not([hidden])').last().locator('.lb-rank').textContent(),'—');
    await page.locator('#lb-reset').click();
    await page.locator('#lb-search').fill('gEmInI');
    assert.equal(await page.locator('.lb-result:not([hidden])').count(),2);
    await page.locator('#lb-search').fill('no matching model');
    assert.equal(await page.locator('#lb-empty').isVisible(),true);
    await page.locator('#lb-clear').click();
    await page.locator('#lb-status').selectOption('pending');
    assert.equal(await page.locator('.lb-result:not([hidden])').count(),9);
    assert.ok((await page.locator('.lb-result:not([hidden]) .lb-rank').allTextContents()).every(s=>s==='—'));
    await page.locator('#lb-reset').click();
    await page.locator('[data-rank-view="coupling"]').click();
    await page.locator('#lb-metric').selectOption('success');
    const gemini=page.locator('.lb-result[data-model="gemini"]');
    assert.equal(await gemini.locator('[data-group="coupling"][data-value="success"]').textContent(),'0.0');
    await page.locator('#lb-reset').click();
    const details=page.locator('.lb-result[data-model="astra"] .lb-details-button');
    await details.click();
    assert.equal(await page.locator('#detail-astra').isVisible(),true);
    assert.equal(await details.evaluate(el=>el===document.activeElement),true);
    await page.reload();
    assert.equal(await page.locator('#detail-astra').isVisible(),true);
    await page.locator('[data-rank-view="act"]').click();
    await page.goBack();
    assert.equal(await page.locator('[data-rank-view="mind"]').getAttribute('aria-pressed'),'true');
    assert.equal(await page.locator('#detail-astra').isVisible(),true);
    await page.locator('#lb-paradigm').selectOption('vla');
    assert.equal(await page.locator('#detail-astra').isVisible(),false);
    assert.ok(!new URL(page.url()).searchParams.has('model'));

    // Every view and metric sorts correctly, with unreported entries always last.
    for(const view of data.views) for(const metric of ['score','success']) {
      await page.goto(new URL(`leaderboard.html?view=${view.key}&metric=${metric}`,base).href);
      const expected=data.models.filter(m=>m.results[view.key][metric]!=null).sort((a,b)=>b.results[view.key][metric]-a.results[view.key][metric]).map(m=>m.id);
      const actual=await page.locator('.lb-result').evaluateAll(rows=>rows.map(r=>r.dataset.model));
      assert.deepEqual(actual.slice(0,expected.length),expected);
    }
    console.log('PASS: original results, six metric sorts, zero versus missing, filters, details, focus and history');

    for(const width of [320,390,820,1024,1440,1920]) {
      await page.setViewportSize({width,height:1000});
      await page.goto(new URL('leaderboard.html',base).href);
      await page.evaluate(()=>document.fonts.ready);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`page overflow ${width}`);
      if(width<=1040) {
        assert.equal(await page.locator('td[data-group="act"]').first().isVisible(),false);
        await page.locator('#lb-all-metrics').click();
        assert.equal(await page.locator('td[data-group="act"]').first().isVisible(),true);
        await page.locator('#lb-all-metrics').click();
        await page.locator('[data-rank-view="act"]').click();
        assert.equal(await page.locator('td[data-group="act"]').first().isVisible(),true);
        assert.equal(await page.locator('td[data-group="mind"]').first().isVisible(),false);
      }
      if(shots && [390,1440].includes(width)) {
        fs.mkdirSync(shots,{recursive:true});
        await page.goto(new URL('leaderboard.html',base).href);
        await page.screenshot({path:path.join(shots,`leaderboard-${width}.png`),fullPage:true});
      }
      console.log('PASS: responsive table',width);
    }
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(new URL('leaderboard.html',base).href);
    await page.locator('.lb-stage-tabs [data-stage-select="act"]').click();
    await page.locator('.lb-stage-full').click();
    assert.equal(await page.locator('[data-rank-view="act"]').getAttribute('aria-pressed'),'true');
    await page.waitForFunction(()=>document.getElementById('results').getBoundingClientRect().y<200);
    assert.ok((await page.locator('#results').boundingBox()).y>=88);
    assert.deepEqual(errors,[]);
    console.log('PASS: static hero navigation and no browser errors');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exit(1)});
