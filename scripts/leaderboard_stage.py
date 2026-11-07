"""Leaderboard hero: the lunar campus under a wide sky, with the Earth on the horizon and the Moon above.
Each reported end-to-end model launches from the Earth's surface (0) straight toward the Moon's surface
(100, every case solved) and stops at the fraction of the way given by its Overall score (plain mean
over all 30 tasks, Clean setting). Launch sites run left to right in release order; contours mark 25,
50 and 75 percent of every route.

Mind, Act and Mind2Act scores and the Random setting are columns in the tables below.

Until three end-to-end results are published, the route shows anonymous placeholder entries
(PREVIEW), captioned as placeholders, together with the first release date and batch.
"""
import math
from datetime import date
from html import escape

# One station per suite (see media/leaderboard-motion/scene.js). Labels name the dimension only.
# x, y: the label's bottom anchor above the arm, in v3 artwork units (1983 x 793, SKY less sky than v4,
# mapped to the corrected view by _view); align: which
# edge of the label sits on x, so labels near the crop edge stay inside the stage.
STATIONS = [
    # (slug, index, name, gist, shoulder pivot x/y on the 1983x793 artwork (scene.js S), placement, leader length)
    ('mind', '01', 'Mind', 'memory and decisions', 436, 383, 'start', 58),
    ('mind2act', '03', 'Mind2Act', 'reasoning and execution together', 954, 594, 'side', 28),
    ('act', '02', 'Act', 'physical execution', 1681, 400, 'end', 52),
]


def stations():
    """HUD tags: each dimension hangs on a leader line whose beacon sits on the shoulder of the arm illustrating it."""
    items = ''.join(
        f'<a class="lb-station lb-station--{slug} lb-station--{place}" href="benchmark.html#suite-{slug}" '
        f'style="{_pct(*_view(x, y + SKY))};--lead:{lead * ZOOM / 10.53:.2f}cqh">'
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


# Geometry of leaderboard-lunar-campus-v5.webp (v4 with the Earth enhanced, scripts/enhance_earth.py) in
# artwork units (1983 x 1053): v3 with SKY units of sky
# inserted between the Moon and the Earth (scripts/extend_lunar_sky.py), so v3 y + SKY = v4 y.
W, H, SKY = 1983, 1053, 260
# The painted camera is rolled: the Earth's horizon falls about 2.8 degrees to the right, so its crest
# sits off the left edge and the Earth looks tilted. The page turns the art (still and loop) back by
# ROLL about its centre and enlarges it by ZOOM to cover the corners (.lb-stage-art in
# leaderboard-stage.css). Everything below is laid out in that corrected view, where the horizon is a
# level, symmetric arc.
ROLL, ZOOM = 2.8, 1.035
# The horizon on v4, fitted to a parabola from x 360 to 1840: y = A x^2 + B x + C, artwork units.
HORIZON_FIT = (1.8239e-05, 1.31081e-02, 528.449)
MOON_ART = ((1698.5, -369.5), 590.0)         # the Moon's centre and radius on v4
LAUNCH = (640, 1460)                         # launch sites along the horizon, clear of the Mind and Act labels
LANDING = (1290, 1740)                       # landing sites along the Moon's visible lower limb


def _view(x, y):
    """Artwork point -> corrected view point (turned by -ROLL about the centre, scaled by ZOOM)."""
    a = math.radians(ROLL)
    dx, dy = x - W / 2, y - H / 2
    return (W / 2 + ZOOM * (dx * math.cos(a) + dy * math.sin(a)),
            H / 2 + ZOOM * (-dx * math.sin(a) + dy * math.cos(a)))


_HZ = sorted(_view(x, HORIZON_FIT[0] * x * x + HORIZON_FIT[1] * x + HORIZON_FIT[2]) for x in range(-200, 2201, 25))
MOON = (*_view(*MOON_ART[0]), MOON_ART[1] * ZOOM)   # centre and radius of the Moon's disc in view


def _earth(x):
    """The Earth's horizon at view x."""
    for (x0, y0), (x1, y1) in zip(_HZ, _HZ[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return _HZ[-1][1]


def _limb(x):
    """The Moon's surface (its lower limb) at view x."""
    cx, cy, r = MOON
    return x, cy + (r * r - (x - cx) ** 2) ** .5


def _ray(t):
    """Route t in [0, 1]: a flight from a launch site on the Earth's horizon to a landing site on the
    Moon's surface, both spread left to right. It climbs straight up first and then turns toward the
    Moon, sampled by arc length so a fraction of the list is that fraction of the distance flown."""
    ex = LAUNCH[0] + (LAUNCH[1] - LAUNCH[0]) * t
    (ex, ey), (lx, ly) = (ex, _earth(ex) - 6), _limb(LANDING[0] + (LANDING[1] - LANDING[0]) * t)
    c1, c2 = (ex, ey - .62 * (ey - ly)), (lx - .35 * (lx - ex), ly + .12 * (ey - ly))
    pts = []
    for k in range(121):
        u = k / 120
        v = 1 - u
        pts.append((v ** 3 * ex + 3 * v * v * u * c1[0] + 3 * v * u * u * c2[0] + u ** 3 * lx,
                    v ** 3 * ey + 3 * v * v * u * c1[1] + 3 * v * u * u * c2[1] + u ** 3 * ly))
    lens = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        lens.append(lens[-1] + ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5)
    return pts, lens


def _at(ray, f):
    pts, lens = ray
    d = max(0.0, min(1.0, f)) * lens[-1]
    for i in range(len(pts) - 1):
        if lens[i + 1] >= d:
            u = (d - lens[i]) / ((lens[i + 1] - lens[i]) or 1)
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u
    return pts[-1]


def _path(ray, f0, f1, steps=40):
    return 'M' + ' L'.join('%.1f %.1f' % _at(ray, f0 + (f1 - f0) * k / steps) for k in range(steps + 1))


def _pct(x, y):
    return f'left:{x / W * 100:.3f}%;top:{y / H * 100:.3f}%'


# A small rocket, nose up, 40 x 80; the model's logo sits in the porthole (centre 20, 36).
SHIP = ('<svg class="lb-ship-svg" viewBox="0 0 40 80" focusable="false">'
        '<path class="lb-ship-fin" d="M9 44 L1 58 L1 67 L9 61Z M31 44 L39 58 L39 67 L31 61Z"/>'
        '<path class="lb-ship-hull" d="M20 2 C30 12 31.5 30 31.5 46 L31 63 L9 63 L8.5 46 C8.5 30 10 12 20 2Z"/>'
        '<path class="lb-ship-nose" d="M20 2 C25.5 7.5 28.2 13.5 29.4 19 L10.6 19 C11.8 13.5 14.5 7.5 20 2Z"/>'
        '<path class="lb-ship-fin" d="M18 52 L22 52 L22 66 L18 66Z"/>'
        '<rect class="lb-ship-nozzle" x="12.5" y="63" width="15" height="5" rx="1.5"/></svg>')


def _shot(entries, preview, data, when):
    """entries: (name, score, model or None) in release order, launched left to right. Each model flies
    from the Earth's surface toward the Moon's and stops at the fraction of the way given by its
    Overall score; a dashed line carries on to the Moon. Lines through 25, 50 and 75 percent of every
    route read as altitude contours."""
    n = len(entries)
    lead = max(range(n), key=lambda i: entries[i][1])
    best = entries[lead][1]
    top = set(sorted(range(n), key=lambda i: -entries[i][1])[:3])
    lines, items = [], []
    for i, (name, score, m) in enumerate(entries):
        t = i / max(1, n - 1)
        ray = _ray(t)
        (ex, ey), f = ray[0][0], score / TARGET
        px, py = _at(ray, f)
        keys = ''
        for k in range(4):
            fk = f * k / 3
            (ax, ay), (bx, by) = _at(ray, max(0.0, fk - .01)), _at(ray, min(1.0, fk + .01))
            keys += f';--r{k}:{math.degrees(math.atan2(bx - ax, ay - by)):.1f}deg'
            if k < 3:
                kx, ky = _at(ray, fk)
                keys += f';--k{k}x:{(kx - px) / W * 100:.3f};--k{k}y:{(ky - py) / H * 100:.3f}'
        lines.append(f'<path class="lb-shot-trail" d="{_path(ray, 0, f)}" pathLength="1" style="--i:{i};--c:{HUES[i % len(HUES)]}"/>'
                     f'<path class="lb-shot-rest{" is-lead" if i == lead else ""}" d="{_path(ray, f, 1)}" style="--i:{i}"/>'
                     f'<circle class="lb-shot-pad" cx="{ex:.1f}" cy="{ey:.1f}" r="4" style="--i:{i}"/>')
        badge = _icon(m, 28) if m else f'<span class="lb-shot-mono">{escape(name.split()[-1][:2])}</span>'
        href = f'models/{escape(m["id"])}.html' if m else '#board-e2e'
        cls = 'lb-shot-model' + (' is-lead' if i == lead else '') + (' is-top' if i in top else '')
        items.append(f'<li class="{cls}" style="{_pct(px, py)};--i:{i};--c:{HUES[i % len(HUES)]}{keys}">'
                     f'<a href="{href}" title="{escape(name)} · Overall {score:.1f}" aria-label="{escape(name)}: Overall {score:.1f}{" (placeholder)" if preview else ""}">'
                     f'<span class="lb-ship" aria-hidden="true"><span class="lb-ship-body">{SHIP}<span class="lb-ship-flame"></span>'
                     f'<span class="lb-shot-badge">{badge}</span></span></span>'
                     f'<span class="lb-shot-label"><span>{escape(name)}</span><b>{score:.1f}</b>'
                     + (f'<small><i>{TARGET - score:.1f}</i> to the Moon</small>' if i == lead else '') + '</span></a></li>')
    # Contours through the same fraction of every route, extended a little past the outermost routes.
    contours = ''
    for v in (25, 50, 75):
        pts = [_at(_ray(k / 40), v / TARGET) for k in range(0, 41)]
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        lx, ly = pts[0]
        contours += f'<path class="lb-shot-contour" d="{d}"/><text class="lb-shot-contour-label" x="{lx - 10:.1f}" y="{ly + 4:.1f}">{v}</text>'
    # The two surfaces: the Earth's horizon under the launch sites, the Moon's limb above the routes.
    cx, cy, r = MOON
    moon = f'M{cx - (r * r - (cy + 0) ** 2) ** .5 + 1:.1f} 0 A{r} {r} 0 0 0 {W} {cy + (r * r - (W - cx) ** 2) ** .5:.1f}'
    first = ''
    if preview:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        first = ('<p class="lb-shot-note"><span>Preview · placeholder models and scores, <strong>not results</strong></span>'
                 '<span class="lb-shot-first">First results <strong>' + escape(when) + '</strong>'
                 + ''.join(f'<span title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 18)}</span>' for m in batch)
                 + '</span></p>')
    (ex0, ey0) = (1850, _earth(1850) + 24)       # on the ocean right of the Act arm, clear of the tags
    mx0, my0 = _limb(1620)
    return (f'<div class="lb-shot{" lb-shot--preview" if preview else ""}" style="--n:{n};--lead:{lead}">'
            f'<svg class="lb-shot-svg" viewBox="0 0 {W} {H}" aria-hidden="true">'
            f'<path class="lb-shot-surface lb-shot-surface--moon" d="{moon}"/>'
            f'<g class="lb-shot-contours">{contours}</g><g class="lb-shot-routes">{"".join(lines)}</g></svg>'
            f'<span class="lb-shot-tag lb-shot-tag--earth" style="{_pct(ex0, ey0)}"><b>0</b>Earth surface</span>'
            f'<span class="lb-shot-tag lb-shot-tag--moon" style="{_pct(mx0, my0 - 62)}"><b>{TARGET}</b>Moon surface<small>every case solved</small></span>'
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
             '<p class="lb-stage-sub">Every model launches from the Earth toward the Moon. How far it gets '
             'is its Overall score; the Moon\'s surface, 100, is every case solved.</p>'
             f'{note}</div>'
             + ('<div class="lb-stage-controls"><p class="lb-stage-metric">VLA / WAM · Clean · Overall score</p></div>' if not preview else '')
             + '</div><div class="lb-stage-visual"><div class="lb-stage-world">'
             + '<div class="lb-stage-scene">'
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v5.webp" alt="Lunar robotics campus under a wide sky, '
             'with the Earth on the horizon and the Moon above." width="1983" height="1053" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v3e.webp" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
    parts.append(stations())
    parts.append(shot)      # on the artwork, so routes start on the Earth's horizon and end on the Moon
    parts.append('</div></div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View both leaderboards ↓</a>'
                 f'<p>Protocol {escape(data["protocol"]["version"])} · Ranked by Overall score · Random reported separately</p>'
                 '<button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button>'
                 '</div></section>')
    return ''.join(parts)
