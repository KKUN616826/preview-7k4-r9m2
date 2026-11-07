#!/usr/bin/env python3
"""Replace the 90 benchmark demonstrations with the head-camera package (Mind2Act_训练数据主视角视频.zip).

The package holds one 640x480 head-camera episode per task and tier, <task>_<tier>.mp4, with no
burned-in labels, and an index.csv (task, tier, episode, frames, seconds, bytes, instruction).
Video bytes are copied without re-encoding. Posters, covers, task instructions and captions are
regenerated from the package; the previous videos stay in git history.

    python3 scripts/sync_head_camera_package.py <extracted package directory> [<zip>]
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Package task id -> site task id, checked against the site instructions (84 of 90 identical; the
# PR1 and PR2 episodes differ only in their target value).
ALIASES = {'E1': 'E', 'F1': 'F', 'M1': 'M', 'P1': 'P', 'S1': 'S',
           'DR1': 'FR1', 'DR2': 'FR2', 'DR3': 'DR3', 'DR4': 'DR7'}
LEVELS = ['easy', 'medium', 'hard']
CAPTION = 'Head-camera demonstration'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def probe(path):
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'quiet', '-show_format', '-show_streams', '-of', 'json', str(path)]))
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    return float(info['format']['duration']), v['width'], v['height'], v['codec_name']


def still(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '1', '-i', str(src),
                    '-frames:v', '1', '-q:v', '2', str(dst)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('package', type=Path)
    parser.add_argument('zip', type=Path, nargs='?')
    args = parser.parse_args()

    index = list(csv.DictReader((args.package / 'index.csv').open(encoding='utf-8-sig')))
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    site_ids = {c['id'] for s in suites for c in s['cases']}
    previous = {(r['task'], r['level']): r for r in json.loads((ROOT / 'data/benchmark-video-imports.json').read_text())}
    rows = []
    for e in index:
        task, level = ALIASES.get(e['task'], e['task']), e['tier']
        assert task in site_ids and level in LEVELS, (e['task'], level)
        src = args.package / f'{e["task"]}_{level}.mp4'
        assert src.is_file() and src.stat().st_size == int(e['bytes']), src
        duration, width, height, codec = probe(src)
        assert (width, height, codec) == (640, 480, 'h264'), (src, width, height, codec)
        dst = ROOT / f'media/task-demos/{task}/{level}.mp4'
        old = previous.get((task, level), {})
        before = sha(dst) if dst.exists() else None
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        digest = sha(dst)
        assert digest == sha(src)
        rows.append(dict(task=task, source_task=e['task'], level=level, source_filename=src.name,
                         instruction=e['instruction'], episode_id=e['episode'], parameter_values='',
                         previous_sha256=before, source_sha256=digest,
                         audit_status='missing' if before is None else 'same' if before == digest else 'different recording/version',
                         previous_presentation=old.get('presentation'),
                         path=dst.relative_to(ROOT).as_posix(), sha256=digest, bytes=dst.stat().st_size,
                         duration=duration, width=width, height=height, codec=codec,
                         presentation='head-camera', processing='exact source copy; no re-encoding'))
        still(dst, ROOT / f'media/benchmark-expansion/{task}/{level}.jpg')
        if level == 'easy':
            still(dst, ROOT / f'media/benchmark-covers/{task}.jpg')
        print(f'{len(rows)}/90 {e["task"]} -> {task} / {level}', flush=True)
    assert len(rows) == 90 and {(r['task'], r['level']) for r in rows} == {(t, l) for t in site_ids for l in LEVELS}
    order = [c['id'] for s in suites for c in s['cases']]
    rows.sort(key=lambda r: (order.index(r['task']), LEVELS.index(r['level'])))

    expansion = json.loads((ROOT / 'data/benchmark-expansion.json').read_text())
    for case in expansion['cases']:
        mine = [r for r in rows if r['task'] == case['id']]
        case['media'] = {r['level']: r['source_filename'] for r in mine}
        case['instructions'] = {r['level']: r['instruction'] for r in mine}
    (ROOT / 'data/benchmark-expansion.json').write_text(json.dumps(expansion, ensure_ascii=False, indent=2) + '\n')

    for cid in order:
        p = ROOT / f'scripts/benchmark/{cid}.html'
        content = p.read_text()
        for r in (r for r in rows if r['task'] == cid):
            pattern = (r'(<section class="demo-panel"[^>]*data-panel="' + r['level'] +
                       r'".*?)(?=<section class="demo-panel"|<nav class="task-footer")')

            def update(m, r=r):
                panel = re.sub(r'(<div class="instruction"><h2>Instruction</h2><p>).*?(</p>)',
                               lambda x: x[1] + escape(r['instruction']) + x[2], m[0], count=1, flags=re.S)
                panel = re.sub(r'poster="[^"]+"', f'poster="../media/benchmark-expansion/{cid}/{r["level"]}.jpg"', panel)
                return re.sub(r'<figcaption>.*?</figcaption>', f'<figcaption>{r["level"].title()} · {CAPTION}</figcaption>', panel, flags=re.S)
            content, n = re.subn(pattern, update, content, count=1, flags=re.S)
            assert n == 1, (cid, r['level'])
        p.write_text(content)

    (ROOT / 'data/benchmark-video-imports.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    report = {'package': args.zip.name if args.zip else args.package.name,
              'package_sha256': sha(args.zip) if args.zip else None,
              'index_sha256': sha(args.package / 'index.csv'),
              'aliases': ALIASES,
              'presentation': 'head camera only, 640x480, no burned-in labels',
              'counts': {k: sum(r['audit_status'] == k for r in rows) for k in ['missing', 'same', 'different recording/version']},
              'instruction_matching': 'Instructions come from the package index; 84 of 90 equal the previous site text, '
                                      'PR1 and PR2 differ in their episode-specific target values.'}
    (ROOT / 'data/bench30-sync-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Synced 90 videos; rebuild with scripts/build_benchmark.py')


if __name__ == '__main__':
    main()
