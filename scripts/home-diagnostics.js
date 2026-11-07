(() => {
  'use strict';
  const root = document.getElementById('model-diagnostics');
  if (!root) return;
  const video = root.querySelector('.md-video');
  const controls = root.querySelector('.md-controls');
  const pause = root.querySelector('.md-pause');
  const replay = root.querySelector('.md-replay');
  const fullscreen = root.querySelector('.md-fullscreen');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let visible = false;
  let userPaused = false;
  let failed = false;
  let loaded = false;
  video.muted = true;
  root.classList.add('md-enhanced');
  controls.hidden = false;

  const updateUI = () => {
    const playing = !video.paused && video.readyState >= 2 && !video.ended && !reduced.matches && !failed;
    root.dataset.playing = String(playing);
    root.classList.toggle('md-static-mode', reduced.matches || failed);
    pause.hidden = reduced.matches || failed;
    replay.disabled = reduced.matches || failed;
    pause.textContent = playing ? 'Pause' : 'Play';
    pause.setAttribute('aria-label', playing ? 'Pause animation' : 'Play animation');
    pause.setAttribute('aria-pressed', String(userPaused));
    root.querySelector('.md-error').hidden = !failed;
  };
  const shouldPlay = () => visible && !document.hidden && !userPaused && !reduced.matches && !failed;
  const sync = () => {
    if (!shouldPlay()) { video.pause(); updateUI(); return; }
    if (!loaded) { video.load(); loaded = true; }
    const request = video.play();
    if (request) request.catch(error => {
      if (error.name === 'AbortError' || !shouldPlay()) return;
      userPaused = true;
      updateUI();
    });
    updateUI();
  };
  pause.addEventListener('click', () => { userPaused = !video.paused; sync(); });
  replay.addEventListener('click', () => { video.currentTime = 0; userPaused = false; sync(); });
  fullscreen.addEventListener('click', () => {
    const media = root.querySelector('.md-media');
    if (document.fullscreenElement === media) document.exitFullscreen?.();
    else if (media.requestFullscreen) media.requestFullscreen().catch(() => {});
    else if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
  });
  video.addEventListener('play', updateUI);
  video.addEventListener('playing', updateUI);
  video.addEventListener('loadeddata', updateUI);
  video.addEventListener('pause', updateUI);
  video.addEventListener('ended', updateUI);
  const showFallback = () => { failed = true; video.pause(); updateUI(); };
  video.addEventListener('error', showFallback);
  video.querySelector('source').addEventListener('error', showFallback);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      visible = entries.some(entry => entry.isIntersecting);
      sync();
    }, { threshold: .12 }).observe(root);
  } else visible = true;
  reduced.addEventListener('change', sync);
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('beforeprint', () => video.pause());
  window.addEventListener('afterprint', sync);
  sync();
})();
