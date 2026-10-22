"""«Место без возврата» — чёрная дыра, тревожная документалка. Вся графика нарисована кодом и привязана к словам озвучки (PHRASES движка).
Факты: ОТО (горизонт событий, замедление времени со стороны наблюдателя, приливные силы), Стрелец A* ≈ 4 млн масс Солнца, ≈ 26 тыс. св. лет (EHT, 12.05.2022),
M87* ≈ 6,5 млрд масс Солнца, ≈ 54 млн св. лет (EHT, 10.04.2019). Сценарий: scripts/blackhole_2.md, визуал: scripts/blackhole_2_visual.md."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import bh_cine as B
from bh_cine import W, H, ease, seg, lerp, fnt
HEAD = ("ЧЁРНАЯ ДЫРА", "ЧТО СКРЫВАЕТ КОСМОС")
TITLE = ("", "", "")
HOOK = ("МЕСТО\nБЕЗ ВОЗВРАТА", 2.4)
HOOK_Y = 1000
MUSIC = ("music/ogv_aria.mp3", 0)
AA = 0.35
TAIL = 0.3; XF = 0.4; LEAD_N = 0.25; GAP = 0.3
RED = (255, 70, 60); GOLD = (255, 205, 110); ICE = (170, 205, 255); WHT = (240, 244, 255); DIM = (110, 130, 175)
def ph(i, k):
    import __main__ as E
    return E.PHRASES[i][k]
def T(i, k, f=0.0): st, en, _ = ph(i, k); return st + f * (en - st)
def P(i, lt, k, f0=0.0, f1=1.0): return seg(lt, T(i, k, f0), T(i, k, f1))
def layer(): lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)
def done(base, lay, lt, shake=2.0, streak=0.5, ca=2):
    base = base.convert("RGBA"); base.alpha_composite(lay); return B.finish_c(base, shake=shake, lt=lt, streak=streak, ca=ca)
def tx(d, xy, s, size, col=WHT, a=1.0, w="Bold", anchor="mm"):
    if a < 0.03: return
    d.text(xy, s, font=fnt(size, w), fill=lerp((5, 7, 15), col, min(a, 1.0)), anchor=anchor)
def trail(base, pts, col, width=5, a=1.0):
    if len(pts) > 1: B.glow_polyline(base, pts, col, width=width, blur=7, a=a)
def spiral_pos(c, R0, R1, th0, th1, p, sq=0.42):
    R = R0 + (R1 - R0) * p; th = th0 + (th1 - th0) * p; return (c[0] + R * math.cos(th), c[1] + R * math.sin(th) * sq)
# ---------- 1: «Есть место без возврата. Узнаешь, что там с упавшим.»
def s1(lt, D):
    S = 55 + 215 * ease(lt / D * 1.05); c = (540, 620)
    im = B.bh_frame(c[0], c[1], S, t=lt, exposure=0.35 + 0.3 * seg(lt, 0.2, 1.6), incl=83, drift=lt).convert("RGBA")
    lay, d = layer()
    ra = P(0, lt, 0, 0.7, 1.0)
    if ra > 0: B.reticle(d, c, S * 1.22, RED + (int(230 * ra),), u=ra, ticks=48, w=3)
    p = P(0, lt, 1, 0.45, 1.0)
    if p > 0:
        pts = [spiral_pos(c, 640, 330, -2.6, -0.7, max(0, p - 0.0 - k * 0.025)) for k in range(14)][::-1]
        trail(im, pts, (255, 255, 255), width=4, a=0.8); B.dot_glow(im, pts[-1], 9, (255, 255, 255))
        B.leader(d, (pts[-1][0] + 14, pts[-1][1]), (pts[-1][0] + 80, pts[-1][1] - 60), (pts[-1][0] + 300, pts[-1][1] - 60), ICE + (200,), u=seg(p, 0.1, 0.6))
        B.tracked(d, (pts[-1][0] + 310, pts[-1][1] - 60), "ОБЪЕКТ", 30, ICE, u=seg(p, 0.4, 0.9), anchor="l") if False else None
        tx(d, (pts[-1][0] + 190, pts[-1][1] - 90), "ОБЪЕКТ", 28, ICE, a=seg(p, 0.3, 0.7), w="Medium")
    return done(im, lay, lt, shake=3.0)
# ---------- 2: «Это чёрная дыра. Её граница — горизонт событий. Свет оттуда не уходит.»
def s2(lt, D):
    c = (540, 730); S = 205 + 14 * (lt / D)
    im = B.bh_frame(c[0], c[1], S, t=lt + 4, incl=82, exposure=0.6, drift=lt).convert("RGBA"); lay, d = layer()
    B.tracked(d, (540, 290), "ЧЁРНАЯ ДЫРА", 60, WHT, u=P(1, lt, 0, 0.4, 0.95), w="Bold", sp=0.22)
    u = P(1, lt, 1, 0.15, 0.6)
    if u > 0:
        B.reticle(d, c, S * 1.0, RED + (255,), u=u, ticks=72, w=3)
        p0 = (c[0], c[1] + S); B.leader(d, p0, (c[0], c[1] + S + 40), (c[0], c[1] + S + 40), RED + (230,), u=seg(u, 0.4, 1.0))
        B.tracked(d, (540, c[1] + S + 75), "ГОРИЗОНТ СОБЫТИЙ", 30, RED, u=P(1, lt, 1, 0.5, 0.9))
    k = P(1, lt, 2, 0.1, 0.8)
    if k > 0:
        a = [(110, 340)]; pts = []
        for i in range(0, int(60 * k) + 1):
            t = i / 60; pts.append(((1 - t) ** 2 * 60 + 2 * (1 - t) * t * 540 + t * t * 1020, (1 - t) ** 2 * 560 + 2 * (1 - t) * t * 330 + t * t * 560))
        trail(im, pts, (255, 250, 225), width=5); B.dot_glow(im, pts[-1], 10, (255, 255, 255))
        pts2 = [spiral_pos(c, S * 0.96 - 0.5 * S * (i / 60), 0, 0.2, 0.2 + 5.5 * (i / 60), 1.0, 0.25) for i in range(0)]
        q = []
        for i in range(0, int(70 * k) + 1):
            t = i / 70; R = S * 0.92 * (1 - 0.0) * (1 + 0.12 * math.sin(t * 6)); ang = -0.3 + 4.2 * t
            q.append((c[0] + (S * 0.6 + 0.4 * S * (1 - t)) * math.cos(ang) * (0.95 - 0.1 * t) * 0.9 + S * 0.35 * (1 - t) * 0, c[1] + (S * 0.6 + 0.4 * S * (1 - t)) * math.sin(ang) * 0.4 * (0.95 - 0.1 * t)))
        trail(im, q, (255, 120, 80), width=5, a=0.9); B.dot_glow(im, q[-1], 9, (255, 190, 140))
        tx(d, (540, 1075), "СВЕТ НЕ ВЫХОДИТ", 32, ICE, a=P(1, lt, 2, 0.5, 0.9), w="Medium")
    return done(im, lay, lt)
# ---------- 3: «Но быстрее света ничего нет. Поэтому не вернётся ничто.»
def s3(lt, D):
    c = (540, 850); S = 135
    im = B.bh_frame(c[0], c[1], S, t=lt + 9, incl=81, exposure=0.55, drift=lt, stars=0.7).convert("RGBA"); lay, d = layer()
    u = P(2, lt, 0, 0.0, 0.85)
    B.tracked(d, (540, 290), "ПРЕДЕЛ СКОРОСТИ", 36, ICE, u=P(2, lt, 0, 0.0, 0.5))
    v = int(299792 * ease(u)); tx(d, (540, 380), f"{v:,}".replace(",", " ") + " КМ/С", 78, GOLD, a=seg(u, 0.02, 0.2))
    rng = np.random.default_rng(4)
    for i in range(34):
        y = 470 + (i * 37) % 260 + rng.integers(0, 12); sp = 0.4 + (i % 7) * 0.2; x0 = (lt * 900 * sp * (0.2 + 1.8 * ease(u)) + i * 173) % 1500 - 200
        L = 40 + 360 * ease(u) * sp; d.line([(x0 - L, y), (x0, y)], fill=ICE + (int(70 + 140 * sp / 1.6),), width=3)
    xe = 985; d.line([(xe, 450), (xe, 750)], fill=RED + (255,), width=4); tx(d, (xe - 6, 430), "ПРЕДЕЛ", 28, RED, a=seg(u, 0.1, 0.4), w="Medium")
    if u >= 1: fl = math.exp(-(lt - T(2, 0, 0.85)) * 6); d.rectangle((xe - 18, 450, xe + 18, 750), fill=RED + (int(200 * fl),))
    n = P(2, lt, 1, 0.05, 0.95)
    for j in range(7):
        pr = seg(n, j * 0.1, j * 0.1 + 0.55)
        if 0 < pr < 1:
            ang = math.pi * (0.15 + j * 0.31); start = (c[0] + 520 * math.cos(ang), c[1] - 180 + 330 * math.sin(ang) * 0.6 - 120)
            tail = [(start[0] + (c[0] - start[0]) * max(0, pr - 0.06 * k_), start[1] + (c[1] - start[1]) * max(0, pr - 0.06 * k_)) for k_ in range(8)][::-1]
            trail(im, tail, (255, 255, 255), width=3, a=1 - pr * 0.7); B.dot_glow(im, tail[-1], 6, (255, 255, 255), a=1 - pr * 0.6)
    if lt >= T(2, 1, 0.0): tx(d, (540, 1040), "ВЕРНУЛОСЬ: 0", 56, GOLD, a=P(2, lt, 1, 0.0, 0.3))
    return done(im, lay, lt)
# ---------- 4: часы
def dial(d, c, r, tick, col, label, f=0.0, big=True):
    for rr, w, a in ((r + 14, 2, 90), (r, 6, 255), (r - 20, 1, 80)): d.ellipse((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), outline=col + (a,), width=w)
    for k in range(60):
        a = k * math.pi / 30; l = 16 if k % 5 == 0 else 6; d.line([(c[0] + (r - 6) * math.sin(a), c[1] - (r - 6) * math.cos(a)), (c[0] + (r - 6 - l) * math.sin(a), c[1] - (r - 6 - l) * math.cos(a))], fill=col + (255 if k % 5 == 0 else 140,), width=3 if k % 5 == 0 else 2)
    a = (tick + f) * math.pi / 6; d.line([c, (c[0] + (r - 34) * math.sin(a), c[1] - (r - 34) * math.cos(a))], fill=col + (255,), width=7); d.ellipse((c[0] - 9, c[1] - 9, c[0] + 9, c[1] + 9), fill=col + (255,))
    tx(d, (c[0], c[1] - r - 46), label, 34, col, w="Bold"); tx(d, (c[0], c[1] + r + 62), f"{tick} с", 74, col, w="Bold")
def s4(lt, D):
    bh = (540, 520); S = 78
    im = B.bh_frame(bh[0], bh[1], S, t=lt + 2, incl=82, exposure=0.55, drift=lt, stars=0.7).convert("RGBA"); lay, d = layer()
    prog = seg(lt, T(3, 0, 0.3), T(3, 3, 1.0)); y = 300 + 175 * (1 - (1 - prog) ** 2.2)
    col = lerp((255, 255, 255), (255, 60, 40), prog)
    pts = [(540 + 18 * math.sin(i * 0.3), y - 14 * i * (0.6 + prog)) for i in range(10)][::-1]
    pts = [p_ for p_ in pts if p_[1] > 270]; trail(im, pts, col, width=3, a=0.7) if len(pts) > 1 else None
    B.dot_glow(im, (540, y), 9, col); tx(d, (630, y), "ТЫ", 32, col, a=P(3, lt, 0, 0.3, 0.6), w="Medium")
    if lt >= T(3, 1, 0.0):
        t1 = int((lt - T(3, 1, 0.05)) / 0.8) + 1 if lt >= T(3, 1, 0.05) else 0; dial(d, (300, 770), 135, t1, GOLD, "У ТЕБЯ")
    if lt >= T(3, 2, 0.0):
        marks = [T(3, 2, 0.1), T(3, 2, 0.1) + 1.0, T(3, 2, 0.1) + 2.2, T(3, 2, 0.1) + 4.0]; t2 = sum(1 for m in marks if lt >= m); stop = lt >= T(3, 3, 0.45)
        dial(d, (780, 770), 135, t2, RED, "СНАРУЖИ")
        if stop: tx(d, (780, 1040), "ПОЧТИ СТОП", 50, RED, a=0.5 + 0.5 * (int(lt * 4) % 2), w="Bold")
        tx(d, (780, 1095), "со стороны наблюдателя", 28, DIM, a=P(3, lt, 2, 0.2, 0.6), w="Medium")
    return done(im, lay, lt)
# ---------- 5: приливные силы (частицы)
def s5(lt, D):
    bh = (540, 400); S = 90
    im = B.bh_frame(bh[0], bh[1], S, t=lt + 5, incl=82, exposure=0.55, drift=lt, stars=0.7).convert("RGBA"); lay, d = layer()
    fl = 0.7 * math.exp(-(lt - T(4, 0, 0.0)) * 5) if lt >= T(4, 0, 0.0) else 0
    s = seg(lt, T(4, 1, 0.1), T(4, 2, 0.95)); mv = seg(lt, T(4, 0, 0.5), T(4, 2, 1.0))
    cols_, rows_ = 7, 14; cy0 = 800 - 110 * mv
    for j in range(rows_):
        fj = j / (rows_ - 1)
        for i in range(cols_):
            x0 = (i - (cols_ - 1) / 2) * 24; y0 = (j - (rows_ - 1) / 2) * 24
            st = s * (1.0 + 1.6 * (1 - fj)); x = 540 + x0 * (1 - 0.8 * min(s, 1)); y = min(1040, cy0 + y0 * (1 + 2.6 * st) - 40 * st * (1 - fj))
            c_ = lerp((255, 255, 255), (255, 80, 50), min(1, s * 1.1))
            L = 4 + 22 * s * (1 - fj); d.line([(x, y), (x, y + L)], fill=c_ + (150,), width=4); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=c_ + (255,))
    k = P(4, lt, 1, 0.3, 0.9)
    if k > 0:
        d.line([(760, cy0 + 150), (760, cy0 + 150 + 130 * k)], fill=RED + (255,), width=6); tx(d, (860, cy0 + 280), "СИЛЬНО", 30, RED, a=k, w="Bold")
        d.line([(760, cy0 - 150), (760, cy0 - 150 + 40 * k)], fill=GOLD + (255,), width=6); tx(d, (860, cy0 - 120), "СЛАБЕЕ", 30, GOLD, a=k, w="Bold")
    B.tracked(d, (540, 540), "ПРИЛИВНЫЕ СИЛЫ", 32, RED, u=P(4, lt, 1, 0.2, 0.6) * (1 - P(4, lt, 2, 0.0, 0.25)))
    B.tracked(d, (540, 540), "СПАГЕТТИФИКАЦИЯ", 36, GOLD, u=P(4, lt, 2, 0.2, 0.6))
    out = done(im, lay, lt)
    if fl > 0.02: out.alpha_composite(Image.new("RGBA", (W, H), RED + (int(120 * fl),)))
    return out
# ---------- 6: центр Галактики
def s6(lt, D):
    zoom = 0.55 + 1.7 * ease(lt / D) ** 1.3; c = (540, 600)
    im = B.galaxy_layer(zoom, lt * 3.0, cx=c[0], cy=c[1])
    bg = B.bh_frame(540, 5000, 40, t=lt, stars=1.0).convert("RGB"); im = ImageChops.add(im, bg.point(lambda v: int(v * 0.9))).convert("RGBA")
    lay, d = layer(); B.tracked(d, (540, 300), "ЦЕНТР МЛЕЧНОГО ПУТИ", 36, ICE, u=P(5, lt, 0, 0.1, 0.9))
    q = seg(lt, T(5, 0, 0.4), T(5, 0, 1.0)); cx_, cy_ = c
    B.reticle(d, (cx_, cy_), 36 + 6 * math.sin(lt * 4), GOLD + (230,), u=q, ticks=24, w=2)
    B.leader(d, (cx_ + 30, cy_ - 26), (cx_ + 100, cy_ - 110), (cx_ + 360, cy_ - 110), GOLD + (230,), u=q); B.tracked(d, (cx_ + 115, cy_ - 140), "СТРЕЛЕЦ A*", 28, GOLD, u=q, anchor="l")
    n = P(5, lt, 1, 0.05, 0.65); cnt = int(4_000_000 * ease(n)); rng = np.random.default_rng(6)
    for j in range(int(40 * n)):
        a = rng.uniform(0, 2 * math.pi); r_ = 60 + rng.uniform(0, 120); d.ellipse((cx_ + r_ * math.cos(a) - 3, cy_ + r_ * math.sin(a) * 0.5 - 3, cx_ + r_ * math.cos(a) + 3, cy_ + r_ * math.sin(a) * 0.5 + 3), fill=GOLD + (255,))
    if lt >= T(5, 1, 0.02): tx(d, (540, 940), f"{cnt:,}".replace(",", " ") + " СОЛНЦ", 66, GOLD)
    k = P(5, lt, 2, 0.05, 0.7)
    if k > 0:
        d.line([(160, 1040), (160 + 760 * k, 1040)], fill=ICE + (230,), width=3); d.ellipse((150, 1030, 170, 1050), fill=(80, 150, 255, 255))
        B.dot_glow(lay, (160 + 760 * k, 1040), 8, (255, 255, 255)); tx(d, (540, 995), f"{int(26000 * ease(k)):,}".replace(",", " ") + " СВЕТОВЫХ ЛЕТ", 44, WHT)
        tx(d, (160, 1075), "ЗЕМЛЯ", 24, DIM, w="Medium", anchor="lm"); tx(d, (920, 1075), "ЦЕНТР", 24, DIM, w="Medium", anchor="rm")
    return done(im, lay, lt, shake=1.5)
# ---------- 7: M87* и «первый снимок»
def s7(lt, D):
    a = P(6, lt, 0, 0.0, 1.0); p = P(6, lt, 1, 0.05, 0.9)
    big = 30 + 175 * ease(a); c = (610, 720)
    im = B.bh_frame(c[0], c[1], big, t=lt + 3, incl=80, exposure=0.55, drift=lt, stars=0.8)
    sm = B.bh_frame(150, 930, 22, t=lt, incl=82, exposure=0.6, stars=0.0); im = ImageChops.add(im, sm).convert("RGBA"); lay, d = layer()
    B.tracked(d, (150, 990), "СТРЕЛЕЦ A*", 22, ICE, u=seg(a, 0.3, 0.8) * (1 - min(1, p * 4))); B.tracked(d, (610, 290), "M87*", 40, GOLD, u=seg(a, 0.2, 0.7) * (1 - min(1, p * 4)))
    if a > 0.4: tx(d, (610, 345), f"{int(6_500_000_000 * ease(a)):,}".replace(",", " ") + " СОЛНЦ", 38, GOLD, a=seg(a, 0.4, 0.6) * (1 - min(1, p * 4)))
    if p > 0:
        im.alpha_composite(Image.new("RGBA", (W, H), (3, 4, 10, int(255 * min(1, p * 2.2)))))
        ring = B.eht_ring(370, u=min(1, p * 1.5), cx=540, cy=650).convert("RGBA"); ring.putalpha(Image.new("L", (W, H), 255)); im = ImageChops.add(im.convert("RGB"), ring.convert("RGB")).convert("RGBA")
        for (x0, y0, sx, sy) in ((130, 250, 1, 1), (950, 250, -1, 1), (130, 960, 1, -1), (950, 960, -1, -1)):
            d.line([(x0, y0), (x0 + sx * 50, y0)], fill=ICE + (230,), width=3); d.line([(x0, y0), (x0, y0 + sy * 50)], fill=ICE + (230,), width=3)
        B.tracked(d, (540, 262), "2019 · ПЕРВЫЙ СНИМОК", 30, GOLD, u=p); tx(d, (540, 1010), "СХЕМА, НЕ ФОТО", 26, DIM, a=p, w="Medium")
    return done(im, lay, lt, shake=1.5)
# ---------- 8: формулы ломаются
def s8(lt, D):
    rng = np.random.default_rng(int(lt * 24)); im = B.bh_frame(540, 5000, 60, t=lt, stars=1.0).convert("RGBA"); lay, d = layer()
    br = P(7, lt, 0, 0.3, 1.0); forms = ["r → 0", "ρ → ∞", "G = 8πT", "ds² = ?", "1 / 0"]
    for j, f in enumerate(forms):
        y = 380 + j * 110; x = 540 + (rng.normal(0, 40) * br if br > 0.05 else 0); y += rng.normal(0, 12) * br
        txt = f if rng.random() > br * 0.55 else "".join(rng.choice(list("#?@%&§Ж")) for _ in f)
        tx(d, (x, y), txt, 64, lerp(ICE, RED, br), w="Light")
    for k in range(int(10 * br)):
        yy = int(rng.integers(300, 1000)); h = int(rng.integers(6, 40)); sh = int(rng.integers(-60, 60)); d.rectangle((0, yy, W, yy + h), fill=(255, 60, 50, int(rng.integers(20, 70))))
    if br > 0.6: B.tracked(d, (540, 930), "СИНГУЛЯРНОСТЬ: ФОРМУЛЫ НЕ РАБОТАЮТ", 26, RED, u=P(7, lt, 0, 0.6, 0.95))
    q = P(7, lt, 1, 0.45, 0.95)
    if q > 0:
        d.rectangle((0, 250, W, 1100), fill=(3, 4, 10, int(235 * q))); tx(d, (540, 620), "?", int(280 * q + 60), RED, w="Black")
        B.tracked(d, (540, 900), "ИНФОРМАЦИЯ: НЕ РЕШЕНО", 34, WHT, u=q)
    out = done(im, lay, lt, shake=2.5, ca=4 if br > 0.3 else 2)
    return out
# ---------- 9: финал
def s9(lt, D):
    c = (540, 560); S = 235
    im = B.bh_frame(c[0], c[1], S, t=lt + 6, incl=82, exposure=0.55, drift=lt).convert("RGBA"); lay, d = layer()
    m = P(8, lt, 0, 0.1, 0.9)
    if m > 0:
        col = lerp(WHT, (70, 80, 100), seg(lt, T(8, 0, 0.6), T(8, 0, 0.9))); tx(d, (540, 900), "МОНСТР", 78, col, w="Black"); d.line([(340, 900), (340 + 400 * P(8, lt, 0, 0.6, 0.9), 900)], fill=RED + (255,), width=8)
    o = P(8, lt, 1, 0.2, 0.7)
    if o > 0: tx(d, (540, 1010), "ОТВЕТ", int(40 + 56 * o), lerp((60, 70, 90), GOLD, o), w="Black")
    b = P(8, lt, 2, 0.2, 0.6)
    if b > 0:
        d.rectangle((0, 250, W, 1100), fill=(3, 4, 10, int(235 * b))); s_ = 1 + 0.04 * math.sin(lt * 6); w_, h_ = 470 * s_, 120 * s_
        d.rounded_rectangle((540 - w_ / 2, 760 - h_ / 2, 540 + w_ / 2, 760 + h_ / 2), 60, fill=(255, 190, 60, 255)); tx(d, (540, 760), "ОТПРАВЬ", 58, (20, 14, 6), w="Bold")
    return done(im, lay, lt)
SCENES = [
    ("Есть место без возврата. | Узнаешь, что там с упавшим.", "SUB", "", s1, "", None),
    ("Это чёрная дыра. | Её граница — горизонт соб+ытий. | Свет оттуда не уходит.", "SUB", "ГОРИЗОНТ СОБЫТИЙ", s2, "", None),
    ("Но быстрее света ничего нет. | Поэтому не вернётся ничто.", "SUB", "ПРЕДЕЛ СКОРОСТИ", s3, "", None),
    ("Ты падаешь. | Твои часы идут как обычно. | Но снаружи они замедляются. | У границы — почти стоят.", "SUB", "ВРЕМЯ", s4, "", None),
    ("А теперь хуже. | Ноги тянет сильнее, чем голову. | Тело — в нить.", "SUB", "ПРИЛИВНЫЕ СИЛЫ", s5, "", None),
    ("В центре нашей Галактики — одна. | Четыре миллиона Солнц. | Двадцать шесть тысяч световых лет.", "SUB", "СТРЕЛЕЦ А*", s6, "", None),
    ("Другая — больше шести миллиардов Солнц. | Её сфотографировали.", "SUB", "M87*", s7, "", None),
    ("Но в центре наши формулы ломаются. | А что с информацией упавшего? Не знает никто.", "SUB", "СИНГУЛЯРНОСТЬ", s8, "", None),
    ("Космос скрывает не монстра. | Он скрывает ответ. | Отправь тому, кто думает, что дыра всасывает всё. | Подпишись.", "SUB", SUB_PLATE, s9, "", None),
]
# ---------- звук кодом: гул, удары, тики, свисты (привязаны к фразам)
def SFX(STARTS, PHRASES, DURS, SR):
    out = []; rr = np.random.default_rng(1)
    def tm(i, k, f=0.0): st, en, _ = PHRASES[i][k]; return STARTS[i] + st + f * (en - st)
    def boom(a=0.5, f0=60, dur=1.2): t = np.arange(int(SR * dur)) / SR; return a * np.exp(-t * 3.2) * np.sin(2 * np.pi * (f0 + 70 * np.exp(-t * 14)) * t)
    def tick(a=0.22): t = np.arange(int(SR * 0.05)) / SR; return a * np.exp(-t * 90) * np.sin(2 * np.pi * 1800 * t)
    def tone(f, dur, a=0.12): t = np.arange(int(SR * dur)) / SR; return a * np.sin(2 * np.pi * f * t) * np.minimum(t / 0.2, 1) * np.clip((dur - t) / 0.4, 0, 1)
    def whoosh(dur=0.7, a=0.12): n = rr.normal(0, 1, int(SR * dur)); t = np.arange(len(n)) / SR; return a * n * np.sin(np.pi * t / dur) ** 2 * 0.4
    def glitch(dur=0.5, a=0.18): n = rr.normal(0, 1, int(SR * dur)); g = (np.sin(2 * np.pi * 22 * np.arange(len(n)) / SR) > 0.3); return a * n * g * 0.4
    out += [(tm(0, 0, 0.4), boom(0.55)), (tm(0, 0, 0.85), tone(110, 1.6, 0.1)), (tm(0, 1, 0.75), tick(0.2))]
    out += [(tm(1, 0, 0.5), whoosh(0.9)), (tm(1, 1, 0.55), tick(0.35)), (tm(1, 2, 0.5), whoosh(0.8, 0.12))]
    out += [(tm(2, 0, 0.85), boom(0.4, 90, 0.5)), (tm(2, 1, 0.1), tone(70, 2.0, 0.1))]
    for f in (0.1, 0.5, 0.9): out.append((tm(3, 1, f), tick()))
    for f in (0.1, 0.8): out.append((tm(3, 2, f), tick(0.18)))
    out += [(tm(3, 3, 0.3), tone(165, 2.0, 0.12))]
    out += [(tm(4, 0, 0.0), boom(0.7, 50, 1.0)), (tm(4, 2, 0.1), whoosh(1.2, 0.14))]
    out += [(tm(5, 0, 0.3), whoosh(1.0, 0.1)), (tm(5, 2, 0.1), tone(130, 2.5, 0.09))]
    out += [(tm(6, 1, 0.05), tick(0.4)), (tm(6, 0, 0.5), tone(98, 2.0, 0.1))]
    out += [(tm(7, 0, 0.5), glitch(0.9)), (tm(7, 1, 0.5), tone(147, 3.0, 0.12))]
    out += [(tm(8, 0, 0.0), boom(0.45, 55, 1.2)), (tm(8, 2, 0.2), tick(0.25))]
    return out
