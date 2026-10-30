/* Homepage destination regression; full results have their own interaction suite. */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const base=process.env.HERO_PREVIEW_URL||'http://127.0.0.1:8765/';
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base,{waitUntil:'domcontentloaded'});
  const banner=page.locator('.home-leaderboard-banner');await banner.scrollIntoViewIfNeeded();
  assert.equal(await page.locator('.view-leaderboard').count(),0);
  await page.waitForFunction(()=>{const img=document.querySelector('.home-leaderboard-art');return img.complete&&img.naturalWidth>0});
  assert.equal(await banner.locator('a').getAttribute('href'),'leaderboard.html');
  for(const width of [320,390,700,1024,1920]){
   await page.setViewportSize({width,height:900});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'overflow at '+width);
   assert.equal(await banner.locator('a').isVisible(),true);
  }
  await banner.locator('a').click();await page.waitForURL('**/leaderboard.html');
  assert.equal(await page.locator('.lb-table').count(),1);
  assert.deepEqual(errors,[]);
  console.log('PASS: homepage banner, image, responsive widths and standalone leaderboard navigation');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
