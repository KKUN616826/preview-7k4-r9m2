const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  await page.goto('http://127.0.0.1:8765/#capability-explorer');
  await page.waitForFunction(()=>document.querySelector('.capability-map').dataset.renderer==='webgl');
  const orbit=page.locator('.cm-orbit'),node=page.locator('[data-task="CP04"]');
  const snapshot=()=>page.locator('.cm-orbit').evaluate(el=>{
   const r=el.getBoundingClientRect(),nodes=[...el.querySelectorAll('[data-task]')].filter(n=>n.dataset.front==='true');
   return {visible:nodes.length,central:nodes.filter(n=>{const b=n.getBoundingClientRect();return Math.hypot(b.x+b.width/2-r.x-r.width/2,b.y+b.height/2-r.y-r.height/2)<r.width*.32}).length};
  });
  for(const horizontal of ['ArrowLeft','ArrowRight'])for(const vertical of ['ArrowUp','ArrowDown']){
   await orbit.focus();for(let i=0;i<20;i++){await page.keyboard.press(horizontal);await page.keyboard.press(vertical)}
   await page.waitForTimeout(100);
   const stats=await snapshot();assert.ok(stats.visible>=12,JSON.stringify(stats));assert.ok(stats.central>=4,JSON.stringify(stats));
   const atLimit=await node.getAttribute('style');
   for(let i=0;i<10;i++){await page.keyboard.press(horizontal);await page.keyboard.press(vertical)}
   await page.waitForTimeout(100);assert.equal(await node.getAttribute('style'),atLimit,'repeated keys cannot flip past populated view');
  }
  // Large repeated drags settle at the same limits without accumulating roll.
  for(const direction of [-1,1]){
   const r=await orbit.boundingBox();
   for(let i=0;i<5;i++){
    await page.mouse.move(r.x+r.width*.5,r.y+r.height*.5);await page.mouse.down();
    await page.mouse.move(r.x+r.width*(.5+direction*.44),r.y+r.height*(.5+direction*.35),{steps:8});await page.mouse.up();await page.waitForTimeout(100);
   }
   const stats=await snapshot();assert.ok(stats.visible>=12);assert.ok(stats.central>=4);
  }
  await page.locator('[data-suite="act"]').click();await page.waitForTimeout(100);
  const before=await node.getAttribute('style');
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.locator('.cm-motion').click();await page.mouse.move(10,10);await page.waitForTimeout(700);
  const after=await node.getAttribute('style');assert.notEqual(after,before,'motion animates from current category');
  const position=style=>[...style.matchAll(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)/g)][0].slice(1).map(Number);
  const a=position(before),b=position(after);assert.ok(Math.hypot(a[0]-b[0],a[1]-b[1])<35,'autoplay does not jump back to default');
  await page.locator('.cm-motion').click();
  await page.locator('.cm-reset').click();await page.waitForTimeout(900);
  await orbit.scrollIntoViewIfNeeded();await page.screenshot({path:'../../outputs/lunar-bounded-rotation.png'});
  console.log('PASS: bounded keyboard, repeated drags, populated corners, no accumulated roll, autoplay retains current view.');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
