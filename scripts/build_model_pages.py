#!/usr/bin/env python3
"""One page per leaderboard model, models/<id>.html: its scores and its diagnosis card.

A model's optional `diagnosis` in data/leaderboard-results.json uses the card schema of
data/diagnosis-samples.json (code, quote, findings, views, axes, failures, fix). Until it is
published, the page shows an empty card that names what will appear there. models/sample.html
renders the first synthetic sample card in the same layout, labelled as a sample.

Called by build_leaderboard.py; the Profile column on both boards links here.
"""
import hashlib
import json
import re
from datetime import date
from html import escape
from pathlib import Path

import profile_v5 as pv
from build_home_diagnosis import card
from leaderboard_stage import monogram

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'models'
ASSETS = ['media/site-shell.css', 'scripts/home-structure.css', 'scripts/model-page.css']
GHOST = '--fam:#9aa8ae;--fam-ink:#4a5d66;--fam-tint:#f1f4f4'
VIEWS = [('overall', 'Overall'), ('mind', 'Mind'), ('act', 'Act'), ('coupling', 'Mind2Act')]
CARD_VIEWS = [('mind2act', 'Mind2Act'), ('mind', 'Mind'), ('act', 'Act')]


def e(value):
    return escape(str(value), quote=True)


# A plain grey figure with a question mark, for a model that has no profile yet.
UNKNOWN = ['................', '......kkkk......', '.....kkkkkk.....', '....kkkkkkkk....',
           '....kkkkkkkk....', '....kkkkkkkk....', '.....kkkkkk.....', '......kkkk......',
           '...kkkkkkkkkk...', '..kkkkkwwkkkkk..', '..kkkkkkkwkkkk..', '..kkkkkkwkkkkk..',
           '..kkkkkkkkkkkk..', '...kkkkwkkkkk...', '.....kk..kk.....', '.....kk..kk.....']


def silhouette(cls):
    fill = {'k': '#c9d2d5', 'w': '#ffffff'}
    rects = []
    for y, row in enumerate(UNKNOWN):
        x = 0
        while x < 16:
            run = 1
            while x + run < 16 and row[x + run] == row[x]:
                run += 1
            if row[x] != '.':
                rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{fill[row[x]]}"/>')
            x += run
    return (f'<svg class="{cls} is-unknown" viewBox="0 0 16 16" shape-rendering="crispEdges" aria-hidden="true" '
            f'focusable="false">{"".join(rects)}</svg>')


def profile_cell(m):
    """Profile column on the boards: pixel avatar, code and nickname, or a pending chip."""
    href = f'models/{e(m["id"])}.html'
    d = m.get('diagnosis')
    if d:
        code = d['code']
        return (f'<a class="lb-profile" href="{href}" style="{pv.style(code)}" '
                f'aria-label="{e(m["name"])}: profile {code}, {e(pv.title(code))}. Open the diagnosis card">'
                f'{pv.avatar(code, "lb-profile-avatar")}<b>{code}</b><span>{e(pv.nickname(code))}</span></a>')
    return (f'<a class="lb-profile is-pending" href="{href}" aria-label="{e(m["name"])}: diagnosis pending. Open the model page">'
            f'{silhouette("lb-profile-avatar")}<span>Pending</span></a>')


def icon(m, size, prefix='../'):
    if m.get('icon'):
        return f'<img src="{prefix}{e(m["icon"])}" width="{size}" height="{size}" alt="">'
    return f'<span class="mp-monogram" aria-hidden="true">{e(monogram(m["name"]))}</span>'


def when(m, data):
    if m.get('results'):
        return 'Results reported'
    if m.get('release'):
        d = date.fromisoformat(m['release'])
        return f'First results {d.day} {d.strftime("%B")}'
    return f'Evaluation queue · #{m["queue"]}'


def ghost_card(m, data):
    bars = ''.join(f'<div class="dx-bar dx-bar--{k}"><span class="dx-bar-name">{label}</span>'
                   '<span class="dx-bar-track"></span><strong>—</strong></div>' for k, label in CARD_VIEWS)
    axes = ''.join(
        f'<div class="dx-axis"><span class="dx-axis-name" title="{e(compares)}">{name}</span>'
        f'<span class="dx-axis-bar"><span class="dx-pole"><b>{left[0]}</b> {pv.SHORT[left[0]]}</span>'
        f'<span class="dx-track"></span><span class="dx-pole">{pv.SHORT[right[0]]} <b>{right[0]}</b></span></span>'
        '<span class="dx-letter">?</span></div>' for _, name, compares, left, right in pv.AXES)
    track = 'coding agent' if m['track'] == 'agent' else 'VLA / WAM'
    return (f'<article class="dx-card mp-ghost" style="{GHOST}" aria-label="Diagnosis card for {e(m["name"])}, pending">'
            f'<div class="dx-card-head"><p class="dx-model">{e(m["name"])} <span>· {track} · diagnosis pending</span></p>'
            '<span class="dx-code" aria-label="Profile code not yet assigned">????</span></div>'
            f'<div class="dx-hero">{silhouette("dx-avatar")}<div class="dx-hero-text">'
            '<p class="dx-hero-kicker">Your model is the</p><p class="dx-hero-name">To be diagnosed</p>'
            f'<p class="dx-hero-family">{e(when(m, data))}</p>'
            '<p class="dx-hero-traits">One of sixteen profiles, from where its successes and failures fall</p></div></div>'
            f'<div class="dx-bars">{bars}<p class="dx-cap">Mind, Act and Mind2Act, each against the level expected for its overall score</p></div>'
            f'<div class="dx-profile"><p class="dx-label">Behavioural profile <span>tendencies, not ability</span></p>{axes}</div>'
            '<p class="mp-ghost-note">The full card also traces where the closed loop breaks and names one targeted next step. '
            '<a href="sample.html">See a sample card →</a></p></article>')


def scores(m, data):
    r = m.get('results')
    if not r:
        rows = ''.join(f'<tr><th scope="row">{label}</th><td>—</td><td>—</td><td>—</td><td>—</td></tr>' for _, label in VIEWS)
        note = f'<p class="mp-note">No results yet. {e(when(m, data))}.</p>'
        rank = ''
    else:
        rows = ''.join(f'<tr><th scope="row">{label}</th>'
                       + ''.join(f'<td>{r[s][k]["score"]:.2f}</td><td>{r[s][k]["success"]:.1f}%</td>' for s in ('clean', 'random'))
                       + '</tr>' for k, label in VIEWS)
        peers = sorted((p for p in data['models'] if p['track'] == m['track'] and p.get('results')),
                       key=lambda p: -p['results']['clean']['overall']['score'])
        note = f'<p class="mp-note">Valid cases: {r["valid"]["clean"]} Clean, {r["valid"]["random"]} Random.</p>'
        rank = f'<p class="mp-rank"><b>#{peers.index(m) + 1}</b> of {len(peers)} on the board</p>'
    return ('<section class="mp-panel mp-scores" aria-labelledby="mp-scores-title"><h2 id="mp-scores-title">Scores</h2>'
            f'{rank}<table><thead><tr><th scope="col"></th><th scope="col" colspan="2">Clean</th><th scope="col" colspan="2">Random</th></tr>'
            '<tr><th scope="col"><span class="mp-sr">View</span></th><th scope="col">Score</th><th scope="col">Success</th>'
            '<th scope="col">Score</th><th scope="col">Success</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>{note}</section>')


def key_panel():
    items = ''.join(f'<li><span><b>{l[0]}</b> {e(l[1])}</span><span><b>{r[0]}</b> {e(r[1])}</span><small>{e(name)}</small></li>'
                    for _, name, _, l, r in pv.AXES)
    return ('<section class="mp-panel mp-key" aria-labelledby="mp-key-title"><h2 id="mp-key-title">Reading the profile</h2>'
            '<p>Four letters, one per axis, borrowed from MBTI with meanings defined by this benchmark. '
            'They describe tendencies, not ability; letters one and four set the family.</p>'
            f'<ul>{items}</ul><a href="../index.html#dx-types-title">All sixteen profiles →</a></section>')


def shell(title, body):
    header = (ROOT / 'scripts/benchmark/header.html').read_text().replace(' aria-current="page"', '')
    header = header.replace('href="leaderboard.html"', 'href="leaderboard.html" aria-current="page"')
    header = re.sub(r'(href|src)="(?!https?:|#)([^"]+)"', lambda x: f'{x[1]}="../{x[2]}"', header)
    styles = ''.join(f'<link rel="stylesheet" href="../{a}?v={hashlib.sha256((ROOT / a).read_bytes()).hexdigest()[:10]}">' for a in ASSETS)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)} · Leaderboard · Mind2Act World</title><link rel="icon" href="../media/images/mind2act-favicon-v2.png">'
            f'{styles}</head><body class="model-page">{header}<main class="mp" id="main">{body}</main>'
            '<script src="../scripts/site-shell.js?v=unified-1" defer></script></body></html>\n')


def model_page(m, data):
    track = next(t for t in data['tracks'] if t['key'] == m['track'])
    d = m.get('diagnosis')
    head = (f'<a class="mp-back" href="../leaderboard.html#board-{e(m["track"])}"><span aria-hidden="true">←</span> {e(track["title"])}</a>'
            f'<header class="mp-head"><span class="mp-icon">{icon(m, 56)}</span><div>'
            f'<h1>{e(m["name"])}</h1><p class="mp-meta"><span class="mp-type">{e(data["types"][m["type"]])}</span>{e(m["org"])}</p></div>'
            f'<p class="mp-status{" is-done" if m.get("results") else ""}">{e(when(m, data))}</p></header>')
    diagnosis = card(d, sample=False) if d else ghost_card(m, data)
    body = (head + '<div class="mp-grid"><section class="mp-diagnosis" id="diagnosis" aria-labelledby="mp-dx-title">'
            f'<h2 id="mp-dx-title" class="mp-sr">Diagnosis card</h2>{diagnosis}</section>'
            f'<div class="mp-side">{scores(m, data)}{key_panel()}</div></div>')
    return shell(m['name'], body)


def sample_page():
    c = json.loads((ROOT / 'data/diagnosis-samples.json').read_text())['cards'][0]
    head = ('<a class="mp-back" href="../leaderboard.html#results"><span aria-hidden="true">←</span> Leaderboard</a>'
            f'<header class="mp-head"><span class="mp-icon"><span class="mp-monogram" aria-hidden="true">S</span></span><div>'
            f'<h1>{e(c["name"])}</h1><p class="mp-meta"><span class="mp-type">{e(c["track"])}</span>Synthetic sample</p></div>'
            '<p class="mp-status">Sample</p></header>'
            '<p class="mp-sample-note"><strong>Synthetic sample.</strong> This card comes from a fault-injected simulated policy and '
            'shows the layout a model page takes once its diagnosis is published. It is not a result of any real model.</p>')
    side = ('<section class="mp-panel mp-scores"><h2>Scores</h2><p class="mp-note">A synthetic policy has no leaderboard scores. '
            'Model pages show Overall, Mind, Act and Mind2Act for Clean and Random here.</p></section>')
    body = (head + '<div class="mp-grid"><section class="mp-diagnosis" id="diagnosis" aria-label="Diagnosis card">'
            f'{card(c)}</section><div class="mp-side">{side}{key_panel()}</div></div>')
    return shell('Sample diagnosis', body)


def build(data):
    OUT.mkdir(exist_ok=True)
    keep = {f'{m["id"]}.html' for m in data['models']} | {'sample.html'}
    for old in OUT.glob('*.html'):
        if old.name not in keep:
            old.unlink()
    for m in data['models']:
        (OUT / f'{m["id"]}.html').write_text(model_page(m, data), newline='\n')
    (OUT / 'sample.html').write_text(sample_page(), newline='\n')
    return len(data['models'])
