# Local three-station animation source

`campus-loop.mp4` is a silent, eight-second, 2880 × 1152 H.264 loop (CRF 20) used behind the live leaderboard controls and scores. It is rendered from `scene.html` and `scene.js`, with the campus artwork (`media/images/leaderboard-lunar-campus-v2.webp`) and two repair plates (`clean-plate-front.webp`, `clean-plate-sides.webp`). No external video service or Three.js is required.

Each arm acts out one benchmark case from its suite, and the leaderboard labels each station with a link to that task (`STATIONS` in `scripts/leaderboard_stage.py`):

- Left, **Mind** (E, Duplicate Item Identification): the board marks the green triangle, covers its tiles, and the probe weighs the blue and yellow blocks before tapping the green one; the triangle reopens with a check.
- Front, **Mind2Act** (CP08, Reference-Guided Block Construction): a projected reference shows blue on yellow, disappears, and the arm stacks the blue block on the yellow one from memory; the reference returns in green when they match.
- Right, **Act** (FR1, Continuous Conveyor Picking): rollers turn and a parcel rides the belt; the arm matches its speed, picks it in motion and sets it on the collection deck.

This remains a 2D layered concept: complex 3D occlusion and crop edges are not a finished rig. Station labels that the cover crop would cut at the stage edge are hidden, and all labels are hidden below 760 px.

To regenerate, run `node scripts/render_leaderboard_motion.cjs` from the project root with Playwright available in Node's module path, Chrome installed, and FFmpeg on PATH. The script exports frames into an OS temporary directory and removes them after encoding. The authored source files stay here.

The website keeps its static poster when reduced motion is requested or video loading fails. Users can pause playback. Scrolling the scene out of view or hiding the tab suspends playback. Ranking controls and data remain independent of the video.

## Resolution (2026-11-06)

The original artwork and plates were 1983 × 793. They were upscaled 2× (3966 × 1586) with Real-ESRGAN x4plus (ONNX, 64-pixel tiles with 8-pixel overlap, then Lanczos down to 2×) and stored as WebP. The loop is rendered at device scale 1.5 (2880 × 1152) so it stays sharp on wide and high-density screens. The previous 1983 × 793 PNG remains in git history (`media/images/leaderboard-lunar-campus-v1.png`).
