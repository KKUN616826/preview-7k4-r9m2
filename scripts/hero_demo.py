"""Render static hero assets and embed the same event data used by the player."""
import html
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render():
    data = json.loads((ROOT / 'data/hero-demo.json').read_text())
    cards = []
    crop_x, _, crop_width, _ = data['keyboard']['snapshotCrop']
    for event in data['events']:
        # Display convention: the 29 white keys span C2–C6; not calibrated audio pitches.
        note = 'CDEFGAB'[event['keyId'] % 7] + str(2 + event['keyId'] // 7)
        label = html.escape(note)
        target_x = 100 * (event['target'][0] - crop_x) / crop_width
        cards.append(
            f'<li class="demo-card" data-step="{event["step"]}" hidden>'
            '<span class="demo-card-image">'
            f'<img src="{html.escape(event["snapshot"], quote=True)}" width="420" height="156" '
            f'alt="{label} illuminated in demonstration step {event["step"]}" decoding="async">'
            f'<span class="demo-card-target" style="left:{target_x:.3f}%" aria-hidden="true"></span></span>'
            f'<span class="demo-card-caption"><span>{label}</span><span class="demo-card-status">{event["step"]:02d}</span></span></li>'
        )
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    for char, escaped in [('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026')]:
        payload = payload.replace(char, escaped)
    template = (ROOT / 'scripts/hero-demo.html').read_text()
    version = hashlib.sha256((ROOT / 'scripts/hero-intro.css').read_bytes()).hexdigest()[:10]
    return template.replace('__HERO_CARDS__', '\n'.join(cards)).replace('__HERO_DATA__', payload).replace('__HERO_VIDEO__', data['presentation']['path']).replace('__HERO_INTRO_VERSION__', version)
