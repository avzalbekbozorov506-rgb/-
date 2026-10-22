"""«Место без возврата» — чёрная дыра, тревожная документалка. Вся графика нарисована кодом и привязана к словам озвучки (PHRASES движка).
Факты: ОТО (горизонт событий, замедление времени со стороны наблюдателя, приливные силы), Стрелец A* ≈ 4 млн масс Солнца, ≈ 26 тыс. св. лет (EHT, 12.05.2022),
M87* ≈ 6,5 млрд масс Солнца, ≈ 54 млн св. лет (EHT, 10.04.2019). Сценарий: scripts/blackhole_2.md, визуал: scripts/blackhole_2_visual.md."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from blackhole_1 import canvas, finish, txt, circ, ring, shadow, lerp, arrow, funnel, disk, seg, ease, fnt, W, H, CX
HEAD = ("ЧЁРНАЯ ДЫРА", "ЧТО СКРЫВАЕТ КОСМОС")
TITLE = ("", "", "")
HOOK = ("МЕСТО\nБЕЗ ВОЗВРАТА", 2.4)
HOOK_Y = 1000
MUSIC = ("music/ogv_aria.mp3", 0)
AA = 0.5
TAIL = 0.3; XF = 0.4; LEAD_N = 0.25; GAP = 0.3
RED = (235, 60, 50); YEL = (255, 214, 40); WHT = (240, 244, 255); DIM = (120, 135, 175)
def ph(i, k):
    import __main__ as E
    return E.PHRASES[i][k]
def T(i, k, f=0.0): st, en, _ = ph(i, k); return st + f * (en - st)          # момент (с сцены), когда произнесена доля f фразы k
def P(i, lt, k, f0=0.0, f1=1.0): return seg(lt, T(i, k, f0), T(i, k, f1))     # прогресс 0..1 на отрезке фразы
def flash(im, a, col=RED):
    if a > 0.01: im.alpha_composite(Image.new("RGBA", (W, H), col + (int(130 * a),)))
    return im
def dashed(d, c, r, col, w=6, n=48, upto=1.0):
    for i in range(int(n * upto)):
        if i % 2 == 0: d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), i * 360 / n, (i + 0.9) * 360 / n, fill=col, width=w)
def lab(d, xy, s, size=44, col=WHT, a=1.0, w="Bold"):
    col = tuple(int(v * a) for v in col); txt(d, xy, s, size, col, w)
# ---------- сцена 1: «Есть место без возврата. Узнаешь, что там с упавшим.»
def s1(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); c = (CX, 640)
    g = P(0, lt, 0, 0.35, 0.8); r = 4 + 250 * g
    moveY = 40 * P(0, lt, 1, 0.0, 0.5)
    circ(d, (c[0], c[1] + moveY), r, fill=(0, 0, 0))
    dashed(d, (c[0], c[1] + moveY), r + 26, RED, upto=P(0, lt, 0, 0.7, 1.0))
    ra = P(0, lt, 0, 0.75, 1.0); ring(d, (c[0], c[1] + moveY), r + 6, a=ra * 0.9)
    dp = P(0, lt, 1, 0.55, 1.0)
    if dp > 0: circ(d, (c[0] + 80 - 80 * dp, 250 + 330 * dp * dp), 12 * (1 - 0.4 * dp), fill=(255, 255, 255))
    if lt >= T(0, 1, 0.1): lab(d, (CX, 330), "ЧТО С УПАВШИМ?", 46, DIM, a=P(0, lt, 1, 0.1, 0.3))
    return flash(finish(im), 0.5 * (1 - seg(lt, T(0, 0, 0.8), T(0, 0, 0.8) + 0.4)) * (lt > T(0, 0, 0.8)))
# ---------- сцена 2: «Это чёрная дыра. Её граница — горизонт событий. Даже свет оттуда не уходит.»
def s2(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); c = (CX, 700)
    dep = 300 * P(1, lt, 0, 0.3, 1.0); funnel(d, (CX, 560), dep, 0.95, a=P(1, lt, 0, 0.0, 0.4))
    R = 190; circ(d, c, 22, fill=(0, 0, 0)); circ(d, c, 22, outline=(255, 150, 40), width=5)
    lab(d, (CX, 300), "ЧЁРНАЯ ДЫРА", 74, WHT, a=P(1, lt, 0, 0.5, 0.9))
    k = P(1, lt, 1, 0.1, 0.55)
    if k > 0:
        dashed(d, c, R, YEL if lt < T(1, 1, 0.6) else RED, w=8, upto=k)
    if lt >= T(1, 1, 0.55):
        a = P(1, lt, 1, 0.55, 0.8); lab(d, (CX, 1000), "ГОРИЗОНТ СОБЫТИЙ", 54, RED, a=a); arrow(d, (CX, 960), (CX, 905), col=RED, w=8) if a > 0.5 else None
    kk = P(1, lt, 2, 0.15, 0.7)
    if kk > 0:
        def bez(p0, p1, p2, t): return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
        A = ((120, 520), (540, 220), (980, 520)); pts = [bez(*A, kk * i / 40) for i in range(41)]; d.line(pts, fill=(255, 250, 200), width=8); circ(d, pts[-1], 13, fill=(255, 255, 255))
        B = ((c[0] + 40, c[1] - 10), (c[0] + 170, c[1] - 130), (c[0] + 10, c[1] + 80)); pts = [bez(*B, kk * i / 40) for i in range(41)]; d.line(pts, fill=(255, 120, 80), width=8); circ(d, pts[-1], 13, fill=(255, 255, 255))
        lab(d, (CX, 960 if lt < T(1, 1, 0.55) else 1060), "СВЕТ НЕ ВЫХОДИТ", 48, (255, 160, 120), a=P(1, lt, 2, 0.5, 0.9))
    return finish(im)
# ---------- сцена 3: «Но быстрее света ничего нет. Поэтому не вернётся ничто.»
def s3(lt, D):
    im = canvas(); d = ImageDraw.Draw(im)
    lab(d, (CX, 300), "ПРЕДЕЛ СКОРОСТИ", 60, WHT, a=P(2, lt, 0, 0.0, 0.3))
    x0, x1, y = 160, 920, 520; d.line([(x0, y), (x1, y)], fill=DIM, width=6)
    for t in range(0, 11): d.line([(x0 + (x1 - x0) * t / 10, y - 14), (x0 + (x1 - x0) * t / 10, y + 14)], fill=DIM, width=3)
    d.line([(x1, y - 70), (x1, y + 70)], fill=RED, width=10); lab(d, (x1 - 10, y - 110), "СВЕТ", 44, RED)
    k = P(2, lt, 0, 0.4, 0.8); bump = 0.0 if k < 1 else 10 * math.sin((lt - T(2, 0, 0.8)) * 40) * math.exp(-(lt - T(2, 0, 0.8)) * 5)
    arrow(d, (x0, y), (x0 + (x1 - x0 - 40) * k + bump, y), col=YEL, w=12)
    cc = (CX, 940); r = 150; circ(d, cc, r, fill=(0, 0, 0)); dashed(d, cc, r + 14, RED, w=6)
    n = int(P(2, lt, 1, 0.1, 0.9) * 8) + (1 if lt >= T(2, 1, 0.1) else 0)
    for j in range(min(n, 8)):
        u = P(2, lt, 1, 0.1 + j * 0.09, 0.45 + j * 0.09); ang = math.pi * (0.1 + j * 0.37)
        sx, sy = cc[0] + 420 * math.cos(ang) * (1 - u), cc[1] + 260 * math.sin(ang) * (1 - u) - 60 * (1 - u)
        if u < 0.95: circ(d, (sx, sy), 11, fill=(255, 255, 255, int(255 * (1 - u * 0.2))))
    lab(d, (CX, 1115 if False else 760), "ВЕРНУЛОСЬ: " + str(0), 56, YEL, a=P(2, lt, 1, 0.0, 0.2))
    return finish(im)
# ---------- сцена 4: часы (падаешь; у тебя идут; снаружи замедляются; почти замирают)
def dial(d, c, r, tick, col, label, sub=None, frac=0.0):
    circ(d, c, r, outline=col, width=8); circ(d, c, 6, fill=col)
    for k in range(12):
        a = k * math.pi / 6; d.line([(c[0] + (r - 18) * math.sin(a), c[1] - (r - 18) * math.cos(a)), (c[0] + (r - 4) * math.sin(a), c[1] - (r - 4) * math.cos(a))], fill=col, width=4)
    a = (tick + frac) * math.pi / 6; d.line([c, (c[0] + (r - 30) * math.sin(a), c[1] - (r - 30) * math.cos(a))], fill=col, width=8)
    txt(d, (c[0], c[1] - r - 50), label, 44, col, "Bold"); txt(d, (c[0], c[1] + r + 70), f"{tick} с", 70, col, "Bold")
def s4(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); bh = (CX, 470)
    circ(d, bh, 70, fill=(0, 0, 0)); dashed(d, bh, 96, RED, w=5)
    u = lt / D; y = 190 + 150 * (1 - math.exp(-3.2 * P(3, lt, 0, 0.3, 1.0) - 3.2 * seg(lt, T(3, 1, 0), T(3, 3, 1.0)) * 0))
    y = 190 + 135 * (1 - (1 - seg(lt, T(3, 0, 0.3), T(3, 3, 1.0))) ** 2.6)
    circ(d, (CX, y), 13, fill=(255, 255, 255)); lab(d, (CX + 90, y), "ТЫ", 40, WHT, a=P(3, lt, 0, 0.3, 0.6))
    a1 = P(3, lt, 1, 0.0, 0.2)
    t1 = int(lt >= T(3, 1, 0.1)) + int(lt >= T(3, 1, 0.5)) + int(lt >= T(3, 1, 0.9))
    if a1 > 0: dial(d, (300, 820), 130, t1, YEL, "У ТЕБЯ")
    if lt >= T(3, 2, 0.0):
        t2 = int(lt >= T(3, 2, 0.15)) + int(lt >= T(3, 2, 0.55)) + int(lt >= T(3, 2, 0.95)) * 0 + int(lt >= T(3, 3, 0.25)) * 0
        t2 = int(lt >= T(3, 2, 0.1)) + int(lt >= T(3, 2, 0.8))
        dial(d, (780, 820), 130, t2, RED, "СНАРУЖИ")
        if lt >= T(3, 3, 0.0):
            bl = int(lt * 5) % 2; lab(d, (780, 1030), "ПОЧТИ СТОП", 46, RED, a=0.5 + 0.5 * bl)
            lab(d, (CX, 1085), "со стороны наблюдателя", 34, DIM, a=P(3, lt, 3, 0.2, 0.5), w="Medium") if False else None
    if lt >= T(3, 3, 0.2): lab(d, (CX, 1085), "СНАРУЖИ — СО СТОРОНЫ НАБЛЮДАТЕЛЯ", 32, DIM, a=P(3, lt, 3, 0.2, 0.5), w="Medium")
    return finish(im)
# ---------- сцена 5: рехук — приливные силы
def s5(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); c = (CX, 330)
    circ(d, (CX, 280), 110, fill=(0, 0, 0)); ring(d, (CX, 280), 116, col=RED, w=10, a=0.9)
    fl = 0.8 * (1 - seg(lt, T(4, 0, 0.0), T(4, 0, 0.0) + 0.45))
    k = P(4, lt, 1, 0.3, 0.9); s = P(4, lt, 2, 0.0, 0.9)
    top = 470 + 0 * k; bw, bh = 120, 120
    h = bh * 3 + 380 * s; x0 = CX - bw / 2
    wid = bw * (1 - 0.8 * s)
    d.rectangle((CX - wid / 2, top, CX + wid / 2, top + h), fill=(240, 244, 255))
    for j in range(1, 3): d.line([(CX - wid / 2, top + h * j / 3), (CX + wid / 2, top + h * j / 3)], fill=(60, 80, 120), width=4)
    if k > 0:
        arrow(d, (CX + 170, top + h - 10), (CX + 170, top + h - 10 + 190 * k), col=RED, w=12); lab(d, (CX + 290, top + h + 70), "СИЛЬНО", 38, RED, a=k)
        arrow(d, (CX + 170, top + 10), (CX + 170, top + 10 + 60 * k), col=YEL, w=12); lab(d, (CX + 290, top + 80), "СЛАБЕЕ", 38, YEL, a=k)
    lab(d, (CX, 1010 if False else 1080), "ПРИЛИВНЫЕ СИЛЫ", 48, RED, a=P(4, lt, 1, 0.2, 0.5) * (1 - 0.0))
    if s > 0.2: lab(d, (CX, 1040), "СПАГЕТТИФИКАЦИЯ", 54, YEL, a=P(4, lt, 2, 0.1, 0.4))
    return flash(finish(im), fl)
# ---------- сцена 6: центр Галактики
def s6(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); c = (CX, 600); rr = np.random.default_rng(5)
    zoom = 1 + 0.5 * P(5, lt, 0, 0.0, 1.0)
    for i in range(900):
        arm = i % 2; t = rr.uniform(0.04, 1); r = (40 + 380 * t) * zoom; a = arm * math.pi + t * 5.2 + lt * 0.15 + rr.normal(0, 0.12)
        x = c[0] + r * math.cos(a); y = c[1] + r * 0.5 * math.sin(a); b = int(100 + 150 * (1 - t))
        if 0 <= x < W and 0 <= y < 1100: circ(d, (x, y), 2.5, fill=(b, b, min(255, b + 40)))
    circ(d, c, 12, fill=(255, 220, 120)); lab(d, (CX, 330), "ЦЕНТР МЛЕЧНОГО ПУТИ", 46, WHT, a=P(5, lt, 0, 0.3, 0.7))
    n = P(5, lt, 1, 0.1, 0.8); cnt = int(4_000_000 * n)
    for j in range(int(26 * n)):
        a = j * 2.4; r = 70 + 9 * j; circ(d, (c[0] + r * math.cos(a), c[1] + r * 0.5 * math.sin(a)), 9, fill=YEL)
    if lt >= T(5, 1, 0.05): lab(d, (CX, 930), f"{cnt:,}".replace(",", " ") + " СОЛНЦ", 66, YEL)
    k = P(5, lt, 2, 0.1, 0.85)
    if k > 0:
        d.line([(170, 1040), (170 + 740 * k, 1040)], fill=WHT, width=6); circ(d, (170, 1040), 12, fill=(60, 140, 255)); circ(d, (170 + 740 * k, 1040), 10, fill=(255, 255, 255))
        lab(d, (CX, 1020 if False else 990), f"{int(26000 * k):,}".replace(",", " ") + " СВЕТОВЫХ ЛЕТ", 50, WHT)
    return finish(im)
# ---------- сцена 7: M87* и первый снимок
def s7(lt, D):
    im = canvas(); d = ImageDraw.Draw(im)
    a = P(6, lt, 0, 0.0, 0.5); k = P(6, lt, 0, 0.35, 1.0)
    r1 = 14; r2 = 14 + 300 * k
    circ(d, (270, 760), r1, fill=(0, 0, 0)); ring(d, (270, 760), r1 + 5, w=4); lab(d, (270, 940), "НАША", 36, DIM, a=a)
    circ(d, (CX + 120, 560), r2, fill=(0, 0, 0)); ring(d, (CX + 120, 560), r2 + 8, w=10, a=0.8)
    if k > 0.3: lab(d, (CX + 120, 560), f"{int(6_500_000_000 * k):,}".replace(",", " ") + " СОЛНЦ", 40, YEL)
    p = P(6, lt, 1, 0.1, 0.9)
    if p > 0:
        d.rectangle((0, 0, W, 1120), fill=(5, 7, 15, int(255 * min(1, p * 2))))
        rr = np.random.default_rng(2)
        cx, cy = CX, 600
        for i in range(160): 
            ang = rr.uniform(0, 2 * math.pi); rad = 200 + rr.normal(0, 18); bb = 0.4 + 0.6 * (math.cos(ang - 2.2) * 0.5 + 0.5); col = tuple(int(v * bb) for v in (255, 170, 60))
            circ(d, (cx + rad * math.cos(ang) * p, cy + rad * math.sin(ang) * p), 22 * p, fill=col + (150,))
        circ(d, (cx, cy), 175 * p, fill=(0, 0, 0)); lab(d, (CX, 330), "2019 · ПЕРВЫЙ СНИМОК", 54, YEL, a=p); lab(d, (CX, 1000), "СХЕМА, НЕ ФОТО", 34, DIM, a=p, w="Medium")
    return finish(im.filter(ImageFilter.GaussianBlur(1.2)) if False else im)
# ---------- сцена 8: формулы ломаются, информация
def s8(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); rr = np.random.default_rng(int(lt * 20))
    c = (CX, 560); circ(d, c, 14, fill=(0, 0, 0)); ring(d, c, 20, w=5, col=RED)
    br = P(7, lt, 0, 0.35, 1.0)
    forms = ["r → 0", "ρ → ∞", "G = 8πT", "ds² = ?", "1 / 0"]
    for j, f in enumerate(forms):
        y = 330 + j * 100; x = CX + (rr.normal(0, 30) * br * 4 if br > 0.05 else 0); y += rr.normal(0, 14) * br
        txt(d, (x, y), f if rr.random() > br * 0.6 else "".join(rr.choice(list("#?@%&§")) for _ in f), 60, tuple(int(v * (1 - 0.5 * br)) for v in (255, 214, 40)) if False else lerp(YEL, RED, br), "Bold")
    if br > 0.6: lab(d, (CX, 880), "СИНГУЛЯРНОСТЬ: ФОРМУЛЫ НЕ РАБОТАЮТ", 38, RED, a=P(7, lt, 0, 0.6, 0.9))
    q = P(7, lt, 1, 0.45, 0.95)
    if q > 0:
        d.rectangle((0, 250, W, 1100), fill=(5, 7, 15, int(235 * q)))
        txt(d, (CX, 640), "?", int(300 * q + 50), RED, "Black"); lab(d, (CX, 930), "ИНФОРМАЦИЯ: НЕ РЕШЕНО", 52, WHT, a=q)
    return flash(finish(im), 0.0)
# ---------- сцена 9: финал
def s9(lt, D):
    im = canvas(); d = ImageDraw.Draw(im); c = (CX, 600)
    circ(d, c, 240 + 6 * math.sin(lt * 3), fill=(0, 0, 0)); ring(d, c, 248, a=P(8, lt, 0, 0.0, 0.5))
    m = P(8, lt, 0, 0.1, 0.9)
    if m > 0:
        txt(d, (CX, 880), "МОНСТР", 80, tuple(int(v * (1 - 0.7 * seg(lt, T(8, 0, 0.6), T(8, 0, 0.9)))) for v in WHT), "Black")
        d.line([(CX - 200, 880), (CX - 200 + 400 * P(8, lt, 0, 0.6, 0.9), 880)], fill=RED, width=10)
    o = P(8, lt, 1, 0.2, 0.7); txt(d, (CX, 780), "ОТВЕТ", int(40 + 60 * o), lerp((60, 70, 90), YEL, o), "Black") if o > 0 else None
    b = P(8, lt, 2, 0.2, 0.6)
    if b > 0:
        d.rectangle((0, 250, W, 1100), fill=(5, 7, 15, int(240 * b))); shadow(d, (CX, 560), 190); s = 1 + 0.04 * math.sin(lt * 6)
        w, h = 470 * s, 120 * s; d.rounded_rectangle((CX - w / 2, 900 - h / 2, CX + w / 2, 900 + h / 2), 60, fill=(255, 190, 60)); txt(d, (CX, 900), "ОТПРАВЬ", 60, (20, 14, 6), "Bold")
    return finish(im)
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
