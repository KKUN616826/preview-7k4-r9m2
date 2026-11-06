"""Render data-backed homepage statistics; update only their homepage locations."""
import json
import re
from datetime import date
from pathlib import Path
from build_home_tasks import refresh_stylesheet_versions

ROOT = Path(__file__).resolve().parents[1]


def render():
    suites = json.loads((ROOT / 'data/benchmark-navigation.json').read_text())
    board = json.loads((ROOT / 'data/leaderboard-results.json').read_text())
    models = board['models']
    task_count = sum(len(suite['cases']) for suite in suites)
    reported = sum(1 for model in models if model['results'])
    if reported:
        model_detail = f'{reported} with published results'
    else:
        first = date.fromisoformat(board['first_release'])
        batch = sum(1 for model in models if model.get('release') == board['first_release'])
        model_detail = f'{batch} with results on {first.day} {first.strftime("%b")}'
    metrics = [
        (task_count, 'Tasks', 'Ten per capability suite', 'layout-grid'),
        (task_count * 3, 'Task configurations', 'Easy · Medium · Hard', 'chart-bar'),
        (len(suites), 'Capability suites', 'Mind · Act · Mind2Act', 'stack'),
        (len(models), 'Models on the leaderboard', model_detail, 'robot'),
    ]
    cards = ''.join(
        f'<div class="home-stat"><img class="home-stat-icon" src="media/icons/benchmark-stats/{icon}.svg" width="24" height="24" alt="">'
        f'<dt>{label}</dt><dd class="home-stat-value">{value}</dd>'
        f'<dd class="home-stat-detail">{detail}</dd>'
        + '</div>' for value, label, detail, icon in metrics)
    return ('<!-- HOME_STATS_START -->\n'
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
    page.write_bytes(refresh_stylesheet_versions(update(page.read_bytes().decode())).encode())
    print('Updated four homepage statistics beneath the promotional video.')
