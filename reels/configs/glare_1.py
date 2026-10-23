"""«Встречные фары слепят. Почему?» — «Простым языком», ночная трасса от лица водителя. Сценарий: scripts/glare_1.md, визуал: scripts/glare_1_visual.md.
Идея и структура — по референсу пользователя (хук-плашка, главы в шапке, спидометры, жёлтые субтитры); текст и графика свои, кодом: configs/road_kit.py."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import bh_cine as B, road_kit as R
from bh_cine import W, H, ease, seg, lerp, fnt
HEAD = ("ПРОСТЫМ ЯЗЫКОМ", "ОСЛЕПЛЕНИЕ ФАРАМИ")
TITLE = ("", "", "")
HOOK = ("ВСТРЕЧНЫЕ ФАРЫ\nСЛЕПЯТ. ПОЧЕМУ?", 1.9)
HOOK_Y = 1010
MUSIC = ("music/ogv_aria.mp3", 0)
SUB_STYLE = "words"; WORDS_TAG = False; WORDS_Y = 1300; WORDS_SIZE = 92
AA = 0.35; GRAIN = 4.5
TAIL = 0.3; XF = 0.3; LEAD_N = 0.2; GAP = 0.28
RED = (255, 80, 60); GOLD = (255, 214, 60); ICE = (170, 215, 255); WHT = (240, 244, 255); DIM = (130, 150, 190); BLUE = (60, 150, 255); ORNG = (255, 140, 50); NEON = (80, 235, 205); GRN = (110, 235, 140)
BG = (6, 9, 18)
def ph(i, k):
    import __main__ as E
    return E.PHRASES[i][k]
def T(i, k, f=0.0): st, en, _ = ph(i, k); return st + f * (en - st)
def P(i, lt, k, f0=0.0, f1=1.0): return seg(lt, T(i, k, f0), T(i, k, f1))
def layer(): lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)
def fin(base, lay=None, lt=0.0, shake=1.0, k=0.6, streak=0.06, ca=2, zoom=True):
    base = base.convert("RGBA")
    if lay is not None: base.alpha_composite(lay)
    if zoom:
        z = 1.0 + 0.010 * min(lt, 9.0)
        if z > 1.0005:
            w_, h_ = W / z, H / z; base = base.transform((W, H), Image.AFFINE, (1 / z, 0, (W - w_) / 2, 0, 1 / z, (H - h_) / 2), Image.BICUBIC)
    return B.finish_c(base, k=k + 0.1, streak=streak, shake=shake, lt=lt, ca=ca)
def tx(d, xy, s, size, col=WHT, a=1.0, w="Bold", anchor="mm"):
    if a < 0.03: return
    d.text(xy, s, font=fnt(size, w), fill=col + (int(255 * min(a, 1)),), anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0, int(140 * min(a, 1))))
def card(d, box, col, a=1.0, r=20):
    if a < 0.03: return
    d.rounded_rectangle(box, r, fill=(8, 14, 28, int(232 * a)), outline=col + (int(240 * a),), width=3)
def dark(): return Image.new("RGBA", (W, H), BG + (255,))
def grid_bg(lt):
    im = dark(); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(20, 30, 52, 255), width=1)
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(20, 30, 52, 255), width=1)
    return im
def chap(d, n, title, u=1.0):
    tx(d, (90, 318), f"{n} / 06", 34, GOLD, a=u, anchor="lm"); tx(d, (990, 318), title, 38, WHT, a=u, anchor="rm")
    d.line([(90, 350), (990, 350)], fill=NEON + (int(120 * u),), width=2)
def corners(d, a=0.5):
    for (x, y, sx, sy) in ((60, 380, 1, 1), (1020, 380, -1, 1), (60, 1120, 1, -1), (1020, 1120, -1, -1)):
        d.line([(x, y), (x + 44 * sx, y)], fill=NEON + (int(200 * a),), width=3); d.line([(x, y), (x, y + 44 * sy)], fill=NEON + (int(200 * a),), width=3)
def rec(d, lt, a=1.0):
    if int(lt * 2) % 2 == 0: d.ellipse((92, 372, 110, 390), fill=RED + (int(230 * a),))
    tx(d, (170, 381), "ЗАПИСЬ · САЛОН", 22, DIM, a=a, w="Medium", anchor="lm")
# ---------- 0. хук
def s0(lt, D):
    zc = 34 - 24 * seg(lt, 0, D); im = R.road(lt * 9, 1.0, 1.0); R.headlights(im, zc, a=1.0); R.car_front(im, zc)
    f = 0.35 + 0.65 * seg(lt, 0.0, 1.0); R.flood(im, 0.5 * f, (460, 740)); lay, d = layer()
    p = R.proj(-1.8, zc, 0.68); B.reticle(d, p, 130, RED + (230,), u=seg(lt, 0.15, 0.6), ticks=36, w=3)
    R.dial(d, (870, 1150), 120, 60 + 30 * seg(lt, 0, 1.2), 140, WHT); corners(d, 0.5)
    return fin(im, lay, lt, shake=1.4, k=0.5)
# ---------- 1. «Простым языком»
def s1(lt, D):
    zc = 20 - 6 * seg(lt, 0, D); im = R.road(lt * 9 + 20, 1.0, 0.85); R.headlights(im, zc, a=0.55); R.car_front(im, zc)
    lay, d = layer(); a = P(1, lt, 0, 0.0, 0.8); chap(d, "01", "ВОПРОС", a); rec(d, lt, a)
    B.tracked(d, (540, 1120), "ПОЧЕМУ ЭТО ПРОИСХОДИТ", 38, NEON, u=P(1, lt, 0, 0.3, 1.0)); corners(d, 0.5)
    return fin(im, lay, lt, k=0.55)
# ---------- 2. зрачок: 8 мм → 4 мм
def s2(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "02", "ЗРАЧОК", P(2, lt, 0, 0.0, 0.3)); n = P(2, lt, 2, 0.0, 0.9)
    mm = lerp((8, 0, 0), (4, 0, 0), 0)[0] if False else 8.0 - 4.0 * ease(P(2, lt, 2, 0.05, 0.8))
    light = 0.9 * P(2, lt, 2, 0.0, 0.5) * (1 - P(2, lt, 2, 0.6, 1.0) * 0.4)
    c = (540, 700); pr = R.eye(im, c, 1.0, mm, light)
    if lt > T(2, 1, 0.1):
        cc = (540 + (pr), 700)
        a = P(2, lt, 1, 0.2, 0.8)
        d.line([(540 - pr, 700 + 200), (540 + pr, 700 + 200)], fill=GOLD + (int(255 * min(1, a + n)),), width=5)
        for x in (540 - pr, 540 + pr): d.line([(x, 700 + 186), (x, 700 + 214)], fill=GOLD + (255,), width=4)
        tx(d, (540, 700 + 250), f"{mm:.0f} мм".replace(".", ","), 70, GOLD, a=1.0, w="Black")
    t1 = P(2, lt, 1, 0.3, 0.9); t2 = P(2, lt, 2, 0.3, 0.9)
    card(d, (90, 1040, 520, 1130), NEON, t1); tx(d, (305, 1085), "ТЕМНОТА: до 8 мм", 32, NEON, a=t1)
    card(d, (560, 1040, 990, 1130), GOLD, t2); tx(d, (775, 1085), "СВЕТ: до 4 мм", 32, GOLD, a=t2)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 3. фары навстречу, зрачок сужается, дорога темнеет
def s3(lt, D):
    u = P(3, lt, 0, 0.0, 1.0); w2 = P(3, lt, 2, 0.0, 0.9)
    zc = 120 - 95 * seg(lt, 0, T(3, 2, 0.5)); dk = 1.0 - 0.62 * w2
    im = R.road(lt * 9 + 40, 1.0, dk); R.headlights(im, zc, a=1.0); R.car_front(im, zc)
    R.flood(im, 0.35 * seg(lt, T(3, 1, 0), T(3, 2, 0.8)), R.proj(-1.8, zc, 0.68)); lay, d = layer()
    chap(d, "02", "ЗРАЧОК", 1.0); mm = 8.0 - 4.0 * ease(P(3, lt, 1, 0.1, 1.0))
    R.eye_mini(d, (900, 520), 90, mm); tx(d, (900, 640), f"{mm:.0f} мм".replace(".", ","), 34, WHT, a=1.0)
    b = P(3, lt, 2, 0.1, 0.9); card(d, (90, 1040, 600, 1130), RED, b); tx(d, (345, 1070), "яркость дороги", 26, DIM, a=b, w="Medium")
    d.rounded_rectangle((120, 1092, 570, 1108), 7, outline=RED + (int(255 * b),), width=2); d.rounded_rectangle((120, 1092, 120 + 450 * (1 - 0.62 * w2), 1108), 7, fill=RED + (int(255 * b),))
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 4. вуаль внутри глаза
def s4(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "03", "ВУАЛЬ", P(4, lt, 0, 0.0, 0.4))
    c = (610, 700); rr = 230
    d.ellipse((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), outline=ICE + (255,), width=6, fill=(14, 22, 40, 255))
    d.arc((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), -50, 50, fill=RED + (255,), width=14)                # сетчатка
    d.ellipse((c[0] - 235, c[1] - 55, c[0] - 160, c[1] + 55), fill=(120, 190, 235, 200), outline=ICE + (255,), width=3)       # хрусталик
    d.arc((c[0] - rr - 40, c[1] - 120, c[0] - rr + 60, c[1] + 120), 270, 90, fill=ICE + (255,), width=6)  # роговица
    ray = P(4, lt, 1, 0.0, 0.5); fan = P(4, lt, 1, 0.4, 1.0); rng = np.random.default_rng(3)
    x0 = c[0] - 470; xe = c[0] - 215
    if ray > 0: d.line([(x0, c[1]), (x0 + (xe - x0) * ray, c[1])], fill=(255, 246, 222, 255), width=9)
    if fan > 0:
        for k in range(26):
            ang = rng.uniform(-0.75, 0.75); L = 330 * fan * rng.uniform(0.7, 1.0)
            d.line([(c[0] - 150, c[1]), (c[0] - 150 + L * math.cos(ang), c[1] + L * math.sin(ang))], fill=(255, 246, 222, 120), width=3)
    v = P(4, lt, 2, 0.1, 0.9)
    if v > 0:
        vl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); vd = ImageDraw.Draw(vl); vd.ellipse((c[0] + 20, c[1] - 170, c[0] + 270, c[1] + 170), fill=(255, 250, 235, int(170 * v))); im.alpha_composite(vl.filter(ImageFilter.GaussianBlur(26)))
    # панель «дорога»: силуэт тонет
    pb = (90, 980, 990, 1170); d.rounded_rectangle(pb, 20, fill=(10, 14, 24, 255), outline=NEON + (230,), width=2)
    d.polygon([(90, 1170), (990, 1170), (800, 980), (280, 980)], fill=(26, 32, 46, 255)); R.person(d, (540, 1160), 150, (8, 10, 16))
    cv = P(4, lt, 3, 0.0, 0.9); veil = 0.78 * max(v * 0.5, cv)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); od.rounded_rectangle(pb, 20, fill=(255, 250, 238, int(255 * veil))); im2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im2.alpha_composite(ov)
    lay.alpha_composite(im2) if False else None
    tx(d, (300, 950), "контраст", 28, DIM, a=1.0, w="Medium"); d.rounded_rectangle((380, 938, 640, 962), 10, outline=NEON + (255,), width=2); d.rounded_rectangle((380, 938, 380 + 260 * (1 - 0.7 * cv), 962), 10, fill=NEON + (255,))
    corners(d, 0.5); base = fin(im, lay, lt, k=0.6)
    if veil > 0.01: base = base.convert("RGBA"); base.alpha_composite(ov); 
    return base
# ---------- 5. рехук: фары проехали, а дорога тёмная
def s5(lt, D):
    zc = 14 - 12 * seg(lt, 0, 1.2); dk = 0.38
    im = R.road(lt * 9 + 60, 0.6, dk); lay, d = layer()
    if zc > 3: R.headlights(im, zc, a=1.0 * (1 - seg(lt, 0.6, 1.2))); R.car_front(im, zc)
    ln = R.proj(4.0, 15); R.person(d, (ln[0], R.proj(4.0, 15)[1]), 105, (4, 6, 10), 235)
    q = seg(lt, 0.8, 1.6); B.reticle(d, (ln[0], ln[1] - 52), 90, RED + (int(230 * q),), u=q, ticks=24, w=3); tx(d, (ln[0], ln[1] - 200), "?", 120, RED, a=q, w="Black")
    chap(d, "04", "ТЕМНОТА", P(5, lt, 0, 0.0, 0.4)); corners(d, 0.5)
    return fin(im, lay, lt, k=0.55)
# ---------- 6. адаптация: шкалы времени
def s6(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "04", "ТЕМНОТА", 1.0)
    t0 = T(6, 0, 0.1); span = T(6, 0, 1.0) - t0; flash_t = T(6, 1, 0.1)
    def prog(full):
        if lt < t0: return 0.0
        if lt < flash_t: return min(1.0, (lt - t0) / span) * full
        return max(0.0, min(1.0, (flash_t - t0) / span) * full - 0.0) * (1 - 0.7 * seg(lt, flash_t, flash_t + 0.35)) + 0.0
    x0, x1 = 120, 960
    for k, m in enumerate((0, 10, 20, 30, 45)):
        x = x0 + (x1 - x0) * m / 45; d.line([(x, 560), (x, 580)], fill=DIM + (255,), width=3); tx(d, (x, 620), f"{m}", 28, DIM, a=1.0, w="Medium")
    tx(d, (540, 670), "минут в темноте", 26, DIM, a=1.0, w="Medium")
    for y, nm, full, col in ((780, "КОЛБОЧКИ ≈ 10 мин", 10 / 45, NEON), (940, "ПАЛОЧКИ 30–45 мин", 1.0, GOLD)):
        d.rounded_rectangle((x0, y, x1, y + 56), 14, outline=col + (255,), width=3); tx(d, (x0, y - 28), nm, 30, col, a=1.0, anchor="lm")
        pr = prog(full) if lt < flash_t else prog(full)
        d.rounded_rectangle((x0 + 4, y + 4, x0 + 4 + max(0, (x1 - x0 - 8) * pr), y + 52), 11, fill=col + (255,))
    fl = max(0.0, 1 - abs(lt - flash_t) / 0.35) if lt > flash_t - 0.05 else 0
    base = fin(im, lay, lt, k=0.6)
    if fl > 0.02: R.flood(base, fl * 0.9)
    return base
# ---------- 7. «Теперь цифры» — вид сверху
def topview(d, car_z, lt, a=1.0, scale=7.0, veil=None):
    """Вид сверху: полоса сверху вниз, 1 м = scale px; машина ниже центра."""
    x = 540; d.rectangle((x - 150, 380, x + 150, 1130), fill=(18, 24, 38, 255)); d.line([(x - 150, 380), (x - 150, 1130)], fill=(220, 224, 232, 255), width=4); d.line([(x + 150, 380), (x + 150, 1130)], fill=(220, 224, 232, 255), width=4)
    for k in range(-2, 12):
        y = 1130 - ((k * 20 + car_z) % 220) * 1.0 * 3.4 + 0
    return x
def s7(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "05", "РАСЧЁТ", P(7, lt, 0, 0.0, 0.4))
    x = 540; d.rectangle((x - 140, 380, x + 140, 1130), fill=(18, 24, 38, 255)); d.line([(x - 140, 380), (x - 140, 1130)], fill=ICE + (255,), width=4); d.line([(x + 140, 380), (x + 140, 1130)], fill=ICE + (255,), width=4)
    for k in range(8):
        y = 400 + ((k * 100 + lt * 300) % 760); d.line([(x, y), (x, y + 50)], fill=(200, 205, 215, 255), width=4)
    d.rounded_rectangle((x - 40, 940, x + 40, 1070), 16, fill=NEON + (255,)); d.polygon([(x - 28, 960), (x + 28, 960), (x + 20, 990), (x - 20, 990)], fill=(8, 14, 28, 255))
    a = P(7, lt, 0, 0.3, 1.0); card(d, (300, 1170, 780, 1250), GOLD, a); tx(d, (540, 1210), "СЧИТАЕМ", 32, GOLD, a=a); corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 8. 90 км/ч = 25 м/с
def s8(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "05", "РАСЧЁТ", 1.0)
    v = 90 * ease(P(8, lt, 0, 0.0, 0.7)); R.dial(d, (540, 720), 250, v, 140, NEON)
    f1 = P(8, lt, 1, 0.1, 0.6); f2 = P(8, lt, 1, 0.5, 1.0)
    if f1 > 0:
        card(d, (110, 1040, 970, 1150), GOLD, f1); tx(d, (540, 1095), "90 000 м ÷ 3 600 с", 60, WHT, a=f1)
    if f2 > 0: tx(d, (540, 1210), "= 25 м/с", 90, GOLD, a=f2, w="Black")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 9. метры вслепую
def s9(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "05", "РАСЧЁТ", 1.0)
    x = 540; top, bot = 420, 1090; sc = (bot - top) / 80.0                      # 80 м на экране
    d.rectangle((x - 140, top, x + 140, bot), fill=(18, 24, 38, 255)); d.line([(x - 140, top), (x - 140, bot)], fill=ICE + (255,), width=4); d.line([(x + 140, top), (x + 140, bot)], fill=ICE + (255,), width=4)
    for m in range(0, 81, 10):
        y = bot - m * sc; d.line([(x + 140, y), (x + 170, y)], fill=DIM + (255,), width=3); tx(d, (x + 200, y), f"{m}", 22, DIM, a=1.0, w="Medium", anchor="lm")
    a = P(9, lt, 0, 0.1, 0.9); b = P(9, lt, 1, 0.0, 0.9); c = P(9, lt, 2, 0.1, 0.9)
    for m, f, col in ((50, a if lt < T(9, 2, 0) else 1.0, ORNG), (75, c, RED)):
        if f > 0:
            y = bot - m * sc * min(1, f); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); od.rectangle((x - 140, y, x + 140, bot), fill=col + (int(70 * f),)); lay.alpha_composite(ov)
            d.line([(x - 190, y), (x + 140, y)], fill=col + (255,), width=5); tx(d, (x - 220, y), f"{m} м", 44, col, a=f, w="Black", anchor="rm")
    cy = bot - 4 + 0; d.rounded_rectangle((x - 36, cy - 120, x + 36, cy - 4), 14, fill=NEON + (255,))
    sec = 2 if lt < T(9, 2, 0.1) else 3
    card(d, (110, 1170, 450, 1260), GOLD, 1.0); tx(d, (280, 1215), f"{sec} с", 56, GOLD, a=1.0, w="Black")
    card(d, (500, 1170, 970, 1260), RED, 1.0); tx(d, (735, 1215), "ВСЛЕПУЮ", 44, RED, a=1.0)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 10. «Что делать?» — белое → чёрное
def s10(lt, D):
    im = dark(); lay, d = layer(); chap(d, "06", "ЧТО ДЕЛАТЬ", seg(lt, 0.1, 0.6))
    a = seg(lt, 0.2, 1.0)
    for k, (t, col) in enumerate((("1  ВЗГЛЯД", NEON), ("2  СКОРОСТЬ", GOLD), ("3  СВЕТ", ORNG))):
        f = seg(lt, 0.3 + 0.25 * k, 0.8 + 0.25 * k); y = 560 + k * 150; card(d, (140, y - 55, 940, y + 55), col, f); tx(d, (540, y), t, 56, col, a=f, w="Black")
    base = fin(im, lay, lt, k=0.6); R.flood(base, 1 - seg(lt, 0.0, 0.5)); return base
# ---------- 11. взгляд на правый край
def s11(lt, D):
    u = P(11, lt, 0, 0.0, 1.0); g = P(11, lt, 1, 0.0, 0.8)
    im = R.road(lt * 9 + 80, 1.0, 0.9); zc = 30 - 8 * seg(lt, 0, D); R.headlights(im, zc, a=1.0); R.car_front(im, zc)
    if g > 0: R.edge_line(im, NEON, a=g)
    lay, d = layer(); chap(d, "06", "ЧТО ДЕЛАТЬ", 1.0); p0 = R.proj(-1.8, zc, 0.68); p1 = (860, 1130)
    p = (p0[0] + (p1[0] - p0[0]) * ease(g), p0[1] + (p1[1] - p0[1]) * ease(g))
    B.reticle(d, p, 80, (RED if g < 0.5 else NEON) + (240,), u=1.0, ticks=24, w=3)
    t = P(11, lt, 0, 0.3, 1.0); card(d, (110, 400, 970, 480), RED if g < 0.4 else NEON, t); tx(d, (540, 440), "1. взгляд — на правый край" if g > 0.4 else "не смотри в фары", 36, WHT, a=t)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.55)
# ---------- 12. скорость вниз, аварийка, п. 19.2
def s12(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "06", "ЧТО ДЕЛАТЬ", 1.0)
    v = 90 - 90 * ease(P(12, lt, 3, 0.0, 1.0)) if lt >= T(12, 3, 0) else 90 - 45 * ease(P(12, lt, 0, 0.1, 0.9))
    R.dial(d, (540, 640), 215, v, 140, GOLD)
    h = P(12, lt, 1, 0.2, 0.9); on = (int(lt * 3) % 2 == 0)
    if h > 0:
        for sx in (-1, 1):
            c = (540 + sx * 330, 920); col = ORNG if on else (90, 60, 30); d.polygon([(c[0], c[1] - 70), (c[0] + 66, c[1] + 50), (c[0] - 66, c[1] + 50)], outline=col + (255,), width=10)
    pc = P(12, lt, 1, 0.3, 1.0); card(d, (110, 1010, 970, 1180), GOLD, pc); tx(d, (540, 1050), "п. 19.2 ПДД РФ", 44, GOLD, a=pc, w="Black")
    for k, s in enumerate(("аварийка", "полоса не меняется", "скорость вниз → остановка")):
        f = P(12, lt, 2 if k < 2 else 3, 0.1, 0.9); tx(d, (540, 1095 + k * 30), s, 24, WHT, a=f, w="Medium") if f > 0 and k == 0 and False else None
    f2 = P(12, lt, 2, 0.1, 0.9); f3 = P(12, lt, 3, 0.1, 0.9)
    tx(d, (540, 1105), "аварийка · полоса та же · остановись", 28, WHT, a=min(1, f2 + f3), w="Medium")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 13. дальний → ближний за 150 м
def s13(lt, D):
    sw = P(13, lt, 1, 0.0, 0.7); zc = 190 - 140 * seg(lt, 0, D)
    im = R.road(lt * 9 + 100, 1.0 - 0.5 * sw, 1.0); R.headlights(im, zc, a=1.0 - 0.8 * sw, size=1.0 - 0.0 * sw); R.car_front(im, zc)
    R.flood(im, 0.35 * (1 - sw) * seg(lt, 0.3, 1.4), R.proj(-1.8, zc, 0.68)); lay, d = layer(); chap(d, "06", "ЧТО ДЕЛАТЬ", 1.0)
    z150 = 150.0
    if zc < 190: pass
    p = R.proj(0, 150); d.line([(p[0] - 220, p[1]), (p[0] + 220, p[1])], fill=GOLD + (255,), width=5); tx(d, (p[0], p[1] - 36), "150 м", 50, GOLD, a=1.0, w="Black")
    k = P(13, lt, 1, 0.1, 0.9); card(d, (110, 400, 970, 480), NEON, P(13, lt, 0, 0.2, 0.9)); tx(d, (540, 440), "дальний → ближний" if sw > 0.3 else "дальний свет", 36, WHT, a=1.0)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.55)
# ---------- 14. вывод — кадр хука, но спокойно
def s14(lt, D):
    zc = 60 - 20 * seg(lt, 0, D); im = R.road(lt * 9 + 120, 1.0, 1.0); R.headlights(im, zc, a=0.45); R.car_front(im, zc); R.edge_line(im, NEON, a=P(14, lt, 2, 0.0, 0.6))
    lay, d = layer(); chap(d, "06", "ВЫВОД", 1.0); R.eye_mini(d, (900, 520), 80, 6.0)
    for k, (s, col) in enumerate((("широкий зрачок", NEON), ("вуаль внутри глаза", ICE), ("сбитая привычка", GOLD))):
        f = P(14, lt, 1, 0.2 + 0.3 * k, 0.5 + 0.3 * k); card(d, (110, 440 + 80 * k, 640, 510 + 80 * k), col, f, 16); tx(d, (375, 475 + 80 * k), s, 32, col, a=f)
    q = P(14, lt, 2, 0.1, 0.8)
    if q > 0: card(d, (80, 1010, 1000, 1180), GOLD, q); tx(d, (540, 1065), "НЕ СМОТРИ НА СВЕТ —", 48, WHT, a=q, w="Black"); tx(d, (540, 1130), "СМОТРИ НА КРАЙ", 56, NEON, a=q, w="Black")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.55)
# ---------- 15. зеркало и призыв
def s15(lt, D):
    im = R.road(lt * 9 + 140, 1.0, 0.45); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * P(15, lt, 0, 0.0, 0.4)))))
    lay, d = layer(); m = (540, 520); d.rounded_rectangle((m[0] - 250, m[1] - 90, m[0] + 250, m[1] + 90), 40, fill=(10, 16, 26, 240), outline=ICE + (255,), width=4)
    b = P(15, lt, 0, 0.1, 0.5); R.eye(lay, (540, 520), 0.28, 6.0, 0.0)
    s_ = 1 + 0.04 * math.sin(lt * 6); w_, h_ = 480 * s_, 120 * s_
    if b > 0: d.rounded_rectangle((540 - w_ / 2, 820 - h_ / 2, 540 + w_ / 2, 820 + h_ / 2), 60, fill=(255, 200, 60, int(255 * b))); tx(d, (540, 820), "ОТПРАВЬ", 58, (20, 14, 6), a=b)
    return fin(im, lay, lt, k=0.5, zoom=False)
SCENES = [
    ("Встречные фары слепят. Почему?", "SUB", "", s0, "", None),
    ("Простым языком.", "SUB", "", s1, "", None),
    ("Ночью зрачок широкий. | В темноте — до восьми миллиметров, | на свету — до четырёх.", "SUB", "", s2, "", None),
    ("Навстречу — фары. | Зрачок сужается, | и вся остальная дорога темнеет.", "SUB", "", s3, "", None),
    ("Но это не всё. | Яркий свет рассеивается прямо внутри глаза. | На картинку ложится светлая вуаль, | и контраст пропадает.", "SUB", "", s4, "", None),
    ("А когда фары проехали — легче не станет.", "SUB", "", s5, "", None),
    ("Привыкнуть к темноте — от десяти до сорока пяти минут. | Яркий свет сбивает эту привычку.", "SUB", "", s6, "", None),
    ("Теперь цифры.", "SUB", "", s7, "", None),
    ("Девяносто километров в час — | это двадцать пять метров в секунду.", "SUB", "", s8, "", None),
    ("Ты ослеп на две секунды — | пятьдесят метров вслепую. | На три секунды — семьдесят пять.", "SUB", "", s9, "", None),
    ("Что делать?", "SUB", "", s10, "", None),
    ("Не смотри в фары. | Скоси взгляд правее, на обочину.", "SUB", "", s11, "", None),
    ("Сбрось скорость. | Если ослеп совсем — пункт девятнадцать, два: | включи аварийку, не меняй полосу, | снижай скорость и остановись.", "SUB", "", s12, "", None),
    ("Свой дальний свет | переключай на ближний | за сто пятьдесят метров до встречной.", "SUB", "", s13, "", None),
    ("Так почему слепят фары? | Широкий зрачок, вуаль внутри глаза, плюс сбитая привычка. | Не смотри на свет — смотри на край.", "SUB", "", s14, "", None),
    ("Отправь тому, кто смотрит прямо в фары. | Подпишись.", "SUB", SUB_PLATE, s15, "", None),
]
def SFX(STARTS, PHRASES, DURS, SR):
    out = []
    def tm(i, k, f=0.0): st, en, _ = PHRASES[i][k]; return STARTS[i] + st + f * (en - st)
    def click(a=0.25): t = np.arange(int(SR * 0.04)) / SR; return a * np.exp(-t * 120) * np.sin(2 * np.pi * 2200 * t)
    def whoosh(a=0.3, dur=0.9): t = np.arange(int(SR * dur)) / SR; n = np.random.default_rng(4).standard_normal(len(t)); return a * n * np.sin(np.pi * t / dur) ** 2 * 0.4
    def beep(dur=1.0, a=0.08): t = np.arange(int(SR * dur)) / SR; g = (np.floor(t * 3) % 2 == 0); return a * g * np.sin(2 * np.pi * 880 * t)
    out += [(STARTS[0] + 0.3, whoosh(0.5, 1.2)), (tm(1, 0, 0.0), click(0.3)), (tm(3, 0, 0.0), whoosh(0.4, 1.4)), (tm(5, 0, 0.0), whoosh(0.35, 1.0)), (tm(6, 1, 0.1), whoosh(0.45, 0.6)),
            (tm(8, 0, 0.0), click(0.3)), (tm(9, 0, 0.0), click(0.3)), (tm(10, 0, 0.0), click(0.3)), (tm(12, 1, 0.1), beep(1.2, 0.08)), (tm(15, 0, 0.1), click(0.25))]
    return out
