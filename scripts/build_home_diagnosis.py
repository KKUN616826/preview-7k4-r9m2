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
import profile_v5 as pv

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
     'MBTI-style letters with meanings defined by this benchmark: E acts / I thinks, S remembers what / '
     'N remembers where, T precision / F reactivity, J plans ahead / P follows feedback. '
     'Tendencies, not ability; a weak lean is shown with its stability.'),
    ('Where the loop breaks',
     'Every failed episode is traced to the first stage after which success became impossible: '
     'physics rules first, an agent judge on the evidence second, human calibration on new tasks.'),
    ('A targeted next step',
     'The largest failure stage becomes a concrete fix: an agent module for coding agents, '
     'training data for end-to-end policies, with an expected gain.'),
]


VIEW_ORDER = ['mind', 'act', 'mind2act']
AXIS_COLOUR = {'energy': '#203749', 'information': '#49796b', 'decisions': '#446f86', 'lifestyle': '#91793d'}


def view_bar(v):
    call = 'in line with expectation' if v['call'] == 'in line' else f'{abs(v["delta"]):.1f} pp {v["call"]} expectation'
    return (f'<div class="dx-bar dx-bar--{v["key"]}"><span class="dx-bar-name">{escape(v["label"])}</span>'
            f'<span class="dx-bar-track" role="img" aria-label="{v["value"]:.1f}%, expected {v["expected"]:.1f}%, {escape(call)}">'
            f'<i style="width:{v["value"]:.1f}%"></i><b style="left:{v["expected"]:.1f}%"></b></span>'
            f'<strong>{v["value"]:.1f}%</strong></div>')


def axis_row(a):
    key, name, compares, left, right = next(x for x in pv.AXES if x[0] == a['key'])
    # 50% is the centre; the marker moves toward the pole the lean points to.
    pos = 50 - (a['lean'] - 50) if a['side'] == 'left' else 50 + (a['lean'] - 50)
    weak = a['stability'] < pv.STABLE
    pole = left if a['side'] == 'left' else right
    note = f'{"weak lean · " if weak else ""}stability {a["stability"]}%'
    small = f'<small>weak lean · {a["stability"]}%</small>' if weak else ''
    return (f'<div class="dx-axis{" is-weak" if weak else ""}" style="--axis:{AXIS_COLOUR[key]}">'
            f'<span class="dx-axis-name" title="{escape(compares)}">{name}{small}</span>'
            f'<span class="dx-axis-bar" role="img" aria-label="{a["lean"]}% {escape(pole[1])}, {escape(note)}">'
            f'<span class="dx-pole"><b>{left[0]}</b> {pv.SHORT[left[0]]}</span><span class="dx-track"><i style="left:{pos:.0f}%"></i></span>'
            f'<span class="dx-pole">{pv.SHORT[right[0]]} <b>{right[0]}</b></span></span>'
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
    code, fam = c['code'], pv.family(c['code'])
    views = {v['key']: v for v in c['views']}
    findings = ''.join(f'<li><strong>{escape(h)}</strong><span>{escape(t)}</span></li>' for h, t in c['findings'])
    return (f'<article class="dx-card" style="{pv.style(code)}" aria-label="Sample diagnosis card: {escape(c["name"])}">'
            f'<div class="dx-card-head"><p class="dx-model">{escape(c["name"])} <span>· {escape(c["track"].lower())} · synthetic sample</span></p>'
            f'<span class="dx-code" aria-label="Profile code {escape(code)}">{escape(code)}</span></div>'
            f'<div class="dx-hero">{pv.avatar(code, "dx-avatar")}<div class="dx-hero-text">'
            f'<p class="dx-hero-kicker">Your model is the</p><p class="dx-hero-name">{escape(pv.nickname(code))}</p>'
            f'<p class="dx-hero-family">{escape(pv.FAMILIES[fam][0])}</p>'
            f'<p class="dx-hero-traits">{escape(pv.traits(code))}</p></div></div>'
            f'<p class="dx-quote">“{escape(c["quote"])}”</p>'
            f'<ol class="dx-findings">{findings}</ol>'
            f'<div class="dx-bars">{"".join(view_bar(views[k]) for k in VIEW_ORDER)}'
            '<p class="dx-cap">Tick = expected for a model of this overall level</p></div>'
            f'<div class="dx-profile"><p class="dx-label">Behavioural profile <span>tendencies, not ability</span></p>'
            f'{"".join(axis_row(a) for a in c["axes"])}</div>'
            f'{failure_bar(c["failures"])}'
            f'<div class="dx-fix"><p class="dx-label">Priority 1 · {escape(c["fix"]["kind"])}</p>'
            f'<p><strong>{escape(c["fix"]["name"])}.</strong> {escape(c["fix"]["action"])}</p>'
            f'<p class="dx-gain">Expected: {escape(c["fix"]["gain"])}</p></div>'
            '</article>')


def types_grid():
    """Sixteen profiles in four families, after the family rows of an MBTI type chart."""
    rows = []
    for fam in pv.ORDER:
        name, blurb, good, risk = pv.FAMILIES[fam]
        codes = [c for c in pv.TYPES if pv.family(c) == fam]
        tiles = ''.join(f'<li style="{pv.style(c)}">{pv.avatar(c, "dx-avatar")}<b>{c}</b><span>{escape(pv.NICKNAMES[c])}</span></li>' for c in codes)
        rows.append(f'<div class="dx-family dx-fam--{fam.lower()}" style="--fam:{pv.FAMILY_COLOUR[fam]}"><div class="dx-family-text">'
                    f'<p class="dx-family-key">{fam[0]}··{fam[1]}</p><h4>{escape(name)}</h4><p>{escape(blurb)}</p>'
                    f'<p class="dx-family-edge"><span>Strong at</span> {escape(good)}<br><span>Watch for</span> {escape(risk)}</p></div>'
                    f'<ul class="dx-family-tiles">{tiles}</ul></div>')
    key = ''.join(f'<li><b>{l[0]}</b> {escape(l[1])} <i>/</i> <b>{r[0]}</b> {escape(r[1])}</li>' for _, _, _, l, r in pv.AXES)
    return ('<div class="dx-types" aria-labelledby="dx-types-title">'
            '<div class="dx-types-head"><h3 id="dx-types-title">Sixteen profiles, four families</h3>'
            '<p>The letters are borrowed from MBTI; their meanings are defined by this benchmark. Each axis shows the side '
            'a model leans to, so every model gets one of sixteen codes; the first and last letters set the family.</p>'
            f'<ul class="dx-types-key">{key}</ul></div>{"".join(rows)}</div>')


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
            f'{types_grid()}'
            '<p class="dx-disclaimer"><strong>Synthetic samples.</strong> Both cards were generated from fault-injected '
            'simulated policies to show the card’s format and logic; they are not results of any real model. '
            f'<a href="{escape(data["pdf"])}" target="_blank" rel="noopener">Full sample card (PDF, {escape(data["pdf_note"])}) '
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
