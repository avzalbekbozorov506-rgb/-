"""«Выдернуть роутер на ночь?» — аналог по формату референса пользователя (идея: изометрия + HUD + главы), свой сценарий и своя графика кодом.
Факты и источники: scripts/wifi_1.md (ВОЗ, ICNIRP 2020, ETSI EN 300 328, NIST). Графика: configs/iso_kit.py. Фото не используются."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter1d
import bh_cine as B, iso_kit as I_
from bh_cine import W, H, ease, seg, lerp, fnt
HEAD = ("ПРОСТЫМ ЯЗЫКОМ", "ВРЕДЕН ЛИ WI-FI")
TITLE = ("", "", "")
HOOK = ("ВЫДЕРНУТЬ РОУТЕР\nНА НОЧЬ?", 2.0)
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
def fin(base, lay=None, lt=0.0, shake=1.0, k=0.6, streak=0.06, ca=2):
    base = base.convert("RGBA")
    if lay is not None: base.alpha_composite(lay)
    return B.finish_c(base, k=k, streak=streak, shake=shake, lt=lt, ca=ca)
def tx(d, xy, s, size, col=WHT, a=1.0, w="Bold", anchor="mm"):
    if a < 0.03: return
    d.text(xy, s, font=fnt(size, w), fill=col + (int(255 * min(a, 1)),), anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0, int(140 * min(a, 1))))
def pill(d, xy, s, size, col, a=1.0, w="Bold"):
    size = max(size, 34)
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
def chap(d, n, title, u=1.0):
    tx(d, (170, 300), f"{n} / 06", 34, GOLD, a=u, w="Bold"); tx(d, (540, 300), title, 38, WHT, a=u, w="Bold")
    d.line([(90, 335), (990, 335)], fill=NEON + (int(120 * u),), width=2)
def corners(d, a=0.5):
    for (x, y, sx, sy) in ((60, 380, 1, 1), (1020, 380, -1, 1), (60, 1120, 1, -1), (1020, 1120, -1, -1)):
        d.line([(x, y), (x + 44 * sx, y)], fill=NEON + (int(200 * a),), width=3); d.line([(x, y), (x, y + 44 * sy)], fill=NEON + (int(200 * a),), width=3)
def iso(S=78, cy=700): return I_.Iso(S=S, cx=540, cy=cy)
def photons(im, I, lt, n=14, a=1.0, speed=1.6, col=(255, 255, 255), size=9, z=I_.RZ):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rng = np.random.default_rng(5)
    for k in range(n):
        ang = rng.uniform(0, 2 * math.pi); ph_ = (lt * speed * 0.3 + rng.uniform(0, 1)) % 1; r = ph_ * 5.5
        x, y = I.p(I_.RX + r * math.cos(ang), I_.RY + r * math.sin(ang), z); al = a * (1 - ph_) ** 0.8
        d.ellipse((x - size, y - size, x + size, y + size), fill=col + (int(255 * al),))
    g = lay.filter(ImageFilter.GaussianBlur(8)); im.alpha_composite(g); im.alpha_composite(lay)
# ---------- 0. хук: роутер и вилка
def s0(lt, D):
    I = iso(82, 690); u = P(0, lt, 0, 0.55, 1.0); im, sock, ce = I_.room(lt, I, plug=1 - 0.85 * u); lay, d = layer()
    a = P(0, lt, 0, 0.15, 0.6)
    if a > 0:
        rp = I.p(I_.RX + 0.2, I_.RY + 0.2, I_.RZ); B.reticle(d, rp, 120, RED + (int(230 * a),), u=a, ticks=36, w=3)
        B.leader(d, (rp[0] + 80, rp[1] - 80), (rp[0] + 150, rp[1] - 260), (900, rp[1] - 260), RED + (230,), u=a); B.tracked(d, (760, rp[1] - 300), "РОУТЕР ВКЛЮЧЁН 24/7", 26, RED, u=P(0, lt, 0, 0.4, 1.0))
    if u > 0.2:
        for k in range(8):
            ang = k * 0.8 + lt * 7; d.line([ce, (ce[0] + 36 * math.cos(ang) * u, ce[1] + 36 * math.sin(ang) * u)], fill=RED + (int(220 * u),), width=3)
    corners(d, 0.5)
    return fin(im, lay, lt, shake=1.0, k=0.55)
# ---------- 1. «Давай проверим расчётом»
def s1(lt, D):
    zoom = 82 + 14 * seg(lt, 0, D); I = iso(zoom, 700); im, sock, ce = I_.room(lt, I); lay, d = layer(); a = P(1, lt, 0, 0.0, 0.7)
    chap(d, "01", "ВОПРОС", a)
    y = 380 + 700 * ((lt * 0.9) % 1); d.line([(60, y), (1020, y)], fill=NEON + (140,), width=3)
    B.tracked(d, (540, 1080), "ПРОВЕРИМ РАСЧЁТОМ", 40, NEON, u=P(1, lt, 0, 0.2, 0.9)); corners(d, 0.5)
    return fin(im, lay, lt, k=0.55)
# ---------- 2. радиостанция, волны, частота
def s2(lt, D):
    I = iso(96, 700); im, sock, ce = I_.room(lt, I, wall_a=110); lay, d = layer()
    gr = P(2, lt, 0, 0.0, 0.9); I_.rings(im, I, lt * 0.9, a=min(1.0, gr * 1.3) )
    chap(d, "02", "ЧТО ЭТО ЗА ВОЛНА", P(2, lt, 0, 0.0, 0.3))
    c = P(2, lt, 2, 0.2, 0.9)
    if c > 0:
        n = int(2_400_000_000 * ease(c)); d.rounded_rectangle((90, 980, 990, 1070), 16, fill=(8, 14, 28, int(225 * c)), outline=NEON + (int(220 * c),), width=2)
        tx(d, (540, 1008), "КОЛЕБАНИЙ В СЕКУНДУ", 26, DIM, a=c, w="Medium"); tx(d, (540, 1045), f"≈ {n:,}".replace(",", " "), 44, NEON, a=c)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 3. поток частиц света
def s3(lt, D):
    I = iso(96, 700); im, sock, ce = I_.room(lt, I, wall_a=100, dim=0.8); lay, d = layer()
    I_.rings(im, I, lt * 0.9, a=max(0.0, 1 - P(3, lt, 0, 0.1, 0.5)) * 0.9)
    photons(im, I, lt, n=18, a=P(3, lt, 0, 0.15, 0.6))
    chap(d, "02", "ЧТО ЭТО ЗА ВОЛНА", 1.0)
    e = P(3, lt, 0, 0.4, 1.0)
    if e > 0:
        d.rounded_rectangle((250, 1000, 830, 1090), 16, fill=(8, 14, 28, int(225 * e)), outline=GOLD + (int(230 * e),), width=2); tx(d, (540, 1045), "E = h · f", 56, GOLD, a=e)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 4. спектр: рентген рвёт молекулу
def molecule(d, c, u, broken):
    ox, oy = c
    h1 = (ox - 70 - 50 * broken, oy + 55 + 30 * broken); h2 = (ox + 70 + 50 * broken, oy + 55 + 30 * broken)
    col = (255, 80, 60) if broken > 0.1 else (150, 200, 255)
    for h in (h1, h2): d.line([(ox, oy), h], fill=col + (int(255 * u * (1 - 0.5 * broken)),), width=8)
    for h in (h1, h2): d.ellipse((h[0] - 22, h[1] - 22, h[0] + 22, h[1] + 22), fill=(230, 236, 255, int(255 * u)))
    d.ellipse((ox - 40, oy - 40, ox + 40, oy + 40), fill=(255, 90, 80, int(255 * u)))
def s4(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "03", "МИКРОМИР", P(4, lt, 0, 0.0, 0.3)); u = P(4, lt, 0, 0.1, 0.5)
    x0, x1, y = 90, 990, 470
    for i in range(900): t = i / 900; col = lerp(lerp((60, 230, 200), (255, 240, 120), t * 2), (255, 70, 120), max(0, t * 2 - 1)) if t > 0.5 else lerp((60, 230, 200), (255, 240, 120), t * 2); d.line([(x0 + i, y), (x0 + i, y + 30)], fill=col + (int(235 * u),))
    for xx, nm, cc in ((x0 + 60, "РАДИО", NEON), (x0 + 250, "WI-FI", NEON), (x0 + 520, "СВЕТ", GOLD), (x0 + 800, "РЕНТГЕН", RED)): tx(d, (xx, y - 36), nm, 26, cc, a=u); d.line([(xx, y + 34), (xx, y + 54)], fill=cc + (int(230 * u),), width=3)
    hit = P(4, lt, 1, 0.1, 0.5); br = P(4, lt, 1, 0.4, 0.8)
    molecule(d, (540, 820), 1.0, br)
    px = lerp((0, 0, 0), (0, 0, 0), 0); xs = 140 + (540 - 140) * hit; ys = 560 + (790 - 560) * hit
    if 0 < hit < 1: d.line([(xs - 120, ys - 80), (xs, ys)], fill=(255, 90, 140, 255), width=6); d.ellipse((xs - 14, ys - 14, xs + 14, ys + 14), fill=(255, 140, 180, 255))
    if br > 0.2: B.reticle(d, (540, 820), 110 * br, RED + (200,), u=1, ticks=24, w=2); tx(d, (540, 980), "СВЯЗИ РВУТСЯ", 40, RED, a=min(1, br * 1.5))
    tx(d, (540, 1060), "H₂O", 30, DIM, a=0.9, w="Medium"); corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 5. энергия частицы вайфая против ионизации
def s5(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "03", "МИКРОМИР", 1.0)
    a = P(5, lt, 0, 0.3, 0.9); b = P(5, lt, 1, 0.2, 0.9); r = P(5, lt, 2, 0.2, 0.8)
    base = 1000
    d.rectangle((300, base - 8 * a, 400, base), fill=GRN + (255,)); tx(d, (350, base + 60), "ЧАСТИЦА Wi-Fi", 28, DIM, a=a); tx(d, (350, base - 90), "≈ 10 мкэВ", 44, GRN, a=a)
    hh = 520 * ease(b); d.rectangle((680, base - hh, 780, base), fill=RED + (255,)); tx(d, (730, base + 60), "ИОНИЗАЦИЯ ВОДЫ", 28, DIM, a=b); tx(d, (730, base - hh - 50), "12,6 эВ", 44, RED, a=b)
    if r > 0:
        d.rounded_rectangle((240, 390, 840, 500), 16, fill=(8, 14, 28, int(230 * r)), outline=GOLD + (int(230 * r),), width=2); tx(d, (540, 445), "×1 270 000", 64, GOLD, a=r)
    tx(d, (540, 1135), "ШКАЛА УСЛОВНАЯ", 24, DIM, a=min(1, b), w="Medium"); corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 6. рехук: «Но их же много?»
def s6(lt, D):
    I = iso(78 - 8 * seg(lt, 0, D), 700); im, sock, ce = I_.room(lt, I, wall_a=90, dim=0.7); lay, d = layer(); u = P(6, lt, 0, 0.1, 0.9)
    photons(im, I, lt, n=70, a=u, size=7); chap(d, "04", "МОЩНОСТЬ", P(6, lt, 1, 0.0, 0.5))
    q = P(6, lt, 1, 0.3, 0.9)
    if q > 0: tx(d, (540, 560), "?", int(260 * (0.8 + 0.2 * q)), RED, a=q, w="Black")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.6, shake=1.5)
# ---------- 7. лимит 100 мВт
def s7(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "04", "МОЩНОСТЬ", 1.0); a = P(7, lt, 0, 0.2, 0.8); b = P(7, lt, 1, 0.2, 0.8)
    d.rounded_rectangle((190, 450, 890, 640), 22, fill=(8, 14, 28, int(235 * a)), outline=NEON + (int(240 * a),), width=3); tx(d, (540, 515), "100 мВт", 96, NEON, a=a, w="Black"); tx(d, (540, 600), "ЕВРОПЕЙСКИЙ ПРЕДЕЛ · 2,4 ГГц", 26, DIM, a=a, w="Medium")
    for k in range(10):
        x0 = 120 + k * 84; d.rounded_rectangle((x0, 780, x0 + 70, 900), 8, outline=ICE + (200,), width=3, fill=(10, 20, 40, 255))
        if k == 0 and b > 0: d.rounded_rectangle((x0 + 5, 785, x0 + 65, 895), 6, fill=GOLD + (int(255 * b),))
    tx(d, (540, 970), "0,1 ВАТТА  =  ОДНА ДЕСЯТАЯ", 36, GOLD, a=b); tx(d, (540, 1050), "ВЕРХНИЙ ПРЕДЕЛ, А НЕ ТИПИЧНАЯ МОЩНОСТЬ", 24, DIM, a=b, w="Medium"); corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 8. расстояние: круг растёт
def s8(lt, D):
    I = iso(96, 700); im, sock, ce = I_.room(lt, I, wall_a=80, dim=0.75); lay, d = layer(); u = seg(lt, 0.0, D); chap(d, "05", "РАССТОЯНИЕ", P(8, lt, 0, 0.0, 0.4))
    r = 0.4 + 4.6 * u; disk = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(disk)
    pts = [I.p(I_.RX + r * math.cos(t), I_.RY + r * math.sin(t), 0.01) for t in np.linspace(0, 2 * math.pi, 90)]; dd.polygon(pts, fill=NEON + (int(110 * (1 - 0.8 * u)),), outline=NEON + (230,))
    im.alpha_composite(disk); I_.rings(im, I, lt * 1.0, a=0.6)
    tx(d, (540, 1060), f"r = {r:.1f} м".replace(".", ","), 44, NEON, a=1.0); corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 9. закон обратных квадратов
def s9(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "05", "РАССТОЯНИЕ", 1.0); a = P(9, lt, 0, 0.1, 0.5); b = P(9, lt, 0, 0.5, 0.9); c = P(9, lt, 1, 0.1, 0.6)
    d.rectangle((140, 560, 140 + 100, 660), fill=NEON + (int(200 * a),)); tx(d, (190, 710), "1 м", 34, WHT, a=a); tx(d, (190, 770), "1", 60, NEON, a=a)
    for i in range(2):
        for j in range(2): d.rectangle((420 + i * 105, 480 + j * 105, 420 + i * 105 + 100, 480 + j * 105 + 100), outline=GOLD + (int(220 * b),), width=3, fill=(255, 214, 60, int(60 * b)))
    tx(d, (525, 735), "2 м", 34, WHT, a=b); tx(d, (525, 795), "1/4", 60, GOLD, a=b)
    if c > 0:
        for i in range(4):
            for j in range(4): d.rectangle((790 + i * 38, 520 + j * 38, 790 + i * 38 + 34, 520 + j * 38 + 34), outline=ORNG + (int(220 * c),), width=2, fill=(255, 140, 50, int(55 * c)))
        tx(d, (865, 735), "4 м", 34, WHT, a=c); tx(d, (865, 795), "1/16", 60, ORNG, a=c)
    f = P(9, lt, 1, 0.3, 0.9)
    if f > 0: d.rounded_rectangle((200, 920, 880, 1030), 18, fill=(8, 14, 28, int(230 * f)), outline=NEON + (int(230 * f),), width=2); tx(d, (540, 975), "I ∝ 1 / r²", 60, NEON, a=f)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 10. верхняя оценка против нормы
def s10(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "05", "РАССТОЯНИЕ", 1.0); a = P(10, lt, 0, 0.3, 0.9); b = P(10, lt, 1, 0.2, 0.7); r = P(10, lt, 2, 0.2, 0.8)
    y = 700; d.line([(100, y), (980, y)], fill=DIM + (200,), width=3)
    for k, nm in enumerate(("0,001", "0,01", "0,1", "1", "10", "100")): x = 100 + k * 176; d.line([(x, y - 12), (x, y + 12)], fill=DIM + (200,), width=3); tx(d, (x, y + 50), nm, 26, DIM, a=1.0, w="Medium")
    tx(d, (540, y + 105), "ПЛОТНОСТЬ ПОТОКА, Вт/м²  (ШКАЛА ЛОГАРИФМИЧЕСКАЯ)", 24, DIM, a=1.0, w="Medium")
    xa = 100 + (math.log10(0.008) + 3) * 176; xb = 100 + (math.log10(10) + 3) * 176
    if a > 0: d.ellipse((xa - 16, y - 16, xa + 16, y + 16), fill=NEON + (255,)); tx(d, (xa, y - 80), "0,008", 44, NEON, a=a); tx(d, (xa, y - 130), "РОУТЕР, 1 м  ·  8 мВт/м²", 26, NEON, a=a, w="Medium")
    if b > 0: d.ellipse((xb - 16, y - 16, xb + 16, y + 16), fill=GOLD + (255,)); tx(d, (xb, y - 80), "10", 44, GOLD, a=b); tx(d, (xb, y - 130), "НОРМА ДЛЯ ЛЮДЕЙ", 26, GOLD, a=b, w="Medium")
    if r > 0:
        d.line([(xa + 24, y + 175), (xa + 24 + (xb - xa - 48) * r, y + 175)], fill=GRN + (255,), width=6); tx(d, ((xa + xb) / 2, y + 230), "≈ В 1 200 РАЗ", 52, GRN, a=r)
    tx(d, (540, 1120), "ВЕРХНЯЯ ОЦЕНКА: ИДЕАЛЬНАЯ АНТЕННА, ПЕРЕДАЧА БЕЗ ПАУЗ", 22, DIM, a=min(1, b), w="Medium"); corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 11. телефон у головы
def s11(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "06", "ВЫВОД", P(11, lt, 0, 0.0, 0.4)); a = P(11, lt, 0, 0.1, 0.7); b = P(11, lt, 1, 0.2, 0.8)
    c = (480, 760); d.ellipse((c[0] - 150, c[1] - 190, c[0] + 150, c[1] + 190), outline=ICE + (int(230 * a),), width=5); d.rounded_rectangle((c[0] - 70, c[1] + 170, c[0] + 70, c[1] + 330), 40, outline=ICE + (int(230 * a),), width=5)
    d.rounded_rectangle((c[0] + 140, c[1] - 80, c[0] + 195, c[1] + 70), 12, fill=(30, 40, 60, int(255 * a)), outline=NEON + (int(255 * a),), width=3)
    for k in range(3):
        r = 40 + ((lt * 60 + k * 30) % 90); d.arc((c[0] + 168 - r, c[1] - r, c[0] + 168 + r, c[1] + r), 140, 220, fill=NEON + (int(220 * (1 - r / 130) * a),), width=4)
    if b > 0: d.rounded_rectangle((170, 1010, 910, 1110), 18, fill=(8, 14, 28, int(230 * b)), outline=NEON + (int(230 * b),), width=2); tx(d, (540, 1060), "ПРЕДЕЛ  2 Вт/кг", 52, NEON, a=b)
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 12. ВОЗ: осторожный вывод
def s12(lt, D):
    im = grid_bg(lt); lay, d = layer(); chap(d, "06", "ВЫВОД", 1.0); a = P(12, lt, 0, 0.1, 0.5); b = P(12, lt, 1, 0.1, 0.6); c = P(12, lt, 2, 0.1, 0.6)
    d.rounded_rectangle((100, 440, 980, 600), 22, fill=(8, 14, 28, int(235 * a)), outline=ICE + (int(240 * a),), width=3); tx(d, (540, 490), "ВСЕМИРНАЯ ОРГАНИЗАЦИЯ", 40, ICE, a=a); tx(d, (540, 550), "ЗДРАВООХРАНЕНИЯ", 40, ICE, a=a)
    if b > 0: tx(d, (540, 720), "ГЛАВНЫЙ ЭФФЕКТ — НАГРЕВ", 46, ORNG, a=b)
    if c > 0: tx(d, (540, 830), "ПРИ НИЗКОМ УРОВНЕ", 40, WHT, a=c); tx(d, (540, 895), "ВРЕД НЕ ПОДТВЕРЖДЁН", 46, GRN, a=c); tx(d, (540, 985), "ИССЛЕДОВАНИЯ ИДУТ", 32, DIM, a=c, w="Medium")
    corners(d, 0.5)
    return fin(im, lay, lt, k=0.7)
# ---------- 13. доза, вилка в розетке
def s13(lt, D):
    I = iso(88, 700); im, sock, ce = I_.room(lt, I, wall_a=130, plug=1.0); lay, d = layer(); a = P(13, lt, 0, 0.1, 0.7)
    rp = I.p(I_.RX + 0.2, I_.RY + 0.2, I_.RZ); B.reticle(d, rp, 120, GRN + (int(230 * a),), u=a, ticks=36, w=3); I_.rings(im, I, lt * 0.6, a=0.35 * a, col=GRN)
    d.rounded_rectangle((250, 960, 830, 1070), 20, fill=(8, 14, 28, int(235 * a)), outline=GRN + (int(240 * a),), width=3); tx(d, (540, 1015), "ОПАСНА ДОЗА", 64, GRN, a=a, w="Black"); corners(d, 0.5)
    return fin(im, lay, lt, k=0.6)
# ---------- 14. концовка
def s14(lt, D):
    I = iso(88, 700); im, sock, ce = I_.room(lt, I, wall_a=130, dim=0.6); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(140 * P(14, lt, 0, 0.0, 0.4)))))
    lay, d = layer(); b = P(14, lt, 0, 0.1, 0.5); s_ = 1 + 0.04 * math.sin(lt * 6); w_, h_ = 480 * s_, 120 * s_
    if b > 0: d.rounded_rectangle((540 - w_ / 2, 760 - h_ / 2, 540 + w_ / 2, 760 + h_ / 2), 60, fill=(255, 200, 60, int(255 * b))); tx(d, (540, 760), "ОТПРАВЬ", 58, (20, 14, 6), a=b)
    return fin(im, lay, lt, k=0.5)
SCENES = [
    ("Выдернуть роутер на ночь?", "SUB", "", s0, "", None),
    ("Давай проверим расчётом.", "SUB", "", s1, "", None),
    ("Роутер — это маленькая радиостанция. | Он шлёт радиоволны | около двух с половиной гигагерц.", "SUB", "", s2, "", None),
    ("Волна — это поток частиц.", "SUB", "", s3, "", None),
    ("Рентген рвёт молекулы: | его частица несёт много энергии.", "SUB", "", s4, "", None),
    ("Частица вайфая — десять миллионных долей электронвольта. | Чтобы ионизировать воду, нужно двенадцать с половиной. | Это в миллион раз больше.", "SUB", "", s5, "", None),
    ("Частицы слабые. | Но их же много?", "SUB", "", s6, "", None),
    ("Закон разрешает роутеру в Европе до ста милливатт. | Это одна десятая ватта.", "SUB", "", s7, "", None),
    ("Теперь расстояние.", "SUB", "", s8, "", None),
    ("Отошёл вдвое дальше — стало вчетверо слабее. | Это закон обратных квадратов.", "SUB", "", s9, "", None),
    ("На расстоянии метр, при максимуме, — восемь милливатт на квадратный метр. | Норма — десять ватт. | Это примерно в тысячу двести раз больше.", "SUB", "", s10, "", None),
    ("Телефон возле головы проверяют отдельно. | Предел — два ватта на килограмм.", "SUB", "", s11, "", None),
    ("Всемирная организация здравоохранения: | главный эффект — нагрев. | При низком уровне вред не подтверждён.", "SUB", "", s12, "", None),
    ("Опасна не волна, а доза.", "SUB", "", s13, "", None),
    ("Отправь тому, кто выдёргивает роутер на ночь. | Подпишись.", "SUB", SUB_PLATE, s14, "", None),
]
def SFX(STARTS, PHRASES, DURS, SR):
    out = []; rng = np.random.default_rng(2)
    def tm(i, k, f=0.0): st, en, _ = PHRASES[i][k]; return STARTS[i] + st + f * (en - st)
    def click(a=0.25): t = np.arange(int(SR * 0.04)) / SR; return a * np.exp(-t * 120) * np.sin(2 * np.pi * 2200 * t)
    def zap(a=0.3): t = np.arange(int(SR * 0.25)) / SR; return a * np.exp(-t * 14) * np.sin(2 * np.pi * (900 - 2200 * t) * t)
    def hum(dur, a=0.05): t = np.arange(int(SR * dur)) / SR; return a * np.sin(2 * np.pi * 60 * t) * np.sin(np.pi * t / dur) ** 2
    def beep(dur=1.2, a=0.1): t = np.arange(int(SR * dur)) / SR; g = (np.floor(t * 6) % 2 == 0); return a * g * np.sin(2 * np.pi * 880 * t)
    out += [(tm(0, 0, 0.6), zap(0.4)), (tm(1, 0, 0.0), click(0.3)), (tm(2, 0, 0.0), hum(DURS[2], 0.06)), (tm(4, 1, 0.1), zap(0.35)), (tm(5, 2, 0.2), click(0.3)), (tm(6, 1, 0.3), beep(1.0, 0.08)), (tm(9, 1, 0.1), click(0.3)), (tm(10, 2, 0.2), click(0.3)), (tm(13, 0, 0.1), click(0.3)), (tm(14, 0, 0.1), click(0.25))]
    return out
