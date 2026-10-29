const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const {readFileSync} = require('node:fs');
const plain = s => s.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://127.0.0.1:8765/index.html#introduction');
    const root = page.locator('#introduction');
    const paragraphs = readFileSync('scripts/intro-story-background.html','utf8').match(/<p>.*?<\/p>/gs);
    const visibleCopy = plain(await root.innerText());
    for (const i of [0]) assert.ok(visibleCopy.includes(plain(paragraphs[i])), 'original research paragraph visible');
    assert.equal(await root.locator('details').count(), 0, 'core research needs no expansion');
    assert.equal(await page.locator('.benchmark-facts').isVisible(), false, 'redundant statistic cards removed');
    const taskImage = root.locator('.story-task-media img');
    await taskImage.evaluate(i=>i.decode());
    assert.equal(await root.locator('.story-task-media a').getAttribute('href'),'tasks/CP05.html#hard');
    assert.equal(await root.locator('.story-evidence-flow li').count(),3);
    const frames=root.locator('.story-view-art,.story-loop-art');
    const sources=JSON.parse(readFileSync('media/research-frames/sources.json','utf8')).frames;
    assert.equal(await frames.count(),7);
    assert.equal(await root.locator('img[src*="research-illustrations"]').count(),0,'generated illustrations replaced');
    assert.deepEqual(await frames.evaluateAll(images=>images.map(i=>i.getAttribute('src'))),sources.map(f=>f.image),'every frame has a recorded video source');
    assert.deepEqual(await root.locator('.story-view-example').evaluateAll(links=>links.map(a=>a.getAttribute('href'))),['tasks/S.html#medium','tasks/PR3.html#medium','tasks/CP01.html#medium']);
    for (const frame of await frames.all()) {
      await frame.scrollIntoViewIfNeeded();
      await frame.evaluate(e=>e.decode());
      assert.ok(await frame.evaluate(e=>e.naturalWidth>=960),'full-resolution simulation frame loads');
    }
    const img = root.locator('.intro-overview img');
    await img.scrollIntoViewIfNeeded();
    await img.evaluate(i => i.decode());
    for (const width of [320,390,820,1440,1920]) {
      await page.setViewportSize({width,height:1000});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'no horizontal overflow at '+width);
      for (const frame of await frames.all()) {
        const bounds=await frame.boundingBox();
        assert.ok(bounds.width <= width, 'simulation frame fits at '+width);
        const naturalRatio=await frame.evaluate(e=>e.naturalWidth/e.naturalHeight);
        assert.ok(Math.abs(bounds.width/bounds.height-naturalRatio)<.01,'frame is not cropped or distorted');
        assert.equal(await frame.evaluate(e=>getComputedStyle(e).filter),'none','original simulation colors');
      }
      const box = await img.boundingBox();
      assert.ok(Math.abs(box.width/box.height - 2600/2113)<.01, 'overview aspect ratio');
      const columns = await root.locator('.story-view-grid').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length);
      assert.equal(columns, width<=600 ? 1 : 3, 'evaluation views adapt at '+width);
      const frameColumns=await root.locator('.story-keyframes').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length);
      assert.equal(frameColumns,width<=450?1:2,'keyframes remain readable at '+width);
    }
    await page.setViewportSize({width:1440,height:1000});
    await root.scrollIntoViewIfNeeded();
    const before = await page.evaluate(()=>scrollY);
    await page.mouse.move(700,400);
    await page.mouse.wheel(0,260);
    await page.waitForTimeout(400);
    assert.ok(await page.evaluate(y=>scrollY>y+100,before), 'ordinary document scrolling');
    await root.locator('.story-explore-link').click();
    await page.waitForTimeout(300);
    assert.equal(new URL(page.url()).hash, '#capability-explorer');
    assert.equal(await page.locator('.cm-orbit-card').count(),30);
    assert.deepEqual(errors,[]);
    console.log('PASS: seven authentic video frames, original colors and aspect ratios, task links, research visible, responsive columns, no overflow at five widths, overview ratio, document scrolling, 30-task explorer link.');
  } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
