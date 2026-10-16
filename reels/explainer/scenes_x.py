"""Сцены ролика «Tesla Roadster едет по потолку»: разбор машины, частицы воздуха, схема сопел. Рисуем в 2x."""
import math, random
from PIL import ImageFont, ImageDraw

W, H, K = 1080, 1920, 2
FD = "/usr/share/fonts/opentype/inter/"
def F(sz, w="Bold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", sz)
CY, YEL, RED, GRN, WHITE, ORG, VIO = (60, 200, 255), (255, 176, 40), (255, 80, 80), (60, 230, 150), (240, 244, 250), (255, 140, 40), (150, 110, 255)

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def rot(p, a): c, s = math.cos(a), math.sin(a); return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)
def seg(t, a, b): return ease((t - a) / max(1e-6, b - a))
def tri(p, L): m = p % (2 * L); return m if m < L else 2 * L - m
def dim(c, k): return tuple(int(v * k) for v in c)

# ---------- геометрия машины (вид сбоку, колёса на y=0, вверх — минус) ----------
BODY = [(-222, -40), (-208, -92), (-92, -122), (-10, -132), (112, -82), (228, -64), (224, -38)]
GLASS = [(-84, -112), (-8, -122), (84, -86), (-78, -86)]
FANS = [-95, -25, 45, 110]                                     # положение вентиляторов (схема)
TANKS = [(-175, -82, -95), (-80, -82, -5)]                      # баллоны: x0, y, x1 (схема)
NOZ = [((-175, -104), (0, -1)), ((-100, -116), (0, -1)), ((-30, -126), (0, -1)), ((40, -118), (0, -1)),
       ((-205, -66), (-1, 0)), ((-215, -50), (-1, 0)), ((226, -58), (1, 0)), ((215, -46), (1, 0)),
       ((-150, -38), (0, 1)), ((150, -38), (0, 1))]            # 10 сопел: точка, направление наружу

def mk(x, y, a=0, s=1.0, xd=1, ys=1.0):
    def T(p):
        q = rot((p[0] * xd * s, p[1] * ys * s), a); return ((x + q[0]) * K, (y + q[1]) * K)
    return T

def circ(d, c, r, **kw): d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], **kw)

def car(d, x, y, a=0, s=1.0, xd=1, ys=1.0, alpha=1.0, xray=0.0, tt=0.0, jets=(), jt=0.0):
    """xray 0 — обычная машина, 1 — прозрачный корпус и видна «начинка» (схема); jets — номера сопел, из которых бьёт воздух."""
    T = mk(x, y, a, s, xd, ys); sh = (236, 240, 246)
    if xray < 1:
        k = 1 - xray
        d.polygon([T(p) for p in BODY], fill=dim(sh, k) if xray else sh)
        d.polygon([T(p) for p in [(-222, -40), (-208, -62), (226, -52), (224, -38)]], fill=dim((150, 160, 175), k))
        d.polygon([T(p) for p in GLASS], fill=dim((18, 26, 48), k))
    if xray > 0:
        d.polygon([T(p) for p in BODY], outline=dim(CY, xray), fill=(10, 24, 44))
        d.rounded_rectangle([T((-150, -62))[0], min(T((-150, -62))[1], T((120, -44))[1]), T((120, -44))[0], max(T((-150, -62))[1], T((120, -44))[1])], 6, fill=(14, 80, 90), outline=(40, 200, 200))
        for ti, (x0, yy, x1) in enumerate(TANKS):
            p0, p1 = T((x0, yy - 11)), T((x1, yy + 11)); xs, ys_ = sorted([p0[0], p1[0]]), sorted([p0[1], p1[1]])
            d.rounded_rectangle([xs[0], ys_[0], xs[1], ys_[1]], 18 * s, fill=(60, 40, 10), outline=ORG, width=3 * K)
        for cx in FANS:
            c = T((cx, -44)); r = 17 * s * K
            d.ellipse([c[0] - r, c[1] - r * .55, c[0] + r, c[1] + r * .55], fill=(20, 60, 90), outline=CY)
            for b in range(3):
                th = tt * 24 + cx + b * 2.094; d.line([c[0], c[1], c[0] + math.cos(th) * r * .9, c[1] + math.sin(th) * r * .5], fill=CY, width=3)
        for n, ((px, py), (nx, ny)) in enumerate(NOZ):
            c = T((px, py)); on = n in jets
            circ(d, c, 6 * s * K, fill=ORG if on else (90, 60, 30))
            if on:
                for k in range(7):                              # струя воздуха из сопла
                    u = ((jt * 3 + k / 7) % 1); L = 70 * u * s
                    e = T((px + nx * L * 1.0 / s, py + ny * L / s)); circ(d, e, (6 - 4 * u) * K, fill=dim(WHITE, 1 - u))
    for cx in (-132, 142):
        c = T((cx, -36)); r = 34 * s * K
        circ(d, c, r, fill=(14, 16, 24), outline=(90, 100, 120), width=3); circ(d, c, 14 * s * K, fill=VIO if xray else (120, 130, 150))
    if not xray:
        circ(d, T((222, -56)), 7 * K, fill=YEL); circ(d, T((-214, -70)), 5 * K, fill=RED)
    return T

def tag(d, x, y, text, col=CY, fs=26, fill=(8, 22, 40), anchor="l"):
    f = F(fs * K, "Bold"); b = d.textbbox((0, 0), text, font=f); tw, th = b[2] - b[0], b[3] - b[1]; pad = 12 * K
    x0 = x * K if anchor == "l" else x * K - tw / 2
    d.rectangle([x0 - pad, y * K - pad, x0 + tw + pad, y * K + th + pad], fill=fill, outline=col, width=2 * K)
    d.text((x0, y * K - b[1]), text, font=f, fill=col)

def big(d, x, y, text, col=YEL, fs=110, a=1.0):
    f = F(fs * K, "ExtraBold"); b = d.textbbox((0, 0), text, font=f)
    d.text((x * K - (b[2] - b[0]) / 2, y * K), text, font=f, fill=dim(col, a))

def arrow(d, x0, y0, x1, y1, col=CY, w=6, hd=22):
    d.line([x0 * K, y0 * K, x1 * K, y1 * K], fill=col, width=int(w * K)); a = math.atan2(y1 - y0, x1 - x0)
    for sg in (-1, 1): d.line([x1 * K, y1 * K, (x1 - hd * math.cos(a - sg * .5)) * K, (y1 - hd * math.sin(a - sg * .5)) * K], fill=col, width=int(w * K))

def leader(d, p, q, col=CY): d.line([p[0], p[1], q[0] * K, q[1] * K], fill=col, width=2 * K); circ(d, p, 4 * K, fill=col)

def ceiling(d, y, x0=0, x1=W):
    d.rectangle([x0 * K, (y - 90) * K, x1 * K, y * K], fill=(150, 158, 172)); d.rectangle([x0 * K, (y - 8) * K, x1 * K, y * K], fill=(235, 238, 245))

def ground(d, y): d.line([0, y * K, W * K, y * K], fill=(70, 84, 110), width=3 * K)

def pts(n, sd):
    r = random.Random(sd); return [(r.random(), r.random(), r.random(), r.random()) for _ in range(n)]

def gas(d, t, box, n, sd=1, speed=160, col=CY, r=3.5, hits=None, avoid=None):
    """Частицы газа отскакивают от стенок коробки box=(x0,y0,x1,y1) (аналитически). hits — список коробок-стенок, где вспыхивают удары."""
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0; nh = 0
    for (a, b, c, e) in pts(n, sd):
        ang = e * 6.283; vx, vy = math.cos(ang) * speed * (.5 + c), math.sin(ang) * speed * (.5 + c)
        px = tri(a * w + vx * t, w); py = tri(b * h + vy * t, h); X, Y = x0 + px, y0 + py
        if avoid and avoid(X, Y): continue
        circ(d, (X * K, Y * K), r * K, fill=dim(col, .55 + .45 * c))
        if hits:
            for side, (hx0, hy0, hx1, hy1) in enumerate(hits):
                if hx0 - 4 <= X <= hx1 + 4 and hy0 - 4 <= Y <= hy1 + 4:
                    circ(d, (X * K, Y * K), 9 * K, outline=WHITE, width=2 * K); nh += 1
    return nh

# ---------- сцены ----------
def sc_hook(d, t, T):
    cy = 560; ceiling(d, cy)
    x = lerp(-250, 540, ease(t / 2.6)) + max(0, t - 2.6) * 30
    car(d, x, cy, 0, 1.15, 1, -1, xray=0)
    gas(d, t, (0, cy + 60, W, 1250), 90, 5, 40, CY, 2)
    if t > .6: tag(d, 90, 900, "ВВЕРХ НОГАМИ", CY, 34)
    if t > 1.6: tag(d, 90, 980, "✓  НЕ ПАДАЕТ", GRN, 34, fill=(6, 40, 30))
    ground(d, 1300)

def sc_parts(d, t, T):
    cx, cy = 540, 800; s = 1.5
    p = seg(t, 0.4, 1.8) * (1 - seg(t, T - 1.3, T - .2))          # степень разлёта
    x = cx; X = 0.0
    xr = seg(t, .1, 1.0) * (1 - seg(t, T - 1.0, T - .1))           # прозрачность корпуса
    # слои разносятся по вертикали
    layers = [("КУЗОВ", -330, None), ("БАЛЛОНЫ И СОПЛА", -150, "tank"), ("ВЕНТИЛЯТОРЫ", 40, "fan"), ("БАТАРЕЯ", 200, "bat"), ("КОЛЁСА", 330, "wh")]
    # корпус (оболочка)
    T0 = mk(cx, cy + layers[0][1] * p, 0, s)
    d.polygon([T0(q) for q in BODY], fill=(236, 240, 246) if xr < .5 else None, outline=WHITE if xr >= .5 else None) if False else None
    if p < .02: car(d, cx, cy, 0, s, 1, 1, xray=0)
    else:
        d.polygon([T0(q) for q in BODY], outline=(190, 200, 215), fill=(30, 40, 58)); d.polygon([T0(q) for q in GLASS], fill=(18, 26, 48))
        tag(d, 60, cy + layers[0][1] * p - 150, "КУЗОВ", WHITE, 26)
        Tt = mk(cx, cy + layers[1][1] * p, 0, s)
        for (x0, yy, x1) in TANKS:
            p0, p1 = Tt((x0, yy - 11)), Tt((x1, yy + 11))
            d.rounded_rectangle([min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])], 26, fill=(60, 40, 10), outline=ORG, width=3 * K)
        for (q, nn) in NOZ[:6]:
            c = Tt((q[0], q[1] + 40)); circ(d, c, 7 * K, fill=ORG)
        tag(d, 60, cy + layers[1][1] * p - 25, "БАЛЛОНЫ И СОПЛА", ORG, 26, fill=(40, 22, 6))
        Tf = mk(cx, cy + layers[2][1] * p, 0, s)
        for fx in FANS:
            c = Tf((fx, -44)); r = 26 * s * K
            d.ellipse([c[0] - r, c[1] - r * .55, c[0] + r, c[1] + r * .55], fill=(20, 60, 90), outline=CY, width=2 * K)
            for b in range(3):
                th = t * 24 + fx + b * 2.094; d.line([c[0], c[1], c[0] + math.cos(th) * r * .9, c[1] + math.sin(th) * r * .5], fill=CY, width=4)
        tag(d, 60, cy + layers[2][1] * p - 20, "ВЕНТИЛЯТОРЫ", CY, 26)
        Tb = mk(cx, cy + layers[3][1] * p, 0, s)
        d.rounded_rectangle([Tb((-190, -60))[0], Tb((-190, -60))[1], Tb((200, -42))[0], Tb((200, -42))[1]], 8, fill=(14, 80, 90), outline=(40, 200, 200), width=2 * K)
        tag(d, 60, cy + layers[3][1] * p - 10, "БАТАРЕЯ", GRN, 26, fill=(6, 40, 30))
        Tw = mk(cx, cy + layers[4][1] * p, 0, s)
        for wx in (-132, 142): circ(d, Tw((wx, -36)), 34 * s * K, fill=(14, 16, 24), outline=(90, 100, 120), width=3); circ(d, Tw((wx, -36)), 14 * s * K, fill=VIO)
        tag(d, 60, cy + layers[4][1] * p - 15, "КОЛЁСА", VIO, 26, fill=(24, 16, 44))
    if t > 2.0 and t < T - 1.0: tag(d, 540, 1370, "СХЕМА, НЕ ЧЕРТЁЖ", (110, 140, 170), 22, anchor="c")

def sc_event(d, t, T):
    G = 1180; R = 420; cx0 = 640; ground(d, G)
    d.arc([(cx0 - R) * K, (G - 2 * R) * K, (cx0 + R) * K, G * K], 200, 90, fill=(190, 198, 210), width=14 * K)
    t1 = 2.4; trail = []
    def pose(tt):
        if tt < t1: return lerp(-200, cx0, ease(tt / t1)), G, 0, 1, 1
        if tt < t1 + 3.0:
            th = ease((tt - t1) / 3.0) * math.pi; return cx0 + R * math.sin(th), G - R + R * math.cos(th), -th, 1, 1
        u = min(1.0, (tt - t1 - 3.0) / 3.0); return cx0 - 520 * u, (G - 2 * R) + (G - (G - 2 * R)) * u * u, 0, -1, -math.cos(min(1, u * 1.15) * math.pi)
    for k in range(1, 9):
        px, py, *_ = pose(max(0, t - k * .09))
        circ(d, (px * K, (py - 60) * K), (14 - k) * K, fill=dim(CY, 1 - k / 9))
    x, y, a, xd, ys = pose(t); car(d, x, y, a, .78, xd, ys)
    if t > .6: tag(d, 60, 330, "15 ОКТЯБРЯ · ПОКАЗ", YEL, 30)
    if t1 + .5 < t < t1 + 3: tag(d, 60, 400, "ВВЕРХ КОЛЁСАМИ", CY, 30)
    if t1 + 3 < t < t1 + 6: tag(d, 60, 400, "ПЕРЕВОРОТ В ВОЗДУХЕ", CY, 30)
    if t > T - 3.0: big(d, W / 2, 560, "КАК?", WHITE, 220, ease((t - (T - 3.0)) / .5))

def sc_ceil(d, t, T):
    cy = 560; ceiling(d, cy); car(d, 540, cy, 0, 1.25, 1, -1)
    # присоска перечёркнута
    cx, c0 = 200, 960
    d.ellipse([(cx - 60) * K, (c0 - 30) * K, (cx + 60) * K, (c0 + 30) * K], fill=(120, 40, 50), outline=RED, width=3 * K); d.rectangle([(cx - 8) * K, (c0 + 30) * K, (cx + 8) * K, (c0 + 120) * K], fill=(120, 40, 50))
    if t > .8: d.line([(cx - 90) * K, (c0 - 60) * K, (cx + 90) * K, (c0 + 140) * K], fill=RED, width=10 * K); d.line([(cx + 90) * K, (c0 - 60) * K, (cx - 90) * K, (c0 + 140) * K], fill=RED, width=10 * K)
    tag(d, 90, 880, "ПРИСОСКА?  НЕТ", RED, 32, fill=(40, 10, 14))
    if t > 1.8:
        for xx in (460, 620, 780, 940):
            arrow(d, xx, 1260 - 10 * math.sin(t * 6 + xx), xx, 900, CY, 7)
        tag(d, 440, 1320, "ЕЁ ПРИЖИМАЕТ ВОЗДУХ", GRN, 34, fill=(6, 40, 30))
    gas(d, t, (0, cy + 140, W, 1250), 120, 7, 70, CY, 3)

def sc_tons(d, t, T):
    cx, cy, s = 540, 1000, 300
    box = (cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2)
    d.rectangle([b * K for b in box], outline=CY, width=4 * K, fill=(8, 24, 44))
    gas(d, t, box, 60, 9, 200, CY, 4, hits=[(box[0] - 2, box[1], box[0] + 2, box[3]), (box[2] - 2, box[1], box[2] + 2, box[3]), (box[0], box[1] - 2, box[2], box[1] + 2), (box[0], box[3] - 2, box[2], box[3] + 2)])
    tag(d, cx, cy + s / 2 + 30, "1 м²", CY, 34, anchor="c")
    for k in range(10):                                   # 10 блоков «1 т» падают на квадрат
        t0 = .5 + k * .32; u = seg(t, t0, t0 + .35)
        if u <= 0: continue
        yy = lerp(150, box[1] - 38 * (k + 1), u * u)
        d.rectangle([(cx - 150) * K, yy * K, (cx + 150) * K, (yy + 34) * K], fill=(60, 70, 90), outline=(200, 210, 225), width=2 * K)
        d.text(((cx - 22) * K, (yy + 4) * K), "1 т", font=F(22 * K, "Bold"), fill=WHITE)
    n = min(10, int(max(0, t - .5) / .32 + .5)); big(d, cx, 1290, f"≈ {n} ТОНН" if n < 10 else "≈ 10 ТОНН", YEL, 100, 1.0)

def sc_zero(d, t, T):
    cx, cy, s = 540, 800, 300
    box = (cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2); d.rectangle([b * K for b in box], outline=CY, width=4 * K, fill=(8, 24, 44))
    gas(d, t, box, 50, 9, 200, CY, 4)
    p = seg(t, .2, 1.0)
    for ang in range(0, 360, 45):
        a = math.radians(ang); r1 = (430 - 18 * math.sin(t * 6 + ang)) * p + 190 * (1 - p); r0 = 190
        arrow(d, cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r0 * math.cos(a), cy + r0 * math.sin(a), CY, 6)
    if t > 1.6: tag(d, cx, 1130, "СИЛЫ УРАВНОВЕШЕНЫ  Σ = 0", GRN, 36, fill=(6, 40, 30), anchor="c")
    gas(d, t, (0, 300, W, 1250), 70, 3, 60, (30, 110, 160), 2, avoid=lambda X, Y: box[0] - 40 < X < box[2] + 40 and box[1] - 40 < Y < box[3] + 40)

def gapscene(d, t, T, phase):
    cy = 420; s = 1.5; ceiling(d, cy)
    xc = 540; Tc = car(d, xc, cy, 0, s, 1, -1, xray=1, tt=t)
    gx0, gx1 = xc - 222 * s, xc + 228 * s; gy0, gy1 = cy, cy + 38 * s
    q = seg(t, .8, 3.5) if phase == 1 else 1.0                          # откачка зазора (0 → 1)
    # воздух под машиной — плотный, бьёт в крышу и днище кузова снизу
    nb = gas(d, t, (60, cy + 160, W - 60, 1060), 130, 4, 130, CY, 3.5,
             avoid=lambda X, Y: gx0 < X < gx1 and cy < Y < cy + 175)
    # зазор — редеет
    gas(d, t, (gx0 + 4, gy0 + 4, gx1 - 4, gy1 - 4), max(1, int(26 * (1 - .88 * q))), 12, 60, GRN, 3)
    for X0 in (gx0, gx1 - 8): d.rectangle([X0 * K, cy * K, (X0 + 8) * K, (cy + 40 * s) * K], fill=(120, 130, 150))   # уплотнения-«юбка»
    # потоки в вентиляторы и выхлоп назад
    if phase == 1 and q > .05:
        for k, fx in enumerate(FANS):
            fp = Tc((fx, -44))
            for j in range(3):
                u = (t * 1.4 + j / 3 + k * .2) % 1; px = fp[0] / K; py = cy + 8 + (1 - u) * 36
                circ(d, (px * K, py * K), 3 * K, fill=GRN)
        arrow(d, gx0 - 10, cy + 200, gx0 - 150, cy + 200, GRN, 6); tag(d, 40, cy + 215, "ВОЗДУХ ВЫХОДИТ", GRN, 22, fill=(6, 40, 30))
    # давление: два столбика
    bx = 70; by = 1150
    d.text((bx * K, (by - 64) * K), "ДАВЛЕНИЕ", font=F(24 * K, "Bold"), fill=(150, 170, 200))
    d.rectangle([bx * K, by * K, (bx + 200) * K, (by + 36) * K], outline=CY, width=2 * K); d.rectangle([bx * K, by * K, (bx + 200) * K, (by + 36) * K], fill=(20, 90, 130))
    d.text(((bx + 214) * K, (by + 2) * K), "СНИЗУ  100 %", font=F(26 * K, "Bold"), fill=CY)
    val = 1 - .88 * q
    d.rectangle([bx * K, (by + 56) * K, (bx + 200) * K, (by + 92) * K], outline=GRN, width=2 * K); d.rectangle([bx * K, (by + 56) * K, (bx + 200 * val) * K, (by + 92) * K], fill=(20, 130, 90))
    d.text(((bx + 214) * K, (by + 58) * K), "ЗАЗОР", font=F(26 * K, "Bold"), fill=GRN)
    return q

def sc_gap1(d, t, T): gapscene(d, t, T, 1)

def sc_gap2(d, t, T):
    q = gapscene(d, t, T, 2); cy = 420
    p = seg(t, .3, 1.2)
    for xx in (330, 440, 540, 640, 750):
        arrow(d, xx, 1010, xx, 1010 - 190 * p, CY, 9, 26)
    if t > 1.2: tag(d, 640, 1070, "РАЗНИЦА ДАВЛЕНИЙ → ПРИЖИМ", YEL, 28, fill=(40, 28, 6), anchor="c")
    if t > T - 3.6: big(d, 880, 1130 - 10, "до 2 g", YEL, 96, ease((t - (T - 3.6)) / .5))

def sc_nofuel(d, t, T):
    cx, cy = 540, 780
    for k, (dx, dy, s) in enumerate([(0, 0, 1), (-40, 40, .7), (40, 30, .75)]):          # пламя
        pts_ = [(cx + dx - 70 * s, cy + dy + 90 * s), (cx + dx - 30 * s, cy + dy - 30 * s), (cx + dx, cy + dy - 150 * s + 14 * math.sin(t * 14 + k)), (cx + dx + 40 * s, cy + dy - 20 * s), (cx + dx + 74 * s, cy + dy + 90 * s)]
        d.polygon([(a * K, b * K) for a, b in pts_], fill=[(255, 90, 30), (255, 150, 40), (255, 220, 90)][k])
    if t > .8:
        d.line([(cx - 170) * K, (cy - 190) * K, (cx + 170) * K, (cy + 190) * K], fill=RED, width=22 * K)
        d.line([(cx + 170) * K, (cy - 190) * K, (cx - 170) * K, (cy + 190) * K], fill=RED, width=22 * K)
    big(d, cx, 1090, "ТОПЛИВО  0", RED, 100, ease((t - 1.0) / .5))
    car(d, cx, 1330, 0, .75)

def sc_tanks(d, t, T):
    cx, cy = 540, 780; s = 1.55
    Tc = car(d, cx, cy, 0, s, 1, 1, xray=1, tt=t, jets=(), jt=t)
    # воздух в баллонах — плотный
    for (x0, yy, x1) in TANKS:
        a, b = Tc((x0 + 6, yy - 8)), Tc((x1 - 6, yy + 8)); gas(d, t, (min(a[0], b[0]) / K, min(a[1], b[1]) / K, max(a[0], b[0]) / K, max(a[1], b[1]) / K), 40, 3 + int(x0), 70, WHITE, 2)
    if t > .6:
        p = Tc((-130, -92)); leader(d, p, (120, 410), ORG); tag(d, 40, 380, "2 БАЛЛОНА", ORG, 30, fill=(40, 22, 6))
    if t > 2.6: tag(d, 40, 1040, "600 Л СЖАТОГО ВОЗДУХА", YEL, 32, fill=(40, 28, 6)); tag(d, 40, 1120, "≈ 250 КГ", YEL, 32, fill=(40, 28, 6))
    n = int(max(0, t - 5.2) / .32)
    for k, ((px, py), nn) in enumerate(NOZ):
        c = Tc((px, py)); on = k < n
        circ(d, c, 11 * K, fill=ORG if on else (90, 60, 30), outline=WHITE if on else None, width=2 * K)
        if on: d.text((c[0] + 12 * K, c[1] - 30 * K), str(k + 1), font=F(26 * K, "ExtraBold"), fill=YEL)
    if n >= 1: big(d, 540, 1290, f"{min(10, n)} / 10 СОПЕЛ", YEL, 90, 1.0)

def sc_flip(d, t, T):
    # кувырок: сопла работают сериями, воздух бьёт в одну сторону — машину крутит и толкает в другую
    ph = t / T; s = .95
    x = lerp(300, 780, ease(ph)); y = lerp(1000, 760, math.sin(ph * math.pi))
    a = -ease(max(0, (ph - .15) / .75)) * 2 * math.pi
    jets = (1, 3, 9) if .15 < ph < .55 else (0, 2, 8) if ph < .9 else ()
    Tc = car(d, x, y, a, s, 1, 1, xray=1, tt=t, jets=jets, jt=t)
    ground(d, 1300)
    if .15 < ph < .9:
        arrow(d, x - 280, 1180, x - 120, 1180, WHITE, 8); tag(d, 40, 1210, "ВОЗДУХ — ТУДА", WHITE, 28)
        arrow(d, x - 200, 1100, x - 40, 1100, CY, 8)
    tag(d, 40, 330, "СХЕМА", (110, 140, 170), 22)
    if ph > .15: tag(d, 540, 1380, "МАШИНА — В ПРОТИВОПОЛОЖНУЮ СТОРОНУ", CY, 30, anchor="c")

def sc_sat(d, t, T):
    bx, by = 540, 760; a = seg(t, .6, T - .5) * 2.2 * math.pi
    for sd, cols in ((-1, 0), (1, 0)):                       # солнечные панели
        pts_ = [rot(p, a) for p in [(sd * 80, -50), (sd * 330, -50), (sd * 330, 50), (sd * 80, 50)]]
        d.polygon([((bx + px) * K, (by + py) * K) for px, py in pts_], fill=(20, 50, 100), outline=CY)
    pts_ = [rot(p, a) for p in [(-80, -80), (80, -80), (80, 80), (-80, 80)]]
    d.polygon([((bx + px) * K, (by + py) * K) for px, py in pts_], fill=(214, 150, 40), outline=(255, 210, 120))
    for k in range(4):
        corner = [(-80, -80), (80, -80), (80, 80), (-80, 80)][k]; on = int(t * 4) % 4 == k and 0.6 < t < T - .5
        if on:
            c = rot(corner, a); dirv = rot((corner[0] / 80, corner[1] / 80), a)
            for j in range(8):
                u = (t * 3 + j / 8) % 1; circ(d, ((bx + c[0] + dirv[0] * 90 * u) * K, (by + c[1] + dirv[1] * 90 * u) * K), (7 - 5 * u) * K, fill=dim(WHITE, 1 - u))
    tag(d, 540, 1160, "ТАК ПОВОРАЧИВАЮТ КОСМИЧЕСКИЕ АППАРАТЫ", YEL, 26, anchor="c")

def sc_end(d, t, T):
    cx, cy = 540, 560
    d.rounded_rectangle([(cx - 200) * K, (cy - 200) * K, (cx + 200) * K, (cy + 140) * K], 30 * K, fill=(20, 28, 48), outline=YEL, width=5 * K)
    d.rectangle([(cx - 200) * K, (cy - 200) * K, (cx + 200) * K, (cy - 130) * K], fill=YEL)
    d.text(((cx - 100) * K, (cy - 195) * K), "ВЫПУСК", font=F(60 * K, "ExtraBold"), fill=(20, 20, 20))
    big(d, cx, cy - 115, "2028", WHITE, 170, ease(t / .6))
    car(d, 540, 980, 0, .9)
    if t > 5.2:
        tag(d, 540, 1110, "СЕЛ БЫ?", WHITE, 54, fill=(10, 20, 36), anchor="c")
        tag(d, 360, 1270, "ДА", GRN, 44, fill=(6, 40, 30)); tag(d, 600, 1270, "НЕТ", RED, 44, fill=(40, 10, 14))

SCENES = dict(hook=sc_hook, parts=sc_parts, event=sc_event, ceil=sc_ceil, tons=sc_tons, zero=sc_zero, gap1=sc_gap1, gap2=sc_gap2,
              nofuel=sc_nofuel, tanks=sc_tanks, flip=sc_flip, sat=sc_sat, end=sc_end)
