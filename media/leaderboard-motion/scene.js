/* Three stations, one per benchmark suite, on an 8-second loop (artwork units, 1983 × 793).
 *
 * Left  · Mind     (E, duplicate identification): the board marks one item, covers it,
 *                   and the probe weighs the blocks before choosing the matching green one.
 * Front · Mind2Act (CP08, reference-guided construction): a projected reference shows the
 *                   target stack, disappears, and the arm rebuilds it from memory.
 * Right · Act      (FR1, conveyor picking): the arm tracks a parcel on the moving belt,
 *                   picks it in motion and sets it on the collection deck.
 */
const LOOP = 8;
const svg = document.querySelector('#scene'), $ = id => document.getElementById(id), ns = 'http://www.w3.org/2000/svg';
const view = new URLSearchParams(location.search).get('view') || 'full';
if (view !== 'full') svg.setAttribute('viewBox', ({front: '960 520 220 140', left: '470 280 240 190', right: '1460 340 330 170'})[view]);

const smooth = u => u * u * (3 - 2 * u);
const clamp01 = u => Math.max(0, Math.min(1, u));
const ramp = (t, a, b) => smooth(clamp01((t - a) / (b - a)));            // 0 before a, 1 after b
const pulse = (t, a, b, c, d) => ramp(t, a, b) * (1 - ramp(t, c, d));     // fades in a→b, out c→d
function track(keys, t) {                                                 // keys: [time, x, y]
  for (let i = 0; i < keys.length - 1; i++) {
    const [ta, xa, ya] = keys[i], [tb, xb, yb] = keys[i + 1];
    if (t >= ta && t <= tb) { const u = smooth((t - ta) / (tb - ta)); return [xa + (xb - xa) * u, ya + (yb - ya) * u]; }
  }
  return keys[keys.length - 1].slice(1);
}
// Two-link arm: rotate the upper arm about S and carry the forearm and tool to the wrist target.
function solve(arm, p, sign) {
  const [sx, sy] = arm.S, [ex, ey] = arm.E, [wx, wy] = arm.W;
  const l1 = Math.hypot(ex - sx, ey - sy), l2 = Math.hypot(wx - ex, wy - ey), d = Math.hypot(p[0] - sx, p[1] - sy);
  const a = Math.atan2(p[1] - sy, p[0] - sx) + sign * Math.acos(Math.max(-1, Math.min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))));
  const e = [sx + l1 * Math.cos(a), sy + l1 * Math.sin(a)], b = Math.atan2(p[1] - e[1], p[0] - e[0]);
  const deg = r => r * 180 / Math.PI;
  $(arm.upper).setAttribute('transform', `rotate(${deg(a - Math.atan2(ey - sy, ex - sx))} ${arm.S})`);
  $(arm.fore).setAttribute('transform', `translate(${e[0] - ex} ${e[1] - ey}) rotate(${deg(b - Math.atan2(wy - ey, wx - ex))} ${arm.E})`);
  $(arm.tool).setAttribute('transform', `translate(${p[0] - wx} ${p[1] - wy})`);
}

/* Ambient stars and lamps. */
for (let i = 0; i < 22; i++) {
  const e = document.createElementNS(ns, 'circle');
  e.setAttribute('cx', 35 + (i * 167) % 1890); e.setAttribute('cy', 35 + (i * 41) % 190); e.setAttribute('r', 4 + (i % 3) * 2);
  $('stars').append(e);
}
[[483, 730, 26, 4], [737, 767, 38, 4], [1236, 767, 40, 4], [1572, 641, 7, 7], [418, 635, 7, 7], [764, 495, 18, 4], [920, 510, 27, 3], [1158, 508, 20, 3]]
  .forEach(([x, y, width, height]) => {
    const e = document.createElementNS(ns, 'rect');
    for (const [k, v] of Object.entries({x, y, width, height, rx: 2})) e.setAttribute(k, v);
    $('lights').append(e);
  });

/* Left · Mind. The probe tip sits 80 units below the wrist. */
const LEFT = {S: [436, 383], E: [489, 317], W: [580, 364], upper: 'LupperMoving', fore: 'LforeMoving', tool: 'LtoolMoving'};
const tip = (x, y) => [x - 1, y - 80];
const leftKeys = [[0, ...tip(566, 420)], [2.2, ...tip(566, 420)],
  [2.7, ...tip(538, 424)], [3.0, ...tip(538, 428)], [3.25, ...tip(538, 424)],     // weighs the blue block
  [3.7, ...tip(574, 422)], [3.95, ...tip(574, 426)], [4.15, ...tip(574, 422)],   // then the yellow one
  [4.6, ...tip(607, 424)], [4.85, ...tip(607, 439)], [5.15, ...tip(607, 424)],   // and taps green
  [7.2, ...tip(566, 420)], [LOOP, ...tip(566, 420)]];
const covers = [...$('covers').children];
function renderMind(t) {
  solve(LEFT, track(leftKeys, t), -1);
  $('cueRing').setAttribute('opacity', pulse(t, .25, .6, 1.7, 2.0) * (.75 + .25 * Math.sin(t * 9)));
  covers.forEach((c, i) => {
    // All four close at 2.0 s; the triangle reopens when the right block is chosen, the rest at 7.0 s.
    const open = i === 2 ? ramp(t, 4.95, 5.25) : ramp(t, 7.0, 7.4);
    const s = Math.max(.001, ramp(t, 1.95 + i * .06, 2.25 + i * .06) * (1 - open));
    const x = +c.dataset.x, y = +c.dataset.y;
    c.setAttribute('transform', `translate(${x} ${y}) scale(1 ${s}) translate(${-x} ${-y})`);
  });
  const ok = pulse(t, 4.95, 5.25, 6.6, 7.0);
  $('okRing').setAttribute('opacity', ok);
  $('tapRing').setAttribute('opacity', ok * .9);
  $('tapRing').setAttribute('rx', 13 + 4 * ramp(t, 4.9, 5.6));
}

/* Front · Mind2Act. The blue cube follows the wrist while carried. */
const FRONT = {S: [954, 594], E: [1029, 549], W: [1087, 591], upper: 'upperArm', fore: 'foreArm', tool: 'tool'};
const frontKeys = [[0, 1087, 580], [2.0, 1087, 580], [2.3, 1087, 591], [2.55, 1087, 591], [3.15, 1087, 545],
  [3.8, 1042, 545], [4.3, 1042, 570], [4.6, 1042, 570], [5.0, 1042, 552], [5.6, 1042, 570], [5.85, 1042, 570],
  [6.35, 1042, 545], [7.0, 1087, 545], [7.45, 1087, 591], [7.7, 1087, 591], [LOOP, 1087, 580]];
function renderMind2Act(t) {
  const p = track(frontKeys, t);
  solve(FRONT, p, -1);
  const carry = (t >= 2.55 && t < 4.6) || (t >= 5.85 && t < 7.7), stacked = t >= 4.6 && t < 5.85;
  const cube = carry ? [p[0] - 1087, p[1] - 591] : stacked ? [-45, -21] : [0, 0];
  $('movingCube').setAttribute('transform', `translate(${cube})`);
  const lift = carry ? Math.max(0, -cube[1] - (cube[0] < -30 ? 21 : 0)) : 0;
  $('shadow').setAttribute('cx', 1092 + cube[0]);
  $('shadow').setAttribute('rx', 17 + lift * .13);
  $('shadow').setAttribute('opacity', (stacked || cube[0] < -30 ? 0 : .2) - lift * .0015);
  const g = carry ? 0 : 2;
  $('fingerL').setAttribute('transform', `translate(${-g} 0)`);
  $('fingerR').setAttribute('transform', `translate(${g} 0)`);
  // The reference is shown, withdrawn, and shown again in green once the stack matches it.
  const shown = pulse(t, .2, .55, 1.6, 2.0) * (.8 + .2 * Math.sin(t * 7)), check = pulse(t, 4.6, 4.85, 5.35, 5.6);
  $('ghost').setAttribute('opacity', Math.max(shown, check));
  $('ghost').setAttribute('stroke', check > shown ? '#5fae86' : '#7fd0e6');
  $('status').setAttribute('fill', check > .1 ? '#5fae86' : carry ? '#7fb6c8' : '#d4bb75');
}

/* Right · Act. The belt runs right to left; the arm matches the parcel's speed before it grips. */
const RIGHT = {S: [1681, 400], E: [1591, 367], W: [1525, 426], upper: 'RupperMoving', fore: 'RforeMoving', tool: 'RtoolMoving'};
const BELT = {x0: 1757, x1: 1592, speed: 36, grip: 4.0};
const beltY = x => 468 + (x - 1590) * 6 / 167;                         // parcel base on the belt
const parcelX = t => BELT.x0 - BELT.speed * t;
const GRIP_DY = 22;                                                   // wrist above the parcel base when gripping
const rightKeys = (() => {
  const keys = [[0, 1625, 418], [2.4, 1625, 418]];
  for (let t = 2.8; t <= BELT.grip + 1e-9; t += .2) {                  // follow, then descend onto the moving parcel
    const x = parcelX(t), d = clamp01((t - 2.8) / (BELT.grip - 2.8));
    keys.push([t, x, 418 + (beltY(x) - GRIP_DY - 418) * smooth(d)]);
  }
  return keys.concat([[4.6, 1602, 410], [5.3, 1548, 410], [5.7, 1548, 449 - GRIP_DY], [5.9, 1548, 449 - GRIP_DY],
    [6.3, 1556, 412], [7.4, 1625, 418], [LOOP, 1625, 418]]);
})();
const rollers = [[1591, 476], [1612, 478], [1634, 480], [1654, 482], [1676, 484], [1698, 486], [1717, 489]];
rollers.forEach(() => { const e = document.createElementNS(ns, 'path'); $('rollers').append(e); });
for (let i = 0; i < 16; i++) { const e = document.createElementNS(ns, 'path'); $('belt').append(e); }
function renderAct(t) {
  const p = track(rightKeys, t);
  solve(RIGHT, p, 1);
  let x, y, o = 1;
  if (t < BELT.grip) { x = parcelX(t); y = beltY(x); o = ramp(t, 0, .35); }
  else if (t < 5.9) { x = p[0]; y = p[1] + GRIP_DY; }
  else { x = 1548; y = 449; o = 1 - ramp(t, 6.7, 7.4); }               // collected
  $('parcel').setAttribute('transform', `translate(${x} ${y})`);
  $('parcel').setAttribute('opacity', o);
  $('tapRingR').setAttribute('opacity', pulse(t, 5.85, 6.05, 6.5, 6.9) * .9);
  // Roller spokes turn and belt marks drift with the belt speed (36 units/s).
  [...$('rollers').children].forEach((e, i) => {
    const [cx, cy] = rollers[i], a = -BELT.speed * t / 4 + i;
    e.setAttribute('d', `M${cx} ${cy}l${(3 * Math.cos(a)).toFixed(2)} ${(3 * Math.sin(a)).toFixed(2)}`);
  });
  [...$('belt').children].forEach((e, i) => {
    const span = BELT.x0 - BELT.x1 + 12, gx = BELT.x1 + ((i * 12 - BELT.speed * t) % span + span) % span;
    const y0 = beltY(gx) - 2.2;
    e.setAttribute('d', gx < BELT.x0 - 4 ? `M${gx.toFixed(1)} ${y0.toFixed(1)}h4` : '');
  });
}

window.renderFrame = function (time) {
  const t = ((time % LOOP) + LOOP) % LOOP;
  renderMind(t); renderMind2Act(t); renderAct(t);
  [...$('stars').children].forEach((e, i) => e.setAttribute('opacity', .2 + .3 * (1 + Math.sin(t * Math.PI / 4 + i))));
  [...$('lights').children].forEach((e, i) => e.setAttribute('opacity', .25 + .45 * (1 + Math.sin(t * Math.PI / 4 - i * .8)) / 2));
  $('phase').textContent = `${t.toFixed(1)} s`;
};

let paused = false, last = performance.now(), elapsed = 0;
function frame(now) { if (!paused) elapsed += (now - last) / 1000; last = now; if (!window.manualFrames) renderFrame(elapsed); requestAnimationFrame(frame); }
$('pause').onclick = () => { paused = !paused; $('pause').textContent = paused ? 'Play animation' : 'Pause animation'; };
renderFrame(0);
requestAnimationFrame(frame);
