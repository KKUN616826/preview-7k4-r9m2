/* Homepage leaderboard preview: one column per board, linking to the full leaderboard. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
(async () => {
  const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/leaderboard-results.json'), 'utf8'));
  const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_EXECUTABLE || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--disable-dev-shm-usage'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    await page.route('**/*.mp4', r => r.abort());
    await page.goto(base, { waitUntil: 'load' });
    const preview = page.locator('#top-ten.home-leaderboard');
    await preview.scrollIntoViewIfNeeded();
    assert.equal(await preview.locator('.hl-col').count(), data.tracks.length, 'one column per board');
    for (const [i, track] of data.tracks.entries()) {
      const models = data.models.filter(m => m.track === track.key);
      const reported = models.filter(m => m.results);
      const expected = reported.length ? Math.min(5, reported.length) : models.filter(m => m.release === data.first_release).length;
      assert.equal(await preview.locator('.hl-col').nth(i).locator('.hl-list li').count(), expected, `${track.key}: rows`);
    }
    for (const width of [320, 390, 700, 1024, 1920]) {
      await page.setViewportSize({ width, height: 900 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'overflow at ' + width);
      assert.equal(await preview.locator('a[href="leaderboard.html"]').isVisible(), true);
    }
    await preview.locator('a[href="leaderboard.html"]').click();
    await page.waitForURL('**/leaderboard.html');
    assert.equal(await page.locator('.lb-board').count(), data.tracks.length);
    assert.deepEqual(errors, []);
    console.log('PASS: homepage preview has one column per board, fits all widths and opens the leaderboard');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
