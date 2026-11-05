const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const data = require('../data/leaderboard-results.json');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
const url = new URL('leaderboard.html', base).href;
const box = (page, selector) => page.locator(selector).boundingBox();
const overlaps = (a, b) => a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE});
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 900}, reducedMotion: 'reduce'});
    const errors = [], bad = [], requests = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', r => { if (r.status() >= 400) bad.push(r.url()); });
    page.on('request', r => requests.push(r.url()));
    await page.goto(url);
    await page.evaluate(() => document.fonts.ready);
    assert.ok(!requests.some(u => /three|stage-scene/.test(u)), 'no WebGL dependency');
    assert.equal(await page.locator('.lb-stage canvas, .lb-stage-board').count(), 0);
    assert.ok(await page.locator('.lb-stage-art').evaluate(img => img.complete && img.naturalWidth > 0));

    for (const view of data.views) {
      await page.locator(`.lb-stage-tabs [data-stage-select="${view.key}"]`).click();
      assert.equal(await page.locator('.lb-stage').getAttribute('data-current-view'), view.key);
      const leaders = data.models.filter(m => m.results[view.key].score != null)
        .sort((a, b) => b.results[view.key].score - a.results[view.key].score).slice(0, 3);
      for (let i = 0; i < 3; i++) {
        const label = page.locator(`[data-podium-rank="${i + 1}"]`);
        assert.equal(await label.locator('.lb-podium-name').innerText(), leaders[i].name);
        assert.equal(await label.locator('strong').innerText(), leaders[i].results[view.key].score.toFixed(2));
      }
      assert.equal(await page.locator('.lb-result:not([hidden])').first().getAttribute('data-model'), leaders[0].id);
      assert.equal(await page.locator(`[data-rank-view="${view.key}"]`).getAttribute('aria-pressed'), 'true');
    }
    await page.locator('.lb-stage-tabs [data-stage-select="act"]').click();
    await page.locator('.lb-podium-rank-1').click();
    assert.equal(await page.locator('#detail-pi05').isVisible(), true);
    assert.equal(new URL(page.url()).searchParams.get('model'), 'pi05');
    await page.goBack();
    assert.equal(await page.locator('#detail-pi05').isVisible(), false);

    for (const [width, height] of [[320,640], [390,844], [820,900], [1024,768], [1440,900], [1440,720], [1774,887], [1920,1080], [2560,720], [2910,1496]]) {
      await page.setViewportSize({width, height});
      await page.goto(url + '?view=coupling');
      await page.evaluate(() => document.fonts.ready);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `page overflow ${width}`);
      const stage = await box(page, '.lb-stage');
      assert.equal(stage.x, 0);
      assert.equal(stage.y, 0, 'no reserved white band above the hero');
      assert.ok(Math.abs(stage.width - width) < 1 && Math.abs(stage.height - height) < 1, `full viewport ${width}×${height}`);
      const nav = await box(page, '.header'), head = await box(page, '.lb-stage-head');
      const copy = await box(page, '.lb-stage-head > div:first-child');
      const controls = await box(page, '.lb-stage-controls');
      assert.ok(nav.y > 0 && nav.y + nav.height < head.y, 'floating navigation clears the title');
      const expectedNavWidth = width <= 1040 ? Math.min(840, width - 24) : Math.min(1600, width * .82);
      assert.ok(Math.abs(nav.width - expectedNavWidth) < 1, 'preserve the original shared navigation width');
      const tabs = await box(page, '.lb-stage-tabs');
      assert.ok(Math.abs(tabs.x + tabs.width - head.x - head.width) < 1, 'suite tabs remain on the right at every width');
      const caption = await box(page, '.lb-stage-caption');
      const scene = await box(page, '.lb-stage-scene');
      const art = await box(page, '.lb-stage-art'), video = await box(page, '.lb-stage-motion-video');
      for (const property of ['x', 'y', 'width', 'height']) assert.ok(Math.abs(art[property] - video[property]) < 1, 'image and motion remain aligned');
      assert.ok(Math.abs(scene.width / scene.height - 1983 / 793) < .01, 'undistorted scene');
      for (const rect of await page.locator('.lb-podium-label').evaluateAll(es => es.map(e => e.getBoundingClientRect().toJSON()))) {
        assert.ok(rect.left >= 0 && rect.right <= width, `all podium labels visible ${width}`);
        assert.ok(!overlaps(rect, caption) && !overlaps(rect, copy) && !overlaps(rect, controls), `rankings clear the controls ${width}×${height}`);
      }
      const footer = await box(page, '.lb-stage-footer');
      assert.ok(footer.y + footer.height <= height && footer.x >= 0 && footer.x + footer.width <= width, 'footer remains within the scene');
      await page.locator('.lb-stage-tabs [data-stage-select="act"]').click();
      assert.equal(await page.locator('.lb-podium-rank-1 .lb-podium-name').innerText(), 'π0.5');
      console.log('PASS full viewport', width, height);
    }
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(url);
    await page.locator('#menuToggle').click();
    assert.equal(await page.locator('#siteNav').isVisible(), true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#menuToggle').getAttribute('aria-expanded'), 'false');
    await page.locator('.lb-stage-tabs [data-stage-select="act"]').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('.lb-stage').getAttribute('data-current-view'), 'act');
    await page.locator('.lb-stage-full').click();
    await page.waitForFunction(() => document.querySelector('#results').getBoundingClientRect().top >= 0 && document.querySelector('#results').getBoundingClientRect().top < 200);
    assert.equal(await page.locator('[data-rank-view="act"]').getAttribute('aria-pressed'), 'true');
    assert.deepEqual(errors, []);
    assert.deepEqual(bad, []);
    console.log('PASS: full-viewport artwork, floating controls, aligned rankings, responsive layout, mobile menu, keyboard, results navigation and preserved scores');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
