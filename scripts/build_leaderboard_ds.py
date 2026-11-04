"""Render leaderboard.html and protocol.html on the shared design system.

Data: data/leaderboard-results.json (validated by build_leaderboard.load).
Models without any reported score are listed as "in evaluation", not as rows.
"""
import json
from html import escape
from pathlib import Path

from site_shell import apply_shell, REPO

ROOT = Path(__file__).resolve().parents[1]
SUITE = {'mind': 'mind', 'act': 'act', 'coupling': 'm2a'}
ISSUE = REPO + '/issues/new?title=Leaderboard%20submission%3A%20'


def e(value):
    return escape(str(value), quote=True)


def has_scores(model):
    return any(r.get('score') is not None for r in model['results'].values())


def mean_score(model, views):
    values = [model['results'][v['key']]['score'] for v in views]
    return None if any(v is None for v in values) else sum(values) / len(values)


def logo(model):
    if model.get('icon'):
        return f'<span class="model-logo"><img src="{e(model["icon"])}" alt="" width="14" height="14"></span>'
    initials = ''.join(w[0] for w in model['name'].replace('-', ' ').split()[:2]).upper()
    return f'<span class="model-logo"><b>{e(initials)}</b></span>'


def mosaic(ids):
    return '<div class="page-hero-mosaic" aria-hidden="true">' + ''.join(
        f'<img src="media/thumbs/{i}.webp" alt="" width="640" height="480">' for i in ids) + '</div>'


def matrix(data, models):
    views = data['views']
    best = {v['key']: max(m['results'][v['key']]['score'] or 0 for m in models) for v in views}
    best_mean = max((mean_score(m, views) or 0) for m in models)
    head = ''.join(f'<th class="num" scope="col" data-suite="{SUITE[v["key"]]}"><button type="button" data-sort="{v["key"]}"><span class="dot"></span>{e(v["label"])}</button></th>' for v in views)
    rows = []
    for m in sorted(models, key=lambda m: -(mean_score(m, views) or 0)):
        cells = []
        for v in views:
            r = m['results'][v['key']]
            score, success = r.get('score'), r.get('success')
            if score is None:
                cells.append(f'<td data-v="-1"><span class="cell cell--empty">—</span></td>')
                continue
            top = (' is-best' if score == best[v['key']] else '') + (' is-dark' if score >= 45 else '')
            tip = f'Score {score:.2f} · Success {success:.1f}%' if success is not None else f'Score {score:.2f}'
            cells.append(f'<td data-v="{score}"><span class="cell{top}" data-suite="{SUITE[v["key"]]}" style="--v:{score:.2f}" title="{e(tip)}">{score:.1f}</span></td>')
        mean = mean_score(m, views)
        mean_cell = f'<span class="cell cell--mean{" is-best" if mean == best_mean else ""}">{mean:.1f}</span>' if mean is not None else '<span class="cell cell--empty">—</span>'
        rows.append(
            f'<tr data-type="{e(m["paradigm"])}"><th scope="row"><span class="mx-model">{logo(m)}{e(m["name"])}</span></th>'
            f'<td><span class="badge badge--plain">{e(data["paradigms"][m["paradigm"]])}</span></td>'
            + ''.join(cells) + f'<td data-v="{mean if mean is not None else -1}">{mean_cell}</td></tr>'
        )
    return (
        '<div class="table-wrap"><table class="data-table matrix" id="matrix"><caption class="sr-only">Score by model and suite</caption>'
        f'<thead><tr><th scope="col">Model</th><th scope="col">Type</th>{head}'
        '<th class="num" scope="col"><button type="button" data-sort="mean">Mean</button></th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def ranking(data, models):
    views = data['views']
    tabs = ''.join(
        f'<button type="button" role="tab" data-view="{v["key"]}" data-suite="{SUITE[v["key"]]}" aria-selected="{"true" if i == 0 else "false"}">{e(v["label"])}</button>'
        for i, v in enumerate(views))
    types = sorted({m['paradigm'] for m in models})
    type_chips = '<button type="button" class="chip" data-type="all" aria-pressed="true">All</button>' + ''.join(
        f'<button type="button" class="chip" data-type="{e(t)}" aria-pressed="false">{e(data["paradigms"][t])}</button>' for t in types)
    rows = []
    for m in models:
        attrs = ' '.join(
            f'data-{v["key"]}-score="{m["results"][v["key"]]["score"] if m["results"][v["key"]]["score"] is not None else -1}" '
            f'data-{v["key"]}-success="{m["results"][v["key"]]["success"] if m["results"][v["key"]]["success"] is not None else -1}"'
            for v in views)
        demo = f'<a class="icon-btn" href="{e(m["cases"])}" aria-label="{e(m["name"])} model-family demos"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></a>' if m.get('cases') else ''
        rows.append(
            f'<tr data-type="{e(m["paradigm"])}" {attrs}><td class="rk"><span class="rank"></span></td>'
            f'<th scope="row"><span class="mx-model">{logo(m)}{e(m["name"])}</span></th>'
            f'<td><span class="badge badge--plain">{e(data["paradigms"][m["paradigm"]])}</span></td>'
            '<td class="score-cell"><div class="score-wrap"><span class="bar"><i></i></span><span class="num score"></span></div></td>'
            '<td class="num success"></td>'
            f'<td class="demo">{demo}</td></tr>'
        )
    return (
        '<div class="lb-toolbar">'
        f'<div class="tabs" role="tablist" aria-label="Suite">{tabs}</div>'
        f'<div class="lb-filters"><div class="chip-row" role="group" aria-label="Model type">{type_chips}</div>'
        '<div class="tabs tabs--sm" role="group" aria-label="Rank by"><button type="button" data-rank="score" aria-selected="true">Score</button><button type="button" data-rank="success" aria-selected="false">Success</button></div></div></div>'
        '<p class="lb-view-desc" id="lb-view-desc"></p>'
        '<div class="table-wrap"><table class="data-table ranking" id="ranking"><caption class="sr-only">Ranking for the selected suite</caption>'
        '<thead><tr><th scope="col">Rank</th><th scope="col">Model</th><th scope="col">Type</th>'
        '<th scope="col" class="num">Score <abbr title="Task performance including stage progress, 0–100">ⓘ</abbr></th>'
        '<th scope="col" class="num">Success <abbr title="Final task success rate, %">ⓘ</abbr></th><th scope="col"><span class="sr-only">Demos</span></th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


SUBMIT = f'''<section class="section section--tint" id="submit" aria-labelledby="submit-title"><div class="container">
<header class="section-head"><p class="eyebrow">Submit</p><h2 id="submit-title">Evaluate your model</h2><p class="lead">Submissions are evaluated on the same task configurations as the models above.</p></header>
<div class="submit-grid">
<div class="card card-body submit-card"><span class="icon-disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="7" width="14" height="12" rx="3"/><path d="M12 3v4M9 12h.01M15 12h.01M9 16h6"/></svg></span><h3>Submit a policy</h3><p>VLA or world-action models with a checkpoint we can run in simulation.</p><a class="btn btn-primary btn-sm" href="{ISSUE}policy" target="_blank" rel="noopener">Open a submission →</a></div>
<div class="card card-body submit-card"><span class="icon-disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></svg></span><h3>Submit an agent</h3><p>Coding agents or harnesses that write and run robot programs.</p><a class="btn btn-primary btn-sm" href="{ISSUE}agent" target="_blank" rel="noopener">Open a submission →</a></div>
<div class="card card-body submit-card"><span class="icon-disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><path d="M17.5 14v7M14 17.5h7"/></svg></span><h3>Contribute a task</h3><p>New Mind, Act or Mind2Act tasks with a scripted success check.</p><a class="btn btn-primary btn-sm" href="{ISSUE}task" target="_blank" rel="noopener">Propose a task →</a></div>
</div>
<p class="submit-note">Read the <a href="protocol.html">evaluation protocol</a> before submitting.</p>
</div></section>'''


def page(title, description, body, current, extra_head=''):
    return apply_shell(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{e(title)}</title><meta name="description" content="{e(description)}">'
        '<link rel="icon" href="media/images/mind2act-favicon-v2.png">'
        f'{extra_head}</head>\n<body>\n<main id="main">\n{body}\n</main>\n</body></html>\n',
        current=current, prefix='')


def build(data):
    views = data['views']
    models = [m for m in data['models'] if has_scores(m)]
    pending = [m['name'] for m in data['models'] if not has_scores(m) and not m['name'].lower().startswith('to be')]
    evaluated_tasks = sum(len(v['tasks']) for v in views)
    catalog = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    total_tasks = sum(len(s['cases']) for s in catalog)
    view_text = {v['key']: v['description'] for v in views}
    hero = (
        '<section class="page-hero"><div class="container"><p class="eyebrow">Leaderboard</p><h1>Leaderboard</h1>'
        f'<p class="lead">Mind, Act and Mind2Act scores for {len(models)} models across coding agents and VLA policies.</p>'
        f'<p class="meta-line">{evaluated_tasks} of {total_tasks} tasks evaluated · <a href="protocol.html">Protocol →</a> · <a href="#submit">Submit a model →</a></p></div>'
        + mosaic(['CP05', 'FR1', 'P', 'CP03', 'PR2', 'S', 'CP04', 'DR7']) + '</section>'
    )
    overview = (
        '<section class="section" id="overview" aria-labelledby="overview-title"><div class="container">'
        '<header class="section-head"><p class="eyebrow">Overview</p><h2 id="overview-title">Score by suite</h2>'
        '<p class="lead">Each cell is a model’s Score (0–100) on one suite; darker means higher. Hover for Success. Click a column to sort.</p></header>'
        + matrix(data, models) + '</div></section>'
    )
    rank = (
        '<section class="section" id="results" aria-labelledby="results-title"><div class="container">'
        '<header class="section-head"><p class="eyebrow">Ranking</p><h2 id="results-title">Ranking by suite</h2></header>'
        + ranking(data, models)
        + (f'<p class="lb-pending">In evaluation: {e(", ".join(pending))}.</p>' if pending else '')
        + '</div></section>'
    )
    payload = json.dumps(view_text).replace('<', '\\u003c')
    body = hero + overview + rank + SUBMIT + f'<script type="application/json" id="lb-views">{payload}</script><script src="scripts/leaderboard-ds.js?v=ds-20261104" defer></script>'
    head = '<link rel="stylesheet" href="scripts/leaderboard-ds.css?v=ds-20261104">'
    (ROOT / 'leaderboard.html').write_text(page('Leaderboard · Mind2Act World', 'Mind2Act World leaderboard: Mind, Act and Mind2Act scores for coding agents and VLA policies.', body, 'leaderboard', head), newline='\n')

    suite_rows = ''.join(
        f'<tr><td><span class="badge" data-suite="{SUITE[v["key"]]}">{e(v["label"])}</span></td><td>{e(v["description"])}</td>'
        f'<td class="mono">{e(" · ".join(v["tasks"]))}</td></tr>' for v in views)
    protocol = f'''<section class="page-hero page-hero--plain"><div class="container"><p class="eyebrow">Protocol</p><h1>Evaluation protocol</h1>
<p class="lead">How Mind2Act World measures a model, what the current results cover, and how to submit.</p></div></section>
<section class="section"><div class="container protocol">
<nav class="protocol-toc" aria-label="On this page"><p class="eyebrow">On this page</p><a href="#metrics">Metrics</a><a href="#coverage">Coverage</a><a href="#comparing">Comparing models</a><a href="#submitting">Submitting</a></nav>
<div class="prose">
<h2 id="metrics">Metrics</h2>
<p>Every run reports two separate measurements. They are not interchangeable.</p>
<dl class="metric-list">
<div><dt>Score <span class="badge badge--plain">0–100</span></dt><dd>Task performance on a 0–100 scale, combining task success with stage progress.</dd></div>
<div><dt>Success <span class="badge badge--plain">%</span></dt><dd>The final task success rate: successful trials divided by total trials.</dd></div>
<div><dt>Zero and unreported <span class="badge badge--plain">0 vs —</span></dt><dd>A measured zero is a result. A dash means no result has been published yet; models without results are listed as “in evaluation”.</dd></div>
</dl>
<h2 id="coverage">Coverage</h2>
<p>The catalogue has {total_tasks} tasks. Current results cover {evaluated_tasks} of them, five per suite, at all difficulty levels combined. Results for the remaining tasks will be added as they are evaluated.</p>
<div class="table-wrap"><table class="data-table"><thead><tr><th>Suite</th><th>What it measures</th><th>Evaluated tasks</th></tr></thead><tbody>{suite_rows}</tbody></table></div>
<h2 id="comparing">Comparing models</h2>
<p>Coding agents, VLA policies and world-action models differ in how they are trained and how they act. Read any comparison alongside these conditions:</p>
<ul class="factor-list"><li>Training conditions</li><li>Exact checkpoint</li><li>Observation permissions</li><li>Action interface</li><li>Execution assistance</li><li>Evaluation budget</li></ul>
<h2 id="submitting">Submitting</h2>
<p>Open a submission on GitHub with your model, its checkpoint or harness, and the conditions above. Once it has been evaluated on the same task configurations, it is added to the <a href="leaderboard.html">leaderboard</a>.</p>
<p><a class="btn btn-primary" href="leaderboard.html#submit">Submit a model →</a></p>
</div></div></section>'''
    (ROOT / 'protocol.html').write_text(page('Evaluation protocol · Mind2Act World', 'How Mind2Act World measures Score and Success, what the results cover, and how to submit a model.', protocol, '', '<link rel="stylesheet" href="scripts/leaderboard-ds.css?v=ds-20261104">'), newline='\n')
