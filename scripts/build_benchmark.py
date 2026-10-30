#!/usr/bin/env python3
"""Build the benchmark workspace without rebuilding the homepage or media.

Navigation and catalog content: data/benchmark-navigation.json.
Existing task content: scripts/benchmark/<case>.html.
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
                     f'<div class="workspace-group-row"><a href="{prefix}benchmark/{slug}.html"{active}>'
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


def detail(suite, case):
    content = (ROOT / f'scripts/benchmark/{case["id"]}.html').read_text()
    breadcrumb = (f'<div class="workspace-breadcrumb"><a href="../benchmark.html">Benchmark</a> / '
                  f'<a href="../benchmark/{suite["slug"]}.html">{suite["name"]}</a> / {case["id"]}</div>')
    content = re.sub(r'<div class="breadcrumb">.*?</div>', breadcrumb, content, count=1)
    content = content.replace('href="index.html">Browse all 15 tasks',
                              f'href="../benchmark/{suite["slug"]}.html">Back to {suite["name"]}')
    order = [c['id'] for s in json.loads((ROOT / 'data/benchmark-navigation.json').read_text()) for c in s['cases']]
    index = order.index(case['id'])
    previous = f'<a href="{order[index-1]}.html">← Previous task · {order[index-1]}</a>' if index else '<span></span>'
    following = f'<a href="{order[index+1]}.html">Next task · {order[index+1]} →</a>' if index+1 < len(order) else '<span></span>'
    footer = f'<nav class="task-footer" aria-label="Adjacent tasks">{previous}<a href="../benchmark/{suite["slug"]}.html">Back to {suite["name"]}</a>{following}</nav>'
    content = re.sub(r'<nav class="task-footer".*?</nav>', lambda _: footer, content, count=1)
    return content


def page(suites, current, title, content, prefix='', is_detail=False):
    if current == 'overview':
        from benchmark_overview import document
        return document(content)
    header = (ROOT / 'scripts/benchmark/header.html').read_text()
    header = re.sub(r'(href|src)="(?!https?:|#)([^"]+)"',
                    lambda m: f'{m[1]}="{prefix}{m[2]}"', header)
    nav = navigation(suites, current, prefix)
    styles = ''.join(f'<link rel="stylesheet" href="{prefix}{name}">' for name in [
        'tasks/task-pages.css', 'media/site-shell.css?v=white-canvas-1',
        'tasks/benchmark-catalog.css?v=2',
        *(['tasks/task-detail.css?v=case-1', 'tasks/benchmark-expansion.css?v=1'] if is_detail else []),
        'tasks/benchmark-workspace.css?v=1',
        *(['tasks/benchmark-task-rows.css?v=1'] if current in {s['slug'] for s in suites} else [])])
    body_class = 'benchmark-workspace' + (' task-detail' if is_detail else '')
    if current in {suite['slug'] for suite in suites}:
        body_class += ' benchmark-category'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
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


def main(overview_only=False):
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    (ROOT / 'benchmark').mkdir(exist_ok=True)
    (ROOT / 'benchmark.html').write_text(page(suites, 'overview', 'Benchmark', overview(suites)))
    if overview_only:
        print('Built Benchmark landing page only.')
        return
    for suite in suites:
        (ROOT / f'benchmark/{suite["slug"]}.html').write_text(
            page(suites, suite['slug'], suite['name'], category(suite), '../'))
        for case in suite['cases']:
            (ROOT / f'tasks/{case["id"]}.html').write_text(
                page(suites, case['id'], case['title'], detail(suite, case), '../', True))
    print(f'Built benchmark overview, {len(suites)} suites and {sum(len(s["cases"]) for s in suites)} task pages.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overview-only', action='store_true', help='Rebuild benchmark.html only')
    main(overview_only=parser.parse_args().overview_only)
