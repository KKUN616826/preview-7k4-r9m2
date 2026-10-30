/* Benchmark landing only. Native media controls and links remain the primary controls. */
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
  let activeTask = null;

  function load(video) {
    if (!video.getAttribute('src')) {
      video.src = video.dataset.src;
      video.load();
    }
  }

  function updateHeroPlayback() {
    const animate = heroVisible && !document.hidden && !userPaused && !reduced.matches && !activeTask;
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
    if (document.hidden) document.querySelectorAll('.bo-task-video').forEach(v => v.pause());
    updateHeroPlayback();
  });
  const heroObserver = new IntersectionObserver(entries => {
    heroVisible = entries[0].isIntersecting;
    updateHeroPlayback();
  }, {threshold: .2});
  heroObserver.observe(hero);
  function rotateHero() {
    if (!heroVisible || userPaused || reduced.matches || document.hidden || activeTask) return;
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
  }
  function selectSuite(slug) {
    if (!tabs.some(t => t.dataset.suite === slug)) slug = 'mind2act';
    tabs.forEach(tab => {
      const active = tab.dataset.suite === slug;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      const panel = document.getElementById(tab.getAttribute('aria-controls'));
      panel.hidden = !active;
      panel.classList.toggle('is-entering', active);
      if (!active) panel.querySelectorAll('video').forEach(v => v.pause());
    });
    document.querySelectorAll('[data-index-suite]').forEach(link => {
      if (link.dataset.indexSuite === slug) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    document.querySelectorAll(`[data-index-group="${slug}"]`).forEach(group => { group.open = true; });
    if (indexedTask && document.getElementById('task-' + indexedTask)?.closest('[hidden]')) markIndex(null);
  }
  function readHash() {
    const hash = location.hash.slice(1);
    const task = document.getElementById(hash);
    const panel = task?.closest('.bo-suite');
    const selected = tabs.find(tab => tab.getAttribute('aria-selected') === 'true')?.dataset.suite;
    selectSuite(panel ? panel.id.replace('suite-', '') : tabs.some(tab => tab.dataset.suite === hash) ? hash : selected);
    if (task?.matches('.bo-chapter')) {
      markIndex(task.dataset.task);
      task.scrollIntoView({block:'start'});
    }
  }
  function pushHash(hash) {
    if (location.hash !== hash) history.pushState(null, '', hash);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', event => {
      event.preventDefault();
      pushHash('#' + tab.dataset.suite);
      selectSuite(tab.dataset.suite);
    });
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      tabs[next].focus();
      tabs[next].click();
    });
  });
  document.querySelectorAll('[data-index-task], [data-index-suite]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      document.querySelector('.bo-mobile-index').open = false;
      pushHash(link.getAttribute('href'));
      readHash();
      if (link.dataset.indexSuite) document.getElementById('explore').scrollIntoView({block:'start'});
    });
  });
  window.addEventListener('hashchange', readHash);
  window.addEventListener('popstate', readHash);

  const dialog = document.querySelector('.bo-video-dialog');
  const expanded = dialog.querySelector('video');
  let expandedChapter = null;
  let oldOverflow = '';
  function registerPlayback(video) {
    video.addEventListener('play', () => {
      activeTask = video;
      document.querySelectorAll('video').forEach(other => { if (other !== video) other.pause(); });
      const media = video.closest('.bo-media');
      if (media) {
        video.controls = true;
        media.classList.add('is-playing');
        media.querySelector('[data-play]').hidden = true;
      }
      updateHeroPlayback();
    });
    video.addEventListener('pause', () => {
      if (activeTask === video) activeTask = null;
      const media = video.closest('.bo-media');
      if (media) {
        media.classList.remove('is-playing');
        media.querySelector('[data-play]').hidden = false;
      }
      updateHeroPlayback();
    });
  }
  registerPlayback(expanded);
  function expandChapter(chapter) {
    expandedChapter = chapter;
    const video = chapter.querySelector('video');
    const level = chapter.querySelector('select').value;
    const asset = data[chapter.dataset.task][level];
    const time = video.currentTime;
    video.pause();
    document.getElementById('expanded-meta').textContent = `${chapter.dataset.task} / ${level[0].toUpperCase() + level.slice(1)} demonstration`;
    document.getElementById('expanded-title').textContent = chapter.querySelector('h3').getAttribute('title');
    document.getElementById('expanded-instruction').textContent = asset.instruction;
    dialog.querySelector('.bo-expanded-detail').href = chapter.querySelector('.bo-task-detail').href;
    expanded.poster = asset.poster;
    expanded.setAttribute('aria-label', chapter.querySelector('h3').getAttribute('title'));
    expanded.onloadedmetadata = () => { if (time > 0) expanded.currentTime = Math.min(time, expanded.duration); };
    expanded.src = asset.video;
    expanded.load();
    oldOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    dialog.showModal();
    expanded.play().catch(() => { /* Native controls provide a manual playback fallback. */ });
  }
  dialog.querySelector('.bo-dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    const time = expanded.currentTime;
    expanded.pause();
    const original = expandedChapter?.querySelector('video');
    if (original?.readyState >= 1) original.currentTime = time;
    expanded.removeAttribute('src');
    expanded.load();
    document.documentElement.style.overflow = oldOverflow;
  });

  const mediaObserver = new IntersectionObserver(entries => {
    entries.forEach(({target:video, isIntersecting}) => {
      if (isIntersecting && !video.closest('[hidden]')) load(video);
    });
  }, {rootMargin:'200px 0px'});
  const playbackObserver = new IntersectionObserver(entries => {
    entries.forEach(({target:video, isIntersecting}) => { if (!isIntersecting) video.pause(); });
  });
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
    const video = chapter.querySelector('video');
    const error = chapter.querySelector('.bo-media-error');
    const select = chapter.querySelector('select');
    const detail = chapter.querySelector('.bo-task-detail');
    const choices = data[chapter.dataset.task];
    registerPlayback(video);
    if (!reduced.matches) chapter.classList.add('is-waiting');
    revealObserver.observe(chapter);
    mediaObserver.observe(video);
    playbackObserver.observe(video);
    indexObserver.observe(chapter);
    video.addEventListener('error', () => { error.hidden = false; });
    video.addEventListener('loadeddata', () => { error.hidden = true; });
    chapter.querySelector('[data-play]').addEventListener('click', () => {
      load(video);
      video.play().catch(() => { error.hidden = false; });
    });
    chapter.querySelector('[data-expand]').addEventListener('click', () => expandChapter(chapter));
    chapter.querySelector('[data-retry]').addEventListener('click', () => {
      error.hidden = true;
      video.src = video.dataset.src;
      video.load();
    });
    function selectLevel(level, hydrate = true) {
      const asset = choices[level];
      if (!asset) return;
      video.pause();
      video.controls = false;
      video.poster = asset.poster;
      video.dataset.src = asset.video;
      video.setAttribute('aria-label', `${chapter.querySelector('h3').getAttribute('title')}: ${level} demonstration`);
      if (hydrate) { video.src = asset.video; video.load(); }
      select.value = level;
      detail.hash = level;
      error.querySelector('a').hash = level;
      error.hidden = true;
      savedLevels[chapter.dataset.task] = level;
      try { sessionStorage.setItem(levelKey, JSON.stringify(savedLevels)); } catch { /* Storage is optional. */ }
    }
    select.addEventListener('change', () => selectLevel(select.value));
    const restored = savedLevels[chapter.dataset.task];
    if (choices[restored]) selectLevel(restored, false);
  });

  readHash();
  updateHeroPlayback();
  window.addEventListener('pagehide', () => {
    clearInterval(rotation);
    if (dialog.open) dialog.close();
    document.querySelectorAll('video').forEach(video => video.pause());
  });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    rotation = setInterval(rotateHero, 8000);
    updateHeroPlayback();
  });
})();
