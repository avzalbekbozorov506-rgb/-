"""«Кнопка счастья» — притча по мотивам книги Анны Лембке «Дофаминовая нация» (баланс удовольствия и боли:
после быстрой радости мозг уравновешивает её тоской, и мир становится серее, чем был). Псевдо-3D «под Pixar»."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pixar_kit import ball, put, shade, Character, BOY, DAD

W, H = 1080, 1920
HEAD = ("ПРИТЧА", "ПО МОТИВАМ КНИГИ «ДОФАМИНОВАЯ НАЦИЯ»")
TITLE = ("", "", "")
CREDIT = "Анимация · по мотивам книги Анны Лембке «Дофаминовая нация»"
HOOK = ("ОН НАШЁЛ\nКНОПКУ СЧАСТЬЯ", 3.0)
HOOK_Y = 330
SPEAKER = "eugene"
VOSK = dict(speaker=4, rate=1.0, dot=340)
SENTENCES = True
SUB_STYLE, SUB_FONT, QUOTE_SIZE, SUB_CHARS = "karaoke", "Bold", 64, 30
BOT_ALPHA, TOP_ALPHA, VIG, AA, GRAIN = 205, 140, 110, 0.35, 2.5
TEXT_DY = 250
LEAD0, FADE_IN, GAP, TAIL = 0.05, 0.12, 0.3, 0.6
PROG = [[53, 60, 64, 69], [50, 57, 62, 65], [48, 55, 60, 64], [45, 52, 57, 60]]

GY = 1330                                                                     # линия земли
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(int(lerp(a[i], b[i], t)) for i in range(3))
def blink_at(t, ph=0.0): k = (t + ph) % 3.1; return max(0, 1 - abs(k - 0.08) / 0.08) if k < 0.16 else 0.0
def font(w, s): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
F_BIG, F_LBL, F_NUM = font("Black", 84), font("Bold", 30), font("Black", 64)

# ---------- герои ----------
def grand_hair(cv, hc, hr, f):
    col = (236, 236, 240)
    for s in (-1, 1): put(cv, ball(int(hr * 0.7), int(hr * 0.6), col, rim=0.3, spec=0.15), hc[0] + hr * 0.78 * s, hc[1] - hr * 0.25)
    put(cv, ball(int(hr * 1.2), int(hr * 0.42), col, rim=0.3, spec=0.15), hc[0], hc[1] - hr * 0.92)
def grand_beard(cv, hc, hr, off):
    col = (240, 240, 244); put(cv, ball(int(hr * 1.4), int(hr * 0.9), col, rim=0.4, spec=0.12), hc[0], hc[1] + hr * 0.92)
    put(cv, ball(int(hr * 0.95), int(hr * 0.26), shade(col, 0.95), rim=0.3, spec=0.1), hc[0] + off * 1.5, hc[1] + hr * 0.42)
GRAND = Character(dict(DAD.P, skin=(236, 184, 150), shirt=(150, 96, 70), sleeve=(150, 96, 70), pants=(80, 74, 70), shoes=(70, 50, 40),
                       iris=(80, 110, 150), brow=(230, 230, 236), hair_fn=grand_hair, beard_fn=grand_beard, eye=0.25))
KID = BOY

# ---------- миры ----------
def grad(top, bot):
    yy = np.linspace(0, 1, H)[:, None, None]; a = np.array(top) * (1 - yy) + np.array(bot) * yy
    return Image.fromarray(np.repeat(a, W, 1).astype(np.uint8)).convert("RGBA")
def glow(size, col, a):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((size * 0.25, size * 0.25, size * 0.75, size * 0.75), fill=col + (a,))
    return g.filter(ImageFilter.GaussianBlur(size / 7))
def build_attic():
    im = grad((70, 58, 92), (150, 96, 92)); d = ImageDraw.Draw(im)
    d.polygon([(0, 260), (540, 60), (1080, 260), (1080, 330), (540, 140), (0, 330)], fill=(96, 62, 50))       # скат крыши
    for x in range(-40, W, 150): d.line(((x, 300), (x + 60, GY)), fill=(120, 80, 70), width=6)
    d.rounded_rectangle((380, 470, 700, 790), 24, fill=(40, 46, 96)); d.ellipse((560, 520, 640, 600), fill=(250, 240, 200))  # окошко с луной
    d.line(((540, 470), (540, 790)), fill=(110, 76, 64), width=14); d.line(((380, 630), (700, 630)), fill=(110, 76, 64), width=14)
    d.rectangle((0, GY - 20, W, H), fill=(120, 80, 62))
    for y in range(GY, H, 46): d.line(((0, y), (W, y)), fill=(100, 66, 52), width=4)
    put(im, ball(260, 200, (150, 104, 70), rim=0.4, spec=0.08), 150, GY - 70); put(im, ball(200, 150, (170, 120, 80), rim=0.4, spec=0.08), 930, GY - 60)  # сундуки
    return im.filter(ImageFilter.GaussianBlur(2.5))
ATTIC = build_attic()
def build_mountain():
    im = grad((90, 120, 190), (250, 190, 150)); d = ImageDraw.Draw(im)
    d.polygon([(-200, GY + 40), (300, 700), (520, 820), (760, 420), (1300, GY + 40)], fill=(96, 110, 150))       # дальние горы
    im = im.filter(ImageFilter.GaussianBlur(4)); d = ImageDraw.Draw(im)
    d.polygon([(-100, H), (-100, GY + 60), (540, 520), (1180, GY + 60), (1180, H)], fill=(110, 140, 96))          # наша гора
    d.polygon([(540, 520), (470, 640), (560, 610), (620, 660)], fill=(240, 240, 246))                              # снежная шапка
    for k in range(60): r = random.Random(k); x, y = r.uniform(0, W), r.uniform(800, H); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(90, 120, 80))
    return im
MOUNT = build_mountain()
PATH = [(250, 1560), (700, 1380), (380, 1180), (760, 960), (500, 780), (540, 560)]                                 # тропа серпантином
def path_pt(p):
    p = min(max(p, 0), 1) * (len(PATH) - 1); k = min(int(p), len(PATH) - 2); u = p - k
    return (lerp(PATH[k][0], PATH[k + 1][0], u), lerp(PATH[k][1], PATH[k + 1][1], u))
def build_summit():
    im = grad((60, 70, 150), (255, 170, 110)); d = ImageDraw.Draw(im)
    im.alpha_composite(glow(1300, (255, 220, 140), 230), (-110, 380))
    d = ImageDraw.Draw(im); d.polygon([(-100, H), (-100, 1500), (540, GY - 10), (1180, 1500), (1180, H)], fill=(96, 126, 88))
    cl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cl)
    for k in range(14): r = random.Random(k + 7); s = r.randint(240, 420); x, y = r.randint(-60, 1140), r.randint(1480, 1820); dc.ellipse((x - s / 2, y - s / 4, x + s / 2, y + s / 4), fill=(255, 236, 226, 210))
    im.alpha_composite(cl.filter(ImageFilter.GaussianBlur(26)))
    return im
SUMMIT = build_summit()

def desat(im, k):
    """k=0 — цвет как есть, k=1 — серый; отрицательный k — ярче обычного."""
    if k == 0: return im
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGB")
    if k > 0: return Image.blend(im.convert("RGB"), g, min(k, 1)).convert("RGBA")
    from PIL import ImageEnhance
    return ImageEnhance.Color(im.convert("RGB")).enhance(1 - k).convert("RGBA")
def place(im, spr, x, feet, shadow=0.4):
    sh = Image.new("RGBA", (spr.width, 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((spr.width * 0.22, 12, spr.width * 0.78, 48), fill=(10, 10, 20, int(255 * shadow)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (int(x - spr.width / 2), int(feet - 34)))
    im.alpha_composite(spr, (int(x - spr.width / 2), int(feet - spr.height + 12)))

# ---------- кнопка, фейерверк, шкала ----------
def button(s=1.0, glow_a=0.0, press=0.0):
    S = 2; c = Image.new("RGBA", (int(260 * S), int(220 * S)), (0, 0, 0, 0)); cx, cy = 130 * S, 150 * S
    if glow_a: c.alpha_composite(glow(int(260 * S), (255, 90, 90), int(220 * glow_a)), (0, int(-30 * S)))
    put(c, ball(int(200 * S), int(80 * S), (70, 72, 90), rim=0.4, spec=0.3), cx, cy + 20 * S)
    put(c, ball(int(150 * S), int(int(120 - 50 * press) * S), (232, 44, 52), rim=0.6, spec=0.5), cx, cy - (24 - 18 * press) * S)
    return c.resize((int(260 * s), int(220 * s)), Image.LANCZOS)
def fireworks(im, lt, cx=540, cy=700, power=1.0, n=5):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cols = [(255, 214, 90), (255, 110, 150), (110, 220, 255), (170, 255, 140), (220, 150, 255)]
    for b in range(n):
        r_ = random.Random(b); t0 = b * 0.35; p = (lt - t0)
        if p <= 0 or p > 1.6: continue
        bx, by = cx + r_.uniform(-380, 380), cy + r_.uniform(-300, 200); col = cols[b % len(cols)]; R = 260 * power * ease(p / 1.0)
        a = int(255 * max(0, 1 - p / 1.6))
        for k in range(18):
            ang = k / 18 * 6.283; x, y = bx + R * math.cos(ang), by + R * math.sin(ang) + 60 * p * p
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col + (a,))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.5)))
CONF = [(random.Random(k).uniform(0, W), random.Random(k + 1).uniform(-600, 0), random.Random(k + 2).uniform(0.6, 1.4), k) for k in range(90)]
def confetti(im, lt, amount=1.0):
    d = ImageDraw.Draw(im); cols = [(255, 214, 90), (255, 110, 150), (110, 220, 255), (170, 255, 140), (255, 150, 80)]
    for x, y0, sp, k in CONF[: int(len(CONF) * amount)]:
        y = y0 + lt * 520 * sp; xx = x + 40 * math.sin(lt * 3 + k); w = 14 * abs(math.sin(lt * 6 + k))
        if 0 < y < H: d.rectangle((xx - w, y - 8, xx + w, y + 8), fill=cols[k % len(cols)])
def meter(im, v, y=470, label="РАДОСТЬ"):
    """Шкала радости 0–100 вверху кадра."""
    d = ImageDraw.Draw(im); x0, x1 = 170, 910; v = max(0, min(100, v))
    d.rounded_rectangle((x0 - 8, y - 8, x1 + 8, y + 52), 30, fill=(20, 16, 34, 200))
    col = lerpc((230, 70, 70), (120, 220, 110), v / 100)
    if v > 1: d.rounded_rectangle((x0, y, x0 + (x1 - x0) * v / 100, y + 44), 22, fill=col)
    d.text((x0 + 24, y + 22), label, font=F_LBL, fill=(255, 255, 255), anchor="lm"); d.text((x1 - 22, y + 22), str(int(round(v))), font=F_LBL, fill=(255, 255, 255), anchor="rm")
def big_text(im, txt, y, a=1.0, bg=(232, 56, 76), f=None):
    f = f or F_BIG; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = d.multiline_textbbox((W // 2, y), txt, font=f, anchor="ma", align="center", spacing=12)
    d.rounded_rectangle((x0 - 36, y0 - 26, x1 + 36, y1 + 34), 30, fill=bg + (int(230 * a),))
    d.multiline_text((W // 2, y), txt, font=f, fill=(255, 255, 255, int(255 * a)), anchor="ma", align="center", spacing=12); im.alpha_composite(lay)

# ---------- сцены ----------
def kid(mood="neutral", lt=0.0, **kw): return KID.render(mood=mood, blink=blink_at(lt), **kw)
def s_hook(lt, D):
    im = ATTIC.copy(); g = 0.6 + 0.4 * math.sin(lt * 4)
    place(im, kid("surprised" if lt > 0.6 else "neutral", lt, look=(0.4, 0.6), arms=((40, 30), (-30, 20)), scale=1.25), 360, GY + 30)
    put(im, button(1.0, g), 720, GY - 90)
    return desat(im, 0.45).convert("RGB")
def s_press(lt, D):
    p = ease((lt - 0.6) / 0.25); col = -0.35 * ease((lt - 0.7) / 0.6)
    im = ATTIC.copy(); im.alpha_composite(glow(1200, (255, 190, 120), int(160 * p)), (-60, 200))
    place(im, kid("happy" if lt > 0.8 else "neutral", lt, look=(0.4, 0.5), arms=((150 if lt > 0.8 else 60, 20), (-150 if lt > 0.8 else -20, -20)), bounce=10 * abs(math.sin(lt * 5)) * p, scale=1.25), 360, GY + 30)
    put(im, button(1.0, 0.8, press=max(0, 1 - abs(lt - 0.7) * 4)), 720, GY - 90)
    fireworks(im, lt - 0.7); confetti(im, lt - 0.7, p); meter(im, 100 * p)
    return desat(im, col if p > 0 else 0.45).convert("RGB")
def s_again(lt, D):
    presses = [0.5, 1.6, 2.6, 3.4, 4.1, 4.7, 5.2]; n = sum(1 for t in presses if lt > t)
    joy = [100, 70, 45, 25, 12, 6, 3, 1][n]; last = max([t for t in presses if lt > t], default=-9)
    im = ATTIC.copy(); fireworks(im, lt - last, power=joy / 100 + 0.1, n=max(1, int(5 * joy / 100)))
    place(im, kid("neutral" if n < 3 else "sad", lt, look=(0.4, 0.5), arms=((70, 40), (-20, 20)), scale=1.25), 360, GY + 30)
    put(im, button(1.0, 0.5, press=max(0, 1 - abs(lt - last) * 5)), 720, GY - 90)
    meter(im, joy); return desat(im, 0.15 + 0.6 * (1 - joy / 100)).convert("RGB")
def s_grey(lt, D):
    im = ATTIC.copy()
    place(im, kid("sad", lt, look=(-0.3, 0.6), arms=((10, 10), (-8, 12)), squash=0.03 * math.sin(lt * 1.5), scale=1.25), 470, GY + 30)
    put(im, button(1.0, 0.25), 820, GY - 90)
    meter(im, max(0, 18 - lt * 6), label="РАДОСТЬ БЕЗ КНОПКИ")
    out = desat(im, 1.0); d = ImageDraw.Draw(out)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rectangle((0, 0, W, H), fill=(10, 14, 30, int(90 * ease(lt / 2)))); out.alpha_composite(lay)
    return out.convert("RGB")
def s_grand(lt, D):
    im = ATTIC.copy(); walk = ease(lt / 1.6)
    place(im, GRAND.render(mood="talk" if lt > 1.6 else "neutral", blink=blink_at(lt, 1), look=(-0.4, 0.3), f=-1, scale=1.15,
                           arms=((-40 if lt > 2 else 10, 30), (10, 12)), talk=abs(math.sin(lt * 8)) * (lt > 1.6)), lerp(1150, 760, walk), GY + 40)
    place(im, kid("sad" if lt < 2.5 else "neutral", lt, look=(0.5, -0.2), arms=((10, 10), (-8, 12)), scale=1.25), 340, GY + 30)
    if lt < 2.2: put(im, button(0.9, 0.2), 600, GY - 80)
    return desat(im, 0.75 - 0.35 * ease((lt - 2) / 3)).convert("RGB")
def s_climb(lt, D):
    im = MOUNT.copy(); p = 0.85 * ease(lt / D); x, y = path_pt(p); fall = 1.8 < lt < 2.6
    d = ImageDraw.Draw(im); d.line(PATH, fill=(196, 170, 120), width=26, joint="curve")
    place(im, GRAND.render(mood="happy", blink=blink_at(lt, 1), look=(0.3, -0.6), scale=0.55, arms=((150, 20), (10, 12))), 160, 1640)
    step = math.sin(lt * 7)
    place(im, KID.render(mood="sad" if fall else "neutral", blink=blink_at(lt), look=(0.3, -0.5), scale=0.6, legs=(18 * step, -18 * step), squash=0.15 if fall else 0,
                         arms=((40 * step, 30), (-40 * step, 30)), bounce=0 if fall else 6 * abs(step)), x, y + 10)
    meter(im, 8 + 40 * p, label="РАДОСТЬ")
    return desat(im, 0.35 - 0.3 * p).convert("RGB")
def s_top(lt, D):
    im = SUMMIT.copy(); s = ease(lt / 1.2)
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(rays)
    for k in range(14):
        a = k / 14 * 6.283 + lt * 0.1; d.polygon([(540, 960), (540 + 1400 * math.cos(a - 0.05), 960 + 1400 * math.sin(a - 0.05)), (540 + 1400 * math.cos(a + 0.05), 960 + 1400 * math.sin(a + 0.05))], fill=(255, 236, 170, int(60 * s)))
    im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(8)))
    place(im, KID.render(mood="happy", blink=blink_at(lt), look=(0.2, -0.6), scale=1.15, arms=((160 + 10 * math.sin(lt * 3), 20), (-160 - 10 * math.sin(lt * 3), -20)), bounce=8 * abs(math.sin(lt * 3))), 540, GY + 20)
    d = ImageDraw.Draw(im)
    for k in range(3):
        x = (lt * 110 + k * 320) % (W + 200) - 100; y = 640 + k * 70 + 14 * math.sin(lt * 3 + k); w = 24 * math.sin(lt * 9 + k)
        d.line(((x - 28, y - w), (x, y), (x + 28, y - w)), fill=(70, 60, 90), width=6, joint="curve")
    meter(im, min(100, 48 + 60 * s)); return desat(im, -0.25 * s).convert("RGB")
def s_moral(lt, D):
    im = SUMMIT.copy()
    place(im, GRAND.render(mood="happy", blink=blink_at(lt, 1), look=(0.5, 0), scale=1.0, arms=((40, 40), (10, 12))), 300, GY + 30)
    place(im, KID.render(mood="happy", blink=blink_at(lt), look=(-0.5, -0.2), scale=1.0, f=-1, arms=((20, 20), (-8, 12))), 760, GY + 20)
    meter(im, 100 - 2 * math.sin(lt)); return desat(im, -0.2).convert("RGB")
def s_cta(lt, D):
    im = ATTIC.copy(); put(im, button(1.4, 0.6 + 0.4 * math.sin(lt * 4)), 540, 1000)
    return desat(im, 0.3).convert("RGB")

SCENES = [
    ("Мальчик нашёл кнопку, | которая дарит счастье за одну секунду.", "SUB", "", s_hook, CREDIT, None),
    ("Он нажал, и мир взорвался красками. | Радость на максимуме.", "SUB", "", s_press, CREDIT, None),
    ("Он нажал ещё раз. И ещё. | Но с каждым разом радости было меньше.", "SUB", "", s_again, CREDIT, None),
    ("А потом случилось самое страшное. | Без кнопки мир стал серее, | чем был до неё.", "SUB", "", s_grey, CREDIT, None),
    ("Тогда пришёл дедушка и забрал кнопку. | Он сказал: у быстрой радости есть цена. | Мозг уравновешивает её тоской.", "SUB", "", s_grand, CREDIT, None),
    ("Он отвёл внука к горе. | Подъём был трудным. | Он падал и вставал снова.", "SUB", "", s_climb, CREDIT, None),
    ("Но на вершине мир засиял ярче, | чем от любой кнопки. | И этот свет не погас.", "SUB", "", s_top, CREDIT, None),
    ("Лёгкая радость берёт в долг у завтра. | А трудная радость возвращает с процентами.", "SUB", "", s_moral, CREDIT, None),
    ("Какая кнопка есть у тебя? | Напиши в комментариях и подпишись.", "SUB", "НАПИШИ В КОММЕНТАРИЯХ", s_cta, CREDIT, None),
]
