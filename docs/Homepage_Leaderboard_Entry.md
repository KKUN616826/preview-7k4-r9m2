# Homepage leaderboard destination

The homepage ranking table at `#top-ten` is replaced by a scenic link to `leaderboard.html`. The existing navigation and project resource links remain available. The old section anchor is retained for inbound links; old `#leaderboard` links now go directly to the standalone page. Model results remain on the standalone leaderboard.

The panorama reuses `media/images/leaderboard-lunar-campus-v1.png`, converted into a 243 KB WebP. A cream gradient supports navy text and a sage button. Mobile stacks the copy above the scene; reduced motion disables the small button-arrow transition. The decorative image has an empty alt and is lazy loaded.

Sources: `scripts/home-leaderboard-entry.html`, `scripts/home-leaderboard-entry.css`. Run `python3 scripts/build_home_leaderboard_entry.py` to update only this module and its source template. The full site builder also calls this step; the expansion synchronizer skips result-scope notes for the homepage invitation. Legacy homepage leaderboard-specific JS/CSS are no longer loaded. Existing hidden legacy source sections are preserved.

Checked at widths 320, 390, 700, 1024 and 1920: no horizontal overflow, visible CTA, image loads, successful navigation to the standalone result table, no browser page errors. Desktop and mobile screenshots saved in the task outputs folder.
