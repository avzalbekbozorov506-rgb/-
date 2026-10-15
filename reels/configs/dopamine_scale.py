"""Анна Лембке, «Дофаминовая нация» — притча о весах удовольствия и боли и гремлинах. Псевдо-3D «под Pixar», хук с первой секунды."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pixar_kit import ball, put, eye, shade, Character, DAD

W, H = 1080, 1920
HEAD = ("АННА ЛЕМБКЕ", "«ДОФАМИНОВАЯ НАЦИЯ»")
TITLE = ("ВЕСЫ", "", "")
CREDIT = "Анимация · по мотивам книги А. Лембке «Дофаминовая нация»"
PROG = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 55]]
BOT_ALPHA, TOP_ALPHA, VIG, AA, GRAIN = 215, 150, 120, 0.35, 2.5
TEXT_DY, QUOTE_SIZE, SUB_CHARS = 262, 66, 26
LEAD0, FADE_IN, GAP, TAIL = 0.08, 0.15, 0.12, 0.55
OF = 255; GY = 1075 + OF
SM = 1.0                                                     # масштаб героя
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(int(lerp(a[i], b[i], t)) for i in range(3))
def blink_at(t, ph=0.0): k = (t + ph) % 3.2; return max(0, 1 - abs(k - 0.08) / 0.08) if k < 0.16 else 0.0
def talk_amp(lt): return abs(math.sin(lt * 9)) * (0.6 + 0.4 * math.sin(lt * 2.3))
def font(w, s): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
F_HOOK, F_LBL, F_CNT, F_SMALL = font("Black", 92), font("Bold", 30), font("Black", 110), font("Bold", 34)

# ---------- герой: парень в худи ----------
def guy_hair(cv, hc, hr, f):
    col = (52, 38, 32); put(cv, ball(int(hr * 2.1), int(hr * 1.2), col, rim=0.5, spec=0.2), hc[0], hc[1] - hr * 0.58)
    for dx, dy, a in [(-0.6, -0.86, 35), (0.0, -1.0, 0), (0.55, -0.9, -35)]: put(cv, ball(int(hr * 0.7), int(hr * 0.6), col, rim=0.5, spec=0.2), hc[0] + hr * dx * f, hc[1] + hr * dy, a * f)
GUY = Character(dict(DAD.P, skin=(238, 188, 150), shirt=(86, 92, 170), sleeve=(86, 92, 170), pants=(48, 52, 70), shoes=(230, 230, 236),
                     iris=(92, 64, 44), brow=(52, 38, 32), hair_fn=guy_hair, beard_fn=None))

# ---------- миры ----------
def grad(top, bot, h=H):
    yy = np.linspace(0, 1, h)[:, None, None]; a = np.array(top) * (1 - yy) + np.array(bot) * yy
    return Image.fromarray(np.repeat(a, W, 1).astype(np.uint8)).convert("RGBA")
def glow(size, col, a):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((size * 0.25, size * 0.25, size * 0.75, size * 0.75), fill=col + (a,))
    return g.filter(ImageFilter.GaussianBlur(size / 7))
def build_room(gray=0.0):
    im = grad(lerpc((36, 40, 78), (40, 40, 46), gray), lerpc((70, 60, 110), (58, 56, 60), gray)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((640, 420 + OF - 120, 980, 820 + OF - 120), 18, fill=(24, 30, 64))                   # окно с луной
    d.ellipse((820, 470 + OF - 120, 900, 550 + OF - 120), fill=(240, 236, 210)); d.line(((810, 420 + OF - 120), (810, 820 + OF - 120)), fill=(90, 80, 120), width=14); d.line(((640, 620 + OF - 120), (980, 620 + OF - 120)), fill=(90, 80, 120), width=14)
    for k in range(12): r = random.Random(k); x, y = r.uniform(660, 960), r.uniform(320 + OF - 120, 700 + OF - 120); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 230))
    d.rectangle((0, GY - 20, W, H), fill=lerpc((86, 64, 70), (60, 58, 60), gray))                          # пол
    put(im, ball(520, 210, lerpc((120, 90, 160), (80, 78, 84), gray), rim=0.4, spec=0.05), 210, GY - 60)   # кресло-мешок
    return im.filter(ImageFilter.GaussianBlur(3))
ROOM, ROOM_GRAY = build_room(), build_room(0.85)
def build_mind():
    im = grad((26, 16, 52), (64, 28, 86)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(4)
    pts = [(r.uniform(0, W), r.uniform(280, 1500)) for _ in range(26)]
    for k, p in enumerate(pts):                                                                             # «нейроны» на фоне
        q = pts[(k * 7 + 3) % len(pts)]; d.line((p, q), fill=(150, 110, 220, 50), width=3); d.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), fill=(200, 160, 255, 110))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3))); return im
MIND = build_mind()
def build_park():
    im = grad((112, 178, 236), (255, 216, 168), GY).crop((0, 0, W, H)); im = grad((112, 178, 236), (255, 216, 168))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(3)
    d.ellipse((-300, 900 + OF - 100, 700, 1500 + OF), fill=(126, 170, 110)); d.ellipse((380, 860 + OF - 100, 1500, 1500 + OF), fill=(110, 156, 104))
    for k in range(12): s = r.randint(160, 300); put(lay, ball(s, int(s * 1.1), (70 + r.randint(0, 30), 136 + r.randint(0, 30), 70), rim=0.5, spec=0.06), r.randint(-80, 1160), r.randint(1000, 1110) + OF - 255)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im)
    a = np.zeros((H - GY, W, 3)); g = np.linspace(0, 1, H - GY)[:, None, None]; a[:] = np.array((118, 172, 84)) * (1 - g * 0.45); im.paste(Image.fromarray(a.astype(np.uint8)), (0, GY))
    for k in range(240): x, y = r.uniform(0, W), r.uniform(GY - 10, GY + 220); d.line(((x, y), (x + r.uniform(-6, 6), y - r.uniform(10, 26))), fill=(78, 130, 60), width=3)
    for k in range(30): x, y = r.uniform(0, W), r.uniform(GY + 30, GY + 250); c = r.choice([(255, 210, 90), (255, 150, 170), (250, 250, 250)]); d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=c)
    return im
PARK = build_park()
DUST = [(random.Random(k).uniform(0, W), random.Random(k + 50).uniform(300, 1300), random.Random(k + 90).uniform(0, 6)) for k in range(24)]
def dust(im, lt, col=(255, 236, 190), a0=110):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, ph in DUST:
        yy = y - (lt * 14 + ph * 40) % 200; xx = x + 18 * math.sin(lt * 0.6 + ph); a = 0.5 + 0.5 * math.sin(lt * 1.5 + ph)
        d.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=col + (int(a0 * a),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2.5)))
def place(im, spr, x, feet, shadow=0.45):
    sh = Image.new("RGBA", (spr.width, 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((spr.width * 0.2, 10, spr.width * 0.8, 50), fill=(10, 10, 20, int(255 * shadow)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (int(x - spr.width / 2), int(feet - 34)))
    im.alpha_composite(spr, (int(x - spr.width / 2), int(feet - spr.height + 12)))
def screen_glow(im, x, y, a=170):
    im.alpha_composite(glow(700, (120, 180, 255), a), (int(x - 350), int(y - 350)))

# ---------- гремлин ----------
GCOL = (120, 196, 96)
def gremlin(s=1.0, t=0.0, mood="happy", blink=0.0, look=(0, 0), wave=0.0):
    S = 2; c = Image.new("RGBA", (int(130 * S), int(150 * S)), (0, 0, 0, 0)); d = ImageDraw.Draw(c); cx, cy = 65 * S, 88 * S
    for sx in (-1, 1):                                                                            # уши-рожки
        d.polygon([(cx + sx * 30 * S, cy - 30 * S), (cx + sx * 62 * S, cy - 70 * S - 6 * S * math.sin(t * 6 + sx)), (cx + sx * 44 * S, cy - 18 * S)], fill=shade(GCOL, 0.85))
    put(c, ball(int(26 * S), int(20 * S), shade(GCOL, 0.8), rim=0.3), cx - 26 * S, cy + 52 * S); put(c, ball(int(26 * S), int(20 * S), shade(GCOL, 0.8), rim=0.3), cx + 26 * S, cy + 52 * S)
    put(c, ball(int(104 * S), int(100 * S), GCOL, rim=0.6, spec=0.2), cx, cy)
    if wave: put(c, ball(int(22 * S), int(22 * S), GCOL, rim=0.4), cx + 58 * S, cy - 20 * S - 14 * S * math.sin(t * 10))
    for sx in (-1, 1): eye(c, cx + sx * 21 * S, cy - 10 * S, 17 * S, 20 * S, look, blink, (230, 70, 60), GCOL, "neutral")
    if mood == "happy": d.chord((cx - 26 * S, cy + 6 * S, cx + 26 * S, cy + 34 * S), 0, 180, fill=(70, 30, 34)); [d.polygon([(cx + k * S - 5 * S, cy + 20 * S), (cx + k * S + 5 * S, cy + 20 * S), (cx + k * S, cy + 30 * S)], fill=(250, 250, 246)) for k in (-12, 12)]
    else: d.arc((cx - 20 * S, cy + 14 * S, cx + 20 * S, cy + 34 * S), 200, 340, fill=(70, 30, 34), width=int(5 * S))
    return c.resize((int(130 * s), int(150 * s)), Image.LANCZOS)

# ---------- весы ----------
def scale_draw(im, ang, cx=540, py=560 + OF - 240, L=330, left=(), right=0, lt=0.0, labels=True, glow_l=0.0, gremlins_leaving=0.0, appear=1.0):
    """ang > 0 — перевес в сторону удовольствия (левая чаша ниже). right — число гремлинов на правой чаше."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    a = math.radians(-ang); ends = [(cx - L * math.cos(a), py - L * math.sin(a)), (cx + L * math.cos(a), py + L * math.sin(a))]
    d.polygon([(cx - 120, py + 640), (cx + 120, py + 640), (cx + 60, py + 600), (cx - 60, py + 600)], fill=(176, 132, 60))
    for off, col in ((10, (150, 110, 46)), (0, (214, 170, 90))): d.line(((cx + off, py), (cx + off, py + 610)), fill=col, width=30 - off)
    for off, col, w in ((6, (150, 110, 46), 26), (0, (232, 190, 104), 20)): d.line(((ends[0][0], ends[0][1] + off), (ends[1][0], ends[1][1] + off)), fill=col, width=w)
    put(lay, ball(70, 70, (236, 196, 110), rim=0.4, spec=0.5), cx, py)
    pans = []
    for k, (ex, ey) in enumerate(ends):
        pyy = ey + 230
        for sx in (-1, 1): d.line(((ex, ey), (ex + sx * 120, pyy)), fill=(200, 160, 90), width=5)
        put(lay, ball(26, 26, (236, 196, 110), rim=0.4, spec=0.5), ex, ey)
        if k == 0 and glow_l > 0: lay.alpha_composite(glow(560, (255, 210, 120), int(200 * glow_l)), (int(ex - 280), int(pyy - 320)))
        d.chord((ex - 150, pyy - 50, ex + 150, pyy + 60), 0, 180, fill=(196, 150, 70)); d.ellipse((ex - 150, pyy - 16, ex + 150, pyy + 20), fill=(236, 200, 120))
        pans.append((ex, pyy))
    (lx, ly), (rx, ry) = pans
    for k, item in enumerate(left):                                                               # что лежит на чаше удовольствия
        x = lx - 60 + k * 60; y = ly - 20
        if item == "phone": d.rounded_rectangle((x - 30, y - 100, x + 30, y), 12, fill=(30, 32, 40)); d.rounded_rectangle((x - 23, y - 92, x + 23, y - 8), 8, fill=(150, 200, 255))
        elif item == "heart": put(lay, heart(70), x, y - 40)
        elif item == "donut": put(lay, ball(80, 70, (236, 140, 170), rim=0.4, spec=0.3), x, y - 34); d.ellipse((x - 12, y - 44, x + 12, y - 24), fill=(196, 150, 70))
    slots = [(-96, 0), (-32, 0), (32, 0), (96, 0), (-64, -84), (0, -84), (64, -84), (-32, -168), (32, -168), (0, -250)]
    n = int(right); fall = right - n
    for k in range(min(n + (1 if fall > 0 else 0), len(slots))):
        sx, sy = slots[k]; drop = 0
        if k == n: drop = -260 * (1 - ease(fall))                                                  # гремлин запрыгивает
        g = gremlin(0.95, lt + k, blink=blink_at(lt, k * 0.4), look=(-0.4, -0.2), wave=(k % 3 == 0 and right >= 3))
        put(lay, g, rx + sx, ry - 56 + sy + drop - 3 * abs(math.sin(lt * 4 + k)))
    if labels:
        for (x, y), txt, col in (((lx, ly + 100), "УДОВОЛЬСТВИЕ", (255, 214, 120)), ((rx, ry + 100), "БОЛЬ", (180, 230, 160))):
            w = d.textlength(txt, font=F_LBL); d.rounded_rectangle((x - w / 2 - 22, y - 26, x + w / 2 + 22, y + 26), 26, fill=(20, 14, 40, 200)); d.text((x, y), txt, font=F_LBL, fill=col, anchor="mm")
    if appear < 1:
        s = 0.6 + 0.4 * appear; lay = lay.resize((int(W * s), int(H * s)), Image.BICUBIC); full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        full.alpha_composite(lay, (int(cx - cx * s), int(py - py * s))); lay = full; lay.putalpha(lay.getchannel("A").point(lambda v: int(v * appear)))
    im.alpha_composite(lay)
def heart(s):
    S = 2; c = Image.new("RGBA", (s * S, s * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c); r = s * S / 4
    d.ellipse((0, 0, 2 * r, 2 * r), fill=(240, 70, 90)); d.ellipse((2 * r, 0, 4 * r, 2 * r), fill=(240, 70, 90)); d.polygon([(0.15 * r, 1.4 * r), (3.85 * r, 1.4 * r), (2 * r, 3.9 * r)], fill=(240, 70, 90))
    return c.resize((s, s), Image.LANCZOS)
def big_text(im, txt, y, a=1.0, col=(255, 255, 255), bg=(232, 56, 76), shake=0.0, f=F_HOOK):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = d.multiline_textbbox((W // 2, y), txt, font=f, anchor="ma", align="center", spacing=14)
    d.rounded_rectangle((x0 - 40, y0 - 30, x1 + 40, y1 + 40), 34, fill=bg + (int(235 * a),))
    d.multiline_text((W // 2, y), txt, font=f, fill=col + (int(255 * a),), anchor="ma", align="center", spacing=14)
    if shake: lay = lay.rotate(shake, center=(W // 2, y + 80))
    im.alpha_composite(lay)
def counter(im, n, label, x=540, y=380, col=(255, 244, 220)):
    d = ImageDraw.Draw(im); d.text((x + 4, y + 6), str(n), font=F_CNT, fill=(20, 10, 30, 160), anchor="mm"); d.text((x, y), str(n), font=F_CNT, fill=col, anchor="mm")
    d.text((x, y + 80), label, font=F_SMALL, fill=col, anchor="mm")
def icons(im, lt, x, y, n=6, speed=1.0):
    """Лайки и уведомления вылетают из телефона."""
    for k in range(n):
        p = (lt * 0.7 * speed + k / n) % 1; ix = x + (k % 2 * 2 - 1) * (40 + p * 160) + 30 * math.sin(k * 2.1); iy = y - p * 520
        s = int(46 + 30 * math.sin(math.pi * p)); spr = heart(s) if k % 3 else ball(s, s, (255, 196, 60), rim=0.3, spec=0.5)
        spr.putalpha(spr.getchannel("A").point(lambda v, p=p: int(v * min(1, (1 - p) * 2.5)))); put(im, spr, ix, iy)

# ---------- сцены ----------
def s_hook(lt, D):
    im = ROOM.copy(); screen_glow(im, 560, GY - 640)
    g = GUY.render(scale=SM, mood="tired", blink=blink_at(lt), look=(0.1, 0.5), f=1, arms=((60, 80), (-10, 20)), item="phone", item_ang=140)
    place(im, g, 520, GY + 20); icons(im, lt, 600, GY - 560, speed=1.6)
    k = ease(lt / 0.25); sh = 3 * math.sin(lt * 40) * max(0, 1 - lt / 0.9)
    big_text(im, "ПОЧЕМУ ТЕБЯ\nБОЛЬШЕ НИЧЕГО\nНЕ РАДУЕТ?", 330, k, shake=sh)
    return im.convert("RGB")
def s_intro(lt, D):
    im = MIND.copy(); scale_draw(im, 1.5 * math.sin(lt * 1.6), lt=lt, appear=ease(lt / 0.8)); dust(im, lt, (210, 180, 255)); return im.convert("RGB")
def s_pleasure(lt, D):
    im = MIND.copy(); u = ease((lt - 0.5) / 1.0); ang = 18 * u + 1.5 * math.sin(lt * 5) * u
    items = ("phone", "heart", "donut")[: 1 + int(min(lt / max(D * 0.33, 0.1), 2))]
    scale_draw(im, ang, left=items, lt=lt, glow_l=u); dust(im, lt, (255, 220, 150), 160); return im.convert("RGB")
def s_gremlins(lt, D):
    im = MIND.copy(); r = min(8, lt / (D - 0.8) * 8); ang = 18 - 34 * ease(r / 8) + 1.2 * math.sin(lt * 4)
    scale_draw(im, ang, left=("phone", "heart", "donut"), right=r, lt=lt, glow_l=max(0, 1 - r / 4)); return im.convert("RGB")
def s_more(lt, D):
    im = ROOM.copy(); screen_glow(im, 470, GY - 640, 200)
    g = GUY.render(scale=0.82, mood="tired", blink=blink_at(lt), look=(0.1, 0.5), arms=((60, 80), (-10, 20)), item="phone", item_ang=140 + 8 * math.sin(lt * 12))
    place(im, g, 300, GY + 20); icons(im, lt, 360, GY - 480, speed=2.4)
    n = 8 + int(min(lt / max(D - 0.8, 0.1), 1) * 2); scale_draw(im, -16 - 2 * n * 0.3, cx=730, L=180, py=560 + OF - 180, right=n, lt=lt, labels=False)
    tm = int(lt * 47) % 60; counter(im, f"{3 + int(lt * 0.25)}:{tm:02d}", "в телефоне сегодня", x=540, y=380, col=(255, 180, 180))
    return im.convert("RGB")
def s_empty(lt, D):
    im = ROOM_GRAY.copy()
    g = GUY.render(scale=SM, mood="sad", blink=blink_at(lt), look=(-0.2, 0.4), arms=((10, 10), (-8, 12)), squash=0.02 * math.sin(lt * 1.5))
    place(im, g, 400, GY + 20)
    for k, (x, y) in enumerate(((770, GY - 40), (900, GY - 20), (690, GY - 300))):              # гремлины вокруг героя
        put(im, gremlin(1.0, lt + k, blink=blink_at(lt, k), look=(-0.6, 0)), x, y - 8 * abs(math.sin(lt * 3 + k)))
    d = ImageDraw.Draw(im)
    for k, w in enumerate(("СКУКА", "ТРЕВОГА", "ПУСТОТА")):
        a = ease((lt - 0.6 - k * 0.9) / 0.4)
        if a > 0: big_text(im, w, 330 + k * 140, a * 0.95, bg=(60, 58, 70), f=F_LBL.font_variant(size=58) if False else font("Black", 60))
    return im.convert("RGB")
def s_detox(lt, D):
    im = MIND.copy(); p = min(lt / max(D - 0.6, 0.1), 1); day = 1 + int(p * 29); r = 10 * (1 - ease(p))
    ang = -30 * (1 - ease(p)) + 1.2 * math.sin(lt * 3)
    scale_draw(im, ang, right=r, lt=lt, labels=True)
    counter(im, day, "из 30 дней", x=540, y=400, col=(190, 240, 170)); return im.convert("RGB")
def s_joy(lt, D):
    im = PARK.copy(); im.alpha_composite(glow(900, (255, 220, 150), 170), (-200, 300 + OF - 400))
    g = GUY.render(scale=SM, mood="happy", blink=blink_at(lt), look=(0.5, -0.4), arms=((150 + 10 * math.sin(lt * 3), 20), (-150 - 10 * math.sin(lt * 3), -20)), squash=0.03 * math.sin(lt * 3), bounce=6 * abs(math.sin(lt * 3)))
    place(im, g, 540, GY + 20); d = ImageDraw.Draw(im)
    for k in range(3):                                                                            # птицы
        x = (lt * 120 + k * 300) % (W + 200) - 100; y = 420 + k * 70 + 14 * math.sin(lt * 3 + k); w = 26 * math.sin(lt * 9 + k)
        d.line(((x - 30, y - w), (x, y), (x + 30, y - w)), fill=(60, 60, 80), width=6, joint="curve")
    dust(im, lt); return im.convert("RGB")
def s_cta(lt, D):
    im = PARK.copy(); im.alpha_composite(glow(900, (255, 220, 150), 170), (-200, 300 + OF - 400))
    g = GUY.render(scale=0.85, mood="talk" if (lt % 3) < 2 else "happy", talk=talk_amp(lt) * 0.0, blink=blink_at(lt), look=(0.3, 0), arms=((150 + 20 * math.sin(lt * 8), 30), (-8, 12)))
    place(im, g, 330, GY + 20); scale_draw(im, 1.2 * math.sin(lt * 1.4), cx=790, L=200, py=560 + OF - 150, lt=lt, labels=False)
    dust(im, lt); return im.convert("RGB")

SCENES = [
    ("Почему тебя больше ничего не радует?", "SUB", "", s_hook, CREDIT, None),
    ("В книге «Дофам+иновая н+ация» есть притча. | В голове у каждого — весы. | Удовольствие и боль.", "SUB", "ПРИТЧА О ВЕСАХ", s_intro, CREDIT, None),
    ("Телефон. Лайк. Сладкое. | Весы склоняются к удовольствию.", "SUB", "ДОФАМИН", s_pleasure, CREDIT, None),
    ("Но мозг не терпит перекоса. | На чашу боли прыгают гремлины. | И весы уходят в сторону боли.", "SUB", "ГРЕМЛИНЫ", s_gremlins, CREDIT, None),
    ("Ты листаешь снова и снова. | Гремлинов всё больше.", "SUB", "ЗАВИСИМОСТЬ", s_more, CREDIT, None),
    ("Без телефона — скука, тревога, пустота. | Это не жизнь стала хуже. | Это гремлины.", "SUB", "", s_empty, CREDIT, None),
    ("Как их прогнать? | Тридцать дней без того, что тебя затянуло. | Гремлины уходят. Весы выпрямляются.", "SUB", "ДОФАМИНОВЫЙ ПОСТ", s_detox, CREDIT, None),
    ("И снова радуют простые вещи: | солнце, прогулка, разговор.", "SUB", "БАЛАНС", s_joy, CREDIT, None),
    ("А что затягивает тебя? | Напиши в комментариях.", "SUB", "ВАШ ОТВЕТ", s_cta, CREDIT, None),
]
