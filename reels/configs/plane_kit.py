"""Сцены для роликов про авиацию: небо с облаками (процедурное), силуэт двухпалубного лайнера (без марки), фото с наездом камеры
и цветокоррекцией, куб воздуха на весах, транспортир, стрелки сил со свечением. Всё бесплатно, кодом."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from scipy.ndimage import gaussian_filter
import bh_cine as B
from bh_cine import W, H, ease, seg, lerp, fnt
HERE = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
_CL = {}
def cloud_tex(seed, h=900, w=1600, sig=(30, 60), thr=0.15):
    if seed not in _CL:
        rng = np.random.default_rng(seed); f = np.zeros((h, w), np.float32)
        for s_, a_ in ((sig[0], 1.0), (sig[1], 1.4), (8, 0.35)):
            g = gaussian_filter(rng.normal(0, 1, (h, w)).astype(np.float32), (s_ * 0.5, s_), mode="wrap"); f += a_ * g / (g.std() + 1e-6)
        f = (f - f.mean()) / f.std(); _CL[seed] = np.clip((f - thr) / 1.4, 0, 1) ** 1.3
    return _CL[seed]
def sky(lt, mood="sunset", speed=40.0, cy_horizon=1150):
    """Небо 1080x1920 RGB: градиент + три слоя облаков с параллаксом."""
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    if mood == "sunset": top, mid, bot = (12, 18, 40), (90, 60, 90), (255, 150, 80)
    elif mood == "day": top, mid, bot = (25, 70, 150), (70, 130, 205), (170, 205, 235)
    else: top, mid, bot = (6, 9, 18), (14, 22, 44), (30, 40, 70)
    hz = cy_horizon / H
    t1 = np.clip(y / hz, 0, 1); col = np.zeros((H, W, 3), np.float32)
    for c in range(3):
        col[..., c] = np.where(t1 < 0.6, top[c] + (mid[c] - top[c]) * (t1 / 0.6), mid[c] + (bot[c] - mid[c]) * ((t1 - 0.6) / 0.4)) * np.ones((1, W), np.float32)
    if mood == "sunset":
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); sunx, suny = 760, cy_horizon - 60
        r = np.hypot(xx - sunx, (yy - suny) * 1.0); col += (np.exp(-r / 380) * 140)[..., None] * np.array([1.0, 0.65, 0.35], np.float32) + (np.exp(-r / 60) * 255)[..., None] * np.array([1, 0.95, 0.8], np.float32)
    for k, (seed, sp, y0, sc, alpha, tint) in enumerate(((1, 0.35, 380, 1.0, 0.55, 0.75), (2, 0.7, 760, 1.3, 0.7, 0.9), (3, 1.3, 1150, 1.8, 0.85, 1.05))):
        tex = cloud_tex(seed); th, tw = tex.shape; off = int(lt * speed * sp) % tw
        band = np.roll(tex, -off, 1)
        hh = int(th * sc * 0.6); band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).resize((int(tw * sc), hh), Image.BILINEAR)).astype(np.float32) / 255
        band = band[:, :W]; ys = max(0, y0 - hh // 2); ye = min(H, ys + hh); band = band[:ye - ys]
        light = np.array([255, 190, 150], np.float32) if mood == "sunset" else (np.array([245, 248, 255], np.float32) if mood == "day" else np.array([90, 100, 130], np.float32))
        shade = np.array([70, 50, 80], np.float32) if mood == "sunset" else (np.array([150, 170, 200], np.float32) if mood == "day" else np.array([30, 35, 55], np.float32))
        lg = np.linspace(1, 0, band.shape[0], dtype=np.float32)[:, None, None]
        cc = (light * lg + shade * (1 - lg)) * tint
        a = (band * alpha)[..., None]; col[ys:ye] = col[ys:ye] * (1 - a) + cc * a
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
def liner(d, cx, cy, L, col=(14, 16, 24), rim=(255, 200, 150), rim_a=200, ang=0.0, flaps=0.0):
    """Силуэт двухпалубного широкофюзеляжного лайнера сбоку (без марки). L — длина в пикселях, ang — тангаж (рад)."""
    h = L * 0.105
    pts = []
    for t in np.linspace(0, 1, 60):                                      # верх фюзеляжа: нос — горб второй палубы — хвост
        x = -L / 2 + L * t
        if t < 0.06: yt = -h * 0.5 * math.sqrt(max(0, t / 0.06)) * 0.95
        elif t < 0.8: yt = -h * 0.5
        else: yt = -h * 0.5 + (t - 0.8) / 0.2 * h * 0.28
        pts.append((x, yt))
    for t in np.linspace(1, 0, 60):                                      # низ
        x = -L / 2 + L * t
        if t < 0.05: yb = h * 0.5 * math.sqrt(max(0, t / 0.05)) * 0.8
        elif t < 0.72: yb = h * 0.5
        else: yb = h * 0.5 - (t - 0.72) / 0.28 * h * 0.62
        pts.append((x, yb))
    fin = [(L * 0.33, -h * 0.45), (L * 0.47, -h * 1.75), (L * 0.5, -h * 1.75), (L * 0.5, -h * 0.25)]
    stab = [(L * 0.36, -h * 0.05), (L * 0.5, -h * 0.12), (L * 0.5, h * 0.02), (L * 0.4, h * 0.05)]
    wing = [(-L * 0.08, h * 0.32), (L * 0.16, h * 0.45), (L * 0.18, h * 0.58), (-L * 0.06, h * 0.52)]
    flap = [(L * 0.12, h * 0.5), (L * 0.2, h * 0.5 + flaps * h * 0.5), (L * 0.19, h * 0.62 + flaps * h * 0.5), (L * 0.11, h * 0.6)]
    eng = [[(-L * 0.06 + dx, h * 0.62), (L * 0.02 + dx, h * 0.62), (L * 0.02 + dx, h * 0.9), (-L * 0.06 + dx, h * 0.9)] for dx in (0, L * 0.11)]
    ca, sa = math.cos(ang), math.sin(ang)
    def tr(P): return [(cx + x * ca + y * sa, cy - x * sa + y * ca) for x, y in P]
    for poly in (fin, stab, wing, flap, *eng): d.polygon(tr(poly), fill=col + (255,))
    body = tr(pts); d.polygon(body, fill=col + (255,)); d.line(body[:60], fill=rim + (rim_a,), width=3)
    for k in range(12): x = -L * 0.38 + k * L * 0.055; d.ellipse(tr([(x - 2, -h * 0.18)])[0] + tuple(np.add(tr([(x + 2, -h * 0.12)])[0], 0)), fill=(255, 220, 160, 120)) if False else None
def _grade(a):
    a = np.clip(a, 0, 1); a = a * 0.86                                                   # ниже экспозиция
    a = a - 0.10 * np.sin(a * math.pi) * (a - 0.5) * 2                                   # мягкая S-кривая
    lum = a.mean(-1, keepdims=True)
    a = a + (1 - lum) ** 2 * np.array([-0.025, 0.005, 0.04]) + lum ** 2 * np.array([0.035, 0.01, -0.035])
    return np.clip(a, 0, 1)
def photo(name, lt, D, z0=1.0, z1=1.1, fx=0.5, fy=0.5, dx=0.05, cy=640, pw=1.18, darken=0.45):
    """Фото на всю ширину в центре кадра (не режем самолёт), медленный наезд и сдвиг; сверху и снизу — размытая тёмная копия."""
    key = ("ph2", name)
    if key not in _CL:
        im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); im.thumbnail((2600, 2600), Image.LANCZOS)
        a = _grade(np.asarray(im).astype(np.float32) / 255); im = Image.fromarray((a * 255).astype(np.uint8))
        s = max(W / im.width, H / im.height) * 1.1; bg = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(28))
        bg = ImageEnhance.Brightness(bg).enhance(darken); _CL[key] = (im, bg)
    im, bg = _CL[key]; u = ease(lt / max(D, 0.1)) * 0.7 + lt / max(D, 0.1) * 0.3; z = z0 + (z1 - z0) * u
    w = int(W * pw * z); h = int(w * im.height / im.width)
    cw = im.width / z; chh = im.height / z
    ccx = fx * im.width + dx * im.width * (u - 0.5); ccy = fy * im.height
    ccx = min(max(ccx, cw / 2), im.width - cw / 2); ccy = min(max(ccy, chh / 2), im.height - chh / 2)
    ph = im.resize((w, h), Image.BICUBIC, box=(ccx - cw / 2, ccy - chh / 2, ccx + cw / 2, ccy + chh / 2))
    out = bg.copy(); m = Image.new("L", (w, h), 255); md = ImageDraw.Draw(m); fade = int(h * 0.14)
    for i in range(fade): v = int(255 * (i / fade) ** 1.5); md.line([(0, i), (w, i)], fill=v); md.line([(0, h - 1 - i), (w, h - 1 - i)], fill=v)
    out.paste(ph, ((W - w) // 2, int(cy - h / 2)), m); return out
def arrow_glow(im, p0, p1, col, w=14, head=46, a=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    L = math.dist(p0, p1)
    if L < 4: return
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hb = (p1[0] - head * 0.8 * math.cos(ang), p1[1] - head * 0.8 * math.sin(ang))
    d.line([p0, hb], fill=col + (int(255 * a),), width=w)
    d.polygon([p1, (hb[0] + head * 0.5 * math.cos(ang + math.pi / 2), hb[1] + head * 0.5 * math.sin(ang + math.pi / 2)), (hb[0] - head * 0.5 * math.cos(ang + math.pi / 2), hb[1] - head * 0.5 * math.sin(ang + math.pi / 2))], fill=col + (int(255 * a),))
    g = lay.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(g); im.alpha_composite(lay)
def cube(d, c, s, u=1.0, rng_seed=1, col=(170, 205, 255), lt=0.0):
    """Изометрический куб 1 м³ с «молекулами» воздуха."""
    dx, dy = s * 0.5, s * 0.28
    P = {"a": (c[0] - s / 2, c[1] - s / 2 + dy), "b": (c[0] + s / 2 - dx * 0.0, c[1] - s / 2 + dy)}
    f = [(c[0] - s / 2, c[1] - s / 2), (c[0] + s / 2, c[1] - s / 2), (c[0] + s / 2, c[1] + s / 2), (c[0] - s / 2, c[1] + s / 2)]
    b = [(x + dx, y - dy) for x, y in f]
    for poly in (f, b):
        d.line(poly + [poly[0]], fill=col + (int(220 * u),), width=3)
    for i in range(4): d.line([f[i], b[i]], fill=col + (int(220 * u),), width=3)
    rng = np.random.default_rng(rng_seed)
    for k in range(70):
        x = rng.uniform(0, 1); y = rng.uniform(0, 1); z = rng.uniform(0, 1)
        px = c[0] - s / 2 + x * s + z * dx + 6 * math.sin(lt * 3 + k); py = c[1] - s / 2 + y * s - z * dy + 6 * math.cos(lt * 2.4 + k * 1.3)
        r = 3 + 3 * z; d.ellipse((px - r, py - r, px + r, py + r), fill=(220, 235, 255, int(200 * u)))
def protractor(d, c, r, alpha, col=(255, 214, 40), u=1.0):
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), 180, 360, fill=col + (int(120 * u),), width=2)
    for k in range(0, 181, 5):
        a = math.radians(180 + k); l = 16 if k % 15 == 0 else 7
        d.line([(c[0] + r * math.cos(a), c[1] + r * math.sin(a)), (c[0] + (r - l) * math.cos(a), c[1] + (r - l) * math.sin(a))], fill=col + (int(170 * u),), width=2)
    d.line([c, (c[0] - r * 1.05, c[1])], fill=col + (int(255 * u),), width=3)
    d.line([c, (c[0] - r * 1.05 * math.cos(alpha), c[1] - r * 1.05 * math.sin(alpha))], fill=col + (int(255 * u),), width=3)
    d.arc((c[0] - r * 0.45, c[1] - r * 0.45, c[0] + r * 0.45, c[1] + r * 0.45), 180, 180 + math.degrees(alpha), fill=col + (int(255 * u),), width=5)
