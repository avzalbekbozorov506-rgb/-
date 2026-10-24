"""«Взаимка» — мультфильм без слов (20 с): все подписываются друг на друга, подписчиков 100K, а просмотров 0.
Всё рисуется кодом (PIL/numpy), звук синтезируется кодом. Сценарий: scripts/mutual_1.md.
Запуск: python3 cartoon/mutual.py              → hq/mutual_1_hq.mp4 + covers/73_mutual_click.jpg
        python3 cartoon/mutual.py 0.3 9.8 16.5 → превью кадров work/mutual_1/pv_*.png"""
import os, sys, math, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
S = 1.5; W, H = 1080, 1920; CW, CH = int(W * S), int(H * S); FPS = 30; DUR = 20.0
INK = (28, 20, 46); BLUE = (30, 144, 255); GOLD = (255, 205, 60); PINK = (255, 90, 150); GREEN = (60, 205, 120)
PAL = [(255, 170, 90), (120, 200, 255), (190, 150, 255), (255, 130, 160), (110, 220, 170), (255, 220, 100), (150, 180, 255), (255, 160, 220)]
HERO = (255, 140, 40); CX, CY = 540, 880

def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def seg(t, a, b): return ease((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def back(x):  # выскок с перелётом
    x = min(max(x, 0.0), 1.0); c1 = 2.2; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def mix(a, b, k): return tuple(int(lerp(a[i], b[i], k)) for i in range(3))
_F = {}
def F(size):
    k = int(size * S)
    if k not in _F: _F[k] = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", max(k, 6))
    return _F[k]

class Cv:
    def __init__(s, im): s.im = im; s.d = ImageDraw.Draw(im, "RGBA")
    def P(s, pts): return [(x * S, y * S) for x, y in pts]
    def poly(s, pts, fill, outline=None, w=0):
        s.d.polygon(s.P(pts), fill=fill)
        if outline: s.d.line(s.P(list(pts) + [pts[0]]), fill=outline, width=max(int(w * S), 1), joint="curve")
    def ell(s, c, rx, ry, fill=None, outline=None, w=0):
        s.d.ellipse(((c[0] - rx) * S, (c[1] - ry) * S, (c[0] + rx) * S, (c[1] + ry) * S), fill=fill, outline=outline, width=max(int(w * S), 1) if outline else 0)
    def rr(s, b, r, fill=None, outline=None, w=0):
        s.d.rounded_rectangle((b[0] * S, b[1] * S, b[2] * S, b[3] * S), r * S, fill=fill, outline=outline, width=max(int(w * S), 1) if outline else 0)
    def line(s, pts, fill, w, caps=True):
        s.d.line(s.P(pts), fill=fill, width=max(int(w * S), 1), joint="curve")
        if caps:
            for p in (pts[0], pts[-1]): s.ell(p, w / 2, w / 2, fill=fill)
    def text(s, xy, t, size, fill, stroke=0, anchor="mm"):
        s.d.text((xy[0] * S, xy[1] * S), t, font=F(size), fill=fill, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=INK + (255,))

_bg = None
def background():
    global _bg
    if _bg is None:
        yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
        k = yy / CH; base = np.stack([lerp(24, 70, k), lerp(14, 22, k), lerp(52, 92, k)], -1)
        d = np.sqrt(((xx - CW / 2) / CW) ** 2 + ((yy - CH * 0.46) / CH) ** 2)
        glow = np.clip(1 - d * 2.2, 0, 1)[..., None] ** 2
        base = base + glow * np.array([70, 20, 60], np.float32)
        base *= (1 - 0.35 * np.clip(d * 1.6 - 0.35, 0, 1))[..., None]
        _bg = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(_bg, "RGB").convert("RGBA")

# ---------- иконки
def heart_pts(x, y, r):
    pts = []
    for i in range(41):
        a = i / 40 * 2 * math.pi
        pts.append((x + r * 16 * math.sin(a) ** 3 / 16, y - r * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16))
    return pts
def heart(c, x, y, r, col, outline=None):
    c.poly(heart_pts(x, y, r), col, outline, r * 0.12 if outline else 0)
def person(c, x, y, r, col):
    c.ell((x, y - r * 0.35), r * 0.38, r * 0.38, fill=col)
    c.d.pieslice(((x - r * 0.75) * S, (y + r * 0.1) * S, (x + r * 0.75) * S, (y + r * 1.4) * S), 180, 360, fill=col)
def eye_icon(c, x, y, r, col):
    c.ell((x, y), r, r * 0.6, outline=col, w=r * 0.18); c.ell((x, y), r * 0.3, r * 0.3, fill=col)
def bubble(c, x, y, r, col):
    c.rr((x - r, y - r * 0.7, x + r, y + r * 0.5), r * 0.35, outline=col, w=r * 0.18)
    c.poly([(x - r * 0.5, y + r * 0.45), (x - r * 0.7, y + r * 0.95), (x - r * 0.05, y + r * 0.45)], col)
def check(c, x, y, r, col, w):
    c.line([(x - r * 0.5, y), (x - r * 0.1, y + r * 0.4), (x + r * 0.55, y - r * 0.4)], col, w)
def plus(c, x, y, r, col, w):
    c.line([(x - r, y), (x + r, y)], col, w); c.line([(x, y - r), (x, y + r)], col, w)
def cursor(c, x, y, sc, press=0):
    pts = [(0, 0), (0, 44), (11, 34), (19, 52), (28, 48), (20, 31), (34, 31)]
    c.poly([(x + px * sc * (1 - 0.1 * press), y + py * sc * (1 - 0.1 * press)) for px, py in pts], (255, 255, 255), INK, 3 * sc)
def crown(c, x, y, r):
    c.poly([(x - r, y + r * 0.5), (x - r, y - r * 0.4), (x - r * 0.5, y + r * 0.05), (x, y - r * 0.7), (x + r * 0.5, y + r * 0.05), (x + r, y - r * 0.4), (x + r, y + r * 0.5)], GOLD, INK, r * 0.07)
    for dx in (-0.5, 0, 0.5): c.ell((x + dx * r * 2, y + r * 0.22), r * 0.09, r * 0.09, fill=PINK)

def avatar(c, x, y, r, col, look=(0, 0), m=1.0, blink=0.0, alpha=1.0):
    if r < 3: return
    sh = int(70 * alpha); c.ell((x, y + r * 1.02), r * 0.8, r * 0.13, fill=(0, 0, 0, sh))
    out = INK + (int(255 * alpha),); body = tuple(col) + (int(255 * alpha),)
    c.ell((x, y), r, r, fill=body, outline=out, w=max(r * 0.06, 1.5))
    c.ell((x - r * 0.35, y - r * 0.5), r * 0.32, r * 0.18, fill=(255, 255, 255, int(70 * alpha)))
    for sx in (-1, 1):
        ex, ey = x + sx * r * 0.36, y - r * 0.08
        c.ell((ex, ey), r * 0.24, max(r * 0.29 * (1 - blink), r * 0.03), fill=(255, 255, 255, int(255 * alpha)), outline=out, w=max(r * 0.03, 1))
        if blink < 0.6:
            px, py = ex + look[0] * r * 0.1, ey + look[1] * r * 0.13
            c.ell((px, py), r * 0.115, r * 0.125, fill=out); c.ell((px - r * 0.035, py - r * 0.045), r * 0.04, r * 0.04, fill=(255, 255, 255, int(255 * alpha)))
    pts = []
    for i in range(13):
        u = i / 6 - 1; pts.append((x + u * r * 0.3, y + r * 0.38 + m * r * 0.15 * (1 - u * u) - abs(m) * 0.0))
    c.line(pts, out, max(r * 0.06, 2))
    if m > 0.5: c.ell((x - r * 0.62, y + r * 0.22), r * 0.12, r * 0.07, fill=(255, 90, 120, int(110 * alpha))); c.ell((x + r * 0.62, y + r * 0.22), r * 0.12, r * 0.07, fill=(255, 90, 120, int(110 * alpha)))

def pill(c, x, y, txt, col=(255, 255, 255), sc=1.0, bg=(20, 12, 40, 230)):
    w = (46 + 24 * len(txt)) * sc; h = 54 * sc
    c.rr((x - w / 2, y - h / 2, x + w / 2, y + h / 2), h / 2, fill=bg, outline=(255, 255, 255, 60), w=2)
    person(c, x - w / 2 + 28 * sc, y + 2 * sc, 15 * sc, col); c.text((x + 16 * sc, y + 1), txt, 30 * sc, col)

def fmt(n):
    if n < 1000: return str(int(n))
    if n < 10000: return f"{n / 1000:.1f}K".replace(".0K", "K")
    if n < 1000000: return f"{int(n / 1000)}K"
    return "1M"

# ---------- мир: кольца аватаров
RINGS = [(14, 330, 62, -90), (26, 560, 62, -90 + 7), (36, 790, 58, -90 + 3)]
AV = []  # (x, y, r, color, spawn_t)
for ri, (n, R, r, a0) in enumerate(RINGS):
    for k in range(n):
        a = math.radians(a0 + 360 * k / n); AV.append([CX + R * math.cos(a), CY + R * math.sin(a), r, ri, k, a])
N = len(AV)
for i, a in enumerate(AV):
    a.append(1.5 + (i / N) ** 1.7 * 6.5 if i > 1 else (0.0 if i == 0 else 0.9))
    a.append(HERO if i == 0 else PAL[(i * 3 + i // 8) % len(PAL)])
def cnt(t):  # число подписчиков по времени
    if t < 1.5: return 0
    if t < 2.2: return 1 if t >= 1.5 else 0
    if t < 8: return 1 + sum(1 for a in AV[2:] if a[6] <= t) + 1
    if t < 11.4: return int(math.exp(lerp(math.log(N), math.log(100000), seg(t, 8, 11.4))))
    return 100000
MILES = [(10, "10"), (50, "50"), (100, "100"), (1000, "1K"), (10000, "10K"), (100000, "100K")]
def mile_times():
    out = []; t = 1.5
    for v, _ in MILES:
        tt = 0.0
        while cnt(tt) < v: tt += 1 / 120
        out.append(tt)
    return out
def zoom(t):
    if t < 4.5: return 1.0
    if t < 9: return lerp(1.0, 0.6, seg(t, 4.5, 9))
    if t < 14: return 0.6
    return lerp(0.6, 0.5, seg(t, 14, 16))
def cam(x, y, z): return CX + (x - CX) * z, CY + (y - CY) * z

CONF = []
rng = np.random.RandomState(7)
for i in range(150):
    CONF.append((rng.uniform(-1, 1), rng.uniform(0.3, 1.0), rng.uniform(5, 14), rng.uniform(0, 6.28), rng.uniform(-6, 6), [PINK, GOLD, BLUE, GREEN, (255, 255, 255)][i % 5]))
def confetti(c, t0, t):
    if t < t0 or t - t0 > 3.2: return
    tt = t - t0
    for vx, vy, sz, a0, om, col in CONF:
        x = CX + vx * 520 * tt ** 0.7; y = 760 - vy * 780 * tt + 700 * tt * tt
        a = a0 + om * tt; dx, dy = math.cos(a) * sz, math.sin(a) * sz
        c.poly([(x - dx, y - dy), (x + dy * 0.5, y - dx * 0.5), (x + dx, y + dy), (x - dy * 0.5, y + dx * 0.5)], col + (int(255 * min(1, (3.2 - tt) * 2)),))
def burst(c, x, y, t0, t, n=9, big=46):
    if t < t0 or t - t0 > 0.9: return
    k = (t - t0) / 0.9
    for i in range(n):
        a = i / n * 6.283 + 0.4; d = 40 + 190 * ease(k)
        heart(c, x + math.cos(a) * d, y + math.sin(a) * d - 30 * k, big * (1 - k) * (0.6 + 0.4 * (i % 2)), PINK + (int(255 * (1 - k)),))

T_FOLLOW = 1.5; T_HEART = 16.2; T_EYE = 16.0; T_TAP = 18.5
MT = None

def frame(t):
    global MT
    if MT is None: MT = mile_times()
    im = background(); c = Cv(im); z = zoom(t)
    n_now = cnt(t); sad = seg(t, 11.8, 13.2)
    # 1) стрелки «все на всех» вдоль колец
    ringfade = 1 - 0.8 * seg(t, 14, 15.2)
    if t > 2.2:
        for ri, (n, R, r, a0) in enumerate(RINGS):
            idx = [i for i, a in enumerate(AV) if a[3] == ri]
            for j, i in enumerate(idx):
                i2 = idx[(j + 1) % n]
                if AV[i][6] > t or AV[i2][6] > t: continue
                for dirn, off, col in ((1, 22, (255, 255, 255)), (-1, -22, (255, 120, 190))):
                    ph = (t * 0.8 * dirn + j * 0.13) % 1.0 if dirn > 0 else (1 - (t * 0.8 + j * 0.13) % 1.0)
                    aa = AV[i][5] + (AV[i2][5] - AV[i][5] + (2 * math.pi if j == n - 1 else 0)) * (0.22 + 0.56 * ph)
                    px, py = cam(CX + (R + off) * math.cos(aa), CY + (R + off) * math.sin(aa), z)
                    tx, ty = -math.sin(aa) * dirn, math.cos(aa) * dirn; nx, ny = math.cos(aa), math.sin(aa); s = 14 * z + 3
                    c.line([(px - tx * s - nx * s * 0.8 * 0 + nx * s * 0.7, py - ty * s + ny * s * 0.7), (px + tx * s * 0.6, py + ty * s * 0.6), (px - tx * s - nx * s * 0.7, py - ty * s - ny * s * 0.7)], col + (int(200 * ringfade),), max(5 * z, 2.5))
    # 2) аватары
    order = sorted(range(N), key=lambda i: -AV[i][2])
    for i in order:
        x0, y0, r0, ri, k, a, ts, col = AV[i]
        if t < ts: continue
        if i == 0:
            hx, hy, hr = lerp(400, x0, seg(t, 2.2, 3.4)), lerp(960, y0, seg(t, 2.2, 3.4)), lerp(150, r0, seg(t, 2.2, 3.4))
            if t < 2.2: hx, hy, hr = 400 - 40 * (1 - ease(seg(t, 0, 1.2))) * 0, 960, 150
            continue  # герой рисуется поверх всего
        if i == 1:
            x0 = lerp(680, x0, seg(t, 2.2, 3.4)); y0 = lerp(960, y0, seg(t, 2.2, 3.4)); r0 = lerp(150, r0, seg(t, 2.2, 3.4))
        pop = back((t - ts) / 0.35)
        x, y = cam(x0, y0, z); r = r0 * z * pop * (1.0 if i != 1 else 1.0)
        if i > 1 and t < 8 and i % 7 == 0 and ts + 0.35 > t: pass
        look = (0, 0.3) if t < 11.8 else (0, 0.9 * seg(t, 11.8, 12.6))
        if t < 11.8: look = (math.sin(t * 2 + i) * 0.4, math.cos(t * 1.3 + i * 2) * 0.3)
        m = 1.0 - 2.0 * sad if t < 14 else 1.0 - 2.0 * sad + 0.0
        if t >= 14: m = lerp(-1.0, -0.3, seg(t, 14, 16))
        blink = 0.9 if (t * 0.9 + i * 0.37) % 3.1 < 0.12 else 0.0
        dim = 1.0 if t < 14 else 1 - 0.55 * seg(t, 14, 15.2)
        avatar(c, x, y, r, col, look, m, blink, dim)
    # 3) счётчик в центре
    if t >= 2.2:
        k = back((t - 2.2) / 0.5); big = 150 + 40 * seg(t, 2.2, 3) * 0
        scl = 1.0 + 0.06 * math.sin(t * 9) * (1 if t < 11.4 else 0)
        col = GOLD if t >= 11.4 else (255, 255, 255)
        if t >= 14: col = mix(GOLD, (200, 200, 220), 0)
        yy = CY + 0 + 10 * math.sin(t * 3) * (t < 11.4)
        if t >= 14: yy = lerp(CY, 330, seg(t, 14, 15.2))
        c.rr((CX - 330 * k, yy - 118 * k, CX + 330 * k, yy + 118 * k), 70 * k, fill=(20, 10, 40, int(215 * (1 - 0.0))), outline=(255, 255, 255, 70), w=3)
        if t < 14 or True:
            person(c, CX - 230 * k, yy + 6, 50 * k, col)
            c.text((CX + 40, yy + 6), fmt(n_now), int(150 * k * scl) if n_now < 1000 else int(130 * k * scl), col, stroke=5)
        if t >= 11.4: crown(c, CX, yy - 180 * k, 74 * k * (0.6 + 0.4 * seg(t, 11.4, 11.9)))
    # 4) нули: просмотры, лайки, комментарии
    if t >= 6.0:
        k = seg(t, 6.0, 6.8)
        base_y = lerp(2050, 1640, k)
        if t >= 14: base_y = lerp(1640, 1400, seg(t, 14, 15.0))
        shake = 8 * math.sin(t * 40) * seg(t, 11.5, 12.0) * (1 - seg(t, 13.5, 14)) if 11.5 < t < 14 else 0
        red = seg(t, 11.5, 12.2) * (1 - seg(t, 14.5, 15.0))
        vals = [("eye", 0 if t < T_EYE else 1, -270), ("heart", 0 if t < T_HEART else 1, 0), ("bub", 0, 270)]
        for kind, v, dx in vals:
            x = CX + dx + shake; y = base_y
            col = mix((150, 150, 175), (255, 80, 90), red)
            if v == 1 and t >= 14: col = mix((150, 150, 175), GOLD, ease((t - (T_HEART if kind == "heart" else T_EYE)) / 0.3))
            c.rr((x - 120, y - 56, x + 120, y + 56), 56, fill=(20, 10, 40, 200), outline=col + (120,), w=3)
            ix = x - 62
            if kind == "eye": eye_icon(c, ix, y, 34, col)
            elif kind == "heart":
                pp = 1.0 + 0.5 * math.sin(min(max((t - T_HEART) / 0.35, 0), 1) * 3.14) if t >= T_HEART else 1.0
                heart(c, ix, y, 36 * pp, col)
            else: bubble(c, ix, y + 4, 33, col)
            c.text((x + 36, y + 3), str(v), 52, col)
    # 5) перекати-поле
    if 12.2 < t < 15.3:
        k = (t - 12.2) / 3.1; x = lerp(-150, 1250, k); y = 1535 - abs(math.sin(k * 14)) * 60; rot = k * 40
        for i in range(7):
            a = rot + i * 0.9
            c.line([(x + math.cos(a) * 12, y + math.sin(a) * 12), (x + math.cos(a + 1.1) * 52, y + math.sin(a + 1.1) * 52), (x + math.cos(a - 0.4) * 62, y + math.sin(a - 0.4) * 48)], (170, 130, 80, 230), 5)
        c.ell((x, y), 40, 40, outline=(170, 130, 80, 230), w=5)
    # 6) конфетти
    confetti(c, MT[5] if MT else 11.4, t)
    # 7) вспышка «взаимной подписки» вначале
    # 8) герой
    sc_h = 1.0
    if t < 14:
        if t < 2.2: hx, hy, hr = 400, 960, 150
        else: hx, hy = cam(lerp(400, AV[0][0], seg(t, 2.2, 3.4)) if t < 3.4 else AV[0][0], lerp(960, AV[0][1], seg(t, 2.2, 3.4)) if t < 3.4 else AV[0][1], z); hr = lerp(150, 62, seg(t, 2.2, 3.4)) * (z if t > 3.4 else 1)
        if t >= 3.4: hx, hy = cam(AV[0][0], AV[0][1], z); hr = 62 * z * 1.25
        elif t >= 2.2: hx, hy = lerp(400, cam(AV[0][0], AV[0][1], zoom(3.4))[0], seg(t, 2.2, 3.4)), lerp(960, cam(AV[0][0], AV[0][1], zoom(3.4))[1], seg(t, 2.2, 3.4))
        look = (1.0, 0.0) if t < 0.9 else ((0.6, 0.4) if t < 1.4 else (0, 0.2))
        if t > 3.4: look = (math.sin(t * 2) * 0.4, 0.3)
        m = 0.9 if t >= T_FOLLOW else -0.4
        if t < T_FOLLOW: m = -0.2 + 0.0
        if t > 11.8: m = 1 - 2.0 * sad
        if t < 0.9 and t > 0.0: m = -0.6
        bl = 0.9 if (t % 2.6) < 0.1 else 0.0
        hpop = back(t / 0.4) if t < 0.4 else 1.0
        avatar(c, hx, hy, hr * hpop, HERO, look, m, bl)
        if t < 2.4:
            hb = hr * 0.78
            pulse = 1 + 0.12 * math.sin(t * 10)
            for who, (bx, by) in ((0, (hx + hr * 0.75, hy + hr * 0.85)),) + (((1, (680 + 150 * 0.75, 960 + 150 * 0.85)),) if t >= 0.9 else ()):
                done = t >= T_FOLLOW + 0.1
                k2 = 1.0 if who == 0 else back((t - 0.9) / 0.35)
                c.ell((bx, by), 56 * pulse * k2 if not done else 56 * k2, 56 * pulse * k2 if not done else 56 * k2, fill=(GREEN if done else BLUE) + (255,), outline=(255, 255, 255, 255), w=6)
                if done: check(c, bx, by, 44, (255, 255, 255), 10)
                else: plus(c, bx, by, 26, (255, 255, 255), 10)
            pill(c, hx, hy - hr - 60, "1" if t >= T_FOLLOW else "0", sc=1.2)
            if t >= 0.9: pill(c, 680, 960 - 150 - 60, "1" if t >= T_FOLLOW else "0", sc=1.2)
            if 0.9 <= t < T_FOLLOW + 0.2:
                k3 = seg(t, 0.95, T_FOLLOW); cursor(c, lerp(900, 680 + 150 * 0.75 + 10, k3), lerp(1250, 960 + 150 * 0.85 + 10, k3), 2.0, press=1 if abs(t - T_FOLLOW) < 0.08 else 0)
            burst(c, 540, 960, T_FOLLOW + 0.05, t, big=44)
    else:
        # герой выходит из кольца к зрителю
        k = seg(t, 14, 15.4)
        sx, sy = cam(AV[0][0], AV[0][1], zoom(14)); hx, hy = lerp(sx, 540, k), lerp(sy, 1010, k); hr = lerp(62 * 0.6 * 1.25, 200, k)
        look = (0, 0.0) if t > 15.4 else (0, 0.6 * (1 - k))
        m = lerp(-0.6, 1.0, seg(t, 15.0, 15.6))
        wob = 8 * math.sin(t * 4)
        avatar(c, hx, hy + wob, hr, HERO, look, m, 0.9 if (t % 2.4) < 0.1 else 0)
        if k > 0.7:  # телефон-«ролик» в руке (вставлен справа)
            kk = back((t - 15.0) / 0.5); px, py = hx + hr * 1.5, hy + hr * 0.2
            c.rr((px - 105 * kk, py - 170 * kk, px + 105 * kk, py + 170 * kk), 26 * kk, fill=(30, 20, 60), outline=(255, 255, 255), w=7)
            c.rr((px - 90 * kk, py - 150 * kk, px + 90 * kk, py + 150 * kk), 14 * kk, fill=mix(PINK, GOLD, 0.4))
            c.poly([(px - 28 * kk, py - 44 * kk), (px - 28 * kk, py + 44 * kk), (px + 50 * kk, py)], (255, 255, 255))
        if t > T_EYE - 0.3: burst(c, hx - 250, 1400 - 70, T_HEART, t, n=7, big=38)
    # 9) финальная кнопка-подсказка
    if t >= 16.9:
        k = back((t - 16.9) / 0.5); pul = 1 + 0.08 * math.sin(t * 9)
        done = t >= T_TAP + 0.12
        by = 1700
        # стрелка вниз от героя
        for j in range(3):
            ph = (t * 1.6 - j * 0.25) % 1.0; ay = 1500 + ph * 110
            c.line([(CX - 38, ay), (CX, ay + 36), (CX + 38, ay)], (255, 255, 255, int(255 * (1 - ph) * k)), 14)
        rad = 78 * k * (pul if not done else 1.0)
        c.ell((CX, by), rad, rad, fill=(GREEN if done else BLUE) + (255,), outline=(255, 255, 255, 255), w=8)
        if done: check(c, CX, by, 60 * k, (255, 255, 255), 14)
        else: plus(c, CX, by, 34 * k, (255, 255, 255), 14)
        if t < T_TAP + 0.5:
            k3 = seg(t, 17.6, T_TAP); cursor(c, lerp(850, CX + 30, k3), lerp(1850, by + 30, k3), 2.4, press=1 if abs(t - T_TAP) < 0.1 else 0)
        burst(c, CX, by - 40, T_TAP + 0.1, t, n=10, big=50)
        if t > T_TAP + 0.4:
            hh = seg(t, T_TAP + 0.4, T_TAP + 0.9)
            for i in range(5):
                x = 140 + i * 200; heart(c, x, 1560 - 20 * math.sin(t * 5 + i) , 28 * hh, PINK + (int(220 * hh),))
    out = im.convert("RGB").resize((W, H), Image.LANCZOS)
    # лёгкое виньетирование/затемнение в конце цикла
    if t > DUR - 0.25:
        out = Image.blend(out, Image.new("RGB", (W, H), (0, 0, 0)), (t - (DUR - 0.25)) / 0.25 * 0.0)
    return out

# ---------- звук
SR = 44100
def env(n, a=0.002, d=0.1):
    t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def put(buf, t0, sig, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    j = min(i + len(sig), len(buf)); buf[i:j] += sig[:j - i] * g
def tone(f, dur, d=0.15, harm=((1, 1),)):
    t = np.arange(int(dur * SR)) / SR; s = sum(a * np.sin(2 * np.pi * f * h * t) for h, a in harm); return s * env(len(t), 0.003, d)
def pop(f0, f1, dur=0.09):
    t = np.arange(int(dur * SR)) / SR; f = f0 + (f1 - f0) * (t / dur); ph = 2 * np.pi * np.cumsum(f) / SR; return np.sin(ph) * env(len(t), 0.001, dur / 3)
def bell(f, dur=1.0): return tone(f, dur, 0.35, ((1, 1), (2.76, .35), (5.4, .15)))
def kick():
    t = np.arange(int(0.25 * SR)) / SR; f = 130 * np.exp(-t * 18) + 45; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def hat():
    n = int(0.05 * SR); x = np.random.RandomState(3).randn(n); x = np.diff(x, prepend=0); return x * np.exp(-np.arange(n) / SR * 90) * 0.35
def pluck(f, dur=0.22):
    t = np.arange(int(dur * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sign(np.sin(2 * np.pi * f * t))) * np.exp(-t * 14)
def wah(f0, f1, dur):
    t = np.arange(int(dur * SR)) / SR; f = f0 + (f1 - f0) * (t / dur) + 4 * np.sin(2 * np.pi * 6 * t) * (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR; s = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.33 * np.sin(3 * ph)) * 0.6
    return s * np.minimum(t / 0.03, 1) * np.minimum((dur - t) / 0.06, 1)

def make_audio(path):
    buf = np.zeros(int(DUR * SR) + SR)
    mt = mile_times()
    # ритм 1.5–11.4 (ускоряется)
    bpm = 118; beat = 60 / bpm; scale = [196, 233.1, 261.6, 293.7, 349.2, 392, 466.2, 523.3]
    tt = 1.5; b = 0
    while tt < 11.4:
        if b % 2 == 0 or tt > 8: put(buf, tt, kick(), 0.55)
        put(buf, tt + beat / 2, hat(), 0.5)
        put(buf, tt, pluck(scale[[0, 2, 4, 2, 3, 5, 4, 2][b % 8]] * 0.5, 0.3), 0.18)
        if tt > 5: put(buf, tt + beat / 2, pluck(scale[[4, 5, 7, 5][b % 4]], 0.15), 0.1)
        tt += beat; b += 1
    # хлопки «поп»
    for i, a in enumerate(AV):
        if i == 0: continue
        ts = a[6]
        if ts < 11: put(buf, ts, pop(380 + (i % 7) * 70, 900 + (i % 7) * 90), 0.4)
    put(buf, 0.0, pop(200, 700, 0.12), 0.4)
    put(buf, T_FOLLOW, bell(1318), 0.5); put(buf, T_FOLLOW + 0.08, bell(1760), 0.35)
    for k, tm in enumerate(mt): put(buf, tm, bell(880 * 2 ** (k / 6.0), 0.9), 0.35)
    # фанфара на 100K
    for k, f in enumerate((523, 659, 784, 1047)): put(buf, mt[5] + 0.06 * k, tone(f, 0.6, 0.3, ((1, 1), (2, .4), (3, .2))), 0.3)
    # обрыв: скретч
    t = np.arange(int(0.45 * SR)) / SR; f = 1800 * np.exp(-t * 5); sc = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + np.random.RandomState(5).randn(len(t)) * 0.05
    put(buf, 11.7, sc * np.exp(-t * 3), 0.7)
    buf[int(11.7 * SR):int(12.1 * SR)] *= 1.0
    # сверчки
    for tm in np.arange(12.3, 14.0, 0.42):
        for j in range(3): put(buf, tm + j * 0.07, tone(4300, 0.05, 0.02), 0.07)
    # грустная труба
    for tm, f0, f1, dur in ((12.8, 311, 294, 0.45), (13.3, 294, 277, 0.45), (13.8, 277, 262, 0.45), (14.25, 262, 196, 1.0)): put(buf, tm, wah(f0, f1, dur), 0.18)
    # тёплый пэд героя
    for f in (261.6, 329.6, 392): put(buf, 14.5, np.sin(2 * np.pi * f * np.arange(int(5.5 * SR)) / SR) * np.minimum(np.arange(int(5.5 * SR)) / SR / 1.2, 1) * 0.07)
    put(buf, T_EYE, bell(1568, 0.8), 0.35); put(buf, T_HEART, bell(1976, 1.2), 0.6); put(buf, T_HEART + 0.1, bell(2637, 1.2), 0.35)
    put(buf, 17.0, pop(300, 1000, 0.15), 0.5)
    put(buf, T_TAP, tone(900, 0.04, 0.02), 0.6)
    for k, f in enumerate((784, 988, 1175, 1568)): put(buf, T_TAP + 0.1 + 0.08 * k, bell(f, 0.9), 0.4)
    buf = np.tanh(buf * 1.4) * 0.8
    pk = np.abs(buf).max(); buf = buf / pk * 0.89
    buf = buf[:int(DUR * SR)]
    st = (np.stack([buf, buf], 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

def render_frame(i): return frame(i / FPS).tobytes()

if __name__ == "__main__":
    work = os.path.join(ROOT, "work", "mutual_1"); os.makedirs(work, exist_ok=True)
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            frame(float(a)).save(os.path.join(work, f"pv_{float(a):05.2f}.png"))
        sys.exit()
    wav = os.path.join(work, "audio.wav"); make_audio(wav)
    raw = os.path.join(work, "raw.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                           "-shortest", "-movflags", "+faststart", os.path.join(ROOT, "hq", "mutual_1_hq.mp4")], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for b in p.imap(render_frame, range(int(DUR * FPS)), chunksize=4): ff.stdin.write(b)
    ff.stdin.close(); ff.wait()
    frame(9.9).convert("RGB").save(os.path.join(ROOT, "covers", "73_mutual_click.jpg"), quality=92)
    print("OK")
