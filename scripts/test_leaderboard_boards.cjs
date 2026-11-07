/* Leaderboard page: separate VLA / WAM and coding-agent boards built from data/leaderboard-results.json.
   Uses the same Playwright environment as the other browser tests (CHROMIUM_EXECUTABLE, HERO_PREVIEW_URL). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
(async () => {
  const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/leaderboard-results.json'), 'utf8'));
  const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_EXECUTABLE || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--disable-dev-shm-usage'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    await page.route('**/*.mp4', r => r.abort());
    await page.goto(base + 'leaderboard.html', { waitUntil: 'load' });
    for (const track of data.tracks) {
      const models = data.models.filter(m => m.track === track.key);
      const rows = page.locator(`#board-${track.key} tbody tr`);
      assert.equal(await rows.count(), models.length, `${track.key}: one row per model`);
      const names = await rows.locator('.lb-model-name > span:last-child').allTextContents();
      assert.deepEqual(new Set(names.map(n => n.trim())), new Set(models.map(m => m.name)), `${track.key}: roster matches data`);
      const pending = models.filter(m => !m.results).length;
      assert.equal(await page.locator(`#board-${track.key} tr.lb-pending`).count(), pending);
      for (const rank of await page.locator(`#board-${track.key} tr.lb-pending .lb-rank`).allTextContents()) assert.equal(rank, '—', 'pending models are unranked');
      const ranked = await page.locator(`#board-${track.key} tr:not(.lb-pending) .lb-rank`).allTextContents();
      assert.deepEqual(ranked.map(Number), [...ranked.map(Number)].sort((a, b) => a - b), `${track.key}: ranked rows in order`);
    }
    assert.ok(data.models.filter(m => m.type === 'agent').every(m => m.track === 'agent'), 'agents only on the agent board');
    assert.match(await page.locator('#board-agent .lb-board-note').textContent(), /ranked\s+separately/);
    assert.equal(await page.locator('.lb-shot-model').count() > 0, true, 'hero places models on routes from the Earth to the Moon');
    assert.equal(await page.locator('.lb-shot-tag--moon').count(), 1, 'hero marks the Moon surface as the target');
    assert.equal(await page.locator('.lb-shot-model.is-lead').count(), 1, 'hero names one leader');
    await page.click('#board-e2e [data-setting="random"]');
    assert.equal(await page.getAttribute('#board-e2e [data-setting="random"]', 'aria-pressed'), 'true');
    for (const width of [320, 390, 820, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'no page overflow at ' + width);
    }
    assert.deepEqual(errors, []);
    console.log('PASS: two boards match the roster, pending models unranked, agent note shown, no overflow or page errors');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
