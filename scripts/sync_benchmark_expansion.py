#!/usr/bin/env python3
"""Synchronize expansion counts and task entries without rebuilding legacy results."""
import json
import re
from html import escape
from pathlib import Path
from build_benchmark_expansion import load
ROOT=Path(__file__).resolve().parents[1]
def apply_homepage(source):
    cases=load();suites=json.loads((ROOT/'data/benchmark-navigation.json').read_text());total=sum(len(s['cases']) for s in suites)
    imported=sum(len(c['media']) for c in cases)
    source=re.sub(r'<b>\d+</b><span>New videos imported</span>', f'<b>{imported}</b><span>New videos imported</span>', source)
    source=source.replace('The benchmark comprises 15 tasks,','The benchmark comprises '+str(total)+' tasks,')
    source=source.replace('<strong>15</strong><span>Tasks</span><p>Five tasks in each capability suite</p>',f'<strong>{total}</strong><span>Tasks</span><p>Ten tasks in each capability suite</p>')
    source=source.replace('<b>15</b><span>Tasks</span>',f'<b>{total}</b><span>Tasks</span>').replace('<b>45</b><span>Task–Difficulty Configurations</span>',f'<b>{total*3}</b><span>Task–Difficulty Configurations</span>').replace('<b>45</b><span>Demonstrations</span>',f'<b>{imported}</b><span>New videos imported</span>')
    source=source.replace('<figcaption>Overview of Mind2Act World</figcaption>','<figcaption>Original task-set overview · Explore the expanded 30-task catalog below.</figcaption>')
    def update_wall(match):
        section=match.group(0)
        old={}
        for tile in re.findall(r'<a class="task-tile".*?</a>',section):
            cid=re.search(r'href="tasks/([^./]+)\.html',tile)[1];old[cid]=tile
        for case in cases:
            level='medium' if 'medium' in case['media'] else next(l for l in ['easy','hard'] if l in case['media'])
            cid=case['id'];name=escape(case['title'])
            old[cid]=f'<a class="task-tile" href="tasks/{cid}.html#{level}"><video muted loop playsinline preload="none" poster="media/benchmark-expansion/{cid}/{level}.jpg" aria-label="{cid} {level.title()} demonstration"><source data-src="media/task-demos/{cid}/{level}.mp4" type="video/mp4"></video><span><b>{cid}</b>{name}</span></a>'
        tiles=''.join(old[c['id']] for s in suites for c in s['cases'])
        section=re.sub(r'(<div class="marquee-track forward">).*?(</div>)',lambda m:m[1]+tiles+m[2],section,count=1,flags=re.S)
        section=section.replace('15 benchmark tasks',f'{total} benchmark tasks').replace('One representative demonstration per task · Medium configuration','One available demonstration per task · Difficulty shown on each task page').replace('Medium: 15 tasks in Mind, Act, Mind2Act order',f'{total} tasks in Mind, Act, Mind2Act order')
        return section
    source=re.sub(r'<section class="academic-section" id="tasks">.*?</section>',update_wall,source,count=1,flags=re.S)
    source=source.replace('Explore all 15 task descriptions',f'Explore all {total} task descriptions')
    notice='<p class="expansion-result-scope">Results shown here preserve the original 15-task snapshot. Results for the added tasks have not been reported.</p>'
    if 'expansion-result-scope' not in source:
        source=re.sub(r'(<section[^>]+id="top-ten"[^>]*>.*?</h2>)',lambda m:m[1]+notice,source,count=1,flags=re.S)
    return source

def main():
    for relative in ['index.html','scripts/research_intro.html']:
        p=ROOT/relative;p.write_bytes(apply_homepage(p.read_bytes().decode()).encode())
    p=ROOT/'resources.html';s=p.read_text()
    s=s.replace('comprises 15 tasks','comprises 30 tasks').replace('<td>5</td>','<td>10</td>').replace('<td>15</td>','<td>30</td>').replace('45 task–level configurations','90 task–level configurations').replace('Browse the 15 tasks','Browse the 30 tasks')
    note='Only the E2 Hard demonstration is pending; all other added task levels have videos available.'
    s=s.replace('Some new difficulty-level videos are pending; task pages identify the recordings currently available.', note)
    if note not in s:s=s.replace('The instruction panel describes the operation required at that level.','The instruction panel describes the task operation. '+note)
    s=s.replace('Use the leaderboard to inspect policy, category, and per-task views; unreported results are marked with a dash.','The leaderboard preserves the original 15-task result snapshot; results for the added tasks are not yet reported. Unreported results are marked with a dash.')
    p.write_text(s)
    p=ROOT/'scripts/leaderboard-page.html';s=p.read_text().replace('15 tasks. Three suites.','30 tasks. Three suites.').replace('Five tasks per suite, each with Easy, Medium, and Hard configurations.','Ten tasks per suite. The results below retain the original 15-task snapshot.').replace('The benchmark defines 15 tasks across three suites and three difficulty levels.','The expanded catalog defines 30 tasks across three suites and three difficulty levels. The added tasks are not included in this result snapshot.')
    p.write_text(s)
    print('Synchronized homepage, documentation and leaderboard scope; result values unchanged.')
if __name__=='__main__':main()
