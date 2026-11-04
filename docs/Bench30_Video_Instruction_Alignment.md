# Benchmark video and instruction alignment

Aligned on 2026-11-03 in `leaderboard-motion`.

## Sources

- Supplied `bench30_videos/README.md`: 90 median-duration sampled recordings, 30 tasks × 3 difficulties; three camera views, 1920×480 at 30 fps.
- Supplied `bench30_instructions.md`: distinguishes fixed task instructions from per-episode PR1/PR2 targets.
- Supplied `bench30_instructions_per_episode.csv`: all 90 selected recordings match an exact episode and the README instruction.

## Task aliases

| Package | Website |
|---|---|
| E1 / F1 / P1 / S1 / M1 | E / F / P / S / M |
| FR3 | DR3 — periodic gate crossing |
| PR7 | DR7 — ball-on-tray transport |
| PR8 | PR6 — domino chain |

Retain website IDs and URLs; match by task semantics and package aliases, not filename prefix alone.

## Findings and changes

- 89 deployed video files differed from the supplied recordings; E2 Hard was absent. A different recording/version is not proof of an incorrect task assignment.
- Replaced the recordings with exact source-byte copies and added E2 Hard. No frame re-encoding.
- Updated 81 task/difficulty instruction blocks to the exact selected-episode instructions.
- PR1 targets (Easy / Medium / Hard): 25 / 16.5 / 16.25 ohm.
- PR2 targets (Easy / Medium / Hard): 100 / 105 / 122 V.
- Corrected E2's summary/focus to entity–value associations and expression decoding.
- Updated all posters to full three-camera frames; task catalog covers use the head-camera crop.
- Preserved original sources and replaced assets in the backup directory recorded in `data/bench30-sync-audit.json`.

## Reproducibility and validation

`data/benchmark-video-imports.json` records source task, website task, difficulty, episode ID, complete instruction, parameter values, hashes and video metadata for every recording.

`python3 scripts/sync_bench30_package.py <video-directory> <episode-csv>` validates aliases, README/CSV agreement and all 90 source files before importing. It is restricted to `leaderboard-motion` and creates a new recoverable backup.

Browser verification passed for all 90 recordings: metadata, playback, byte ranges, selected difficulty and exact instruction text. All 30 pages and all difficulty levels fit the 1366×768 desktop first screen. Source and installed video SHA-256 hashes match for all 90 files. Existing leaderboard measurements were not changed.
