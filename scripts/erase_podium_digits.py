"""Remove the painted 1/2/3 from the podium pillars by per-column vertical interpolation."""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
H, W, _ = im.shape
s = W / 3966
# (x0, y0, x1, y1) boxes in 3966-wide artwork pixels, with a margin around each digit
boxes = [(1612, 745, 1708, 866), (1940, 668, 2018, 800), (2260, 770, 2356, 888)]
rng = np.random.default_rng(7)
for x0, y0, x1, y1 in boxes:
    x0, y0, x1, y1 = (round(v * s) for v in (x0, y0, x1, y1))
    k = 4  # rows averaged above and below for a steadier colour
    top = im[y0 - k:y0, x0:x1].mean(axis=0)
    bot = im[y1:y1 + k, x0:x1].mean(axis=0)
    t = np.linspace(0, 1, y1 - y0)[:, None, None]
    fill = top[None] * (1 - t) + bot[None] * t
    fill += rng.normal(0, 1.2, fill.shape)          # keep a little of the painted grain
    # feather the box edges so no seam shows
    yy = np.minimum(np.arange(y1 - y0), np.arange(y1 - y0)[::-1])[:, None]
    xx = np.minimum(np.arange(x1 - x0), np.arange(x1 - x0)[::-1])[None, :]
    a = np.clip(np.minimum(yy, xx) / 6, 0, 1)[..., None]
    im[y0:y1, x0:x1] = fill * a + im[y0:y1, x0:x1] * (1 - a)
Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(dst, quality=92, method=6)
