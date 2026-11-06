"""Render data-backed homepage statistics; update only their homepage locations."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    models = json.loads((ROOT / 'data/leaderboard-results.json').read_text())['models']
    task_count = sum(len(suite['cases']) for suite in suites)
    reported = sum(any(isinstance(result.get('score'), (int, float))
                       for result in model['results'].values()) for model in models)
    metrics = [
        (task_count, 'Tasks', 'layout-grid'),
        (task_count * 3, 'Task configurations', 'chart-bar'),
        (len(suites), 'Capability suites', 'stack'),
        (reported, 'Models evaluated', 'robot'),
    ]
    cards = ''.join(
        f'<div class="home-stat"><img class="home-stat-icon" src="media/icons/benchmark-stats/{icon}.svg" width="24" height="24" alt="">'
        f'<dt>{label}</dt><dd class="home-stat-value">{value}</dd>'
        '</div>' for value, label, icon in metrics)
    version = hashlib.sha256((ROOT / 'scripts/home-stats.css').read_bytes()).hexdigest()[:10]
    return ('<!-- HOME_STATS_START -->\n'
            f'<link rel="stylesheet" href="scripts/home-stats.css?v={version}">\n'
            f'<section id="benchmark-at-a-glance" class="home-stats" aria-label="Benchmark at a glance"><dl>{cards}</dl></section>\n'
            '<!-- HOME_STATS_END -->')


def update(source):
    # Remove the former three-card summary, not the separate suite explanations.
    source = re.sub(r'<section class="version-status benchmark-facts"[^>]*>.*?</section>', '', source, flags=re.S)
    source = re.sub(r'\s*<!-- HOME_STATS_START -->.*?<!-- HOME_STATS_END -->', '', source, flags=re.S)
    source, count = re.subn(r'(<figure class="intro-film">.*?</figure><script[^>]*intro-film\.js[^>]*></script>)',
                            lambda match: match[1] + '\n\n' + render(), source, count=1, flags=re.S)
    assert count == 1, 'Expected exactly one promotional video'
    return source


if __name__ == '__main__':
    page = ROOT / 'index.html'
    page.write_bytes(update(page.read_bytes().decode()).encode())
    print('Updated four homepage statistics beneath the promotional video.')
