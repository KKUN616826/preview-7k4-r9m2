/* Scoped, progressive scroll narrative. Ordinary site scrolling remains unchanged. */
(() => {
 const root=document.querySelector('#introduction.intro-story');if(!root)return;
 const viewport=root.querySelector('.story-viewport'),panels=[...root.querySelectorAll('.story-panel')],dots=[...root.querySelectorAll('[data-story-index]')],next=root.querySelector('.story-next'),status=root.querySelector('.story-status');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),seen=new Set();
 const titles=['The question','Mind2Act World','The closed loop','Start exploring'];
 let active=0,inView=false,settleTimer=0,gestureTimer=0,latched=false,transitioning=false,lastDirection=0;
 function measure(){const header=document.querySelector('.header');const height=header?.getBoundingClientRect().height||88;root.style.setProperty('--story-header',height+'px');root.style.setProperty('--story-height',Math.max(220,innerHeight-height-1)+'px');root.style.setProperty('--story-width',document.documentElement.clientWidth+'px');root.classList.toggle('story-has-overflow',panels.some(p=>p.offsetHeight>viewport.clientHeight+4));}
 function reveal(index){if(!inView||seen.has(index))return;seen.add(index);if(reduced.matches)return;
  panels[index].querySelector('.story-content').animate([{opacity:0,transform:'translateY(30px) scale(.985)'},{opacity:1,transform:'translateY(-2px) scale(1)',offset:.78},{opacity:1,transform:'translateY(0) scale(1)'}],{duration:600,easing:'cubic-bezier(.2,.75,.25,1)'});
  if(index===2)panels[index].querySelector('.story-loop-line').animate([{opacity:0,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}],{duration:400,delay:220,fill:'backwards'});
 }
 function setActive(index){active=index;panels.forEach((p,i)=>p.classList.toggle('is-active',i===index));dots.forEach((d,i)=>{if(i===index)d.setAttribute('aria-current','step');else d.removeAttribute('aria-current')});next.innerHTML=index===panels.length-1?'Explore tasks <span aria-hidden="true">↘</span>':'Next <span aria-hidden="true">↓</span>';status.textContent=`Screen ${index+1} of ${panels.length}: ${titles[index]}`;reveal(index);}
 function nearest(){let closest=0,dist=Infinity;panels.forEach((p,i)=>{const d=Math.abs(p.offsetTop-viewport.scrollTop);if(d<dist){closest=i;dist=d}});return closest;}
 function finish(){clearTimeout(settleTimer);transitioning=false;setActive(nearest());}
 function align(){const header=parseFloat(root.style.getPropertyValue('--story-header'))||88,box=viewport.getBoundingClientRect();if(Math.abs(box.top-header)>4)window.scrollTo({top:scrollY+box.top-header,behavior:'instant'});}
 function go(index){if(index<0||index>=panels.length)return;align();transitioning=true;viewport.scrollTo({top:panels[index].offsetTop,behavior:reduced.matches?'instant':'smooth'});if(reduced.matches)finish();}
 function leave(){const target=document.querySelector('#capability-explorer');if(!target)return;const header=parseFloat(root.style.getPropertyValue('--story-header'))||88;window.scrollTo({top:scrollY+target.getBoundingClientRect().top-header-12,behavior:reduced.matches?'instant':'smooth'});const heading=target.querySelector('h2');if(heading){heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true})}}
 dots.forEach(d=>d.addEventListener('click',()=>go(Number(d.dataset.storyIndex))));
 next.addEventListener('click',()=>active===panels.length-1?leave():go(active+1));root.querySelector('.story-skip').addEventListener('click',e=>{e.preventDefault();leave()});
 viewport.addEventListener('scroll',()=>{clearTimeout(settleTimer);settleTimer=setTimeout(finish,120)},{passive:true});viewport.addEventListener('scrollend',finish);
 function releaseGesture(){clearTimeout(gestureTimer);gestureTimer=setTimeout(()=>{if(transitioning)releaseGesture();else latched=false;},220);}
 root.querySelector('.story-stage').addEventListener('wheel',e=>{
  if(e.ctrlKey||Math.abs(e.deltaX)>Math.abs(e.deltaY)||Math.abs(e.deltaY)<1||!getSelection().isCollapsed||e.target.closest('input,textarea,select,[contenteditable=true]'))return;
  if(panels[active].offsetHeight>viewport.clientHeight+4)return;
  const direction=Math.sign(e.deltaY),reverse=latched&&direction!==lastDirection;releaseGesture();
  if(latched&&!reverse){e.preventDefault();return;}
  if((active===0&&direction<0)||(active===panels.length-1&&direction>0)){latched=false;return;}
  e.preventDefault();latched=true;lastDirection=direction;
  const header=parseFloat(root.style.getPropertyValue('--story-header'))||88,box=viewport.getBoundingClientRect();
  if(Math.abs(box.top-header)>5){window.scrollTo({top:scrollY+box.top-header,behavior:reduced.matches?'instant':'smooth'});return;}
  if(reverse&&transitioning){go(active);return;}
  go(active+direction);
 },{passive:false});
 viewport.addEventListener('keydown',e=>{if(e.target.closest('a,button,input,textarea,select,summary')||e.ctrlKey||e.metaKey||e.altKey)return;const direction=['ArrowDown','PageDown',' '].includes(e.key)?1:['ArrowUp','PageUp'].includes(e.key)?-1:0;if(!direction)return;if(panels[active].offsetHeight>viewport.clientHeight+4)return;if(active+direction<0||active+direction>=panels.length)return;e.preventDefault();go(active+direction)});
 root.classList.add('is-enhanced');measure();setActive(0);
 new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;root.classList.toggle('is-reading',inView);if(inView)reveal(active)},{threshold:.2}).observe(viewport);
 if(location.hash==='#introduction')document.fonts.ready.then(()=>requestAnimationFrame(align));
 window.addEventListener('resize',()=>{measure();viewport.scrollTo({top:panels[active].offsetTop,behavior:'instant'})});
 reduced.addEventListener('change',()=>{root.getAnimations({subtree:true}).forEach(a=>a.cancel());if(reduced.matches)finish()});
})();
