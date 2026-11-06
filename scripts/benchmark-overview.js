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

  const explorer = document.getElementById('explore');
  const suiteControls = document.querySelector('.bo-suite-tabs');
  const searchForm = document.querySelector('.bo-search');
  const searchInput = document.getElementById('benchmark-search');
  const searchStatus = document.getElementById('benchmark-search-status');
  const clearButton = document.querySelector('.bo-search-clear');
  const emptySearch = document.querySelector('.bo-search-empty');
  const suites = [...document.querySelectorAll('[data-suite-section]')];
  const normalize = value => value.normalize('NFKC').toLowerCase().replace(/[–—-]/g, ' ');
  const searchText = new Map(chapters.map(chapter => [chapter, normalize(chapter.dataset.search)]));
  let selectedSuite = suites[0].dataset.suiteSection;

  // Browsing shows one suite. Searching always considers the complete 30-task catalog.
  function filterTasks() {
    const terms = normalize(searchInput.value.trim()).split(/\s+/).filter(Boolean);
    const searching = terms.length > 0;
    let count = 0;
    chapters.forEach(chapter => {
      chapter.hidden = !terms.every(term => searchText.get(chapter).includes(term));
      if (!chapter.hidden) count++;
    });
    suites.forEach(suite => {
      suite.hidden = searching
        ? ![...suite.querySelectorAll('.bo-chapter')].some(task => !task.hidden)
        : suite.dataset.suiteSection !== selectedSuite;
    });
    tabs.forEach(tab => tab.setAttribute('aria-pressed', String(!searching && tab.dataset.suite === selectedSuite)));
    explorer.classList.toggle('is-searching', searching);
    clearButton.hidden = !searchInput.value;
    document.querySelector('.bo-search-shortcut').hidden = !!searchInput.value;
    emptySearch.hidden = count > 0;
    searchStatus.textContent = searching ? `${count} ${count === 1 ? 'task' : 'tasks'} found` : '';
  }
  function clearSearch() {
    searchInput.value = '';
    filterTasks();
  }
  searchInput.addEventListener('input', filterTasks);
  clearButton.addEventListener('click', () => { clearSearch(); searchInput.focus(); });
  document.querySelector('[data-clear-search]').addEventListener('click', () => { clearSearch(); searchInput.focus(); });
  searchForm.addEventListener('submit', event => {
    event.preventDefault();
    explorer.scrollIntoView({block:'start'});
  });
  document.addEventListener('keydown', event => {
    if (event.isComposing || event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.key === '/' && !event.target.closest('input, textarea, select, [contenteditable]')) {
      event.preventDefault();
      searchInput.focus();
    } else if (event.key === 'Escape' && event.target === searchInput) {
      event.preventDefault();
      clearSearch();
    }
  });
  function readHash() {
    const hash = location.hash.slice(1);
    if (!hash) {
      selectedSuite = suites[0].dataset.suiteSection;
      clearSearch();
      return;
    }
    // Old #mind / #act / #mind2act and task-specific bookmarks remain valid.
    const target = document.getElementById(hash) || document.getElementById('suite-' + hash);
    if (!target?.matches('.bo-chapter, .bo-suite')) return;
    selectedSuite = target.closest('[data-suite-section]').dataset.suiteSection;
    clearSearch();
    (target.matches('.bo-chapter') ? target : explorer).scrollIntoView({block:'start', behavior:'auto'});
  }
  function selectSuite(slug) {
    selectedSuite = slug;
    clearSearch();
    const hash = '#suite-' + slug;
    if (location.hash !== hash) history.pushState(null, '', hash);
  }
  tabs.forEach(tab => tab.addEventListener('click', () => selectSuite(tab.dataset.suite)));
  suiteControls.addEventListener('keydown', event => {
    const current = event.target.closest('[data-suite]');
    if (!current || event.altKey || event.ctrlKey || event.metaKey) return;
    const position = tabs.indexOf(current);
    const next = event.key === 'ArrowRight' ? (position + 1) % tabs.length
      : event.key === 'ArrowLeft' ? (position - 1 + tabs.length) % tabs.length
      : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
    if (next === null) return;
    event.preventDefault();
    selectSuite(tabs[next].dataset.suite);
    tabs[next].focus();
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
  chapters.forEach(chapter => {
    const poster = chapter.querySelector('.bo-task-poster');
    const select = chapter.querySelector('select');
    const link = chapter.querySelector('.bo-task-link');
    const choices = data[chapter.dataset.task];
    if (!reduced.matches) chapter.classList.add('is-waiting');
    revealObserver.observe(chapter);
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

  filterTasks();
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
