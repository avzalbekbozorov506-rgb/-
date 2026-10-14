"""Обложка «Такой друг тебе не нужен» (Плутарх): Рембрандт, «Аристотель с бюстом Гомера» (The Met, CC0), вертикальный фрагмент."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from PIL import Image
def crop(name, cx, cy, h=2300):
    """Кадр 9:16 из картины: высота h пикселей, центр (cx, cy) в долях."""
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); w = int(h * 9 / 16)
    s = max(w / im.width, h / im.height, 1.0); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = min(max(int(cx * im.width - w / 2), 0), im.width - w); y0 = min(max(int(cy * im.height - h / 2), 0), im.height - h)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 1920), Image.LANCZOS)
make_click(crop("met_437394_v", 0.5, 0.42, 2200), "ТАКОЙ ДРУГ\nТЕБЕ НЕ НУЖЕН", "ПЛУТАРХ", "ДРУГ ИЛИ ТЕНЬ", "одна мысль", "30_plutarch_shadow_click", y=1060)
print("ok")
