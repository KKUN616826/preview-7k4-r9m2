# Local three-station animation source

`campus-loop.mp4` is a silent, eight-second, 2880 × 1152 H.264 loop (CRF 20) used behind the live leaderboard controls and scores. It is rendered from `scene.html` and `scene.js`, with the campus artwork (`media/images/leaderboard-lunar-campus-v3.webp`) and two repair plates (`clean-plate-front.webp`, `clean-plate-sides.webp`). No external video service or Three.js is required.

Each arm illustrates one evaluation dimension, and the leaderboard labels the stations with the dimension only (`STATIONS` in `scripts/leaderboard_stage.py`, linking to the suite on `benchmark.html`). Each label is a light tag in the style of the stage cards, on a thin leader whose marker sits on the arm's fixed shoulder pivot (`S` in `scene.js`); a tag the stage crop pushes past the edge is hidden:

- Left, **Mind** (memory and decisions): the board marks the green triangle and covers its tiles; the arm weighs the blue and yellow blocks before touching the green one, and the triangle reopens with a check.
- Front, **Mind2Act** (reasoning and execution together): a projected reference (blue on yellow) shows, disappears, and the arm rebuilds it from memory; the reference returns in green.
- Right, **Act** (physical execution): rollers turn and a parcel rides the belt; the arm matches its speed, picks it in motion and sets it on the deck.

The painted tools differed (a long probe, short fingers and a hook), so each wrist is cut at its flange and all three carry the same drawn two-finger gripper (`gripper()` in `scene.js`).

This remains a 2D layered concept: complex 3D occlusion and crop edges are not a finished rig. Station labels that the cover crop would cut at the stage edge are hidden, and all labels are hidden below 760 px.

To regenerate, run `node scripts/render_leaderboard_motion.cjs` from the project root with Playwright available in Node's module path, Chrome installed, and FFmpeg on PATH. The script exports frames into an OS temporary directory and removes them after encoding. The authored source files stay here.

The website keeps its static poster when reduced motion is requested or video loading fails. Users can pause playback. Scrolling the scene out of view or hiding the tab suspends playback. Ranking controls and data remain independent of the video.

## Resolution (2026-11-06)

The original artwork and plates were 1983 × 793. They were upscaled 2× (3966 × 1586) with Real-ESRGAN x4plus (ONNX, 64-pixel tiles with 8-pixel overlap, then Lanczos down to 2×) and stored as WebP. The loop is rendered at device scale 1.5 (2880 × 1152) so it stays sharp on wide and high-density screens. The previous 1983 × 793 PNG remains in git history (`media/images/leaderboard-lunar-campus-v1.png`).

## Launch towers (2026-11-07)

`leaderboard-lunar-campus-v3.webp` is v2 with the painted 1, 2 and 3 removed from the three central pillars, so they read as launch towers rather than a three-place podium. `scripts/erase_podium_digits.py` fills each digit box by vertical interpolation down each column (the cylinders are shaded across, not down), adds faint grain and feathers the edges; no other pixel changes. The loop was re-rendered from the same scene with v3.

Above the campus, the leaderboard stage draws the climb (`_climb` in `scripts/leaderboard_stage.py`): every reported VLA / WAM model at the height of its Overall score between the launch line (0) and the target line (100), in release order, with a step line for the best score so far and a bracket for the distance still to go. Before three results exist, the climb uses anonymous placeholder entries, captioned as not results.
