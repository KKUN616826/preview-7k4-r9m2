#!/usr/bin/env python3
"""Refresh the coming-soon improvement loop (#model-diagnostics) and its head assets in the Home.

The section is placed directly after the diagnosis-card block (build_home_diagnosis.py).
"""
from pathlib import Path
import hashlib
import profile_v5 as pv

# The model's profile after 0-3 rounds of the loop; must match CODES in home-diagnostics.js.
LOOP_CODES = ['ISTJ', 'ESTJ', 'ESTP', 'ENTP']

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- HOME DIAGNOSTICS START -->'
END = '<!-- HOME DIAGNOSTICS END -->'
AFTER = '<!-- HOME_DIAGNOSIS_END -->\n'


def render():
    source = (ROOT / 'scripts/home-diagnostics.html').read_text().strip()
    avatars = ''.join(pv.avatar(code, 'lp-avatar-img', backdrop=True) for code in LOOP_CODES)
    source = source.replace('<!-- LP_AVATARS -->', avatars)
    return START + '\n' + source + '\n' + END


def main():
    section = render()
    for relative in ['index.html']:
        path = ROOT / relative
        # Preserve legacy line endings and every unrelated edit verbatim.
        source = path.read_bytes().decode()
        # The loop continues the diagnosis-card section, so it sits directly after it.
        if START in source:
            start = source.index(START)
            end = source.index(END, start) + len(END)
            source = source[:start].rstrip('\n') + '\n' + source[end:].lstrip('\n')
        assert source.count(AFTER) == 1, relative
        source = source.replace(AFTER, AFTER + section + '\n', 1)
        assets = '<!-- HOME_DIAGNOSTICS_ASSETS_START -->\n'
        for ext in ['css', 'js']:
            version = hashlib.sha256((ROOT / f'scripts/home-diagnostics.{ext}').read_bytes()).hexdigest()[:10]
            url = f'scripts/home-diagnostics.{ext}?v={version}'
            assets += (f'<link rel="stylesheet" href="{url}">\n' if ext == 'css'
                       else f'<script src="{url}" defer></script>\n')
        assets += '<!-- HOME_DIAGNOSTICS_ASSETS_END -->'
        if '<!-- HOME_DIAGNOSTICS_ASSETS_START -->' in source:
            a = source.index('<!-- HOME_DIAGNOSTICS_ASSETS_START -->')
            b = source.index('<!-- HOME_DIAGNOSTICS_ASSETS_END -->', a) + len('<!-- HOME_DIAGNOSTICS_ASSETS_END -->')
            source = source[:a] + assets + source[b:]
        else:
            source = source.replace('</head>', assets + '\n</head>')
        path.write_bytes(source.encode())
    print('Updated Home diagnostic preview and head assets.')


if __name__ == '__main__':
    main()
