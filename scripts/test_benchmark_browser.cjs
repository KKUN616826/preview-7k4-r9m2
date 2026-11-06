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
    assert.equal(await page.locator('.bo-suite:visible').count(), 1);
    assert.equal(await page.locator('.bo-chapter:visible').count(), suites[0].cases.length);
    assert.equal(await page.locator('.bo-index, .bo-mobile-index, .bo-family-head, .bo-task-id > span').count(), 0);
    assert.equal(await page.locator('.bo-suite-tabs [data-suite]').count(), 3);
    assert.equal(await page.locator('.bo-suite-tabs').evaluate(el => getComputedStyle(el).position), 'static');
    await page.locator('#tab-mind2act').click();
    await page.locator('#task-CP01 select').selectOption('medium');
    assert.match(await page.locator('#task-CP01 .bo-task-poster').getAttribute('src'), /CP01-medium.jpg$/);
    assert.match(await page.locator('#task-CP01 .bo-task-link').getAttribute('href'), /CP01.html#medium$/);
    assert.ok(page.url().endsWith('/benchmark.html#suite-mind2act'));
    assert.equal(await page.getByText('View task', {exact:true}).count(), 0);
    await page.locator('#tab-mind').click();
    assert.equal(await page.locator('#task-E2 option[value=hard]').isDisabled(), false);
    await page.locator('#tab-mind').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#tab-act').getAttribute('aria-pressed'), 'true');
    assert.equal(await page.locator('#tab-act').evaluate(el => el === document.activeElement), true);
    assert.equal(await page.locator('#suite-act').isVisible(), true);
    assert.equal(await page.locator('.bo-chapter:visible').count(), suites[1].cases.length);
    await page.keyboard.press('End');
    assert.equal(await page.locator('#tab-mind2act').getAttribute('aria-pressed'), 'true');
    assert.equal(await page.locator('#tab-mind2act').evaluate(el => el === document.activeElement), true);
    await page.goBack();
    assert.equal(await page.locator('#suite-act').isVisible(), true);
    await page.goForward();
    assert.equal(await page.locator('#suite-mind2act').isVisible(), true);
    // Search covers all suites, even while a different suite was selected.
    await page.locator('#benchmark-search').fill('E2');
    assert.equal(await page.locator('#task-E2').isVisible(), true);
    assert.equal(await page.locator('#task-CP05').isVisible(), false);
    assert.equal(await page.locator('.bo-suite-tabs [aria-pressed=true]').count(), 0);
    await page.locator('.bo-search-clear').click();
    assert.equal(await page.locator('#suite-mind2act').isVisible(), true);
    assert.equal(await page.locator('.bo-chapter:visible').count(), suites[2].cases.length);
    await page.locator('#benchmark-search').fill('not-a-real-task-xyz');
    assert.equal(await page.locator('.bo-chapter:visible').count(), 0);
    assert.equal(await page.locator('.bo-search-empty').isVisible(), true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.bo-chapter:visible').count(), suites[2].cases.length);
    await page.goto(new URL('benchmark.html#task-CP05', base).href);
    assert.equal(await page.locator('#tab-mind2act').getAttribute('aria-pressed'), 'true');
    assert.equal(await page.locator('#task-CP05').isVisible(), true);
    await page.locator('#task-CP05 select').selectOption('medium');
    // Clicking task copy follows the full-card link with the selected difficulty.
    await page.locator('#task-CP05 .bo-task-link').click({position:{x:270,y:75}});
    assert.ok(page.url().endsWith('/tasks/CP05.html#medium'));
    assert.equal(await page.locator('[data-panel="medium"]').isVisible(), true);
    await page.goBack();
    assert.equal(await page.locator('#task-CP05 select').inputValue(), 'medium');
    // The preview area is the same native link, including keyboard and new-tab behavior.
    await page.locator('#task-CP05 .bo-task-link').click({position:{x:80,y:65}});
    assert.ok(page.url().endsWith('/tasks/CP05.html#medium'));
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
    assert.equal(await page.locator('.workspace-sidebar a[aria-current=page] .workspace-case-id').textContent(), suites[0].cases[0].code || suites[0].cases[0].id);
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
      if (relative === 'benchmark.html') assert.equal(await page.locator('.bo-suite:visible').count(), 1);
      else assert.equal(await page.locator('.workspace-sidebar a[aria-current=page]').count(), 1, relative);
      const assets = await page.locator('link[rel=stylesheet],img,video source').evaluateAll(elements =>
        elements.map(el => el.href || el.src).filter(url => url.startsWith(location.origin)));
      for (const asset of new Set(assets)) {
        const result = await page.request.head(asset);
        assert.equal(result.status(), 200, asset);
      }
    }
    console.log('PASS: overview, suites, all catalog tasks, links, assets, hover and history');

    for (const width of [320, 390, 820, 855, 1024, 1440, 1920, 2560]) {
      await page.setViewportSize({ width, height: 1000 });
      for (const relative of ['benchmark.html', 'benchmark/mind.html', 'tasks/E.html#medium']) {
        await page.goto(new URL(relative, base).href);
        await page.evaluate(() => document.fonts.ready);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${relative} ${width}`);
        if (relative === 'benchmark.html') {
          const bounds = await page.locator('.bo-explorer').boundingBox();
          assert.ok(bounds.width <= 1001, `task canvas max width ${width}`);
          assert.ok(bounds.x >= (width < 768 ? 20 : 40), `task canvas side margins ${width}`);
          assert.equal(await page.locator('.bo-chapter:visible').count(), suites[0].cases.length);
        }
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
