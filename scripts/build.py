#!/usr/bin/env python3
"""Build the static site and task documents from public, versioned content."""
import json
import re
from pathlib import Path
from render_cases import card, case_md, cover, e
from leaderboard import render as render_leaderboard
from build_home_leaderboard_entry import main as build_home_leaderboard_entry
from build_rollouts import build_rollouts
from hero_demo import render as render_hero
from task_previews import apply_previews
from build_benchmark import main as build_benchmark
from build_leaderboard import main as build_leaderboard
from build_capability_map import render as render_capability_map
from build_intro_story import render as render_intro_story
from build_benchmark_expansion import main as prepare_expansion
from sync_benchmark_expansion import apply_homepage

ROOT = Path(__file__).resolve().parents[1]

ENGLISH_TITLES = {
    'E': 'Duplicate Item Identification',
    'P': 'Order-Based Meal Assembly',
    'S': 'Rotating Tray Layout Reconstruction',
    'F': 'Unknown Button Mapping and Slider Navigation',
    'M': 'Workpiece Tracking and Route Reproduction',
    'FR1': 'Continuous Conveyor Picking',
    'FR2': 'Light-Guided Button Response',
    'PR1': 'Linear Resistor Adjustment',
    'PR2': 'Rotary Voltage Regulator Setting',
    'PR3': 'Marker Line Tracing',
    'CP01': 'Conveyor Meal Assembly',
    'CP02': 'Rotating Cake Decoration',
    'CP03': 'Dynamic Rack Loading',
    'CP04': 'Dual-Arm Cooking',
    'CP05': 'Keyboard Sequence Reproduction',
}

def task_wall(records):
    tiles = []
    for case in records:
        asset = next((item for item in case['media'] if item['kind'] == 'video'), None)
        if not asset:
            continue
        tiles.append(
            '<a class="task-tile" href="docs/cases/{id}.md"><video muted loop playsinline preload="metadata" poster="{poster}" '
            'aria-label="{title}"><source src="{path}" type="video/mp4"></video>'
            '<span><b>{id}</b>{title}</span></a>'.format(
                id=e(case['id']), title=e(ENGLISH_TITLES[case['id']]),
                poster=e(asset.get('poster', cover(case))), path=e(asset['path'])
            )
        )
    return ''.join(tiles)

def main():
    prepare_expansion()
    build_rollouts(ENGLISH_TITLES)
    records = json.loads((ROOT / 'data/showcase-cases.json').read_text())
    assert len(records) == len({c['id'] for c in records}) == 15
    videos = sum(a['kind'] == 'video' for c in records for a in c['media'])
    images = sum(a['kind'] == 'image' for c in records for a in c['media'])
    for c in records:
        for a in c['media']:
            assert (ROOT / a['path']).is_file(), a['path']
            if a.get('poster'):
                assert (ROOT / a['poster']).is_file(), a['poster']
        (ROOT / 'docs/cases' / (c['id'] + '.md')).write_text(case_md(c, '../../'))
    intro = (ROOT / 'docs/PhysCo_Showcase.md').read_text()
    (ROOT / 'docs/PhysCo_Cases.md').write_text(intro + '\n\n---\n\n' + '\n\n---\n\n'.join(case_md(c, '../') for c in records))
    media = ['# Mind2Act World 演示素材索引', '', f'{videos} 段视频、{images} 张场景图。', '']
    for c in records:
        media += ['## ' + c['id'] + ' · ' + c['title'], '']
        for a in c['media']:
            media.append(f'- [{a["label"]}](../{a["path"]})')
        media += ['']
    (ROOT / 'docs/PhysCo_Media.md').write_text('\n'.join(media))
    payload = json.dumps(records, ensure_ascii=False, separators=(',', ':'))
    for char, escape in [('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026'), ('\u2028', '\\u2028'), ('\u2029', '\\u2029')]:
        payload = payload.replace(char, escape)
    page = (ROOT / 'scripts/showcase.html').read_text()
    page = page.replace('__RESEARCH_INTRO__', (ROOT / 'scripts/research_intro.html').read_text().replace('__INTRO_STORY__', render_intro_story()))
    page = page.replace('__CAPABILITY_MAP__', render_capability_map())
    page = page.replace('__HERO_DEMO__', render_hero())
    page = page.replace('__ACADEMIC_COVER_CSS__', (ROOT / 'scripts/academic-cover.css').read_text())
    page = page.replace('__PROJECT_POLISH_CSS__', (ROOT / 'scripts/project-polish.css').read_text())
    lunar_data = json.loads((ROOT / 'data/lunar-preview.json').read_text())
    for model in lunar_data['models']:
        model['icon_svg'] = (ROOT / ('media/icons/' + model['icon'] + '.svg')).read_text()
    lunar = json.dumps(lunar_data, separators=(',', ':')).replace('<', '\u003c')
    page = page.replace('__LUNAR_DATA__', lunar)
    page = page.replace('__LUNAR_JS__', (ROOT / 'scripts/lunar.js').read_text())
    page = page.replace('__RESEARCH_CSS__', (ROOT / 'scripts/research.css').read_text())
    page = page.replace('__LEADERBOARD__', render_leaderboard(records))
    page = page.replace('__LEADERBOARD_JS__', (ROOT / 'scripts/leaderboard.js').read_text())
    dimensions = json.loads((ROOT / 'data/coupling-dimensions.json').read_text())
    rows = dimensions['rows']
    assert len(rows) == 5 and all(len(row) == len(dimensions['columns']) for row in rows)
    dimension_table = '<div class="table-wrap"><table><caption>协同任务的压力维度 · 原始任务设计标签</caption><thead><tr>' + ''.join('<th scope="col">'+e(h)+'</th>' for h in dimensions['columns']) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in row)+'</tr>' for row in rows) + '</tbody></table></div>'
    page = page.replace('__COUPLING_DIMENSIONS__', dimension_table)
    by_id = {c['id']: c for c in records}
    for cid in ['P', 'PR3', 'CP02']:
        c = by_id[cid]
        a = next(a for a in c['media'] if a['kind'] == 'video' and ('Medium' in a['label'] or cid == 'P'))
        demo = f'<figure class="article-demo"><video controls preload="none" playsinline poster="{e(a["poster"])}" aria-label="观点演示 {cid}"><source src="{e(a["path"])}" type="video/mp4"></video><figcaption><b>{cid} · {e(c["title"])} · {e(a["label"])}</b><span>任务运控演示；不代表模型评测结果。</span><a href="#case-{cid}">任务定义与全部档位 →</a></figcaption></figure>'
        page = page.replace('__POINT_DEMO_' + cid + '__', demo)
    highlights = [('CP01', '历史订单 → 动态取料', '实际入盘才更新剩余需求'), ('CP03', '移动槽口 → 精确装盘', '专家运控演示；非学习策略成绩'), ('CP04', '配方记忆 → 限时温控', 'Easy 预览；其余档位视频待补')]
    previews = {'CP01': 'media/posters/CP01__research_overview.jpg'}
    highlight_cards = []
    for cid, title, note in highlights:
        case = by_id[cid]
        asset = next((item for item in case['media'] if item['kind'] == 'video'), None)
        if asset:
            visual = f'<video autoplay muted loop playsinline preload="metadata" poster="{e(asset.get("poster", cover(case)))}" aria-label="{e(case["title"])}任务演示"><source src="{e(asset["path"])}" type="video/mp4"></video>'
        else:
            visual = f'<img src="{e(previews.get(cid) or cover(case))}" alt="{e(case["title"])}" loading="eager">'
        highlight_cards.append(f'<a href="#case-{cid}"><figure>{visual}<figcaption><b>{cid} · {e(title)}</b><span>{e(note)}</span></figcaption></figure></a>')
    media = ''.join(highlight_cards)
    for key, value in {'INSIGHT_MEDIA': media, 'TASK_WALL': task_wall(records), 'CASES': '\n'.join(card(c) for c in records), 'PUBLIC_DATA': payload, 'VIDEO_COUNT': str(videos), 'IMAGE_COUNT': str(images)}.items():
        page = page.replace('__' + key + '__', value)
    assert not re.search(r'__[A-Z_]+__', page)
    page = apply_previews(page)
    page = apply_homepage(page)
    (ROOT / 'index.html').write_text(page, newline='\n')
    build_home_leaderboard_entry()
    build_benchmark()
    build_leaderboard()
    print(f'Built {len(records)} cases, {videos} videos, {images} images.')

if __name__ == '__main__':
    main()
