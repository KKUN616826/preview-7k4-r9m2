/* Cross-document navigation must keep the same shared capsule geometry. */
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';

function measure() {
  const header = document.querySelector('header.header');
  if (!header) return null;
  const elements = [header, header.querySelector('.header-inner'), header.querySelector('.official-nav-logo')];
  if (innerWidth > 1040) elements.push(...header.querySelectorAll('#siteNav a'));
  else elements.push(header.querySelector('#menuToggle'));
  return elements.map(element => {
    const {x, y, width, height} = element.getBoundingClientRect();
    return {x, y, width, height};
  });
}

function sameGeometry(actual, expected, label) {
  assert.equal(actual.length, expected.length, label);
  actual.forEach((rect, index) => {
    for (const key of ['x', 'y', 'width', 'height']) {
      assert.ok(Math.abs(rect[key] - expected[index][key]) < .5,
        `${label}: element ${index} ${key} changed from ${expected[index][key]} to ${rect[key]}`);
    }
  });
}

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE});
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(`
      window.__siteNavFrames = [];
      const measure = ${measure.toString()};
      function frame() {
        const geometry = measure();
        if (geometry) window.__siteNavFrames.push(geometry);
        if (window.__siteNavFrames.length < 45) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    `);
    for (const width of [1440, 390, 1920]) {
      await page.setViewportSize({width, height: 900});
      for (const route of ['protocol.html', 'leaderboard.html', 'benchmark.html', 'resources.html', 'benchmark/mind.html', 'tasks/E.html']) {
        await page.goto(new URL(route, base).href);
        await page.evaluate(() => document.fonts.ready);
        const source = await page.evaluate(measure);
        if (width <= 1040) await page.locator('#menuToggle').click();
        await page.locator('#siteNav').getByRole('link', {name: 'Home', exact: true}).click();
        await page.waitForURL(new URL('index.html', base).href);
        await page.evaluate(() => document.fonts.ready);
        await page.waitForFunction(() => window.__siteNavFrames.length >= 30);
        const destination = await page.evaluate(measure);
        sameGeometry(destination, source, `${route} → Home (${width}px)`);
        const frames = await page.evaluate(() => window.__siteNavFrames);
        for (const frame of frames) sameGeometry(frame, destination, `Home loading (${width}px)`);
        await page.goBack();
        await page.evaluate(() => document.fonts.ready);
        sameGeometry(await page.evaluate(measure), source, `Back to ${route} (${width}px)`);
        console.log('PASS stable navigation', width, route);
      }
    }
    assert.deepEqual(errors, []);
    console.log('PASS: page switches, Home loading frames, browser history and mobile navigation remain stationary');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
