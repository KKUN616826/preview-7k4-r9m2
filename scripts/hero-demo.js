(() => {
  const hero = document.querySelector('.demo-hero');
  const payload = document.getElementById('heroDemoData');
  if (!hero || !payload || !window.Mind2ActDemo) return;
  const data = JSON.parse(payload.textContent);
  const { presentationAt, sourceTime } = window.Mind2ActDemo;
  const find = selector => hero.querySelector(selector);
  const video = find('video'), scene = find('.demo-scene');
  const play = find('.demo-play');
  const cards = [...hero.querySelectorAll('.demo-card')];
  const viewport = find('.demo-memory-window'), strip = find('.demo-memory-strip');
  const focus = find('.demo-key-focus'), connection = find('.demo-connection');
  const motion = find('.demo-motion');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const samples = data.motion.samples;
  // Preview five central observations; the full 12-note action sequence stays intact.
  const memoryFirst = 3, memoryLast = 7;
  const sceneButtons = [...hero.querySelectorAll('[data-demo-phase]')];
  const noteName = event => 'CDEFGAB'[event.keyId % 7] + (2 + Math.floor(event.keyId / 7));
  const plot = { left: 40, right: 346, top: [20, 93], height: 48 };
  const span = data.media.duration - data.media.actStart;
  const xAt = time => plot.left + (time - data.media.actStart) / span * (plot.right - plot.left);
  const yAt = (height, arm) => plot.top[arm] + plot.height * (1 - (height - data.motion.range[0]) / (data.motion.range[1] - data.motion.range[0]));
  const svg = (tag, attrs, text) => {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value));
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const grid = find('.demo-chart-grid');
  for (let arm = 0; arm < 2; arm++) {
    for (const height of [data.motion.range[0], data.motion.range[1]]) {
      const y = yAt(height, arm);
      grid.append(svg('line', { x1: plot.left, x2: plot.right, y1: y, y2: y }));
      grid.append(svg('text', { x: 32, y: y + 3, 'text-anchor': 'end' }, String(height)));
    }
    grid.append(svg('text', { x: 4, y: plot.top[arm] + 27, class: 'demo-arm-label demo-arm-' + arm }, arm ? 'Right' : 'Left'));
    const path = samples.map((sample, index) => (index ? 'L' : 'M') + xAt(sample[0]).toFixed(2) + ',' + yAt(sample[arm + 1], arm).toFixed(2)).join(' ');
    find(arm ? '.demo-trace-right' : '.demo-trace-left').setAttribute('d', path);
  }
  for (const time of [data.media.actStart, data.media.actStart + span / 2, data.media.duration]) {
    grid.append(svg('text', { x: xAt(time), y: 157, 'text-anchor': time === data.media.actStart ? 'start' : time === data.media.duration ? 'end' : 'middle' }, sourceTime(data, time).toFixed(1)));
  }
  const eventDots = data.events.map(event => {
    const arm = event.arm === 'Left' ? 0 : 1;
    const dot = svg('circle', { cx: xAt(event.trigger), cy: yAt(event.triggerHeights[arm], arm), r: 3.4, class: 'demo-event-dot demo-arm-' + arm });
    dot.append(svg('title', {}, noteName(event) + ' registered · ' + event.sourceTrigger.toFixed(2) + ' s'));
    find('.demo-chart-events').append(dot);
    return dot;
  });
  const reveal = find('#demo-motion-reveal rect'), cursor = find('.demo-chart-cursor');
  const heads = [...hero.querySelectorAll('.demo-chart-head')];
  let ready = false, failed = false, inView = true, wantsPlay = !reduced.matches;
  let frameId = null, lastSignature = '', geometry = null, lastTime = 0;
  const detail = data.actDetail;
  const spotlight = find('.demo-act-spotlight');
  const [regionX, regionY, regionWidth, regionHeight] = detail.highlightRegion;
  const hole = find('.demo-act-focus-hole');
  for (const [name, value] of Object.entries({ x: regionX, y: regionY, width: regionWidth, height: regionHeight })) hole.setAttribute(name, value);
  const right = regionX + regionWidth - 3, bottom = regionY + regionHeight, left = regionX + 3, corner = 32;
  find('.demo-act-focus-corners').setAttribute('d',
    `M${left},${regionY + corner} V${regionY} H${left + corner} M${right - corner},${regionY} H${right} V${regionY + corner} ` +
    `M${left},${bottom - corner} V${bottom} H${left + corner} M${right - corner},${bottom} H${right} V${bottom - corner}`);
  const actX = t => 40 + Math.max(0, Math.min(4.5, t)) / 4.5 * 426;
  const actY = z => 120 - (z - data.motion.range[0]) / (data.motion.range[1] - data.motion.range[0]) * 104;
  const actGrid = find('.demo-act-grid');
  for (const z of [84, 90, 96]) {
    actGrid.append(svg('line', { x1: 40, x2: 466, y1: actY(z), y2: actY(z) }));
    actGrid.append(svg('text', { x: 30, y: actY(z) + 4, 'text-anchor': 'end' }, z));
  }
  for (const t of [0, 1.5, 3, 4.5]) actGrid.append(svg('text', { x: actX(t), y: 146, 'text-anchor': t === 4.5 ? 'end' : 'start' }, t + ' s'));
  for (const [selector, column] of [['.demo-act-reference', 1], ['.demo-act-actual', 2]]) {
    find(selector).setAttribute('d', detail.samples.map((row, i) => (i ? 'L' : 'M') + actX(row[0]).toFixed(2) + ',' + actY(row[column]).toFixed(2)).join(' '));
  }
  const jointReadouts = Array.from({ length: 6 }, (_, i) => {
    const row = document.createElement('div');
    const title = document.createElement('dt'); title.textContent = 'J' + (i + 1);
    const value = document.createElement('dd'); row.append(title, value); find('.demo-joints dl').append(row);
    return value;
  });
  function updateAct(state) {
    if (state.phase !== 'focus') return;
    const time = state.localTime, x = actX(time);
    // Nearest post-step sample, not a wall-clock counter or a simulated trace.
    const row = detail.samples[Math.max(0, Math.min(detail.samples.length - 1, Math.round(time * detail.sampleHz)))];
    find('#act-reveal rect').setAttribute('width', x - 40);
    const cursor = find('.demo-act-cursor'); cursor.setAttribute('x1', x); cursor.setAttribute('x2', x);
    const dot = find('.demo-act-event');
    dot.style.display = state.focusConfirmed ? '' : 'none';
    dot.setAttribute('cx', actX(detail.trigger)); dot.setAttribute('cy', actY(data.events[0].triggerHeights[1]));
    find('.demo-act-status').textContent = state.focusReleased ? 'Released' : state.focusConfirmed ? 'Registered · waiting for release' : 'Follow the target';
    jointReadouts.forEach((node, i) => node.textContent = row[3 + i].toFixed(1) + ' / ' + row[9 + i].toFixed(1));
    const target = find('.demo-act-target');
    target.style.left = (geometry.x + detail.target[0] * geometry.scale) + 'px';
    target.style.top = (geometry.y + detail.target[1] * geometry.scale) + 'px';
    target.dataset.confirmed = String(state.focusConfirmed);
  }
  const format = seconds => String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(Math.floor(seconds % 60)).padStart(2, '0');

  function measure() {
    const box = scene.getBoundingClientRect(), root = hero.getBoundingClientRect();
    const sourceWidth = video.videoWidth || data.media.width, sourceHeight = video.videoHeight || data.media.height;
    const css = getComputedStyle(video);
    const scale = (css.objectFit === 'contain' ? Math.min : Math.max)(box.width / sourceWidth, box.height / sourceHeight);
    const position = css.objectPosition.split(' ').map(value => parseFloat(value) / 100);
    geometry = { scale, x: (box.width - sourceWidth * scale) * position[0], y: (box.height - sourceHeight * scale) * position[1],
      sceneX: box.left - root.left, sceneY: box.top - root.top };
    connection.setAttribute('viewBox', '0 0 ' + root.width + ' ' + root.height);
    focus.style.setProperty('--focus-size', Math.max(18, 70 * scale) + 'px');
    Object.assign(spotlight.style, { left: geometry.x + 'px', top: geometry.y + 'px', width: sourceWidth * scale + 'px', height: sourceHeight * scale + 'px' });
  }

  function connect(state) {
    if (!geometry) return;
    const event = state.acting ? data.events[state.active] : data.events.find(item => state.time >= item.observe && state.time < item.observeEnd);
    const intent = find('.demo-intent-link'), outcome = find('.demo-outcome-link');
    intent.dataset.active = outcome.dataset.active = 'false';
    focus.dataset.active = String(Boolean(!state.acting && event));
    connection.dataset.active = String(state.acting);
    if (event) {
      focus.style.left = (geometry.x + event.target[0] * geometry.scale) + 'px';
      focus.style.top = (geometry.y + event.target[1] * geometry.scale) + 'px';
    }
    if (!state.acting) return;
    const root = hero.getBoundingClientRect(), windowBox = viewport.getBoundingClientRect();
    const chart = find('.demo-chart');
    const matrix = chart.getScreenCTM();
    if (!matrix) return;
    const stacked = matchMedia('(max-width: 760px)').matches;
    const pointAt = (time, height, arm) => {
      const point = new DOMPoint(xAt(time), yAt(height, arm)).matrixTransform(matrix);
      return { x: point.x - root.left, y: point.y - root.top };
    };
    const cardAt = index => {
      const box = cards[index].getBoundingClientRect();
      if (box.right <= windowBox.left + 8 || box.left >= windowBox.right - 8) return null;
      return { x: Math.max(windowBox.left + 12, Math.min(box.left + box.width / 2, windowBox.right - 12)) - root.left,
        top: box.top - root.top, bottom: box.bottom - root.top };
    };
    const labelAt = (group, x, y) => {
      const label = group.querySelector('text');
      label.setAttribute('x', x); label.setAttribute('y', y);
    };
    if (event) {
      const card = cardAt(state.active), arm = event.arm === 'Left' ? 0 : 1;
      if (card) {
        const point = pointAt(state.time, heightsAt(state.time)[arm], arm);
        const startY = stacked ? card.bottom + 3 : card.top - 6;
        const lane = stacked ? windowBox.bottom - root.top - 9 : Math.min(startY, point.y) - 30;
        const right = root.width - 9;
        const path = stacked
          ? `M${card.x},${startY} V${lane} H${right - 8} Q${right},${lane} ${right},${lane + 8} V${point.y - 8} Q${right},${point.y} ${right - 8},${point.y} H${point.x}`
          : `M${card.x},${startY} C${card.x},${lane} ${point.x},${lane} ${point.x},${point.y}`;
        intent.dataset.active = 'true';
        intent.style.color = getComputedStyle(hero).getPropertyValue(arm ? '--demo-right' : '--demo-left');
        const line = find('.demo-connection-line');
        line.setAttribute('d', path);
        const origin = find('.demo-connection-origin'), end = find('.demo-connection-target');
        origin.setAttribute('cx', card.x); origin.setAttribute('cy', startY);
        end.setAttribute('cx', point.x); end.setAttribute('cy', point.y);
        const midpoint = line.getPointAtLength(line.getTotalLength() * 0.45);
        labelAt(intent, stacked ? (card.x + right) / 2 : midpoint.x, stacked ? lane - 6 : midpoint.y - 8);
      }
    }
    // Actual environment events return to memory. The last receipt persists;
    // only its travelling pulse lasts 0.45 media seconds, including after release.
    const index = state.completed - 1, confirmed = data.events[index];
    const card = confirmed && cardAt(index);
    if (card) {
      const arm = confirmed.arm === 'Left' ? 0 : 1;
      const point = pointAt(confirmed.trigger, confirmed.triggerHeights[arm], arm);
      const lane = card.bottom + 14;
      const channel = stacked ? 9 : windowBox.right - root.left + 8;
      const path = `M${point.x},${point.y} H${channel} V${lane} H${card.x} V${card.bottom + 3}`;
      const line = find('.demo-outcome-line'), pulse = find('.demo-outcome-pulse');
      outcome.dataset.active = 'true';
      outcome.dataset.step = String(index + 1);
      line.setAttribute('d', path);
      labelAt(outcome, (card.x + channel) / 2, lane - 5);
      const age = state.time - confirmed.trigger;
      const moving = !reduced.matches && age >= 0 && age < 0.45;
      pulse.style.display = moving ? '' : 'none';
      if (moving) {
        const position = line.getPointAtLength(line.getTotalLength() * age / 0.45);
        pulse.setAttribute('cx', position.x); pulse.setAttribute('cy', position.y);
      }
    }
  }

  function heightsAt(time) {
    let low = 0, high = samples.length - 1;
    while (low < high) {
      const middle = Math.floor((low + high) / 2);
      if (samples[middle][0] < time) low = middle + 1; else high = middle;
    }
    const next = samples[low], previous = samples[Math.max(0, low - 1)];
    const weight = Math.max(0, Math.min(1, (time - previous[0]) / (next[0] - previous[0] || 1)));
    return [1, 2].map(arm => previous[arm] + weight * (next[arm] - previous[arm]));
  }

  function capture(state) {
    const ghost = find('.demo-capture');
    const index = state.captured - 1, event = data.events[index];
    const age = event ? (state.time - event.observe) / 0.32 : -1;
    ghost.hidden = reduced.matches || state.phase !== 'observe' || age < 0 || age >= 1;
    if (ghost.hidden || !geometry) return;
    const root = hero.getBoundingClientRect();
    const card = cards[index].querySelector('img').getBoundingClientRect();
    const [cx, cy, cw, ch] = data.keyboard.snapshotCrop;
    const from = [geometry.sceneX + geometry.x + cx * geometry.scale, geometry.sceneY + geometry.y + cy * geometry.scale, cw * geometry.scale, ch * geometry.scale];
    const to = [card.left - root.left, card.top - root.top, card.width, card.height];
    const progress = age * age * (3 - 2 * age);
    if (ghost.getAttribute('src') !== event.snapshot) ghost.src = event.snapshot;
    ['left', 'top', 'width', 'height'].forEach((property, i) => ghost.style[property] = (from[i] + (to[i] - from[i]) * progress) + 'px');
    ghost.style.opacity = String(Math.min(1, (1 - age) * 8) * state.sceneOpacity);
  }

  function updateChart(state) {
    const x = Math.max(plot.left, Math.min(plot.right, xAt(state.time)));
    reveal.setAttribute('width', x - plot.left);
    cursor.setAttribute('x1', x); cursor.setAttribute('x2', x);
    heightsAt(state.time).forEach((height, arm) => { heads[arm].setAttribute('cx', x); heads[arm].setAttribute('cy', yAt(height, arm)); });
    eventDots.forEach((dot, index) => dot.style.display = state.acting && data.events[index].trigger <= state.time ? '' : 'none');
  }

  function sync(time = video.currentTime, force = false) {
    if (failed) return;
    const state = presentationAt(data, time);
    // Keep the decoded frame visible during chapter seeks and automatic cuts.
    // Seeking to an edit boundary must not land on an artificial black frame.
    hero.style.setProperty('--scene-opacity', 1);
    const signature = [state.phase, state.captured, state.completed, state.released].join(':');
    if (signature !== lastSignature || force) {
      lastSignature = signature;
      hero.dataset.phase = state.phase;
      hero.dataset.registered = String(state.registered);
      hero.dataset.complete = String(state.complete);
      motion.hidden = !state.acting;
      find('.demo-workspace').hidden = state.phase === 'focus';
      find('.demo-act-workspace').hidden = state.phase !== 'focus';
      find('.demo-act-target').hidden = state.phase !== 'focus';
      spotlight.toggleAttribute('hidden', state.phase !== 'focus');
      find('.demo-act-caption').hidden = state.phase !== 'focus';
      sceneButtons.forEach(button => button.setAttribute('aria-current', String(button.dataset.demoPhase === state.phase)));
      const active = data.events[state.active];
      find('.demo-stage').firstChild.textContent = state.acting ? 'ACT ' : 'MIND ';
      find('.demo-title').textContent = state.phase === 'focus' ? 'Follow the trajectory. Make precise contact.' : state.complete ? 'Sequence complete.' : state.acting ? 'Guided by intent. Updated by outcomes.' : 'Remember the order.';
      find('.demo-count').textContent = (state.acting ? state.completed : state.captured) + ' / ' + data.events.length;
      find('.demo-memory-footer').hidden = !state.acting;
      find('.demo-step').textContent = state.complete ? '12 / 12 confirmed' : state.acting ? 'Step ' + (state.active + 1) + ' / 12 · ' + (state.registered ? 'Waiting for release' : 'Target ' + noteName(active)) : 'Watch · Remember';
      find('.demo-feedback').textContent = (state.completed ? '✓ Registered · ' : '') + (data.events.length - state.completed) + ' remaining';
      find('.demo-memory-empty').hidden = state.captured > 0;
      cards.forEach((card, index) => {
        card.hidden = index >= state.captured || (!state.acting && (index < memoryFirst || index > memoryLast));
        card.dataset.completed = String(index < state.completed);
        card.dataset.active = String(index === state.active);
        card.dataset.capturing = String(!state.acting && index === state.captured - 1);
        card.setAttribute('aria-current', index === state.active ? 'step' : 'false');
        card.querySelector('.demo-card-status').textContent = index < state.completed ? '✓' : index === state.active ? 'NEXT' : String(index + 1).padStart(2, '0');
        card.setAttribute('aria-label', 'Step ' + (index + 1) + ', ' + noteName(data.events[index]) + (index < state.completed ? ', confirmed' : index === state.active ? ', current target' : ''));
      });
      const selected = state.acting ? Math.min(state.released, cards.length - 1) : state.captured - 1;
      if (selected >= 0) {
        const card = cards[selected];
        viewport.scrollLeft = Math.max(0, card.offsetLeft - strip.offsetLeft - (viewport.clientWidth - card.offsetWidth) / 2);
      } else viewport.scrollLeft = 0;
      find('.demo-phase-status').textContent = state.phase === 'focus' ? 'Act. Isolated right-arm action; sequence progress is unchanged.' : (state.acting ? 'Mind and Act' : 'Demonstration') + ' · ' + find('.demo-step').textContent + ' · ' + find('.demo-feedback').textContent;
      measure();
    }
    // Entry is media-timed too: pause, reverse seeks and loop resets stay exact.
    cards.forEach((card, index) => {
      const age = Math.max(0, Math.min(1, (state.time - data.events[index].observe) / 0.24));
      card.style.setProperty('--entry', reduced.matches ? 1 : age);
    });
    connect(state);
    capture(state);
    updateChart(state);
    updateAct(state);
    find('.demo-speed').textContent = (state.sourceSpeed * video.playbackRate).toFixed(2).replace(/\.?0+$/, '') + '× source speed';
    play.setAttribute('aria-label', video.paused ? 'Play demo' : 'Pause demo');
    play.setAttribute('aria-pressed', String(!video.paused));
    lastTime = state.presentationTime;
  }
  function cancelFrame() {
    if (frameId !== null) {
      if ('cancelVideoFrameCallback' in video) video.cancelVideoFrameCallback(frameId);
      else cancelAnimationFrame(frameId);
      frameId = null;
    }
  }
  function scheduleFrame() {
    if (frameId !== null || video.paused || video.ended) return;
    const tick = (_, metadata) => { frameId = null; sync(metadata ? metadata.mediaTime : video.currentTime); scheduleFrame(); };
    frameId = 'requestVideoFrameCallback' in video ? video.requestVideoFrameCallback(tick) : requestAnimationFrame(tick);
  }
  async function resume() {
    if (!ready || failed || !wantsPlay || !inView || document.hidden) return;
    try { await video.play(); } catch { wantsPlay = false; sync(); }
  }
  function initialize() {
    if (ready || failed) return;
    ready = true;
    video.defaultPlaybackRate = data.media.playbackRate;
    video.playbackRate = data.media.playbackRate;
    video.currentTime = 0;
    play.disabled = false;
    sceneButtons.forEach(button => button.disabled = false);
    sync(video.currentTime, true);
    resume();
  }
  play.addEventListener('click', () => { wantsPlay = video.paused; if (wantsPlay) resume(); else video.pause(); });
  sceneButtons.forEach(button => button.addEventListener('click', () => {
    // Retire the previous phase's queued frame before seeking to the new one.
    // The seeked event schedules the next callback once that frame is decoded.
    cancelFrame();
    const time = data.presentation.segments.find(segment => segment.phase === button.dataset.demoPhase).start;
    video.currentTime = time;
    sync(time, true);
  }));
  video.addEventListener('loadedmetadata', initialize);
  video.addEventListener('seeking', () => { cancelFrame(); sync(video.currentTime, true); });
  video.addEventListener('seeked', () => { sync(video.currentTime, true); scheduleFrame(); });
  video.addEventListener('play', () => { sync(); scheduleFrame(); });
  video.addEventListener('pause', () => { cancelFrame(); sync(); });
  video.addEventListener('timeupdate', () => { if (frameId === null || video.paused || video.currentTime < lastTime) sync(); });
  video.addEventListener('ratechange', () => sync());
  video.addEventListener('error', () => {
    failed = true; wantsPlay = false; cancelFrame();
    hero.style.setProperty('--scene-opacity', 1);
    play.disabled = true;
    sceneButtons.forEach(button => button.disabled = true);
    find('.demo-title').textContent = 'Demo unavailable.';
    find('.demo-feedback').textContent = 'Open the full demonstration in Tasks below.';
    find('.demo-phase-status').textContent = 'Demo unavailable. Open the full demonstration in Tasks below.';
    connection.dataset.active = focus.dataset.active = 'false';
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) video.pause(); else resume(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting; if (!inView) video.pause(); else resume();
  }).observe(hero);
  reduced.addEventListener('change', () => { if (reduced.matches) { wantsPlay = false; video.pause(); } sync(); });
  viewport.addEventListener('scroll', () => connect(presentationAt(data, lastTime)), { passive: true });
  if ('ResizeObserver' in window) new ResizeObserver(() => { measure(); sync(video.currentTime, true); }).observe(hero);
  else window.addEventListener('resize', () => { measure(); sync(video.currentTime, true); });
  if (video.readyState >= 1) initialize(); else { measure(); sync(0, true); }
})();
