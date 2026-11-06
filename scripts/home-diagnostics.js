(() => {
  'use strict';
  const root = document.getElementById('model-diagnostics');
  if (!root) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const pause = root.querySelector('.md-pause');
  const replay = root.querySelector('.md-replay');
  let visible = false;
  let paused = false;
  const positionIntro = () => {
    const surface = root.querySelector('.md-surface').getBoundingClientRect();
    const svg = root.querySelector('.md-framework > svg').getBoundingClientRect();
    if (!svg.width) return;
    const scale = svg.width / 600;
    // Use the same model throughout: start at the center of the whole scene,
    // then travel to its final diagram position. Works for both column layouts.
    root.style.setProperty('--md-intro-x', `${(surface.width / 2 - (svg.left - surface.left)) / scale - 91}px`);
    root.style.setProperty('--md-intro-y', `${(surface.height * .43 - (svg.top - surface.top)) / scale - 146}px`);
    root.style.setProperty('--md-intro-scale', String(Math.min(235, surface.width * .48) / (134 * scale)));
  };
  const update = () => {
    const animated = !reduced.matches;
    root.classList.toggle('md-enabled', animated);
    root.dataset.playing = String(animated && visible && !paused && !document.hidden);
    pause.hidden = !animated;
    replay.disabled = !animated;
    pause.setAttribute('aria-pressed', String(paused));
    pause.textContent = paused ? 'Resume' : 'Pause';
  };
  pause.addEventListener('click', () => { paused = !paused; update(); });
  replay.addEventListener('click', () => {
    if (reduced.matches) return;
    paused = false;
    root.getAnimations({ subtree: true }).forEach(animation => { animation.currentTime = 0; });
    update();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      visible = entries.some(entry => entry.isIntersecting);
      update();
    }, { threshold: .12 }).observe(root);
  } else {
    visible = true;
  }
  document.addEventListener('visibilitychange', update);
  reduced.addEventListener('change', update);
  // Printing always shows the complete illustrative profile.
  window.addEventListener('beforeprint', () => root.classList.remove('md-enabled'));
  window.addEventListener('afterprint', update);
  positionIntro();
  if ('ResizeObserver' in window) new ResizeObserver(positionIntro).observe(root);
  else window.addEventListener('resize', positionIntro);
  update();
})();
