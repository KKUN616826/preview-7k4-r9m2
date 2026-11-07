"""Leaderboard hero, after the summit charts of RoboDojo and other leaderboards: a compact card from the
surface of the Earth (0) to the surface of the Moon (100, every case solved). Every reported end-to-end
model flies as high as its Overall score (plain mean over all 30 tasks, Clean setting), in release order
from left to right, with its logo, name and score; the leader carries the distance still to the Moon.

Mind, Act and Mind2Act scores and the Random setting are columns in the tables below.

Until three end-to-end results are published, the card shows anonymous placeholder entries (PREVIEW),
captioned as placeholders, together with the first release date and batch.
"""
import random
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


def _moon():
    """The Moon's lower limb across the top of the card: a wide disc, craters and a soft limb shadow.
    Drawn in fixed pixels and centred, so narrower screens show its middle."""
    rng = random.Random(7)
    craters = []
    for _ in range(70):
        x, r = rng.uniform(40, 1960), rng.choice([3, 4, 5, 6, 7, 9, 12, 16])
        y = rng.uniform(4, 128)
        craters.append(f'<g transform="translate({x:.0f} {y:.0f})"><ellipse rx="{r}" ry="{r * .62:.1f}" class="c-rim"/>'
                       f'<ellipse rx="{r * .82:.1f}" ry="{r * .5:.1f}" cy="{r * .08:.1f}" class="c-pit"/></g>')
    maria = ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" class="c-mare"/>'
                    for x, y, rx, ry in [(420, 60, 210, 46), (980, 92, 260, 40), (1520, 54, 190, 50), (1240, 20, 160, 30)])
    return ('<svg class="lb-moon" width="2000" height="150" viewBox="0 0 2000 150" aria-hidden="true" focusable="false">'
            '<defs><clipPath id="lb-moon-disc"><circle cx="1000" cy="-3460" r="3600"/></clipPath>'
            '<radialGradient id="lb-moon-fill" cx="1000" cy="-3460" r="3600" gradientUnits="userSpaceOnUse">'
            '<stop offset=".96" stop-color="#e6e9e8"/><stop offset=".993" stop-color="#d6dcde"/><stop offset="1" stop-color="#bfc8cc"/></radialGradient></defs>'
            '<circle cx="1000" cy="-3460" r="3601" class="lb-moon-glow"/>'
            f'<g clip-path="url(#lb-moon-disc)"><rect width="2000" height="150" fill="url(#lb-moon-fill)"/>{maria}{"".join(craters)}</g></svg>')


def _earth():
    """The Earth's surface along the bottom: ocean, land, cloud bands and the atmosphere's rim."""
    rng = random.Random(3)
    clouds = ''.join(f'<ellipse cx="{rng.uniform(0, 2000):.0f}" cy="{rng.uniform(40, 150):.0f}" rx="{rng.uniform(60, 180):.0f}" '
                     f'ry="{rng.uniform(3, 8):.0f}" class="e-cloud"/>' for _ in range(40))
    land = ''.join(f'<path class="e-land" d="{d}"/>' for d in [
        'M150 96 C200 70 260 84 300 74 C350 62 420 80 440 104 C452 120 420 150 380 150 L170 150 C140 132 128 110 150 96Z',
        'M770 70 C800 58 850 66 880 60 C930 52 990 70 1000 88 C1006 102 970 112 930 108 C890 118 830 112 800 100 C770 92 756 80 770 70Z',
        'M1400 82 C1440 64 1500 74 1540 66 C1600 56 1680 76 1700 104 C1712 124 1680 150 1640 150 L1430 150 C1392 134 1380 100 1400 82Z'])
    return ('<svg class="lb-earth" width="2000" height="150" viewBox="0 0 2000 150" aria-hidden="true" focusable="false">'
            '<defs><clipPath id="lb-earth-disc"><circle cx="1000" cy="3630" r="3600"/></clipPath>'
            '<linearGradient id="lb-earth-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5f9fc8"/>'
            '<stop offset=".5" stop-color="#3c79a8"/><stop offset="1" stop-color="#2c5f8c"/></linearGradient></defs>'
            '<circle cx="1000" cy="3630" r="3622" class="lb-earth-air"/><circle cx="1000" cy="3630" r="3608" class="lb-earth-air2"/>'
            f'<g clip-path="url(#lb-earth-disc)"><rect width="2000" height="150" fill="url(#lb-earth-fill)"/>{land}{clouds}</g></svg>')


def _sky(entries, preview, data, when):
    """entries: (name, score, model or None) in release order."""
    n = len(entries)
    lead = max(range(n), key=lambda i: entries[i][1])
    best = entries[lead][1]
    top = set(sorted(range(n), key=lambda i: -entries[i][1])[:3])
    items = []
    for i, (name, score, m) in enumerate(entries):
        x = 5 + 90 * (i / max(1, n - 1))
        badge = _icon(m, 30) if m else f'<span class="lb-sky-mono">{escape(name.split()[-1][:2])}</span>'
        href = f'models/{escape(m["id"])}.html' if m else '#board-e2e'
        cls = 'lb-sky-model' + (' is-lead' if i == lead else '') + (' is-top' if i in top else '')
        items.append(f'<li class="{cls}" style="--x:{x:.2f}%;--y:{score:.2f};--i:{i};--c:{HUES[i % len(HUES)]}">'
                     f'<a href="{href}" title="{escape(name)} · Overall {score:.1f}" '
                     f'aria-label="{escape(name)}: Overall {score:.1f}{" (placeholder)" if preview else ""}">'
                     f'<span class="lb-sky-badge">{badge}</span>'
                     f'<span class="lb-sky-label"><span>{escape(name)}</span><b>{score:.1f}</b></span></a></li>')
    grid = ''.join(f'<span class="lb-sky-line" style="--y:{v}"><i>{v}</i></span>' for v in (25, 50, 75))
    lx = 5 + 90 * (lead / max(1, n - 1))
    caption = (f'<span>Protocol {escape(data["protocol"]["version"])} · VLA / WAM · Clean · Overall score, higher is better</span>')
    if preview:
        batch = [m for m in data['models'] if m.get('release') == data['first_release']]
        caption = ('<span class="lb-sky-note">Preview · placeholder models and scores, <strong>not results</strong></span>'
                   '<span class="lb-sky-first">First results <strong>' + escape(when) + '</strong>'
                   + ''.join(f'<span title="{escape(m["name"])} · {escape(m["org"])}">{_icon(m, 18)}</span>' for m in batch)
                   + '</span>' + caption)
    return (f'<figure class="lb-sky{" lb-sky--preview" if preview else ""}" style="--n:{n}" aria-label="Overall score from the Earth (0) to the Moon (100)">'
            f'<div class="lb-sky-space">{_moon()}{_earth()}'
            '<p class="lb-sky-moon"><b>100</b> The Moon · every case solved<small>Still unclaimed</small></p>'
            '<p class="lb-sky-earth"><b>0</b> Earth</p>'
            f'<div class="lb-sky-plot">{grid}'
            f'<span class="lb-sky-gap" style="--x:{lx:.2f}%;--y:{best:.2f}" aria-hidden="true"><em>{TARGET - best:.1f} to the Moon</em></span>'
            f'<ol class="lb-sky-models" aria-label="Overall score by model, in release order">{"".join(items)}</ol></div>'
            '<span class="lb-sky-axis" aria-hidden="true">Earlier releases <i>→</i> later releases</span></div>'
            f'<figcaption>{caption}</figcaption></figure>'), best


def render(data):
    e2e = sorted([m for m in data['models'] if m['track'] == 'e2e' and m['results']],
                 key=lambda m: -m['results']['clean']['overall']['score'])
    first = date.fromisoformat(data['first_release'])
    when = f'{first.day} {first.strftime("%B")}'
    preview = len(e2e) < 3
    if preview:
        entries = [(n, sc, None) for n, sc in PREVIEW]
    else:
        in_order = sorted(e2e, key=lambda m: (m.get('release') or '', m['name']))
        entries = [(m['name'], m['results']['clean']['overall']['score'], m) for m in in_order]
    sky, best = _sky(entries, preview, data, when)
    stats = (f'<dl class="lb-hero-stats"><div><dt>Best so far</dt><dd><b>{best:.1f}</b> / {TARGET}</dd></div>'
             f'<div><dt>To the Moon</dt><dd><b>{TARGET - best:.1f}</b></dd></div>'
             f'<div><dt>Models</dt><dd><b>{len(entries)}</b>{"<small> placeholders</small>" if preview else ""}</dd></div></dl>')
    return ('<section class="lb-hero" id="leaderboard-stage" aria-labelledby="lb-title">'
            '<div class="lb-hero-head"><div><h1 id="lb-title">Leaderboard</h1>'
            '<p>From the Earth to the Moon. Each model flies as high as its Overall score; '
            'the Moon, 100, is every case solved.</p></div>' + stats + '</div>'
            + sky +
            '<a href="#results" class="lb-hero-more">Both leaderboards, full scores <span aria-hidden="true">↓</span></a></section>')
