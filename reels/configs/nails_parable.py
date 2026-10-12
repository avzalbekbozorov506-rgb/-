"""Притча о гвоздях — псевдо-3D «под Pixar»: объёмные персонажи с эмоциями, тёплый свет, размытый задний план."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pixar_kit import BOY, DAD, ball, put

W, H = 1080, 1920
HEAD = ("ПРИТЧА", "О СЛОВАХ, СКАЗАННЫХ В ГНЕВЕ")
TITLE = ("ГВОЗДИ", "Притча, которую стоит показать каждому", "СМОТРИ ДО КОНЦА")
CREDIT = "Анимация · народная притча"
PROG = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]
BOT_ALPHA, TOP_ALPHA, VIG, AA, GRAIN = 215, 160, 120, 0.35, 2.5
TEXT_DY, QUOTE_SIZE = 262, 64                      # субтитры ниже и компактнее — больше места для героев
OF = 255                                           # весь мир опущен на OF пикселей
GY, FT, FB = 1075 + OF, 560 + OF, 1045 + OF       # земля, верх и низ забора
SB, SD = 1.38, 1.18                                 # масштаб мальчика и отца
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(int(lerp(a[i], b[i], t)) for i in range(3))
def blink_at(t, ph=0.0): k = (t + ph) % 3.3; return max(0, 1 - abs(k - 0.08) / 0.08) if k < 0.16 else 0.0

# ---------- небо и мир ----------
def sky_img(top, hor):
    yy = np.linspace(0, 1, GY)[:, None, None]; a = np.array(top) * (1 - yy) + np.array(hor) * yy
    im = np.zeros((H, W, 3)); im[:GY] = a; return Image.fromarray(im.astype(np.uint8)).convert("RGBA")
def glow(size, col, a):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((size * 0.25, size * 0.25, size * 0.75, size * 0.75), fill=col + (a,))
    return g.filter(ImageFilter.GaussianBlur(size / 7))
def far_layer(tint=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(2)
    d.rectangle((720, 330 + OF, W, 1000 + OF), fill=lerpc((238, 214, 182), (90, 80, 100), 1 - tint)); d.polygon([(690, 340 + OF), (900, 180 + OF), (1110, 340 + OF)], fill=lerpc((170, 78, 62), (60, 40, 50), 1 - tint))
    d.rounded_rectangle((800, 470 + OF, 960, 660 + OF), 14, fill=(255, 216, 140)); d.line(((880, 470 + OF), (880, 660 + OF)), fill=(160, 120, 90), width=8); d.line(((800, 565 + OF), (960, 565 + OF)), fill=(160, 120, 90), width=8)
    for k in range(9):
        s = r.randint(200, 330); put(lay, ball(s, int(s * 0.9), lerpc((96, 150, 80), (30, 50, 50), 1 - tint), rim=0.5, spec=0.08), r.randint(-60, 700), r.randint(660, 820) + OF)
    return lay.filter(ImageFilter.GaussianBlur(7))                                     # глубина резкости: задний план размыт
PLANKS = [20 + i * 108 for i in range(10)]
def fence_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for y in (680 + OF, 930 + OF): d.rectangle((0, y, W, y + 34), fill=(134, 92, 60))
    for x in PLANKS:
        pl = ball(96, 1200, (204, 156, 104), rim=0.35, spec=0.05, amb=0.7).crop((0, 300, 96, 300 + FB - FT))  # цилиндрический объём доски
        lay.alpha_composite(pl, (x, FT)); d.polygon([(x, FT + 2), (x + 48, FT - 40), (x + 96, FT + 2)], fill=(214, 168, 116))
        r = random.Random(x)
        for g in range(5): gx = x + r.randint(14, 80); d.line(((gx, FT + 20), (gx + r.randint(-6, 6), FB - 10)), fill=(176, 128, 84), width=2)
    return lay
NAILS = []
_r = random.Random(37)
while len(NAILS) < 37:
    x = _r.choice(PLANKS) + _r.randint(22, 74); y = _r.randint(620, 1000) + OF
    if all(abs(x - a) + abs(y - b) > 46 for a, b in NAILS): NAILS.append((x, y))
def nail(d, lay, x, y): put(lay, ball(22, 22, (176, 180, 190), rim=0.3, spec=0.6), x, y)
def hole(d, x, y): d.ellipse((x - 7, y - 6, x + 7, y + 6), fill=(54, 34, 24)); d.arc((x - 8, y - 7, x + 8, y + 8), 20, 160, fill=(232, 190, 140), width=2)
def ground(im, col=(118, 168, 82)):
    d = ImageDraw.Draw(im); a = np.zeros((H - GY, W, 3)); g = np.linspace(0, 1, H - GY)[:, None, None]
    a[:] = np.array(col) * (1 - g * 0.5); im.paste(Image.fromarray(a.astype(np.uint8)), (0, GY))
    r = random.Random(5)
    for k in range(260): x, y = r.uniform(0, W), r.uniform(GY - 12, GY + 220); d.line(((x, y), (x + r.uniform(-6, 6), y - r.uniform(10, 26))), fill=lerpc(col, (60, 110, 50), 0.6), width=3)
SKY_DAY = sky_img((118, 178, 230), (255, 214, 160)); FAR = far_layer(); FENCE = fence_layer()
DUST = [(random.Random(k).uniform(0, W), random.Random(k + 50).uniform(300, 1300), random.Random(k + 90).uniform(0, 6)) for k in range(26)]

def world(lt, sky=None, sun=(230, 470 + OF), tint=1.0, nails=0, holes=0, warm=0.0):
    im = (sky or SKY_DAY).copy()
    im.alpha_composite(glow(900, (255, 220, 150), int(170 * tint)), (int(sun[0] - 450), int(sun[1] - 450)))
    d = ImageDraw.Draw(im); d.ellipse((sun[0] - 70, sun[1] - 70, sun[0] + 70, sun[1] + 70), fill=lerpc((255, 240, 200), (230, 230, 240), 1 - tint))
    im.alpha_composite(FAR if tint > 0.9 else far_layer(tint))
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rays)               # лучи света
    for k in range(5):
        a = math.radians(-20 + k * 14 + 3 * math.sin(lt * 0.4 + k)); rd.polygon([sun, (sun[0] + 1600 * math.cos(a), sun[1] + 1600 * math.sin(a)), (sun[0] + 1600 * math.cos(a + 0.07), sun[1] + 1600 * math.sin(a + 0.07))], fill=(255, 230, 170, int(34 * tint)))
    im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(20)))
    im.alpha_composite(FENCE); d = ImageDraw.Draw(im)
    for k, (x, y) in enumerate(NAILS):
        if k < holes: hole(d, x, y)
        elif k < nails: nail(d, im, x, y)
    ground(im, lerpc((118, 168, 82), (50, 64, 70), 1 - tint))
    if warm: im.alpha_composite(Image.new("RGBA", (W, H), (255, 120, 60, int(60 * warm))))
    if tint < 1: im.alpha_composite(Image.new("RGBA", (W, H), (20, 24, 60, int(150 * (1 - tint)))))
    return im
def dust(im, lt, tint=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, ph in DUST:
        yy = y - (lt * 14 + ph * 40) % 200; xx = x + 18 * math.sin(lt * 0.6 + ph); a = 0.5 + 0.5 * math.sin(lt * 1.5 + ph)
        d.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=(255, 236, 190, int(110 * a * tint)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2.5)))
def place(im, spr, x, feet):
    sh = Image.new("RGBA", (spr.width, 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((spr.width * 0.2, 10, spr.width * 0.8, 50), fill=(20, 30, 10, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (int(x - spr.width / 2), int(feet - 34)))
    im.alpha_composite(spr, (int(x - spr.width / 2), int(feet - spr.height + 12)))
def talk_amp(lt): return abs(math.sin(lt * 9)) * (0.6 + 0.4 * math.sin(lt * 2.3)) if (lt % 2.6) < 2.2 else 0.0
F_COUNT, F_LBL = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 120), ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 34)
def counter(im, n, label, x=860, y=420):
    d = ImageDraw.Draw(im); d.text((x + 4, y + 6), str(n), font=F_COUNT, fill=(60, 30, 20, 160), anchor="mm"); d.text((x, y), str(n), font=F_COUNT, fill=(255, 244, 220), anchor="mm")
    d.text((x, y + 86), label, font=F_LBL, fill=(255, 244, 220), anchor="mm")

# ---------- сцены ----------
def s_title(lt, D):
    im = world(lt); b = BOY.render(scale=SB, mood="happy" if lt > 2.5 else "neutral", blink=blink_at(lt), squash=0.02 * math.sin(lt * 2.4), look=(0.2 * math.sin(lt * 0.7), 0))
    place(im, b, 540, GY + 20); dust(im, lt); return im.convert("RGB")
def s_angry(lt, D):
    im = world(lt); st = abs(math.sin(lt * 6)); ang = 0.65 + 0.35 * math.sin(lt * 3)
    b = BOY.render(scale=SB, mood="angry", anger=ang, bounce=st * 16, squash=0.06 * (1 - st), arms=((40 + 40 * math.sin(lt * 12), 70), (-40 - 40 * math.sin(lt * 12 + 1), 60)), legs=(12 * math.sin(lt * 6), -12 * math.sin(lt * 6)), blink=0)
    place(im, b, 540, GY + 20)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)                  # «пар» из ушей
    for k in range(6):
        p = ((lt * 1.3 + k / 6) % 1); x = 540 + (-150 if k % 2 else 150) + (-1 if k % 2 else 1) * p * 70; y = GY - 360 * SB - p * 200; r = 18 + p * 40
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(170 * (1 - p))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6))); dust(im, lt); return im.convert("RGB")
def s_give(lt, D):
    im = world(lt); u = ease((lt - D * 0.72) / 0.6)
    dad = DAD.render(scale=SD, mood="talk", talk=talk_amp(lt), blink=blink_at(lt, 1.1), arms=((lerp(20, 62, ease(lt / 1.2)), 24), (-6, 10)), item="bag" if u < 0.5 else None, f=1, look=(0.6, 0.1))
    boy = BOY.render(scale=SB, mood="surprised" if u < 0.5 else "neutral", blink=blink_at(lt, 0.5), f=-1, look=(-0.7, -0.3), arms=((lerp(10, 70, u), 30), (-8, 12)), item="bag" if u >= 0.5 else None)
    place(im, dad, 300, GY + 20); place(im, boy, 780, GY + 20); dust(im, lt); return im.convert("RGB")
def s_hammer(lt, D):
    n = min(37, int(lt / max(D - 1.2, 1) * 37)); im = world(lt, nails=n)
    ph = lt * 1.7; a1 = 80 + 80 * abs(math.cos(math.pi * ph)); hit = abs(math.cos(math.pi * ph)) < 0.12
    b = BOY.render(scale=SB, mood="angry", anger=0.6, f=-1, arms=((a1, -10), (-10, 20)), item="hammer", item_ang=a1 + 70, blink=0, look=(-0.8, 0), lean=4)
    place(im, b, 720, GY + 20)
    if hit and BOY.tip:                                                         # искры от удара — там, где молоток
        d = ImageDraw.Draw(im); cx, cy = 720 - b.width / 2 + BOY.tip[0], GY + 32 - b.height + BOY.tip[1]
        for k in range(8): a = k * math.pi / 4; d.line(((cx + 14 * math.cos(a), cy + 14 * math.sin(a)), (cx + 44 * math.cos(a), cy + 44 * math.sin(a))), fill=(255, 230, 120), width=6)
    counter(im, n, "гвоздей за день"); dust(im, lt); return im.convert("RGB")
def s_days(lt, D):
    cyc = lt / D * 3; tod = cyc % 1; night = max(0, math.sin(math.pi * (tod - 0.55) / 0.45)) if tod > 0.55 else 0.0
    sun = (lerp(-80, 1160, min(tod / 0.6, 1)), 620 + OF - 260 * math.sin(math.pi * min(tod / 0.6, 1)))
    im = world(lt, sun=sun, tint=1 - 0.8 * night, nails=37)
    if night > 0.2:
        d = ImageDraw.Draw(im)
        for k in range(30): r = random.Random(k); x, y = r.uniform(0, W), r.uniform(250, 600 + OF); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 230, int(200 * night)))
    b = BOY.render(scale=SB, mood="neutral" if cyc < 1.5 else "happy", blink=blink_at(lt), f=-1, look=(-0.5, -0.2), squash=0.02 * math.sin(lt * 2))
    place(im, b, 760, GY + 20)
    day = 1 + int(cyc * 4); left = max(1, int(37 * (1 - cyc / 3) ** 1.6))
    counter(im, left, f"день {day}"); dust(im, lt, 1 - night); return im.convert("RGB")
def s_pull_talk(lt, D):
    im = world(lt, nails=37)
    dad = DAD.render(scale=SD, mood="talk", talk=talk_amp(lt), blink=blink_at(lt), arms=((30, 40), (-6, 10)), f=1, look=(0.6, 0.1))
    nod = abs(math.sin(lt * 3)) * 6 if lt > D * 0.5 else 0
    boy = BOY.render(scale=SB, mood="happy" if lt > D * 0.5 else "neutral", blink=blink_at(lt, 0.7), f=-1, look=(-0.7, -0.3), bounce=nod)
    place(im, dad, 290, GY + 20); place(im, boy, 780, GY + 20); dust(im, lt); return im.convert("RGB")
def s_pull(lt, D):
    k = min(37, int(lt / max(D - 1.0, 1) * 37)); im = world(lt, nails=37, holes=k)
    ph = (lt * 1.6) % 1; a1 = 80 - 40 * ease((ph - 0.5) * 2) if ph > 0.5 else 80
    b = BOY.render(scale=SB, mood="happy", f=-1, arms=((a1, 0), (-10, 20)), item="pliers", item_ang=a1 + 10, lean=-6 * (a1 < 70), blink=blink_at(lt), look=(-0.8, 0))
    place(im, b, 720, GY + 20)
    if ph > 0.5 and BOY.tip:                                                    # вытащенный гвоздь отлетает от клещей
        d = ImageDraw.Draw(im); p = (ph - 0.5) * 2; x0, y0 = 720 - b.width / 2 + BOY.tip[0], GY + 32 - b.height + BOY.tip[1]; x, y = x0 + p * 160, y0 - 120 * math.sin(math.pi * p); d.line(((x, y), (x + 30, y + 8)), fill=(190, 194, 204), width=7)
    counter(im, 37 - k, "осталось"); dust(im, lt); return im.convert("RGB")
def s_holes(lt, D, warm=0.35):
    im = world(lt, sun=(200, 640 + OF), nails=37, holes=37, warm=warm)
    dad = DAD.render(scale=SD, mood="talk", talk=talk_amp(lt), blink=blink_at(lt), arms=((52, 18), (-6, 10)), f=1, look=(0.5, 0.3))
    boy = BOY.render(scale=SB, mood="sad" if lt < D * 0.6 else "neutral", blink=blink_at(lt, 0.4), f=-1, look=(-0.3, -0.6) if lt > D * 0.4 else (-0.9, 0.2))
    place(im, dad, 350, GY + 20); place(im, boy, 690, GY + 20); dust(im, lt); return im.convert("RGB")
def s_outro(lt, D):
    im = world(lt, sun=(200, 700 + OF), nails=37, holes=37, warm=0.6)
    dad = DAD.render(scale=SD, mood="happy", blink=blink_at(lt), arms=((52, 18), (-6, 10)), f=1, look=(0.5, 0.3))
    boy = BOY.render(scale=SB, mood="happy", blink=blink_at(lt, 0.4), f=-1, look=(-0.3, -0.6))
    place(im, dad, 350, GY + 20); place(im, boy, 690, GY + 20); dust(im, lt); return im.convert("RGB")

SCENES = [
    ("Притча о гвоздях. Короткая история, которую стоит показать каждому.", None, None, s_title, CREDIT, None),
    ("Жил-был мальчик с очень вспыльчивым характером. Чуть что — он кричал и злился.",
     "Жил-был мальчик\nс очень вспыльчивым\nхарактером", "ПРИТЧА", s_angry, CREDIT, None),
    ("Вот тебе мешок гвоздей, сын. Каждый раз, когда разозлишься, — забей один гвоздь в забор.",
     "Каждый раз, когда разозлишься, —\nзабей один гвоздь\nв забор", "ОТЕЦ", s_give, CREDIT, None, "eugene"),
    ("В первый же день мальчик забил тридцать семь гвоздей.",
     "В первый день —\nтридцать семь гвоздей", "ДЕНЬ ПЕРВЫЙ", s_hammer, CREDIT, None),
    ("Но с каждым днём гвоздей становилось всё меньше. Оказалось, сдержаться легче, чем забивать гвозди.",
     "Оказалось, сдержаться\nлегче, чем забивать\nгвозди", "НЕДЕЛИ СПУСТЯ", s_days, CREDIT, None),
    ("Молодец. А теперь за каждый день без гнева вытаскивай по одному гвоздю.",
     "За каждый день без гнева —\nвытаскивай\nпо одному гвоздю", "ОТЕЦ", s_pull_talk, CREDIT, None, "eugene"),
    ("Прошло время, и в заборе не осталось ни одного гвоздя.",
     "И в заборе не осталось\nни одного гвоздя", "МЕСЯЦЫ СПУСТЯ", s_pull, CREDIT, None),
    ("Ты молодец, сын. Но посмотри на эти дыры. Забор уже никогда не станет прежним. Слова, сказанные в гневе, оставляют такие же следы.",
     "Слова, сказанные в гневе,\nоставляют такие же\nследы", "ОТЕЦ", s_holes, CREDIT, None, "eugene"),
    ("Прежде чем сказать что-то в гневе, — вспомни о заборе. Отправьте эту историю тому, кому она нужна.",
     "Прежде чем сказать в гневе —\nвспомни о заборе", "ОТПРАВЬТЕ ТОМУ, КОМУ ЭТО НУЖНО", s_outro, CREDIT, None),
]
