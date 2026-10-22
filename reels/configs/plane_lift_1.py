"""«Сотни тонн металла. Почему они не падают?» — формат «Простым языком», кинематографичная моушен-графика.
Фото: NASA Image and Video Library (общественное достояние): ED11-0211-06, ED07-0079-03, ED07-0079-02, AFRC2021-0106-03, EC98-44428-005.
Обтекание крыла посчитано кодом (профиль Жуковского, условие Кутты) — configs/aero.py. Факты: NASA Glenn, Beginner's Guide to Aeronautics
(Lift Equation; Incorrect Theory — Equal Transit; Four Forces; Inclination Effects). Сценарий: scripts/plane_lift_1.md, визуал: scripts/plane_lift_1_visual.md."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter1d
import bh_cine as B, aero as A, plane_kit as K
from bh_cine import W, H, ease, seg, lerp, fnt
HEAD = ("ПРОСТЫМ ЯЗЫКОМ", "ПОЧЕМУ САМОЛЁТ НЕ ПАДАЕТ")
TITLE = ("", "", "")
HOOK = ("СОТНИ ТОНН.\nПОЧЕМУ НЕ ПАДАЮТ?", 2.6)
HOOK_Y = 1000
MUSIC = ("music/ogv_aria.mp3", 0)
SUB_STYLE = "words"; WORDS_TAG = False; WORDS_Y = 1300; WORDS_SIZE = 92
AA = 0.35
TAIL = 0.3; XF = 0.35; LEAD_N = 0.2; GAP = 0.28
RED = (255, 80, 60); GOLD = (255, 214, 60); ICE = (170, 215, 255); WHT = (240, 244, 255); DIM = (130, 150, 190); BLUE = (60, 150, 255); ORNG = (255, 140, 50)
BG = (6, 9, 18)
def ph(i, k):
    import __main__ as E
    return E.PHRASES[i][k]
def T(i, k, f=0.0): st, en, _ = ph(i, k); return st + f * (en - st)
def P(i, lt, k, f0=0.0, f1=1.0): return seg(lt, T(i, k, f0), T(i, k, f1))
def layer(): lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)
def fin(base, lay=None, lt=0.0, shake=1.5, k=0.6, streak=0.3, ca=2):
    base = base.convert("RGBA")
    if lay is not None: base.alpha_composite(lay)
    return B.finish_c(base, k=k, streak=streak, shake=shake, lt=lt, ca=ca)
def tx(d, xy, s, size, col=WHT, a=1.0, w="Bold", anchor="mm"):
    if a < 0.03: return
    d.text(xy, s, font=fnt(size, w), fill=col + (int(255 * min(a, 1)),), anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0, int(140 * min(a, 1))))
def pill(d, xy, s, size, col, a=1.0, w="Bold"):
    if a < 0.03: return
    f = fnt(size, w); tw = d.textlength(s, font=f); x, y = xy
    d.rounded_rectangle((x - tw / 2 - 18, y - size * 0.75, x + tw / 2 + 18, y + size * 0.75), int(size * 0.75), fill=(6, 9, 18, int(200 * a)), outline=col + (int(200 * a),), width=2)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor="mm")
def dark(): return Image.new("RGBA", (W, H), BG + (255,))
def grid_bg(lt, a=1.0):
    im = dark(); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(20, 30, 52, int(255 * a)), width=1)
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(20, 30, 52, int(255 * a)), width=1)
    return im
def wing_scene(alpha, lt, pressure=0.0, particles=1.0, chaos=0.0, lift=0.0, cy=640, flap=0.0, tint=1.0):
    """Крыло в разрезе: сетка, поле давления, частицы потока, само крыло, стрелка подъёмной силы."""
    v = A.View(cy=cy, alpha=alpha); im = grid_bg(lt)
    if pressure > 0.01: im.alpha_composite(A.pressure_layer(v, alpha, strength=pressure * (1 - 0.8 * min(1, chaos))))
    lay, d = layer()
    if particles > 0.01: A.draw_particles(lay, v, alpha, lt, a=particles, chaos=chaos)
    im.alpha_composite(lay)
    lay2, d2 = layer(); pts = A.wing_shape(lay2, v)
    if flap > 0:
        te = A.outline()[0]; ang = -alpha - flap * 0.6
        fx_, fy_ = v.to_screen(np.array([te])); fx_, fy_ = float(fx_[0]), float(fy_[0]); L = 150 * flap + 40
        d2.polygon([(fx_ - 10, fy_ - 6), (fx_ + L * math.cos(ang), fy_ - L * math.sin(ang)), (fx_ + L * math.cos(ang) - 6, fy_ - L * math.sin(ang) + 14), (fx_ - 14, fy_ + 10)], fill=(30, 36, 50, 255), outline=(255, 214, 60, 255))
        le = A.outline()[len(A.outline()) // 2]; lx, ly = v.to_screen(np.array([le])); lx, ly = float(lx[0]), float(ly[0])
        d2.polygon([(lx - 30 * flap - 6, ly + 6), (lx - 70 * flap, ly + 30 * flap), (lx - 10, ly + 26), (lx + 10, ly + 10)], fill=(30, 36, 50, 255), outline=(255, 214, 60, 255))
    im.alpha_composite(lay2)
    if lift > 0.01:
        Lc = A.lift_coef(alpha) * (1 - 0.75 * min(1, chaos)); c0 = v.to_screen(np.array([complex(-0.5, 0.15)])); c0 = (float(c0[0][0]), float(c0[1][0]))
        K.arrow_glow(im, c0, (c0[0], c0[1] - 380 * Lc * lift), GOLD, w=16, head=50)
    return im, v
# ---------- 0. хук: «Сотни тонн металла. Почему они не падают?»
def s0(lt, D):
    im = K.photo("nasa_sofia_sunset", lt, D, z0=1.0, z1=1.12, fx=0.62, fy=0.5, dx=0.05, cy=660).convert("RGBA"); lay, d = layer()
    a = P(0, lt, 0, 0.2, 0.7)
    if a > 0:
        B.reticle(d, (590, 610), 150, GOLD + (int(220 * a),), u=a, ticks=36, w=2)
        B.leader(d, (470, 560), (400, 450), (90, 450), GOLD + (220,), u=a); B.tracked(d, (245, 418), "БОЛЕЕ 300 ТОНН", 26, GOLD, u=P(0, lt, 0, 0.5, 1.0))
    return fin(im, lay, lt, shake=2.5 * P(0, lt, 1, 0.5, 1.0) + 1.0, k=0.45, streak=0.35)
# ---------- 1. «Ответ: самолёт всё время толкает воздух вниз.»
def s1(lt, D):
    im = K.photo("nasa_sofia_blue", lt, D, z0=1.0, z1=1.08, fx=0.5, fy=0.5, dx=0.04, cy=600).convert("RGBA"); lay, d = layer()
    a = P(1, lt, 0, 0.45, 0.8)
    if a > 0:
        for k in range(9):
            x = 260 + k * 75; ph_ = (lt * 1.4 + k * 0.37) % 1
            for j in range(4):
                y0 = 690 + ((ph_ + j * 0.25) % 1) * 380; al = a * (1 - ((ph_ + j * 0.25) % 1))
                d.line([(x, y0), (x, y0 + 46)], fill=ICE + (int(230 * al),), width=4); d.polygon([(x - 9, y0 + 40), (x + 9, y0 + 40), (x, y0 + 58)], fill=ICE + (int(230 * al),))
        B.tracked(d, (540, 300), "ВОЗДУХ — ВНИЗ", 40, ICE, u=a)
    return fin(im, lay, lt, k=0.45, streak=0.2)
# ---------- 2. «Простым языком.»
def s2(lt, D):
    im = dark(); lay, d = layer(); u = P(2, lt, 0, 0.0, 0.7)
    B.tracked(d, (540, 700), "ПРОСТЫМ ЯЗЫКОМ", 64, WHT, u=u, w="Bold", sp=0.18)
    d.line([(540 - 300 * u, 760), (540 + 300 * u, 760)], fill=GOLD + (230,), width=3)
    return fin(im, lay, lt, shake=0, k=0.7)
# ---------- 3. куб воздуха на весах
def s3(lt, D):
    im = grid_bg(lt); lay, d = layer(); B.tracked(d, (540, 300), "ВОЗДУХ — НЕ ПУСТОТА", 40, ICE, u=P(3, lt, 0, 0.0, 0.6))
    a = P(3, lt, 0, 0.2, 0.9); drop = P(3, lt, 1, 0.45, 0.75)
    cy = 560 + 150 * ease(drop); K.cube(d, (500, cy), 260, u=a, lt=lt)
    d.rounded_rectangle((300, 860, 780, 900), 12, fill=(40, 48, 70, 255), outline=ICE + (200,), width=2); d.rectangle((520, 900, 560, 1000), fill=(40, 48, 70, 255)); d.rounded_rectangle((400, 1000, 680, 1030), 10, fill=(40, 48, 70, 255))
    kg = 1.2 * ease(P(3, lt, 1, 0.65, 1.0))
    d.rounded_rectangle((420, 920, 660, 985), 10, fill=(8, 12, 22, 255), outline=GOLD + (200,), width=2); tx(d, (540, 953), f"{kg:.1f} КГ".replace(".", ","), 44, GOLD, w="Bold")
    tx(d, (540, 1075), "1 м³ воздуха у земли ≈ 1,2 кг", 30, DIM, a=P(3, lt, 1, 0.8, 1.0), w="Medium")
    return fin(im, lay, lt, k=0.7)
# ---------- 4. угол атаки
def s4(lt, D):
    al = math.radians(6) * P(4, lt, 0, 0.2, 0.9); im, v = wing_scene(al, lt, particles=0.6 * P(4, lt, 0, 0.0, 0.4)); lay, d = layer()
    u = P(4, lt, 1, 0.3, 0.8)
    if u > 0:
        te = v.to_screen(np.array([A.outline()[0]])); c = (float(te[0][0]) - 0, float(te[1][0]))
        K.protractor(d, (c[0], c[1]), 230, al, u=u); B.tracked(d, (540, 330), "УГОЛ АТАКИ", 44, GOLD, u=u)
        tx(d, (c[0] - 300, c[1] - 70), f"α = {math.degrees(al):.0f}°", 44, GOLD, a=u)
    return fin(im, lay, lt, k=0.7)
# ---------- 5. поворот потока вниз, крыло вверх
def s5(lt, D):
    al = math.radians(6); lift = P(5, lt, 1, 0.5, 0.95); im, v = wing_scene(al, lt, particles=1.0, lift=lift); lay, d = layer()
    if lt >= T(5, 0, 0.3):
        for k in range(5):
            x = 760 + k * 55; ph_ = (lt * 1.2 + k * 0.2) % 1; y0 = 720 + ph_ * 250
            d.line([(x, y0), (x + 25, y0 + 60)], fill=ICE + (int(220 * (1 - ph_) * P(5, lt, 0, 0.3, 0.7)),), width=4)
        pill(d, (860, 1050), "ПОТОК ВНИЗ", 30, ICE, a=P(5, lt, 0, 0.5, 0.9))
    if lift > 0.3: B.tracked(d, (540, 300), "КРЫЛО — ВВЕРХ", 42, GOLD, u=lift)
    return fin(im, lay, lt, k=0.7)
# ---------- 6. давление
def s6(lt, D):
    al = math.radians(6); pr = max(P(6, lt, 0, 0.0, 0.4), 0.0); im, v = wing_scene(al, lt, pressure=pr, particles=0.8, lift=P(6, lt, 1, 0.3, 0.8)); lay, d = layer()
    pill(d, (300, 380), "НИЗКОЕ ДАВЛЕНИЕ", 30, BLUE, a=P(6, lt, 0, 0.05, 0.3)); pill(d, (300, 980), "ВЫСОКОЕ ДАВЛЕНИЕ", 30, ORNG, a=P(6, lt, 0, 0.5, 0.8))
    if lt >= T(6, 1, 0.3): B.tracked(d, (540, 300), "ПОДЪЁМНАЯ СИЛА", 44, GOLD, u=P(6, lt, 1, 0.3, 0.8))
    return fin(im, lay, lt, k=0.7)
# ---------- 7. миф о «длинном пути»
def s7(lt, D):
    al = math.radians(6); im, v = wing_scene(al, lt, pressure=0.6, particles=0.35); lay, d = layer()
    tr = A.streamlines(al); steps, n = tr.shape
    j_up = int(n * 0.53); j_dn = int(n * 0.47)
    prog = P(7, lt, 0, 0.1, 1.0)
    for j, col in ((j_up, (120, 200, 255)), (j_dn, (255, 160, 80))):
        k = int(prog * (steps - 1)); path = tr[max(0, k - 25):k + 1, j]
        sx, sy = v.to_screen(path)
        if len(sx) > 1: B.glow_polyline(im, list(zip(sx, sy)), col, width=4, blur=6)
        B.dot_glow(im, (float(sx[-1]), float(sy[-1])), 14, col)
    tx(d, (540, 320), "ВЕРХНЯЯ ПРИХОДИТ РАНЬШЕ", 34, ICE, a=P(7, lt, 0, 0.6, 0.9))
    st = P(7, lt, 1, 0.15, 0.3)
    if st > 0:
        sz = int(150 * (1.6 - 0.6 * st)); lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
        d2.rounded_rectangle((540 - sz * 1.4, 860 - sz * 0.55, 540 + sz * 1.4, 860 + sz * 0.55), 20, outline=RED + (int(255 * st),), width=10)
        d2.text((540, 860), "МИФ", font=fnt(sz, "Black"), fill=RED + (int(255 * st),), anchor="mm"); lay2 = lay2.rotate(-8, center=(540, 860)); im.alpha_composite(lay2)
    c = P(7, lt, 1, 0.55, 0.85)
    if c > 0:
        d.rounded_rectangle((120, 990, 960, 1100), 16, fill=(10, 14, 26, int(230 * c)), outline=DIM + (int(200 * c),), width=2)
        tx(d, (540, 1025), "NASA Glenn: «incorrect theory»", 30, WHT, a=c, w="Medium"); tx(d, (540, 1068), "«неверная теория подъёмной силы»", 28, DIM, a=c, w="Medium")
    return fin(im, lay, lt, k=0.7)
# ---------- 8. четыре силы (фото)
def s8(lt, D):
    im = K.photo("nasa_sofia_land", lt, D, z0=1.0, z1=1.06, fx=0.45, fy=0.5, dx=0.03, cy=650).convert("RGBA"); lay, d = layer(); c = (520, 660)
    im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(70 * P(8, lt, 0, 0.0, 0.5)))))
    B.tracked(d, (540, 270), "ЧЕТЫРЕ СИЛЫ", 40, WHT, u=P(8, lt, 0, 0.0, 0.7) * (1 - P(8, lt, 2, 0.4, 0.6)))
    for (k, f0, end, col, label, lp) in ((1, 0.0, (c[0] + 340, c[1]), (120, 220, 140), "ТЯГА", (c[0] + 330, c[1] - 55)), (1, 0.55, (c[0] - 340, c[1]), RED, "СОПРОТИВЛЕНИЕ", (c[0] - 230, c[1] + 55)),
                                          (2, 0.0, (c[0], c[1] + 320), (200, 200, 220), "ВЕС", (c[0] + 100, c[1] + 290)), (2, 0.55, (c[0], c[1] - 300), GOLD, "ПОДЪЁМНАЯ СИЛА", (c[0] + 190, c[1] - 260))):
        u = P(8, lt, k, f0, f0 + 0.3)
        if u > 0: K.arrow_glow(im, c, (c[0] + (end[0] - c[0]) * u, c[1] + (end[1] - c[1]) * u), col, w=14, head=44); pill(d, lp, label, 28, col, a=u)
    return fin(im, lay, lt, k=0.5, streak=0.2)
# ---------- 9. равновесие
def s9(lt, D):
    im = K.photo("nasa_sofia_land", lt + 6, D + 6, z0=1.06, z1=1.1, fx=0.45, fy=0.5, cy=650).convert("RGBA"); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 90))); lay, d = layer(); c = (520, 660)
    u = P(9, lt, 0, 0.1, 0.7); L = 300
    K.arrow_glow(im, c, (c[0], c[1] - L), GOLD, w=14, head=44); K.arrow_glow(im, c, (c[0], c[1] + L), (200, 200, 220), w=14, head=44)
    e = P(9, lt, 1, 0.2, 0.7)
    if e > 0:
        d.rounded_rectangle((150, 1000, 930, 1090), 18, fill=(10, 14, 26, int(220 * e)), outline=GOLD + (int(220 * e),), width=2); tx(d, (540, 1045), "ПОДЪЁМНАЯ СИЛА  =  ВЕС", 40, GOLD, a=e)
    B.tracked(d, (540, 300), "РАВНОВЕСИЕ", 44, WHT, u=u)
    return fin(im, lay, lt, k=0.5, streak=0.2)
# ---------- 10. скорость ×2 → сила ×4
def s10(lt, D):
    sp = 1 + P(10, lt, 0, 0.3, 0.8); im, v = wing_scene(math.radians(5), lt * sp, particles=1.0, cy=560); lay, d = layer()
    tx(d, (300, 920), "СКОРОСТЬ", 30, ICE, a=1); tx(d, (300, 990), f"×{sp:.1f}".replace(".", ","), 64, ICE, a=1)
    lf = sp * sp; tx(d, (780, 920), "ПОДЪЁМНАЯ СИЛА", 30, GOLD, a=1); tx(d, (780, 990), f"×{lf:.1f}".replace(".", ","), 64, GOLD, a=1)
    c0 = (540, 560); K.arrow_glow(im, (c0[0], c0[1] - 20), (c0[0], c0[1] - 20 - 70 * lf), GOLD, w=16, head=48)
    return fin(im, lay, lt, k=0.7)
# ---------- 11. закрылки и предкрылки (фото → схема)
def s11(lt, D):
    sw = P(11, lt, 0, 0.0, 1.0)
    if lt < T(11, 1, 0.0):
        im = K.photo("nasa_dc8_landing", lt, D, z0=1.0, z1=1.1, fx=0.5, fy=0.48, cy=640).convert("RGBA"); lay, d = layer()
        B.tracked(d, (540, 300), "ВЗЛЁТ И ПОСАДКА: МАЛАЯ СКОРОСТЬ", 30, WHT, u=P(11, lt, 0, 0.1, 0.8))
        return fin(im, lay, lt, k=0.45, streak=0.2)
    f = P(11, lt, 1, 0.1, 0.8); A.set_camber(0.09 + 0.07 * f)
    try:
        im, v = wing_scene(math.radians(6), lt, pressure=0.5, particles=1.0, flap=f, lift=1.0)
    finally:
        A.set_camber(0.09)
    lay, d = layer(); pill(d, (790, 960), "ЗАКРЫЛКИ", 32, GOLD, a=P(11, lt, 1, 0.15, 0.45)); pill(d, (270, 960), "ПРЕДКРЫЛКИ", 32, GOLD, a=P(11, lt, 1, 0.6, 0.9))
    return fin(im, lay, lt, k=0.7)
# ---------- 12. сваливание
def s12(lt, D):
    al = math.radians(6 + 14 * P(12, lt, 0, 0.2, 0.9)); ch = P(12, lt, 1, 0.1, 0.6)
    im, v = wing_scene(al, lt, pressure=0.7, particles=1.0, chaos=ch * 1.4, lift=1.0); lay, d = layer()
    te = v.to_screen(np.array([A.outline()[0]])); K.protractor(d, (float(te[0][0]), float(te[1][0])), 200, al, u=1, col=lerp(GOLD, RED, ch) )
    tx(d, (300, 330), f"α = {math.degrees(al):.0f}°", 48, lerp(GOLD, RED, ch))
    if lt >= T(12, 2, 0.0):
        bl = 0.6 + 0.4 * (int(lt * 5) % 2); d.rounded_rectangle((250, 960, 830, 1060), 16, fill=(60, 8, 8, int(220 * bl)), outline=RED + (255,), width=3); tx(d, (540, 1010), "СВАЛИВАНИЕ", 54, (255, 230, 230), a=1, w="Black")
    return fin(im, lay, lt, k=0.7, shake=1.5 + 3 * ch)
# ---------- 13. финал: тот же закат, но виден поток
def s13(lt, D):
    im = K.photo("nasa_sofia_sunset", lt + 4, D + 4, z0=1.08, z1=1.14, fx=0.62, fy=0.5, cy=660).convert("RGBA"); lay, d = layer()
    a = P(13, lt, 1, 0.2, 0.8)
    for k in range(10):
        x = 420 + k * 34; ph_ = (lt * 1.1 + k * 0.29) % 1; y0 = 690 + ph_ * 300
        d.line([(x, y0), (x + 12, y0 + 50)], fill=ICE + (int(220 * a * (1 - ph_)),), width=3)
    B.tracked(d, (540, 300), "ДЕРЖИТ ВОЗДУХ", 44, ICE, u=a)
    return fin(im, lay, lt, k=0.45, streak=0.35)
# ---------- 14. концовка
def s14(lt, D):
    im = K.photo("nasa_sofia_sunset", lt + 9, D + 9, z0=1.14, z1=1.18, fx=0.62, fy=0.5, cy=660).convert("RGBA"); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * P(14, lt, 0, 0.0, 0.4)))))
    lay, d = layer(); b = P(14, lt, 0, 0.1, 0.5); s_ = 1 + 0.04 * math.sin(lt * 6); w_, h_ = 480 * s_, 120 * s_
    if b > 0: d.rounded_rectangle((540 - w_ / 2, 760 - h_ / 2, 540 + w_ / 2, 760 + h_ / 2), 60, fill=(255, 200, 60, int(255 * b))); tx(d, (540, 760), "ОТПРАВЬ", 58, (20, 14, 6), a=b)
    return fin(im, lay, lt, k=0.45)
SCENES = [
    ("Сотни тонн металла. | Почему они не падают?", "SUB", "", s0, "", None),
    ("Ответ: самолёт всё время толкает воздух вниз.", "SUB", "", s1, "", None),
    ("Простым языком.", "SUB", "", s2, "", None),
    ("Воздух — не пустота. | Кубометр воздуха весит больше килограмма.", "SUB", "", s3, "", None),
    ("Крыло идёт чуть наклонно. | Этот наклон называют углом атаки.", "SUB", "", s4, "", None),
    ("Крыло поворачивает поток вниз. | А воздух в ответ толкает крыло вверх.", "SUB", "", s5, "", None),
    ("Сверху давление падает, снизу растёт. | Эта разница и есть подъёмная сила.", "SUB", "", s6, "", None),
    ("Про длинный путь сверху слышал? | Это миф, Н+АСА называет его ошибкой.", "SUB", "", s7, "", None),
    ("Сил всего четыре. | Тяга тянет вперёд, сопротивление — назад. | Вес тянет вниз, подъёмная сила — вверх.", "SUB", "", s8, "", None),
    ("В полёте они уравновешены: | подъёмная сила равна весу.", "SUB", "", s9, "", None),
    ("Скорость вдвое больше — подъёмная сила вчетверо больше.", "SUB", "", s10, "", None),
    ("Поэтому на взлёте, на малой скорости, | крылу помогают закр+ылки и предкр+ылки.", "SUB", "", s11, "", None),
    ("Но слишком крутой наклон опасен: | поток срывается, подъёмная сила пропадает. | Это св+аливание.", "SUB", "", s12, "", None),
    ("Сотни тонн. | А держит их воздух, который крыло толкает вниз.", "SUB", "", s13, "", None),
    ("Отправь тому, кто боится летать. | Подпишись.", "SUB", SUB_PLATE, s14, "", None),
]
def SFX(STARTS, PHRASES, DURS, SR):
    out = []; rng = np.random.default_rng(1)
    def tm(i, k, f=0.0): st, en, _ = PHRASES[i][k]; return STARTS[i] + st + f * (en - st)
    def rumble(dur, a=0.18):
        n = rng.normal(0, 1, int(SR * dur)); x = gaussian_filter1d(n, 40) * 6; t = np.arange(len(x)) / SR
        return a * x * np.minimum(t / 0.6, 1) * np.clip((dur - t) / 0.8, 0, 1)
    def wind(dur, a=0.10):
        n = rng.normal(0, 1, int(SR * dur)); x = gaussian_filter1d(n, 6) * 2.5; t = np.arange(len(x)) / SR
        return a * x * np.sin(np.pi * t / dur) ** 2
    def click(a=0.25): t = np.arange(int(SR * 0.04)) / SR; return a * np.exp(-t * 120) * np.sin(2 * np.pi * 2200 * t)
    def thud(a=0.5): t = np.arange(int(SR * 0.6)) / SR; return a * np.exp(-t * 7) * np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 20)) * t)
    def beep(dur=1.6, a=0.12):
        t = np.arange(int(SR * dur)) / SR; g = (np.floor(t * 6) % 2 == 0); return a * g * np.sin(2 * np.pi * 880 * t)
    out += [(tm(0, 0, 0.0), rumble(DURS[0] + DURS[1], 0.16)), (tm(1, 0, 0.45), wind(1.6))]
    out += [(tm(2, 0, 0.0), click(0.35)), (tm(3, 1, 0.7), thud(0.35)), (tm(4, 1, 0.3), click()), (tm(5, 1, 0.5), wind(1.2, 0.08))]
    out += [(tm(7, 1, 0.15), thud(0.6)), (tm(9, 1, 0.2), click()), (tm(12, 1, 0.1), wind(1.8, 0.14)), (tm(12, 2, 0.0), beep())]
    out += [(tm(13, 0, 0.0), rumble(DURS[13], 0.12)), (tm(14, 0, 0.1), click(0.25))]
    for i, k_ in ((8, 1), (8, 2)):
        out += [(tm(i, k_, 0.0), click(0.2)), (tm(i, k_, 0.55), click(0.2))]
    return out
