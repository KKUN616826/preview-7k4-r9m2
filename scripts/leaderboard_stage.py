"""Leaderboard hero: the lunar campus under a wide sky, with the Earth on the horizon and the Moon above.
Height is score. Each reported end-to-end model launches straight up from its pad on the Earth's horizon
(0) and stops at the height of its Overall score (plain mean over all 30 tasks, Clean setting); the
level of the Moon's lower edge is 100, every case solved. Pads run left to right in release order, and
level lines mark 25, 50 and 75, so the picture reads like a chart without looking like one.

Mind, Act and Mind2Act scores and the Random setting are columns in the tables below.

Until three end-to-end results are published, the sky shows anonymous placeholder entries (PREVIEW),
captioned as placeholders, together with the first release date and batch.
"""
from datetime import date
from html import escape

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


# Geometry of leaderboard-lunar-campus-v4.webp in artwork units (1983 x 1053): v3 with SKY units of sky
# inserted between the Moon and the Earth (scripts/extend_lunar_sky.py), so v3 y + SKY = v4 y.
W, H, SKY = 1983, 1053, 260
MOON_LOW = 220                               # the Moon's lowest point (x 1698)
TOP = 236                                    # the 100 level, just under the Moon
# The Earth's horizon, measured on v3 and moved down by SKY: (x, y) samples, interpolated linearly.
HORIZON = [(300, 272), (600, 279), (900, 300), (1150, 320), (1500, 330), (1700, 343), (1983, 365)]
PADS = (360, 1660)                           # first and last launch pad along the horizon


def _earth(x):
    for (x0, y0), (x1, y1) in zip(HORIZON, HORIZON[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0) + SKY
    return HORIZON[-1][1] + SKY


def _height(x, score):
    """Artwork y of a score at x: 0 on the horizon, 100 at the Moon's level."""
    y0 = _earth(x) - 4
    return y0 + (TOP - y0) * score / TARGET


def _pct(x, y):
    return f'left:{x / W * 100:.3f}%;top:{y / H * 100:.3f}%'


def _shot(entries, preview, data, when):
    """entries: (name, score, model or None) in release order, on pads from left to right."""
    n = len(entries)
    lead = max(range(n), key=lambda i: entries[i][1])
    best = entries[lead][1]
    rank = {i: r + 1 for r, i in enumerate(sorted(range(n), key=lambda i: -entries[i][1]))}
    items, trails = [], []
    for i, (name, score, m) in enumerate(entries):
        x = PADS[0] + (PADS[1] - PADS[0]) * i / max(1, n - 1)
        y0, y = _earth(x) - 4, _height(x, score)
        trails.append(f'<line class="lb-shot-trail{" is-lead" if i == lead else ""}" x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                      f'pathLength="1" style="--i:{i}"/><circle class="lb-shot-pad" cx="{x:.1f}" cy="{y0:.1f}" r="3.5"/>')
        badge = _icon(m, 28) if m else f'<span class="lb-shot-mono">{escape(name.split()[-1][:2])}</span>'
        href = f'models/{escape(m["id"])}.html' if m else '#board-e2e'
        cls = 'lb-shot-model' + (' is-lead' if i == lead else '') + (' is-top' if rank[i] <= 3 else '')
        place = f'<em>#{rank[i]}</em>' if rank[i] <= 3 else ''
        items.append(f'<li class="{cls}" style="{_pct(x, y)};--i:{i};--rise:{(y0 - y) / H * 100:.3f};--t:{i / max(1, n - 1):.4f};--s:{score / TARGET:.4f}">'
                     f'<a href="{href}" title="{escape(name)} · Overall {score:.1f}" aria-label="{escape(name)}: Overall {score:.1f}{" (placeholder)" if preview else ""}">'
                     f'<span class="lb-shot-label"><span>{place}{escape(name)}</span><b>{score:.1f}</b>'
                     + (f'<small><i>{TARGET - score:.1f}</i> to the Moon</small>' if i == lead else '') + '</span>'
                     f'<span class="lb-shot-badge">{badge}</span></a></li>')
    # Level lines across the sky, from the first pad to the Moon.
    levels = ''
    for v in (0, 25, 50, 75, 100):
        x0 = PADS[0] - 60
        pts = [(x, _height(x, v)) for x in range(int(x0), W + 1, 40)]
        cls = 'lb-shot-level' + (' is-top' if v == 100 else ' is-ground' if v == 0 else '')
        levels += (f'<path class="{cls}" d="M' + ' L'.join(f'{a:.0f} {b:.1f}' for a, b in pts) + '"/>'
                   f'<text class="lb-shot-tick" x="{x0 - 10:.0f}" y="{_height(x0, v) + 5:.1f}">{v}</text>')
    lx = PADS[0] + (PADS[1] - PADS[0]) * lead / max(1, n - 1)
    ly = _height(lx, best)
    gap = (f'<line class="lb-shot-gap" x1="{lx:.1f}" y1="{ly - 90:.1f}" x2="{lx:.1f}" y2="{TOP:.1f}"/>')
    first = ''
    if preview:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        first = ('<p class="lb-shot-note"><span>Preview · placeholder models and scores, <strong>not results</strong></span>'
                 '<span class="lb-shot-first">First results <strong>' + escape(when) + '</strong>'
                 + ''.join(f'<span title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 18)}</span>' for m in batch)
                 + '</span></p>')
    return (f'<div class="lb-shot{" lb-shot--preview" if preview else ""}" style="--n:{n}">'
            f'<svg class="lb-shot-svg" viewBox="0 0 {W} {H}" aria-hidden="true">'
            f'<g class="lb-shot-levels">{levels}</g>{gap}<g class="lb-shot-trails">{"".join(trails)}</g>'
            f'<text class="lb-shot-axis-title" transform="translate({PADS[0] - 115:.0f} {(_earth(PADS[0]) + _height(PADS[0], 100)) / 2:.0f}) rotate(-90)">Overall score</text></svg>'
            f'<p class="lb-shot-tag lb-shot-tag--moon" style="{_pct(1500, TOP)}"><b>100</b> The Moon · every case solved</p>'
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
             '<p class="lb-stage-sub">Overall score of every VLA / WAM model, Clean setting. Height is score, from the '
             'Earth\'s horizon (0) to the Moon (100, every case solved); left to right is release order.</p>'
             f'{note}</div>'
             + '</div><div class="lb-stage-visual"><div class="lb-stage-world">'
             + '<div class="lb-stage-scene">'
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v4.webp" alt="Lunar robotics campus under a wide sky, '
             'with the Earth on the horizon and the Moon above." width="1983" height="1053" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v3.webp" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
    parts.append(shot)      # on the artwork, so pads sit on the Earth's horizon and 100 is the Moon's level
    parts.append('</div></div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View both leaderboards ↓</a>'
                 f'<p>Protocol {escape(data["protocol"]["version"])} · Ranked by Overall score · Random reported separately</p>'
                 '<button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button>'
                 '</div></section>')
    return ''.join(parts)
