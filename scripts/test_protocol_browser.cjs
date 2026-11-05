const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
const sections = ['tracks', 'episodes', 'clock', 'metrics', 'diagnostics', 'disclosure', 'submit'];
(async () => {
  const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_EXECUTABLE ? {executablePath: process.env.CHROMIUM_EXECUTABLE} : {})});
  try {
    for (const width of [320, 390, 820, 1040, 1100, 1440]) {
      const page = await browser.newPage({viewport: {width, height: 1000}, reducedMotion: 'reduce'});
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('response', r => { if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`); });
      await page.goto(new URL('protocol.html', base).href);
      await page.evaluate(() => document.fonts.ready);
      assert.equal(await page.locator('.pr-toc a').count(), 7);
      assert.equal(await page.locator('#siteNav a[aria-current="page"]').textContent(), 'Protocol');
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${width}: no horizontal overflow`);
      for (const id of sections) {
        await page.locator(`.pr-toc a[href="#${id}"]`).click();
        await page.waitForFunction(id => document.querySelector(`.pr-toc a[href="#${id}"]`).getAttribute('aria-current') === 'true', id);
        const top = await page.locator(`#${id}`).evaluate(el => el.getBoundingClientRect().top);
        const atEnd = await page.evaluate(() => innerHeight + scrollY >= document.documentElement.scrollHeight - 4);
        assert.ok(top >= 68 && (top < 160 || (id === 'submit' && atEnd && top < 1000)), `${width}: ${id} clears sticky header (${top})`);
      }
      await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
      await page.waitForFunction(() => document.querySelector('.pr-toc a[href="#submit"]').getAttribute('aria-current') === 'true');
      await page.evaluate(() => scrollTo(0, 0));
      await page.waitForFunction(() => document.querySelector('.pr-toc a[href="#tracks"]').getAttribute('aria-current') === 'true');
      if (width <= 1040) {
        const button = page.locator('#menuToggle');
        await button.click();
        assert.equal(await button.getAttribute('aria-expanded'), 'true');
        await page.keyboard.press('Escape');
        assert.equal(await button.getAttribute('aria-expanded'), 'false');
        await button.click();
        await page.locator('#siteNav a[href="protocol.html"]').click();
        assert.equal(await button.getAttribute('aria-expanded'), 'false');
      }
      const issue = page.locator('.pr-cta-actions a').first();
      assert.equal(await issue.getAttribute('href'), 'https://github.com/KKUN616826/preview-7k4-r9m2/issues');
      assert.deepEqual(errors, [], `${width}: no script or resource errors`);
      if (process.env.PROTOCOL_SCREENSHOTS && [390, 1440].includes(width)) {
        fs.mkdirSync(process.env.PROTOCOL_SCREENSHOTS, {recursive: true});
        await page.screenshot({path: path.join(process.env.PROTOCOL_SCREENSHOTS, `protocol-${width}.png`), fullPage: true});
      }
      await page.close();
    }
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
    await page.goto(new URL('leaderboard.html#protocol', base).href);
    await page.locator('.lb-protocol-link').click();
    assert.equal(new URL(page.url()).pathname, '/protocol.html');
    await page.locator('#disclosure a').click();
    assert.equal(new URL(page.url()).pathname + new URL(page.url()).hash, '/leaderboard.html#protocol');
    console.log('Protocol: six viewport sizes, all sections, scroll state, mobile menu and leaderboard round trip passed.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
