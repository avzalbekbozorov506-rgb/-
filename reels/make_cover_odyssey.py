"""Обложка «Одиссей и сирены»: Уотерхаус «Улисс и сирены» (1891, Wikimedia Commons, PD) — корабль и Одиссей у мачты по центру."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
FX = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5          # центр кадра по горизонтали (доля ширины картины)
im = Image.open(f"{HERE}/art/waterhouse_sirens.jpg").convert("RGB")
sc = 2050 / im.height; big = im.resize((int(im.width * sc), 2050), Image.LANCZOS)
x0 = max(0, min(big.width - 1080, int(big.width * FX - 540))); bg = big.crop((x0, 60, x0 + 1080, 60 + 1920))
make_click(bg, "ОН ЗНАЛ, ЧТО\nНЕ УСТОИТ", "ПЕСНЬ XII", "ОДИССЕЙ", "и пение сирен", "26_odyssey_sirens_click", y=1060)
print("ok")
