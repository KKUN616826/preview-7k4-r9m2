/* Optional browser regression: NODE_PATH=/path/to/node_modules node scripts/test_hero_browser.cjs
 * Start scripts/preview.py first. Playwright/Chromium are QA dependencies only.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { chromium } = require('playwright');
const data = require('../data/hero-demo.json');
const { presentationAt } = require('./hero-demo-data.js');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
const [mind, focus, coupling] = data.presentation.segments;
// Existing evidence boundaries use the original edit clock; translate once into
// the presentation clock so the same event assertions cover the new edit.
const displayedTime = time => time < 8
  ? Math.max(0, Math.min(mind.end - 0.00001, time - mind.legacyStart))
  : coupling.start + time - 8;

async function open(browser, width, height, motion = 'reduce', fallback = false) {
  const page = await browser.newPage({ viewport: { width, height }, reducedMotion: motion });
  page.errors = [];
  page.on('pageerror', error => page.errors.push(error.message));
  // Inspect after the player's callback, rather than before it in a competing
  // callback queue (which would incorrectly report a one-frame delay).
  await page.addInitScript(() => {
    const native = HTMLVideoElement.prototype.requestVideoFrameCallback;
    if (!native) return;
    HTMLVideoElement.prototype.requestVideoFrameCallback = function(callback) {
      const video = this;
      return native.call(video, (now, metadata) => {
        callback(now, metadata);
        if (video.id === 'hero-demo-video' && window.heroFrameAudit) {
          window.heroFrameAudit.push({ time: metadata.mediaTime, completed: document.querySelectorAll('.demo-card[data-completed="true"]').length });
        }
      });
    };
  });
  // Other task videos are unrelated to this player and expensive to decode together.
  await page.route('**/*.mp4', route => route.request().url().includes(data.presentation.path.split('/').at(-1)) ? route.continue() : route.abort());
  if (fallback) await page.addInitScript(() => {
    delete HTMLVideoElement.prototype.requestVideoFrameCallback;
    delete HTMLVideoElement.prototype.cancelVideoFrameCallback;
  });
  await page.goto(base, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    const video = document.querySelector('.demo-video');
    return video.readyState >= 2 && video.seekable.length && video.seekable.end(0) > 18.9 && !document.querySelector('.demo-play').disabled;
  });
  return page;
}

async function seekPresentation(page, time) {
  await page.evaluate(time => {
    const video = document.querySelector('.demo-video');
    video.pause();
    video.currentTime = time;
  }, time);
  await page.waitForFunction(() => !document.querySelector('.demo-video').seeking);
}

async function seek(page, time) { return seekPresentation(page, displayedTime(time)); }

async function inspect(page, time) {
  const actual = await page.evaluate(() => ({
    time: document.querySelector('.demo-video').currentTime,
    captured: [...document.querySelectorAll('.demo-card')].filter(card => !card.hidden).length,
    completed: document.querySelectorAll('.demo-card[data-completed="true"]').length,
    active: [...document.querySelectorAll('.demo-card')].findIndex(card => card.dataset.active === 'true'),
    dots: [...document.querySelectorAll('.demo-event-dot')].filter(dot => dot.style.display !== 'none').length,
    complete: document.querySelector('.demo-hero').dataset.complete === 'true',
    phase: document.querySelector('.demo-hero').dataset.phase,
    overflow: document.documentElement.scrollWidth > innerWidth,
    receipt: document.querySelector('.demo-feedback').textContent,
    step: document.querySelector('.demo-step').textContent,
    outcome: document.querySelector('.demo-outcome-link').dataset.active === 'true',
    outcomeStep: Number(document.querySelector('.demo-outcome-link').dataset.step),
    checks: [...document.querySelectorAll('.demo-card[data-completed="true"] .demo-card-status')].filter(e => getComputedStyle(e).display !== 'none' && e.textContent === '✓').length,
    pulse: getComputedStyle(document.querySelector('.demo-outcome-pulse')).display !== 'none',
    reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
    feedbackOnScreen: ['.demo-step', '.demo-feedback'].every(selector => {
      const box = document.querySelector(selector).getBoundingClientRect();
      return box.width > 0 && box.left >= 0 && box.right <= innerWidth;
    }),
    outcomeOriginError: (() => {
      const outcome = document.querySelector('.demo-outcome-link');
      if (outcome.dataset.active !== 'true') return null;
      const dot = document.querySelectorAll('.demo-event-dot')[Number(outcome.dataset.step) - 1];
      const event = new DOMPoint(Number(dot.getAttribute('cx')), Number(dot.getAttribute('cy'))).matrixTransform(dot.getScreenCTM());
      const path = document.querySelector('.demo-outcome-line');
      const start = path.getPointAtLength(0).matrixTransform(path.getScreenCTM());
      return Math.hypot(start.x - event.x, start.y - event.y);
    })(),
  }));
  assert.ok(Math.abs(actual.time - displayedTime(time)) < 0.000003, 'Shortened demonstration seek at ' + time);
  const expected = presentationAt(data, actual.time);
  const visible = expected.acting ? expected.captured : data.events.filter((event, index) => index >= 3 && index <= 7 && event.observe <= expected.time).length;
  assert.equal(actual.captured, visible);
  for (const key of ['completed', 'active', 'complete']) assert.equal(actual[key], expected[key], key + ' at ' + time);
  assert.equal(actual.dots, expected.completed);
  assert.equal(actual.phase, expected.phase);
  assert.equal(actual.overflow, false);
  if (expected.acting) assert.equal(actual.feedbackOnScreen, true, 'Feedback text must fit the visible viewport');
  assert.equal(actual.checks, expected.completed, 'Confirmed checks must be visible');
  assert.equal(actual.outcome, expected.completed > 0, 'Environment outcome returns to memory');
  if (expected.completed) {
    assert.equal(actual.outcomeStep, expected.completed);
    assert.ok(actual.outcomeOriginError < 1, 'Return arrow must start at the recorded trigger, not the moving cursor');
    assert.match(actual.receipt, /Registered/);
    assert.match(actual.receipt, new RegExp((12 - expected.completed) + ' remaining'));
    const age = expected.time - data.events[expected.completed - 1].trigger;
    assert.equal(actual.pulse, !actual.reduced && age < 0.45);
  }
  assert.equal(actual.step.includes('Waiting for release'), expected.registered);
}

(async () => {
  const options = { headless: true };
  if (process.env.CHROMIUM_EXECUTABLE) {
    options.executablePath = process.env.CHROMIUM_EXECUTABLE;
    options.args = ['--no-sandbox', '--disable-dev-shm-usage', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'];
  }
  const browser = await chromium.launch(options);
  try {
    for (const [name, width, height] of [['wide', 1920, 1080], ['desktop', 1440, 900], ['short', 1440, 768], ['wide-short', 1920, 700], ['tablet', 820, 1100], ['mobile', 390, 1100], ['narrow', 320, 900]]) {
      const page = await open(browser, width, height);
      assert.equal(await page.locator('.demo-video').evaluate(v => v.paused), true, 'Reduced motion disables autoplay');
      for (const time of [8, 12.08, 3, 18.8, 0, 7.5, 8.4]) {
        await seek(page, time); await inspect(page, time);
      }
      await seek(page, 12.08);
      const alignment = await page.evaluate(() => {
        const h = document.querySelector('.demo-hero').getBoundingClientRect();
        const chart = document.querySelector('.demo-chart');
        const s = chart.getBoundingClientRect();
        const t = document.querySelector('.demo-connection-target');
        const x = h.left + Number(t.getAttribute('cx')), y = h.top + Number(t.getAttribute('cy'));
        const card = document.querySelector('.demo-card[data-active="true"]').getBoundingClientRect();
        const windowBox = document.querySelector('.demo-memory-window').getBoundingClientRect();
        const arm = JSON.parse(document.getElementById('heroDemoData').textContent).events[Number(document.querySelector('.demo-card[data-active="true"]').dataset.step) - 1].arm;
        const head = document.querySelector(arm === 'Left' ? '.demo-chart-head.demo-trace-left' : '.demo-chart-head.demo-trace-right');
        const point = new DOMPoint(Number(head.getAttribute('cx')), Number(head.getAttribute('cy'))).matrixTransform(chart.getScreenCTM());
        return { targetInChart: x >= s.left && x <= s.right && y >= s.top && y <= s.bottom,
          targetError: Math.hypot(x - point.x, y - point.y),
          cardVisible: card.left >= windowBox.left - 1 && card.right <= windowBox.right + 1 };
      });
      assert.equal(alignment.targetInChart, true); assert.equal(alignment.cardVisible, true);
      assert.ok(alignment.targetError < 1, 'Target arrow must track the executing arm');
      await seek(page, data.events[2].trigger + 0.05); await inspect(page, data.events[2].trigger + 0.05);
      if (process.env.HERO_SCREENSHOTS) {
        fs.mkdirSync(process.env.HERO_SCREENSHOTS, { recursive: true });
        await page.screenshot({ path: path.join(process.env.HERO_SCREENSHOTS, name + '-act.png') });
        await seek(page, 3);
        await page.screenshot({ path: path.join(process.env.HERO_SCREENSHOTS, name + '-mind.png') });
      }
      for (const local of [0, data.actDetail.trigger - 0.0001, data.actDetail.trigger + 0.0001, data.actDetail.release + 0.0001, 1]) {
        await page.evaluate(time => { const v = document.querySelector('.demo-video'); v.pause(); v.currentTime = time; }, focus.start + local);
        await page.waitForFunction(() => !document.querySelector('.demo-video').seeking);
        assert.equal(await page.locator('.demo-hero').getAttribute('data-phase'), 'focus');
        assert.equal(await page.locator('.demo-workspace').isVisible(), false);
        assert.equal(await page.locator('.demo-act-workspace').isVisible(), true);
        const contact = await page.evaluate(() => {
          const key = document.querySelector('.demo-act-target').getBoundingClientRect();
          const title = document.querySelector('.demo-copy').getBoundingClientRect();
          const scene = document.querySelector('.demo-scene').getBoundingClientRect();
          return {visible: key.left >= scene.left && key.right <= scene.right && key.top >= scene.top && key.bottom <= scene.bottom,
            clear: key.bottom <= title.top || key.top >= title.bottom || key.right <= title.left || key.left >= title.right};
        });
        assert.equal(contact.visible, true, 'Contact outline must stay in the video');
        assert.equal(contact.clear, true, 'Title must not cover the contact outline');
        assert.equal(await page.locator('.demo-act-spotlight').isVisible(), true);
        const mappingError = await page.evaluate(target => {
          const svg = document.querySelector('.demo-act-spotlight');
          const point = new DOMPoint(...target).matrixTransform(svg.getScreenCTM());
          const outline = document.querySelector('.demo-act-target').getBoundingClientRect();
          return Math.hypot(point.x - (outline.left + outline.width / 2), point.y - (outline.top + outline.height / 2));
        }, data.events[0].target);
        assert.ok(mappingError < 1, 'Highlight must map directly from the original frame');
        assert.equal(await page.locator('.demo-card[data-completed="true"]').count(), 0);
        assert.equal(await page.locator('.demo-act-event').isVisible(), local >= data.actDetail.trigger);
        const row = data.actDetail.samples[Math.round(local * data.actDetail.sampleHz)];
        assert.equal(await page.locator('.demo-joints dd').first().textContent(), row[3].toFixed(1) + ' / ' + row[9].toFixed(1));
        assert.ok(Math.abs(Number(await page.locator('#act-reveal rect').getAttribute('width')) - local / 4.5 * 426) < 0.001);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      }
      if (process.env.HERO_SCREENSHOTS) await page.screenshot({ path: path.join(process.env.HERO_SCREENSHOTS, name + '-focus.png') });
      const geometry = () => page.locator('.demo-scene').evaluate(scene => {
        const r = scene.getBoundingClientRect(), root = scene.closest('.demo-hero').getBoundingClientRect(), video = getComputedStyle(scene.querySelector('video'));
        return [r.x - root.x, r.y - root.y, r.width, r.height, video.objectFit, video.objectPosition];
      });
      const actGeometry = await geometry();
      if (width <= 760) assert.ok(Math.abs(actGeometry[2] / actGeometry[3] - 16 / 9) < 0.001);
      await page.locator('[data-demo-phase="reproduce"]').click();
      await page.waitForFunction(() => !document.querySelector('.demo-video').seeking);
      await inspect(page, 8);
      assert.deepEqual(await geometry(), actGeometry, 'Act and Mind2Act must use identical camera geometry');
      assert.equal(await page.locator('.demo-act-spotlight').isVisible(), false);
      await seekPresentation(page, coupling.start + 0.1);
      assert.equal(await page.locator('.demo-scene').evaluate(e => getComputedStyle(e).opacity), '1', 'Reduced motion removes the dip');
      assert.deepEqual(page.errors, []);
      await page.close();
      console.log('PASS: responsive layout, seeks and target mapping:', name);
    }
    const page = await open(browser, 1440, 1000);
    for (const event of data.events) {
      for (const time of [event.observe - 0.0001, event.observe + 0.0001, event.trigger - 0.0001, event.trigger + 0.0001, event.release - 0.0001, event.release + 0.0001]) {
        await seek(page, time); await inspect(page, time);
      }
    }
    await seek(page, 8); await inspect(page, 8);
    await page.locator('.demo-play').focus(); await page.keyboard.press('Space');
    await page.waitForFunction(() => !document.querySelector('.demo-video').paused);
    await page.keyboard.press('Space');
    await page.waitForFunction(() => document.querySelector('.demo-video').paused);
    await seek(page, data.media.duration - 0.05); await inspect(page, data.media.duration - 0.05);
    await seek(page, 0); await inspect(page, 0);
    for (let i = 0; i < 2; i++) {
      await seek(page, data.media.duration - 0.1);
      await page.getByRole('button', { name: 'Play demo', exact: true }).click();
      await page.waitForFunction(start => document.querySelector('.demo-video').currentTime >= start && document.querySelector('.demo-video').currentTime < start + 0.5 && document.querySelectorAll('.demo-card[data-completed="true"]').length === 0, 0);
      assert.equal(await page.locator('.demo-card[data-completed="true"]').count(), 0);
      await page.getByRole('button', { name: 'Pause demo', exact: true }).click();
    }
    await seek(page, 8.9);
    await page.evaluate(() => { window.heroFrameAudit = []; });
    await page.getByRole('button', { name: 'Play demo', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.demo-video').currentTime > 9.3);
    await page.getByRole('button', { name: 'Pause demo', exact: true }).click();
    const frames = await page.evaluate(() => window.heroFrameAudit);
    const confirmed = frames.find(frame => frame.completed === 1);
    assert.ok(confirmed && confirmed.time >= displayedTime(data.events[0].trigger) - 1e-6);
    assert.ok(confirmed.time - displayedTime(data.events[0].trigger) <= 1 / 30 + 1e-6, JSON.stringify(frames));
    const pausedTime = await page.locator('.demo-video').evaluate(v => v.currentTime);
    await page.waitForTimeout(200);
    assert.equal(await page.locator('.demo-video').evaluate(v => v.currentTime), pausedTime);
    await page.getByRole('button', { name: 'Play demo', exact: true }).click();
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForFunction(() => document.querySelector('.demo-video').paused);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForFunction(() => !document.querySelector('.demo-video').paused);
    for (const hidden of [true, false]) {
      await page.evaluate(hidden => {
        Object.defineProperty(document, 'hidden', { configurable: true, value: hidden });
        document.dispatchEvent(new Event('visibilitychange'));
      }, hidden);
      await page.waitForFunction(hidden => document.querySelector('.demo-video').paused === hidden, hidden);
    }
    await page.getByRole('button', { name: 'Pause demo', exact: true }).click();
    await page.evaluate(() => { document.querySelector('.demo-video').dispatchEvent(new Event('error')); });
    assert.equal(await page.locator('.demo-play').isDisabled(), true);
    assert.equal(await page.locator('.demo-title').textContent(), 'Demo unavailable.');
    assert.deepEqual(page.errors, []);
    await page.close();
    console.log('PASS: all event boundaries, keyboard controls, loops, frame synchronization, pause/visibility and error handling');
    const fallback = await open(browser, 1280, 900, 'no-preference', true);
    await fallback.waitForFunction(start => document.querySelector('.demo-video').currentTime > start + 0.2, 0);
    for (const offset of [0.05, 0.2, 0.449, 0.451]) {
      await seek(fallback, data.events[0].trigger + offset); await inspect(fallback, data.events[0].trigger + offset);
    }
    await seek(fallback, data.events[0].trigger + 0.05);
    const pulsePosition = () => fallback.locator('.demo-outcome-pulse').evaluate(e => [e.getAttribute('cx'), e.getAttribute('cy')]);
    const frozen = await pulsePosition();
    await fallback.waitForTimeout(150);
    assert.deepEqual(await pulsePosition(), frozen, 'Paused media freezes the feedback pulse');
    await seek(fallback, 16.5); await inspect(fallback, 16.5);
    for (const boundary of data.presentation.transition.boundaries) {
      for (const offset of [-0.3, -0.2, -0.1, -0.01, 0, 0.01, 0.1, 0.2, 0.3, -0.1]) {
        await seekPresentation(fallback, boundary + offset);
        const actual = await fallback.evaluate(() => ({
          time: document.querySelector('.demo-video').currentTime,
          opacity: Number(getComputedStyle(document.querySelector('.demo-scene')).opacity),
          information: Number(getComputedStyle(document.querySelector('.demo-copy')).opacity),
          brand: getComputedStyle(document.querySelector('.demo-moon-panel')).opacity,
          controls: getComputedStyle(document.querySelector('.demo-controls')).opacity,
          completed: document.querySelectorAll('.demo-card[data-completed="true"]').length,
        }));
        assert.equal(actual.opacity, 1, 'The background stays visible at every edit boundary');
        assert.equal(actual.information, 1, 'Evidence stays visible through the cut');
        assert.equal(actual.brand, '1'); assert.equal(actual.controls, '1'); assert.equal(actual.completed, 0);
      }
      const pausedDip = await fallback.locator('.demo-scene').evaluate(e => getComputedStyle(e).opacity);
      await fallback.waitForTimeout(160);
      assert.equal(await fallback.locator('.demo-scene').evaluate(e => getComputedStyle(e).opacity), pausedDip);
      await fallback.getByRole('button', { name: 'Play demo', exact: true }).click();
      await fallback.waitForFunction(end => document.querySelector('.demo-video').currentTime > end, boundary + 0.3);
      await fallback.getByRole('button', { name: 'Pause demo', exact: true }).click();
      assert.equal(await fallback.locator('.demo-scene').evaluate(e => getComputedStyle(e).opacity), '1');
      await seekPresentation(fallback, boundary - 0.1);
      await fallback.emulateMedia({reducedMotion: 'reduce'});
      await fallback.waitForFunction(() => getComputedStyle(document.querySelector('.demo-scene')).opacity === '1');
      await fallback.emulateMedia({reducedMotion: 'no-preference'});
      await fallback.waitForFunction(() => getComputedStyle(document.querySelector('.demo-scene')).opacity === '1');
      await seekPresentation(fallback, 0);
      assert.equal(await fallback.locator('.demo-scene').evaluate(e => getComputedStyle(e).opacity), '1');
    }
    console.log('PASS: visible edit boundaries, paused and reverse seeks, resume, loop reset and live reduced-motion changes');
    assert.deepEqual(fallback.errors, []); await fallback.close();
    console.log('PASS: muted autoplay and requestAnimationFrame fallback');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
