"""«Чёрная дыра — это не дыра» — моушен-графика, всё нарисовано кодом (numpy/PIL), сцены — функции (lt, D) -> RGBA.
Факты: EHT (M87* 10.04.2019, Sgr A* 12.05.2022), вторая космическая скорость Земли 11,2 км/с, радиус Шварцшильда Солнца ≈ 2,95 км, Земли ≈ 8,87 мм.
Сценарий: scripts/blackhole_1.md, визуал: scripts/blackhole_1_visual.md."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
HEAD = ("ЧЁРНАЯ ДЫРА", "ОБЪЯСНЯЕМ ЗА МИНУТУ")
TITLE = ("", "", "")
HOOK = ("ЧЁРНАЯ ДЫРА —\nЭТО НЕ ДЫРА", 2.2)
HOOK_Y = 980
MUSIC = ("music/ogv_aria.mp3", 0)
AA = 0.6
W, H = 1080, 1920
CX, CY = 540, 700
def fnt(size, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def seg(u, a, b): return ease((u - a) / (b - a))
_r = np.random.default_rng(7)
STARS = [(int(_r.integers(0, W)), int(_r.integers(0, 1400)), int(_r.integers(1, 4)), int(_r.integers(70, 200))) for _ in range(230)]
_BG = None
def canvas():
    global _BG
    if _BG is None:
        im = Image.new("RGBA", (W, H), (5, 7, 15, 255)); d = ImageDraw.Draw(im)
        for x, y, s, b in STARS: d.ellipse((x, y, x + s, y + s), fill=(b, b, min(255, b + 30), 255))
        _BG = im
    return _BG.copy()
def finish(im, k=0.9):
    sm = im.convert("RGB").resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    sm = sm.point(lambda v: int(v * k))
    return ImageChops.add(im.convert("RGB"), sm).convert("RGBA")
def txt(d, xy, s, size, fill=(240, 244, 255), w="Bold", anchor="mm"): d.text(xy, s, font=fnt(size, w), fill=fill, anchor=anchor)
def circ(d, c, r, fill=None, outline=None, width=1): d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=fill, outline=outline, width=width)
def ring(d, c, r, col=(255, 170, 60), w=14, a=1.0):
    col = tuple(int(v * a) for v in col); circ(d, c, r, outline=col, width=w); circ(d, c, r - w // 2, outline=tuple(min(255, int(v * 1.0 + 60 * a)) for v in col), width=max(2, w // 3))
def shadow(d, c, r, a=1.0, ringa=1.0):
    circ(d, c, r, fill=(0, 0, 0, 255)); ring(d, c, r + 8, a=ringa * a)
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def arrow(d, p0, p1, col=(255, 214, 40), w=10):
    d.line([p0, p1], fill=col, width=w); ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.45, 0.45): d.line([p1, (p1[0] - 46 * math.cos(ang + s), p1[1] - 46 * math.sin(ang + s))], fill=col, width=w)
def earth(d, c, r):
    circ(d, c, r, fill=(40, 110, 220)); circ(d, (c[0] - r * .25, c[1] - r * .2), r * .45, fill=(60, 160, 90)); circ(d, c, r, outline=(150, 200, 255), width=3)
def sun(d, c, r): circ(d, c, r, fill=(255, 205, 60)); circ(d, c, r, outline=(255, 240, 170), width=4)
def funnel(d, c, depth, scale=1.0, a=1.0):
    R = 420 * scale; rs = [R * (0.93 ** k) for k in range(0, 26, 1)]; rs = [r for r in rs if r > 14]
    col = (int(70 * a), int(105 * a), int(190 * a))
    def pt(r, ang): return (c[0] + r * math.cos(ang), c[1] + r * 0.33 * math.sin(ang) + depth * scale * (70 / (r / scale + 70)) * 1.4 - depth * scale * 0.2)
    angs = [i * math.pi / 12 for i in range(25)]
    for r in rs: d.line([pt(r, x) for x in angs], fill=col, width=2)
    for x in angs[:-1]: d.line([pt(r, x) for r in rs], fill=col, width=2)
    return pt(0.01, 0)
def disk(d, c, rin, rout, heat, dop=0.6, rot=0.0, tilt=0.30):
    n = 46
    for i in range(n):
        f = i / (n - 1); r = rin + (rout - rin) * f
        base = lerp((255, 245, 200), lerp((255, 150, 40), (200, 50, 20), heat), f ** .8); cold = lerp((120, 170, 255), (60, 90, 200), f)
        col0 = lerp(cold, base, heat)
        for k in range(48):
            a0 = rot + k * 2 * math.pi / 48; a1 = a0 + 2 * math.pi / 48 + .02
            b = (1 - dop / 2) + dop / 2 * math.cos(a0 - rot * 0 - 0.0 + math.pi) * -1
            b = max(0.15, 1 - dop / 2 + dop / 2 * math.cos(k * 2 * math.pi / 48))
            col = tuple(int(v * b) for v in col0)
            d.line([(c[0] + r * math.cos(a0), c[1] + r * tilt * math.sin(a0)), (c[0] + r * math.cos(a1), c[1] + r * tilt * math.sin(a1))], fill=col, width=5)
    d.ellipse((c[0] - rin * 0.98, c[1] - rin * 0.98, c[0] + rin * 0.98, c[1] + rin * 0.98), fill=(0, 0, 0, 255))
    d.arc((c[0] - rin * 1.05 - 6, c[1] - rin * 1.05 - 6, c[0] + rin * 1.05 + 6, c[1] + rin * 1.05 + 6), 180, 360, fill=(255, 190, 90), width=10)
    d.arc((c[0] - rin * 1.0, c[1] - rin * 1.0, c[0] + rin * 1.0, c[1] + rin * 1.0), 0, 180, fill=(255, 150, 40), width=6)
# ------------------------------------------------------------------ сцены
def s1(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im)
    fill = lerp((245, 245, 255), (0, 0, 0), seg(u, 0.05, 0.6)); r = 250 - 20 * seg(u, 0, 0.6)
    circ(d, (CX, CY), r, fill=fill); ring(d, (CX, CY), r + 8, a=seg(u, 0.4, 0.9)); return finish(im)
def s2(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); a = seg(u, 0.1, 0.4)
    shadow(d, (CX, CY), 230, ringa=a)
    L = 150 + 25 * math.sin(u * 12); x0, y0, x1, y1 = 110, 270, 970, 1130; col = (255, 214, 40)
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(x, y), (x + sx * L * .4, y)], fill=col, width=8); d.line([(x, y), (x, y + sy * L * .4)], fill=col, width=8)
    return finish(im)
def s3(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); dep = 260 * seg(u, 0.35, 0.95)
    funnel(d, (CX, 560), dep, 0.95, a=seg(u, 0.0, 0.3))
    br = 200 * (1 - seg(u, 0.1, 0.6)) + 18; by = 380 + (330 + dep * 0.55) * seg(u, 0.15, 0.95) if u > 0.15 else 380 + 0
    circ(d, (CX, 300 + 360 * seg(u, 0.1, 0.9) + 0 * dep), br, fill=(255, 205, 80)); circ(d, (CX, 300 + 360 * seg(u, 0.1, 0.9)), br, outline=(255, 240, 190), width=4)
    return finish(im)
def s4(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im)
    earth(d, (290, 920), 90); k = seg(u, 0.05, 0.4); arrow(d, (290, 790), (290, 790 - 230 * k)) if k > 0.02 else None
    txt(d, (290, 400), "ЗЕМЛЯ", 44, (180, 200, 240)); txt(d, (290, 480), "11 КМ/С", 64, (255, 214, 40)) if k > 0.5 else None
    circ(d, (790, 920), 60, fill=(0, 0, 0)); ring(d, (790, 920), 66, w=8)
    k2 = seg(u, 0.45, 0.85); bump = 0.0
    top = 790 - 520 * k2; top = max(top, 430) + (12 * math.sin(lt * 20) if k2 >= 1 else 0)
    if k2 > 0.02: arrow(d, (790, 790), (790, top), col=(255, 120, 80))
    if u > 0.5: d.line([(640, 400), (940, 400)], fill=(240, 244, 255), width=5); txt(d, (790, 350), "СВЕТ — ПРЕДЕЛ", 42, (240, 244, 255))
    txt(d, (790, 1010), "ДЫРА: БОЛЬШЕ СВЕТА", 40, (255, 140, 100)) if u > 0.6 else None
    return finish(im)
def s5(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); c = (CX, 760); R = 210
    circ(d, c, 20, fill=(0, 0, 0)); circ(d, c, 20, outline=(255, 150, 40), width=5)
    n = int(60 * seg(u, 0.15, 0.55))
    for i in range(n):
        a = 2 * math.pi * i / 60
        if i % 2 == 0: d.arc((c[0] - R, c[1] - R, c[0] + R, c[1] + R), math.degrees(a), math.degrees(a + 0.07), fill=(255, 214, 40), width=7)
    def bez(p0, p1, p2, t): return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
    t1 = seg(u, 0.25, 0.65); A = ((80, 520), (540, 250), (1000, 520))
    pts = [bez(*A, t1 * i / 40) for i in range(41)]; d.line(pts, fill=(255, 250, 200), width=8); circ(d, pts[-1], 14, fill=(255, 255, 255))
    t2 = seg(u, 0.5, 0.95); B = ((c[0] + 60, c[1] - 20), (c[0] + 190, c[1] - 130), (c[0] + 20, c[1] + 70))
    pts = [bez(*B, t2 * i / 40) for i in range(41)]; d.line(pts, fill=(255, 120, 80), width=8); circ(d, pts[-1], 14, fill=(255, 255, 255))
    txt(d, (CX, 1040), "ВНУТРИ — НАЗАД", 44, (255, 140, 100)) if u > 0.7 else None; txt(d, (CX, 330), "СНАРУЖИ — УЛЕТАЕТ", 40, (255, 250, 200)) if u > 0.5 else None
    return finish(im)
def s6(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); c = (CX, 700)
    k = seg(u, 0.2, 0.65); r = 190 * (1 - k) + 6
    d.arc((c[0] - 360, c[1] - 180, c[0] + 360, c[1] + 180), 0, 360, fill=(90, 110, 170), width=3)
    if k < 0.98: sun(d, c, r)
    else: circ(d, c, 8, fill=(0, 0, 0)); ring(d, c, 14, w=5)
    a = u * 2 * math.pi * 1.4; earth(d, (c[0] + 360 * math.cos(a), c[1] + 180 * math.sin(a)), 34)
    if u > 0.6:
        al = seg(u, 0.6, 0.8); d.line([(CX - 110, 940), (CX + 110, 940)], fill=(255, 214, 40), width=6); d.line([(CX - 110, 920), (CX - 110, 960)], fill=(255, 214, 40), width=6); d.line([(CX + 110, 920), (CX + 110, 960)], fill=(255, 214, 40), width=6)
        txt(d, (CX, 1000), "3 КМ", 76, (255, 214, 40))
    txt(d, (CX, 330), "СОЛНЦЕ", 44, (255, 220, 130)); return finish(im)
def s7(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); a = u * 2 * math.pi * 1.2
    for cx, lab, hole in ((280, "ЗВЕЗДА", False), (800, "ЧЁРНАЯ ТОЧКА", True)):
        c = (cx, 720); d.arc((c[0] - 210, c[1] - 105, c[0] + 210, c[1] + 105), 0, 360, fill=(90, 110, 170), width=3)
        if hole: circ(d, c, 9, fill=(0, 0, 0)); ring(d, c, 15, w=5); circ(d, c, 60 + 8 * math.sin(lt * 5), outline=(255, 90, 60), width=3) if u > 0.5 else None
        else: sun(d, c, 52)
        earth(d, (c[0] + 210 * math.cos(a), c[1] + 105 * math.sin(a)), 26); txt(d, (cx, 470), lab, 40, (220, 228, 250))
    txt(d, (CX, 960), "ОРБИТА ОДНА И ТА ЖЕ", 50, (255, 214, 40)) if u > 0.4 else None
    return finish(im)
def s8(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); c = (CX, 700); k = seg(u, 0.1, 0.75); r = 230 * (1 - k) + 12
    earth(d, c, r)
    if u > 0.7:
        al = seg(u, 0.7, 0.9); circ(d, (CX + 220, 700), 12, fill=(120, 200, 90)); circ(d, (CX + 220, 700), 12, outline=(210, 250, 180), width=3)
        d.line([(CX - 110, 900), (CX + 110, 900)], fill=(255, 214, 40), width=6); txt(d, (CX, 960), "9 ММ", 80, (255, 214, 40))
    txt(d, (CX, 330), "ЗЕМЛЯ", 44, (180, 200, 240)); return finish(im)
def s9(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); c = (CX, 700); rr = np.random.default_rng(3)
    if u < 0.45:
        k = seg(u, 0.0, 0.45)
        for i in range(260):
            a0 = rr.uniform(0, 2 * math.pi); r0 = rr.uniform(120, 460); r = r0 * (1 - 0.3 * k) + 60; a = a0 + k * 6 * (300 / (r + 80))
            y = c[1] + (r * math.sin(a)) * (0.30 + 0.7 * (1 - k)); x = c[0] + r * math.cos(a)
            col = lerp((120, 170, 255), (255, 170, 70), k); circ(d, (x, y), 4, fill=col)
        shadow(d, c, 70, ringa=0.0)
    else:
        k = seg(u, 0.45, 0.8); disk(d, c, 85, 85 + 330 * k + 20, heat=min(1, k * 1.2), rot=u * 3)
    if u > 0.8:
        txt(d, (CX, 1060), "СХЕМА, НЕ ФОТО", 40, (160, 175, 215)); txt(d, (CX, 330), "2019", 120, (255, 214, 40)) if u > 0.85 else None
    return finish(im)
def s10(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); c = (CX, 700); rr = np.random.default_rng(5)
    for i in range(900):
        arm = i % 2; t = rr.uniform(0.05, 1); r = 40 + 400 * t; a = arm * math.pi + t * 5.2 + u * 0.8 + rr.normal(0, 0.12)
        x = c[0] + r * math.cos(a); y = c[1] + r * 0.55 * math.sin(a); b = int(110 + 140 * (1 - t))
        circ(d, (x, y), 2.5, fill=(b, b, min(255, b + 40)))
    k = seg(u, 0.45, 0.8); circ(d, c, 10 + 28 * k, fill=(0, 0, 0)); ring(d, c, 18 + 28 * k, a=k, w=8)
    txt(d, (CX, 330), "2022", 120, (255, 214, 40)); txt(d, (CX, 1060), "ЦЕНТР НАШЕЙ ГАЛАКТИКИ", 40, (190, 205, 240)); return finish(im)
def s11(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); shadow(d, (CX, CY), 230 + 10 * math.sin(lt * 3), ringa=1.0)
    arc_a = seg(u, 0.1, 0.7)
    for i in range(int(40 * arc_a)): d.arc((CX - 300, CY - 300, CX + 300, CY + 300), i * 9, i * 9 + 5, fill=(255, 200, 100), width=5)
    return finish(im)
def s12(lt, D):
    u = lt / D; im = canvas(); d = ImageDraw.Draw(im); shadow(d, (CX, 560), 190); s = 1 + 0.04 * math.sin(lt * 6)
    w, h = 460 * s, 120 * s; d.rounded_rectangle((CX - w / 2, 960 - h / 2, CX + w / 2, 960 + h / 2), 60, fill=(255, 190, 60)); txt(d, (CX, 960), "ОТПРАВЬ", 60, (20, 14, 6))
    return finish(im)
SCENES = [
    ("Чёрная дыра — это не дыра.", "SUB", "", s1, "", None),
    ("Поймёшь, почему её видно, | хотя она чёрная.", "SUB", "ЧТО УЗНАЕШЬ", s2, "", None),
    ("Много вещества в малом месте.", "SUB", "МНОГО МАССЫ В МАЛОМ МЕСТЕ", s3, "", None),
    ("Ракете с Земли хватает одиннадцати километров в секунду. | Здесь нужно больше скорости св+ета.", "SUB", "ЗЕМЛЯ — 11 КМ/С", s4, "", None),
    ("Есть граница — горизонт соб+ытий. | Пересёк — пути назад нет.", "SUB", "ГОРИЗОНТ СОБЫТИЙ", s5, "", None),
    ("Сожми Солнце до трёх километров — | будет чёрная дыра. | А Земля не упадёт.", "SUB", "СОЛНЦЕ → 3 КМ", s6, "", None),
    ("Издали притяжение прежнее. | Это не пылесос.", "SUB", "НЕ ПЫЛЕСОС", s7, "", None),
    ("Землю надо сжать до горошины.", "SUB", "ЗЕМЛЯ = ГОРОШИНА", s8, "", None),
    ("Как увидеть чёрное? По свету вокруг. | В две тысячи девятнадцатом — первый снимок.", "SUB", "ПЕРВЫЙ СНИМОК", s9, "", None),
    ("Не дыра. | Не пылесос. | Место, откуда не уходит свет.", "SUB", "НЕ ДЫРА. НЕ ПЫЛЕСОС.", s11, "", None),
    ("Отправь тому, кто думает, что она всасывает всё. | Подпишись.", "SUB", SUB_PLATE, s12, "", None),
]
