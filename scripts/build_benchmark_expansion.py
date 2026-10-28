#!/usr/bin/env python3
"""Build the supplied expansion briefs and synchronize the shared task catalog."""
import json
import re
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEVELS=('easy','medium','hard')
def load():return json.loads((ROOT/'data/benchmark-expansion.json').read_text())['cases']
def task_content(case):
    cid=case['id'];levels=case['media'];initial=next(l for l in LEVELS if l in levels)
    title=escape(case['title']);brief=escape(case['instruction']);tags=''.join(f'<span>{escape(t)}</span>' for t in case['focus'])
    out=[f'<div class="breadcrumb"><a href="index.html">All tasks</a> / {cid}</div><div class="task-head"><h1>{title}</h1><p>{escape(case["summary"])}</p><p class="task-original-title" lang="zh-CN">{escape(case["title_zh"])}</p></div>',
         f'<div class="demo-toolbar"><nav class="difficulty" aria-label="Difficulty" data-default="{initial}">']
    for level in LEVELS:
        pending='' if level in levels else '<small class="difficulty-status">Pending</small>'
        out.append(f'<a href="#{level}" data-level="{level}" aria-current="{str(level==initial).lower()}">{level.title()}{pending}</a>')
    out.append('</nav></div>')
    for level in LEVELS:
        hidden='' if level==initial else ' hidden'
        out.append(f'<section class="demo-panel" data-panel="{level}" aria-label="{level.title()} demonstration"{hidden}><div class="demo-layout"><div>')
        if level in levels:
            view='Multi-view' if 'triview' in levels[level].lower() else 'Head-view'
            out.append(f'<figure class="expansion-demo"><div class="video-shell"><video controls playsinline preload="none" poster="../media/benchmark-expansion/{cid}/{level}.jpg" aria-label="{cid} {level.title()} demonstration"><source src="../media/task-demos/{cid}/{level}.mp4" type="video/mp4"></video></div><figcaption>{level.title()} · {view} demonstration</figcaption></figure>')
        else:
            available=' · '.join(l.title() for l in LEVELS if l in levels)
            out.append(f'<div class="demo-pending" role="status"><h2>{level.title()} demonstration pending</h2><p>A video for this level has not been supplied yet.</p><p>Available demonstrations: {available}.</p><a href="#{initial}">Watch {initial.title()} instead →</a></div>')
        out.append(f'</div><aside class="brief"><div class="instruction"><h2>Instruction</h2><p>{brief}</p></div><section class="dimensions"><h2>Task focus</h2><div class="dimension-list">{tags}</div></section></aside></div></section>')
    out.append('<nav class="task-footer" aria-label="Adjacent tasks"></nav><script src="../scripts/task-difficulty.js" defer></script>')
    return ''.join(out)
def main():
    cases=load();suites=json.loads((ROOT/'data/benchmark-navigation.json').read_text())
    for case in cases:
        first=next(l for l in LEVELS if l in case['media'])
        for level in case['media']:
            assert (ROOT/f'media/task-demos/{case["id"]}/{level}.mp4').is_file()
        existing=next((c for s in suites for c in s['cases'] if c['id']==case['id']),None)
        item={k:case[k] for k in ['id','title','summary','nav_title']}
        item.update(title_zh=case['title_zh'],cover=f'media/benchmark-covers/{case["id"]}.jpg',row_cover=f'media/benchmark-covers/{case["id"]}.jpg',initial_level=first,available_levels=[l for l in LEVELS if l in case['media']],expansion=True)
        if existing is not None:existing.update(item)
        else:next(s for s in suites if s['slug']==case['suite'])['cases'].append(item)
        (ROOT/f'scripts/benchmark/{case["id"]}.html').write_text(task_content(case))
    ids=[c['id'] for s in suites for c in s['cases']];assert len(ids)==len(set(ids))
    (ROOT/'data/benchmark-navigation.json').write_text(json.dumps(suites,ensure_ascii=False,indent=2)+'\n')
    print(f'Prepared {len(cases)} new task briefs; catalog now contains {len(ids)} tasks.')
if __name__=='__main__':main()
