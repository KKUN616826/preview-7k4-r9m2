"""Leaderboard hero: the lunar campus under a wide sky, with the Earth on the horizon and the Moon above.
Each reported end-to-end model launches from the Earth's surface (0) straight toward the Moon's surface
(100, every case solved) and stops at the fraction of the way given by its Overall score (plain mean
over all 30 tasks, Clean setting). The best model launches from the middle and the others alternate
outward by rank, so the rockets stand like a mountain; every route converges on one landing beacon on
the Moon, the summit at 100. Contours mark 25, 50 and 75 percent of every route.

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
LAUNCH = (650, 1540)                         # launch sites along the horizon, clear of the Mind and Act labels
LANDING = (1500, 1620)                       # a narrow landing zone on the Moon's lower limb: every route converges on it
SUMMIT = 1560                               # the beacon at its centre, the 100 every model is heading for


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
    """Route t in [0, 1]: a flight from a launch site on the Earth's horizon (spread left to right) to
    the landing zone on the Moon's surface (narrow, so the routes converge like paths up one peak). It
    climbs straight up first and then turns toward the Moon, sampled by arc length so a fraction of
    the list is that fraction of the distance flown."""
    ex = LAUNCH[0] + (LAUNCH[1] - LAUNCH[0]) * t
    (ex, ey), (lx, ly) = (ex, _earth(ex) - 6), _limb(LANDING[0] + (LANDING[1] - LANDING[0]) * t)
    c1, c2 = (ex, ey - .85 * (ey - ly)), (lx, ly + .15 * (ey - ly))
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


# A chubby pixel rocket in the style of the site's pixel avatars, 16 x 24 cells: k ink, w hull,
# a accent, l porthole glass (the model's logo sits on it, centre 8, 8), g nozzle; rows 18-23 hold two
# flame frames (y, o) that alternate.
_ROCKET = ['.......kk.......', '......kaak......', '.....kaaaak.....', '....kaaaaaak....',
           '...kwwkkkkwwk...', '..kwwkllllkwwk..', '..kwkllllllkwk..', '..kwkllllllkwk..',
           '..kwkllllllkwk..', '..kwkllllllkwk..', '..kwwkllllkwwk..', '..kwwwkkkkwwwk..',
           '..kwwwwwwwwwwk..', '.kakwwwwwwwwkak.', 'kaaakaaaaaakaaak', 'kaak.kkkkkk.kaak',
           'kkk..kggggk..kkk', '......kggk......']
_FLAMES = [['.....yyyyyy.....', '......yooy......', '......oyyo......', '.......oo.......', '.......o........'],
           ['.....yyyyyy.....', '.....yooooy.....', '......oyyo......', '......o..o......', '.......oo.......', '........o.......']]


def _sprite(rows, top=0):
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < 16:
            run = 1
            while x + run < 16 and row[x + run] == row[x]:
                run += 1
            if row[x] != '.':
                out.append(f'<rect class="s{row[x]}" x="{x}" y="{y + top}" width="{run}" height="1"/>')
            x += run
    return ''.join(out)


SHIP = ('<svg class="lb-ship-svg" viewBox="0 0 16 24" shape-rendering="crispEdges" focusable="false">'
        + ''.join(f'<g class="lb-ship-flame lb-ship-flame--{k}">{_sprite(f, 18)}</g>' for k, f in enumerate(_FLAMES))
        + _sprite(_ROCKET) + '</svg>')


def _slots(entries):
    """Launch site t in [0, 1] for each entry: the best score launches a little right of the middle,
    under the landing beacon, and the rest alternate outward by rank (the right flank, where routes
    lean toward the Moon, filling more slowly), with every other pair swapped, so the rockets stand
    like a mountain, highest in the middle, without forming two straight flanks."""
    n = len(entries)
    if n == 1:
        return [.6]
    c = round(.6 * (n - 1))
    order = sorted(range(n), key=lambda k: ((c - k) if k < c else (k - c) * 1.4, k))
    for j in range(3, n - 1, 4):
        order[j], order[j + 1] = order[j + 1], order[j]
    ranked = sorted(range(n), key=lambda i: -entries[i][1])
    # The leader's rocket is larger: widen the two gaps beside its site.
    gaps = [1.5 if k + 1 == c else 2.2 if k == c else 1.0 for k in range(n - 1)]
    at = [sum(gaps[:k]) / sum(gaps) for k in range(n)]
    return {i: at[order[r]] for r, i in enumerate(ranked)}


def _label_sides(points, lead, top):
    """Where each runner-up's score chip goes: above its rocket, or beside it when a neighbour on a
    converging route, or the leader's label, is in the way. Boxes in artwork units at a 1440 px
    stage (a rocket is about 58 x 87, a chip 55 x 25, the leader's label 190 x 80)."""
    def box(x0, y0, x1, y1):
        return (x0, y0, x1, y1)

    def hit(a, b):
        return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

    taken = []
    for i, (x, y) in enumerate(points):
        s = 1.43 if i == lead else 1.0
        taken.append(box(x - 29 * s, y - 29 * s, x + 29 * s, y + 58 * s))
    lx, ly = points[lead]
    taken.append(box(lx - 96, ly - 41 - 85, lx + 96, ly - 41))
    out = {}
    for i in sorted(top - {lead}, key=lambda i: -points[i][1]):
        x, y = points[i]
        for side, b in (('', box(x - 28, y - 58, x + 28, y - 32)),
                        (' is-label-left', box(x - 88, y - 12, x - 33, y + 13)),
                        (' is-label-right', box(x + 33, y - 12, x + 88, y + 13))):
            if not any(hit(b, o) for o in taken):
                break
        else:
            side, b = '', box(x - 28, y - 58, x + 28, y - 32)
        out[i] = side
        taken.append(b)
    return out


def _shot(entries, preview, data, when):
    """entries: (name, score, model or None) in release order; _slots picks the launch sites. Each model flies
    from the Earth's surface toward the Moon's and stops at the fraction of the way given by its
    Overall score; a dashed line carries on to the Moon. Lines through 25, 50 and 75 percent of every
    route read as altitude contours."""
    n = len(entries)
    lead = max(range(n), key=lambda i: entries[i][1])
    best = entries[lead][1]
    top = set(sorted(range(n), key=lambda i: -entries[i][1])[:3])
    lines, items = [], []
    slot = _slots(entries)
    sides = _label_sides([_at(_ray(slot[i]), sc / TARGET) for i, (_, sc, _) in enumerate(entries)], lead, top)
    for i, (name, score, m) in enumerate(entries):
        t = slot[i]
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
        cls = 'lb-shot-model' + (' is-lead' if i == lead else '') + (' is-top' if i in top else '') + sides.get(i, '')
        items.append(f'<li class="{cls}" style="{_pct(px, py)};--i:{i};--c:{HUES[i % len(HUES)]}{keys}">'
                     f'<a href="{href}" title="{escape(name)} · Overall {score:.1f}" aria-label="{escape(name)}: Overall {score:.1f}{" (placeholder)" if preview else ""}">'
                     f'<span class="lb-ship" aria-hidden="true"><span class="lb-ship-body">{SHIP}'
                     f'<span class="lb-shot-badge">{badge}</span></span></span>'
                     f'<span class="lb-shot-label"><span>{escape(name)}</span><b>{score:.1f}</b>'
                     + (f'<small><i>{TARGET - score:.1f}</i> to the Moon</small>' if i == lead else '') + '</span></a></li>')
    # Contours through the same fraction of every route, extended a little past the outermost routes.
    contours = ''
    for v in (25, 50, 75):
        pts = [_at(_ray(k / 40), v / TARGET) for k in range(0, 41)]
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        lx, ly = pts[0]
        contours += f'<path class="lb-shot-contour" d="{d}"/>'
        if v < 75:      # near the summit the routes have converged; the leader's label would cover a 75
            contours += f'<text class="lb-shot-contour-label" x="{lx - 10:.1f}" y="{ly + 4:.1f}">{v}</text>'
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
    # The corridor: the band between the outermost routes, brightening toward the Moon, so the eye runs
    # from the Earth up to the one landing beacon, the summit of the board.
    left, right = _ray(0)[0], _ray(1)[0]
    corridor = ('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in left)
                + ' L' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in reversed(right)) + 'Z')
    sx, sy = _limb(SUMMIT)
    gy0, gy1 = _earth(SUMMIT), sy
    beacon = (f'<radialGradient id="lb-summit-glow"><stop offset="0" stop-color="#fff7e8" stop-opacity=".95"/>'
              f'<stop offset=".35" stop-color="#ffd9b0" stop-opacity=".55"/><stop offset="1" stop-color="#ffd9b0" stop-opacity="0"/></radialGradient>'
              f'<linearGradient id="lb-corridor-fill" gradientUnits="userSpaceOnUse" x1="0" y1="{gy0:.0f}" x2="0" y2="{gy1:.0f}">'
              f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/>'
              f'<stop offset="1" stop-color="#fff1dc" stop-opacity=".72"/></linearGradient>')
    summit = (f'<g class="lb-shot-summit" transform="translate({sx:.1f} {sy:.1f})">'
              f'<circle class="lb-shot-summit-glow" r="110" fill="url(#lb-summit-glow)"/>'
              f'<circle class="lb-shot-summit-pulse" r="17"/><circle class="lb-shot-summit-halo" r="27"/><circle class="lb-shot-summit-ring" r="17"/>'
              f'<circle class="lb-shot-summit-core" r="8"/></g>')
    mx0, my0 = sx, sy
    return (f'<div class="lb-shot{" lb-shot--preview" if preview else ""}" style="--n:{n};--lead:{lead}">'
            f'<svg class="lb-shot-svg" viewBox="0 0 {W} {H}" aria-hidden="true">'
            f'<defs>{beacon}</defs><path class="lb-shot-corridor" d="{corridor}" fill="url(#lb-corridor-fill)"/>'
            f'<path class="lb-shot-surface lb-shot-surface--moon" d="{moon}"/>'
            f'<g class="lb-shot-contours">{contours}</g><g class="lb-shot-routes">{"".join(lines)}</g>{summit}</svg>'
            f'<span class="lb-shot-tag lb-shot-tag--earth" style="{_pct(ex0, ey0)}"><b>0</b>Earth surface</span>'
            f'<span class="lb-shot-tag lb-shot-tag--moon" style="{_pct(mx0, my0)}"><b>{TARGET}</b>Moon surface<small>every case solved</small></span>'
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
