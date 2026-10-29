/* Local layered animation is pre-rendered: real leaderboard data remains live HTML. */
(() => {
 const root=document.querySelector('.lb-stage');
 const video=root?.querySelector('.lb-stage-motion-video');
 const button=root?.querySelector('.lb-stage-motion-toggle');
 if(!video||!button)return;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let inView=false,userPaused=false,failed=false,playAttempt=0;
 video.muted=true;
 button.hidden=false;
 function updateButton(){
  button.disabled=reduced.matches;
  button.textContent=reduced.matches?'Motion reduced':userPaused?'Play animation':'Pause animation';
  button.setAttribute('aria-pressed',String(userPaused||reduced.matches));
  button.setAttribute('aria-label',reduced.matches?'Animation disabled by reduced motion preference':userPaused?'Play mechanical arm animation':'Pause mechanical arm animation');
 }
 function sync(){
  updateButton();const attempt=++playAttempt;
  if(failed||reduced.matches||userPaused||!inView||document.hidden){video.pause();if(reduced.matches)delete root.dataset.motionReady;return;}
  video.play().catch(()=>{if(attempt===playAttempt){userPaused=true;updateButton();}});
 }
 video.addEventListener('playing',()=>{if(!reduced.matches&&!failed)root.dataset.motionReady='true';});
 function fallback(){failed=true;video.pause();delete root.dataset.motionReady;button.hidden=true;}
 video.addEventListener('error',fallback);
 video.querySelector('source')?.addEventListener('error',fallback);
 // Metadata failure may happen before deferred scripts attach event listeners.
 if(video.error||video.networkState===HTMLMediaElement.NETWORK_NO_SOURCE)fallback();
 button.addEventListener('click',()=>{userPaused=!userPaused;sync();});
 reduced.addEventListener('change',sync);
 document.addEventListener('visibilitychange',sync);
 new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;sync();},{threshold:.1}).observe(root.querySelector('.lb-stage-world'));
 updateButton();
})();
