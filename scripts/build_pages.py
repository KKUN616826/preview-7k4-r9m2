#!/usr/bin/env python3
"""Build resources.html (Docs) and news.html on the shared design system."""
import json
from html import escape
from pathlib import Path

from site_shell import apply_shell, REPO

ROOT = Path(__file__).resolve().parents[1]
SUITE_KEY = {'mind': 'mind', 'act': 'act', 'mind2act': 'm2a'}
FOCUS = {
    'mind': 'Memory, goal selection and task-level planning.',
    'act': 'Timely, precise and stable physical execution.',
    'mind2act': 'Reasoning and execution coordinated through feedback.',
}


def e(value):
    return escape(str(value), quote=True)


def document(title, description, body, current, css):
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><meta name="description" content="{e(description)}">'
            f'<link rel="icon" href="media/images/mind2act-favicon-v2.png"><link rel="stylesheet" href="{css}?v=ds-20261104">'
            f'</head>\n<body>\n<main id="main">\n{body}\n</main>\n</body></html>\n')
    return apply_shell(page, current=current, prefix='')


def docs():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    total = sum(len(s['cases']) for s in suites)
    rows = ''.join(
        f'<tr><td><span class="badge" data-suite="{SUITE_KEY[s["slug"]]}">{e(s["name"])}</span></td><td>{e(FOCUS[s["slug"]])}</td>'
        f'<td class="num">{len(s["cases"])}</td><td>Easy · Medium · Hard</td></tr>' for s in suites)
    rows += f'<tr class="total"><td>Total</td><td>Three complementary suites</td><td class="num">{total}</td><td>{total * 3} task configurations</td></tr>'
    example = suites[0]['cases'][0]
    body = f'''<section class="page-hero page-hero--plain"><div class="container"><p class="eyebrow">Docs</p><h1>Documentation</h1>
<p class="lead">A guide to the tasks, demonstrations and evaluation material in Mind2Act World.</p></div></section>
<section class="section"><div class="container docs">
<nav class="docs-toc" aria-label="On this page"><p class="eyebrow">On this page</p><a href="#overview">Overview</a><a href="#suites">Task suites</a><a href="#instructions">Instructions and difficulty</a><a href="#evaluation">Evaluation</a><a href="#reference">Reference material</a></nav>
<div class="prose">
<h2 id="overview">Overview</h2>
<p>Robotic manipulation requires more than choosing the right goal or executing an isolated skill. Over a long horizon, a robot must remember task state, act under physical constraints, and use execution feedback to decide what comes next. Final success alone offers limited insight into where this process breaks down.</p>
<p>Mind2Act World is a simulation benchmark for studying task reasoning, physical execution, and their coordination. Shared observation and action interfaces, explicit timing conditions, and disclosure of execution assistance support comparisons across VLA and world-action policies, coding agents, and hybrid systems.</p>
<figure class="docs-figure"><a href="media/overview/mind2act-overview-v3.pdf" target="_blank" rel="noopener"><picture><source srcset="media/images/mind2act-overview-v3.webp" type="image/webp"><img src="media/images/mind2act-overview-v3.png" width="2600" height="2113" loading="lazy" alt="Mind2Act World overview: the Mind, Act and Mind2Act suites, task highlights, open-source ecosystem and leaderboard."></picture></a>
<figcaption>Overview figure from the original task design; its task counts predate the current {total}-task catalogue. Open the PDF for full resolution.</figcaption></figure>
<h2 id="suites">Task suites</h2>
<p>The benchmark comprises {total} tasks in three suites. Each task has Easy, Medium and Hard configurations that vary memory load, planning dependencies, precision requirements and timing pressure.</p>
<div class="table-wrap"><table class="data-table"><thead><tr><th>Suite</th><th>Focus</th><th class="num">Tasks</th><th>Levels</th></tr></thead><tbody>{rows}</tbody></table></div>
<p><a class="btn btn-secondary" href="benchmark.html">Browse the {total} tasks →</a></p>
<h2 id="instructions">Instructions and difficulty</h2>
<ol class="steps"><li>Open a task from the <a href="benchmark.html">catalogue</a>.</li><li>Switch between Easy, Medium and Hard to see the matching demonstration video.</li><li>Read the instruction panel next to the video for the exact task operation and what is evaluated.</li></ol>
<p><a class="btn btn-secondary" href="tasks/{e(example["id"])}.html">Open an example task →</a></p>
<h2 id="evaluation">Evaluation</h2>
<p>Every run reports a <strong>Score</strong> (0–100, combining task success with stage progress) and a <strong>Success</strong> rate (%). The <a href="protocol.html">evaluation protocol</a> defines both, lists the tasks the current results cover, and explains how to submit a model.</p>
<p class="btn-row"><a class="btn btn-secondary" href="protocol.html">Read the protocol →</a><a class="btn btn-secondary" href="leaderboard.html">View the leaderboard →</a></p>
<h2 id="reference">Reference material</h2>
<ul class="ref-list">
<li><a href="{REPO}" target="_blank" rel="noopener"><span class="icon-disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></svg></span><span><b>Source repository</b><small>Website, task assets and build scripts on GitHub</small></span></a></li>
<li><a href="data/benchmark-navigation.json"><span class="icon-disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 4H7a3 3 0 0 0-3 3v2a2 2 0 0 1-2 2 2 2 0 0 1 2 2v2a3 3 0 0 0 3 3h1M16 4h1a3 3 0 0 1 3 3v2a2 2 0 0 0 2 2 2 2 0 0 0-2 2v2a3 3 0 0 1-3 3h-1"/></svg></span><span><b>Task metadata</b><small>Suites, task titles and summaries as JSON</small></span></a></li>
<li><a href="media/overview/mind2act-overview-v3.pdf" target="_blank" rel="noopener"><span class="icon-disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/></svg></span><span><b>Benchmark overview</b><small>One-page summary figure, PDF</small></span></a></li>
</ul>
</div></div></section>'''
    (ROOT / 'resources.html').write_text(document('Docs · Mind2Act World', 'Documentation for Mind2Act World: task suites, demonstrations, evaluation and reference material.', body, 'docs', 'scripts/pages-ds.css'), newline='\n')


def news():
    items = sorted(json.loads((ROOT / 'data/news.json').read_text()), key=lambda n: n['date'], reverse=True)
    rows = ''.join(
        f'<li><time class="meta-line" datetime="{e(n["date"])}">{e(n["date"])}</time><span class="badge badge--plain">{e(n["type"])}</span><p>{n["html"]}</p></li>'
        for n in items)
    body = ('<section class="page-hero page-hero--plain"><div class="container"><p class="eyebrow">News</p><h1>News</h1>'
            '<p class="lead">Releases, new tasks and leaderboard updates.</p></div></section>'
            f'<section class="section"><div class="container"><div class="card"><ol class="news-page">{rows}</ol></div></div></section>')
    (ROOT / 'news.html').write_text(document('News · Mind2Act World', 'Mind2Act World releases, new tasks and leaderboard updates.', body, '', 'scripts/pages-ds.css'), newline='\n')


def main():
    docs()
    news()
    print('Built Docs and News pages.')


if __name__ == '__main__':
    main()
