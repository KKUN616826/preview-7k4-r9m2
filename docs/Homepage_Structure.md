# Homepage structure

The homepage follows the pattern used by RoboDojo, Embodied First Exam and X2Real: each section has one job, and details live on the dedicated pages.

| Order | Section | Job | Source |
|---|---|---|---|
| 1 | `#overview` | Title, tagline, calls to action, interactive demo, paper information, film, key numbers | hand-maintained in `index.html`; demo data from `build_home_hero_data.py`, numbers from `build_home_stats.py` |
| 2 | `#introduction` | Motivation and the three suites (Mind, Act, Mind2Act) | `scripts/intro-story.html` via `build_intro_story.py` |
| 3 | `#diagnosis` | What the diagnosis card adds (four points) and two synthetic sample cards | `build_home_diagnosis.py` from `data/diagnosis-samples.json` |
| 3b | `#model-diagnostics` | Coming soon: the improvement loop (evaluate → diagnose → prescribe targeted data → train), drawn on the page so it continues the diagnosis cards | `build_home_diagnostics.py` from `home-diagnostics.html`, CSS and JS |
| 4 | `#top-ten` | Leaderboard preview: every model with reported scores, ranked by the selected suite | `build_home_leaderboard_entry.py` from `data/leaderboard-results.json` |
| 5 | `#tasks` | One moving film strip of all 30 tasks, then one link per suite | `build_home_tasks.py` from `data/benchmark-navigation.json` |
| 6 | `#news`, `#resources-overview`, `#contributors` | Updates, documents and people | hand-maintained in `index.html` |

The evaluation scope notes and the overview figure moved off the homepage; the introduction links to `protocol.html` and to `media/overview/mind2act-overview-v36.pdf`. The lunar capability map was removed with its scripts and tests (see git history before this change if it is needed again).

## Leaderboard preview

- Shows only models with all three suite scores; the row count and "N of M listed models" come from the data file.
- Default ranking is Mind, matching `leaderboard.html`. The Mind / Act / Mind2Act buttons re-rank in place (`scripts/home-structure.js`); ties share a rank.
- The note "from the original 15-task snapshot" is computed from the task lists in `views`, so it updates if the scored set grows. `sync_benchmark_expansion.py` no longer inserts its own scope note when this module is present.
- On narrow screens only the selected suite's score column is shown.

## Diagnosis cards

- The two cards are the harness v3 reference samples (`harness/docs/reference_card`, 2026-11-04): the English coding-agent card and the end-to-end card, translated with the English card's terms. They come from fault-injected simulated policies; the section and each card say "synthetic sample". Replace them with real cards once official results exist.
- Percentages in the failure bars are the exact segment widths from the reference cards. `media/diagnosis/diagnosis-card-sample-en.pdf` is the full English sample.
- Profile codes and axis letters use Pixelify Sans, the pixel face that matches the navigation wordmark.

## Hero title

Set like the logo lockup (`mind2act-official-logo.png` in git history before 6d5c517): the pixel planet (`media/images/mind2act-planet.webp`, cut from the navigation logo), "Mind2Act" in Pixelify Sans (`media/fonts/pixelify-sans`, OFL) with a mint "2", and a small tracked "WORLD". "WORLD" sits after "Act" when the line has room and under the name otherwise. Styles are in `scripts/hero-intro.css`; the markup is hand-maintained in `index.html`.

## Task strip

The intro already presents the three suites and `benchmark.html` holds the full catalogue, so the homepage shows the range only: every task in one strip that scrolls slowly, pauses on hover or focus, and becomes a plain horizontal scroller (no duplicate) with reduced motion.

## Task grid

Covers come from `media/benchmark-overview/<ID>-<level>.jpg` (medium, then easy, then hard). The frames in `media/benchmark-covers/` carry camera labels and episode names burnt in from the source videos, so the grid does not use them.

## Styles

`scripts/home-structure.css` and `scripts/home-structure.js` are inserted in `<head>` between `<!-- HOME_STRUCTURE_START -->` and `<!-- HOME_STRUCTURE_END -->` so these sections are styled on first paint. Several legacy `body #top-ten …` rules use `!important`; the table rules override them deliberately.

Rebuild after changing data or templates:

```sh
python3 scripts/build_intro_story.py
python3 scripts/build_home_leaderboard_entry.py
python3 scripts/build_home_tasks.py
python3 scripts/build_home_diagnosis.py
python3 scripts/build_home_diagnostics.py
```
