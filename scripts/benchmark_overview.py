"""Benchmark landing page only; task content stays in scripts/benchmark/*.html."""
import json
import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ('easy', 'medium', 'hard')

# Concise catalog copy, based on the existing task goals. Full instructions stay in the player/detail.
CATALOG_GOALS = {
    'E': 'Find repeated items across successive batches.',
    'F': 'Infer button controls from feedback and guide the slider to its target.',
    'P': 'Remember meal orders and deliver the requested ingredients.',
    'S': 'Restore a remembered layout after the tray rotates.',
    'M': 'Track a hidden workpiece and reproduce its station route.',
    'E2': 'Recall object–digit pairs and enter the matching code.',
    'F2': 'Use trial feedback to infer the required color-block order.',
    'P2': 'Remember a steamer stack and reconstruct its layer order.',
    'S2': 'Remember hidden restricted cells and guide the marker to the goal.',
    'M2': 'Recall card identities and locations to find matching pairs.',
    'FR1': 'Pick moving packages from the conveyor into the collection tray.',
    'FR2': 'Respond to light cues with the correct button presses.',
    'PR1': 'Adjust the linear resistor to the target setting.',
    'PR2': 'Rotate the voltage regulator to the requested setting.',
    'PR3': 'Trace the marked line with the pen.',
    'PR4': 'Align the cloth edge and place it in the target area.',
    'PR5': 'Orient the stamp and press it at the target.',
    'PR6': 'Arrange dominoes to trigger a chain and ring the bell.',
    'DR3': 'Time the approach and withdrawal to cross a periodic gate.',
    'DR7': 'Balance the ball on a tray while transporting it to the target.',
    'CP01': 'Remember orders and assemble meals from a moving food supply.',
    'CP02': 'Remember a decoration layout and recreate it on a rotating cake.',
    'CP03': 'Place upright plates into moving empty rack slots.',
    'CP04': 'Remember the recipe and coordinate cooking, temperature control, and cleanup.',
    'CP05': 'Remember the key sequence and reproduce it with the mallets.',
    'CP06': 'Use scale feedback to balance produce with counterweights.',
    'CP07': 'Build a bridge across the gap using the available pieces.',
    'CP08': 'Remember a reference structure and recreate it with blocks.',
    'CP09': 'Reproduce a reference drawing on the whiteboard using markers.',
    'CP10': 'Return target balls and avoid red balls by predicting their motion.',
}


def plain(value):
    return unescape(re.sub(r'<[^>]*>', '', value)).strip()


def e(value):
    return escape(str(value), quote=True)


def task_data(case):
    """Use the same media and instructions as the existing task detail page."""
    source = (ROOT / f'scripts/benchmark/{case["id"]}.html').read_text()
    levels = {}
    for panel in re.split(r'<section\b[^>]*\bclass="demo-panel"', source)[1:]:
        level = re.search(r'data-panel="([^"]+)"', panel)[1]
        video = re.search(r'<source\s+src="([^"]+)"', panel)
        if level not in LEVELS or not video:
            continue
        path = video[1].removeprefix('../')
        if not (ROOT / path).is_file():
            raise FileNotFoundError(f'{case["id"]} {level}: {path}')
        instruction = re.search(r'<div class="instruction">.*?<p>(.*?)</p>', panel, re.S)
        text = plain(instruction[1]) if instruction else case['summary']
        if len(text.split()) < 3:
            text = case['summary']
        # Prefer the dedicated action stills. Fall back to existing task posters.
        poster = f'media/benchmark-overview/{case["id"]}-{level}.jpg'
        if not (ROOT / poster).is_file():
            match = re.search(r'poster="([^"]+)"', panel)
            poster = match[1].removeprefix('../') if match else case['cover']
        levels[level] = {'video': path, 'poster': poster, 'instruction': text}
    if not levels:
        raise ValueError(f'No available demonstration for {case["id"]}')
    return {**case, 'levels': levels}


def chapter(case, index, total):
    levels = case['levels']
    initial = case.get('initial_level', 'easy')
    if initial not in levels:
        initial = next(iter(levels))
    current = levels[initial]
    choices = ''.join(
        f'<option value="{level}"{" selected" if level == initial else ""}'
        f'{" disabled" if level not in levels else ""}>{level.title()}'
        f'{" (not available)" if level not in levels else ""}</option>'
        for level in LEVELS)
    return f'''<article class="bo-chapter" id="task-{case['id']}" data-task="{case['id']}" aria-labelledby="title-{case['id']}">
      <div class="bo-chapter-layout">
        <div class="bo-media">
          <video class="bo-task-video" id="video-{case['id']}" playsinline preload="none"
            poster="{e(current['poster'])}" data-src="{e(current['video'])}" aria-label="{e(case['title'])}: {initial.title()} demonstration"></video>
          <button type="button" class="bo-play" data-play aria-label="Play {e(case['title'])}"><span aria-hidden="true">▶</span></button>
          <button type="button" class="bo-expand" data-expand aria-label="Expand {e(case['title'])}">Expand <span aria-hidden="true">↗</span></button>
        </div>
        <div class="bo-task-copy">
          <p class="bo-task-id">{case['id']}</p>
          <h3 id="title-{case['id']}" title="{e(case['title'])}">{e(case.get('nav_title', case['title']))}</h3>
          <p class="bo-task-goal" title="{e(case['summary'])}">{e(CATALOG_GOALS.get(case['id'], case['summary']))}</p>
          <div class="bo-task-actions"><select class="bo-level-select" aria-label="Demonstration difficulty for {e(case['title'])}" aria-controls="video-{case['id']}">{choices}</select>
          <a class="bo-task-detail" href="tasks/{case['id']}.html#{initial}">View task <span aria-hidden="true">↗</span></a></div>
        </div>
      </div>
      <p class="bo-media-error" hidden>Unable to load this demonstration. <button type="button" data-retry>Try again</button> or <a href="tasks/{case['id']}.html#{initial}">open the task page</a>.</p>
    </article>'''


def quick_index(suites):
    groups = []
    for suite in suites:
        links = ''.join(f'<li><a href="#task-{c["id"]}" data-index-task="{c["id"]}"><span>{c["id"]}</span>{e(c.get("nav_title", c["title"]))}</a></li>' for c in suite['cases'])
        groups.append(f'<details data-index-group="{suite["slug"]}"{" open" if suite["slug"] == "mind2act" else ""}><summary><a href="#{suite["slug"]}" data-index-suite="{suite["slug"]}">{suite["name"]}<span>{len(suite["cases"])}</span></a></summary><ul>{links}</ul></details>')
    return '<nav aria-label="Task quick index">' + ''.join(groups) + '</nav>'


def render(suites):
    records = {c['id']: task_data(c) for s in suites for c in s['cases']}
    default = 'mind2act'
    # A representative task from each suite. Only the front frame plays.
    featured = [('mind', 'E2'), ('act', 'PR3'), ('mind2act', 'CP05')]
    frames = []
    for slug, task_id in featured:
        c = records[task_id]
        asset = c['levels']['easy']
        preview = f'media/benchmark-overview/hero-{task_id}.mp4'
        frames.append(f'''<figure class="bo-hero-frame" data-hero-frame="{slug}" data-position="{'front' if slug == default else 'left' if slug == 'mind' else 'right'}">
          <video muted playsinline loop preload="none" poster="{e(asset['poster'])}" data-preview="{preview}" aria-hidden="true" tabindex="-1"></video>
          <figcaption>{task_id} <span>{e(c.get('nav_title', c['title']))}</span></figcaption>
        </figure>''')
    hero_buttons = ''.join(f'<button type="button" data-hero-select="{s["slug"]}" aria-pressed="{str(s["slug"] == default).lower()}"><span aria-hidden="true"></span>{s["name"]}</button>' for s in suites)
    tabs = ''.join(f'<a role="tab" id="tab-{s["slug"]}" href="#{s["slug"]}" data-suite="{s["slug"]}" aria-controls="suite-{s["slug"]}" aria-selected="{str(s["slug"] == default).lower()}" tabindex="{0 if s["slug"] == default else -1}">{s["name"]}<span>{len(s["cases"])}</span></a>' for s in suites)
    panels = []
    for s in suites:
        hidden = ' hidden' if s['slug'] != default else ''
        chapters = ''.join(chapter(records[c['id']], i + 1, len(s['cases'])) for i, c in enumerate(s['cases']))
        panels.append(f'''<section class="bo-suite" id="suite-{s['slug']}" role="tabpanel" aria-labelledby="tab-{s['slug']}"{hidden}>
          <div class="bo-suite-intro"><h2>{s['name']}</h2><p>{e(s['description'])}</p></div><div class="bo-task-grid">{chapters}</div>
        </section>''')
    payload = {k: v['levels'] for k, v in records.items()}
    return f'''<section class="bo-hero" aria-labelledby="benchmark-title">
      <div class="bo-hero-copy"><p class="bo-eyebrow">Mind2Act World / Task explorer</p><h1 id="benchmark-title">Benchmark</h1>
        <p class="bo-hero-tagline">Reason. Execute.<br><strong>Coordinate.</strong></p>
        <dl class="bo-hero-meta"><div><dt>Tasks</dt><dd>{len(records)}</dd></div><div><dt>Capability suites</dt><dd>{len(suites)}</dd></div></dl></div>
      <div class="bo-hero-visual"><div class="bo-hero-stage">{''.join(frames)}</div>
        <div class="bo-hero-controls"><div class="bo-hero-selector" role="group" aria-label="Featured capability">{hero_buttons}</div>
        <button type="button" class="bo-motion-toggle" aria-pressed="false">Pause preview</button></div>
      </div>
    </section>
    <section class="bo-explorer" id="explore" aria-labelledby="explorer-title">
      <div class="bo-explorer-layout"><aside class="bo-index"><p class="bo-index-title">Quick index</p>{quick_index(suites)}</aside><div class="bo-explorer-body">
      <div class="bo-explorer-heading"><h2 id="explorer-title">Explore the benchmark</h2><nav class="bo-suite-tabs" role="tablist" aria-label="Capability suite">{tabs}</nav></div>
      <details class="bo-mobile-index"><summary>Browse tasks</summary>{quick_index(suites)}</details>
      {''.join(panels)}
      </div></div>
    </section>
    <dialog class="bo-video-dialog" aria-labelledby="expanded-title"><div class="bo-dialog-heading"><div><p class="bo-task-id" id="expanded-meta"></p><h2 id="expanded-title"></h2></div><button type="button" class="bo-dialog-close" aria-label="Close expanded video">Close ×</button></div><video class="bo-expanded-video" controls playsinline preload="none"></video><p id="expanded-instruction"></p><a class="bo-expanded-detail">View full task ↗</a></dialog>
    <script type="application/json" id="benchmark-overview-data">{json.dumps(payload, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>'''


def document(content):
    header = (ROOT / 'scripts/benchmark/header.html').read_text()
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Benchmark · Mind2Act World</title>
<meta name="description" content="Explore 30 robotic manipulation tasks across Mind, Act, and Mind2Act. Watch demonstrations and compare available difficulty levels.">
<link rel="icon" href="media/images/mind2act-favicon-v2.png">
<link rel="preload" href="media/fonts/Sora-variable.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="tasks/task-pages.css"><link rel="stylesheet" href="media/site-shell.css?v=white-canvas-1">
<link rel="stylesheet" href="scripts/benchmark-overview.css?v=2">
</head><body class="benchmark-overview"><a class="bo-skip" href="#explore">Skip to tasks</a>{header}
<main class="bo-main" id="benchmark-content">{content}</main>
<script src="scripts/benchmark-overview.js?v=2" defer></script><script src="scripts/site-shell.js?v=unified-1" defer></script>
</body></html>\n'''
