"""Изометрическая 2.5D-комната кодом (бесплатно): проекция, коробки с гранями, спальня с роутером, кольца волн, подписи HUD.
Для ролика wifi_1 («Простым языком»)."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import bh_cine as B
from bh_cine import W, H, ease, seg, lerp, fnt
RX, RY, RZ = 1.7, 0.7, 0.72          # роутер в системе комнаты
class Iso:
    """Изометрия с медленным поворотом камеры (yaw, рад) вокруг центра комнаты — даёт ощущение настоящей 3D-сцены."""
    def __init__(s, S=78.0, cx=540.0, cy=700.0, yaw=0.0): s.S, s.cx, s.cy, s.yaw = S, cx, cy, yaw
    def p(s, x, y, z=0.0):
        if s.yaw:
            c, sn = math.cos(s.yaw), math.sin(s.yaw); dx, dy = x - 3.0, y - 3.0; x, y = 3.0 + dx * c - dy * sn, 3.0 + dx * sn + dy * c
        return (s.cx + (x - y) * 0.866 * s.S, s.cy + (x + y) * 0.5 * s.S - z * s.S)
def poly(d, pts, fill, outline=None, w=2): d.polygon(pts, fill=fill, outline=outline)
def box(d, I, x, y, z, w, dp, h, top, left, right, edge=None):
    P = I.p; x1, y1, z1 = x + w, y + dp, z + h
    poly(d, [P(x, y1, z), P(x1, y1, z), P(x1, y1, z1), P(x, y1, z1)], left, edge)       # грань y = y1
    poly(d, [P(x1, y, z), P(x1, y1, z), P(x1, y1, z1), P(x1, y, z1)], right, edge)      # грань x = x1
    poly(d, [P(x, y, z1), P(x1, y, z1), P(x1, y1, z1), P(x, y1, z1)], top, edge)         # верх
def room(lt, I, wall_a=150, dim=1.0, plug=1.0, leds=True, window=True):
    """Тёмная спальня: пол с сеткой, две стены, кровать, тумбочка, роутер на ней, розетка и шнур."""
    im = Image.new("RGBA", (W, H), (6, 9, 18, 255)); d = ImageDraw.Draw(im, "RGBA"); P = I.p
    sc = lambda c: tuple(int(v * dim) for v in c)
    N = 6
    poly(d, [P(0, 0), P(N, 0), P(N, N), P(0, N)], sc((14, 22, 40, 255)))
    for k in range(N + 1):
        d.line([P(k, 0), P(k, N)], fill=(30, 60, 90, 120), width=1); d.line([P(0, k), P(N, k)], fill=(30, 60, 90, 120), width=1)
    zt = 3.0
    poly(d, [P(0, 0, 0), P(N, 0, 0), P(N, 0, zt), P(0, 0, zt)], (12, 20, 38, wall_a), (50, 110, 150, 200))     # правая задняя (y=0)
    poly(d, [P(0, 0, 0), P(0, N, 0), P(0, N, zt), P(0, 0, zt)], (10, 17, 33, wall_a), (50, 110, 150, 200))     # левая задняя (x=0)
    if window:
        glow = 0.6 + 0.1 * math.sin(lt * 0.7)
        poly(d, [P(0, 2.2, 1.0), P(0, 4.2, 1.0), P(0, 4.2, 2.3), P(0, 2.2, 2.3)], (int(40 * glow), int(70 * glow), int(120 * glow), 235), (120, 180, 230, 255))
        d.line([P(0, 3.2, 1.0), P(0, 3.2, 2.3)], fill=(120, 180, 230, 255), width=2)
    box(d, I, 2.6, 0.15, 0, 3.2, 2.2, 0.55, (46, 78, 140, 255), (30, 52, 100, 255), (24, 42, 84, 255), (90, 140, 210, 255))        # кровать
    box(d, I, 2.75, 0.3, 0.55, 0.9, 1.2, 0.18, (170, 190, 230, 255), (120, 140, 190, 255), (96, 116, 166, 255))                       # подушка
    box(d, I, 1.2, 0.15, 0, 1.0, 1.0, 0.62, (58, 66, 88, 255), (40, 46, 64, 255), (32, 38, 54, 255), (110, 130, 170, 255))            # тумбочка
    box(d, I, 1.42, 0.38, 0.62, 0.56, 0.5, 0.1, (46, 54, 70, 255), (28, 34, 46, 255), (22, 28, 38, 255), (120, 150, 190, 255))        # роутер
    for k in range(3):                                                                                                                 # антенны
        ax = 1.5 + 0.22 * k; a0 = P(ax, 0.5, 0.72); a1 = P(ax - 0.06 + 0.06 * k, 0.5, 1.45); d.line([a0, a1], fill=(150, 175, 215, 255), width=5)
    if leds:
        for k in range(3):
            on = 0.5 + 0.5 * math.sin(lt * 5 + k * 1.3); q = P(1.55 + 0.17 * k, 0.88, 0.7); d.ellipse((q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4), fill=(60, int(150 + 100 * on), 90, 255))
    sock = P(0.9, 0.0, 0.35); poly(d, [P(0.8, 0, 0.27), P(1.0, 0, 0.27), P(1.0, 0, 0.45), P(0.8, 0, 0.45)], (30, 38, 52, 255), (120, 150, 190, 255))
    pg = (0.0, 0.0)
    if plug < 1.0: pg = (0.0, 0.0)
    cord_end = P(0.9, 0.0 - 0.55 * (1 - plug) * 0 , 0.36 + 0.55 * (1 - plug)) if False else P(0.9, 0.02 + 0.9 * (1 - plug), 0.36 + 0.3 * (1 - plug))
    d.line([P(1.5, 0.45, 0.62), P(1.2, 0.5, 0.2), cord_end], fill=(20, 24, 30, 255), width=5)
    # --- кино-свет: лунный свет из окна, тёплое свечение роутера, объёмный туман, пыль
    lt_lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lt_lay)
    shaft = [P(0, 2.2, 1.0), P(0, 4.2, 1.0), P(3.6, 5.6, 0.0), P(1.8, 3.4, 0.0)]
    ld.polygon([P(0, 2.2, 2.3), P(0, 4.2, 2.3), P(3.2, 5.9, 0.0), P(1.2, 3.2, 0.0)], fill=(120, 170, 255, int(34 * dim)))
    im.alpha_composite(lt_lay.filter(ImageFilter.GaussianBlur(26)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow); rp = P(RX, RY, RZ)
    for r_, a_ in ((320, 20), (210, 30), (110, 46)): gd.ellipse((rp[0] - r_, rp[1] - r_ * 0.55, rp[0] + r_, rp[1] + r_ * 0.55), fill=(60, 255, 200, int(a_ * dim)))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
    hz = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hz)
    for k in range(4):
        cxh = 540 + 280 * math.sin(lt * 0.17 + k * 1.7); cyh = 760 + 140 * math.cos(lt * 0.13 + k * 2.3); hd.ellipse((cxh - 300, cyh - 150, cxh + 300, cyh + 150), fill=(70, 110, 190, 16))
    im.alpha_composite(hz.filter(ImageFilter.GaussianBlur(60)))
    dl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dl); rng = np.random.default_rng(11)
    for k in range(46):
        px = (rng.uniform(0, W) + 12 * lt * rng.uniform(-1, 1)) % W; py = 330 + ((rng.uniform(0, 780) - 9 * lt * rng.uniform(0.3, 1)) % 780); r_ = rng.uniform(1.2, 3.2)
        dd.ellipse((px - r_, py - r_, px + r_, py + r_), fill=(190, 225, 255, int(70 + 60 * math.sin(lt * 1.3 + k))))
    im.alpha_composite(dl.filter(ImageFilter.GaussianBlur(1.1)))
    return im, sock, cord_end
def rings(im, I, r0, n=5, spread=0.9, a=1.0, col=(80, 230, 200), z=RZ, cx=RX, cy=RY, fade=2.6, width=4):
    """Кольца волны в горизонтальной плоскости, яркость падает с радиусом."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(n):
        r = (r0 + k * spread) % (n * spread) + 0.15
        al = a * max(0.0, 1 - r / (n * spread)) ** 1.2
        if al < 0.03: continue
        pts = [I.p(cx + r * math.cos(t), cy + r * math.sin(t), z) for t in np.linspace(0, 2 * math.pi, 90)]
        d.line(pts + [pts[0]], fill=col + (int(255 * al),), width=width, joint="curve")
    for k in range(n):
        r = (r0 + k * spread) % (n * spread) + 0.15; al = a * max(0.0, 1 - r / (n * spread)) ** 1.6 * 0.10
        if al < 0.01: continue
        pts = [I.p(cx + r * math.cos(t), cy + r * math.sin(t), z) for t in np.linspace(0, 2 * math.pi, 90)]; d.polygon(pts, fill=col + (int(255 * al),))
    g = lay.filter(ImageFilter.GaussianBlur(7)); im.alpha_composite(g); im.alpha_composite(lay)
