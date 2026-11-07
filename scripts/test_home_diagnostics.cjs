/* Checks for the coming-soon improvement loop drawn on the homepage (#model-diagnostics). */
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE});
  try {
    for (const width of [320, 390, 820, 1440]) {
      const page = await browser.newPage({viewport: {width, height: 1000}});
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(base, {waitUntil: 'domcontentloaded'});
      const root = page.locator('#model-diagnostics');
      assert.equal(await root.count(), 1);
      // It follows the diagnosis cards and carries no video of its own.
      assert.equal(await page.evaluate(() => document.querySelector('#diagnosis').nextElementSibling?.id), 'model-diagnostics');
      assert.equal(await root.locator('video').count(), 0);
      assert.equal(await root.getAttribute('data-playing'), 'false', 'no animation before entering the viewport');
      await root.locator('.lp-figure').scrollIntoViewIfNeeded();
      await page.waitForFunction(() => document.querySelector('#model-diagnostics').dataset.playing === 'true');
      // The loop advances: the step indicator changes and data packets travel the return path.
      const steps = new Set();
      for (let i = 0; i < 12; i++) { steps.add(await root.locator('.lp-figure').getAttribute('data-step')); await page.waitForTimeout(450); }
      assert.ok(steps.size >= 3, `steps seen: ${[...steps]}`);
      const toggle = root.locator('.lp-toggle');
      await toggle.click();
      assert.equal(await root.getAttribute('data-playing'), 'false');
      assert.equal(await toggle.getAttribute('aria-pressed'), 'true');
      const still = await root.locator('.lp-figure').getAttribute('data-step');
      await page.waitForTimeout(700);
      assert.equal(await root.locator('.lp-figure').getAttribute('data-step'), still, 'paused loop stays put');
      await toggle.click();
      await page.waitForFunction(() => document.querySelector('#model-diagnostics').dataset.playing === 'true');
      // Layout: no horizontal overflow; nodes in one row on wide screens and stacked on narrow ones.
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `overflow at ${width}`);
      const tops = await root.locator('.lp-node').evaluateAll(n => n.map(e => Math.round(e.getBoundingClientRect().top)));
      if (width >= 1024) assert.equal(new Set(tops).size, 1, 'four nodes in one row');
      if (width <= 820) assert.equal(new Set(tops).size, 4, 'nodes stacked');
      assert.match(await root.locator('.lp-disclaimer').textContent(), /not results of any model/);
      // The model's pixel avatar follows its profile: one per round, exactly one shown.
      assert.equal(await root.locator('.lp-avatar-img').count(), 4);
      assert.equal(await root.locator('.lp-avatar-img.is-current').count(), 1);
      assert.match(await root.locator('.lp-node--model .lp-code').textContent(), /^[EI][SN][TF][JP]$/);
      await page.emulateMedia({reducedMotion: 'reduce'});
      await page.waitForFunction(() => document.querySelector('#model-diagnostics').dataset.playing === 'false');
      assert.equal(await toggle.isHidden(), true);
      assert.equal(await root.locator('.lp-data i.is-filled').count(), 12, 'reduced motion shows a complete still');
      assert.deepEqual(errors, []);
      await page.close();
    }
    console.log('PASS: improvement loop follows the diagnosis cards, plays only in view, pauses, reflows and respects reduced motion');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
