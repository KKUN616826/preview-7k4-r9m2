/* Run with the same Playwright / CHROMIUM_EXECUTABLE environment as other browser checks. */
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_EXECUTABLE });
  try {
    for (const width of [320, 390, 700, 820, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      const missing = [];
      page.on('response', response => {
        if (response.status() >= 400 && /home-diagnostics|lunar-silver/.test(response.url())) missing.push(response.url());
      });
      await page.route('**/*.mp4', route => route.abort());
      await page.goto(base, { waitUntil: 'domcontentloaded' });
      const root = page.locator('#model-diagnostics');
      await root.scrollIntoViewIfNeeded();
      await page.waitForFunction(() => document.querySelector('#model-diagnostics').dataset.playing === 'true');
      assert.equal(await root.count(), 1);
      assert.equal(await root.locator('h2').textContent(), 'Your model. Decoded.');
      assert.deepEqual(missing, [], 'All teaser assets must load');
      const layout = await root.evaluate(el => {
        const r = el.getBoundingClientRect();
        return {
          left: r.left, right: r.right, height: r.height,
          bottomOfResources: document.querySelector('#resources-overview').getBoundingClientRect().bottom,
          top: r.top,
          overflowing: [...el.querySelectorAll('button, .md-report, h2')].some(e => {
            const b = e.getBoundingClientRect();
            return b.left < r.left - 1 || b.right > r.right + 1;
          })
        };
      });
      assert.ok(layout.left >= 0 && layout.right <= width, `Section fits viewport ${width}`);
      assert.ok(!layout.overflowing, `Report, controls and title fit at ${width}`);
      if (width === 1440) assert.ok(layout.height <= 560, 'Desktop teaser stays compact');
      assert.ok(layout.top >= layout.bottomOfResources, 'Preview appears after existing Home content');

      const pause = root.locator('.md-pause');
      await pause.click();
      assert.equal(await root.getAttribute('data-playing'), 'false');
      assert.equal(await pause.getAttribute('aria-pressed'), 'true');
      await root.evaluate(el => el.getAnimations({ subtree: true }).forEach(a => { a.currentTime = 6400; }));
      const frozen = await root.evaluate(el => el.getAnimations({ subtree: true }).map(a => a.currentTime));
      await page.waitForTimeout(80);
      assert.deepEqual(await root.evaluate(el => el.getAnimations({ subtree: true }).map(a => a.currentTime)), frozen, 'Pause freezes the complete timeline');
      assert.equal(await root.locator('.md-report').evaluate(el => getComputedStyle(el).opacity), '1', 'Card is revealed at the final hold');
      assert.ok(await root.locator('.md-report').evaluate(el => getComputedStyle(el).maskImage !== 'none'), 'Card lower edge dissolves into the background');
      assert.ok(await root.locator('.md-particles').evaluate(el => [...el.children].filter(p => Number(getComputedStyle(p).opacity) > .1).length > 80), 'The particle edge remains visible during the final hold');
      if (width === 1440) {
        const frame = time => root.evaluate((el, time) => {
          el.getAnimations({ subtree: true }).forEach(a => { a.currentTime = time; });
          const style = selector => getComputedStyle(el.querySelector(selector));
          return {
            card: Number(style('.md-report').opacity),
            model: Number(style('.md-model-pixels').opacity),
            scores: Number(style('.md-scores').opacity),
            findings: Number(style('.md-failures').opacity),
            header: Number(style('.md-heading').opacity),
            harness: Number(style('.md-harness-unit').opacity),
            example: Number(style('.md-example-label').opacity),
            modelWidth: el.querySelector('.md-model-pixels').getBoundingClientRect().width,
            modelCenter: el.querySelector('.md-model-pixels').getBoundingClientRect().left + el.querySelector('.md-model-pixels').getBoundingClientRect().width / 2 - el.getBoundingClientRect().left,
            sceneWidth: el.getBoundingClientRect().width,
            arcs: ['.md-arc-evaluate', '.md-arc-trace', '.md-arc-diagnose'].map(s => parseFloat(style(s).strokeDashoffset)),
            durations: [...new Set(el.getAnimations({ subtree: true }).map(a => a.effect.getTiming().duration))]
          };
        }, time);
        const start = await frame(0);
        assert.equal(start.model, 1);
        assert.equal(start.card, 0);
        assert.equal(start.header, 0, 'No heading at the opening');
        assert.equal(start.harness, 0, 'No harness at the opening');
        assert.equal(start.example, 0, 'No example subtitle at the opening');
        assert.ok(start.modelWidth > 210, 'Opening model is large');
        assert.ok(Math.abs(start.modelCenter - start.sceneWidth / 2) < 3, 'Opening model is centered in the whole scene');
        assert.deepEqual(start.durations, [8000], 'Every moving element shares the eight-second loop');
        const moving = await frame(2000);
        assert.ok(moving.modelCenter < start.modelCenter && moving.modelCenter > 150, 'The same model gradually travels left');
        assert.equal(moving.header, 0);
        const positioned = await frame(2800);
        assert.ok(positioned.modelCenter < 130 && positioned.modelWidth < start.modelWidth * .7);
        assert.ok(positioned.harness > 0 && positioned.card === 0, 'Harness emerges after model travel, before the card');
        const evaluation = await frame(3390);
        assert.ok(evaluation.arcs[0] < .1 && evaluation.arcs[1] === 1 && evaluation.arcs[2] === 1, 'Evaluation happens before tracing and diagnosis');
        const tracing = await frame(3790);
        assert.ok(tracing.arcs[1] < .1 && tracing.arcs[2] === 1, 'Tracing precedes diagnosis');
        const diagnosed = await frame(4200);
        assert.ok(diagnosed.arcs.every(value => value === 0));
        assert.equal(diagnosed.card, 0, 'Card waits until diagnosis is complete');
        const reveal = await frame(4600);
        assert.ok(reveal.card > .9 && reveal.scores === 0, 'Identity precedes detailed results');
        assert.equal(reveal.header, 0, 'Heading waits until the report reveal');
        const complete = await frame(5600);
        assert.equal(complete.card, 1);
        assert.equal(complete.findings, 1);
        assert.equal((await frame(6400)).header, 1, 'Final heading is revealed only after the card');
        assert.equal((await frame(7500)).card, 1, 'Final profile stays readable through 7.5s');
        const loop = await frame(8000);
        assert.equal(loop.card, start.card);
        assert.equal(loop.model, start.model);
        assert.ok(Math.abs(loop.modelCenter - start.modelCenter) < 1);
        console.log('PASS centered model opening, spatial travel, harness then report then copy, eight-second loop');
      }
      await root.locator('.md-replay').click();
      assert.equal(await root.getAttribute('data-playing'), 'true');
      assert.ok(await root.evaluate(el => el.getAnimations({ subtree: true }).every(a => a.currentTime < 400)), 'Replay restarts all parts together');
      await page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
      await page.waitForFunction(() => document.querySelector('#model-diagnostics').dataset.playing === 'false');

      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.waitForFunction(() => !document.querySelector('#model-diagnostics').classList.contains('md-enabled'));
      assert.equal(await root.evaluate(el => el.getAnimations({ subtree: true }).length), 0);
      assert.equal(await root.locator('.md-report').evaluate(el => getComputedStyle(el).opacity), '1');
      assert.ok(await root.locator('.md-pause').isHidden());
      assert.ok(await root.locator('.md-replay').isDisabled());
      console.log(`PASS ${width}px: layout, asset loading, final reveal, pause/replay, offscreen pause, reduced motion`);
      await page.close();
    }
    const noJS = await browser.newPage({ javaScriptEnabled: false, viewport: { width: 1440, height: 1000 } });
    await noJS.route('**/*.mp4', route => route.abort());
    await noJS.goto(base, { waitUntil: 'domcontentloaded' });
    assert.ok(await noJS.locator('#model-diagnostics .md-report').isVisible(), 'The illustrative report remains visible without JavaScript');
    await noJS.close();
    console.log('PASS no-JavaScript fallback');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
