"""Ночная трасса в перспективе, свет фар, силуэты, глаз, спидометр — всё кодом (numpy/PIL), без внешних картинок."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from bh_cine import W, H, ease, seg, lerp, fnt

F = 900.0                      # фокусное расстояние, px
CAM_H = 1.2                    # высота камеры, м
CAM_X = 1.8                    # машина едет по правой полосе
HY = 700                       # горизонт
WARM = (255, 246, 222)

_xs = None


def road(s=0.0, beam=1.0, dark=1.0, hy=HY):
    """Дорога в перспективе. s — пройденный путь (двигает разметку), beam — свет своих фар, dark — общая яркость 0..1."""
    global _xs
    hw, hh = W // 2, H // 2
    if _xs is None:
        _xs = np.arange(hw, dtype=np.float32)[None, :] * 2 - 540
    ys = np.arange(hh, dtype=np.float32)[:, None] * 2
    dy = ys - hy
    below = dy > 1.5
    z = np.where(below, F * CAM_H / np.maximum(dy, 1.5), 9999.0).astype(np.float32)
    u = _xs * z / F + CAM_X
    lit = 0.16 * dark + beam * dark * np.exp(-z / 34.0) * np.exp(-(((u - CAM_X) / (0.55 * z + 3.0)) ** 2))
    img = np.zeros((hh, hw, 3), np.float32)
    # небо и дымка у горизонта
    t = np.clip((ys - 0) / max(hy, 1), 0, 1)
    sky = np.stack([4 + 12 * t, 6 + 18 * t, 14 + 34 * t], -1) * (0.45 + 0.55 * dark)
    img[:] = sky
    # земля: обочина и поле
    absu = np.abs(u)
    road_m = np.clip((3.6 - absu) * 6, 0, 1)
    shld_m = np.clip((6.2 - absu) * 3, 0, 1) * (1 - road_m)
    asphalt = np.array([20, 24, 34], np.float32)
    shoulder = np.array([26, 28, 30], np.float32)
    field = np.array([9, 14, 18], np.float32)
    ground = field[None, None] * (1 - road_m - shld_m)[..., None] + shoulder[None, None] * shld_m[..., None] + asphalt[None, None] * road_m[..., None]
    ground = ground * (0.34 + 1.0 * lit[..., None]) * (0.4 + 0.6 * dark)
    ground += np.array([34, 33, 26], np.float32)[None, None] * (beam * dark * np.exp(-z / 22.0) * np.exp(-(((u - CAM_X) / (0.5 * z + 3.2)) ** 2)))[..., None]
    # разметка
    mark_l = 0.22 + 1.6 * lit
    dash = ((z + s) % 9.0 < 4.5) & (absu < 0.09)
    edge = (np.abs(absu - 3.3) < 0.08)
    mk = (dash | edge).astype(np.float32)
    ground += (np.array([210, 210, 196], np.float32)[None, None] * (mk * mark_l * (0.5 + 0.5 * dark))[..., None])
    img = np.where(below[..., None], ground, img)
    # свечение горизонта
    img += np.array([26, 40, 76], np.float32)[None, None] * (np.exp(-np.abs(dy) / 55.0) * 0.55 * dark)[..., None]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").resize((W, H), Image.BILINEAR).convert("RGBA")
    lamps(out, s, dark, hy)
    return out


def proj(u, z, y_up=0.0, hy=HY):
    """Мировая точка (u — поперёк, z — вперёд, y_up — высота над дорогой) → пиксель."""
    z = max(z, 0.5)
    return (540 + (u - CAM_X) * F / z, hy + (CAM_H - y_up) * F / z)


GL = None


def _grad():
    global GL
    if GL is None:
        n = 256; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32); d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
        core = np.exp(-(d / 0.07) ** 2); halo = 0.55 / (1 + (d / 0.16) ** 2) * np.clip(1 - d, 0, 1) ** 2; mid = 0.5 * np.exp(-(d / 0.3) ** 2)
        GL = np.clip(core + halo + mid * 0.5, 0, 1)
    return GL


def glow(im, p, r, col=WARM, a=1.0, aspect=1.0):
    """Аддитивное свечение: im (RGBA) меняется на месте."""
    if a < 0.01 or r < 2: return
    w = max(int(2 * r * aspect), 2); h = max(int(2 * r), 2)
    g = Image.fromarray((_grad() * 255).astype(np.uint8), "L").resize((w, h), Image.BILINEAR)
    x0, y0 = int(p[0] - w / 2), int(p[1] - h / 2); x1, y1 = x0 + w, y0 + h
    cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    if cx1 <= cx0 or cy1 <= cy0: return
    g = g.crop((cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0))
    tint = Image.merge("RGB", [g.point(lambda v, c=c: int(min(255, v * c / 255.0 * min(a, 1.6)))) for c in col])
    reg = im.crop((cx0, cy0, cx1, cy1)).convert("RGB"); reg = ImageChops.add(reg, tint)
    im.paste(reg.convert("RGBA"), (cx0, cy0))


def flood(im, a, c=(540, 760)):
    """Ослепление: белое заливает кадр."""
    if a < 0.01: return
    glow(im, c, 1500, WARM, a * 1.3)
    if a > 0.4: im.alpha_composite(Image.new("RGBA", (W, H), (255, 252, 240, int(255 * (a - 0.4) / 0.6 * 0.85))))


def lamps(im, s, dark, hy=HY):
    d = ImageDraw.Draw(im)
    step = 38.0; k0 = int(s // step)
    for k in range(k0 - 1, k0 + 8):
        z = k * step - s + step
        if z < 8 or z > 260: continue
        bx, by = proj(5.6, z); tx_, ty = proj(5.6, z, 7.5); hx, hy_ = proj(4.0, z, 7.5)
        a = 0.9 * dark
        d.line([(bx, by), (tx_, ty)], fill=(50, 56, 70, int(255 * a)), width=max(1, int(300 / z)))
        d.line([(tx_, ty), (hx, hy_)], fill=(50, 56, 70, int(255 * a)), width=max(1, int(220 / z)))
        glow(im, (hx, hy_), 8000 / (z + 80) * dark, (255, 190, 110), 0.7 * dark)


def headlights(im, zc, u=-1.8, a=1.0, size=1.0, sep=0.72, y_up=0.68):
    """Фары встречной машины на дистанции zc. Возвращает центр между фарами."""
    pl = proj(u - sep, zc, y_up); pr = proj(u + sep, zc, y_up); r = min(900, (9500.0 / (zc + 6)) * size) * a
    for p in (pl, pr):
        glow(im, p, r, WARM, 0.95 * a); glow(im, p, r * 0.9, WARM, 0.45 * a, aspect=4.2)
    return ((pl[0] + pr[0]) / 2, (pl[1] + pr[1]) / 2)


def car_front(im, zc, u=-1.8, col=(6, 8, 12)):
    """Силуэт встречной машины (без логотипов и номеров)."""
    d = ImageDraw.Draw(im); w = 1.8 * F / zc; hgt = 1.45 * F / zc
    bx, by = proj(u, zc); x0, x1 = bx - w / 2, bx + w / 2
    d.rounded_rectangle((x0, by - hgt * 0.62, x1, by - hgt * 0.1), int(w * 0.08), fill=col + (255,), outline=(30, 40, 60, 255), width=1)
    d.polygon([(x0 + w * 0.14, by - hgt * 0.62), (x0 + w * 0.26, by - hgt), (x1 - w * 0.26, by - hgt), (x1 - w * 0.14, by - hgt * 0.62)], fill=col + (255,), outline=(30, 40, 60, 255))
    d.rectangle((x0 + w * 0.05, by - hgt * 0.12, x1 - w * 0.05, by), fill=(2, 3, 6, 255))


def person(d, base, h, col=(8, 10, 16), a=255):
    x, y = base; hd = h * 0.13
    d.ellipse((x - hd, y - h, x + hd, y - h + 2 * hd), fill=col + (a,))
    d.rounded_rectangle((x - h * 0.17, y - h + 2.1 * hd, x + h * 0.17, y - h * 0.45), int(h * 0.07), fill=col + (a,))
    d.line([(x - h * 0.08, y - h * 0.46), (x - h * 0.1, y)], fill=col + (a,), width=max(2, int(h * 0.09)))
    d.line([(x + h * 0.08, y - h * 0.46), (x + h * 0.12, y)], fill=col + (a,), width=max(2, int(h * 0.09)))


def edge_line(im, col, u=3.3, a=1.0, z0=6, z1=120):
    """Подсвеченный правый край дороги."""
    pts = [proj(u, z) for z in np.linspace(z1, z0, 24)]
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.line(pts, fill=col + (int(255 * a),), width=10)
    b = g.filter(ImageFilter.GaussianBlur(14)); im.alpha_composite(b); im.alpha_composite(g)


def dial(d, c, r, v, vmax, col, label="км/ч", sw=1.0):
    """Спидометр: дуга 225°..−45°, стрелка по v."""
    a0, a1 = 135, 405
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), a0, a1, fill=(70, 90, 130, 255), width=6)
    for k in range(0, int(vmax / 10) + 1):
        a = math.radians(a0 + (a1 - a0) * k * 10 / vmax); l = 18 if k % 2 == 0 else 9
        d.line([(c[0] + (r - 6) * math.cos(a), c[1] + (r - 6) * math.sin(a)), (c[0] + (r - 6 - l) * math.cos(a), c[1] + (r - 6 - l) * math.sin(a))], fill=(150, 170, 210, 255), width=3)
    f = min(max(v / vmax, 0), 1); aa = math.radians(a0 + (a1 - a0) * f)
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), a0, a0 + (a1 - a0) * f, fill=col + (255,), width=10)
    d.line([c, (c[0] + (r - 30) * math.cos(aa), c[1] + (r - 30) * math.sin(aa))], fill=col + (255,), width=6)
    d.ellipse((c[0] - 9, c[1] - 9, c[0] + 9, c[1] + 9), fill=col + (255,))
    d.text((c[0], c[1] + r * 0.5), f"{int(round(v))}", font=fnt(int(r * 0.62), "Black"), fill=col + (255,), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 160))
    d.text((c[0], c[1] + r * 0.88), label, font=fnt(int(r * 0.2), "Medium"), fill=(140, 160, 200, 255), anchor="mm")


def eye(im, c, sc, mm=8.0, light=0.0, col=(70, 190, 215)):
    """Схематичный глаз крупным планом. mm — диаметр зрачка, light — вспышка света в глаз."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); cx, cy = c
    wd, ht = 420 * sc, 215 * sc
    top = [(cx + wd * (2 * t - 1), cy - ht * (1 - (2 * t - 1) ** 2) ** 0.9) for t in np.linspace(0, 1, 40)]
    bot = [(cx + wd * (2 * t - 1), cy + ht * 0.8 * (1 - (2 * t - 1) ** 2) ** 0.9) for t in np.linspace(1, 0, 40)]
    d.polygon(top + bot, fill=(206, 212, 226, 255))
    R = 150 * sc
    for k in range(10, 0, -1):
        t = k / 10; rr = R * t; d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=lerp((22, 70, 100), col, 1 - t * 0.9) + (255,))
    for k in range(48):
        a = k * math.pi / 24; d.line([(cx + R * 0.5 * math.cos(a), cy + R * 0.5 * math.sin(a)), (cx + R * 0.96 * math.cos(a), cy + R * 0.96 * math.sin(a))], fill=(190, 240, 250, 90), width=max(1, int(2 * sc)))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(10, 30, 50, 255), width=max(3, int(8 * sc)))
    pr = R * mm / 12.0; d.ellipse((cx - pr, cy - pr, cx + pr, cy + pr), fill=(0, 0, 0, 255))
    d.ellipse((cx - R * 0.36, cy - R * 0.55, cx - R * 0.14, cy - R * 0.33), fill=(255, 255, 255, 220))
    # веки
    d.line(top, fill=(10, 14, 26, 255), width=max(6, int(14 * sc)), joint="curve"); d.line(bot, fill=(10, 14, 26, 255), width=max(4, int(8 * sc)), joint="curve")
    im.alpha_composite(lay)
    if light > 0.02: glow(im, (cx - R * 0.25, cy - R * 0.4), 420 * sc * (0.6 + light), WARM, light)
    return pr


def eye_mini(d, c, r, mm, col=(70, 190, 215)):
    """Маленький индикатор зрачка в углу кадра."""
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=(10, 20, 34, 235), outline=col + (255,), width=3)
    ir = r * 0.78; d.ellipse((c[0] - ir, c[1] - ir, c[0] + ir, c[1] + ir), fill=lerp((22, 70, 100), col, 0.5) + (255,))
    pr = ir * mm / 12.0; d.ellipse((c[0] - pr, c[1] - pr, c[0] + pr, c[1] + pr), fill=(0, 0, 0, 255))
