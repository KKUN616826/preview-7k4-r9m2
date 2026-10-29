/* Local layered animation is pre-rendered: real leaderboard data remains live HTML. */
(() => {
 const root=document.querySelector('.lb-stage');
 const video=root?.querySelector('.lb-stage-motion-video');
 const button=root?.querySelector('.lb-stage-motion-toggle');
 if(!video||!button)return;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let inView=false,userPaused=false,failed=false,playAttempt=0,blocked=false,retries=0,retryTimer;
 video.muted=true;
 button.hidden=false;
 function updateButton(){
  button.disabled=reduced.matches;
  button.textContent=reduced.matches?'Motion reduced':(userPaused||blocked)?'Play animation':'Pause animation';
  button.setAttribute('aria-pressed',String(userPaused||blocked||reduced.matches));
  button.setAttribute('aria-label',reduced.matches?'Animation disabled by reduced motion preference':(userPaused||blocked)?'Play mechanical arm animation':'Pause mechanical arm animation');
 }
 function sync(){
  clearTimeout(retryTimer);updateButton();const attempt=++playAttempt;
  if(failed||reduced.matches||userPaused||!inView||document.hidden){video.pause();if(reduced.matches)delete root.dataset.motionReady;return;}
  if(blocked)return;
  video.play().catch(error=>{
   if(attempt!==playAttempt)return;
   // A browser interruption is not a user pause. Retry briefly, then allow
   // readiness/visibility events or the play control to recover playback.
   if(error.name==='NotAllowedError'){blocked=true;updateButton();return;}
   if(retries<2){retries++;retryTimer=setTimeout(sync,250*retries);}
   else{blocked=true;updateButton();}
  });
 }
 video.addEventListener('playing',()=>{if(reduced.matches||failed||userPaused||!inView||document.hidden){video.pause();return;}blocked=false;retries=0;root.dataset.motionReady='true';updateButton();});
 function fallback(){clearTimeout(retryTimer);++playAttempt;failed=true;video.pause();delete root.dataset.motionReady;button.hidden=true;}
 video.addEventListener('error',fallback);
 video.querySelector('source')?.addEventListener('error',fallback);
 // Metadata failure may happen before deferred scripts attach event listeners.
 if(video.error||video.networkState===HTMLMediaElement.NETWORK_NO_SOURCE)fallback();
 button.addEventListener('click',()=>{userPaused=blocked?false:!userPaused;blocked=false;retries=0;sync();});
 function recover(){blocked=false;retries=0;sync();}
 reduced.addEventListener('change',recover);
 document.addEventListener('visibilitychange',recover);
 window.addEventListener('pageshow',recover);
 video.addEventListener('canplay',()=>{if(video.paused)sync();});
 new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;recover();},{threshold:.1}).observe(root.querySelector('.lb-stage-world'));
 updateButton();
})();
