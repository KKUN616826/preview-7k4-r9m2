#!/usr/bin/env python3
"""Check the generated site before publishing (2026-11 redesign).

The previous homepage checks live in validate_legacy.py; they assert the old
showcase template and no longer apply.
"""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'leaderboard.html', 'protocol.html', 'benchmark.html', 'resources.html', 'news.html']
# Words that only make sense internally; they must not reach visible page text.
HASH_ROUTES = {'easy', 'medium', 'hard'}  # difficulty state on task pages, handled by task-difficulty.js
BANNED = ['coming soon', 'to be announced', 'snapshot', 'table 6', 'not provided', 'physco', 'to be specified', 'pending', 'xx%']


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.text, self.skip = [], [], [], 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.links += [a[k] for k in ('src', 'href', 'poster', 'srcset') if a.get(k)]
        if 'id' in a:
            self.ids.append(a['id'])
        if tag in ('script', 'style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def check(relative):
    path = ROOT / relative
    page = Page()
    page.feed(path.read_text())
    dupes = {i for i in page.ids if page.ids.count(i) > 1}
    assert not dupes, f'{relative}: duplicate ids {sorted(dupes)[:5]}'
    for link in page.links:
        link = link.split()[0]
        url = urlsplit(link)
        if url.scheme or url.netloc or link.startswith(('mailto:', 'data:')):
            continue
        if url.path:
            target = (path.parent / unquote(url.path)).resolve()
            assert target.is_file(), f'{relative}: missing {link}'
        elif url.fragment and url.fragment not in HASH_ROUTES:
            assert unquote(url.fragment) in page.ids, f'{relative}: missing anchor #{url.fragment}'
    visible = ' '.join(page.text).lower()
    for word in BANNED:
        assert word not in visible, f'{relative}: internal wording "{word}" in visible text'
    for needed in ('media/tokens.css', 'media/components.css', 'class="site-header"', 'class="site-footer"'):
        assert needed in path.read_text(), f'{relative}: missing shared shell ({needed})'
    return len(page.links)


def main():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    tasks = [c['id'] for s in suites for c in s['cases']]
    pages = PAGES + [f'tasks/{t}.html' for t in tasks]
    links = sum(check(p) for p in pages)
    print(f'PASS: {len(pages)} pages, {links} local links and anchors, shared shell, no internal wording')

    index = (ROOT / 'index.html').read_text()
    assert '<style' not in index, 'index.html must not contain inline style blocks'
    assert index.count('<h1') == 1 and 'Mind2Act World</h1>' in index
    for t in tasks:
        assert (ROOT / f'media/thumbs/{t}.webp').is_file(), t
        assert f'tasks/{t}.html' in index and f'tasks/{t}.html' in (ROOT / 'benchmark.html').read_text(), t
    from build_leaderboard import load
    board = load()
    scored = [m for m in board['models'] if any(r.get('score') is not None for r in m['results'].values())]
    lb = (ROOT / 'leaderboard.html').read_text()
    assert lb.count('<tr data-type=') == 2 * len(scored), 'matrix and ranking should list every scored model'
    print(f'PASS: homepage, {len(tasks)} thumbnails and task links, {len(scored)} scored models on the leaderboard')

    records = json.loads((ROOT / 'data/showcase-cases.json').read_text())
    sync = json.loads((ROOT / 'data/case-sync.json').read_text())
    assert sync['case_count'] == len(records)
    for asset in sync['media']:
        p = ROOT / asset['path']
        assert p.stat().st_size == asset['bytes'], 'Size mismatch: ' + asset['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == asset['sha256'], 'Hash mismatch: ' + asset['path']
    previews = json.loads((ROOT / 'data/task-previews.json').read_text())['previews']
    for item in previews:
        for key in ('source', 'preview', 'poster'):
            asset = ROOT / item[key]
            assert hashlib.sha256(asset.read_bytes()).hexdigest() == item[key + 'Sha256'], item[key]
    print(f'PASS: {len(sync["media"])} media hashes and {len(previews)} preview assets')

    for font in ['inter/Inter-latin-wght.woff2', 'jetbrains-mono/JetBrainsMono-latin-wght.woff2']:
        assert (ROOT / 'media/fonts' / font).read_bytes().startswith(b'wOF2'), font
    assert (ROOT / 'media/fonts/inter/OFL.txt').is_file() and (ROOT / 'media/fonts/jetbrains-mono/OFL.txt').is_file()
    assert (ROOT / 'media/fonts/Sora-OFL.txt').is_file()
    print('PASS: self-hosted fonts and licences')

    from validate_hero import validate_hero
    validate_hero(index)


if __name__ == '__main__':
    main()
