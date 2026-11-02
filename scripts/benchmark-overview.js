/* Benchmark landing only. Task cards use native links; difficulty selection updates their destination. */
(() => {
  const data = JSON.parse(document.getElementById('benchmark-overview-data').textContent);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const tabs = [...document.querySelectorAll('[data-suite]')];
  const chapters = [...document.querySelectorAll('.bo-chapter')];
  const hero = document.querySelector('.bo-hero');
  const frames = [...document.querySelectorAll('[data-hero-frame]')];
  const selectors = [...document.querySelectorAll('[data-hero-select]')];
  const motionButton = document.querySelector('.bo-motion-toggle');
  const levelKey = 'mind2act-benchmark-demonstration-levels';
  let savedLevels = {};
  try { savedLevels = JSON.parse(sessionStorage.getItem(levelKey)) || {}; } catch { /* Storage is optional. */ }
  let selectedHero = 'mind2act';
  let heroVisible = true;
  let userPaused = reduced.matches;

  function updateHeroPlayback() {
    const animate = heroVisible && !document.hidden && !userPaused && !reduced.matches;
    frames.forEach(frame => {
      const video = frame.querySelector('video');
      if (frame.dataset.heroFrame === selectedHero && animate) {
        if (!video.getAttribute('src')) video.src = video.dataset.preview;
        video.play().catch(() => { /* The poster remains usable when autoplay is unavailable. */ });
      } else video.pause();
    });
    motionButton.setAttribute('aria-pressed', String(userPaused));
    motionButton.textContent = userPaused ? 'Play preview' : 'Pause preview';
    motionButton.disabled = reduced.matches;
    if (reduced.matches) motionButton.textContent = 'Motion reduced';
  }

  function chooseHero(slug) {
    selectedHero = slug;
    const index = frames.findIndex(f => f.dataset.heroFrame === slug);
    frames.forEach((frame, i) => {
      frame.dataset.position = i === index ? 'front' : i === (index + 1) % frames.length ? 'right' : 'left';
    });
    selectors.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.heroSelect === slug)));
    updateHeroPlayback();
  }
  selectors.forEach(button => button.addEventListener('click', () => chooseHero(button.dataset.heroSelect)));
  motionButton.addEventListener('click', () => { userPaused = !userPaused; updateHeroPlayback(); });
  reduced.addEventListener('change', () => { userPaused = reduced.matches; updateHeroPlayback(); });
  document.addEventListener('visibilitychange', () => {
    updateHeroPlayback();
  });
  const heroObserver = new IntersectionObserver(entries => {
    heroVisible = entries[0].isIntersecting;
    updateHeroPlayback();
  }, {threshold: .2});
  heroObserver.observe(hero);
  function rotateHero() {
    if (!heroVisible || userPaused || reduced.matches || document.hidden) return;
    const index = frames.findIndex(f => f.dataset.heroFrame === selectedHero);
    chooseHero(frames[(index + 1) % frames.length].dataset.heroFrame);
  }
  let rotation = setInterval(rotateHero, 8000);

  const indexLinks = [...document.querySelectorAll('[data-index-task]')];
  let indexedTask = null;
  function markIndex(id) {
    indexedTask = id;
    indexLinks.forEach(link => {
      if (link.dataset.indexTask === id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    const suite = id && document.getElementById('task-' + id)?.closest('[data-suite-section]');
    if (suite) highlightSuite(suite.dataset.suiteSection);
  }
  function highlightSuite(slug) {
    tabs.forEach(tab => {
      const active = tab.dataset.suite === slug;
      if (active) tab.setAttribute('aria-current', 'location');
      else tab.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-index-suite]').forEach(link => {
      if (link.dataset.indexSuite === slug) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    document.querySelectorAll(`[data-index-group="${slug}"]`).forEach(group => { group.open = true; });
  }
  function readHash() {
    const hash = location.hash.slice(1);
    // Old #mind / #act / #mind2act bookmarks also remain valid.
    const target = document.getElementById(hash) || document.getElementById('suite-' + hash);
    if (!target?.matches('.bo-chapter, .bo-suite')) return;
    const suite = target.closest('[data-suite-section]');
    markIndex(target.matches('.bo-chapter') ? target.dataset.task : null);
    highlightSuite(suite.dataset.suiteSection);
    target.scrollIntoView({block:'start', behavior:'auto'});
  }
  function pushHash(hash) {
    if (location.hash !== hash) history.pushState(null, '', hash);
  }
  tabs.forEach(tab => {
    tab.addEventListener('click', event => {
      event.preventDefault();
      pushHash(tab.getAttribute('href'));
      readHash();
    });
  });
  document.querySelectorAll('[data-index-task], [data-index-suite]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      document.querySelector('.bo-mobile-index').open = false;
      pushHash(link.getAttribute('href'));
      readHash();
    });
  });
  window.addEventListener('hashchange', readHash);
  window.addEventListener('popstate', readHash);

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(({target, isIntersecting}) => {
      if (!isIntersecting) return;
      target.classList.remove('is-waiting');
      revealObserver.unobserve(target);
    });
  }, {threshold: .06});
  const visibleTasks = new Set();
  const indexObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) visibleTasks.add(entry.target);
      else visibleTasks.delete(entry.target);
    });
    const header = parseInt(getComputedStyle(document.body).getPropertyValue('--bo-header'), 10);
    const candidates = [...visibleTasks].filter(task => !task.closest('[hidden]')).sort((a,b) =>
      Math.abs(a.getBoundingClientRect().top - header) - Math.abs(b.getBoundingClientRect().top - header));
    if (!candidates.length) return;
    // Keep an explicitly selected task active while it is visible, including the last row
    // where the document cannot scroll far enough to put that task at the very top.
    const current = indexedTask && document.getElementById('task-' + indexedTask);
    if (current && !current.closest('[hidden]')) {
      const rect = current.getBoundingClientRect();
      if (rect.bottom > header && rect.top < innerHeight) return;
    }
    markIndex(candidates[0].dataset.task);
  }, {rootMargin:'-90px 0px 0px 0px', threshold: .05});

  chapters.forEach(chapter => {
    const poster = chapter.querySelector('.bo-task-poster');
    const select = chapter.querySelector('select');
    const link = chapter.querySelector('.bo-task-link');
    const choices = data[chapter.dataset.task];
    if (!reduced.matches) chapter.classList.add('is-waiting');
    revealObserver.observe(chapter);
    indexObserver.observe(chapter);
    function selectLevel(level) {
      const asset = choices[level];
      if (!asset) return;
      poster.src = asset.poster;
      select.value = level;
      link.hash = level;
      savedLevels[chapter.dataset.task] = level;
      try { sessionStorage.setItem(levelKey, JSON.stringify(savedLevels)); } catch { /* Storage is optional. */ }
    }
    select.addEventListener('change', () => selectLevel(select.value));
    const restored = savedLevels[chapter.dataset.task];
    if (choices[restored]) selectLevel(restored);
  });

  readHash();
  updateHeroPlayback();
  window.addEventListener('pagehide', () => {
    clearInterval(rotation);
    document.querySelectorAll('video').forEach(video => video.pause());
  });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    rotation = setInterval(rotateHero, 8000);
    updateHeroPlayback();
  });
})();
