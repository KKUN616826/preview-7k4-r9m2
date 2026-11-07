#!/usr/bin/env python3
"""Refresh the diagnostic teaser and its head assets in the maintained Home."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- HOME DIAGNOSTICS START -->'
END = '<!-- HOME DIAGNOSTICS END -->'


def render():
    source = (ROOT / 'scripts/home-diagnostics.html').read_text().strip()
    return START + '\n' + source + '\n' + END


def main():
    section = render()
    for relative in ['index.html']:
        path = ROOT / relative
        # Preserve legacy line endings and every unrelated edit verbatim.
        source = path.read_bytes().decode()
        if START in source:
            start = source.index(START)
            end = source.index(END, start) + len(END)
            source = source[:start] + section + source[end:]
        else:
            assert source.count('</main>') == 1, relative
            source = source.replace('</main>', section + '\n</main>')
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
