"""Leaderboard hero: the lunar podium shows the top three end-to-end models (Clean, Overall score).

Before any end-to-end result is published, the podium is replaced by the first
release date and the models in that batch.
"""
from datetime import date
from html import escape

# One station per suite (see media/leaderboard-motion/scene.js). Labels name the dimension only.
# x, y: the label's bottom anchor above the arm, in artwork units (1983 x 793); align: which
# edge of the label sits on x, so labels near the crop edge stay inside the stage.
STATIONS = [
    ('mind', 'Mind', 'memory and decisions', 522, 298, 'center'),
    ('mind2act', 'Mind2Act', 'reasoning and execution together', 992, 520, 'center'),
    ('act', 'Act', 'physical execution', 1696, 300, 'right'),
]


def stations():
    items = ''.join(
        f'<a class="lb-station lb-station--{slug} lb-station--{align}" href="benchmark.html#suite-{slug}" '
        f'style="left:{x / 19.83:.2f}%;top:{y / 7.93:.2f}%">'
        f'<strong>{name}</strong><span>{escape(gist)}</span></a>'
        for slug, name, gist, x, y, align in STATIONS)
    return f'<nav class="lb-stations" aria-label="The three evaluation dimensions">{items}</nav>'


def monogram(name):
    """Two letters for a model without a logo, skipping punctuation (X-WAM -> XW)."""
    return ''.join(ch for ch in name if ch.isalnum())[:2]


def _icon(m, size):
    if m['icon']:
        return f'<img src="{escape(m["icon"])}" width="{size}" height="{size}" alt="">'
    return f'<span class="lb-podium-monogram">{escape(monogram(m["name"]))}</span>'


def render(data):
    e2e = sorted([m for m in data['models'] if m['track'] == 'e2e' and m['results']],
                 key=lambda m: -m['results']['clean']['overall']['score'])
    first = date.fromisoformat(data['first_release'])
    when = f'{first.day} {first.strftime("%B")}'
    parts = ['<section class="lb-stage" id="leaderboard-stage" aria-labelledby="lb-title">'
             '<div class="lb-stage-head"><div><h1 id="lb-title">Leaderboard</h1>'
             '</div>'
             + ('<div class="lb-stage-controls"><p class="lb-stage-metric">VLA / WAM · Clean · Overall score</p></div>' if len(e2e) >= 3 else '')
             + '</div><div class="lb-stage-visual"><div class="lb-stage-world">'
             + '<div class="lb-stage-scene">'
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v2.webp" alt="Lunar robotics campus with three '
             'demonstration stations and a central first, second and third place podium." width="1983" height="793" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v2.webp" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
    parts.append(stations())
    if len(e2e) >= 3:
        parts.append('<div class="lb-podium-labels">')
        for rank in (2, 1, 3):
            m = e2e[rank - 1]
            score = m['results']['clean']['overall']['score']
            parts.append(f'<a class="lb-podium-label lb-podium-rank-{rank}" href="#board-e2e" '
                         f'aria-label="Rank {rank}: {escape(m["name"])}, Overall score {score:.2f}">'
                         f'<span class="lb-podium-avatar">{_icon(m, 32)}</span>'
                         f'<span class="lb-podium-name">{escape(m["name"])}</span><strong>{score:.2f}</strong></a>')
        parts.append('</div>')
    else:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        parts.append('<div class="lb-stage-upcoming"><p>First results</p>'
                     f'<strong>{escape(when)}</strong><ul>'
                     + ''.join(f'<li title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 32)}<span>{escape(m["name"])}</span></li>' for m in batch)
                     + '</ul></div>')
    parts.append('</div></div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View both leaderboards ↓</a>'
                 f'<p>Protocol {escape(data["protocol"]["version"])} · Clean and Random reported separately</p>'
                 '<button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button>'
                 '</div></section>')
    return ''.join(parts)
