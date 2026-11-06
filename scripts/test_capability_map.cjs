const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const url = process.env.PREVIEW_URL || 'http://127.0.0.1:8766/';
(async () => {
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(url);
    const root = page.locator('#capability-explorer');
    await page.waitForFunction(() => document.querySelector('.capability-map').dataset.texture === 'loaded');
    assert.deepEqual(await root.locator('.cm-suite-title').allTextContents(), ['Mind', 'Act', 'Mind2Act']);
    assert.equal(await root.locator('.cm-choices,.cm-example,.cm-case-demands').count(), 0);
    assert.equal(await root.locator('[data-task]').count(), 30);
    assert.match(await root.locator('.cm-suite-title').first().evaluate(e => getComputedStyle(e).fontFamily), /^Sora/);
    const suites = JSON.parse(await root.locator('#cm-data').textContent());
    let checked = 0;
    for (const suite of suites) {
      await root.locator(`[data-region-label="${suite.slug}"]`).click();
      await page.waitForTimeout(150);
      assert.equal(await root.locator('.cm-suite-intro:visible').count(), 3);
      for (const task of suite.cases) {
        const card = root.locator(`[data-task="${task.id}"]`);
        assert.equal(await card.isVisible(), true);
        assert.equal(await card.evaluate(e => getComputedStyle(e).borderTopWidth), '0px');
        await card.focus();
        await page.keyboard.press('Enter');
        assert.equal(await root.locator('.cm-preview-link').getAttribute('href'), `tasks/${task.id}.html`);
        await page.keyboard.press('Escape');
        assert.equal(await root.locator('.cm-task-preview').isVisible(), false);
        assert.equal(await card.evaluate(e => e === document.activeElement), true);
        checked++;
      }
    }
    assert.equal(checked, 30);
    await root.locator('.cm-reset').click();
    await page.waitForTimeout(150);
    const orbit = root.locator('.cm-orbit');
    const before = await root.locator('[data-task="CP04"]').getAttribute('style');
    await orbit.focus();
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(150);
    assert.notEqual(await root.locator('[data-task="CP04"]').getAttribute('style'), before);
    for (const width of [320,390,820,1024,1440,1920]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.waitForTimeout(100);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `overflow at ${width}`);
      const blocks = await root.locator('.cm-suite-intro').all();
      const bounds = await Promise.all(blocks.map(b => b.boundingBox()));
      assert.ok(bounds[0].y + bounds[0].height <= bounds[1].y + 1);
      assert.ok(bounds[1].y + bounds[1].height <= bounds[2].y + 1);
      if (width >= 1024) {
        const copy = await root.locator('.cm-copy').boundingBox(), globe = await orbit.boundingBox();
        assert.ok(copy.x + copy.width + 23 <= globe.x);
      }
    }
    await page.setViewportSize({ width:1440,height:1000 });
    const suiteLinks = root.locator('a.cm-suite-intro');
    assert.equal(await suiteLinks.count(), 3);
    const lineColors = [];
    for (const slug of ['mind', 'act', 'mind2act']) {
      const link = suiteLinks.filter({ has: page.locator(`#cm-title-${slug}`) });
      assert.equal(await link.getAttribute('href'), `benchmark.html#suite-${slug}`);
      const line = await link.evaluate(e => ({ width:getComputedStyle(e).borderLeftWidth, color:getComputedStyle(e).borderLeftColor }));
      assert.equal(line.width, '2px');
      lineColors.push(line.color);
      await link.hover();
      assert.equal(await link.evaluate(e => getComputedStyle(e).transform), 'none', 'reduced motion disables lift');
    }
    assert.equal(new Set(lineColors).size, 3);
    await page.emulateMedia({ reducedMotion:'no-preference' });
    await suiteLinks.first().hover();
    await page.waitForFunction(() => getComputedStyle(document.querySelector('a.cm-suite-intro')).transform === 'matrix(1, 0, 0, 1, 0, -4)');
    await page.emulateMedia({ reducedMotion:'reduce' });
    for (const slug of ['mind', 'act', 'mind2act']) {
      const link = page.locator(`a.cm-suite-intro[href="benchmark.html#suite-${slug}"]`);
      if (slug === 'mind') { await link.focus(); await page.keyboard.press('Enter'); }
      else await link.click();
      await page.waitForURL(`**/benchmark.html#suite-${slug}`);
      await page.waitForFunction(slug => document.querySelector(`.bo-suite-tabs a[href="#suite-${slug}"]`)?.getAttribute('aria-current') === 'location', slug);
      const target = page.locator(`#suite-${slug}`);
      await page.waitForFunction(slug => {const b=document.getElementById(`suite-${slug}`).getBoundingClientRect();return b.top >= 0 && b.top < innerHeight/2;}, slug);
      assert.equal(await target.isVisible(), true);
      await page.goto(url);
      await page.waitForFunction(() => document.querySelector('.capability-map').dataset.texture === 'loaded');
    }
    await root.locator('.cm-reset').click();
    await page.waitForTimeout(150);
    await root.screenshot({path:'/tmp/capability-stacked-desktop.png'});
    await page.setViewportSize({width:390,height:844});
    await root.screenshot({path:'/tmp/capability-stacked-mobile.png'});
    const fallback = await browser.newPage();
    await fallback.route('**/vendor/three/**', r => r.abort());
    await fallback.goto(url);
    await fallback.waitForFunction(() => document.querySelector('.capability-map').dataset.renderer === 'fallback');
    await fallback.locator('[data-task="CP04"]').click();
    assert.equal(await fallback.locator('.cm-task-preview').isVisible(), true);
    assert.equal(await fallback.locator('.cm-motion').isDisabled(), true);
    assert.deepEqual(errors, []);
    console.log('PASS: three colored suite links, hover/reduced motion, Benchmark anchor navigation, 30 task previews, keyboard rotation/focus, six viewport sizes and WebGL fallback.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
