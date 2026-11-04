(() => {
  const root = document.querySelector('#tasks');
  if (!root) return;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const button = root.querySelector('.demo-motion-toggle');
  let paused = preference.matches;
  function updateButton() {
    button.textContent = paused ? 'Play' : 'Pause';
    button.setAttribute('aria-pressed', String(paused));
    button.setAttribute('aria-label', paused ? 'Play automatic scrolling' : 'Pause automatic scrolling');
  }
  button.addEventListener('click', () => { paused = !paused; updateButton(); });
  preference.addEventListener('change', () => { paused = preference.matches; updateButton(); });
  root.querySelectorAll('.difficulty-row').forEach(row => {
    const viewport = row.querySelector('.task-marquee');
    const track = row.querySelector('.marquee-track');
    const right = row.dataset.direction === 'right';
    let offset = 0;
    let previous = 0;
    let hovering = false;
    viewport.addEventListener('pointerenter', () => { hovering = true; });
    viewport.addEventListener('pointerleave', () => { hovering = false; });
    function tick(now) {
      const delta = previous ? Math.min(now - previous, 50) : 0;
      previous = now;
      const bounds = viewport.getBoundingClientRect();
      if (!paused && !document.hidden && !hovering && !viewport.contains(document.activeElement) && bounds.bottom > 0 && bounds.top < innerHeight) {
        const step = track.firstElementChild.offsetWidth + parseFloat(getComputedStyle(track).gap);
        offset += delta * (right ? -0.025 : 0.025);
        if (offset < 0) {
          track.prepend(track.lastElementChild);
          offset += step;
        }
        if (offset >= step) {
          track.append(track.firstElementChild);
          offset -= step;
        }
        viewport.scrollLeft = offset;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
  updateButton();
})();
