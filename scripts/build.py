#!/usr/bin/env python3
"""Build the static site and task documents from public, versioned content."""
import json
import re
from pathlib import Path
from render_cases import card, case_md, cover, e
from build_rollouts import build_rollouts
from build_benchmark import main as build_benchmark
from build_leaderboard import main as build_leaderboard
from build_home import main as build_home
from build_pages import main as build_pages
from build_benchmark_expansion import main as prepare_expansion

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
    # 2026-11 redesign: the homepage is built from scripts/home.html (see build_home.py).
    # The previous scripts/showcase.html template is kept for reference but no longer built.
    build_home()
    build_benchmark()
    build_leaderboard()
    build_pages()
    print(f'Built {len(records)} cases, {videos} videos, {images} images.')

if __name__ == '__main__':
    main()
