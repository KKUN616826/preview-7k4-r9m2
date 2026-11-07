#!/usr/bin/env python3
"""Make the Earth on the lunar campus read as the Earth: a soft fog-blue ocean under its white clouds, and
a thin bright atmosphere along its limb.

Works on v3-frame images (1983 x 793 artwork units, any pixel scale): the campus artwork and the two
clean plates of the arm loop, so the still and the loop agree. Only bluish pixels between the horizon
and the lunar ground are recoloured, and the rim is drawn only on sky pixels, so the dome, towers,
dish and cylinders that stand in front of the Earth are left as they are.

    python3 scripts/enhance_earth.py <in.webp> <out.webp> [<in> <out> ...]
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

# The horizon, fitted on v4 (v3 y + 260): y = A x^2 + B x + C, artwork units.
A, B, C, SKY = 1.8239e-05, 1.31081e-02, 528.449, 260


def horizon(x):
    return A * x * x + B * x + C - SKY


def ground(x):
    """Where the lunar ground starts below the Earth."""
    return 383 + .02 * (x - 400)


def _edge(blue, k):
    """The Earth's top edge per pixel column: where the pale sky turns ocean blue, searched near the
    fitted horizon and smoothed; columns hidden by a building fall back to the fit."""
    hp, wp = blue.shape
    fit = horizon(np.arange(wp) / k)
    edge = fit.copy()
    for x in range(wp):
        y0, y1 = int((fit[x] - 25) * k), int((fit[x] + 15) * k)
        col = blue[max(0, y0):y1, x]
        run = np.convolve(col > 30, np.ones(int(4 * k)), 'valid') >= int(4 * k)
        hit = np.argmax(run) if run.any() else -1
        if hit >= 0:
            edge[x] = (max(0, y0) + hit) / k
    # Keep only edges close to a smooth curve, then smooth along x.
    good = np.abs(edge - fit) < 14
    c = np.polyfit(np.arange(wp)[good] / k, edge[good], 2) if good.sum() > wp // 4 else None
    return np.polyval(c, np.arange(wp) / k) if c is not None else fit


def enhance(src, dst):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im, dtype=np.float32)
    hp, wp, _ = a.shape
    k = wp / 1983
    ys, xs = np.mgrid[0:hp, 0:wp] / k
    soft = np.asarray(im.filter(ImageFilter.GaussianBlur(2 * k)), dtype=np.float32)
    blue = soft[..., 2] - soft[..., 0]
    lum = soft @ np.array([.3, .55, .15], dtype=np.float32)
    h, g = _edge(blue, k)[None, :] * np.ones((hp, 1)), ground(xs)

    # Ocean: within the band, weighted by how blue the pixel is; fades out toward the lunar ground.
    band = np.clip((ys - h + 1) / 2, 0, 1) * np.clip((g - ys) / 14, 0, 1)
    # Bright bluish pixels only: the ocean is bright (luminance ~200+), the arms' blue joints are dark.
    w = band * np.clip((blue - 10) / 26, 0, 1) * np.clip((lum - 150) / 30, 0, 1) * .5
    t = np.clip((lum - 120) / 120, 0, 1)[..., None]
    deep, light = np.array([84, 132, 170], np.float32), np.array([158, 196, 222], np.float32)   # the site's fog blues
    ocean = deep * (1 - t) + light * t
    # Slightly deeper toward the limb, as the atmosphere thickens.
    depth = np.clip((ys - h) / 40, 0, 1)[..., None]
    ocean = ocean * (.92 + .08 * depth)
    out = a * (1 - w[..., None]) + ocean * w[..., None]

    # Atmosphere: a bright rim hugging the horizon and a blue haze just above it, on sky pixels only.
    sky = np.clip((blue - 8) / 14, 0, 1) * (ys < h + 1)
    d = h - ys
    rim = np.exp(-.5 * ((d - 1.2) / 2.2) ** 2) * .6
    haze = np.clip(1 - d / 26, 0, 1) * (d > 0) * .22
    out = out * (1 - (rim * sky)[..., None]) + np.array([236, 249, 255], np.float32) * (rim * sky)[..., None]
    out = out * (1 - (haze * sky)[..., None]) + np.array([150, 205, 238], np.float32) * (haze * sky)[..., None]

    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(dst, 'WEBP', quality=90, method=6)
    print(f'{src} -> {dst}')


if __name__ == '__main__':
    args = sys.argv[1:]
    for i in range(0, len(args), 2):
        enhance(args[i], args[i + 1])
