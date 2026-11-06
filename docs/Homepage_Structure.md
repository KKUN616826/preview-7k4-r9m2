# Homepage structure

The homepage follows the pattern used by RoboDojo, Embodied First Exam and X2Real: each section has one job, and details live on the dedicated pages.

| Order | Section | Job | Source |
|---|---|---|---|
| 1 | `#overview` | Title, tagline, calls to action, interactive demo, paper information, film, key numbers | hand-maintained in `index.html`; numbers from `build_home_stats.py` |
| 2 | `#introduction` | Motivation and the three suites (Mind, Act, Mind2Act) | `scripts/intro-story.html` via `build_intro_story.py` |
| 3 | `#top-ten` | Leaderboard preview: every model with reported scores, ranked by the selected suite | `build_home_leaderboard_entry.py` from `data/leaderboard-results.json` |
| 4 | `#tasks` | All 30 tasks, one row per suite, each linking to its task page | `build_home_tasks.py` from `data/benchmark-navigation.json` |
| 5 | `#news`, `#resources-overview`, `#contributors` | Updates, documents and people | hand-maintained in `index.html` |

The evaluation scope notes and the overview figure moved off the homepage; the introduction links to `protocol.html` and to `media/overview/mind2act-overview-v36.pdf`. The lunar capability map is no longer on the homepage; `build_capability_map.py` skips `index.html` when the section is absent, and its assets remain for reuse.

## Leaderboard preview

- Shows only models with all three suite scores; the row count and "N of M listed models" come from the data file.
- Default ranking is Mind, matching `leaderboard.html`. The Mind / Act / Mind2Act buttons re-rank in place (`scripts/home-structure.js`); ties share a rank.
- The note "from the original 15-task snapshot" is computed from the task lists in `views`, so it updates if the scored set grows. `sync_benchmark_expansion.py` no longer inserts its own scope note when this module is present.
- On narrow screens only the selected suite's score column is shown.

## Task grid

Covers come from `media/benchmark-overview/<ID>-<level>.jpg` (medium, then easy, then hard). The frames in `media/benchmark-covers/` carry camera labels and episode names burnt in from the source videos, so the grid does not use them.

## Styles

`scripts/home-structure.css` and `scripts/home-structure.js` are inserted in `<head>` between `<!-- HOME_STRUCTURE_START -->` and `<!-- HOME_STRUCTURE_END -->` so these sections are styled on first paint. Several legacy `body #top-ten …` rules use `!important`; the table rules override them deliberately.

Rebuild after changing data or templates:

```sh
python3 scripts/build_intro_story.py
python3 scripts/build_home_leaderboard_entry.py
python3 scripts/build_home_tasks.py
```
