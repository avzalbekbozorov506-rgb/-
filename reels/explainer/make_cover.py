"""Кликбейт-обложка ролика «Tesla Roadster едет по потолку» (1080x1920, важное — в зоне y 240–1680)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
from scenes_x import *

Hh = 1920
y = np.linspace(0, 1, Hh)[:, None, None]
base = np.array((6, 10, 22), np.float32)[None, None, :] * (1 + 1.4 * y)
img = Image.fromarray(np.clip(np.broadcast_to(base, (Hh, W, 3)), 0, 255).astype(np.uint8))
lay = Image.new("RGBA", (W * K, Hh * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
cy = 760; ceiling(d, cy)
car(d, 560, cy, 0, 2.05, 1, -1, xray=0)
gas(d, 1.3, (0, cy + 140, W, 1560), 170, 21, 0, CY, 3.5)
for xx in (230, 420, 610, 800):
    arrow(d, xx, 1390, xx, 1110, CY, 9, 28)
lay = lay.resize((W, Hh), Image.LANCZOS)
rgb = Image.new("RGB", lay.size, (0, 0, 0)); rgb.paste(lay, (0, 0), lay)
img.paste(lay, (0, 0), lay)
img = ImageChops.screen(img, rgb.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .45)))
d2 = ImageDraw.Draw(img)
def txt(y0, s, fs, col, sh=(0, 0, 0)):
    f = F(fs, "Black"); w = d2.textlength(s, font=f); x = (W - w) / 2
    d2.text((x + 5, y0 + 6), s, font=f, fill=sh); d2.text((x, y0), s, font=f, fill=col)
txt(300, "TESLA", 150, (255, 255, 255))
txt(450, "ЕДЕТ ПО ПОТОЛКУ", 92, (255, 190, 40))
d2.rectangle([60, 1490, W - 60, 1640], fill=(210, 30, 40))
txt(1522, "КАК ОНА НЕ ПАДАЕТ?", 70, (255, 255, 255), (90, 0, 0))
d2.text((54, 70), "15 ОКТЯБРЯ · ПОКАЗ", font=F(26, "Bold"), fill=(110, 140, 170))
out = os.path.join(os.path.dirname(__file__), "..", "covers", "tesla_ceiling_click.jpg")
img.convert("RGB").save(out, quality=93); print(out)
