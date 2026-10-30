"""Render the homepage task explorer from the benchmark's shared task catalog."""
import html
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

EXPLORER_COPY = {
    'mind': {'description': 'Memory and operation selection', 'coverage': 'Memory retention · Rule inference · Spatial and sequence tracking'},
    'act': {'description': 'Precision, timing and stability', 'coverage': 'Contact precision · Action timing · Motion stability'},
    'mind2act': {'description': 'Decision-execution coordination', 'coverage': 'Multi-stage goals · Dynamic conditions · Feedback'}
}

def render():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    for suite in suites:
        suite['explorer'] = EXPLORER_COPY[suite['slug']]
    total = sum(len(s['cases']) for s in suites)
    rows, links = [], []
    for i, suite in enumerate(suites):
        slug, name = suite['slug'], suite['name']
        selected = slug == 'mind2act'
        rows.append(f'''<div class="cm-suite cm-{slug}">
<button type="button" class="cm-suite-choice" data-suite="{slug}" aria-pressed="{str(selected).lower()}" aria-expanded="{str(selected).lower()}" aria-controls="cm-coverage-{slug}"><span class="cm-suite-heading"><strong>{name}</strong><small>{len(suite['cases'])}</small></span><span class="cm-suite-goal">{html.escape(suite['explorer']['description'])}</span></button>
<div class="cm-detail" id="cm-coverage-{slug}"{'' if selected else ' hidden'}><a class="cm-detail-link" href="benchmark/{slug}.html" aria-label="View {name} tasks">View tasks ↗</a></div></div>''')
        for j, task in enumerate(suite['cases']):
            links.append(f'<a href="tasks/{task["id"]}.html">{task["id"]} · {html.escape(task["title"])}</a>')
    cards = []
    for suite in suites:
        for task in suite['cases']:
            cards.append(f'<button type="button" class="cm-orbit-card cm-{suite["slug"]}" data-task="{task["id"]}" data-parent="{suite["slug"]}" aria-pressed="false" aria-label="{html.escape(task["id"]+": "+task["title"])}"><img src="{task["row_cover"]}" alt="" loading="lazy" draggable="false"><span class="cm-node-id">{task["id"]}</span></button>')
    payload = json.dumps(suites,ensure_ascii=False).replace('<','\\u003c')
    markup = '''<section id="capability-explorer" class="academic-section capability-map" aria-labelledby="cm-heading">
<link rel="stylesheet" href="scripts/capability-map.css">
<div class="cm-layout"><div class="cm-copy"><div class="cm-overview"><h2 id="cm-heading"><span>__TASK_COUNT__</span><span class="cm-sr-only"> tasks</span></h2><p>Tasks across reasoning, execution,<br>and coordination.</p><div class="cm-metrics"><div><strong>3</strong><span>Evaluation suites</span></div><div><strong>3</strong><span>Difficulty levels</span><small>Easy / Medium / Hard</small></div></div><div class="cm-composition" aria-hidden="true">'''+''.join(f'<span class="cm-{suite["slug"]}">'+ '<i></i>'*len(suite['cases'])+'</span>' for suite in suites)+'''</div><p class="cm-composition-caption">10 tasks in each suite</p></div><div class="cm-choices" role="group" aria-label="Evaluation suites">'''+''.join(rows)+'''</div></div>
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

    markup = markup.replace('__TASK_COUNT__', str(total))
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
