"""Extract Benchmark-only action stills and small, silent hero loops from existing videos.

Source videos and assets used by other pages are never overwritten.
"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from benchmark_overview import ROOT, task_data

OUT = ROOT / 'media/benchmark-overview'


def extract(item):
    task, level, asset = item
    source = ROOT / asset['video']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(source)]))
    duration = float(probe['format']['duration'])
    time = round(duration * .35, 3)
    name = f'{task}-{level}.jpg'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(time), '-i', str(source),
                    '-frames:v', '1', '-vf', 'scale=720:-2', '-q:v', '3', '-threads', '1',
                    str(OUT / name)], check=True)
    return {'task': task, 'level': level, 'source': asset['video'],
            'time_seconds': time, 'duration_seconds': duration,
            'poster': f'media/benchmark-overview/{name}'}


def main():
    OUT.mkdir(exist_ok=True)
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    jobs = [(c['id'], level, asset) for s in suites for c in s['cases']
            for level, asset in task_data(c)['levels'].items()]
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(extract, jobs))
    for task in ('E2', 'PR3', 'CP05'):
        record = next(r for r in records if r['task'] == task and r['level'] == 'easy')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(record['time_seconds']),
                        '-i', str(ROOT / record['source']), '-t', '8', '-an',
                        '-vf', 'scale=640:-2,fps=24', '-c:v', 'libx264', '-preset', 'veryfast',
                        '-crf', '26', '-threads', '2', '-movflags', '+faststart',
                        str(OUT / f'hero-{task}.mp4')], check=True)
    (OUT / 'sources.json').write_text(json.dumps(records, indent=2) + '\n')
    print(f'Extracted {len(records)} action stills and 3 silent hero loops for Benchmark only.')


if __name__ == '__main__':
    main()
