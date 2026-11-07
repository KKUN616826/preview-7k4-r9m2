/* Playback checks for the approved eight-second silver teaser. */
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const base = process.env.HERO_PREVIEW_URL || 'http://127.0.0.1:8765/';
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE});
  try {
    for (const width of [320,390,820,1440]) {
      const page = await browser.newPage({viewport:{width,height:1000}});
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.route('**/*.mp4', r => r.request().url().includes('/diagnostics-teaser/') ? r.continue() : r.abort());
      await page.goto(base,{waitUntil:'domcontentloaded'});
      const root = page.locator('#model-diagnostics');
      assert.equal(await root.count(),1);
      assert.ok(await root.locator('.md-video').evaluate(v => v.paused),'No autoplay before entering the viewport');
      await root.scrollIntoViewIfNeeded();
      await page.waitForFunction(() => document.querySelector('#model-diagnostics').dataset.playing === 'true');
      const media = await root.locator('.md-video').evaluate(v => ({duration:v.duration,width:v.videoWidth,height:v.videoHeight,muted:v.muted,loop:v.loop,src:v.currentSrc}));
      assert.ok(Math.abs(media.duration-8)<.02);
      assert.equal(media.width,1600); assert.equal(media.height,668);
      assert.ok(media.muted && media.loop);
      assert.ok(media.src.endsWith('/media/diagnostics-teaser/diagnostics-silver-8s.mp4'));
      const box = await root.boundingBox();
      assert.ok(box.x>=0 && box.x+box.width<=width+1);
      if(width===1440) assert.ok(box.height<440,'Compact landscape replacement');
      await root.hover();
      await root.locator('.md-pause').click();
      await page.waitForFunction(() => document.querySelector('#model-diagnostics .md-video').paused);
      const time = await root.locator('.md-video').evaluate(v=>v.currentTime);
      await page.waitForTimeout(100);
      assert.ok(Math.abs(await root.locator('.md-video').evaluate(v=>v.currentTime)-time)<.04,'Pause freezes playback');
      await root.locator('.md-replay').click();
      await page.waitForFunction(() => !document.querySelector('#model-diagnostics .md-video').paused);
      assert.ok(await root.locator('.md-video').evaluate(v=>v.currentTime<.5),'Replay restarts from the opening');
      await root.locator('.md-video').evaluate(v=>{v.currentTime=7.85});
      await page.waitForFunction(() => {const v=document.querySelector('#model-diagnostics .md-video');return v.currentTime<1 && !v.paused},{},{timeout:5000});
      if(width===1440){
        await root.locator('.md-fullscreen').click();
        await page.waitForFunction(()=>document.fullscreenElement?.classList.contains('md-media'));
        await page.evaluate(()=>document.exitFullscreen());
      }
      await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
      await page.waitForFunction(()=>document.querySelector('#model-diagnostics .md-video').paused);
      await page.emulateMedia({reducedMotion:'reduce'});
      await root.scrollIntoViewIfNeeded();
      await page.waitForFunction(()=>document.querySelector('#model-diagnostics').classList.contains('md-static-mode'));
      assert.ok(await root.locator('.md-static').isVisible());
      assert.ok(await root.locator('.md-video').isHidden());
      assert.ok(await root.locator('.md-pause').isHidden());
      assert.ok(await root.locator('.md-replay').isDisabled());
      assert.deepEqual(errors,[]);
      console.log('PASS '+width+'px: approved 8s film, fit, muted autoplay, pause/replay, loop, offscreen pause, reduced motion'+(width===1440?', fullscreen':''));
      await page.close();
    }
    const noJS = await browser.newPage({javaScriptEnabled:false});
    await noJS.route('**/*.mp4',r=>r.abort());
    await noJS.goto(base,{waitUntil:'domcontentloaded'});
    await noJS.locator('#model-diagnostics').scrollIntoViewIfNeeded();
    assert.ok(await noJS.locator('#model-diagnostics .md-static').isVisible());
    assert.equal(await noJS.locator('#model-diagnostics .md-open a').getAttribute('href'),'media/diagnostics-teaser/diagnostics-silver-8s.mp4');
    await noJS.close();
    const failed = await browser.newPage();
    await failed.route('**/*.mp4',r=>r.abort());
    await failed.goto(base,{waitUntil:'domcontentloaded'});
    await failed.locator('#model-diagnostics').scrollIntoViewIfNeeded();
    await pageWaitError(failed);
    assert.ok(await failed.locator('#model-diagnostics .md-static').isVisible());
    assert.ok(await failed.locator('#model-diagnostics .md-error a').isVisible());
    await failed.close();
    console.log('PASS no-JavaScript and failed-video poster fallbacks');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1});
async function pageWaitError(page){await page.waitForFunction(()=>!document.querySelector('#model-diagnostics .md-error').hidden);}
