#!/usr/bin/env python3
"""Build only the standalone leaderboard from its versioned result snapshot."""
from leaderboard_stage import render as render_stage
import json
import re
import hashlib
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def e(value):
    return escape(str(value), quote=True)


def load():
    data = json.loads((ROOT / 'data/leaderboard-results.json').read_text())
    assert data['status'] == 'partial'
    ids = [m['id'] for m in data['models']]
    assert len(ids) == len(set(ids))
    for model in data['models']:
        assert model['paradigm'] in data['paradigms']
        for view in data['views']:
            result = model['results'][view['key']]
            for value in result.values():
                assert value is None or (isinstance(value, (float, int)) and math.isfinite(value) and 0 <= value <= 100)
        for key in ['icon', 'cases']:
            assert not model[key] or (ROOT / model[key]).is_file()
    return data


def number(value, metric):
    return '—' if value is None else f'{value:.{2 if metric == "score" else 1}f}'


def table(data):
    views = data['views']
    group_head = ''.join(f'<th colspan="2" scope="colgroup" data-group="{v["key"]}"><span>'
                         f'<img src="{v["icon"]}" width="20" height="20" alt="">{v["label"]}</span></th>' for v in views)
    metrics = ''.join(f'<th scope="col" data-group="{v["key"]}" data-sort-cell="{v["key"]}-{metric}" aria-sort="none">'
                      f'<button type="button" data-sort-view="{v["key"]}" data-sort-metric="{metric}" '
                      f'aria-label="Sort by {v["label"]} {label}">{label}<small>{unit}</small><span class="lb-sort-arrow" aria-hidden="true">↕</span></button></th>'
                      for v in views for metric, label, unit in [('score', 'Score', '0–100'), ('success', 'Success', '%')])
    rows = []
    for model in data['models']:
        mid = e(model['id'])
        icon = f'<img src="{model["icon"]}" width="23" height="23" alt="">' if model['icon'] else '<span class="lb-icon-fallback" aria-hidden="true">'+e(model['name'][:2])+'</span>'
        values = ''.join(f'<td data-group="{v["key"]}" data-value="{metric}" class="lb-number">{number(model["results"][v["key"]][metric], metric)}</td>' for v in views for metric in ['score', 'success'])
        rows.append(f'<tr class="lb-result" data-model="{mid}"><td class="lb-rank">—</td>'
                    f'<th scope="row" class="lb-model-cell"><button type="button" class="lb-model-button" data-details="{mid}" aria-expanded="false" aria-controls="detail-{mid}">'
                    f'{icon}<span>{e(model["name"])}</span></button></th>'
                    f'<td><span class="lb-paradigm">{e(data["paradigms"][model["paradigm"]])}</span></td>{values}'
                    f'<td><button type="button" class="lb-details-button" data-details="{mid}" aria-expanded="false" aria-controls="detail-{mid}">Details <span aria-hidden="true">+</span></button></td></tr>')
        detail_scores = ''.join(f'<div><h4>{v["label"]}</h4><p>{number(model["results"][v["key"]]["score"], "score")} <span>Score</span></p>'
                                f'<p>{number(model["results"][v["key"]]["success"], "success")} <span>Success %</span></p></div>' for v in views)
        has_results = any(r['score'] is not None or r['success'] is not None for r in model['results'].values())
        source = 'All-level results transcribed from the previously supplied Table 6.' if has_results else 'No result is reported in the current data snapshot.'
        demo = f'<a href="{e(model["cases"])}">View model-family demos ↗</a>' if model['cases'] else '<span>No demonstration link available.</span>'
        rows.append(f'<tr class="lb-detail-row" id="detail-{mid}" data-detail-model="{mid}" hidden><td colspan="10">'
                    f'<section class="lb-model-detail" aria-label="{e(model["name"])} details"><div class="lb-detail-head"><h3>{e(model["name"])}</h3>'
                    f'<span>{e(data["paradigms"][model["paradigm"]])}</span></div><div class="lb-detail-scores">{detail_scores}</div>'
                    f'<p>{source} Difficulty-specific results, exact evaluated checkpoints and run-level evidence are not included in this snapshot.</p>'
                    f'<div class="lb-detail-links">{demo}<a href="#protocol">How to read these results ↓</a></div>'
                    '<p class="lb-detail-note">Demo links show model-family examples; they are not evidence for the reported scores.</p></section></td></tr>')
    return ('<div class="lb-table-scroll" role="region" aria-label="Model results; scroll to view all metrics" tabindex="0">'
            '<table class="lb-table"><caption class="lb-sr-only">Mind2Act World results across Mind, Act and Mind2Act</caption>'
            '<thead><tr><th scope="col" rowspan="2" class="lb-rank-heading">Rank</th><th scope="col" rowspan="2" class="lb-model-heading">Model</th>'
            f'<th scope="col" rowspan="2">Paradigm</th>{group_head}<th scope="col" rowspan="2">Explore</th></tr><tr>{metrics}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def main():
    data = load()
    header = (ROOT / 'scripts/benchmark/header.html').read_text().replace(' aria-current="page"', '')
    header = header.replace('href="leaderboard.html"', 'href="leaderboard.html" aria-current="page"')
    options = ''.join(f'<option value="{e(key)}">{e(value)}</option>' for key, value in data['paradigms'].items())
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    template = (ROOT / 'scripts/leaderboard-page.html').read_text()
    for key, value in {'HEADER': header, 'TABLE': table(data), 'DATA': payload, 'PARADIGMS': options, 'STAGE': render_stage(data)}.items():
        template = template.replace('__' + key + '__', value)
    for asset in ['scripts/leaderboard-stage.css', 'scripts/leaderboard-stage-ui.js', 'scripts/leaderboard-explorer.js']:
        version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:10]
        template = re.sub(re.escape(asset)+r'\?v=[^"\s]+', asset+'?v='+version, template)
    (ROOT / 'leaderboard.html').write_text(template, newline='\n')
    print(f'Built standalone leaderboard: {len(data["models"])} entries; original results preserved.')


if __name__ == '__main__':
    main()
