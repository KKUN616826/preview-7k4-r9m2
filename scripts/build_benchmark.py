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
    parts = ['<div class="workspace-page-head"><p class="workspace-kicker">Task explorer</p>'
             '<h1>Benchmark</h1><p class="benchmark-description">Explore task reasoning, physical execution, '
             'and how they work together in closed-loop robotic manipulation.</p>'
             '<p class="workspace-meta">15 tasks <span>·</span> 3 capability suites <span>·</span> Easy / Medium / Hard</p></div>',
             '<section class="workspace-section" aria-labelledby="capabilities-title">'
             '<h2 id="capabilities-title">Three views of robot capability</h2><div class="workspace-suites">']
    for suite in suites:
        parts.append(f'<a class="workspace-suite-link" href="benchmark/{suite["slug"]}.html">'
                     f'<h3>{suite["name"]}</h3><p class="workspace-suite-label">{suite["label"]}</p>'
                     f'<p>{suite["description"]}</p><span>Explore 5 tasks →</span></a>')
    parts.append('</div></section><section class="workspace-section" aria-labelledby="all-tasks-title">'
                 '<h2 id="all-tasks-title">All 15 tasks</h2>')
    for suite in suites:
        parts.append(f'<div class="workspace-task-index"><h3><a href="benchmark/{suite["slug"]}.html">{suite["name"]} →</a></h3><ul>')
        for case in suite['cases']:
            parts.append(f'<li><a href="tasks/{case["id"]}.html"><span class="workspace-case-id">{case["id"]}</span>'
                         f'<span>{e(case["title"])}</span><span aria-hidden="true">→</span></a></li>')
        parts.append('</ul></div>')
    parts.append('</section>')
    return ''.join(parts)


def category(suite):
    task_rows = ''.join(
        f'<article class="benchmark-task-row"><a class="benchmark-task-link" href="../tasks/{c["id"]}.html#easy">'
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
            f'<p class="workspace-meta">5 tasks <span>·</span> Easy / Medium / Hard</p></div>'
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
    return content


def page(suites, current, title, content, prefix='', is_detail=False):
    header = (ROOT / 'scripts/benchmark/header.html').read_text()
    header = re.sub(r'(href|src)="(?!https?:|#)([^"]+)"',
                    lambda m: f'{m[1]}="{prefix}{m[2]}"', header)
    nav = navigation(suites, current, prefix)
    styles = ''.join(f'<link rel="stylesheet" href="{prefix}{name}">' for name in [
        'tasks/task-pages.css', 'media/site-shell.css?v=unified-1',
        'tasks/benchmark-catalog.css?v=2',
        *(['tasks/task-detail.css?v=case-1'] if is_detail else []),
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


def main():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    (ROOT / 'benchmark').mkdir(exist_ok=True)
    (ROOT / 'benchmark.html').write_text(page(suites, 'overview', 'Benchmark', overview(suites)))
    for suite in suites:
        (ROOT / f'benchmark/{suite["slug"]}.html').write_text(
            page(suites, suite['slug'], suite['name'], category(suite), '../'))
        for case in suite['cases']:
            (ROOT / f'tasks/{case["id"]}.html').write_text(
                page(suites, case['id'], case['title'], detail(suite, case), '../', True))
    print('Built benchmark overview, 3 suites and 15 task pages.')


if __name__ == '__main__':
    main()
