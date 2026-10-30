const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {execFileSync}=require('node:child_process');
const plain=s=>s.replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
(async()=>{
 const original=execFileSync('git',['show','f0adf89:index.html'],{encoding:'utf8'});
 const markup=original.match(/<div id="introduction" class="research-abstract".*?<\/div>/s)[0];
 const paragraphs=markup.match(/<p>.*?<\/p>/gs);
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8765/index.html#introduction');
  const root=page.locator('#introduction.research-abstract');
  assert.equal(await root.count(),1);
  const words=s=>s.toLowerCase().match(/[a-z0-9]+/g);
  const copy=await root.locator('.intro-copy').evaluateAll(elements=>elements.map(e=>e.innerText).join(' '));
  assert.deepEqual(words(copy),words(paragraphs.map(plain).join(' ')),'original research wording and order retained');
  assert.equal(await root.locator('.intro-views dt').count(),3);
  assert.deepEqual(await root.locator('.intro-views dt').allTextContents(),['Mind','Act','Mind2Act']);
  assert.match(await root.locator('.intro-copy p').first().evaluate(e=>getComputedStyle(e).fontFamily),/^Helvetica/,'Helvetica typography applied');
  assert.deepEqual(await root.evaluate(e=>[...e.querySelectorAll(':scope > div,:scope > figure')].map(c=>c.className)),['intro-copy intro-motivation','intro-copy intro-framework','intro-overview','intro-copy intro-scope'],'original narrative order retained');
  assert.equal(await page.locator('link[href*="intro-story.css"],script[src*="intro-story.js"],.story-loop-video,.story-view-grid').count(),0,'experimental narrative layout is not loaded');
  assert.equal(await root.locator('details').count(),0);
  assert.equal(await root.locator('figure').count(),1);
  assert.ok((await root.locator('figure a').getAttribute('href')).includes('mind2act-overview-v3.pdf'));
  const image=root.locator('figure img');await image.scrollIntoViewIfNeeded();await image.evaluate(i=>i.decode());
  for(const width of [320,390,820,1440,1920]){
   await page.setViewportSize({width,height:1000});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'no overflow '+width);
   const box=await image.boundingBox();assert.ok(box.width<=width&&Math.abs(box.width/box.height-2600/2113)<.01,'overview keeps its aspect ratio');
   for(const paragraph of await root.locator('.intro-copy p,.intro-views dd').all())assert.equal(await paragraph.isVisible(),true);
   assert.equal(await page.locator('body').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(255, 255, 255)','white page canvas retained');
  }
  const textBox=await root.locator('.intro-copy').first().boundingBox(),figureBox=await image.boundingBox();
  assert.ok(Math.abs(textBox.width-figureBox.width)<1&&Math.abs(textBox.x-figureBox.x)<1,'text and overview share width and alignment');
  assert.equal(await root.locator('.intro-framework p').first().evaluate(e=>getComputedStyle(e).fontSize),'21px','larger desktop body text');
  assert.equal(await page.locator('.cm-orbit-card').count(),30,'task explorer retained');
  assert.deepEqual(errors,[]);
  console.log('PASS original wording, Helvetica, semantic definitions, aligned text and media, overview/PDF, five responsive widths, white background and task explorer.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
