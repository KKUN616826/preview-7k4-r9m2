"""Render the homepage task explorer from the benchmark's shared task catalog."""
import html
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

EXPLORER_COPY = {
    'mind': {
        'headline': 'Choose actions using memory.',
        'description': 'Retain earlier observations to identify targets and select the required operation.',
        'example': 'E',
        'demands': [('Memory', 'Recall items from earlier batches.'), ('Action', 'Select the repeated item.'), ('Goal', 'Place it in the submission tray.')],
    },
    'act': {
        'headline': 'Execute with precision and timing.',
        'description': 'Respond to moving targets and perform stable actions under physical constraints.',
        'example': 'FR1',
        'demands': [('Cue', 'Track the moving packages.'), ('Action', 'Pick and place them into the tray.'), ('Goal', 'Collect every package in the tray.')],
    },
    'mind2act': {
        'headline': 'Connect decisions with physical actions.',
        'description': 'Keep track of the goal as actions change the task.',
        'example': 'CP01',
        'demands': [('Memory', 'Remember each order.'), ('Action', 'Pick food from the moving conveyor.'), ('Goal', 'Complete each meal correctly.')],
    },
}

def render():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    for suite in suites:
        suite['explorer'] = EXPLORER_COPY[suite['slug']]
    total = sum(len(s['cases']) for s in suites)
    tabs, panels, links = [], [], []
    for suite in suites:
        slug, name = suite['slug'], suite['name']
        selected = slug == 'mind2act'
        copy = suite['explorer']
        example = next(task for task in suite['cases'] if task['id'] == copy['example'])
        tabs.append(f'''<button type="button" class="cm-suite-choice cm-{slug}{" is-active" if selected else ""}" data-suite="{slug}" aria-pressed="{str(selected).lower()}" aria-expanded="{str(selected).lower()}" aria-controls="cm-coverage-{slug}"><span>{name}</span><small>{len(suite['cases'])}</small></button>''')
        demands = ''.join(f'<div><dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd></div>' for label, value in copy['demands'])
        panels.append(f'''<div class="cm-detail cm-{slug}" id="cm-coverage-{slug}" role="region" aria-label="{name} tasks"{'' if selected else ' hidden'}>
<p class="cm-suite-label">{name}</p><h3 class="cm-detail-title">{html.escape(copy['headline'])}</h3><p class="cm-suite-goal">{html.escape(copy['description'])}</p>
<div class="cm-example"><p class="cm-example-label">A task in practice</p><div class="cm-example-layout"><a class="cm-example-link" data-example="{example['id']}" href="tasks/{example['id']}.html" aria-label="Preview {html.escape(example['title'])}"><img src="{example['row_cover']}" alt="{html.escape(example['title'])} simulation" loading="lazy" width="160" height="120"></a><div class="cm-example-copy"><h4><a data-example="{example['id']}" href="tasks/{example['id']}.html">{example['id']} · {html.escape(example['title'])}</a></h4><p>{html.escape(example['summary'])}</p></div></div></div>
<dl class="cm-case-demands" aria-label="Example task requirements">{demands}</dl>
<a class="cm-detail-link" href="benchmark/{slug}.html">Explore {len(suite['cases'])} {name} tasks ↗</a></div>''')
        for task in suite['cases']:
            links.append(f'<a href="tasks/{task["id"]}.html">{task["id"]} · {html.escape(task["title"])}</a>')
    cards = []
    for suite in suites:
        for task in suite['cases']:
            cards.append(f'<button type="button" class="cm-orbit-card cm-{suite["slug"]}" data-task="{task["id"]}" data-parent="{suite["slug"]}" aria-pressed="false" aria-label="{html.escape(task["id"]+": "+task["title"])}"><img src="{task["row_cover"]}" alt="" loading="lazy" draggable="false"><span class="cm-node-id">{task["id"]}</span></button>')
    payload = json.dumps(suites,ensure_ascii=False).replace('<','\\u003c')
    markup = '''<section id="capability-explorer" class="academic-section capability-map" aria-labelledby="cm-heading">
<link rel="stylesheet" href="scripts/capability-map.css">
<div class="cm-layout"><div class="cm-copy"><h2 id="cm-heading" class="cm-sr-only">Explore __TASK_COUNT__ tasks</h2><p class="cm-overview-meta">__TASK_COUNT__ tasks · __SUITE_COUNT__ suites · 3 difficulty levels</p><div class="cm-choices" role="group" aria-label="Evaluation suites">'''+''.join(tabs)+'''</div><div class="cm-panels">'''+''.join(panels)+'''</div></div>
<div class="cm-visual"><div class="cm-orbit" tabindex="0" role="group" aria-label="Three-dimensional task sphere. Drag to rotate or select a task.">
<canvas class="cm-particles" aria-hidden="true"></canvas><div class="cm-moon-fallback" aria-hidden="true"></div>
<svg class="cm-regions" aria-hidden="true"><g class="cm-corridor"><path data-band-edge="-0.30"></path><path data-band-edge="0.30"></path></g><g class="cm-region-leaders"><path data-region-line="mind"></path><circle data-region-dot="mind" r="3"></circle><path data-region-line="act"></path><circle data-region-dot="act" r="3"></circle><path data-region-line="mind2act"></path><circle data-region-dot="mind2act" r="3"></circle></g></svg>
<div class="cm-region-labels" role="group" aria-label="Moon task regions"><button type="button" class="cm-region-label cm-mind" data-region-label="mind" aria-pressed="false">Mind</button><button type="button" class="cm-region-label cm-act" data-region-label="act" aria-pressed="false">Act</button><button type="button" class="cm-region-label cm-mind2act" data-region-label="mind2act" aria-pressed="true">Mind2Act</button></div>
<div class="cm-orbit-cards">'''+''.join(cards)+'''</div></div>
<svg class="cm-connector" aria-hidden="true" hidden><path></path><circle r="4"></circle></svg>
<div class="cm-task-preview" aria-labelledby="cm-preview-title" hidden><button type="button" class="cm-preview-close" aria-label="Close task preview">×</button><img class="cm-preview-image" alt=""><div class="cm-preview-caption"><p class="cm-preview-meta"></p><h3 id="cm-preview-title"></h3><p class="cm-preview-summary"></p><a class="cm-preview-link" href="benchmark.html">View task ↗</a></div></div>
<div class="cm-map-footer"><p class="cm-map-hint">Select a task to view its goal.</p><div><button type="button" class="cm-motion" aria-pressed="false">Play motion</button><button type="button" class="cm-reset">Reset view</button></div></div></div></div>
<div class="cm-catalog-footer"><a class="cm-browse-all" href="benchmark.html">Browse all __TASK_COUNT__ tasks ↗</a></div>
<details class="cm-text-index"><summary>Browse tasks as a list</summary><p class="cm-credit">Moon imagery: <a href="https://svs.gsfc.nasa.gov/4720">NASA’s Scientific Visualization Studio</a>. Task regions are a conceptual map.</p><nav aria-label="All benchmark tasks">'''+''.join(links)+'''</nav></details>
<script type="application/json" id="cm-data">'''+payload+'''</script><script src="scripts/capability-map.js" defer></script></section>'''

    markup = markup.replace('__TASK_COUNT__', str(total)).replace('__SUITE_COUNT__', str(len(suites)))
    for asset in ['scripts/capability-map.css', 'scripts/capability-map.js']:
        version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:10]
        markup = markup.replace(asset+'"', asset+'?v='+version+'"')
    return markup

if __name__ == '__main__':
    page = ROOT / 'index.html'
    source = page.read_bytes().decode()
    source, count = re.subn(r'<section id="(?:research-motivation|capability-explorer)".*?</section>',lambda _:render(),source,count=1,flags=re.S)
    assert count == 1
    page.write_bytes(source.encode())
