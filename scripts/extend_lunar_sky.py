#!/usr/bin/env python3
"""Make leaderboard-lunar-campus-v4.webp: v3 with SKY artwork units of sky inserted between the Moon
and the Earth's horizon, so the leaderboard has room to place models between the two surfaces.

The Moon stays where it is at the top of the frame. Everything else (sky below the Moon, the Earth,
the campus) moves down by SKY. The new band is the clean upper sky of v3 stretched to fit, with
its stars and wisps blurred away before stretching and a fresh sprinkling of stars added after; the Moon's disc in the
lower copy is filled with sky graded from the columns beside and below it.

    python3 scripts/extend_lunar_sky.py media/images/leaderboard-lunar-campus-v3.webp media/images/leaderboard-lunar-campus-v4.webp
    python3 scripts/extend_lunar_sky.py <in> <out> --no-moon    # leave the Moon out (scripts/center_moon.py)
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SKY = 260                                  # inserted height, artwork units (1983 x 793)
MOON = (1698.5, -369.5, 590.0)             # centre x, y and radius of the Moon's disc, artwork units
CLEAN = 220                                # rows 0..CLEAN (artwork units) hold only sky and the Moon


def main(src, dst, keep_moon=True):
    im = Image.open(src).convert('RGB')
    W, H = im.size
    k = W / 1983                           # pixels per artwork unit
    d, clean = round(SKY * k), round(CLEAN * k)
    cx, cy, r = (v * k for v in MOON)
    a = np.asarray(im, dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - cx, yy - cy)

    # 1. A moonless copy: inside the disc (plus its bright rim), sky graded from the clean column at
    #    the disc's left edge, shifted per column to meet the sky just below the limb.
    rim = r + 18 * k
    ref_x = int(cx - rim - 30 * k)
    ref = np.asarray(im.filter(ImageFilter.GaussianBlur(6 * k)), dtype=np.float32)[:, ref_x]   # H x 3
    moonless = a.copy()
    cols = range(int(cx - rim), W)
    first, shifts = {}, {}
    for x in cols:
        inside = np.where(dist[:, x] <= rim)[0]
        if len(inside):
            y0 = inside.max() + 1            # first sky row under the disc in this column
            first[x] = inside
            shifts[x] = a[y0 + int(4 * k):y0 + int(14 * k), x].mean(axis=0) - ref[min(H - 1, y0 + int(9 * k))]
    xs = np.array(sorted(shifts))
    sh = np.array([shifts[x] for x in xs])
    kern = np.exp(-0.5 * (np.arange(-120, 121) / 40.0) ** 2); kern /= kern.sum()
    sh = np.stack([np.convolve(np.pad(sh[:, c], 120, mode='edge'), kern, 'valid') for c in range(3)], axis=1)
    for x, d3 in zip(xs, sh):
        moonless[first[x], x] = ref[first[x]] + d3
    soft = np.asarray(Image.fromarray(moonless.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * k)), dtype=np.float32)
    inside_all = (dist <= rim)[..., None]
    moonless = np.where(inside_all, soft, moonless)
    feather = np.clip((rim + 6 * k - dist) / (6 * k), 0, 1)[..., None]
    moonless = moonless * (1 - feather) + soft * feather

    # 2. The new band: the clean upper sky without stars, stretched from `clean` to `clean + d` rows.
    band = Image.fromarray(moonless[:clean].clip(0, 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(9))
    band = band.filter(ImageFilter.GaussianBlur(10 * k)).resize((W, clean + d), Image.BICUBIC)
    out = Image.new('RGB', (W, H + d))
    out.paste(band, (0, 0))
    out.paste(Image.fromarray(moonless[clean:].clip(0, 255).astype(np.uint8)), (0, clean + d))
    # Blend the seam over 24 units.
    o = np.asarray(out, dtype=np.float32)
    s = int(24 * k)
    lower = moonless[clean:clean + s]
    w = np.linspace(1, 0, s)[:, None, None]
    o[clean + d:clean + d + s] = o[clean + d - 1] * w + lower * (1 - w)

    # 3. Grain and a few stars over the stretched band.
    rng = np.random.default_rng(11)
    o[:clean + d] += rng.normal(0, 1.4, (clean + d, W, 1))
    out = Image.fromarray(o.clip(0, 255).astype(np.uint8))
    stars = Image.new('L', out.size, 0)
    draw = ImageDraw.Draw(stars)
    for _ in range(int(140 * (W / 3966))):
        x, y = rng.uniform(0, W), rng.uniform(0, clean + d)
        rr = rng.choice([1.0, 1.4, 1.8, 2.6]) * k
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=int(rng.uniform(150, 255)))
    glow = stars.filter(ImageFilter.GaussianBlur(1.6 * k))
    out = Image.composite(Image.new('RGB', out.size, (255, 251, 238)), out, Image.eval(glow, lambda v: min(255, v * 2)))

    if not keep_moon:                      # a moonless sky, for scripts/center_moon.py
        out.save(dst, 'WEBP', quality=88, method=6)
        print(f'{src} -> {dst}: {W}x{H} -> {out.size[0]}x{out.size[1]}, no Moon')
        return
    # 4. The Moon, unmoved, over everything.
    mask = Image.fromarray((np.clip((r + 2 * k - dist) / (3 * k), 0, 1) * 255).astype(np.uint8))
    moon_layer = Image.new('RGB', out.size)
    moon_layer.paste(im, (0, 0))
    full_mask = Image.new('L', out.size, 0)
    full_mask.paste(mask, (0, 0))
    out = Image.composite(moon_layer, out, full_mask)
    out.save(dst, 'WEBP', quality=88, method=6)
    print(f'{src} -> {dst}: {W}x{H} -> {out.size[0]}x{out.size[1]}')


if __name__ == '__main__':
    main(*sys.argv[1:3], keep_moon='--no-moon' not in sys.argv)
