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

def payslip():
    """Расчётный листок легионера (по мотивам папируса Гая Мессия, Масада): жалованье и вычеты."""
    im = Image.new("RGBA", (420, 560), (238, 220, 170, 255)); d = ImageDraw.Draw(im); ink = (70, 44, 30, 255); red = (160, 36, 30, 255)
    d.rectangle((8, 8, 411, 551), outline=(170, 130, 80, 255), width=6)
    d.text((210, 52), "РАСЧЁТНЫЙ ЛИСТОК", font=F(36), fill=ink, anchor="mm"); d.line((40, 86, 380, 86), fill=ink, width=3)
    d.text((40, 120), "Жалованье: 50 денариев", font=F(28), fill=ink)
    for i, t in enumerate(["− еда", "− ячмень", "− сапоги", "− ремни", "− рубаха"]): d.text((60, 190 + i * 54), t, font=F(34), fill=red)
    d.line((40, 470, 380, 470), fill=ink, width=3); d.text((40, 495), "Остаток:  ?", font=F(40), fill=ink)
    return _arr(im)

def _font(sz): return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", sz)
def newspaper():
    im = Image.new("RGBA", (440, 560), (232, 224, 202, 255)); d = ImageDraw.Draw(im); ink = (40, 34, 30, 255)
    d.rectangle((8, 8, 431, 551), outline=ink, width=4); d.text((220, 44), "НИЦЦА · 1901", font=_font(30), fill=ink, anchor="mm"); d.line((30, 74, 410, 74), fill=ink, width=3)
    d.text((220, 150), "МЕРСЕДЕС", font=_font(64), fill=(150, 30, 30, 255), anchor="mm"); d.text((220, 214), "ПОБЕДИЛ В ГОНКАХ", font=_font(30), fill=ink, anchor="mm")
    d.rectangle((120, 270, 320, 340), fill=(60, 60, 66, 255)); d.rectangle((150, 240, 250, 272), fill=(60, 60, 66, 255))
    for cx in (155, 285): d.ellipse((cx - 28, 320, cx + 28, 376), fill=(30, 30, 30, 255))
    rnd = random.Random(3)
    for r in range(8):
        d.line((40, 410 + r * 17, 40 + rnd.randint(250, 360), 410 + r * 17), fill=(110, 100, 90, 255), width=5)
    return _arr(im)
def docs_merc():
    im = Image.new("RGBA", (460, 620), (236, 224, 192, 255)); d = ImageDraw.Draw(im); ink = (50, 38, 30, 255); red = (150, 30, 30, 255)
    d.rectangle((8, 8, 451, 611), outline=(160, 120, 70, 255), width=6)
    d.text((230, 70), "ТОВАРНЫЙ ЗНАК", font=_font(36), fill=ink, anchor="mm"); d.text((230, 130), "МЕРСЕДЕС", font=_font(58), fill=red, anchor="mm"); d.text((230, 190), "1902 год", font=_font(34), fill=ink, anchor="mm")
    d.line((50, 250, 410, 250), fill=ink, width=3)
    d.text((230, 330), "ФАМИЛИЯ", font=_font(36), fill=ink, anchor="mm"); d.text((230, 395), "ЕЛЛИНЕК-", font=_font(52), fill=red, anchor="mm"); d.text((230, 455), "МЕРСЕДЕС", font=_font(52), fill=red, anchor="mm"); d.text((230, 520), "1903 год", font=_font(34), fill=ink, anchor="mm")
    return _arr(im)
def sign_bmw():
    im = Image.new("RGBA", (560, 320), (34, 38, 56, 255)); d = ImageDraw.Draw(im); w = (240, 236, 224, 255)
    d.rectangle((10, 10, 549, 309), outline=(220, 200, 150, 255), width=6)
    d.text((280, 90), "BAYERISCHE", font=_font(52), fill=w, anchor="mm"); d.text((280, 160), "MOTOREN WERKE", font=_font(52), fill=w, anchor="mm")
    d.text((280, 250), "Баварские моторные заводы · 1917", font=_font(26), fill=(220, 200, 150, 255), anchor="mm")
    return _arr(im)
def _quarter(d, cx, cy, r, c1, c2):
    d.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 270, fill=c1); d.pieslice((cx - r, cy - r, cx + r, cy + r), 270, 360, fill=c2)
    d.pieslice((cx - r, cy - r, cx + r, cy + r), 0, 90, fill=c1); d.pieslice((cx - r, cy - r, cx + r, cy + r), 90, 180, fill=c2)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(20, 20, 24, 255), width=10)
def ad_poster():
    im = Image.new("RGBA", (560, 400), (240, 226, 190, 255)); d = ImageDraw.Draw(im); ink = (50, 38, 30, 255); BL = (40, 100, 190, 255); WH = (244, 244, 248, 255)
    d.rectangle((8, 8, 551, 391), outline=ink, width=6); d.text((280, 40), "РЕКЛАМА · 1929", font=_font(30), fill=ink, anchor="mm")
    d.rectangle((250, 70, 310, 360), fill=(120, 124, 132, 255)); d.rectangle((120, 190, 440, 240), fill=(120, 124, 132, 255))
    _quarter(d, 280, 215, 70, BL, WH); d.text((280, 372), "МОТОРЫ ДЛЯ САМОЛЁТОВ", font=_font(26), fill=ink, anchor="mm")
    return _arr(im)
def flag_vs_emblem():
    im = Image.new("RGBA", (640, 420), (240, 232, 214, 255)); d = ImageDraw.Draw(im); ink = (40, 34, 30, 255); BL = (40, 100, 190, 255); WH = (244, 244, 248, 255)
    d.rectangle((8, 8, 631, 411), outline=ink, width=5)
    for i in range(5):
        for j in range(4):
            d.rectangle((30 + i * 50, 70 + j * 50, 80 + i * 50, 120 + j * 50), fill=BL if (i + j) % 2 == 0 else WH)
    d.rectangle((30, 70, 280, 270), outline=ink, width=4); d.text((155, 40), "ФЛАГ БАВАРИИ", font=_font(26), fill=ink, anchor="mm")
    _quarter(d, 480, 170, 90, WH, BL); d.text((480, 40), "ЭМБЛЕМА", font=_font(26), fill=ink, anchor="mm")
    d.text((320, 350), "цвета — наоборот", font=_font(40), fill=(150, 30, 30, 255), anchor="mm")
    return _arr(im)

def _board(w=760, h=500):
    return Image.new("RGBA", (w, h), (34, 74, 58, 255))
def _chalk(sz): return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", sz)
WHITE = (244, 244, 236, 255); YEL = (250, 222, 110, 255); PINK = (246, 150, 140, 255)
def board_cleo():
    im = _board(); d = ImageDraw.Draw(im); d.rectangle((6, 6, 753, 493), outline=(120, 80, 50, 255), width=8)
    d.text((380, 50), "КТО ДРЕВНЕЕ?", font=_chalk(40), fill=YEL, anchor="mm")
    d.line((70, 250, 690, 250), fill=WHITE, width=5)
    for x, top, bot, c in [(110, "2560 до н. э.", "пирамида Хеопса", WHITE), (390, "30 до н. э.", "Клеопатра", YEL), (650, "1969", "Луна", WHITE)]:
        d.ellipse((x - 12, 238, x + 12, 262), fill=c); d.text((x, 205), top, font=_chalk(26), fill=c, anchor="mm"); d.text((x, 295), bot, font=_chalk(26), fill=c, anchor="mm")
    d.line((110, 380, 390, 380), fill=PINK, width=6); d.text((230, 420), "≈ 2500 лет", font=_chalk(34), fill=PINK, anchor="mm")
    d.line((390, 380, 650, 380), fill=YEL, width=6); d.text((480, 420), "≈ 2000 лет", font=_chalk(34), fill=YEL, anchor="mm")
    return _arr(im)
def board_oxford():
    im = _board(); d = ImageDraw.Draw(im); d.rectangle((6, 6, 753, 493), outline=(120, 80, 50, 255), width=8)
    d.text((380, 50), "ЧТО СТАРШЕ?", font=_chalk(40), fill=YEL, anchor="mm")
    d.text((190, 170), "Оксфорд", font=_chalk(44), fill=WHITE, anchor="mm"); d.text((190, 235), "учат с 1096", font=_chalk(36), fill=YEL, anchor="mm")
    d.text((570, 170), "Ацтеки", font=_chalk(44), fill=WHITE, anchor="mm"); d.text((570, 235), "Теночтитлан, 1325", font=_chalk(30), fill=PINK, anchor="mm")
    d.line((380, 130, 380, 280), fill=WHITE, width=4)
    d.line((90, 380, 670, 380), fill=WHITE, width=5)
    for x, t, c in [(150, "1096", YEL), (560, "1325", PINK)]:
        d.ellipse((x - 12, 368, x + 12, 392), fill=c); d.text((x, 430), t, font=_chalk(34), fill=c, anchor="mm")
    return _arr(im)
def board_vikings():
    im = _board(); d = ImageDraw.Draw(im); d.rectangle((6, 6, 753, 493), outline=(120, 80, 50, 255), width=8)
    d.text((380, 50), "РОГАТЫЕ ШЛЕМЫ ВИКИНГОВ", font=_chalk(36), fill=YEL, anchor="mm")
    d.ellipse((260, 130, 500, 330), outline=WHITE, width=6); d.rectangle((260, 230, 500, 330), fill=(34, 74, 58, 255)); d.arc((260, 130, 500, 330), 180, 360, fill=WHITE, width=6)
    d.line((300, 150, 250, 100), fill=PINK, width=8); d.line((460, 150, 510, 100), fill=PINK, width=8)
    d.line((220, 90, 540, 340), fill=PINK, width=10); d.line((540, 90, 220, 340), fill=PINK, width=10)
    d.text((380, 395), "выдумка 1876 года", font=_chalk(38), fill=YEL, anchor="mm"); d.text((380, 445), "опера Вагнера", font=_chalk(30), fill=WHITE, anchor="mm")
    return _arr(im)
def board_final():
    im = _board(); d = ImageDraw.Draw(im); d.rectangle((6, 6, 753, 493), outline=(120, 80, 50, 255), width=8)
    d.text((380, 70), "РЕЗУЛЬТАТ", font=_chalk(44), fill=YEL, anchor="mm"); d.text((380, 230), "0 из 3", font=_chalk(130), fill=PINK, anchor="mm")
    d.text((380, 370), "Домашнее задание:", font=_chalk(34), fill=WHITE, anchor="mm"); d.text((380, 420), "отправить другу", font=_chalk(40), fill=YEL, anchor="mm")
    return _arr(im)
