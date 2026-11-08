#!/usr/bin/env python3
"""Paint the Moon at the top centre of the leaderboard artwork, so its surface faces the Earth's
horizon across the sky: the Earth's arc at the bottom, the Moon's arc at the top, both level in the
corrected view the page shows (leaderboard_stage._view).

The texture is the painted Moon of the campus artwork itself (v3e, top right, centre 1698.5, -369.5,
radius 590 artwork units), resampled in limb coordinates: a target point at depth d inside the new
limb and arc length s along it (measured from the bottom) takes the source point at depth d / SCALE
and arc length s / SCALE from a point on the source limb, so craters keep their foreshortening. The
source limb is visible over a limited arc and depth; beyond them the texture folds back (mirrored),
and the arc folds are spread over a soft band. A thin rim of the source's glow outside the limb is carried over too.

    python3 scripts/extend_lunar_sky.py media/images/leaderboard-lunar-campus-v3e.webp moonless.webp --no-moon
    python3 scripts/center_moon.py moonless.webp media/images/leaderboard-lunar-campus-v3e.webp media/images/leaderboard-lunar-campus-v6.webp
"""
import math
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from leaderboard_stage import MOON, ROLL, ZOOM, W, H   # noqa: E402  (MOON: the centred Moon, in view units)

SRC = (1698.5, -369.5, 590.0)       # the painted Moon in the source artwork (v3 frame = v5 frame at the top)
SCALE = 1.2                         # craters a little larger than in the source
CENTRE_PHI = -.12                   # source angle (radians from straight down) that lands at the bottom centre
SPAN = (-.58, .46)                  # usable source angles: enough painted depth on both sides of the limb
GLOW = 22                           # artwork units of the source's outer glow carried over


def _fold(a, lo, hi):
    """Reflect a into [lo, hi] (a triangle wave), so the texture mirrors at the ends of the span."""
    span = hi - lo
    u = np.mod(a - lo, 2 * span)
    return lo + np.where(u > span, 2 * span - u, u)


def main(sky_path, src_path, dst):
    sky = Image.open(sky_path).convert('RGB')
    src = np.asarray(Image.open(src_path).convert('RGB'), dtype=np.float32)
    wp, hp = sky.size
    k = wp / W                                   # pixels per artwork unit (same for both images)
    ys, xs = np.mgrid[0:int(420 * k), 0:wp].astype(np.float32) / k      # the top band, artwork units

    # Artwork -> view (the page turns the art by -ROLL about its centre and scales it by ZOOM).
    a = math.radians(ROLL)
    dx, dy = xs - W / 2, ys - H / 2
    xv = W / 2 + ZOOM * (dx * math.cos(a) + dy * math.sin(a))
    yv = H / 2 + ZOOM * (-dx * math.sin(a) + dy * math.cos(a))
    cx, cy, r = MOON
    rho = np.hypot(xv - cx, yv - cy)
    depth = (r - rho) / ZOOM                      # artwork units inside the new limb (negative outside)
    arc = np.arctan2(xv - cx, yv - cy) * r / ZOOM # artwork units along the limb from its bottom

    # Source limb coordinates.
    sx0, sy0, sr = SRC
    phi = _fold(CENTRE_PHI + arc / SCALE / sr, *SPAN)
    # The source shows only so much of its disc above the limb (the frame's top edge cuts it): deeper
    # than that, fold back (mirror) in depth too, rather than stretching the top row.
    dmax = sr - (4 - sy0) / np.cos(phi)
    d = np.clip(depth / SCALE, -GLOW, None)
    d = np.where(d > 0, _fold(d, 0, dmax), d)
    px = sx0 + (sr - d) * np.sin(phi)
    py = sy0 + (sr - d) * np.cos(phi)
    rgb = np.stack([map_coordinates(src[..., c], [py * k, px * k], order=1, mode='nearest') for c in range(3)], -1)

    # Soften the fold lines: blend with a slightly shifted sample where the fold is close.
    near = np.minimum(np.abs(phi - SPAN[0]), np.abs(phi - SPAN[1])) * sr      # artwork units to a fold
    fold_w = np.clip(1 - near / 40, 0, 1)[..., None] * .5
    phi2 = _fold(CENTRE_PHI + (arc + 37) / SCALE / sr, *SPAN)
    d = np.where(d > 0, _fold(d, 0, sr - (4 - sy0) / np.cos(phi2)), d)
    px2, py2 = sx0 + (sr - d) * np.sin(phi2), sy0 + (sr - d) * np.cos(phi2)
    rgb2 = np.stack([map_coordinates(src[..., c], [py2 * k, px2 * k], order=1, mode='nearest') for c in range(3)], -1)
    rgb = rgb * (1 - fold_w) + rgb2 * fold_w

    # Opacity: the disc, antialiased at the limb, plus the outer glow fading over GLOW units; the
    # glow is the source sky's brightening, so it is added as a lightening only.
    inside = np.clip(depth * k / 1.5 + .5, 0, 1)
    out = np.asarray(sky, dtype=np.float32).copy()
    band = out[:ys.shape[0]]
    glow = np.clip(1 + depth / GLOW, 0, 1) * (depth < 0) * .85
    lighter = np.maximum(band, rgb)
    band = band * (1 - glow[..., None]) + lighter * glow[..., None]
    band = band * (1 - inside[..., None]) + rgb * inside[..., None]
    out[:ys.shape[0]] = band
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(dst, 'WEBP', quality=88, method=6)
    print(f'{sky_path} + Moon from {src_path} -> {dst}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
