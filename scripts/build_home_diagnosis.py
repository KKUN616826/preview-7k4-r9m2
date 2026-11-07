#!/usr/bin/env python3
"""Homepage diagnosis-card section, built from data/diagnosis-samples.json.

The section sits between the introduction and the leaderboard preview, between
<!-- HOME_DIAGNOSIS_START --> and <!-- HOME_DIAGNOSIS_END -->. Running it again
replaces only that block. The cards are synthetic samples from the harness
reference cards; the section says so next to them.
"""
import json
import re
from html import escape
from pathlib import Path
from build_home_tasks import refresh_stylesheet_versions

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r'<!-- HOME_DIAGNOSIS_START -->.*?<!-- HOME_DIAGNOSIS_END -->\n?', re.S)
ANCHOR = '<section class="academic-section home-leaderboard" id="top-ten"'

STAGES = {
    'perceive': 'Perceive', 'reason': 'Reason', 'perceive-reason': 'Perceive & reason',
    'act': 'Act', 'verify': 'Verify & recover', 'other': 'Other',
}
CONTRIBUTIONS = [
    ('Three views locate the weakness',
     'Mind and Act test reasoning and execution alone; Mind2Act joins them in one closed loop. '
     'Each is read against the expectation for the model’s level and the task difficulty.'),
    ('A four-letter behavioural profile',
     'Mind or Act, entity or location memory, plan-ahead or feedback-driven control, precision or agility. '
     'Tendencies, not ability; an unstable lean is written X.'),
    ('Where the loop breaks',
     'Every failed episode is traced to the first stage after which success became impossible: '
     'physics rules first, an agent judge on the evidence second, human calibration on new tasks.'),
    ('A targeted next step',
     'The largest failure stage becomes a concrete fix: an agent module for coding agents, '
     'training data for end-to-end policies, with an expected gain.'),
]


def view_tile(v):
    arrow = {'above': '▲', 'below': '▼'}.get(v['call'], '')
    delta = 'in line with expectation' if v['call'] == 'in line' else f'{abs(v["delta"]):.1f} pp {v["call"]} expectation'
    return (f'<div class="dx-view dx-view--{v["key"]}"><span class="dx-view-name">{escape(v["label"])}</span>'
            f'<strong>{v["value"]:.1f}%</strong>'
            f'<span class="dx-view-call dx-call--{v["call"].replace(" ", "-")}">{arrow} {escape(delta)}</span></div>')


def axis_row(a):
    # The bar runs from the second pole (right) to the first pole (left); 50% is the centre.
    pos = 50 - (a['lean'] - 50) if a['side'] == 'first' else 50 + (a['lean'] - 50)
    pole = a['poles'][0] if a['side'] == 'first' else a['poles'][1]
    unstable = a['letter'] == 'X'
    note = f'stability {a["stability"]}%' + (' · no clear lean' if unstable else '')
    return (f'<div class="dx-axis{" is-unstable" if unstable else ""}">'
            f'<span class="dx-axis-name">{escape(a["axis"])}</span>'
            f'<span class="dx-axis-bar" role="img" aria-label="{a["lean"]}% {escape(pole)}, {escape(note)}">'
            f'<span class="dx-pole">{escape(a["poles"][0])}</span><span class="dx-track"><i style="left:{pos:.0f}%"></i></span>'
            f'<span class="dx-pole">{escape(a["poles"][1])}</span></span>'
            f'<span class="dx-letter" title="{escape(note)}">{escape(a["letter"])}</span></div>')


def failure_bar(f):
    segs = ''.join(f'<span class="dx-stage dx-stage--{k}" style="flex-basis:{v}%" title="{STAGES[k]} {v:.0f}%">'
                   f'{f"{v:.0f}%" if v >= 9 else ""}</span>' for k, v in f['stages'])
    legend = ''.join(f'<li class="dx-stage--{k}">{STAGES[k]}</li>' for k, _ in f['stages'])
    largest = max(f['stages'], key=lambda s: s[1])
    note = f'<p class="dx-note">{escape(f["note"])}</p>' if f.get('note') else ''
    return (f'<div class="dx-failures"><p class="dx-label">Where the {escape(f["view"])} loop breaks '
            f'<span>n = {f["n"]} failures</span></p>'
            f'<div class="dx-stack" role="img" aria-label="Largest stage: {STAGES[largest[0]]} {largest[1]:.0f}%">{segs}</div>'
            f'<ul class="dx-legend">{legend}</ul>{note}</div>')


def card(c):
    return (f'<article class="dx-card" aria-label="Sample diagnosis card: {escape(c["name"])}">'
            f'<div class="dx-card-head"><div><p class="dx-model">{escape(c["name"])}</p>'
            f'<p class="dx-kind">{escape(c["track"])} · synthetic sample</p></div>'
            f'<span class="dx-code" aria-label="Profile code {escape(c["code"])}">{escape(c["code"])}</span></div>'
            f'<p class="dx-type"><strong>{escape(c["type"])}</strong> {escape(c["subtype"])}'
            f'<span>“{escape(c["quote"])}”</span></p>'
            f'<div class="dx-views">{"".join(view_tile(v) for v in c["views"])}</div>'
            f'<div class="dx-profile"><p class="dx-label">Behavioural profile <span>tendencies, not ability</span></p>'
            f'{"".join(axis_row(a) for a in c["axes"])}</div>'
            f'{failure_bar(c["failures"])}'
            f'<div class="dx-fix"><p class="dx-label">Priority 1 · {escape(c["fix"]["kind"])}</p>'
            f'<p><strong>{escape(c["fix"]["name"])}.</strong> {escape(c["fix"]["action"])}</p>'
            f'<p class="dx-gain">Expected: {escape(c["fix"]["gain"])}</p></div>'
            '</article>')


def render():
    data = json.loads((ROOT / 'data/diagnosis-samples.json').read_text())
    points = ''.join(f'<li><span class="dx-num">{i}</span><h3>{escape(t)}</h3><p>{escape(d)}</p></li>'
                     for i, (t, d) in enumerate(CONTRIBUTIONS, 1))
    return ('<!-- HOME_DIAGNOSIS_START -->\n'
            '<section class="academic-section home-diagnosis" id="diagnosis" aria-labelledby="home-diagnosis-title">'
            '<div class="dx-head"><p class="home-eyebrow">Diagnosis</p>'
            '<h2 id="home-diagnosis-title">Beyond one score: a diagnosis card for every model</h2>'
            '</div>'
            f'<ol class="dx-points">{points}</ol>'
            f'<div class="dx-cards">{"".join(card(c) for c in data["cards"])}</div>'
            '<p class="dx-disclaimer"><strong>Synthetic samples.</strong> Both cards were generated from fault-injected '
            'simulated policies to show the card’s format and logic; they are not results of any real model. '
            f'<a href="{escape(data["pdf"])}" target="_blank" rel="noopener">Full sample card (PDF) '
            '<span aria-hidden="true">↗</span></a></p>'
            '</section>\n<!-- HOME_DIAGNOSIS_END -->\n')


def update(source):
    if BLOCK.search(source):
        return BLOCK.sub(lambda _: render(), source, count=1)
    assert source.count(ANCHOR) == 1, 'expected one leaderboard preview section'
    return source.replace(ANCHOR, render() + ANCHOR, 1)


if __name__ == '__main__':
    page = ROOT / 'index.html'
    page.write_bytes(refresh_stylesheet_versions(update(page.read_bytes().decode())).encode())
    print('Built homepage diagnosis-card section.')
