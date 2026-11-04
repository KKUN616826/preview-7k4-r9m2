#!/usr/bin/env python3
"""Build index.html from scripts/home.html (2026-11 redesign).

Reuses the CP05 hero player (hero_demo.render) and the task sphere
(build_capability_map.render). Everything else on the page is rendered here
from data files, so the template holds no copied numbers.
"""
import html
import json
from pathlib import Path

from hero_demo import render as render_hero
from build_capability_map import render as render_capability_map
from site_shell import apply_shell

ROOT = Path(__file__).resolve().parents[1]
e = html.escape

SUITE_KEYS = {'mind': 'mind', 'act': 'act', 'mind2act': 'm2a', 'coupling': 'm2a'}
SUITE_EXAMPLE = {'mind': 'P', 'act': 'PR3', 'mind2act': 'CP05'}

ICONS = {
    'tasks': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
    'levels': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20V14M10 20V9M16 20V4"/><path d="M2 20h20"/></svg>',
    'suites': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/></svg>',
    'models': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="7" width="14" height="12" rx="3"/><path d="M12 3v4M9 12h.01M15 12h.01M9 16h6"/></svg>',
    'code': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></svg>',
    'spec': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 12h7M9 16h7"/></svg>',
    'data': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 4H7a3 3 0 0 0-3 3v2a2 2 0 0 1-2 2 2 2 0 0 1 2 2v2a3 3 0 0 0 3 3h1M16 4h1a3 3 0 0 1 3 3v2a2 2 0 0 0 2 2 2 2 0 0 0-2 2v2a3 3 0 0 1-3 3h-1"/></svg>',
    'board': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 17V9h4v8M10 17V4h4v13M15 17v-6h4v6"/></svg>',
    'copy': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/></svg>',
}

BIBTEX = """@misc{huang2026mind2act,
  title  = {Mind2Act World: Benchmarking Robot Mind, Physical Act, and Mind--Act Coordination in Robotic Manipulation},
  author = {Huang, Yuzhi and Lin, Junchao and Huang, Jiazhen and Xiong, Ziyi and L{\\"u}, Yuankun},
  year   = {2026},
  note   = {Project page: https://kkun616826.github.io/preview-7k4-r9m2/}
}"""


def suites():
    return json.loads((ROOT / 'data/benchmark-navigation.json').read_text())


def thumb(task_id):
    return f'media/thumbs/{task_id}.webp'


def model_logo(model):
    if model.get('icon'):
        return f'<span class="model-logo"><img src="{e(model["icon"])}" alt="" width="14" height="14"></span>'
    initials = ''.join(part[0] for part in model['name'].replace('-', ' ').split()[:2]).upper()
    return f'<span class="model-logo"><b>{e(initials)}</b></span>'


def scored_models(data, view):
    rows = []
    for model in data['models']:
        result = (model.get('results') or {}).get(view) or {}
        if result.get('score') is None or model['name'].lower().startswith('to be'):
            continue
        rows.append((model, result))
    return sorted(rows, key=lambda item: -item[1]['score'])


def evaluated_count(data):
    return sum(1 for m in data['models'] if any(((m.get('results') or {}).get(k) or {}).get('score') is not None for k in ('mind', 'act', 'coupling')))


def render_leaderboard_preview(data):
    tabs, panels = [], []
    for index, view in enumerate(data['views']):
        key, label = view['key'], view['label']
        suite = SUITE_KEYS[key]
        selected = index == 0
        tabs.append(f'<button type="button" role="tab" id="lbp-tab-{key}" aria-controls="lbp-{key}" aria-selected="{str(selected).lower()}" data-suite="{suite}">{e(label)}</button>')
        rows = []
        for rank, (model, result) in enumerate(scored_models(data, key)[:5], 1):
            paradigm = data['paradigms'].get(model.get('paradigm'), model.get('paradigm', ''))
            rows.append(
                f'<li class="lbp-row"><span class="rank{" rank--" + str(rank) if rank <= 3 else ""}">{rank}</span>'
                f'{model_logo(model)}<span class="lbp-name">{e(model["name"])}</span>'
                f'<span class="badge badge--plain">{e(paradigm)}</span>'
                f'<span class="bar"><i style="width:{result["score"]:.2f}%"></i></span>'
                f'<span class="lbp-score num">{result["score"]:.2f}</span></li>'
            )
        panels.append(
            f'<div class="lbp-panel" role="tabpanel" id="lbp-{key}" aria-labelledby="lbp-tab-{key}" data-suite="{suite}"{"" if selected else " hidden"}>'
            f'<p class="lbp-desc">{e(view["description"])} Score 0–100.</p><ol class="lbp-list">{"".join(rows)}</ol></div>'
        )
    return (
        '<div class="card lbp"><div class="lbp-head">'
        f'<div class="tabs" role="tablist" aria-label="Leaderboard view">{"".join(tabs)}</div>'
        '<span class="meta-line"><span class="lbp-col">Score</span></span></div>'
        + ''.join(panels) +
        '<div class="lbp-foot"><a class="btn-ghost" href="leaderboard.html">Full leaderboard →</a></div></div>'
    )


def render_suite_cards(nav):
    cards = []
    for suite in nav:
        key = SUITE_KEYS[suite['slug']]
        example = SUITE_EXAMPLE[suite['slug']]
        cards.append(
            f'<a class="card suite-card" data-suite="{key}" href="benchmark.html?suite={suite["slug"]}">'
            f'<img src="{thumb(example)}" alt="" width="640" height="480" loading="lazy">'
            '<div class="card-body">'
            f'<span class="badge">{e(suite["name"])} · {len(suite["cases"])} tasks</span>'
            f'<h3>{e(suite["question"])}</h3>'
            f'<p>{e(suite["description"])}</p>'
            f'<span class="btn-ghost">Explore {e(suite["name"])} →</span></div></a>'
        )
    return ''.join(cards)


def render_marquee(nav):
    rows = []
    for index, suite in enumerate(nav):
        key = SUITE_KEYS[suite['slug']]
        tiles = ''.join(
            f'<a class="tile" href="tasks/{e(case["id"])}.html" tabindex="-1">'
            f'<img src="{thumb(case["id"])}" alt="" width="640" height="480" loading="lazy">'
            f'<span class="tile-label"><b>{e(case["id"])}</b> {e(case.get("nav_title") or case["title"])}</span></a>'
            for case in suite['cases']
        )
        direction = 'reverse' if index % 2 else 'forward'
        clone = tiles.replace('<a class="tile"', '<a class="tile" aria-hidden="true"')
        rows.append(
            f'<div class="marquee" data-suite="{key}" data-direction="{direction}">'
            f'<span class="marquee-label badge">{e(suite["name"])}</span>'
            f'<div class="marquee-track" aria-hidden="true">{tiles}{clone}</div></div>'
        )
    return ''.join(rows)


def render_task_index(nav):
    """Accessible list of every task (the marquee itself is decorative)."""
    items = ''.join(
        f'<li><a href="tasks/{e(c["id"])}.html">{e(c["id"])} · {e(c["title"])}</a></li>'
        for s in nav for c in s['cases']
    )
    return f'<ul class="sr-only">{items}</ul>'


def render_news():
    items = json.loads((ROOT / 'data/news.json').read_text())
    rows = ''.join(
        f'<li><time class="meta-line" datetime="{e(n["date"])}">{e(n["date"])}</time>'
        f'<span class="badge badge--plain">{e(n["type"])}</span><p>{n["html"]}</p></li>'
        for n in sorted(items, key=lambda n: n['date'], reverse=True)[:5]
    )
    return f'<div class="card news-card"><ol class="news-list">{rows}</ol><div class="news-foot"><a class="btn-ghost" href="news.html">All news →</a></div></div>'


def main():
    nav = suites()
    lb = json.loads((ROOT / 'data/leaderboard-results.json').read_text())
    task_count = sum(len(s['cases']) for s in nav)
    page = (ROOT / 'scripts/home.html').read_text()
    values = {
        'HERO_DEMO': render_hero(),
        'CAPABILITY_MAP': render_capability_map(),
        'LB_PREVIEW': render_leaderboard_preview(lb),
        'SUITE_CARDS': render_suite_cards(nav),
        'MARQUEE': render_marquee(nav),
        'TASK_INDEX': render_task_index(nav),
        'NEWS': render_news(),
        'BIBTEX': e(BIBTEX),
        'TASK_COUNT': str(task_count),
        'CONFIG_COUNT': str(task_count * 3),
        'SUITE_COUNT': str(len(nav)),
        'MODEL_COUNT': str(evaluated_count(lb)),
    }
    values.update({'ICON_' + k.upper(): v for k, v in ICONS.items()})
    for key, value in values.items():
        page = page.replace('__' + key + '__', value)
    leftover = [token for token in ('__HERO', '__CAPABILITY', '__LB_', '__ICON_') if token in page]
    assert not leftover, leftover
    page = apply_shell(page, current='', prefix='', body_class='ds')
    (ROOT / 'index.html').write_text(page, newline='\n')
    print(f'Built homepage: {task_count} tasks, {evaluated_count(lb)} evaluated models.')


if __name__ == '__main__':
    main()
