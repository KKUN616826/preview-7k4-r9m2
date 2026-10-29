# Four-screen research introduction

The homepage introduction is now a scoped four-screen story: problem, project definition, feedback loop, and task exploration. Each screen fills the space below the fixed site navigation. Key statements rise and settle once on first reading; supporting text remains one paragraph. Brand colors and sans-serif typography match the site.

Only the introduction uses this behavior. Desktop wheel bursts advance one screen, reverse input can return, and the first/last screens release ordinary scrolling at their boundaries. Touch uses native scroll snapping. Progress buttons, Next, arrow/Page keys, and Skip to benchmark provide alternatives. Tall content remains scrollable instead of being clipped. Reduced motion switches instantly without pop animations; without JavaScript, all content remains a normal document.

Original research paragraphs live in the expandable research background. The existing full-resolution figure and its original-task-set caption are preserved. The task count comes from the shared benchmark catalog. Intro screen four does not imply the added tasks have scored results.

## Source and regeneration

- `scripts/intro-story.html`: four screens and navigation.
- `scripts/intro-story.css` and `.js`: scoped layout and interaction.
- `scripts/intro-story-background.html`: original research text.
- `scripts/intro-story-figure.html`: existing overview figure.
- `scripts/build_intro_story.py`: rebuild only this module with asset cache versions.
- `scripts/research_intro.html` includes `__INTRO_STORY__`; the main build resolves it too.

Run `python3 scripts/build_intro_story.py` for a focused update. `scripts/test_intro_story.cjs` checks gestures, keyboard, boundaries, skip navigation, content preservation, reduced motion, six widths, touch and no-script fallback. Other homepage modules and results are unchanged.
