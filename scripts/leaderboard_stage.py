"""Leaderboard hero: the lunar campus as a moonshot. A route runs from the top of the central launch
tower (0) to the rim of the moon (100, every case solved); each reported end-to-end model sits along
it at the distance given by its Overall score (plain mean over all 30 tasks, Clean setting). Models
launch in release order, and the trail behind them reaches the best score so far.

Mind, Act and Mind2Act scores and the Random setting are columns in the tables below.

Until three end-to-end results are published, the route shows anonymous placeholder entries
(PREVIEW), captioned as placeholders, together with the first release date and batch.
"""
from datetime import date
from html import escape

# One station per suite (see media/leaderboard-motion/scene.js). Labels name the dimension only.
# x, y: the label's bottom anchor above the arm, in artwork units (1983 x 793); align: which
# edge of the label sits on x, so labels near the crop edge stay inside the stage.
STATIONS = [
    # (slug, index, name, gist, shoulder pivot x/y on the 1983x793 artwork (scene.js S), placement, leader length)
    ('mind', '01', 'Mind', 'memory and decisions', 436, 383, 'start', 116),
    ('mind2act', '03', 'Mind2Act', 'reasoning and execution together', 954, 594, 'side', 44),
    ('act', '02', 'Act', 'physical execution', 1681, 400, 'end', 104),
]


def stations():
    """HUD tags: each dimension hangs on a leader line whose beacon sits on the shoulder of the arm illustrating it."""
    items = ''.join(
        f'<a class="lb-station lb-station--{slug} lb-station--{place}" href="benchmark.html#suite-{slug}" '
        f'style="left:{x / 19.83:.2f}%;top:{y / 7.93:.2f}%;--lead:{lead / 7.93:.2f}cqh">'
        f'<span class="lb-station-index">Dimension {num}</span>'
        f'<strong>{name}</strong><span class="lb-station-gist">{escape(gist)}</span></a>'
        for slug, num, name, gist, x, y, place, lead in STATIONS)
    return f'<nav class="lb-stations" aria-label="The three evaluation dimensions">{items}</nav>'


# Placeholder entries for the hero before the first results: anonymous names in release order, with
# illustrative Overall scores that rise unevenly from release to release. Not results of any model.
PREVIEW = [('Model A', 4.8), ('Model B', 9.6), ('Model C', 7.2), ('Model D', 13.9), ('Model E', 11.5),
           ('Model F', 18.7), ('Model G', 16.2), ('Model H', 23.4), ('Model I', 20.8), ('Model J', 28.9),
           ('Model K', 25.7), ('Model L', 33.6), ('Model M', 30.9), ('Model N', 41.2)]
TARGET = 100
# Badge colours for entries without a logo, in release order.
HUES = ['#6f8f97', '#49796b', '#446f86', '#91793d', '#7d5ea8', '#2f7360', '#a2451f', '#4f46b0',
        '#3d6a86', '#9b3f8f', '#5f7d3a', '#8a5a2b', '#2f6386', '#a2451f']


def monogram(name):
    """Two letters for a model without a logo, skipping punctuation (X-WAM -> XW)."""
    return ''.join(ch for ch in name if ch.isalnum())[:2]


def _icon(m, size):
    if m['icon']:
        return f'<img src="{escape(m["icon"])}" width="{size}" height="{size}" alt="">'
    return f'<span class="lb-podium-monogram">{escape(monogram(m["name"]))}</span>'


# The route, in artwork units (1983 x 793): a cubic Bezier from the top of the central launch tower
# (0) to the rim of the moon (100). A model sits at the fraction of the route's length given by its
# Overall score, so distance along the route reads as score.
W, H = 1983, 793
ROUTE = [(993, 300), (990, 150), (1100, 112), (1450, 100)]
LANE = 24          # sideways offset, in artwork units, that keeps neighbouring badges apart
_N = 800


def _bez(t):
    u = 1 - t
    return tuple(u ** 3 * ROUTE[0][k] + 3 * u * u * t * ROUTE[1][k] + 3 * u * t * t * ROUTE[2][k] + t ** 3 * ROUTE[3][k]
                 for k in (0, 1))


_PTS = [_bez(i / _N) for i in range(_N + 1)]
_LEN = [0.0]
for _a, _b in zip(_PTS, _PTS[1:]):
    _LEN.append(_LEN[-1] + ((_b[0] - _a[0]) ** 2 + (_b[1] - _a[1]) ** 2) ** .5)


def _along(frac):
    """Point and unit tangent at a fraction of the route's length."""
    d = max(0.0, min(1.0, frac)) * _LEN[-1]
    i = next((k for k in range(_N) if _LEN[k + 1] >= d), _N - 1)
    (x0, y0), (x1, y1) = _PTS[i], _PTS[i + 1]
    seg = _LEN[i + 1] - _LEN[i] or 1
    u = (d - _LEN[i]) / seg
    return (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u), ((x1 - x0) / seg, (y1 - y0) / seg)


def _pct(x, y):
    return f'left:{x / W * 100:.3f}%;top:{y / H * 100:.3f}%'


def _route(lo, hi, steps=60):
    pts = [_along(lo + (hi - lo) * k / steps)[0] for k in range(steps + 1)]
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)


def _shot(entries, preview, data, when):
    """entries: (name, score, model or None) in release order. Each launches from the tower in turn and
    flies along the route to its score; the trail reaches the best score, a dashed line the moon."""
    n = len(entries)
    lead = max(range(n), key=lambda i: entries[i][1])
    best = entries[lead][1]
    # Alternate sides of the route in score order so close scores do not overlap.
    side = {}
    for k, i in enumerate(sorted((i for i in range(n) if i != lead), key=lambda i: entries[i][1])):
        side[i] = 1 if k % 2 == 0 else -1
    side[lead] = 0
    top = sorted(range(n), key=lambda i: -entries[i][1])[:3]
    items = []
    for i, (name, score, m) in enumerate(entries):
        (x, y), (tx, ty) = _along(score / TARGET)
        nx, ny = -ty, tx                      # unit normal
        fx, fy = x + nx * LANE * side[i], y + ny * LANE * side[i]
        # Flight keyframes: points along the route at 0, 1/3 and 2/3 of this model's distance, relative
        # to where it lands, in percent of the scene (cqw / cqh).
        keys = ''
        for k, f in enumerate((0, 1 / 3, 2 / 3)):
            (px, py), _ = _along(score / TARGET * f)
            keys += f';--k{k}x:{(px - fx) / W * 100:.3f};--k{k}y:{(py - fy) / H * 100:.3f}'
        out_x = nx * side[i]
        place = ('left' if out_x < 0 else 'right') if abs(out_x) > .45 else ('up' if ny * side[i] < 0 else 'down')
        badge = _icon(m, 28) if m else f'<span class="lb-shot-mono">{escape(name.split()[-1][:2])}</span>'
        href = f'models/{escape(m["id"])}.html' if m else '#board-e2e'
        cls = 'lb-shot-model' + (' is-lead' if i == lead else f' is-{place}') + (' is-top' if i in top else '')
        items.append(f'<li class="{cls}" style="{_pct(fx, fy)};--i:{i};--c:{HUES[i % len(HUES)]}{keys}">'
                     f'<a href="{href}" title="{escape(name)} · {score:.1f}" aria-label="{escape(name)}: Overall {score:.1f}{" (placeholder)" if preview else ""}">'
                     f'<span class="lb-shot-badge">{badge}</span>'
                     f'<span class="lb-shot-label"><span>{escape(name)}</span><b>{score:.1f}</b>'
                     + (f'<small>Best so far</small><em><i>{TARGET - score:.1f}</i> to the moon</em>' if i == lead else '') + '</span></a></li>')
    tip = ROUTE[-1]
    first = ''
    if preview:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        first = ('<p class="lb-shot-note"><span>Preview · placeholder models and scores, <strong>not results</strong></span>'
                 '<span class="lb-shot-first">First results <strong>' + escape(when) + '</strong>'
                 + ''.join(f'<span title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 18)}</span>' for m in batch)
                 + '</span></p>')
    return (f'<div class="lb-shot{" lb-shot--preview" if preview else ""}" style="--n:{n};--lead:{lead}">'
            f'<svg class="lb-shot-svg" viewBox="0 0 {W} {H}" aria-hidden="true">'
            f'<path class="lb-shot-route" d="{_route(0, 1)}"/>'
            f'<path class="lb-shot-trail" d="{_route(0, best / TARGET)}" pathLength="1"/>'
            f'<g class="lb-shot-flag" transform="translate({tip[0]} {tip[1]})"><line x1="0" y1="0" x2="0" y2="-34"/>'
            '<path d="M0 -34 L22 -27 L0 -20 Z"/><circle r="5"/></g></svg>'
            f'<span class="lb-shot-pad" style="{_pct(*ROUTE[0])}"><b>0</b> Launch</span>'
            f'<span class="lb-shot-moon" style="{_pct(*tip)}"><b>{TARGET}</b><span>Every case solved<small>The moon is still unclaimed</small></span></span>'
            f'<ol class="lb-shot-models" aria-label="Overall score by model, in release order">{"".join(items)}</ol>'
            f'</div>'), first


def render(data):
    e2e = sorted([m for m in data['models'] if m['track'] == 'e2e' and m['results']],
                 key=lambda m: -m['results']['clean']['overall']['score'])
    first = date.fromisoformat(data['first_release'])
    when = f'{first.day} {first.strftime("%B")}'
    preview = len(e2e) < 3
    if preview:
        shot, note = _shot([(n, sc, None) for n, sc in PREVIEW], True, data, when)
    else:
        in_order = sorted(e2e, key=lambda m: (m.get('release') or '', m['name']))
        shot, note = _shot([(m['name'], m['results']['clean']['overall']['score'], m) for m in in_order], False, data, when)
    parts = ['<section class="lb-stage" id="leaderboard-stage" aria-labelledby="lb-title">'
             '<div class="lb-stage-head"><div><h1 id="lb-title">Leaderboard</h1>'
             '<p class="lb-stage-sub">How far each model has flown toward the moon. '
             'Distance is Overall score; the moon, 100, is every case solved.</p>'
             f'{note}</div>'
             + ('<div class="lb-stage-controls"><p class="lb-stage-metric">VLA / WAM · Clean · Overall score</p></div>' if not preview else '')
             + '</div><div class="lb-stage-visual"><div class="lb-stage-world">'
             + '<div class="lb-stage-scene">'
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v3.webp" alt="Lunar robotics campus with three '
             'demonstration stations around three launch towers." width="1983" height="793" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v3.webp" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
    parts.append(stations())
    parts.append(shot)      # on the artwork, so the route runs from the launch tower to the moon
    parts.append('</div></div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View both leaderboards ↓</a>'
                 f'<p>Protocol {escape(data["protocol"]["version"])} · Ranked by Overall score · Random reported separately</p>'
                 '<button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button>'
                 '</div></section>')
    return ''.join(parts)
