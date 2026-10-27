#!/usr/bin/env python3
"""Extract native-resolution catalog stills, without upscaling or altering source videos."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = {c['id']: c for c in json.loads((ROOT / 'data/showcase-cases.json').read_text())}
    navigation = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    folder = ROOT / 'media/benchmark-covers'
    folder.mkdir(exist_ok=True)
    sources = []
    for suite in navigation:
        for case in suite['cases']:
            asset = next(a for a in records[case['id']]['media'] if a['kind'] == 'video')
            output = folder / f'{case["id"]}.jpg'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', str(ROOT / asset['path']),
                            '-frames:v', '1', '-q:v', '2', '-threads', '1', str(output)], check=True)
            case['row_cover'] = output.relative_to(ROOT).as_posix()
            sources.append({'task': case['id'], 'source': asset['path'], 'source_label': asset['label'],
                            'time_seconds': 1, 'output': case['row_cover']})
    (ROOT / 'data/benchmark-navigation.json').write_text(json.dumps(navigation, ensure_ascii=False, indent=2) + '\n')
    (folder / 'sources.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n')
    print('Extracted 15 native-resolution covers; source videos unchanged.')


if __name__ == '__main__':
    main()
