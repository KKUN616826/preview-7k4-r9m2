"""Render the homepage task explorer from the benchmark's shared task catalog."""
import html
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

EXPLORER_COPY = {
    'mind': {'title': 'Remember and decide.', 'description': 'Retain task information and choose the right operation when it is needed.', 'steps': [['Observe', 'Gather information'], ['Remember', 'Retain what matters'], ['Choose', 'Select the next step']], 'example': 'E'},
    'act': {'title': 'Execute with precision.', 'description': 'Respond to changing conditions with timely, precise, and stable physical actions.', 'steps': [['Detect', 'Read the situation'], ['Respond', 'Time the action'], ['Execute', 'Control the motion']], 'example': 'FR1'},
    'mind2act': {'title': 'Reason, act, and adapt.', 'description': 'Coordinate decisions and physical actions, using execution feedback to guide what happens next.', 'steps': [['Plan', 'Choose an operation'], ['Execute', 'Carry out the action'], ['Observe', 'Check the outcome'], ['Update', 'Decide what is next']], 'example': 'CP04'}
}

def render():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    for suite in suites:
        suite['explorer'] = EXPLORER_COPY[suite['slug']]
    total = sum(len(s['cases']) for s in suites)
    rows, links = [], []
    for i, suite in enumerate(suites):
        slug, name = suite['slug'], suite['name']
        rows.append(f'<button type="button" class="cm-suite-choice cm-{slug}" data-suite="{slug}" aria-pressed="{str(slug == "mind2act").lower()}"><span>{name}</span></button>')
        for j, task in enumerate(suite['cases']):
            links.append(f'<a href="tasks/{task["id"]}.html">{task["id"]} · {html.escape(task["title"])}</a>')
    cards = []
    for suite in suites:
        for task in suite['cases']:
            cards.append(f'<button type="button" class="cm-orbit-card cm-{suite["slug"]}" data-task="{task["id"]}" data-parent="{suite["slug"]}" aria-pressed="false" aria-label="{html.escape(task["id"]+": "+task["title"])}"><img src="{task["row_cover"]}" alt="" loading="lazy" draggable="false"><span class="cm-node-id">{task["id"]}</span></button>')
    default = suites[2]
    content = default['explorer']
    example = next(t for t in default['cases'] if t['id'] == content['example'])
    steps = ''.join(f'<li><strong>{html.escape(title)}</strong><span>{html.escape(note)}</span></li>' for title, note in content['steps'])
    payload = json.dumps(suites,ensure_ascii=False).replace('<','\\u003c')
    markup = '''<section id="capability-explorer" class="academic-section capability-map" aria-labelledby="cm-heading">
<link rel="stylesheet" href="scripts/capability-map.css">
<div class="cm-header"><h2 id="cm-heading">Explore the benchmark</h2><p>Explore how robots remember, act, and use feedback to complete a task.</p></div>
<div class="cm-layout"><div class="cm-copy"><p class="cm-stats">__TASK_COUNT__ tasks <span aria-hidden="true">·</span> 3 suites <span aria-hidden="true">·</span> Easy / Medium / Hard</p>
<div class="cm-choices" role="group" aria-label="Evaluation suites">'''+''.join(rows)+'''</div>
<div class="cm-detail cm-mind2act" aria-live="polite" aria-atomic="true"><p class="cm-detail-label">Mind2Act · 10 tasks</p><h3 class="cm-detail-title">__SUITE_TITLE__</h3><p class="cm-detail-copy">__SUITE_DESCRIPTION__</p>
<ol class="cm-process" aria-label="Task process">__STEPS__</ol>
<div class="cm-example"><p class="cm-example-label">IN PRACTICE</p><a class="cm-example-open" href="tasks/__EXAMPLE_ID__.html"><img class="cm-example-image" src="__EXAMPLE_IMAGE__" alt="" loading="lazy"><span class="cm-example-content"><strong class="cm-example-title">__EXAMPLE_TITLE__</strong><span class="cm-example-summary">__EXAMPLE_SUMMARY__</span><span class="cm-example-action">Preview on moon <span aria-hidden="true">↗</span></span></span></a></div>
<a class="cm-detail-link" href="benchmark/mind2act.html">Browse all 10 Mind2Act tasks ↗</a></div>

</div><div class="cm-visual"><div class="cm-orbit" tabindex="0" role="group" aria-label="Three-dimensional task sphere. Drag to rotate or select a task.">
<canvas class="cm-particles" aria-hidden="true"></canvas><div class="cm-moon-fallback" aria-hidden="true"></div>
<div class="cm-orbit-cards">'''+''.join(cards)+'''</div></div>
<svg class="cm-connector" aria-hidden="true" hidden><path></path><circle r="4"></circle></svg>
<div class="cm-task-preview" aria-labelledby="cm-preview-title" hidden><button type="button" class="cm-preview-close" aria-label="Close task preview">×</button><img class="cm-preview-image" alt=""><div class="cm-preview-caption"><p class="cm-preview-meta"></p><h3 id="cm-preview-title"></h3><p class="cm-preview-summary"></p><a class="cm-preview-link" href="benchmark.html">View task ↗</a></div></div>
<div class="cm-map-footer"><div><button type="button" class="cm-motion" aria-pressed="false">Play motion</button><button type="button" class="cm-reset">Reset view</button></div></div></div></div>
<details class="cm-text-index"><summary>Browse tasks as a list</summary><p class="cm-credit">Moon imagery: <a href="https://svs.gsfc.nasa.gov/4720">NASA’s Scientific Visualization Studio</a>. Task regions are a conceptual map.</p><nav aria-label="All benchmark tasks">'''+''.join(links)+'''</nav></details>
<script type="application/json" id="cm-data">'''+payload+'''</script><script src="scripts/capability-map.js" defer></script></section>'''

    replacements = {'__TASK_COUNT__': str(total), '__SUITE_TITLE__': content['title'], '__SUITE_DESCRIPTION__': content['description'], '__STEPS__': steps, '__EXAMPLE_ID__': example['id'], '__EXAMPLE_IMAGE__': example['row_cover'], '__EXAMPLE_TITLE__': html.escape(example['id']+' · '+example['title']), '__EXAMPLE_SUMMARY__': html.escape(example['summary'])}
    for key, value in replacements.items():
        markup = markup.replace(key, value)
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
