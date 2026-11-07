"""Leaderboard hero: the lunar podium shows the top three end-to-end models (Clean, Overall score),
and a track below it shows how far the reported models are from the target of 100.

The ranking uses one number per model: the Overall score (plain mean over all 30 tasks, Clean
setting). Mind, Act and Mind2Act scores and the Random setting are columns in the tables below.

Until three end-to-end results are published, the podium and the track show anonymous placeholder
entries (PREVIEW), captioned as placeholders, together with the first release date and batch.
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


# Placeholder entries for the hero before 11 November: anonymous names, in release order, with
# illustrative Overall scores that rise from one release to the next. Not results of any model.
PREVIEW = [('Model E', 6.4), ('Model D', 14.9), ('Model C', 22.8), ('Model B', 31.5), ('Model A', 40.6)]
TARGET = 100


def monogram(name):
    """Two letters for a model without a logo, skipping punctuation (X-WAM -> XW)."""
    return ''.join(ch for ch in name if ch.isalnum())[:2]


def _icon(m, size):
    if m['icon']:
        return f'<img src="{escape(m["icon"])}" width="{size}" height="{size}" alt="">'
    return f'<span class="lb-podium-monogram">{escape(monogram(m["name"]))}</span>'


def _podium(top, preview):
    """Ranks 2, 1, 3 on the second, first and third pillars; `top` holds (name, score, model or None)."""
    out = ['<div class="lb-podium-labels' + (' lb-podium-labels--preview' if preview else '') + '">']
    for rank in (2, 1, 3):
        name, score, m = top[rank - 1]
        avatar = _icon(m, 32) if m else f'<span class="lb-podium-monogram">{escape(name.split()[-1])}</span>'
        label = f'Rank {rank}: {escape(name)}, Overall score {score:.2f}' + (' (placeholder)' if preview else '')
        out.append(f'<a class="lb-podium-label lb-podium-rank-{rank}" href="#board-e2e" aria-label="{label}">'
                   f'<span class="lb-podium-avatar">{avatar}</span>'
                   f'<span class="lb-podium-name">{escape(name)}</span><strong>{score:.2f}</strong></a>')
    out.append('</div>')
    return ''.join(out)


def _race(entries, preview, data, when):
    """Overall score track from 0 to the target: one mark per model in release order, the fill up to the leader."""
    best = max(score for _, score in entries)
    marks = ''.join(
        f'<span class="lb-race-mark{" is-lead" if score == best else ""}" style="--at:{score:.2f}%;--n:{i}">'
        f'<b>{score:.1f}</b><small>{escape(name)}</small></span>'
        for i, (name, score) in enumerate(entries))
    summary = ', '.join(f'{name} {score:.1f}' for name, score in entries)
    first = ''
    if preview:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        first = ('<span class="lb-race-first">First results <strong>' + escape(when) + '</strong><span class="lb-race-batch">'
                 + ''.join(f'<span title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 20)}</span>' for m in batch)
                 + '</span></span>')
    return (f'<div class="lb-race{" lb-race--preview" if preview else ""}">'
            '<p class="lb-race-head"><span class="lb-race-title">Distance to the target'
            f'<b>Overall score · VLA / WAM · Clean</b></span>{first}</p>'
            f'<div class="lb-race-track" role="img" aria-label="Overall score out of {TARGET}, in release order: {escape(summary)}'
            f'{" (placeholders)" if preview else ""}. {TARGET - best:.1f} points to the target.">'
            f'<i class="lb-race-fill" style="--to:{best:.2f}%"></i>'
            f'<span class="lb-race-gap" style="--from:{best:.2f}%"><em>{TARGET - best:.1f} to go</em></span>'
            f'{marks}<span class="lb-race-flag"><b>{TARGET}</b><small>Target</small></span></div></div>')


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
             '<img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v2.webp" alt="Lunar robotics campus with three '
             'demonstration stations and a central first, second and third place podium." width="1983" height="793" fetchpriority="high">'
             '<video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v2.webp" '
             'aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video>']
    parts.append(stations())
    if preview:
        ranked = sorted(PREVIEW, key=lambda x: -x[1])
        parts.append('<p class="lb-stage-caption">Preview · placeholder models and scores, <strong>not results</strong></p>')
        parts.append(_podium([(n, sc, None) for n, sc in ranked[:3]], True))
        parts.append(_race(PREVIEW, True, data, when))
    else:
        parts.append(_podium([(m['name'], m['results']['clean']['overall']['score'], m) for m in e2e[:3]], False))
        in_order = sorted(e2e, key=lambda m: (m.get('release') or '', -m['results']['clean']['overall']['score']))[-6:]
        parts.append(_race([(m['name'], m['results']['clean']['overall']['score']) for m in in_order], False, data, when))
    parts.append('</div></div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View both leaderboards ↓</a>'
                 f'<p>Protocol {escape(data["protocol"]["version"])} · Ranked by Overall score · Random reported separately</p>'
                 '<button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button>'
                 '</div></section>')
    return ''.join(parts)
