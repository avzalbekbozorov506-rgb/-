"""Процедурная «нейронная» текстура (синие облака + светящиеся связи) — собственная генерация, без чужих прав.
  python3 art_tools/gen_neuro.py N  → art/gen_neuro_0..N-1.jpg (1620×1000)"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H = 1620, 1000
def noise(rng, w, h, oct_=6):
    out = np.zeros((h, w), np.float32)
    for o in range(oct_):
        s = 2 ** (o + 2); g = rng.random((h // (W // s) + 2, s + 2)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += np.asarray(im, np.float32) / 255 / (o + 1)
    out -= out.min(); return out / out.max()
for k in range(int(sys.argv[1]) if len(sys.argv) > 1 else 4):
    rng = np.random.default_rng(100 + k)
    n = noise(rng, W, H) ** 2.2
    base = np.dstack([4 + 30 * n, 10 + 70 * n, 30 + 170 * n]).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(base).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts = rng.random((70, 2)) * [W, H]
    for i in range(len(pts)):
        dist = np.hypot(*(pts - pts[i]).T); near = np.argsort(dist)[1:4]
        for j in near:
            (x0, y0), (x1, y1) = pts[i], pts[j]; mx, my = (x0 + x1) / 2 + rng.normal(0, 40), (y0 + y1) / 2 + rng.normal(0, 40)
            seg = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1) for t in np.linspace(0, 1, 24)]
            d.line(seg, fill=(120, 190, 255, int(rng.uniform(40, 120))), width=int(rng.integers(1, 4)))
    for x, y in pts:
        r = rng.uniform(2, 6); d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 230, 255, 200))
    glow = lay.filter(ImageFilter.GaussianBlur(6)); img.alpha_composite(glow); img.alpha_composite(lay)
    img.convert("RGB").save(f"art/gen_neuro_{k}.jpg", quality=92); print("art/gen_neuro_%d.jpg" % k)
