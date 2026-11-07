"""Leaderboard hero: the lunar campus with every reported end-to-end model placed at the height of
its Overall score (plain mean over all 30 tasks, Clean setting), from the launch line (0) to the
target line (100), in release order from left to right. A step line follows the best score so far.

Mind, Act and Mind2Act scores and the Random setting are columns in the tables below.

Until three end-to-end results are published, the climb shows anonymous placeholder entries
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


def _climb(entries, preview, data, when):
    """entries: (name, score, model or None) in release order. Each sits on a stem from the launch line;
    the step line traces the best score so far, and the leader carries a label."""
    n = len(entries)
    best, frontier, items = 0.0, [], []
    lead = max(range(n), key=lambda i: entries[i][1])
    for i, (name, score, m) in enumerate(entries):
        x = 4 + 92 * (i / max(1, n - 1))
        record = score > best
        if record:
            frontier.append((x, score))
            best = score
        badge = _icon(m, 28) if m else f'<span class="lb-climb-mono">{escape(name.split()[-1][:2])}</span>'
        href = f'models/{escape(m["id"])}.html' if m else '#board-e2e'
        cls = 'lb-climb-model' + (' is-record' if record else '') + (' is-lead' if i == lead else '')
        items.append(f'<li class="{cls}" style="--x:{x:.2f}%;--y:{score:.2f};--i:{i};--c:{HUES[i % len(HUES)]}">'
                     f'<a href="{href}" title="{escape(name)} · {score:.1f}" aria-label="{escape(name)}: Overall {score:.1f}{" (placeholder)" if preview else ""}">'
                     f'<span class="lb-climb-badge">{badge}</span>'
                     f'<span class="lb-climb-label"><span>{escape(name)}</span><b>{score:.1f}</b></span></a></li>')
        # Only the leader's label names it; the others show the score, and the name on hover or focus.
    # Step path in a 0-100 box: across at the old best, then up to each new record.
    path, prev = '', None
    for x, y in frontier:
        path += f'M{x:.2f} {100 - y:.2f}' if prev is None else f'H{x:.2f}V{100 - y:.2f}'
        prev = y
    path += 'H100'
    area = path.replace('M', 'M', 1) + f'V100H{frontier[0][0]:.2f}Z'
    grid = ''.join(f'<span class="lb-climb-grid" style="--y:{v}"><i>{v}</i></span>' for v in (25, 50, 75))
    first = ''
    if preview:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        first = ('<p class="lb-climb-first">First results <strong>' + escape(when) + '</strong><span>'
                 + ''.join(f'<span title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 18)}</span>' for m in batch)
                 + '</span></p>')
    return (f'<div class="lb-climb{" lb-climb--preview" if preview else ""}" style="--n:{n}">'
            '<div class="lb-climb-field">'
            f'<span class="lb-climb-target"><b>{TARGET}</b><span>Target · every case solved</span></span>'
            f'{grid}<span class="lb-climb-ground"><i>0</i></span>'
            '<svg class="lb-climb-frontier" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
            f'<path class="lb-climb-area" d="{area}"/><path class="lb-climb-step" d="{path}" pathLength="1"/></svg>'
            f'<ol class="lb-climb-models" aria-label="Overall score by model, in release order">{"".join(items)}</ol>'
            f'<span class="lb-climb-togo" style="--x:{4 + 92 * (lead / max(1, n - 1)):.2f}%;--y:{best:.2f}" aria-hidden="true">'
            f'<em>{TARGET - best:.1f} to go</em></span></div>'
            '<div class="lb-climb-hud">'
            '<p class="lb-climb-kicker">Overall · VLA / WAM · Clean</p>'
            f'<p class="lb-climb-best"><span>Best so far</span><b>{best:.1f}</b><i>/ {TARGET}</i></p>'
            f'<p class="lb-climb-gap"><b>{TARGET - best:.1f}</b> points to the target</p>'
            + ('<p class="lb-climb-note">Preview · placeholder models and scores, <strong>not results</strong></p>' if preview else '')
            + f'{first}</div></div>')


def render(data):
    e2e = sorted([m for m in data['models'] if m['track'] == 'e2e' and m['results']],
                 key=lambda m: -m['results']['clean']['overall']['score'])
    first = date.fromisoformat(data['first_release'])
    when = f'{first.day} {first.strftime("%B")}'
    preview = len(e2e) < 3
    parts = ['<section class="lb-stage" id="leaderboard-stage" aria-labelledby="lb-title">'
             '<div class="lb-stage-head"><div><h1 id="lb-title">Leaderboard</h1>'
             '</div>'
             + ('<div class="lb-stage-controls"><p class="lb-stage-metric">VLA / WAM · Clean · Overall score</p></div>' if not preview else '')
             + '</div><div class="lb-stage-visual"><div class="lb-stage-world">'
             + '<div class="lb-stage-scene">'
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v3.webp" alt="Lunar robotics campus with three '
             'demonstration stations around three launch towers." width="1983" height="793" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v3.webp" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
    parts.append(stations())
    parts.append('</div>')  # the climb is laid out on the stage, not on the cover-cropped artwork
    if preview:
        parts.append(_climb([(n, sc, None) for n, sc in PREVIEW], True, data, when))
    else:
        in_order = sorted(e2e, key=lambda m: (m.get('release') or '', m['name']))
        parts.append(_climb([(m['name'], m['results']['clean']['overall']['score'], m) for m in in_order], False, data, when))
    parts.append('</div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View both leaderboards ↓</a>'
                 f'<p>Protocol {escape(data["protocol"]["version"])} · Ranked by Overall score · Random reported separately</p>'
                 '<button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button>'
                 '</div></section>')
    return ''.join(parts)
