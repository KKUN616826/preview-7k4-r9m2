"""Leaderboard hero: the lunar podium shows the top three end-to-end models (Clean, Overall score).

Before any end-to-end result is published, the podium is replaced by the first
release date and the models in that batch.
"""
from datetime import date
from html import escape


def _icon(m, size):
    if m['icon']:
        return f'<img src="{escape(m["icon"])}" width="{size}" height="{size}" alt="">'
    return f'<span class="lb-podium-monogram">{escape(m["name"][:2])}</span>'


def render(data):
    e2e = sorted([m for m in data['models'] if m['track'] == 'e2e' and m['results']],
                 key=lambda m: -m['results']['clean']['overall']['score'])
    first = date.fromisoformat(data['first_release'])
    when = f'{first.day} {first.strftime("%B")}'
    parts = ['<section class="lb-stage" id="leaderboard-stage" aria-labelledby="lb-title">'
             '<div class="lb-stage-head"><div><h1 id="lb-title">Leaderboard</h1>'
             '<p>Official Mind2Act runs, with end-to-end models and coding agents ranked separately.</p></div>'
             + ('<div class="lb-stage-controls"><p class="lb-stage-metric">VLA / WAM · Clean · Overall score</p></div>' if len(e2e) >= 3 else '')
             + '</div><div class="lb-stage-visual"><div class="lb-stage-world">'
             + ('<div class="lb-stage-caption"><strong>VLA / WAM</strong> · Top 3</div>' if len(e2e) >= 3 else '')
             + '<div class="lb-stage-scene">'
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v1.png" alt="Lunar robotics campus with three '
             'demonstration stations and a central first, second and third place podium." width="1983" height="793" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v1.png" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
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
