"""Render the homepage task explorer from the benchmark's shared task catalog."""
import html
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def render():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    total = sum(len(s['cases']) for s in suites)
    rows, links = [], []
    for i, suite in enumerate(suites):
        slug, name = suite['slug'], suite['name']
        rows.append(f'<button type="button" class="cm-suite-choice cm-{slug}" data-suite="{slug}" aria-pressed="false"><span><strong>{name}</strong><small>{html.escape(suite["description"])}</small></span><span class="cm-count">{len(suite["cases"])} <span class="cm-sr">tasks</span>↗</span></button>')
        for j, task in enumerate(suite['cases']):
            links.append(f'<a href="tasks/{task["id"]}.html">{task["id"]} · {html.escape(task["title"])}</a>')
    cards = []
    for suite in suites:
        for task in suite['cases']:
            cards.append(f'<button type="button" class="cm-orbit-card cm-{suite["slug"]}" data-task="{task["id"]}" data-parent="{suite["slug"]}" aria-pressed="false" aria-label="{html.escape(task["id"]+": "+task["title"])}"><img src="{task["row_cover"]}" alt="" loading="lazy" draggable="false"><span>{task["id"]}</span><span class="cm-card-tooltip">{html.escape(task["title"])}</span></button>')
    payload = json.dumps(suites,ensure_ascii=False).replace('<','\\u003c')
    markup = '''<section id="capability-explorer" class="academic-section capability-map" aria-labelledby="cm-heading">
<link rel="stylesheet" href="scripts/capability-map.css">
<div class="cm-header"><h2 id="cm-heading">Explore the benchmark</h2><p>Memory, physical execution, and the feedback connecting them.</p></div>
<div class="cm-layout"><div class="cm-copy"><dl class="cm-stats"><div><dt>Tasks</dt><dd>__TASK_COUNT__</dd></div><div><dt>Evaluation suites</dt><dd>3</dd></div><div><dt>Difficulty levels</dt><dd>3</dd></div></dl>
<div class="cm-detail" aria-live="polite" aria-atomic="true"><p class="cm-detail-label">THE FULL BENCHMARK</p><h3 class="cm-detail-title">Three views of robotic manipulation</h3><p class="cm-detail-copy">Explore tasks across three suites, with Easy, Medium, and Hard configurations.</p><a class="cm-detail-link" href="benchmark.html">Explore all __TASK_COUNT__ tasks <span aria-hidden="true">↗</span></a></div>
<div class="cm-choices" aria-label="Evaluation suites">'''+''.join(rows)+'''</div>
</div><div class="cm-visual"><div class="cm-orbit" aria-label="Three-dimensional task sphere. Drag to rotate or select a task.">
<canvas class="cm-particles" aria-hidden="true"></canvas><div class="cm-orbit-core" aria-hidden="true"><img src="media/images/moon-clean-v53.png" alt=""><span>Mind2Act</span></div>
<div class="cm-orbit-cards">'''+''.join(cards)+'''</div></div>
<div class="cm-task-preview" aria-labelledby="cm-preview-title" hidden><button type="button" class="cm-preview-close" aria-label="Close task preview">×</button><img class="cm-preview-image" alt=""><div class="cm-preview-caption"><p class="cm-preview-meta"></p><h3 id="cm-preview-title"></h3><a class="cm-preview-link" href="benchmark.html">View task ↗</a></div></div>
<div class="cm-map-footer"><span>Drag to rotate · Select a task</span><div><button type="button" class="cm-motion" aria-pressed="false">Pause rotation</button><button type="button" class="cm-reset">Show all</button></div></div></div></div>
<details class="cm-text-index"><summary>Browse tasks as a list</summary><nav aria-label="All benchmark tasks">'''+''.join(links)+'''</nav></details>
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
