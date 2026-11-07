#!/usr/bin/env python3
"""Render the homepage task grid from data/benchmark-navigation.json.

The grid is the homepage's single task overview: one row per suite, one
cover per task, each linking to its task page. It replaces the section with
id="tasks" in index.html and leaves every other module untouched.
"""
import hashlib
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = re.compile(r'<section[^>]*\bid="tasks"[^>]*>.*?</section>', re.S)
HEAD_ASSETS = re.compile(r'<!-- HOME_STRUCTURE_START -->.*?<!-- HOME_STRUCTURE_END -->\n?', re.S)
# Homepage stylesheets live in <head>; builders refresh their cache-busting versions in place.
HEAD_STYLESHEETS = ['media/site-shell.css', 'scripts/hero-intro.css', 'scripts/home-stats.css', 'scripts/intro-typography.css',
                    'scripts/intro-suite-cards.css', 'scripts/resources-cards.css', 'scripts/home-reveal.css',
                    'scripts/home-content-width.css']


def version(asset):
    return hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:10]


def refresh_stylesheet_versions(source):
    for asset in HEAD_STYLESHEETS:
        source = re.sub(rf'href="{re.escape(asset)}(?:\?v=[^"]*)?"', f'href="{asset}?v={version(asset)}"', source)
    return source


def ensure_head_assets(source):
    """Load the homepage structure assets in <head> so the first paint is styled.

    An existing block is replaced in place, so its position in the cascade never moves.
    """
    block = ('<!-- HOME_STRUCTURE_START -->'
             f'<link rel="stylesheet" href="scripts/home-structure.css?v={version("scripts/home-structure.css")}">'
             f'<script src="scripts/home-structure.js?v={version("scripts/home-structure.js")}" defer></script>'
             f'<script src="scripts/site-shell.js?v={version("scripts/site-shell.js")}" defer></script>'
             '<!-- HOME_STRUCTURE_END -->\n')
    if HEAD_ASSETS.search(source):
        source = HEAD_ASSETS.sub(lambda _: block, source, count=1)
    else:
        head_end = source.index('</head>')
        source = source[:head_end] + block + source[head_end:]
    return refresh_stylesheet_versions(source)


def clean_cover(case):
    """Prefer the clean rendered stills; media/benchmark-covers frames carry camera and episode overlays."""
    for level in ('medium', 'easy', 'hard'):
        still = f'media/benchmark-overview/{case["id"]}-{level}.jpg'
        if (ROOT / still).is_file():
            return still
    assert (ROOT / case['cover']).is_file(), f'missing cover for {case["id"]}'
    return case['cover']


def tile(case, slug, hidden=False):
    cid = escape(case['id'])
    focus = ' tabindex="-1"' if hidden else ''
    return (f'<li class="ht-tile ht-tile--{slug}"><a href="tasks/{cid}.html" title="{escape(case["title"])}"{focus}>'
            f'<img src="{escape(clean_cover(case))}" width="720" height="540" alt="" loading="lazy" decoding="async">'
            f'<span class="ht-tile-text"><span class="ht-id">{cid}</span>'
            f'<span class="ht-name">{escape(case["nav_title"])}</span></span></a></li>')


def render():
    """A single moving film strip of every task, then one link per suite.

    The suites themselves are introduced above (#introduction) and the full
    catalogue lives on benchmark.html, so the homepage only previews the range.
    The strip is duplicated once (hidden from assistive tech) for a seamless loop.
    """
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    total = sum(len(s['cases']) for s in suites)
    cases = [(case, escape(s['slug'])) for s in suites for case in s['cases']]
    track = ''.join(tile(c, slug) for c, slug in cases)
    echo = ''.join(tile(c, slug, hidden=True) for c, slug in cases)
    links = ''.join(
        f'<a class="ht-suite-link ht-suite-link--{escape(s["slug"])}" href="benchmark.html#suite-{escape(s["slug"])}">'
        f'<span class="ht-suite-dot" aria-hidden="true"></span><strong>{escape(s["name"])}</strong>'
        f'<span>{escape(s["label"])} · {len(s["cases"])} tasks</span><span aria-hidden="true">→</span></a>'
        for s in suites)
    return (
        '<section class="academic-section home-tasks" id="tasks" aria-labelledby="home-tasks-title">'
        '<div class="ht-head"><div><p class="home-eyebrow">Benchmark</p>'
        f'<h2 id="home-tasks-title">{total} tasks, three suites</h2>'
        '</div>'
        f'<a class="home-link-button" href="benchmark.html">Browse all {total} tasks <span aria-hidden="true">→</span></a></div>'
        f'<div class="ht-strip" role="region" aria-label="All {total} tasks" tabindex="0">'
        f'<ul class="ht-track">{track}</ul><ul class="ht-track ht-track--echo" aria-hidden="true">{echo}</ul></div>'
        f'<nav class="ht-suites" aria-label="Tasks by suite">{links}</nav>'
        '</section>')


def main():
    page = ROOT / 'index.html'
    source = page.read_bytes().decode()
    source, count = SECTION.subn(lambda _: render(), source, count=1)
    assert count == 1, 'index.html has no section with id="tasks"'
    page.write_bytes(ensure_head_assets(source).encode())
    print('Built homepage task grid.')


if __name__ == '__main__':
    main()
