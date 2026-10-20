"""Кликбейт-обложка сатиры «Как я заработал миллион с Claude Code»."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
from scenes_x import *
Hh = 1920
y = np.linspace(0, 1, Hh)[:, None, None]
img = Image.fromarray(np.clip(np.broadcast_to(np.array((6, 10, 22), np.float32)[None, None, :] * (1 + 1.4 * y), (Hh, W, 3)), 0, 255).astype(np.uint8))
lay = Image.new("RGBA", (W * K, Hh * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
for k in range(40):
    x = 60 + (k * 97) % 960; yy = 960 + (k * 131) % 400; d.text((x * K, yy * K), "₽", font=F(70 * K, "Black"), fill=dim(YEL, .5))
big(d, 540, 440, "1 000 000 ₽", GRN, 150)
lay = lay.resize((W, Hh), Image.LANCZOS); rgb = Image.new("RGB", lay.size, (0, 0, 0)); rgb.paste(lay, (0, 0), lay)
img.paste(lay, (0, 0), lay); img = ImageChops.screen(img, rgb.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .6)))
d2 = ImageDraw.Draw(img)
def txt(y0, s, fs, col, sh=(0, 0, 0)):
    f = F(fs); w = d2.textlength(s, font=f); x = (W - w) / 2
    d2.text((x + 5, y0 + 6), s, font=f, fill=sh); d2.text((x, y0), s, font=f, fill=col)
txt(320, "КАК Я ЗАРАБОТАЛ", 84, (255, 255, 255)); txt(660, "ЗА 2 НЕДЕЛИ", 110, (255, 200, 60)); txt(810, "с Claude Code", 84, (120, 210, 255))
d2.rectangle([60, 1380, 1020, 1540], fill=(210, 30, 40)); txt(1415, "ПРАВДА ИЛИ РАЗВОД?", 72, (255, 255, 255), (90, 0, 0))
d2.text((54, 70), "СМОТРИ ДО КОНЦА", font=F(26, "Bold"), fill=(150, 170, 200))
out = os.path.join(os.path.dirname(__file__), "..", "covers", "claude_million_click.jpg"); img.convert("RGB").save(out, quality=93); print(out)
