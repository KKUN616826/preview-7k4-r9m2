# Current hero: independent artwork with native annotations

`evaluation-artwork-hd.png` (1300×1210) was regenerated with the built-in imagegen tool on 2026-11-06 using the approved reference and the earlier isolated keyboard asset. The illustration contains no text or green process arrows. All labels, event marks, curves, arrowheads, and the caption are native HTML/SVG, retaining sharp rendering on high-density screens. On desktop, CSS displays the lunar upper portion and the keyboard/contact lower portion as independently positioned views of this same source. The lower view uses source y=650..1210, at 96% of the lunar frame width, with its complete mallet fade and contact inset inside the first viewport. The lunar fade adapts to the available height so the two views meet on white without a hard edge. Mobile keeps the original unified image. No raster pixels were changed for this layout adjustment. Its maximum CSS width is 1120px; the source is never enlarged beyond its intrinsic CSS pixel width.

The image remains an explanatory concept, not measured evaluation evidence. `approved-reference.png` is retained for design provenance and is no longer displayed.

Generation prompt summary: faithfully rebuild only the reference's right-hand composition as a high-definition standalone illustration on white. Keep the upper lunar dome with its lower fade, gray/gold meridians, small ghosted target keyboard, sharp central keyboard, approaching mallet with ghosted positions, and circular contact enlargement with dashed leaders. Remove all labels, process arrows, dots, webpage text, tabletop, terrain, and frames. Keep space for separately rendered HTML labels and SVG arrows.

## Prior iterations

### Approved reference

`approved-reference.png` is the user-supplied visual reference from 2026-11-06, copied without raster alteration. The webpage shows only its right-hand illustration via a CSS cropping window (source x=965..1914, y=0..882); the upper-left notch excludes text from the original reference. This preserves the moon shading, orbital lines, curved arrows, target keyboard, execution view, and contact enlargement exactly as supplied. The image's annotations are illustrative, not measured episode evidence. The left-hand heading, paragraph, data, and navigation remain native HTML.

The full source is 1914×900. Cropping and responsive placement are maintained in `media/protocol.css`. The reference is not used as a full-page screenshot.

## Earlier generated asset

The unused `keyboard-evaluation.png` asset below is retained from the prior iteration.

### Generation details

`keyboard-evaluation.png` is an AI-generated explanatory illustration, not a screenshot of an evaluated episode or evidence for a model result. It has a transparent background; no wooden table, terrain, or floor is included. All process labels and links are native webpage content.

Generated with the built-in imagegen tool on 2026-11-06, using the approved Protocol concept as reference. The moon background reuses the site's existing `media/moon/lroc-color-2k.jpg` asset.

Generation prompt:

> Extract and recreate ONLY the compact keyboard evaluation illustration from the RIGHT SIDE of the reference webpage as a production-ready transparent PNG asset. Do not generate a webpage. Truly transparent alpha background. Output a wide horizontal illustration, roughly 1600x800. Preserve three visual objects in one connected composition: left a smaller faint ghosted black keyboard with one ivory target-key outline; center a larger sharp black simulation-style keyboard with a slender robot mallet pressing one white key, two very faint ghosted mallet positions below; right a circular zoom inset showing the same mallet tip making contact with the keyboard's white key. Circle has thin ivory outline. Fine pale gray dashed leaders connect the selected key to the zoom inset. Keep simulation materials and proportions of the original. All three objects fully within bounds with generous transparent margin. Center sharp keyboard spans x=30–78%, ghosted target x=1–28%, circle x=80–99%. Keep overall visual height moderate and mallet modest, no bulky gripper bases. No words, NO LETTERS, no labels, no arrows between stages, no UI, no moon, no stars, no orbital lines. Crucially NO WOODEN TABLE, NO sand, NO desert, NO floor, NO ground, no rectangle or background card, no glow. Only isolated keyboards, mallet positions, target key outline, circle contact close-up and delicate leaders on TRANSPARENCY. This is an explanatory concept illustration, not experimental evidence. The reference text and website must be completely removed. Preserve the crisp black keyboard as the strongest visual object.
