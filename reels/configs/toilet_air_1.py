"""«После туалета нажал освежитель?» — юмористический научпоп «Простым языком», изометрия + HUD, графика кодом (configs/iso_kit.py).
Факты и источники: scripts/toilet_air_1.md (Moore 1987, ATSDR, Steinemann 2017, US EPA). Фото не используются."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter1d
import bh_cine as B, iso_kit as I_
from bh_cine import W, H, ease, seg, lerp, fnt
HEAD = ("ПРОСТЫМ ЯЗЫКОМ", "ЧИСТИТ ЛИ ОСВЕЖИТЕЛЬ ВОЗДУХ")
TITLE = ("", "", "")
HOOK = ("ПОСЛЕ ТУАЛЕТА\nНАЖИМАЕШЬ\nОСВЕЖИТЕЛЬ?", 2.4)
HOOK_Y = 930
MUSIC = ("music/ogv_aria.mp3", 0)
SUB_STYLE = "words"; WORDS_TAG = False; WORDS_Y = 1300; WORDS_SIZE = 92
AA = 0.35; GRAIN = 4.5
TAIL = 0.3; XF = 0.3; LEAD_N = 0.2; GAP = 0.28
RED = (255, 80, 60); GOLD = (255, 214, 60); ICE = (170, 215, 255); WHT = (240, 244, 255); DIM = (130, 150, 190); BLUE = (60, 150, 255); ORNG = (255, 140, 50); NEON = (80, 235, 205); GRN = (110, 235, 140)
BG = (6, 9, 18)

# эмоции голоса: вопрос — вверх и быстрее, шутка — медленнее и ниже, вердикт — твёрдо и громче
STYLE = {
    "нажимаешь освежитель": dict(rate=0.98, pitch=1.07, gain=1.1, after_ms=420),
    "обманул только свой нос": dict(rate=0.8, pitch=0.95, gain=1.05),
    "как туристы на экскурсии": dict(rate=0.92, pitch=1.05),
    "вещества с серой": dict(rate=0.86, pitch=0.96),
    "А нос — детектор": dict(rate=0.92, pitch=1.04),
    "Что же делает освежитель": dict(rate=0.95, pitch=1.08, gain=1.1, after_ms=700),
    "Он — парфюмер": dict(rate=0.78, pitch=0.94, gain=1.05, after_ms=520),
    "цветочный букет": dict(rate=0.9, pitch=1.04),
    "Так чистит ли освежитель": dict(rate=0.96, pitch=1.06, gain=1.08, after_ms=700),
    "Нет.": dict(rate=0.72, pitch=0.9, gain=1.2, after_ms=520),
    "Он перебивает": dict(rate=0.82, pitch=0.93, gain=1.1, after_ms=420),
    "окно разбавляет": dict(rate=0.88, pitch=0.97, gain=1.1),
    "лечит комнату": dict(rate=0.95, pitch=1.04),
}
def ph(i, k):
    import __main__ as E
    return E.PHRASES[i][k]
def T(i, k, f=0.0): st, en, _ = ph(i, k); return st + f * (en - st)
def P(i, lt, k, f0=0.0, f1=1.0): return seg(lt, T(i, k, f0), T(i, k, f1))
def layer(): lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)
def fin(base, lay=None, lt=0.0, shake=1.0, k=0.6, streak=0.06, ca=2):
    base = base.convert("RGBA")
    if lay is not None: base.alpha_composite(lay)
    z = 1.0 + 0.012 * min(lt, 9.0)                                    # медленный наезд камеры
    if z > 1.0005:
        w_, h_ = W / z, H / z; base = base.transform((W, H), Image.AFFINE, (1 / z, 0, (W - w_) / 2, 0, 1 / z, (H - h_) / 2 - 20 * (z - 1) * 10), Image.BICUBIC)
    sm = base.resize((W // 2, H // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)   # глубина резкости: края мягче
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); m = np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - 720) / (H * 0.36)) ** 2 - 0.55, 0, 1)
    ma = Image.fromarray((np.clip(m * 1.4, 0, 1) * 255).astype(np.uint8), "L"); base = Image.composite(sm, base, ma)
    return B.finish_c(base, k=k + 0.15, streak=streak, shake=shake, lt=lt, ca=ca)
def tx(d, xy, s, size, col=WHT, a=1.0, w="Bold", anchor="mm"):
    if a < 0.03: return
    d.text(xy, s, font=fnt(size, w), fill=col + (int(255 * min(a, 1)),), anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0, int(140 * min(a, 1))))
def pill(d, xy, s, size, col, a=1.0, w="Bold"):
    size = max(size, 34)
    if a < 0.03: return
    f = fnt(size, w); tw = d.textlength(s, font=f); x, y = xy; x = min(max(x, tw / 2 + 50), W - tw / 2 - 50)
    d.rounded_rectangle((x - tw / 2 - 18, y - size * 0.75, x + tw / 2 + 18, y + size * 0.75), int(size * 0.75), fill=(6, 9, 18, int(200 * a)), outline=col + (int(200 * a),), width=2)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor="mm")
def dark(): return Image.new("RGBA", (W, H), BG + (255,))
def grid_bg(lt, a=1.0):
    im = dark(); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(20, 30, 52, int(255 * a)), width=1)
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(20, 30, 52, int(255 * a)), width=1)
    return im
def chap(d, n, title, u=1.0):
    tx(d, (170, 360), f"{n} / 05", 34, GOLD, a=u, w="Bold"); tx(d, (560, 360), title, 38, WHT, a=u, w="Bold")
    d.line([(90, 395), (990, 395)], fill=NEON + (int(120 * u),), width=2)
def corners(d, a=0.5):
    for (x, y, sx, sy) in ((60, 380, 1, 1), (1020, 380, -1, 1), (60, 1120, 1, -1), (1020, 1120, -1, -1)):
        d.line([(x, y), (x + 44 * sx, y)], fill=NEON + (int(200 * a),), width=3); d.line([(x, y), (x, y + 44 * sy)], fill=NEON + (int(200 * a),), width=3)
def iso(S=78, cy=700, lt=0.0): return I_.Iso(S=S, cx=540 + 26 * math.sin(lt * 0.22), cy=cy + 14 * math.cos(lt * 0.19), yaw=0.16 * math.sin(lt * 0.21 + 0.6))
def photons(im, I, lt, n=14, a=1.0, speed=1.6, col=(255, 255, 255), size=9, z=I_.RZ):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rng = np.random.default_rng(5)
    for k in range(n):
        ang = rng.uniform(0, 2 * math.pi); ph_ = (lt * speed * 0.3 + rng.uniform(0, 1)) % 1; r = ph_ * 5.5
        x, y = I.p(I_.RX + r * math.cos(ang), I_.RY + r * math.sin(ang), z); al = a * (1 - ph_) ** 0.8
        d.ellipse((x - size, y - size, x + size, y + size), fill=col + (int(255 * al),))
    g = lay.filter(ImageFilter.GaussianBlur(8)); im.alpha_composite(g); im.alpha_composite(lay)
YEL = (235, 215, 70); PINK = (255, 130, 200); LIL = (190, 150, 255)
def bath(lt, I, wall_a=140, dim=1.0, fan=0.0):
    """Изометрический санузел: плитка, две стены, окно, унитаз, раковина, полка с флаконом освежителя."""
    im = Image.new("RGBA", (W, H), (6, 9, 18, 255)); d = ImageDraw.Draw(im, "RGBA"); P_ = I.p; N = 6
    sc = lambda c: tuple(int(v * dim) for v in c)
    I_.poly(d, [P_(0, 0), P_(N, 0), P_(N, N), P_(0, N)], sc((18, 30, 52, 255)))
    for k in range(N * 2 + 1):
        d.line([P_(k / 2, 0), P_(k / 2, N)], fill=(40, 80, 115, 90), width=1); d.line([P_(0, k / 2), P_(N, k / 2)], fill=(40, 80, 115, 90), width=1)
    zt = 3.0
    I_.poly(d, [P_(0, 0, 0), P_(N, 0, 0), P_(N, 0, zt), P_(0, 0, zt)], (14, 24, 44, wall_a), (60, 120, 160, 200))
    I_.poly(d, [P_(0, 0, 0), P_(0, N, 0), P_(0, N, zt), P_(0, 0, zt)], (12, 20, 38, wall_a), (60, 120, 160, 200))
    g = 0.6 + 0.1 * math.sin(lt * 0.7)
    I_.poly(d, [P_(0, 2.0, 1.2), P_(0, 4.0, 1.2), P_(0, 4.0, 2.4), P_(0, 2.0, 2.4)], (int(40 * g), int(70 * g), int(120 * g), 235), (120, 180, 230, 255))
    if fan > 0:
        c_ = P_(5.0, 0.0, 2.3); I_.poly(d, [P_(4.6, 0, 1.9), P_(5.4, 0, 1.9), P_(5.4, 0, 2.7), P_(4.6, 0, 2.7)], (30, 38, 56, 255), (140, 180, 220, 255))
        for k in range(4):
            a_ = lt * 6 + k * math.pi / 2; d.line([c_, (c_[0] + 38 * math.cos(a_), c_[1] + 38 * math.sin(a_))], fill=(190, 230, 255, 255), width=8)
    I_.box(d, I, 1.2, 0.1, 0, 1.0, 0.35, 0.95, (225, 232, 245, 255), (170, 180, 200, 255), (140, 150, 175, 255), (220, 230, 250, 255))          # бачок
    I_.box(d, I, 1.2, 0.45, 0, 1.0, 0.8, 0.5, (235, 240, 250, 255), (180, 190, 210, 255), (150, 160, 185, 255), (225, 232, 250, 255))           # унитаз
    I_.box(d, I, 4.2, 0.1, 0, 1.3, 0.6, 0.85, (200, 210, 230, 255), (150, 160, 185, 255), (120, 130, 160, 255), (200, 215, 240, 255))           # тумба
    I_.box(d, I, 3.0, 0.05, 1.3, 0.9, 0.3, 0.07, (150, 120, 90, 255), (110, 85, 65, 255), (90, 70, 55, 255))                                 # полка
    I_.box(d, I, 3.25, 0.1, 1.37, 0.28, 0.25, 0.6, (255, 150, 200, 255), (225, 110, 170, 255), (190, 90, 145, 255), (255, 200, 230, 255))        # флакон
    hz = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hz)
    for k in range(4):
        cx_ = 540 + 280 * math.sin(lt * 0.17 + k * 1.7); cy_ = 760 + 140 * math.cos(lt * 0.13 + k * 2.3); hd.ellipse((cx_ - 300, cy_ - 150, cx_ + 300, cy_ + 150), fill=(70, 110, 190, 16))
    im.alpha_composite(hz.filter(ImageFilter.GaussianBlur(60)))
    return im
SRC = (1.7, 0.85, 0.55)           # источник запаха (унитаз)
CAN = (3.4, 0.2, 1.95)            # флакон
def mol(im, I, lt, n=60, a=1.0, spread=1.0, col=YEL, size=8, t0=0.0, src=SRC, drift=(0.55, 0.7), seed=3, keep=1.0, tour=False):
    """Молекулы запаха: стартуют у унитаза и расползаются по комнате (дрейф + дрожание)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rng = np.random.default_rng(seed)
    for k in range(n):
        ph_ = min(1.0, max(0.0, (lt - t0) * 0.16 + rng.uniform(-0.15, 0.1)));
        if rng.random() > keep: continue
        ang = rng.uniform(0, 2 * math.pi); r = ph_ * spread * rng.uniform(0.6, 3.6)
        x = src[0] + r * (drift[0] + 0.7 * math.cos(ang)) + 0.06 * math.sin(lt * 3 + k); y = src[1] + r * (drift[1] + 0.6 * math.sin(ang)) + 0.06 * math.cos(lt * 2.7 + k)
        z = src[2] + ph_ * rng.uniform(0.0, 1.6) + 0.05 * math.sin(lt * 2 + k)
        x = min(max(x, 0.25), 5.8); y = min(max(y, 0.25), 5.8); p = I.p(x, y, z)
        if ph_ > 0.01:
            d.ellipse((p[0] - size, p[1] - size, p[0] + size, p[1] + size), fill=col + (int(235 * a),))
            if tour and k % 4 == 0: d.polygon([(p[0] - size, p[1] - size + 1), (p[0] + size, p[1] - size + 1), (p[0], p[1] - size * 2.4)], fill=(255, 90, 80, int(235 * a)))     # шляпка туриста
            if tour and k == 0: d.line([(p[0] + size, p[1]), (p[0] + size, p[1] - 70)], fill=(240, 240, 255, 255), width=3); d.polygon([(p[0] + size, p[1] - 70), (p[0] + size + 46, p[1] - 56), (p[0] + size, p[1] - 42)], fill=(80, 200, 255, 255))   # гид с флажком
    g = lay.filter(ImageFilter.GaussianBlur(7)); im.alpha_composite(g); im.alpha_composite(lay)
def spray(im, I, lt, t0, u=1.0, col=PINK):
    """Облако аромата из флакона: расходящиеся полупрозрачные овалы."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); c = I.p(*CAN)
    for k in range(10):
        ph_ = min(1.0, max(0.0, (lt - t0) * 0.8 - k * 0.07));
        if ph_ <= 0: continue
        r = 30 + 330 * ph_; cx_ = c[0] + 120 * ph_ + 18 * k - 60; cy_ = c[1] + 60 * ph_ + 20 * math.sin(k)
        d.ellipse((cx_ - r, cy_ - r * 0.6, cx_ + r, cy_ + r * 0.6), fill=col + (int(60 * u * (1 - 0.6 * ph_)),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
def can_icon(d, c, s, col=PINK, a=1.0):
    d.rounded_rectangle((c[0] - s * 0.5, c[1] - s * 1.2, c[0] + s * 0.5, c[1] + s * 1.0), int(s * 0.15), fill=col + (int(255 * a),), outline=(255, 235, 245, int(255 * a)), width=3)
    d.rectangle((c[0] - s * 0.22, c[1] - s * 1.55, c[0] + s * 0.22, c[1] - s * 1.2), fill=(240, 240, 250, int(255 * a)))

GRNS = (120, 235, 80)
def stink(im, I, lt, a=1.0, n=6, src=SRC, h=220):
    """Зелёные волнистые «линии вони» над унитазом — как в мультиках."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); p0 = I.p(*src)
    for k in range(n):
        x0 = p0[0] - 60 + k * 26; pts = []
        for j in range(26):
            u = j / 25; y = p0[1] - 20 - u * h * (1 + 0.15 * k % 3); x = x0 + 20 * math.sin(u * 7 + lt * 3 + k * 1.3) * (0.4 + u)
            pts.append((x, y))
        d.line(pts, fill=GRNS + (int(235 * a),), width=9, joint="curve")
    g = lay.filter(ImageFilter.GaussianBlur(9)); im.alpha_composite(g); im.alpha_composite(lay)
def face_nose(d, c, s, mood="gross", a=1.0, lt=0.0):
    """Мультяшное лицо: «зажатый нос» (мерзко) или «довольный»."""
    A = int(255 * a); d.ellipse((c[0] - s, c[1] - s, c[0] + s, c[1] + s), fill=(255, 214, 60, A), outline=(40, 30, 10, A), width=6)
    ex = s * 0.38; ey = c[1] - s * 0.25
    if mood == "gross":
        for sx in (-1, 1):
            xx = c[0] + sx * ex; d.line([(xx - sx * s * 0.18, ey - s * 0.12), (xx + sx * s * 0.12, ey), (xx - sx * s * 0.18, ey + s * 0.12)], fill=(40, 30, 10, A), width=7)
        d.arc((c[0] - s * 0.4, c[1] + s * 0.35, c[0] + s * 0.4, c[1] + s * 0.75), 200, 340, fill=(40, 30, 10, A), width=7)
    else:
        for sx in (-1, 1): xx = c[0] + sx * ex; d.ellipse((xx - s * 0.1, ey - s * 0.1, xx + s * 0.1, ey + s * 0.1), fill=(40, 30, 10, A))
        d.arc((c[0] - s * 0.45, c[1] + s * 0.05, c[0] + s * 0.45, c[1] + s * 0.65), 20, 160, fill=(40, 30, 10, A), width=7)
    d.polygon([(c[0] - s * 0.14, c[1] - s * 0.1), (c[0] + s * 0.14, c[1] - s * 0.1), (c[0] + s * 0.24, c[1] + s * 0.28), (c[0] - s * 0.24, c[1] + s * 0.28)], fill=(255, 150, 140, A), outline=(40, 30, 10, A), width=5)
    if mood == "gross": d.rounded_rectangle((c[0] - s * 0.3, c[1] + s * 0.2, c[0] + s * 0.3, c[1] + s * 0.38), 10, fill=(255, 190, 140, A), outline=(40, 30, 10, A), width=4)   # пальцы-прищепка
def stamp(im, c, text, size, col, ang=-8, a=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = fnt(size, "Black"); tw = d.textlength(text, font=f)
    d.rounded_rectangle((c[0] - tw / 2 - 28, c[1] - size * 0.8, c[0] + tw / 2 + 28, c[1] + size * 0.8), 18, fill=(10, 8, 12, int(200 * a)), outline=col + (int(255 * a),), width=8)
    d.text(c, text, font=f, fill=col + (int(255 * a),), anchor="mm"); lay = lay.rotate(ang, center=c, resample=Image.BICUBIC); im.alpha_composite(lay)
def sparkles(d, lt, cx, cy, n=8, r=260, a=1.0, col=(255, 255, 255)):
    rng = np.random.default_rng(9)
    for k in range(n):
        ang = rng.uniform(0, 6.28); rr = rng.uniform(0.4, 1.0) * r; x = cx + rr * math.cos(ang); y = cy + rr * math.sin(ang) * 0.6; sz = 14 + 12 * abs(math.sin(lt * 3 + k))
        d.polygon([(x, y - sz), (x + sz * 0.3, y - sz * 0.3), (x + sz, y), (x + sz * 0.3, y + sz * 0.3), (x, y + sz), (x - sz * 0.3, y + sz * 0.3), (x - sz, y), (x - sz * 0.3, y - sz * 0.3)], fill=col + (int(240 * a),))
# ---------- 0. хук
def s0(lt, D):
    I = iso(102, 690, lt); im = bath(lt, I, wall_a=100); lay, d = layer()
    mol(im, I, lt + 4.0, n=70, a=0.9, spread=1.0); stink(im, I, lt, a=0.9); spray(im, I, lt, 0.5, u=1.8)
    q = P(0, lt, 1, 0.1, 0.8); pc = I.p(*CAN); can_icon(d, (900, 560), 90, a=min(1, lt * 2))
    B.reticle(d, (pc[0], pc[1] + 40), 120, PINK + (int(230 * min(1, lt)),), u=min(1, lt * 1.5), ticks=36, w=3)
    face_nose(d, (170, 560), 105, 'gross', a=min(1, lt * 2.5), lt=lt)
    if q > 0: stamp(im, (540, 400), 'НОС ОБМАНУТ!', 64, (255, 70, 60), ang=-6, a=q)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 1. «Простым языком»
def s1(lt, D):
    im = dark(); lay, d = layer(); u = P(1, lt, 0, 0.0, 0.7)
    B.tracked(d, (540, 700), "ПРОСТЫМ ЯЗЫКОМ", 64, WHT, u=u, w="Bold", sp=0.18); d.line([(540 - 300 * u, 760), (540 + 300 * u, 760)], fill=GOLD + (230,), width=3)
    return fin(im, lay, lt, shake=0, k=0.7)
# ---------- 2. запах: молекулы-туристы
def s2(lt, D):
    I = iso(104, 690, lt); im = bath(lt, I, wall_a=110); lay, d = layer(); chap(d, "01", "ОТКУДА ЗАПАХ", P(2, lt, 0, 0.0, 0.3))
    stink(im, I, lt, a=0.8); mol(im, I, lt * 0.7, n=60, a=1.0, spread=1.8, size=10, tour=True); a = P(2, lt, 1, 0.2, 0.9)
    pc = I.p(*SRC)
    if a > 0: B.leader(d, (pc[0] + 20, pc[1] - 30), (pc[0] + 120, pc[1] - 220), (900, pc[1] - 220), YEL + (230,), u=a); tx(d, (770, pc[1] - 260), "МОЛЕКУЛА ЗАПАХА", 32, YEL, a=a)
    t = P(2, lt, 2, 0.2, 0.9)
    if t > 0: tx(d, (540, 1040), "ЭКСКУРСИЯ ПО КОМНАТЕ", 52, YEL, a=t)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 3. вещества с серой
def s3(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "01", "ОТКУДА ЗАПАХ", 1.0); a = P(3, lt, 0, 0.1, 0.6); b = P(3, lt, 1, 0.2, 0.8)
    c = (540, 700)
    for dx in (-110, 110): d.line([c, (c[0] + dx, c[1] + 70)], fill=(230, 235, 255, int(255 * a)), width=8); d.ellipse((c[0] + dx - 34, c[1] + 70 - 34, c[0] + dx + 34, c[1] + 70 + 34), fill=(230, 236, 255, int(255 * a)))
    d.ellipse((c[0] - 70, c[1] - 70, c[0] + 70, c[1] + 70), fill=YEL + (int(255 * a),)); tx(d, (c[0], c[1]), "S", 70, (30, 28, 10), a=a, w="Black")
    tx(d, (540, 520), "ВЕЩЕСТВА С СЕРОЙ", 52, YEL, a=a)
    if b > 0: d.rounded_rectangle((250, 930, 830, 1030), 20, fill=(8, 14, 28, int(230 * b)), outline=GOLD + (int(230 * b),), width=3); tx(d, (540, 965), "MOORE И ДР. · 1987", 40, GOLD, a=b); tx(d, (540, 1020), "GASTROENTEROLOGY · СЕРОСОДЕРЖАЩИЕ ГАЗЫ", 24, DIM, a=b, w="Medium")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 4. нос-детектор
def s4(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "02", "НОС", P(4, lt, 0, 0.0, 0.3)); a = P(4, lt, 0, 0.1, 0.8); b = P(4, lt, 1, 0.2, 0.8); c = P(4, lt, 2, 0.2, 0.9)
    cx_, cy_ = 300, 700; face_nose(d, (cx_, cy_), 150, 'gross', a=a, lt=lt)
    rng = np.random.default_rng(2)
    for k in range(int(40 * b)):
        px = cx_ + rng.uniform(-30, 30); py = cy_ - 5 + rng.uniform(-30, 20); d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=GRN + (230,))
    if b > 0: tx(d, (700, 560), "СОТНИ ВИДОВ", 44, GRN, a=b); tx(d, (700, 615), "РЕЦЕПТОРОВ", 36, GRN, a=b)
    if c > 0:
        d.rounded_rectangle((120, 900, 960, 1070), 20, fill=(8, 14, 28, int(235 * c)), outline=YEL + (int(240 * c),), width=3)
        tx(d, (540, 945), "СЕРОВОДОРОД (ЗАПАХ ТУХЛЫХ ЯИЦ) · У САМЫХ ЧУТКИХ", 26, DIM, a=c, w="Medium"); tx(d, (540, 1010), "5 молекул на 10 000 000 000", 46, YEL, a=c); tx(d, (540, 1060), "ПОРОГ У ЛЮДЕЙ РАЗНЫЙ (ATSDR)", 24, DIM, a=c, w="Medium")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 5. РЕХУК: освежитель — парфюмер
def s5(lt, D):
    I = iso(104, 690, lt); im = bath(lt, I, wall_a=110); lay, d = layer(); chap(d, "03", "ОСВЕЖИТЕЛЬ", P(5, lt, 0, 0.0, 0.3))
    mol(im, I, lt * 0.7 + 3, n=60, a=1.0, spread=1.6, size=10); spray(im, I, lt, T(5, 1, 0.3), u=2.2); spray(im, I, lt, T(5, 1, 0.5), u=2.0, col=LIL)
    b = P(5, lt, 1, 0.3, 0.9); c = P(5, lt, 2, 0.2, 0.9)
    if b > 0: tx(d, (300, 1010), "ПАРФЮМЕР", 56, PINK, a=b)
    if c > 0: pill(d, (700, 1010), "ЗАПАХ НА МЕСТЕ", 34, YEL, a=c); pill(d, (700, 1080), "ПОВЕРХ — БУКЕТ", 34, PINK, a=c)
    can_icon(d, (880, 520), 100, a=b); sparkles(d, lt, 560, 700, 10, 300, a=b, col=(255, 200, 240))
    if b > 0: face_nose(d, (180, 560), 95, 'happy', a=b, lt=lt); stamp(im, (540, 430), 'МАСКИРОВКА!', 60, (255, 130, 200), ang=-5, a=b)
    if b > 0: d.ellipse((835, 380, 925, 420), fill=(60, 60, 110, int(255 * b)))
    if c > 0: tx(d, (540, 1150), "ЗАПАХ: БЕЗ ИЗМЕНЕНИЙ", 30, YEL, a=c, w="Medium")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 6. обзор 2017
def s6(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "03", "ОСВЕЖИТЕЛЬ", 1.0); a = P(6, lt, 0, 0.1, 0.5); b = P(6, lt, 1, 0.1, 0.6); c = P(6, lt, 2, 0.1, 0.5); e = P(6, lt, 3, 0.1, 0.8)
    d.rounded_rectangle((120, 440, 960, 570), 22, fill=(8, 14, 28, int(235 * a)), outline=ICE + (int(240 * a),), width=3); tx(d, (540, 505), "ОБЗОР 2017 · STEINEMANN", 46, ICE, a=a)
    if b > 0: tx(d, (540, 700), "АРОМАТ ≠ ОЧИСТКА", 58, PINK, a=b)
    if c > 0 or e > 0:
        n = int(100 * ease(e)); rng = np.random.default_rng(4)
        for k in range(n): px = 120 + (k % 20) * 42; py = 810 + (k // 20) * 42; d.ellipse((px - 12, py - 12, px + 12, py + 12), fill=LIL + (230,))
        if n > 0: tx(d, (540, 1050), (f"{n}" if n < 100 else "100+") + " ВЕЩЕСТВ ВЫДЕЛЯЮТ ОСВЕЖИТЕЛИ", 38, LIL, a=max(c, e)); tx(d, (540, 1110), "ОБЗОР 2017 ГОДА", 26, DIM, a=max(c, e), w="Medium")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 7. окно и вытяжка
def s7(lt, D):
    I = iso(104, 690, lt); im = bath(lt, I, wall_a=100, fan=1.0); lay, d = layer(); chap(d, "04", "ЧТО РАБОТАЕТ", P(7, lt, 0, 0.0, 0.3))
    w = P(7, lt, 1, 0.1, 0.6); v = P(7, lt, 3, 0.1, 0.6)
    mol(im, I, lt * 0.7 + 3, n=80, a=1.0, spread=1.2, keep=max(0.12, 1 - 0.8 * max(w, v)))
    if w > 0:
        for k in range(5):
            y = 2.2 + k * 0.38; p0 = I.p(-0.4, y, 1.6); p1 = I.p(1.8, y + 0.3, 1.6); ph_ = (lt * 0.7 + k * 0.2) % 1
            a_ = I.p(-0.4 + 2.2 * ph_, y + 0.3 * ph_, 1.6); d.ellipse((a_[0] - 9, a_[1] - 9, a_[0] + 9, a_[1] + 9), fill=(120, 230, 255, int(230 * w)))
        pill(d, (240, 1000), "ОКНО: РАЗБАВЛЯЕТ", 34, (120, 230, 255), a=w)
    if v > 0: pill(d, (760, 1000), "ВЫТЯЖКА: УНОСИТ", 34, GRN, a=v)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 8. уголь
def s8(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "04", "ЧТО РАБОТАЕТ", 1.0); a = P(8, lt, 0, 0.1, 0.6); b = P(8, lt, 1, 0.2, 0.8)
    d.rounded_rectangle((420, 520, 660, 900), 18, fill=(20, 22, 28, int(255 * a)), outline=(160, 170, 190, int(255 * a)), width=4); tx(d, (540, 710), "УГОЛЬ", 52, (200, 205, 220), a=a, w="Black")
    rng = np.random.default_rng(6)
    for k in range(26):
        ph_ = (lt * 0.5 + rng.uniform(0, 1)) % 1; y = 520 + rng.uniform(0, 380); x = 120 + ph_ * 300 if ph_ < 0.95 else 420
        if x < 415: d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=YEL + (int(230 * a),))
        else: d.ellipse((430, y - 7, 446, y + 7), fill=YEL + (int(160 * a),))
    pill(d, (540, 470), "ЕСЛИ ЕГО МНОГО", 34, GRN, a=a)
    for gx in range(6):
        for gy in range(10): d.ellipse((440 + gx * 33, 560 + gy * 32, 440 + gx * 33 + 20, 560 + gy * 32 + 20), fill=(60, 64, 76, int(255 * a)))
    tx(d, (540, 1130), "НЕ ЗАМЕНЯЕТ ПРОВЕТРИВАНИЕ (US EPA)", 28, GRN, a=b, w="Medium")
    if b > 0: d.rounded_rectangle((130, 980, 950, 1090), 20, fill=(8, 14, 28, int(230 * b)), outline=DIM + (int(230 * b),), width=2); tx(d, (540, 1035), "«ЛОВИТ МОЛЕКУЛЫ» — ПРОВЕРИТЬ ТРУДНО", 34, WHT, a=b)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 9. вывод
def s9(lt, D):
    I = iso(100, 690, lt); im = bath(lt, I, wall_a=110, dim=0.7); lay, d = layer(); chap(d, "05", "ВЫВОД", P(9, lt, 0, 0.0, 0.3))
    a = P(9, lt, 0, 0.2, 0.8); b = P(9, lt, 1, 0.2, 0.8); c = P(9, lt, 2, 0.1, 0.9)
    if a > 0: tx(d, (540, 520), "ЧИСТИТ?", 80, WHT, a=a, w="Black")
    if b > 0: stamp(im, (540, 700), "НЕТ!", 190, (255, 70, 60), ang=-7, a=b)
    if c > 0: pill(d, (300, 1010), "ОСВЕЖИТЕЛЬ — ПЕРЕБИВАЕТ", 32, PINK, a=c); pill(d, (780, 1090), "ОКНО — РАЗБАВЛЯЕТ", 32, (120, 230, 255), a=c)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 10. концовка
def s10(lt, D):
    I = iso(100, 690, lt); im = bath(lt, I, wall_a=130, dim=0.6); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(140 * P(10, lt, 0, 0.0, 0.4)))))
    lay, d = layer(); b = P(10, lt, 0, 0.1, 0.5); s_ = 1 + 0.04 * math.sin(lt * 6); w_, h_ = 480 * s_, 120 * s_
    if b > 0: d.rounded_rectangle((540 - w_ / 2, 760 - h_ / 2, 540 + w_ / 2, 760 + h_ / 2), 60, fill=(255, 200, 60, int(255 * b))); tx(d, (540, 760), "ОТПРАВЬ", 58, (20, 14, 6), a=b)
    return fin(im, lay, lt, k=0.5)
SCENES = [
    ("После туалета нажимаешь освежитель? | Ты обманул только свой нос.", "SUB", "", s0, "", None),
    ("Простым языком.", "SUB", "", s1, "", None),
    ("После туалета остаётся запах. | Это молекулы. | Они летят по комнате, как туристы на экскурсии.", "SUB", "", s2, "", None),
    ("Главные виновники — вещества с серой. | Учёные выяснили это в тысяча девятьсот восемьдесят седьмом.", "SUB", "", s3, "", None),
    ("А нос — детектор. | У него сотни видов рецепторов. | Запах тухлых яиц, сероводород, одни люди чуют при пяти молекулах на десять миллиардов.", "SUB", "", s4, "", None),
    ("Что же делает освежитель? | Он — парфюмер. | Молекулы запаха на месте, а поверх — цветочный букет.", "SUB", "", s5, "", None),
    ("Обзор две тысячи семнадцатого года говорит: | аромат не предназначен чистить воздух. | Заодно в воздух идут его вещества. | Там насчитали больше ста разных.", "SUB", "", s6, "", None),
    ("Как убрать запах по-настоящему? | Открыть окно. | Свежий воздух разбавляет. | Вытяжка уносит.", "SUB", "", s7, "", None),
    ("Активированный уголь ловит газы, если его много. | Обещания «ловить молекулы» проверить трудно.", "SUB", "", s8, "", None),
    ("Так чистит ли освежитель воздух? | Нет. Он перебивает. | Освежитель перебивает, окно разбавляет.", "SUB", "", s9, "", None),
    ("Отправь тому, кто после туалета лечит комнату одним нажатием. | Подпишись.", "SUB", SUB_PLATE, s10, "", None),
]
def SFX(STARTS, PHRASES, DURS, SR):
    out = []; rng = np.random.default_rng(3)
    def tm(i, k, f=0.0): st, en, _ = PHRASES[i][k]; return STARTS[i] + st + f * (en - st)
    def click(a=0.25): t = np.arange(int(SR * 0.04)) / SR; return a * np.exp(-t * 120) * np.sin(2 * np.pi * 2200 * t)
    def hiss(dur=1.0, a=0.12): n = rng.normal(0, 1, int(SR * dur)); x = gaussian_filter1d(n, 2) * 1.5; t = np.arange(len(x)) / SR; return a * x * np.exp(-t * 2.2)
    def buzz(dur=0.6, a=0.2): t = np.arange(int(SR * dur)) / SR; return a * np.exp(-t * 4) * np.sin(2 * np.pi * 150 * t)
    out += [(tm(0, 0, 0.6), hiss(1.2, 0.14)), (tm(1, 0, 0.0), click(0.3)), (tm(5, 1, 0.3), hiss(1.2, 0.14)), (tm(9, 1, 0.2), buzz(0.5, 0.25)), (tm(10, 0, 0.1), click(0.25))]
    return out
