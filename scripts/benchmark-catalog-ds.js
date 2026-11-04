// Task catalogue: search, suite filter (mirrored in ?suite=&q=), hover previews.
(() => {
  const input = document.getElementById('task-search');
  const tabs = [...document.querySelectorAll('.catalog [data-filter]')];
  const groups = [...document.querySelectorAll('.tc-group')];
  const cards = [...document.querySelectorAll('.task-card2')];
  const status = document.getElementById('catalog-status');
  const empty = document.getElementById('catalog-empty');
  const params = new URLSearchParams(location.search);
  const valid = new Set(tabs.map(t => t.dataset.filter));
  const state = { suite: valid.has(params.get('suite')) ? params.get('suite') : 'all', q: params.get('q') || '' };
  input.value = state.q;

  const render = () => {
    const words = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const ok = (state.suite === 'all' || card.dataset.group === state.suite) && words.every(w => card.dataset.search.includes(w));
      card.hidden = !ok;
      if (ok) shown += 1;
    });
    groups.forEach(g => { g.hidden = !g.querySelector('.task-card2:not([hidden])'); });
    tabs.forEach(t => t.setAttribute('aria-selected', t.dataset.filter === state.suite));
    empty.hidden = shown > 0;
    status.textContent = shown === cards.length ? '' : `${shown} of ${cards.length} tasks`;
    const next = new URLSearchParams();
    if (state.suite !== 'all') next.set('suite', state.suite);
    if (state.q) next.set('q', state.q);
    history.replaceState(null, '', location.pathname + (next.toString() ? '?' + next : ''));
  };

  tabs.forEach(t => t.addEventListener('click', () => { state.suite = t.dataset.filter; render(); }));
  input.addEventListener('input', () => { state.q = input.value.trim(); render(); });
  document.addEventListener('keydown', ev => {
    if (ev.key === '/' && document.activeElement !== input && !/input|textarea/i.test(document.activeElement.tagName)) {
      ev.preventDefault(); input.focus();
    }
  });
  render();

  // Hover preview: load the clip only when the pointer rests on a card.
  if (matchMedia('(hover:hover) and (prefers-reduced-motion:no-preference)').matches) {
    cards.filter(c => c.dataset.preview).forEach(card => {
      let timer, video;
      card.addEventListener('mouseenter', () => {
        timer = setTimeout(() => {
          video = Object.assign(document.createElement('video'), { src: card.dataset.preview, muted: true, loop: true, playsInline: true });
          video.setAttribute('aria-hidden', 'true');
          card.querySelector('.tc-media').appendChild(video);
          video.play().catch(() => {});
        }, 300);
      });
      card.addEventListener('mouseleave', () => { clearTimeout(timer); if (video) { video.remove(); video = null; } });
    });
  }
})();
