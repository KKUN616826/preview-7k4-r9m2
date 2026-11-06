#!/usr/bin/env python3
"""Refresh the diagnostic teaser and its head assets in the maintained Home."""
from pathlib import Path
from math import sqrt
import hashlib

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- HOME DIAGNOSTICS START -->'
END = '<!-- HOME DIAGNOSTICS END -->'


def framework():
    pixels = []
    for row, y in enumerate(range(-65, 66, 7)):
        limit = sqrt(max(0, 67 ** 2 - y ** 2))
        for col, x in enumerate(range(-65, 66, 7)):
            if abs(x) > limit or (row * 7 + col * 3) % 23 == 0:
                continue
            size = 2.4 + .9 * (1 - abs(x) / 70)
            opacity = .4 + .6 * (1 - abs(x) / 95)
            pixels.append(f'<rect x="{91+x:.1f}" y="{146+y:.1f}" width="{size:.1f}" height="{size:.1f}" opacity="{opacity:.2f}" style="--scatter-x:{x*.45:.1f}px;--scatter-y:{y*.45:.1f}px"/>')
    return '''<svg viewBox="0 0 600 310" role="img" aria-label="Model to evaluation, evidence tracing, diagnosis and profile">
  <g class="md-model-unit">
    <g class="md-model-pixels">''' + ''.join(pixels) + '''</g>
    <text class="md-model-label" x="91" y="244">MODEL</text>
    <text class="md-small-label md-example-label" x="91" y="264">Example model</text>
  </g>
  <g class="md-links" aria-hidden="true">
    <path class="md-input-path" pathLength="1" d="M158 124 C210 124 207 97 263 97"/>
    <path class="md-input-path md-input-blue" pathLength="1" d="M158 171 C210 171 207 154 263 154"/>
    <circle class="md-tracer" r="3.4" fill="#b4d4ba" style="offset-path:path('M158 124 C210 124 207 97 263 97')"/>
    <circle class="md-tracer" r="3.4" fill="#a5c4d8" style="offset-path:path('M158 171 C210 171 207 154 263 154')"/>
  </g>
  <g class="md-harness-unit">
    <g class="md-ring-spin" aria-hidden="true">
      <path class="md-ring" d="M282 92 A98 98 0 1 1 282 204"/>
      <path class="md-ring-inner md-arc-evaluate" pathLength="1" d="M326 79 A81 81 0 0 1 441 125"/>
      <path class="md-ring-inner md-arc-diagnose" pathLength="1" d="M441 178 A81 81 0 0 1 353 230"/>
      <path class="md-ring-inner md-ring-blue md-arc-trace" pathLength="1" d="M334 224 A81 81 0 0 1 303 200"/>
    </g>
    <g class="md-gate md-gate-evaluate" aria-hidden="true"><rect x="267" y="92" width="3" height="3"/><rect x="272" y="92" width="3" height="3"/><rect x="267" y="97" width="3" height="3"/><rect x="272" y="97" width="3" height="3"/></g>
    <g class="md-gate md-gate-trace"><rect x="267" y="149" width="3" height="3"/><rect x="272" y="149" width="3" height="3"/><rect x="267" y="154" width="3" height="3"/><rect x="272" y="154" width="3" height="3"/></g>
    <g class="md-gate md-gate-diagnose"><rect x="289" y="211" width="3" height="3"/><rect x="294" y="211" width="3" height="3"/><rect x="289" y="216" width="3" height="3"/><rect x="294" y="216" width="3" height="3"/></g>
    <path class="md-output-path md-flow" aria-hidden="true" d="M463 138 H600"/>
    <path class="md-output-path md-output-blue md-flow" aria-hidden="true" d="M463 151 H600"/>
    <path class="md-output-path md-output-gold md-flow" aria-hidden="true" d="M463 164 H600"/>
  <text class="md-main-label" x="365" y="142"><tspan x="365">Mind2Act</tspan><tspan x="365" dy="29">Harness</tspan></text>
  <g class="md-phase md-phase-1"><text class="md-stage-label" x="280" y="277">Evaluate</text><circle cx="280" cy="294" r="3" fill="#b4d4ba"/></g>
  <g class="md-phase md-phase-2"><text class="md-stage-label" x="365" y="277">Trace</text><circle cx="365" cy="294" r="3" fill="#b4d4ba"/></g>
  <g class="md-phase md-phase-3"><text class="md-stage-label" x="450" y="277">Diagnose</text><circle cx="450" cy="294" r="3" fill="#b4d4ba"/></g>
  <path d="M285 294 H360 M370 294 H445" fill="none" stroke="#e7ede7" stroke-opacity=".5" stroke-width=".7"/>
  </g>
</svg>'''


def render():
    source = (ROOT / 'scripts/home-diagnostics.html').read_text().strip()
    # A denser edge becomes a sparse cloud below the card. Fixed geometry keeps
    # the dissolve stable during the readable final hold and without JavaScript.
    particles = []
    for row in range(7):
        for col in range(42):
            seed = (col * 37 + row * 53 + col * row * 7) % 101
            if seed > 92 - row * 9:
                continue
            x = col * 100 / 41 + (seed % 5 - 2) * .3
            y = row * 8 + seed % 6
            size = 2 + seed % 4
            opacity = max(.15, .9 - row * .09 - (seed % 4) * .06)
            particles.append(f'<i style="--x:{x:.2f}%;--y:{y}px;--s:{size}px;--alpha:{opacity:.2f};--dx:{seed%13-6}px;--lift:{4+seed%9}px"></i>')
    particles = ''.join(particles)
    source = source.replace('__FRAMEWORK__', framework()).replace('__PARTICLES__', particles)
    for ext in ['css', 'js']:
        version = hashlib.sha256((ROOT / f'scripts/home-diagnostics.{ext}').read_bytes()).hexdigest()[:10]
        source = source.replace(f'home-diagnostics.{ext}?v=1', f'home-diagnostics.{ext}?v={version}')
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
