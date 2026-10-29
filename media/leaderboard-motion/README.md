# Local three-arm animation source

`campus-loop.mp4` is a silent, six-second, 1920 × 768 H.264 loop used behind the live leaderboard controls and scores. It is rendered from `scene.html` and `scene.js`, with the existing campus artwork and two imagegen repair plates. No external video service or Three.js is required.

Left and right arm cycles are offset by 0.8 and 2 seconds. The left yellow, right red and foreground blue blocks follow their respective grippers. This remains a 2D layered concept: complex 3D occlusion and crop edges are not a finished rig.

To regenerate, run `node scripts/render_leaderboard_motion.cjs` from the project root with Playwright available in Node's module path, Chrome installed, and FFmpeg on PATH. The script exports frames into an OS temporary directory and removes them after encoding. The authored source files stay here.

The website keeps its static poster when reduced motion is requested or video loading fails. Users can pause playback. Scrolling the scene out of view or hiding the tab suspends playback. Ranking controls and data remain independent of the video.
