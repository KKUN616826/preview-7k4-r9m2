/* Reveal content as it enters the page; leave all scrolling to the browser. */
(() => {
 const root=document.querySelector('#introduction.intro-story');if(!root)return;
 const video=root.querySelector('.story-loop-video');
 const chapters=root.querySelector('.story-loop-chapters');
 if(video&&chapters){
  const buttons=[...chapters.querySelectorAll('[data-loop-start]')];
  const sync=()=>buttons.forEach((button,index)=>button.setAttribute('aria-pressed',String(video.currentTime>=Number(button.dataset.loopStart)&&(index===buttons.length-1||video.currentTime<Number(buttons[index+1].dataset.loopStart)))));
  buttons.forEach(button=>button.addEventListener('click',()=>{
   video.currentTime=Number(button.dataset.loopStart);
   sync();
   video.play().catch(()=>{}); // Native controls remain available if playback is interrupted.
  }));
  video.addEventListener('timeupdate',sync);
  video.addEventListener('seeked',sync);
  chapters.hidden=false;
 }
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{
  if(!entry.isIntersecting)return;observer.unobserve(entry.target);
  if(reduced.matches)return;
  entry.target.animate([{opacity:0,transform:'translateY(24px)'},{opacity:1,transform:'translateY(0)'}],{duration:550,easing:'cubic-bezier(.2,.75,.25,1)'});
 })},{threshold:.12});
 root.querySelectorAll('.story-content').forEach(content=>observer.observe(content));
 reduced.addEventListener('change',()=>{if(reduced.matches)root.getAnimations({subtree:true}).forEach(animation=>animation.cancel())});
})();
