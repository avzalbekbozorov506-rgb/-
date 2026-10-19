"""Обложка money_map: Изенбрант «Человек, взвешивающий золото» (The Met, CC0)."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
im = Image.open(os.path.join(HERE, "art/met_436722.jpg")).convert("RGB")
w, h = im.size
im = im.crop((int(w * .04), int(h * .025), int(w * .955), int(h * .975)))
w, h = im.size; nh = int(w * 16 / 9)
im = im.crop((0, max(0, (h - nh) // 2), w, max(0, (h - nh) // 2) + nh)) if nh < h else im
make_click(im.resize((1080, 1920), Image.LANCZOS), "КУДА УТЕКАЕТ\nТВОЯ ЗАРПЛАТА?", "КАРТА ДЕНЕГ", "МЫ СПРОСИЛИ КЛОДА", "50 000 ₽ в месяц — мимо тебя", "42_money_map_click", y=1150)
print("ok")
