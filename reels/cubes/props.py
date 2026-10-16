"""Картинки для предметов: папирус Мерера, берестяные грамоты. Возвращают RGBA-массивы."""
import numpy as np, random
from PIL import Image, ImageDraw, ImageFont

def _arr(im): return np.asarray(im.convert("RGBA"), np.uint8)
F = lambda s: ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", s)

def papyrus():
    """Папирус-журнал: столбцы значков и чёрточек-«сколько камня»."""
    im = Image.new("RGBA", (400, 540), (238, 220, 170, 255)); d = ImageDraw.Draw(im); rnd = random.Random(4)
    for col in range(3):
        x = 40 + col * 120
        for row in range(11):
            y = 40 + row * 44; w = rnd.choice([20, 28, 36])
            d.rectangle((x, y, x + w, y + 14), fill=(60, 40, 30, 255)); d.ellipse((x + 44, y - 2, x + 62, y + 16), outline=(60, 40, 30, 255), width=4)
            for t in range(rnd.randint(1, 4)): d.line((x + 74 + t * 8, y - 4, x + 74 + t * 8, y + 18), fill=(150, 40, 30, 255), width=4)
    d.rectangle((6, 6, 393, 533), outline=(170, 130, 80, 255), width=6)
    return _arr(im)

def bark_letter():
    """Берестяная грамота: строки угловатых «букв» нацарапаны на бересте."""
    im = Image.new("RGBA", (400, 500), (224, 198, 152, 255)); d = ImageDraw.Draw(im); rnd = random.Random(9)
    for row in range(8):
        y = 50 + row * 52; x = 30
        while x < 360:
            w = rnd.randint(14, 30); h = rnd.randint(22, 32)
            k = rnd.randint(0, 3)
            if k == 0: d.line((x, y, x + w // 2, y + h, x + w, y), fill=(70, 46, 30, 255), width=5)
            elif k == 1: d.line((x, y, x, y + h), fill=(70, 46, 30, 255), width=5); d.line((x, y + 4, x + w, y + 4), fill=(70, 46, 30, 255), width=5)
            elif k == 2: d.rectangle((x, y, x + w, y + h), outline=(70, 46, 30, 255), width=5)
            else: d.line((x, y + h, x + w, y), fill=(70, 46, 30, 255), width=5); d.line((x, y, x + w, y + h), fill=(70, 46, 30, 255), width=5)
            x += w + rnd.choice([10, 12, 40])
    return _arr(im)

def onfim():
    """Рисунок Онфима: всадник с копьём и ряд букв азбуки."""
    im = Image.new("RGBA", (640, 420), (224, 198, 152, 255)); d = ImageDraw.Draw(im); ink = (70, 46, 30, 255); w = 7
    d.rectangle((150, 190, 400, 250), outline=ink, width=w)                           # конь
    for lx in (165, 215, 335, 380): d.line((lx, 250, lx - 6, 320), fill=ink, width=w)
    d.line((400, 200, 450, 150, 470, 175), fill=ink, width=w); d.polygon([(470, 175), (500, 190), (468, 195)], outline=ink, width=w)
    d.line((150, 200, 105, 235), fill=ink, width=w)                                    # хвост
    d.rectangle((250, 120, 290, 190), outline=ink, width=w); d.ellipse((248, 70, 292, 114), outline=ink, width=w)   # всадник
    d.line((250, 78, 270, 52, 290, 78), fill=ink, width=w)                             # шлем
    d.line((290, 140, 470, 100), fill=ink, width=w); d.polygon([(470, 100), (540, 86), (472, 120)], outline=ink, width=w)   # копьё
    f = F(54)
    for i, ch in enumerate("АБВГДЕ"): d.text((40 + i * 92, 335), ch, font=f, fill=ink)
    return _arr(im)
