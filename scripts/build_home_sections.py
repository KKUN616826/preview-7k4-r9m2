#!/usr/bin/env python3
"""Refresh editable homepage sections while preserving the current hero and shell."""
import re
from pathlib import Path
from build_home_stats import update as update_stats
from build_intro_story import render as render_intro
from build_capability_map import render as render_capabilities
from build_home_leaderboard_entry import main as build_entry

ROOT = Path(__file__).resolve().parents[1]


def replace_once(source, pattern, content):
    source, count = re.subn(pattern + r'\r?', lambda _: content, source, count=1, flags=re.S)
    assert count == 1, f'Expected one homepage section: {pattern}'
    return source


def main():
    page = ROOT / 'index.html'
    source = update_stats(page.read_bytes().decode())
    source = replace_once(source, r'<!-- INTRO_STORY_START -->.*?<!-- INTRO_STORY_END -->', render_intro().rstrip())
    source = replace_once(source, r'<section id="capability-explorer".*?</section>', render_capabilities())
    resources = r'<section class="academic-section compact-resources" id="resources-overview">.*?</section>'
    resource_markup = re.search(resources, (ROOT / 'scripts/research_intro.html').read_text(), flags=re.S)
    assert resource_markup, 'Missing resource section source'
    source = replace_once(source, resources, resource_markup[0])
    page.write_bytes(source.encode())
    build_entry()
    print('Built homepage statistics, introduction, task explorer, leaderboard entry and resources.')


if __name__ == '__main__':
    main()
