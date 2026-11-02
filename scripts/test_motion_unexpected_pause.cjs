const assert = require('node:assert/strict');
const { chromium } = require('playwright');
(async () => {
 const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try {
  const page = await browser.newPage({reducedMotion:'no-preference'});
  await page.goto('http://127.0.0.1:8765/leaderboard.html');
  await page.waitForFunction(() => document.querySelector('.lb-stage').dataset.motionReady === 'true');
  // Simulate a media-engine interruption without a user pressing our pause control.
  await page.locator('.lb-stage-motion-video').evaluate(v => v.pause());
  await page.waitForFunction(() => !document.querySelector('.lb-stage-motion-video').paused, {}, {timeout:4000});
  const time = await page.locator('video').evaluate(v => v.currentTime);
  await page.waitForTimeout(350);
  assert.notEqual(await page.locator('video').evaluate(v => v.currentTime), time);
  await page.locator('.lb-stage-motion-toggle').click();
  await page.waitForTimeout(1200);
  assert.equal(await page.locator('video').evaluate(v => v.paused), true, 'manual pause must remain paused');
  console.log('PASS unexpected media pause recovers; manual pause is preserved');
 } finally { await browser.close(); }
})().catch(e => { console.error(e.message); process.exit(1); });
