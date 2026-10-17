"""Обложка части 2: «Tesla 0→100 за 0,81 с — это не шины»."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
from scenes_x import *
Hh = 1920
y = np.linspace(0, 1, Hh)[:, None, None]
img = Image.fromarray(np.clip(np.broadcast_to(np.array((6, 10, 22), np.float32)[None, None, :] * (1 + 1.4 * y), (Hh, W, 3)), 0, 255).astype(np.uint8))
lay = Image.new("RGBA", (W * K, Hh * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
G = 1180; ground(d, G)
for k in range(16): d.line([(60) * K, (G - 40 - 14 * k) * K, (330) * K, (G - 40 - 14 * k) * K], fill=dim(CY, .5), width=3 * K)
car(d, 640, G, 0, 1.25, 1, 1)
for k in range(14):
    u = k / 14; circ(d, ((420 - 330 * u) * K, (G - 90 + 10 * math.sin(k * 3)) * K), (9 - 6 * u) * K, fill=dim(WHITE, 1 - u))
lay = lay.resize((W, Hh), Image.LANCZOS); rgb = Image.new("RGB", lay.size, (0, 0, 0)); rgb.paste(lay, (0, 0), lay)
img.paste(lay, (0, 0), lay); img = ImageChops.screen(img, rgb.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .45)))
d2 = ImageDraw.Draw(img)
def txt(y0, s, fs, col, sh=(0, 0, 0)):
    f = F(fs, "Black"); w = d2.textlength(s, font=f); x = (W - w) / 2
    d2.text((x + 5, y0 + 6), s, font=f, fill=sh); d2.text((x, y0), s, font=f, fill=col)
txt(290, "0 → 100 КМ/Ч", 110, (255, 255, 255)); txt(430, "ЗА 0,81 СЕКУНДЫ", 90, (255, 190, 40))
d2.rectangle([60, 1400, W - 60, 1560], fill=(210, 30, 40)); txt(1425, "ЭТО НЕ ШИНЫ!", 96, (255, 255, 255), (90, 0, 0))
txt(560, "ЗАЯВЛЕНО TESLA", 54, (150, 170, 200))
d2.text((54, 70), "TESLA ROADSTER · ЧАСТЬ 2", font=F(26, "Bold"), fill=(110, 140, 170))
out = os.path.join(os.path.dirname(__file__), "..", "covers", "tesla_part2_click.jpg"); img.convert("RGB").save(out, quality=93); print(out)
