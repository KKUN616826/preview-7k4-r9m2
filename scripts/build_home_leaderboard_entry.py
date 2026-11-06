#!/usr/bin/env python3
"""Render the homepage leaderboard preview from data/leaderboard-results.json.

The homepage shows every model with reported scores, ranked by suite score;
the full table, success rates and pending entries stay on leaderboard.html.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import re
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


def ranks(models, view):
    """Competition ranking: tied scores share a rank, as on leaderboard.html."""
    score = lambda m: m['results'][view]['score']
    return {m['id']: 1 + sum(score(o) > score(m) for o in models) for m in models}


def render():
    data = json.loads((ROOT / 'data/leaderboard-results.json').read_text())
    labels = {v['key']: v['label'] for v in data['views']}
    reported = [m for m in data['models'] if all(m['results'][v]['score'] is not None for v in VIEWS)]
    scored_tasks = sum(len(v['tasks']) for v in data['views'])
    first = VIEWS[0]
    rank = ranks(reported, first)
    rows = []
    for model in sorted(reported, key=lambda m: -m['results'][first]['score']):
        scores = {v: model['results'][v]['score'] for v in VIEWS}
        attrs = ''.join(f' data-{v}="{scores[v]}"' for v in VIEWS)
        cells = ''.join(f'<td class="hl-score" data-col="{v}">{scores[v]:.2f}</td>' for v in VIEWS)
        mark = (f'<img src="{escape(model["icon"])}" width="20" height="20" alt="">' if model.get('icon')
                else f'<span class="hl-monogram" aria-hidden="true">{escape(model["name"][:1])}</span>')
        rows.append(
            f'<tr{attrs}><td class="hl-rank">{rank[model["id"]]}</td>'
            f'<th scope="row"><span class="hl-model">{mark}{escape(model["name"])}</span></th>'
            f'<td class="hl-type">{escape(data["paradigms"][model["paradigm"]])}</td>{cells}</tr>')
    tabs = ''.join(
        f'<button type="button" data-hl-view="{v}" aria-pressed="{str(v == first).lower()}">{escape(labels[v])}</button>'
        for v in VIEWS)
    sort_attr = {v: ' aria-sort="descending"' if v == first else '' for v in VIEWS}
    heads = ''.join(
        f'<th scope="col" class="hl-score" data-col="{v}"{sort_attr[v]}>{escape(labels[v])}</th>'
        for v in VIEWS)
    return (
        f'<section class="academic-section home-leaderboard" id="top-ten" data-view="{first}" aria-labelledby="home-leaderboard-title">'
        '<div class="hl-head"><div><p class="home-eyebrow">Leaderboard</p>'
        '<h2 id="home-leaderboard-title">How current models score</h2>'
        f'<p>Score (0–100) on each suite, from the original {scored_tasks}-task snapshot; the added tasks are not yet scored. '
        f'{len(reported)} of {len(data["models"])} listed models have reported results.</p></div>'
        f'<div class="hl-tabs" role="group" aria-label="Rank by suite">{tabs}</div></div>'
        '<div class="hl-table-wrap"><table class="hl-table"><thead><tr><th scope="col" class="hl-rank">#</th>'
        f'<th scope="col">Model</th><th scope="col" class="hl-type">Type</th>{heads}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        '<a class="home-link-button" href="leaderboard.html">Full leaderboard with success rates <span aria-hidden="true">→</span></a>'
        '</section>')


def main():
    entry = render()
    for relative in ['index.html', 'scripts/research_intro.html']:
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
