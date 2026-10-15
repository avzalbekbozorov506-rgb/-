"""Обложка ролика вне плана «Чужую беду терпеть легко» (Ларошфуко, максима 19) — Кауфман, «Скорбь Телемаха», фрагмент."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from PIL import Image
def crop(name, cx, cy, h=2300):
    """Кадр 9:16 из картины (как в make_covers_day2.py): высота h пикселей, центр (cx, cy) в долях."""
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); w = int(h * 9 / 16)
    s = max(w / im.width, h / im.height, 1.0); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = min(max(int(cx * im.width - w / 2), 0), im.width - w); y0 = min(max(int(cy * im.height - h / 2), 0), im.height - h)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 1920), Image.LANCZOS)
make_click(crop("met_436809", 0.7, 0.45, 2100), "ЧУЖУЮ БЕДУ\nТЕРПЕТЬ ЛЕГКО", "МАКСИМА 19", "ЛАРОШФУКО", "одна мысль", "35_larochefoucauld_grief_click", y=1150)
print("ok")
