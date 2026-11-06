/* Regression for oversized Repository SVG during incremental HTML loading.
 * Requires Playwright (NODE_PATH if installed outside this repo).
 * CHROMIUM_EXECUTABLE optionally selects a local Chrome executable.
 * HOME_REFRESH_HTML optionally checks a saved deployment HTML instead.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');

(async () => {
  const html = fs.readFileSync(process.env.HOME_REFRESH_HTML || path.join(__dirname, '../index.html'), 'utf8');
  const marker = 'Repository<span';
  assert.ok(html.includes(marker), 'Repository action must exist in the fixture');
  const split = html.indexOf(marker) + marker.length;
  let finishResponse;
  const server = http.createServer((req, res) => {
    if (req.url !== '/index.html') {
      // Isolate the document's first paint from scripts, media and external CSS.
      res.writeHead(204).end();
      return;
    }
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    finishResponse = () => res.end(html.slice(split));
    res.write(html.slice(0, split));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({
      ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}),
      headless: true,
    });
    for (const width of [2048, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 1162 }, javaScriptEnabled: false });
      try {
        await page.goto(`http://127.0.0.1:${server.address().port}/index.html`, { waitUntil: 'commit' });
        const icon = page.locator('.project-action-icon').first();
        await icon.waitFor({ state: 'attached' });
        const check = async phase => {
          const size = await icon.boundingBox();
          assert.ok(size && Math.abs(size.width - 19) < 1 && Math.abs(size.height - 19) < 1,
            `${width}px ${phase}: Repository icon is ${size?.width} × ${size?.height}; expected 19 × 19`);
          console.log(`PASS ${width}px ${phase}: Repository icon 19 × 19`);
        };
        await check('partial HTML');
        finishResponse();
        await page.waitForLoadState('load');
        await check('complete HTML');
      } finally {
        finishResponse?.();
        await page.close();
      }
    }
  } finally {
    await browser?.close();
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
