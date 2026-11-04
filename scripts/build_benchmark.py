#!/usr/bin/env python3
"""Build the benchmark workspace without rebuilding the homepage or media.

Navigation and catalog content: data/benchmark-navigation.json.
Existing task content: scripts/benchmark/<case>.html.
"""
import json
import re
from html import escape
from pathlib import Path

from site_shell import apply_shell

ROOT = Path(__file__).resolve().parents[1]
SUITE_KEY = {'mind': 'mind', 'act': 'act', 'mind2act': 'm2a'}


def e(value):
    return escape(str(value), quote=True)


def navigation(suites, current, prefix):
    active = ' aria-current="page"' if current == 'overview' else ''
    parts = [f'<nav aria-label="Benchmark navigation"><p class="workspace-nav-title">Benchmark</p>'
             f'<a class="workspace-overview" href="{prefix}benchmark.html"{active}>Overview</a>']
    for suite in suites:
        slug = suite['slug']
        selected = current == slug
        contains_current = selected or any(c['id'] == current for c in suite['cases'])
        active = ' aria-current="page"' if selected else ''
        parts.append(f'<section class="workspace-nav-group" data-group="{slug}"'
                     f' data-contains-current="{str(contains_current).lower()}">'
                     f'<div class="workspace-group-row" data-suite="{SUITE_KEY[slug]}"><a href="{prefix}benchmark.html?suite={slug}"{active}>'
                     f'{suite["name"]}<span class="workspace-count">{len(suite["cases"])}</span></a>'
                     f'<button type="button" aria-label="Toggle {suite["name"]} tasks"'
                     f' aria-expanded="true" aria-controls="nav-{slug}"><span aria-hidden="true">⌄</span></button></div>'
                     f'<ul id="nav-{slug}" class="workspace-case-list">')
        for case in suite['cases']:
            active = ' aria-current="page"' if current == case['id'] else ''
            parts.append(f'<li><a href="{prefix}tasks/{case["id"]}.html" title="{e(case["title"])}"{active}>'
                         f'<span class="workspace-case-id">{case["id"]}</span><span>{e(case.get("nav_title", case["title"]))}</span></a></li>')
        parts.append('</ul></section>')
    parts.append('</nav>')
    return ''.join(parts)


def card(case, prefix):
    # Keep the original card structure and benchmark-catalog.css hover rules.
    return (f'<article class="task-card"><a class="task-card-link" href="{prefix}tasks/{case["id"]}.html#easy">'
            f'<div class="task-cover"><img src="{prefix}{e(case["cover"])}" loading="lazy" alt="Task demonstration">'
            f'<div class="task-hover"><p>{e(case["summary"])}</p><span>View task <span aria-hidden="true">↗</span>'
            f'</span></div></div><h4><b>{case["id"]}</b> {e(case["title"])}</h4></a></article>')


def overview(suites):
    from benchmark_overview import render
    return render(suites)


def category(suite):
    task_rows = ''.join(
        f'<article class="benchmark-task-row"><a class="benchmark-task-link" href="../tasks/{c["id"]}.html#{c.get("initial_level", "easy")}">'
        f'<div class="benchmark-task-image"><img src="../{e(c.get("row_cover", c["cover"]))}" loading="lazy" '
        f'alt="{e(c["title"])} demonstration"></div>'
        f'<div class="benchmark-task-copy"><p class="benchmark-task-meta">{c["id"]} · {suite["name"]}</p>'
        f'<h3>{e(c["title"])}</h3><p class="benchmark-task-summary">{e(c["summary"])}</p>'
        '<span class="benchmark-task-entry">View task <span aria-hidden="true">→</span></span></div></a></article>'
        for c in suite['cases'])
    rows = ''.join(
        f'<div><dt><a href="../tasks/{c["id"]}.html">{c["id"]} · {e(c["title"])}</a></dt>'
        f'<dd>{e(c["summary"])}</dd></div>' for c in suite['cases'])
    return (f'<div class="workspace-page-head"><div class="workspace-breadcrumb"><a href="../benchmark.html">Benchmark</a> / {suite["name"]}</div>'
            f'<h1>{suite["name"]}</h1><p class="workspace-suite-subtitle">{suite["label"]}</p>'
            f'<p class="benchmark-description">{suite["description"]}</p>'
            f'<p class="workspace-meta">{len(suite["cases"])} tasks <span>·</span> Easy / Medium / Hard</p></div>'
            f'<div class="workspace-question"><h2>What does this suite test?</h2><p>{suite["question"]}</p></div>'
            f'<section class="workspace-section" aria-labelledby="suite-tasks-title"><h2 id="suite-tasks-title">Explore the tasks</h2>'
            f'<div class="benchmark-task-rows">{task_rows}</div></section>'
            '<section class="workspace-section" aria-labelledby="compare-title"><h2 id="compare-title">How the tasks differ</h2>'
            f'<dl class="workspace-comparison">{rows}</dl></section>')


def model_demos(case_id):
    """Model-family demo pages that exist for this task (rollouts/<model>-<ID>.html)."""
    models = json.loads((ROOT / 'data/leaderboard-results.json').read_text())['models']
    links = []
    for m in models:
        if not m.get('cases'):
            continue
        slug = Path(m['cases']).stem
        path = ROOT / f'rollouts/{slug}-{case_id}.html'
        if path.is_file():
            icon = f'<img src="../{e(m["icon"])}" alt="" width="14" height="14">' if m.get('icon') else ''
            links.append(f'<a class="demo-link" href="../rollouts/{slug}-{case_id}.html"><span class="model-logo">{icon}</span>{e(m["name"])}<span aria-hidden="true">→</span></a>')
    if not links:
        return ''
    return ('<section class="task-models" aria-labelledby="task-models-title"><h2 id="task-models-title">Model-family demos</h2>'
            '<p>Example runs by model families on this task. They illustrate behaviour and are not the scored evaluation runs.</p>'
            f'<div class="demo-links">{"".join(links)}</div></section>')


def adjacent(case_id, label, direction):
    if not case_id:
        return '<span></span>'
    arrow_l, arrow_r = ('← ', '') if direction == 'prev' else ('', ' →')
    return (f'<a class="card adjacent adjacent--{direction}" href="{case_id}.html"><img src="../media/thumbs/{case_id}.webp" alt="" width="96" height="72">'
            f'<span><small>{arrow_l}{label}{arrow_r}</small><b><span class="code-tag">{case_id}</span> {e(TITLES.get(case_id, ""))}</b></span></a>')


TITLES = {}


def detail(suite, case):
    content = (ROOT / f'scripts/benchmark/{case["id"]}.html').read_text()
    breadcrumb = (f'<div class="workspace-breadcrumb"><a href="../benchmark.html">Benchmark</a> / '
                  f'<a href="../benchmark.html?suite={suite["slug"]}">{suite["name"]}</a> / {case["id"]}</div>'
                  f'<div class="task-badges" data-suite="{SUITE_KEY[suite["slug"]]}"><span class="badge">{suite["name"]}</span><span class="code-tag">{case["id"]}</span></div>')
    content = re.sub(r'<div class="breadcrumb">.*?</div>', breadcrumb, content, count=1)
    content = re.sub(r'(<div class="dimension-list">)(.*?)(</div>)',
                     lambda m: m[1] + re.sub(r'<span>(\w)', lambda n: '<span class="badge">' + n[1].upper(), m[2]) + m[3],
                     content, flags=re.S)
    content = content.replace('<h2>Evaluation dimensions</h2>', '<h2>Evaluated on</h2>')
    order = [c['id'] for s in json.loads((ROOT / 'data/benchmark-navigation.json').read_text()) for c in s['cases']]
    index = order.index(case['id'])
    previous = order[index-1] if index else None
    following = order[index+1] if index+1 < len(order) else None
    footer = f'<nav class="task-footer" aria-label="Adjacent tasks">{adjacent(previous, "Previous", "prev")}{adjacent(following, "Next", "next")}</nav>'
    content = re.sub(r'<nav class="task-footer".*?</nav>', lambda _: model_demos(case['id']) + footer, content, count=1)
    return content


def catalog(suites):
    """benchmark.html: page hero, search, suite filter and one card per task."""
    total = sum(len(s['cases']) for s in suites)
    tabs = (f'<button type="button" role="tab" data-filter="all" aria-selected="true">All<span class="count">{total}</span></button>'
            + ''.join(f'<button type="button" role="tab" data-filter="{s["slug"]}" data-suite="{SUITE_KEY[s["slug"]]}" aria-selected="false">{s["name"]}<span class="count">{len(s["cases"])}</span></button>' for s in suites))
    groups = []
    for s in suites:
        cards = []
        for c in s['cases']:
            preview = next((f'media/task-previews/{c["id"]}/{lvl}.mp4' for lvl in ('medium', 'easy') if (ROOT / f'media/task-previews/{c["id"]}/{lvl}.mp4').is_file()), '')
            video = f' data-preview="{preview}"' if preview else ''
            haystack = e(' '.join([c['id'], c['title'], c.get('nav_title', ''), c['summary'], s['name']]).lower())
            cards.append(
                f'<a class="card task-card2" href="tasks/{c["id"]}.html" data-suite="{SUITE_KEY[s["slug"]]}" data-group="{s["slug"]}" data-search="{haystack}"{video}>'
                f'<span class="tc-media"><img src="media/thumbs/{c["id"]}.webp" alt="" width="640" height="480" loading="lazy">'
                f'<span class="code-tag">{c["id"]}</span><span class="badge">{s["name"]}</span></span>'
                f'<span class="tc-body"><b>{e(c["title"])}</b><span class="tc-goal">{e(c["summary"])}</span>'
                f'<span class="tc-levels" aria-label="Difficulty levels"><span>E</span><span>M</span><span>H</span></span></span></a>')
        groups.append(
            f'<section class="tc-group" data-group="{s["slug"]}" data-suite="{SUITE_KEY[s["slug"]]}" aria-labelledby="g-{s["slug"]}">'
            f'<header class="tc-group-head"><span class="dot"></span><h2 id="g-{s["slug"]}">{s["name"]}</h2><span class="meta-line">{len(s["cases"])} tasks</span>'
            f'<p>{e(s["question"])}</p></header><div class="tc-grid">{"".join(cards)}</div></section>')
    mosaic = ''.join(f'<img src="media/thumbs/{i}.webp" alt="" width="640" height="480">' for i in ['CP02', 'E2', 'PR5', 'CP08', 'FR2', 'M', 'DR3', 'CP06'])
    body = (
        f'<section class="page-hero"><div class="container"><p class="eyebrow">Benchmark</p><h1>{total} tasks</h1>'
        f'<p class="lead">Reason. Execute. Coordinate. Ten tasks in each of Mind, Act and Mind2Act, each at Easy, Medium and Hard.</p>'
        f'<p class="meta-line"><a href="protocol.html">Evaluation protocol →</a></p></div><div class="page-hero-mosaic" aria-hidden="true">{mosaic}</div></section>'
        '<section class="section catalog"><div class="container">'
        '<div class="catalog-tools"><label class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
        f'<span class="sr-only">Search tasks</span><input type="search" id="task-search" placeholder="Search {total} tasks — conveyor, keypad, cloth, timing…" autocomplete="off"><kbd>/</kbd></label>'
        f'<div class="tabs" role="tablist" aria-label="Suite">{tabs}</div></div>'
        f'<p class="catalog-status meta-line" id="catalog-status" role="status" aria-live="polite"></p>'
        + ''.join(groups) +
        '<p class="catalog-empty" id="catalog-empty" hidden>No task matches. Try another word or clear the search.</p>'
        '</div></section><script src="scripts/benchmark-catalog-ds.js?v=ds-20261104" defer></script>'
    )
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Benchmark · Mind2Act World</title><meta name="description" content="All Mind2Act World tasks across the Mind, Act and Mind2Act suites, each at Easy, Medium and Hard.">'
            '<link rel="icon" href="media/images/mind2act-favicon-v2.png"><link rel="stylesheet" href="scripts/benchmark-catalog-ds.css?v=ds-20261104">'
            f'</head>\n<body>\n<main id="main">{body}</main>\n</body></html>\n')
    return apply_shell(page, current='benchmark', prefix='')


def suite_redirect(suite):
    target = f'../benchmark.html?suite={suite["slug"]}'
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{e(suite["name"])} · Mind2Act World</title><link rel="canonical" href="{target}">'
            f'<meta http-equiv="refresh" content="0; url={target}"></head>'
            f'<body><p><a href="{target}">{e(suite["name"])} tasks</a></p></body></html>\n')


def page(suites, current, title, content, prefix='', is_detail=False):
    if current == 'overview':
        from benchmark_overview import document
        return document(content)
    header = (ROOT / 'scripts/benchmark/header.html').read_text()
    header = re.sub(r'(href|src)="(?!https?:|#)([^"]+)"',
                    lambda m: f'{m[1]}="{prefix}{m[2]}"', header)
    nav = navigation(suites, current, prefix)
    styles = ''.join(f'<link rel="stylesheet" href="{prefix}{name}">' for name in [
        'tasks/task-pages.css', 'media/site-shell.css?v=compact-header-1',
        'tasks/benchmark-catalog.css?v=2',
        *(['tasks/task-detail.css?v=case-1', 'tasks/benchmark-expansion.css?v=1'] if is_detail else []),
        'tasks/benchmark-workspace.css?v=1',
        *(['tasks/benchmark-task-rows.css?v=1'] if current in {s['slug'] for s in suites} else [])])
    body_class = 'benchmark-workspace' + (' task-detail' if is_detail else '')
    if current in {suite['slug'] for suite in suites}:
        body_class += ' benchmark-category'
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · Mind2Act World</title>'
            f'<link rel="icon" href="{prefix}media/images/mind2act-favicon-v2.png">{styles}</head>'
            f'<body class="{body_class}"><a class="workspace-skip" href="#benchmark-content">Skip to content</a>{header}'
            '<div class="workspace-mobile-bar"><button type="button" id="browse-tasks" aria-haspopup="dialog" aria-controls="task-drawer">Browse tasks</button>'
            f'<span>{e(title)}</span></div><div class="workspace-layout">'
            f'<aside class="workspace-sidebar">{nav}</aside>'
            f'<main class="benchmark-catalog workspace-content" id="benchmark-content">{content}</main></div>'
            '<dialog id="task-drawer" aria-labelledby="drawer-title"><div class="workspace-drawer-head">'
            '<h2 id="drawer-title">Browse tasks</h2><button type="button" id="close-task-drawer">Close</button></div>'
            '<div id="drawer-navigation"></div></dialog>'
            f'<script src="{prefix}scripts/benchmark-workspace.js?v=1" defer></script>'
            f'<script src="{prefix}scripts/site-shell.js?v=unified-1" defer></script></body></html>\n')
    html = html.replace('</head>', f'<link rel="stylesheet" href="{prefix}tasks/task-ds.css?v=ds-20261104"></head>', 1)
    return apply_shell(html, current='benchmark', prefix=prefix)


def main(overview_only=False):
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    TITLES.update({c['id']: c.get('nav_title', c['title']) for s in suites for c in s['cases']})
    (ROOT / 'benchmark').mkdir(exist_ok=True)
    (ROOT / 'benchmark.html').write_text(catalog(suites), newline='\n')
    if overview_only:
        print('Built Benchmark landing page only.')
        return
    for suite in suites:
        # Suite pages now redirect to the filtered catalogue; the URLs stay valid.
        (ROOT / f'benchmark/{suite["slug"]}.html').write_text(suite_redirect(suite))
        for case in suite['cases']:
            (ROOT / f'tasks/{case["id"]}.html').write_text(
                page(suites, case['id'], case['title'], detail(suite, case), '../', True))
    print(f'Built benchmark overview, {len(suites)} suites and {sum(len(s["cases"]) for s in suites)} task pages.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overview-only', action='store_true', help='Rebuild benchmark.html only')
    main(overview_only=parser.parse_args().overview_only)
