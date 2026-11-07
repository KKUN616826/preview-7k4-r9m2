#!/usr/bin/env python3
"""Render the homepage leaderboard preview from data/leaderboard-results.json.

One column per board (VLA / WAM, coding agents): the top five by Overall score on
Clean once results exist, otherwise the first release batch. Details stay on leaderboard.html.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import re
from datetime import date
from build_home_tasks import ensure_head_assets

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ('mind', 'act', 'coupling')


class SectionBounds(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.depth = 0
        self.bounds = None

    def source_offset(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag != 'section':
            return
        if self.depth:
            self.depth += 1
        elif dict(attrs).get('id') == 'top-ten':
            self.start = self.source_offset()
            self.depth = 1

    def handle_endtag(self, tag):
        if tag == 'section' and self.depth:
            self.depth -= 1
            if not self.depth:
                self.bounds = (self.start, self.source_offset() + len('</section>'))


def monogram(name):
    return ''.join(ch for ch in name if ch.isalnum())[:2]


def mark(model):
    if model['icon']:
        return f'<img src="{escape(model["icon"])}" width="22" height="22" alt="" loading="lazy" decoding="async">'
    return f'<span class="hl-monogram" aria-hidden="true">{escape(monogram(model["name"]))}</span>'


def column(data, track):
    models = [m for m in data['models'] if m['track'] == track['key']]
    reported = sorted([m for m in models if m['results']], key=lambda m: -m['results']['clean']['overall']['score'])
    head = (f'<div class="hl-col-head"><h3>{escape(track["title"].replace(" Leaderboard", ""))}</h3>'
            f'<p>{track["cases_per_cell"]} cases per task × difficulty</p></div>')
    if reported:
        rows = ''.join(
            f'<li><span class="hl-rank">{1 + sum(o["results"]["clean"]["overall"]["score"] > m["results"]["clean"]["overall"]["score"] for o in reported)}</span>'
            f'<span class="hl-model">{mark(m)}{escape(m["name"])}</span>'
            f'<span class="hl-score">{m["results"]["clean"]["overall"]["score"]:.2f}</span></li>' for m in reported[:5])
        return f'<div class="hl-col">{head}<ol class="hl-list">{rows}</ol><p class="hl-foot">Overall score · Clean</p></div>'
    first = date.fromisoformat(data['first_release'])
    batch = [m for m in models if m.get('release') == data['first_release']]
    queued = [m for m in models if not m.get('release')]
    rows = ''.join(f'<li><span class="hl-model">{mark(m)}{escape(m["name"])}</span>'
                   f'<span class="hl-org">{escape(m["org"])}</span></li>' for m in batch)
    foot = f'+ {len(queued)} more queued' if queued else ''
    return (f'<div class="hl-col">{head}<p class="hl-when">Results on {first.day} {first.strftime("%B")}</p>'
            f'<ul class="hl-list">{rows}</ul><p class="hl-foot">{foot}</p></div>')


def render():
    data = json.loads((ROOT / 'data/leaderboard-results.json').read_text())
    any_results = any(m['results'] for m in data['models'])
    lead = ('End-to-end models and coding agents are ranked separately: they run different case counts and interfaces.'
            if any_results else
            'Official results start on 11 November. End-to-end models and coding agents are ranked separately, '
            'because they run different case counts and interfaces.')
    return (
        '<section class="academic-section home-leaderboard" id="top-ten" aria-labelledby="home-leaderboard-title">'
        '<div class="hl-head"><div><p class="home-eyebrow">Leaderboard</p>'
        '<h2 id="home-leaderboard-title">Two boards, one benchmark</h2>'
        f'<p>{escape(lead)}</p></div></div>'
        f'<div class="hl-cols">{"".join(column(data, t) for t in data["tracks"])}</div>'
        '<a class="home-link-button" href="leaderboard.html">Open the leaderboard <span aria-hidden="true">→</span></a>'
        '</section>')


def main():
    entry = render()
    for relative in ['index.html']:
        path = ROOT / relative
        source = path.read_bytes().decode()
        parser = SectionBounds(source)
        parser.feed(source)
        if not parser.bounds:
            raise ValueError(f'Missing homepage leaderboard in {relative}')
        start, end = parser.bounds
        source = source[:start] + entry + source[end:]
        source = source.replace('href="#leaderboard"', 'href="leaderboard.html"')
        if relative == 'index.html':
            source = re.sub(r'<(?:link|script)[^>]+(?:href|src)="scripts/view-leaderboard\.(?:css|js)[^"]*"[^>]*>(?:</script>)?', '', source)
            source = re.sub(r'\n?<link[^>]+href="scripts/home-leaderboard-entry.css[^"]*"[^>]*>\n?', '\n', source)
            source = ensure_head_assets(source)
        path.write_bytes(source.encode())
    print('Built homepage leaderboard preview.')


if __name__ == '__main__':
    main()
