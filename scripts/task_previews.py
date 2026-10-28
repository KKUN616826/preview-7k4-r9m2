"""Bind homepage previews without changing detail-page media or hero assets."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def apply_previews(page):
    manifest = json.loads((ROOT / 'data/task-previews.json').read_text())
    previews = {entry['source']: entry for entry in manifest['previews']}
    seen = set()
    def replace(match):
        source = match['source']
        entry = previews.get(source)
        if entry is None:
            # Expansion recordings already carry their own poster and keep native media.
            return match.group(0)
        for field in ('preview', 'poster'):
            assert (ROOT / entry[field]).is_file(), entry[field]
        seen.add(source)
        return (match['video'] + f' poster="{entry["poster"]}"' + match['middle'] +
                entry['preview'] + match['end'])
    page = re.sub(r'(?P<video><video\b[^>]*)(?P<middle>><source data-src=")'
                  r'(?P<source>media/task-demos/[^\"]+)(?P<end>"[^>]*></video>)', replace, page)
    assert seen, "No homepage task previews were bound"
    return page
