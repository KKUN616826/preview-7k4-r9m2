/* Coming-soon improvement loop: evaluate → diagnose → prescribe → train, three rounds per cycle.
   Every frame is derived from the cycle time, so pausing, resizing and reduced motion stay consistent. */
(() => {
  'use strict';
  const root = document.getElementById('model-diagnostics');
  const fig = root?.querySelector('.lp-figure');
  if (!fig) return;
  const $ = s => fig.querySelector(s), $$ = s => [...fig.querySelectorAll(s)];
  const svg = $('.lp-wires'), forward = $('.lp-path--forward'), back = $('.lp-path--return'), tokens = $('.lp-tokens');
  const nodes = $$('.lp-node'), chips = $$('.lp-suites li'), cells = $$('.lp-data i');
  const skills = {mind: $('.lp-skill--mind'), act: $('.lp-skill--act'), mind2act: $('.lp-skill--mind2act')};
  const toggle = root.querySelector('.lp-toggle');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const NS = 'http://www.w3.org/2000/svg';
  const NAMES = {mind: 'Mind', act: 'Act', mind2act: 'Mind2Act'};
  const COLORS = {mind: '#49796b', act: '#446f86', mind2act: '#91793d'};

  // Illustrative abilities before each round, and the view each round's prescription targets.
  const START = {mind: .58, act: .30, mind2act: .36};
  const ROUNDS = [['act', .22], ['mind2act', .2], ['mind', .16]];
  // Each round lasts R seconds; the cycle ends on a short hold that shows the finished profile.
  const R = 5.6, HOLD = 2.4, CYCLE = R * ROUNDS.length + HOLD;
  // The v5 profile after 0, 1, 2 and 3 rounds (letters 1 and 4 set the family): Act data turns a
  // Mind-dominant model Act-dominant (I→E), closed-loop Mind2Act data makes it feedback-driven
  // (J→P), and memory data settles its unstable memory lean on spatial memory (X→N). Tendencies,
  // not scores; the last code is complete, so it earns a nickname.
  const CODES = ['IXTJ', 'EXTJ', 'EXTP', 'ENTP'];
  const TYPES = ['Feedforward Planner', 'Procedural Executor', 'Servo Responder', 'Tuner · Servo Responder'];
  const avatars = $$('.lp-avatar-img'), typeEl = $('.lp-type');
  const codeEls = {card: $('.lp-card .lp-code'), model: $('.lp-profile .lp-code')};
  const shown = {};
  function setCode(where, code, prev) {
    const key = code + '|' + (prev || '');
    if (shown[where] === key) return;
    shown[where] = key;
    codeEls[where].innerHTML = [...code].map((ch, i) => prev && prev[i] !== ch ? `<span class="is-new">${ch}</span>` : `<span>${ch}</span>`).join('');
    codeEls[where].setAttribute('aria-label', `Profile ${code}`);
  }

  const dot = document.createElementNS(NS, 'circle');
  dot.setAttribute('r', 4.5);
  const packets = Array.from({length: 5}, () => {
    const r = document.createElementNS(NS, 'rect');
    r.setAttribute('width', 8); r.setAttribute('height', 8); r.setAttribute('rx', 2);
    return r;
  });
  tokens.append(dot, ...packets);

  let geo = null;
  function layout() {
    const f = fig.getBoundingClientRect();
    const box = el => { const r = el.getBoundingClientRect(); return {l: r.left - f.left, r: r.right - f.left, t: r.top - f.top, b: r.bottom - f.top, cx: (r.left + r.right) / 2 - f.left, cy: (r.top + r.bottom) / 2 - f.top}; };
    const b = nodes.map(box), stacked = b[1].t > b[0].b - 1, rad = 12;
    svg.setAttribute('viewBox', `0 0 ${f.width} ${f.height}`);
    let hops, ret;
    if (!stacked) {
      const y = b[0].cy, low = f.height - 22;
      hops = b.slice(0, -1).map((n, i) => [[n.r, y], [b[i + 1].l, y]]);
      forward.setAttribute('d', `M${b[0].r} ${y}H${b[3].l}`);
      ret = `M${b[3].cx} ${b[3].b}V${low - rad}q0 ${rad} ${-rad} ${rad}H${b[0].cx + rad}q${-rad} 0 ${-rad} ${-rad}V${b[0].b}`;
    } else {
      const x = b[0].l + 28, gx = f.width - 12;
      hops = b.slice(0, -1).map((n, i) => [[x, n.b], [x, b[i + 1].t]]);
      forward.setAttribute('d', hops.map(([p, q]) => `M${p[0]} ${p[1]}V${q[1]}`).join(''));
      ret = `M${b[3].r} ${b[3].cy}H${gx - rad}q${rad} 0 ${rad} ${-rad}V${b[0].cy + rad}q0 ${-rad} ${-rad} ${-rad}H${b[0].r}`;
    }
    back.setAttribute('d', ret);
    geo = {hops, len: back.getTotalLength()};
  }

  const clamp = v => Math.max(0, Math.min(1, v)), ease = u => u * u * (3 - 2 * u);
  const between = (t, a, b) => clamp((t - a) / (b - a));
  const lerp = (p, q, u) => [p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u];

  function render(time, still) {
    if (!geo) layout();
    const c = ((time % CYCLE) + CYCLE) % CYCLE, k = Math.min(ROUNDS.length - 1, Math.floor(c / R)), t = c - k * R;
    const [focus, gain] = ROUNDS[k], trained = t >= 5.0;
    // Abilities after the prescriptions already absorbed this cycle.
    const level = {...START};
    ROUNDS.slice(0, k + (trained ? 1 : 0)).forEach(([s, g]) => { level[s] += g; });
    for (const s in skills) {
      skills[s].querySelector('i').style.setProperty('--v', level[s].toFixed(3));
      skills[s].classList.toggle('is-growing', s === focus && t >= 4.2 && t < 5.6);
    }
    const done = k + (trained ? 1 : 0);
    fig.style.setProperty('--grow', (.82 + .06 * done).toFixed(2));
    fig.querySelector('.lp-round b').textContent = String(k + 1);
    root.style.setProperty('--lp-focus', COLORS[focus]);
    root.style.setProperty('--xp', (.22 + .2 * done).toFixed(2));
    $('.lp-weak b').textContent = NAMES[focus];
    // The card reads the profile at diagnosis time; the model's profile updates once it has trained.
    setCode('card', CODES[k], null);
    const fresh = trained || (k > 0 && t < 1.4);
    setCode('model', CODES[done], fresh && done > 0 ? CODES[done - 1] : null);
    avatars.forEach((a, i) => a.classList.toggle('is-current', i === done));
    if (typeEl.textContent !== TYPES[done]) typeEl.textContent = TYPES[done];
    nodes[0].classList.toggle('is-final', done === CODES.length - 1);

    const step = t < 1.7 ? 1 : t < 2.6 ? 2 : t < 4.0 ? 3 : t < 5.0 ? 4 : 0;
    fig.dataset.step = String(step);
    nodes.forEach((n, i) => n.classList.toggle('is-active', (i === 0 && step === 4) || (i > 0 && i === step)));
    chips.forEach((ch, i) => ch.classList.toggle('is-lit', t >= .9 + i * .25 && t < 4.0));
    const filled = t >= 3.2 && t < 4.0 ? Math.ceil(between(t, 3.2, 3.9) * cells.length) : t >= 4.0 && t < 4.4 ? cells.length : 0;
    cells.forEach((cell, i) => cell.classList.toggle('is-filled', i < filled));

    // Forward token hops node to node; packets of targeted data ride the return path.
    const hop = [[0, .9, 0], [1.7, 2.4, 1], [2.6, 3.2, 2]].find(([a, b]) => t >= a && t <= b + .1);
    dot.style.display = still || !hop ? 'none' : '';
    if (hop && !still) { const [x, y] = lerp(...geo.hops[hop[2]], ease(between(t, hop[0], hop[1]))); dot.setAttribute('cx', x); dot.setAttribute('cy', y); }
    packets.forEach((p, i) => {
      const u = between(t, 4.0 + i * .12, 4.75 + i * .12);
      const show = !still && t >= 4.0 && u < 1;
      p.style.display = show ? '' : 'none';
      if (show) { const pt = back.getPointAtLength(ease(u) * geo.len); p.setAttribute('x', pt.x - 4); p.setAttribute('y', pt.y - 4); }
    });
  }

  let playing = false, userPaused = false, visible = false, elapsed = 0, last = 0, raf = 0;
  function frame(now) {
    elapsed += Math.min(.1, (now - last) / 1000); last = now;
    render(elapsed, false);
    raf = requestAnimationFrame(frame);
  }
  function sync() {
    const run = visible && !document.hidden && !userPaused && !reduced.matches;
    if (run && !playing) { playing = true; last = performance.now(); raf = requestAnimationFrame(frame); }
    if (!run && playing) { playing = false; cancelAnimationFrame(raf); }
    root.dataset.playing = String(playing);
    toggle.hidden = reduced.matches;
    toggle.textContent = userPaused ? 'Play' : 'Pause';
    toggle.setAttribute('aria-pressed', String(userPaused));
    toggle.setAttribute('aria-label', userPaused ? 'Play loop animation' : 'Pause loop animation');
    if (reduced.matches) render(R * 2 + 3.95, true);      // a still of round three with the prescription filled
  }
  toggle.addEventListener('click', () => { userPaused = !userPaused; sync(); });
  reduced.addEventListener('change', sync);
  document.addEventListener('visibilitychange', sync);
  new ResizeObserver(() => { layout(); render(reduced.matches ? R * 2 + 3.95 : elapsed, reduced.matches || !playing); }).observe(fig);
  new IntersectionObserver(e => { visible = e[0].isIntersecting; sync(); }, {threshold: .2}).observe(fig);
  layout();
  render(0, true);
  sync();
})();
