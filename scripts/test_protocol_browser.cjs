const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
const sections = ['tracks', 'episodes', 'clock', 'metrics', 'diagnostics', 'disclosure', 'submit'];
(async () => {
  const browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_EXECUTABLE ? {executablePath: process.env.CHROMIUM_EXECUTABLE} : {})});
  try {
    for (const width of [320, 390, 820, 1040, 1100, 1440, 1920]) {
      const page = await browser.newPage({viewport: {width, height: 1000}, reducedMotion: 'reduce'});
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('response', r => { if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`); });
      await page.goto(new URL('protocol.html', base).href);
      await page.evaluate(() => document.fonts.ready);
      assert.equal(await page.locator('.pr-toc a').count(), 7);
      assert.equal(await page.locator('.pr-head h1').textContent(), 'How Mind2Act World evaluates a system');
      assert.equal(await page.locator('.pr-head h1').evaluate(el => getComputedStyle(el).fontFamily), await page.locator('body').evaluate(el => getComputedStyle(el).fontFamily), 'Protocol shares the site typography');
      await page.locator('.pr-hero-artwork').evaluate(el => el.decode());
      assert.ok(await page.locator('.pr-hero-artwork').evaluate(el => el.naturalWidth === 1300 && el.naturalWidth >= el.getBoundingClientRect().width), 'Artwork uses a standalone source without enlarging a screenshot crop');
      assert.deepEqual(await page.locator('.pr-scene-labels strong').allTextContents(), ['Target', 'Execution', 'Environment check']);
      assert.equal(await page.locator('.pr-scene-arrows').count(), 1);
      const dataY = await page.locator('.pr-facts dd').evaluateAll(els => els.map(el => Math.round(el.getBoundingClientRect().top)));
      assert.equal(new Set(dataY).size, 2, `${width}: four data values use the reference's two rows`);
      assert.equal(dataY[0], dataY[1]);
      assert.equal(dataY[2], dataY[3]);
      if (width > 1040) {
        const heading = await page.locator('h1').evaluate(el => ({height: el.getBoundingClientRect().height, line: parseFloat(getComputedStyle(el).lineHeight)}));
        assert.ok(Math.abs(heading.height - heading.line * 2) < 2, `${width}: exactly two heading lines`);
        assert.ok(await page.locator('.pr-hero-visual').evaluate(el => el.getBoundingClientRect().left >= innerWidth * .43), `${width}: reference illustration occupies the right half`);
      }
      assert.equal(await page.locator('#siteNav a[aria-current="page"]').textContent(), 'Protocol');
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${width}: no horizontal overflow`);
      assert.ok(await page.locator('.pr-hero').evaluate(el => el.getBoundingClientRect().bottom >= innerHeight - 1), `${width}: overview fills the first screen`);
      assert.ok(await page.locator('.pr-layout').evaluate(el => el.getBoundingClientRect().top >= innerHeight), `${width}: article begins after the first screen`);
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
      if (process.env.PROTOCOL_SCREENSHOTS && [390, 1440, 1920].includes(width)) {
        fs.mkdirSync(process.env.PROTOCOL_SCREENSHOTS, {recursive: true});
        await page.screenshot({path: path.join(process.env.PROTOCOL_SCREENSHOTS, `protocol-${width}.png`), fullPage: true});
        await page.screenshot({path: path.join(process.env.PROTOCOL_SCREENSHOTS, `hero-${width}.png`)});
      }
      await page.close();
    }
    for (const [width, height] of [[1280, 720], [1440, 900], [1920, 1080], [390, 844]]) {
      const page = await browser.newPage({viewport: {width, height}, reducedMotion: 'reduce'});
      await page.goto(new URL('protocol.html', base).href);
      await page.evaluate(() => document.fonts.ready);
      const bottom = await page.locator('.pr-hero').evaluate(el => el.getBoundingClientRect().bottom);
      assert.ok(bottom >= height - 1 && (width <= 1040 || Math.abs(bottom - height) < 2), `${width}×${height}: overview fills the first screen without clipping mobile content`);
      assert.equal(await page.locator('.pr-hero-links').count(), 0, 'Hero quick links are removed');
      if (process.env.PROTOCOL_SCREENSHOTS) await page.screenshot({path: path.join(process.env.PROTOCOL_SCREENSHOTS, `clock-link-${width}-${height}.png`)});
      await page.close();
    }
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
    await page.goto(new URL('leaderboard.html#protocol', base).href);
    await page.locator('.lb-protocol-link').click();
    assert.equal(new URL(page.url()).pathname, '/protocol.html');
    await page.locator('#disclosure a').click();
    assert.equal(new URL(page.url()).pathname + new URL(page.url()).hash, '/leaderboard.html#protocol');
    console.log('Protocol: seven viewport sizes, all sections, scroll state, mobile menu and leaderboard round trip passed.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
