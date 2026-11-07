#!/usr/bin/env python3
"""Validate current published pages without rebuilding legacy homepage templates."""
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.links.extend(attrs[key] for key in ('href', 'src', 'poster', 'data-src') if attrs.get(key))
        if attrs.get('id'):
            self.ids.append(attrs['id'])

def main():
    paths = [ROOT / name for name in ('index.html', 'leaderboard.html', 'protocol.html', 'benchmark.html', 'resources.html', 'news.html')]
    for folder in ('benchmark', 'tasks', 'models'):
        paths.extend(sorted((ROOT / folder).glob('*.html')))
    errors = []
    for path in paths:
        page = Page()
        page.feed(path.read_text())
        errors.extend(f'{path.relative_to(ROOT)}: duplicate id {key}' for key, count in Counter(page.ids).items() if count > 1)
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (ROOT if url.path.startswith('/') else path.parent) / unquote(url.path.lstrip('/'))
            if not target.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing {link}')
    catalog = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    tasks = [task for suite in catalog for task in suite['cases']]
    assert len(tasks) == len({task['id'] for task in tasks}) == 30
    for task in tasks:
        assert (ROOT / 'tasks' / f"{task['id']}.html").is_file()
    assert not errors, '\n'.join(errors)
    print(f'PASS: {len(paths)} published pages, unique IDs, local links/media and all 30 task destinations.')

if __name__ == '__main__':
    main()
