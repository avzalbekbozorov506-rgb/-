"""Сунь-цзы, «Искусство войны» (孫子兵法). Перевод — собственный, с древнекитайского. Анимация в стиле туши."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from make_scenes_demo import figure, walk_pose, bird, POSES

W, H = 1080, 1920
PAPER_T, PAPER_B, INK, RED = (198, 184, 158), (150, 134, 110), (32, 28, 28), (172, 46, 38)
HEAD = ("СУНЬ-ЦЗЫ", "«ИСКУССТВО ВОЙНЫ», V В. ДО Н. Э.")
TITLE = ("СУНЬ-ЦЗЫ", "«Искусство войны»", "ПЯТЬ ПРИНЦИПОВ, КОТОРЫЕ РАБОТАЮТ ДО СИХ ПОР")
PROG = [[45, 52, 57, 60], [43, 50, 55, 62], [41, 48, 53, 60], [40, 47, 52, 59]]
DRUM = True
CREDIT = "Анимация · перевод с древнекитайского"
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

def paper(top=PAPER_T, bot=PAPER_B):
    yy = np.linspace(0, 1, H)[:, None, None]
    a = np.array(top) * (1 - yy) + np.array(bot) * yy
    a = np.repeat(a, W, 1) + np.random.default_rng(3).normal(0, 4, (H, W, 1))       # фактура бумаги
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
def ridge(seed, base, amp, col, blur=0, alpha=255):
    r = random.Random(seed); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts, y = [(0, H)], base - r.uniform(0, amp)
    for x in range(0, W + 40, 40):
        y = min(max(y + r.uniform(-amp * 0.35, amp * 0.35), base - amp), base); pts.append((x, y))
    pts.append((W, H)); d.polygon(pts, fill=col + (alpha,))
    return lay.filter(ImageFilter.GaussianBlur(blur)) if blur else lay
MIST = Image.new("RGBA", (W * 2, 300), (0, 0, 0, 0)); _m = ImageDraw.Draw(MIST)
for k in range(9): x = k * 260; _m.ellipse((x, 80 + (k % 3) * 40, x + 520, 220 + (k % 3) * 30), fill=(235, 228, 214, 70))
MIST = MIST.filter(ImageFilter.GaussianBlur(30))
def mist(im, y, t, sp=25): im.alpha_composite(MIST, (int(-(t * sp) % W), y))
def flag(d, x, top, t, ph=0, h=90, w=110, col=RED, tilt=0):
    bx = x + math.sin(tilt) * (top * 0) ; d.line(((x, top), (x - math.sin(tilt) * 260, top + math.cos(tilt) * 260)), fill=INK, width=6)
    pts = [(x + k * w / 8, top + 8 * math.sin(t * 5 - k * 0.7 + ph)) for k in range(9)]
    pts += [(x + k * w / 8, top + h + 8 * math.sin(t * 5 - k * 0.7 + ph)) for k in range(8, -1, -1)]
    d.polygon(pts, fill=col)
SOLDIER = dict(robe=(46, 40, 40), robe2=(30, 26, 26), hat=(24, 20, 20), beard=None)

# 0. Полководец на утёсе, красное солнце, туман
BG0 = paper(); [BG0.alpha_composite(l) for l in (ridge(1, 1000, 260, (120, 116, 112), 6, 200), ridge(2, 1120, 200, (84, 80, 78), 3, 230))]
_d = ImageDraw.Draw(BG0); _d.polygon([(0, 1010), (360, 975), (520, 1020), (560, 1400), (0, 1400)], fill=INK)
def s_intro(lt, D, sun_y=520):
    im = BG0.copy(); d = ImageDraw.Draw(im)
    sy = sun_y + lt * 6; d.ellipse((700, sy - 110, 920, sy + 110), fill=RED + (230,))
    mist(im, 820, lt, 30); mist(im, 640, lt + 40, 18)
    d = ImageDraw.Draw(im)
    for i in range(3): bird(d, (200 + lt * 70 + i * 90) % (W + 200) - 100, 420 + i * 30 + 10 * math.sin(lt + i), lt + i, 1.0, INK)
    pose = dict(POSES["stand"]); pose["ua2"] = 30; pose["el2"] = -10
    figure(d, 300, 990, pose, s=0.95, f=1, **SOLDIER)
    flag(d, 368, 700, lt, h=100, w=140)
    return im.convert("RGB")

# 1. Две армии: одна отступает без боя
BG1 = paper(); [BG1.alpha_composite(l) for l in (ridge(5, 860, 160, (128, 122, 116), 6, 190), ridge(6, 940, 120, (98, 92, 88), 3, 220))]
ImageDraw.Draw(BG1).rectangle((0, 980, W, H), fill=(120, 106, 86))
def s_armies(lt, D):
    im = BG1.copy(); mist(im, 760, lt); d = ImageDraw.Draw(im); u = ease((lt - D * 0.35) / (D * 0.45))
    for r in range(3):
        for c in range(5):
            figure(d, 70 + c * 70 + r * 18, 1000 + r * 40, POSES["stand"], s=0.36, f=1, **SOLDIER)
            x = 660 + c * 70 + r * 18
            if u <= 0.05: figure(d, x, 1000 + r * 40, POSES["stand"], s=0.36, f=-1, **SOLDIER)
            else: figure(d, x + u * 520, 1000 + r * 40, walk_pose(lt * 6 + c + r, 22), s=0.36, f=1, **SOLDIER)
    for k, x in enumerate([110, 250, 390]): flag(d, x, 700, lt, k, h=60, w=80)
    for k, x in enumerate([720, 860]): flag(d, x + u * 520, 700 + u * 120, lt, k + 3, h=60, w=80, col=(70, 66, 64), tilt=u * 0.9)
    pose = dict(POSES["stand"]); pose["ua1"] = lerp(8, 150, ease((lt - 1.0) / 1.2)); pose["el1"] = 10
    figure(d, 480, 1090, pose, s=0.62, f=1, robe=(120, 30, 30), robe2=(80, 20, 20), hat=INK, beard=INK)
    return im.convert("RGB")

# 2. Отражение в озере: знай себя
BG2 = paper((170, 168, 160), (120, 116, 110)); [BG2.alpha_composite(l) for l in (ridge(9, 820, 200, (110, 108, 106), 6, 200), ridge(10, 880, 120, (80, 78, 76), 3, 230))]
WATER = 900
def s_reflect(lt, D):
    im = BG2.copy(); d = ImageDraw.Draw(im)
    d.ellipse((680, 360, 800, 480), fill=(236, 230, 214))
    mist(im, 700, lt, 15); d = ImageDraw.Draw(im)
    d.rectangle((0, 880, 520, 905), fill=INK)                                    # берег
    figure(d, 330, 902, POSES["jalsa"], s=0.9, f=1, robe=(110, 30, 30), robe2=(80, 20, 20), hat=INK, beard=INK)
    a = np.asarray(im.convert("RGB")).copy(); top = a[WATER - 260:WATER][::-1].astype(np.float32)
    for r in range(top.shape[0]):                                                # отражение с рябью
        top[r] = np.roll(top[r], int(6 * math.sin(r * 0.18 + lt * 3) * (r / 260 + 0.2)), axis=0)
    top = top * 0.62 + np.array([60, 66, 74]) * 0.38
    a[WATER:WATER + 260] = top.astype(np.uint8)
    out = Image.fromarray(a); d = ImageDraw.Draw(out)
    for k in range(6):
        y = WATER + 20 + k * 38; d.line(((60 + 40 * math.sin(lt + k), y), (W - 60, y)), fill=(200, 196, 186), width=1)
    return out

# 3. Ночной лагерь: много костров, мало воинов
BG3 = paper((40, 44, 58), (24, 24, 30)); _d = ImageDraw.Draw(BG3)
BG3.alpha_composite(ridge(13, 900, 160, (16, 18, 24), 2, 255)); _d = ImageDraw.Draw(BG3)
STARS = [(random.Random(k).uniform(0, W), random.Random(k + 99).uniform(260, 700)) for k in range(60)]
FIRES = [(80 + (k % 9) * 115 + (k // 9) * 40, 960 + (k // 9) * 55) for k in range(27)]
for x, y in FIRES[::2]: _d.polygon([(x - 60, y - 20), (x - 10, y - 110), (x + 40, y - 20)], fill=(52, 46, 40))   # шатры
GLOW = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(GLOW).ellipse((20, 20, 140, 140), fill=(255, 150, 60, 120)); GLOW = GLOW.filter(ImageFilter.GaussianBlur(22))
def s_camp(lt, D):
    im = BG3.copy(); d = ImageDraw.Draw(im)
    for k, (x, y) in enumerate(STARS): a = 0.5 + 0.5 * math.sin(lt * 2 + k); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(230, 220, 190, int(120 + 120 * a)))
    sx = -60 + lt / D * 1250
    for k, (x, y) in enumerate(FIRES):
        if x > sx + 30 and k % 9 > 1: continue                                   # костры зажигаются один за другим
        im.alpha_composite(GLOW, (x - 80, y - 100)); fl = 6 * math.sin(lt * 14 + k)
        d.polygon([(x - 14, y), (x + fl / 2, y - 44 - fl), (x + 14, y)], fill=(255, 170, 60)); d.polygon([(x - 6, y), (x, y - 22), (x + 6, y)], fill=(255, 235, 170))
    for x in (300, 520, 760): figure(d, x, 1010, POSES["stand"], s=0.42, f=1, robe=(110, 88, 50), robe2=(90, 70, 40), hat=(120, 96, 50), beard=None); d.line(((x + 20, 1010), (x + 30, 780)), fill=(90, 70, 40), width=5)
    figure(d, sx, 1030, walk_pose(lt * 6.5, 24), s=0.5, f=1, **SOLDIER)
    im.alpha_composite(GLOW, (int(sx) + 10, 760)); d.line(((sx + 30, 900), (sx + 40, 820)), fill=(110, 80, 50), width=6); d.ellipse((sx + 28, 790, sx + 52, 826), fill=(255, 180, 70))
    return im.convert("RGB")

# 4. Вода обходит высокое: река и войско в долине
BG4 = paper(); [BG4.alpha_composite(l) for l in (ridge(17, 760, 260, (122, 118, 112), 6, 200),)]
_d = ImageDraw.Draw(BG4); _d.polygon([(0, 1100), (0, 520), (180, 380), (330, 640), (380, 1100)], fill=(70, 66, 62)); _d.polygon([(W, 1100), (W, 560), (900, 430), (760, 700), (720, 1100)], fill=(58, 54, 52))
RIVER = [(520 + 80 * math.sin(y / 140), y) for y in range(560, 1120, 20)]
def s_water(lt, D):
    im = BG4.copy(); d = ImageDraw.Draw(im)
    left = [(x - (30 + (y - 560) * 0.22), y) for x, y in RIVER]; right = [(x + (30 + (y - 560) * 0.22), y) for x, y in RIVER]
    d.polygon(left + right[::-1], fill=(96, 112, 124))
    for k in range(70):                                                          # течение
        p = ((k * 37 + lt * 160) % 560) / 560; idx = min(int(p * (len(RIVER) - 1)), len(RIVER) - 2)
        x, y = RIVER[idx]; w = 30 + (y - 560) * 0.22; off = ((k * 53) % 100 / 100 - 0.5) * w * 1.6
        d.line(((x + off, y), (x + off, y + 16)), fill=(200, 210, 214), width=2)
    for rx, ry in [(520 + 80 * math.sin(820 / 140), 820), (520 + 80 * math.sin(980 / 140) + 20, 980)]:  # камни, вода огибает
        d.ellipse((rx - 34, ry - 18, rx + 34, ry + 18), fill=INK); d.arc((rx - 50, ry - 30, rx + 50, ry + 26), 200, 340, fill=(230, 232, 230), width=3)
    for k in range(7):
        x = W + 60 - (lt * 95 + k * 70) % (W + 260); y = 1080 + 6 * math.sin(x / 90)
        figure(d, x, y, walk_pose(lt * 6 + k, 22), s=0.38, f=-1, **SOLDIER)
    flag(d, W + 60 - (lt * 95 - 30) % (W + 260), 900, lt, h=50, w=70)
    return im.convert("RGB")

# 5. Ветер, лес, огонь, гора — четыре панели
PANELS = [(40, 300), (550, 300), (40, 710), (550, 710)]; PW, PH = 490, 390
def s_elements(lt, D):
    im = paper().copy(); d = ImageDraw.Draw(im); speak = D - 1.6
    act = min(int(max(lt - 1.2, 0) / (speak / 4)), 3)
    for k, (px, py) in enumerate(PANELS):
        pan = Image.new("RGBA", (PW, PH), (214, 202, 178, 255)); pd = ImageDraw.Draw(pan)
        if k == 0:                                                               # ветер: трава гнётся, листья летят
            for g in range(40):
                gx = g * 13; bend = 40 + 25 * math.sin(lt * 3 + g * 0.3)
                pd.line(((gx, PH), (gx + bend * 0.5, PH - 80), (gx + bend, PH - 130)), fill=(70, 80, 60), width=4, joint="curve")
            for l in range(10):
                lx = (l * 70 + lt * 380) % (PW + 60) - 30; ly = 60 + l * 22 + 20 * math.sin(lt * 4 + l); pd.ellipse((lx, ly, lx + 18, ly + 8), fill=(110, 120, 70))
            for s in range(5):
                sy = 70 + s * 50; sx = (s * 120 + lt * 500) % (PW + 200) - 100; pd.line(((sx, sy), (sx + 90, sy)), fill=(150, 140, 120), width=2)
        elif k == 1:                                                             # лес: деревья качаются медленно
            for tr in range(5):
                tx = 50 + tr * 95; sw = 6 * math.sin(lt * 0.8 + tr)
                pd.rectangle((tx - 6, PH - 90, tx + 6, PH), fill=(60, 44, 36))
                for lvl in range(4): w = 70 - lvl * 14; y = PH - 80 - lvl * 60; pd.polygon([(tx - w + sw * lvl, y), (tx + w + sw * lvl, y), (tx + sw * (lvl + 1), y - 90)], fill=(46, 64, 50))
        elif k == 2:                                                             # огонь
            pd.rectangle((0, 0, PW, PH), fill=(60, 30, 24))
            for f in range(9):
                fx = 40 + f * 52; h = 140 + 80 * math.sin(lt * 9 + f * 1.7) + 40 * math.sin(lt * 5.3 + f)
                pd.polygon([(fx - 34, PH), (fx + 10 * math.sin(lt * 7 + f), PH - h), (fx + 34, PH)], fill=(230, 110, 40)); pd.polygon([(fx - 16, PH), (fx, PH - h * 0.55), (fx + 16, PH)], fill=(255, 210, 120))
            for s in range(14):
                sy = PH - ((lt * 160 + s * 47) % PH); sx = (s * 37) % PW + 10 * math.sin(lt * 3 + s); pd.ellipse((sx, sy, sx + 5, sy + 5), fill=(255, 200, 90))
        else:                                                                    # гора: неподвижна, облака плывут
            pd.polygon([(0, PH), (210, 80), (300, 170), (360, 120), (PW, PH)], fill=(54, 50, 50)); pd.polygon([(170, 140), (210, 80), (250, 140)], fill=(230, 226, 216))
            for c in range(3):
                cx = (c * 200 + lt * 40) % (PW + 240) - 120; cy = 200 + c * 45; pd.ellipse((cx, cy, cx + 200, cy + 50), fill=(225, 220, 208))
        if k != act: pan = Image.blend(pan, Image.new("RGBA", (PW, PH), (40, 34, 30, 255)), 0.55)
        im.alpha_composite(pan, (px, py))
        d.rectangle((px - 2, py - 2, px + PW + 1, py + PH + 1), outline=RED if k == act else (90, 80, 70), width=4 if k == act else 2)
    return im.convert("RGB")

def s_outro(lt, D): return s_intro(lt + 20, D, sun_y=600)

SCENES = [
    ("Сунь-цз+ы. «Иск+усство войн+ы». Этой книге две с половиной тысячи лет. Пять принципов, которые работают до сих пор.",
     None, None, s_intro, CREDIT, None),
    ("Первый принцип. Сто раз сразиться и сто раз победить — не лучшее из лучшего. Лучшее — покорить противника, не сражаясь.",
     "Лучшее из лучшего —\nпокорить противника,\nне сражаясь", "ГЛАВА III  ·  I / V", s_armies, CREDIT, None),
    ("Второй. Знай противника и знай себя — и в сотне сражений не будет опасности.",
     "Знай противника и знай себя —\nи в ста сражениях\nне будет опасности", "ГЛАВА III  ·  II / V", s_reflect, CREDIT, None),
    ("Третий. Война — это путь обмана. Если можешь — показывай, что не можешь.",
     "Война — путь обмана.\nМожешь — показывай,\nчто не можешь", "ГЛАВА I  ·  III / V", s_camp, CREDIT, None),
    ("Четвёртый. Войско подобно воде. Вода обходит высокое и стремится к низкому. Так и войско обходит сильное и бьёт по слабому.",
     "Будь как вода:\nобходи сильное\nи бей по слабому", "ГЛАВА VI  ·  IV / V", s_water, CREDIT, None),
    ("Пятый. Будь быстр, как ветер. Нетороплив, как лес. Яростен, как огонь. И неподвижен, как гора.",
     "Быстр, как ветер. Нетороплив,\nкак лес. Яростен, как огонь.\nНеподвижен, как гора", "ГЛАВА VII  ·  V / V", s_elements, CREDIT, None),
    ("Какой принцип вам ближе? Напишите номер в комментариях. И сохраните, чтобы не забыть.",
     "Какой принцип\nвам ближе?", "НАПИШИТЕ НОМЕР В КОММЕНТАРИЯХ", s_outro, CREDIT, None),
]
