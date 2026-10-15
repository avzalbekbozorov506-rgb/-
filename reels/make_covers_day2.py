"""Обложки роликов дня 2 (16.10): Макиавелли о друзьях и врагах, «любовь или страх», Сунь-цзы и придворные женщины."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from PIL import Image
def pad_top(name, out, px):
    """Сверху добавляет тёмный фон (растянутая и размытая верхняя полоса картины), чтобы лицо ушло ниже логотипа."""
    from PIL import ImageFilter
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); band = im.crop((0, 0, im.width, 40)).resize((im.width, px)).filter(ImageFilter.GaussianBlur(30))
    new = Image.new("RGB", (im.width, im.height + px)); new.paste(band, (0, 0)); new.paste(im, (0, px)); new.save(f"{HERE}/art/{out}.jpg", quality=92)
def crop(name, cx, cy, h=2300):
    """Кадр 9:16 из картины (как в make_covers_day1.py): высота h пикселей, центр (cx, cy) в долях."""
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); w = int(h * 9 / 16)
    s = max(w / im.width, h / im.height, 1.0); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = min(max(int(cx * im.width - w / 2), 0), im.width - w); y0 = min(max(int(cy * im.height - h / 2), 0), im.height - h)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 1920), Image.LANCZOS)
pad_top("wm_machiavelli_tito", "_mach_pad", 420)
make_click(crop("_mach_pad", 0.5, 0.0, 2400), "ДРУГ МОЖЕТ\nТЕБЯ ПОГУБИТЬ", "5 ПРАВИЛ", "МАКИАВЕЛЛИ", "о друзьях и врагах", "27_mach_friends_click", y=1060)
make_click(crop("_mach_pad", 0.5, 0.0, 2200), "ЛЮБОВЬ\nИЛИ СТРАХ?", "ГЛАВА XVII", "МАКИАВЕЛЛИ", "одна мысль", "28_mach_fear_click", y=1060)
make_click(crop("met_49249", 0.5, 0.3, 2000), "КАК ЗАСТАВИТЬ\nСЛУШАТЬСЯ", "ГЛАВА 65", "СУНЬ-ЦЗЫ", "история одного испытания", "29_suntzu_drill_click", y=1060)
print("ok")
