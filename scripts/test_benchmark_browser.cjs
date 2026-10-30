/* Uses the same optional Playwright installation as the existing browser checks. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const suites = require('../data/benchmark-navigation.json');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
const output = process.env.BENCHMARK_SCREENSHOTS;
const taskCount=suites.reduce((n,s)=>n+s.cases.length,0);

(async () => {
  const browser = await chromium.launch({ headless: true,
    ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(new URL('benchmark.html', base).href);
    await page.evaluate(() => document.fonts.ready);
    assert.equal(await page.locator('.bo-chapter').count(), taskCount);
    assert.equal(await page.locator('.bo-suite:not([hidden])').getAttribute('id'), 'suite-mind2act');
    await page.locator('#task-CP01 select').selectOption('medium');
    assert.match(await page.locator('#video-CP01').getAttribute('src'), /CP01\/medium.mp4$/);
    assert.match(await page.locator('#task-CP01 .bo-task-detail').getAttribute('href'), /#medium$/);
    await page.locator('#tab-mind').click();
    assert.equal(await page.locator('#task-E2 option[value=hard]').isDisabled(), true);
    await page.locator('#tab-mind').press('ArrowRight');
    assert.equal(await page.locator('#tab-act').getAttribute('aria-selected'), 'true');
    await page.locator('.bo-index [data-index-task=CP05]').click();
    assert.equal(await page.locator('.bo-index [data-index-task=CP05]').getAttribute('aria-current'), 'location');
    await page.locator('#task-CP05 select').selectOption('medium');
    await page.locator('#task-CP05 [data-expand]').click();
    await page.locator('.bo-video-dialog').waitFor({state:'visible'});
    assert.match(await page.locator('.bo-expanded-video').getAttribute('src'), /CP05\/medium.mp4$/);
    await page.getByRole('button', {name:'Close expanded video'}).press('Escape');
    await page.locator('.bo-video-dialog').waitFor({state:'hidden'});
    assert.equal(await page.locator('#task-CP05 [data-expand]').evaluate(el=>el===document.activeElement), true);
    await page.goto(new URL('benchmark/mind.html', base).href);

    // Collapsing a group must not navigate. Clicking its name must navigate.
    const toggle = page.locator('.workspace-sidebar [data-group="act"] button');
    await toggle.click();
    assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
    assert.ok(page.url().endsWith('/benchmark/mind.html'));
    await page.locator('.workspace-sidebar .workspace-group-row a[href="../benchmark/mind.html"]').click();
    assert.ok(page.url().endsWith('/benchmark/mind.html'));
    assert.equal(await page.locator('.benchmark-task-row').count(), suites[0].cases.length);
    assert.equal(await page.locator('.workspace-sidebar [data-group="act"] button').getAttribute('aria-expanded'), 'false');

    // Row copy is visible before hover; only the image and arrow move, never the row.
    const card = page.locator('.benchmark-task-row').first();
    assert.equal(await card.locator('.benchmark-task-summary').isVisible(), true);
    await card.locator('a').hover();
    await page.waitForFunction(() => getComputedStyle(document.querySelector('.benchmark-task-image img')).transform !== 'none');
    assert.equal(await card.evaluate(el => getComputedStyle(el).transform), 'none');
    assert.notEqual(await card.locator('img').evaluate(el => getComputedStyle(el).transform), 'none');

    await card.locator('a').click();
    assert.ok(page.url().endsWith('/tasks/E.html#easy'));
    assert.equal(await page.locator('.workspace-sidebar a[aria-current=page] .workspace-case-id').textContent(), 'E');
    await page.locator('[data-level="hard"]').click();
    await page.locator('[data-panel="hard"]').waitFor({ state: 'visible' });
    await page.reload();
    assert.equal(await page.locator('[data-level="hard"]').getAttribute('aria-current'), 'true');
    await page.goBack();
    assert.ok(page.url().endsWith('#easy'));
    await page.goBack();
    assert.ok(page.url().endsWith('/benchmark/mind.html'));

    // Every generated page has a unique active item and working relative assets/links.
    const paths = ['benchmark.html', ...suites.flatMap(suite => [
      `benchmark/${suite.slug}.html`, ...suite.cases.map(c => `tasks/${c.id}.html`)])];
    for (const relative of paths) {
      const response = await page.goto(new URL(relative, base).href);
      assert.equal(response.status(), 200, relative);
      assert.equal(await page.locator(relative === 'benchmark.html' ? '.bo-suite-tabs [aria-selected=true]' : '.workspace-sidebar a[aria-current=page]').count(), 1, relative);
      const assets = await page.locator('link[rel=stylesheet],img,video source').evaluateAll(elements =>
        elements.map(el => el.href || el.src).filter(url => url.startsWith(location.origin)));
      for (const asset of new Set(assets)) {
        const result = await page.request.head(asset);
        assert.equal(result.status(), 200, asset);
      }
    }
    console.log('PASS: overview, suites, all catalog tasks, links, assets, hover and history');

    for (const width of [320, 390, 820, 1024, 1440, 1920, 2560]) {
      await page.setViewportSize({ width, height: 1000 });
      for (const relative of ['benchmark.html', 'benchmark/mind.html', 'tasks/E.html#medium']) {
        await page.goto(new URL(relative, base).href);
        await page.evaluate(() => document.fonts.ready);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${relative} ${width}`);
        if (relative === 'benchmark/mind.html') {
          const layout = await page.evaluate(() => {
            const rows = [...document.querySelectorAll('.benchmark-task-row')].map(el => el.getBoundingClientRect());
            const sidebar = document.querySelector('.workspace-sidebar').getBoundingClientRect();
            return { right: innerWidth, left: innerWidth > 850 ? sidebar.right : 0,
              rows: rows.map(r => ({left:r.left, right:r.right, top:r.top, bottom:r.bottom})) };
          });
          layout.rows.forEach((row, i) => {
            assert.ok(Math.abs(row.right-layout.right)<1, `right edge ${width}`);
            assert.ok(Math.abs(row.left-layout.left)<1, `left edge ${width}`);
            if (i) assert.ok(Math.abs(row.top-layout.rows[i-1].bottom)<1, `continuous rows ${width}`);
          });
        }
        if (output && [390, 1440].includes(width)) {
          fs.mkdirSync(output, { recursive: true });
          await page.screenshot({ path: path.join(output, `${relative.split('/').pop().split('.')[0]}-${width}.png`), fullPage: true });
        }
      }
      console.log('PASS: responsive pages', width);
    }

    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(new URL('tasks/E.html#medium', base).href);
    await page.getByRole('button', { name: 'Browse tasks', exact: true }).click();
    const dialog = page.locator('#task-drawer');
    assert.equal(await dialog.isVisible(), true);
    assert.equal(await dialog.locator('a[aria-current=page]').evaluate(el => el === document.activeElement), true);
    await page.keyboard.press('Escape');
    assert.equal(await dialog.isVisible(), false);
    assert.equal(await page.locator('#browse-tasks').evaluate(el => el === document.activeElement), true);
    await page.locator('#browse-tasks').click();
    await dialog.locator('a[href="../tasks/CP05.html"]').click();
    assert.ok(page.url().endsWith('/tasks/CP05.html'));
    assert.equal(await page.locator('[data-panel="easy"]').isVisible(), true);
    await page.locator('#browse-tasks').click();
    await page.setViewportSize({ width: 1440, height: 1000 });
    await dialog.waitFor({ state: 'hidden' });
    assert.equal(await page.evaluate(() => document.documentElement.style.overflow), '');
    assert.deepEqual(errors, []);
    console.log('PASS: mobile drawer, current focus, Escape, case navigation and resize');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
