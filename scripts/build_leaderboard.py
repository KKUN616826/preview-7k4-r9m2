#!/usr/bin/env python3
"""Build leaderboard.html from data/leaderboard-results.json.

End-to-end models (VLA / WAM) and coding agents are ranked on separate boards:
they run different case counts (50 vs 5 per task x difficulty) and interfaces.
A model's `results` stays null until its official run is published; such models
are listed with their release date or queue position and are never ranked.

Published results use:
  "results": {"clean":  {"overall": {"score": S, "success": R}, "mind": {...}, "act": {...}, "coupling": {...}},
              "random": {... same keys ...},
              "valid":  {"clean": N, "random": N}}
Scores are 0-100 means; success is the percentage of cases scoring 100.
"""
from leaderboard_stage import render as render_stage
import hashlib
import json
import math
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ['scripts/leaderboard-explorer.css', 'scripts/leaderboard-stage.css', 'scripts/leaderboard-boards.css',
          'scripts/leaderboard-boards.js', 'scripts/leaderboard-stage-motion.js']


def e(value):
    return escape(str(value), quote=True)


def load():
    data = json.loads((ROOT / 'data/leaderboard-results.json').read_text())
    assert data['schema_version'] == 2
    ids = [m['id'] for m in data['models']]
    assert len(ids) == len(set(ids)), 'duplicate model id'
    tracks = {t['key'] for t in data['tracks']}
    settings = [s['key'] for s in data['settings']]
    views = [v['key'] for v in data['views']]
    for m in data['models']:
        assert m['track'] in tracks and m['type'] in data['types'], m['id']
        assert (m['type'] == 'agent') == (m['track'] == 'agent'), f'{m["id"]}: agents belong on the agent board'
        assert not m['icon'] or (ROOT / m['icon']).is_file(), f'{m["id"]}: missing icon {m["icon"]}'
        assert m['results'] or m.get('release') or m.get('queue'), f'{m["id"]}: needs results, a release date or a queue position'
        if m['results']:
            for s in settings:
                for v in views:
                    for metric in ('score', 'success'):
                        value = m['results'][s][v][metric]
                        assert isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 100, (m['id'], s, v, metric)
    return data


def release_label(model):
    if model.get('release'):
        d = date.fromisoformat(model['release'])
        return f'{d.day} {d.strftime("%b")}'
    return f'Queue #{model["queue"]}'


def icon_html(model, size):
    if model['icon']:
        return f'<img src="{e(model["icon"])}" width="{size}" height="{size}" alt="" loading="lazy" decoding="async">'
    return f'<span class="lb-icon-fallback" aria-hidden="true">{e(model["name"][:2])}</span>'


def board(data, track):
    views = data['views']
    models = [m for m in data['models'] if m['track'] == track['key']]
    reported = sorted([m for m in models if m['results']], key=lambda m: -m['results']['clean']['overall']['score'])
    pending = sorted([m for m in models if not m['results']], key=lambda m: (m.get('release') is None, m.get('release') or '', m.get('queue') or 0))
    sort_attr = {v['key']: ' aria-sort="descending"' if v['key'] == 'overall' else '' for v in views}
    arrow = {v['key']: '↓' if v['key'] == 'overall' else '↕' for v in views}
    heads = ''.join(
        f'<th scope="col" class="lb-number" data-col="{v["key"]}"{sort_attr[v["key"]]}>'
        f'<button type="button" data-sort="{v["key"]}" title="{e(v["description"])}">{e(v["label"])}'
        f'<span class="lb-sort-arrow" aria-hidden="true">{arrow[v["key"]]}</span></button></th>' for v in views)
    rows = []
    for m in reported + pending:
        cells = []
        for v in views:
            if m['results']:
                attrs = ''.join(f' data-{s}-{metric}="{m["results"][s][v["key"]][metric]}"'
                                for s in ('clean', 'random') for metric in ('score', 'success'))
                cells.append(f'<td class="lb-number" data-col="{v["key"]}"{attrs}>'
                             f'{m["results"]["clean"][v["key"]]["score"]:.2f}</td>')
            else:
                cells.append(f'<td class="lb-number lb-pending-cell" data-col="{v["key"]}">—</td>')
        status = ('<span class="lb-status lb-status-done">Reported</span>' if m['results'] else
                  f'<span class="lb-status{" lb-status-date" if m.get("release") else ""}">{e(release_label(m))}</span>')
        rows.append(
            f'<tr class="lb-result{"" if m["results"] else " lb-pending"}" data-model="{e(m["id"])}">'
            f'<td class="lb-rank">{"" if m["results"] else "—"}</td>'
            f'<th scope="row" class="lb-model-cell"><span class="lb-model-name">{icon_html(m, 24)}<span>{e(m["name"])}</span></span></th>'
            f'<td><span class="lb-paradigm" data-family="{e(m["type"])}">{e(data["types"][m["type"]])}</span></td>'
            f'<td class="lb-org">{e(m["org"])}</td>{"".join(cells)}<td class="lb-status-cell">{status}</td></tr>')
    total = track['cases_per_setting']
    settings = ''.join(f'<button type="button" data-setting="{s["key"]}" aria-pressed="{str(s["key"] == "clean").lower()}" '
                       f'title="{e(s["description"])}">{e(s["label"])}</button>' for s in data['settings'])
    note = ''
    if track['key'] == 'agent':
        note = ('<p class="lb-board-note">Coding agents run a 5-case subset of every task × difficulty (450 per setting); '
                'end-to-end models run all 50 (4,500). Because case counts and interfaces differ, the two boards are ranked '
                'separately and their scores should not be compared. We plan to extend agents to the full setting as resources allow.</p>')
    return (
        f'<section class="lb-board" id="board-{e(track["key"])}" data-board="{e(track["key"])}" data-sort="overall" data-setting="clean" data-metric="score" '
        f'aria-labelledby="board-{e(track["key"])}-title">'
        f'<div class="lb-board-head"><div><h3 id="board-{e(track["key"])}-title">{e(track["title"])}</h3>'
        f'<p>{e(track["summary"])} {track["cases_per_cell"]} cases per task × difficulty · {total:,} per setting.</p></div>'
        '<div class="lb-board-controls">'
        f'<div class="lb-toggle" role="group" aria-label="Setting">{settings}</div>'
        '<div class="lb-toggle" role="group" aria-label="Metric"><button type="button" data-metric="score" aria-pressed="true">Score</button>'
        '<button type="button" data-metric="success" aria-pressed="false">Success %</button></div></div></div>'
        '<div class="lb-table-scroll" role="region" tabindex="0" aria-label="' + e(track['title']) + '; scroll for all columns">'
        f'<table class="lb-table lb-board-table"><caption class="lb-sr-only">{e(track["title"])}</caption>'
        '<thead><tr><th scope="col" class="lb-rank-heading">Rank</th><th scope="col" class="lb-model-heading">Model</th>'
        f'<th scope="col">Type</th><th scope="col">Contributor</th>{heads}<th scope="col">Results</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>{note}</section>')


def schedule(data):
    first = [m for m in data['models'] if m.get('release') == data['first_release']]
    queue = sorted([m for m in data['models'] if not m['results'] and m.get('queue')], key=lambda m: m['queue'])
    chip = lambda m: f'<li>{icon_html(m, 20)}<span>{e(m["name"])}</span></li>'
    d = date.fromisoformat(data['first_release'])
    return ('<section class="lb-schedule" aria-labelledby="lb-schedule-title"><h3 id="lb-schedule-title">Evaluation schedule</h3>'
            f'<div class="lb-schedule-step"><p><strong>{d.day} {d.strftime("%B")}</strong> First results</p><ul>{"".join(chip(m) for m in first)}</ul></div>'
            f'<div class="lb-schedule-step"><p><strong>Then</strong> {e(data["cadence"])} In order:</p><ol>{"".join(chip(m) for m in queue)}</ol></div>'
            '</section>')


def main():
    data = load()
    header = (ROOT / 'scripts/benchmark/header.html').read_text().replace(' aria-current="page"', '')
    header = header.replace('href="leaderboard.html"', 'href="leaderboard.html" aria-current="page"')
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    boards = ''.join(board(data, t) for t in data['tracks'])
    template = (ROOT / 'scripts/leaderboard-page.html').read_text()
    for key, value in {'HEADER': header, 'BOARDS': boards, 'SCHEDULE': schedule(data), 'DATA': payload,
                       'STAGE': render_stage(data), 'PROTOCOL_VERSION': e(data['protocol']['version']),
                       'SCORING_VERSION': e(data['protocol']['scoring']), 'UPDATED': e(data['updated'])}.items():
        template = template.replace('__' + key + '__', value)
    leftover = re.findall(r'__[A-Z_]+__', template)
    assert not leftover, f'unreplaced placeholders: {leftover}'
    for asset in ASSETS:
        version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:10]
        template = re.sub(re.escape(asset) + r'(?:\?v=[^"\s]+)?"', asset + '?v=' + version + '"', template)
    (ROOT / 'leaderboard.html').write_text(template, newline='\n')
    reported = sum(1 for m in data['models'] if m['results'])
    print(f'Built leaderboard: {len(data["models"])} models, {reported} with published results.')


if __name__ == '__main__':
    main()
