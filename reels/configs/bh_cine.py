"""Кинематографичная графика для роликов про космос — всё считается кодом (numpy/PIL/scipy), без внешних картинок.
bh_frame(...) — чёрная дыра: диск с доплеровским свечением и турбулентностью, дуга линзированного диска над тенью, фотонное кольцо,
звёзды и туманность, искажённые линзой. finish_c — свечение, анаморфотный блик, хроматическая аберрация. HUD-помощники."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter
W, H = 1080, 1920; HW, HH = W // 2, H // 2
_yy, _xx = np.mgrid[0:HH, 0:HW].astype(np.float32)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def seg(u, a, b): return ease((u - a) / (b - a))
def fnt(size, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", size)
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
# ---------------- текстуры (один раз)
_STARS = None; _TEX = None
def starfield():
    global _STARS
    if _STARS is None:
        rng = np.random.default_rng(21); TH, TW = 2000, 1200
        neb = np.zeros((TH, TW, 3), np.float32)
        for sig, amp, col in ((90, 1.0, (0.10, 0.16, 0.42)), (40, 0.6, (0.30, 0.10, 0.28)), (160, 0.8, (0.05, 0.12, 0.30))):
            f = gaussian_filter(rng.normal(0, 1, (TH // 4, TW // 4)).astype(np.float32), sig / 4, mode="wrap"); f = (f - f.mean()) / (f.std() + 1e-6)
            f = np.clip(f - 0.3, 0, None); f = np.kron(f, np.ones((4, 4), np.float32)); 
            for c in range(3): neb[..., c] += amp * 0.05 * col[c] * f
        n = 5200; ys = rng.integers(0, TH, n); xs = rng.integers(0, TW, n); b = rng.pareto(2.2, n) * 0.25 + 0.12
        col = rng.choice([0, 1, 2], n, p=[0.5, 0.35, 0.15])
        tint = np.array([[0.75, 0.85, 1.0], [1.0, 1.0, 0.95], [1.0, 0.75, 0.55]], np.float32)
        img = neb
        for dy in (0, 1):
            for dx in (0, 1):
                w = 1.0 if dx == dy == 0 else 0.35
                np.add.at(img, ((ys + dy) % TH, (xs + dx) % TW), (np.minimum(b, 2.5)[:, None] * tint[col] * w))
        _STARS = img
    return _STARS
def disk_tex():
    global _TEX
    if _TEX is None:
        rng = np.random.default_rng(5); NR, NP = 256, 720; t = np.zeros((NR, NP), np.float32)
        for sr, sp, a in ((1.5, 14, 1.0), (3, 40, 0.8), (0.8, 5, 0.5)):
            f = gaussian_filter(rng.normal(0, 1, (NR, NP)).astype(np.float32), (sr, sp), mode=("nearest", "wrap")); f = (f - f.mean()) / (f.std() + 1e-6); t += a * f
        _TEX = np.clip(0.9 + 0.35 * t, 0.15, 2.0)
    return _TEX
def bh_frame(cx, cy, S, t=0.0, incl=82, rin=1.25, rout=4.6, exposure=0.62, dopp=0.55, rot=0.35, stars=1.0, drift=0.0, spread=1.0):
    """Кадр 1080x1920 (RGB uint8). cx, cy, S — центр и радиус тени в пикселях полного кадра."""
    cxh, cyh, Sh = cx / 2, cy / 2, S / 2
    x = (_xx - cxh) / Sh; y = (_yy - cyh) / Sh; r = np.hypot(x, y) + 1e-5
    # звёзды и туманность, искажённые линзой: источник = положение * (1 - 1/r^2)
    ST = starfield(); k = np.where(r > 1.0, 1 - 1.0 / (r * r), 0.0)
    sx = (x * k * Sh * 0.55 + HW + drift * 3.0).astype(np.int64) % ST.shape[1]; sy = (y * k * Sh * 0.55 + HH + 40).astype(np.int64) % ST.shape[0]
    col = ST[sy, sx] * stars * (1.0 + 2.2 / (r * r + 0.8) * 0.5)[..., None]
    col = col * (r > 1.0)[..., None]
    # диск (прямое изображение)
    c = math.cos(math.radians(incl)); Yd = y / max(c, 0.05); rho = np.hypot(x, Yd) + 1e-5; phi = np.arctan2(Yd, x)
    TEX = disk_tex(); NR, NP = TEX.shape
    def sample(rr, pp, off):
        ri = np.clip(((rr - rin) / (rout - rin) * (NR - 1)).astype(np.int64), 0, NR - 1)
        pi_ = ((pp + off) / (2 * math.pi) * NP).astype(np.int64) % NP
        return TEX[ri, pi_]
    omega = rot * (rin / rho) ** 1.5 * 6.0
    off = -omega * t
    def disk_I(rr, g):
        I = (rin / rr) ** 2.3 * (1 - 0.55 * np.sqrt(rin / rr)) * 5.0
        return I * g ** 3
    g = 1 + dopp * (-x / (np.hypot(x, Yd) + 1e-5)) * (np.abs(Yd) / (np.abs(Yd) + 0.2))
    front = (Yd > 0) | (r > 1.06)
    band = (rho > rin) & (rho < rout) & front
    I1 = np.where(band, disk_I(np.where(band, rho, rin + 1), g) * sample(np.clip(rho, rin, rout), phi, off), 0.0)
    T1 = np.clip(0.95 * (rin / np.clip(rho, rin, None)) ** 0.7 * g, 0, 1.3)
    # дуга линзированного диска над и под тенью
    d = r - 1.0; arch_w = np.exp(-np.clip(d, 0, None) / (0.16 * spread)) * (r > 1.0)
    pole = (np.abs(y) / r) ** 1.6
    rho2 = rin + (rout - rin) * np.clip(d / 1.0, 0, 1) ** 1.2; phi2 = np.arctan2(y, x)
    g2 = 1 + dopp * (-x / r) * 0.8
    I2 = (rin / rho2) ** 2.3 * 5.0 * g2 ** 3 * sample(rho2, phi2, off * 0.8) * arch_w * (0.15 + 0.9 * pole) * 0.55
    T2 = np.clip(0.95 * (rin / rho2) ** 0.7 * g2, 0, 1.3)
    ring = np.exp(-((r - 1.0) / 0.022) ** 2) * 1.1 * (0.5 + 0.5 * (1 + g2 - 1.0))
    def blackbody(T):
        return np.stack([np.clip(T * 2.2, 0, 1.4), np.clip(T * 1.7 - 0.30, 0, 1.2), np.clip(T * 2.3 - 1.15, 0, 1.0)], -1)
    hdr = blackbody(T1) * I1[..., None] + blackbody(T2) * I2[..., None] + np.array([1.0, 0.72, 0.42], np.float32) * ring[..., None]
    out = col + hdr * exposure
    out = 1 - np.exp(-out * 1.15)
    out = np.clip(out * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(out).resize((W, H), Image.BICUBIC)
# ---------------- постобработка
def finish_c(im, k=0.9, streak=0.5, ca=2, shake=0.0, lt=0.0):
    im = im.convert("RGB")
    if shake:
        im = ImageChops.offset(im, int(round(shake * math.sin(lt * 2.3))), int(round(shake * math.cos(lt * 1.7))))
    a = np.asarray(im).astype(np.float32)
    s4 = im.resize((W // 4, H // 4), Image.BILINEAR); b1 = np.asarray(s4.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)).astype(np.float32)
    s8 = im.resize((W // 8, H // 8), Image.BILINEAR); b2 = np.asarray(s8.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)).astype(np.float32)
    hl = s4.point(lambda v: max(0, v - 150) * 2)
    st = np.asarray(hl.resize((W // 40, H // 4), Image.BILINEAR).resize((W, H), Image.BILINEAR)).astype(np.float32) * np.array([0.55, 0.8, 1.0], np.float32)
    out = a + k * 0.55 * b1 + k * 0.35 * b2 + streak * st
    if ca:
        out[..., 0] = np.roll(out[..., 0], ca, 1); out[..., 2] = np.roll(out[..., 2], -ca, 1)
        out[:, :ca + 1, 0] = out[:, ca + 1:ca + 2, 0]; out[:, -ca - 1:, 2] = out[:, -ca - 2:-ca - 1, 2]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
# ---------------- HUD
def tracked(d, xy, s, size, col, u=1.0, w="Medium", sp=0.28, anchor="mm"):
    """Текст с широким трекингом, буквы проявляются по очереди (u 0..1)."""
    f = fnt(size, w); widths = [d.textlength(ch, font=f) + size * sp for ch in s]; tot = sum(widths) - size * sp
    x = xy[0] - tot / 2 if anchor == "mm" else xy[0]
    for i, ch in enumerate(s):
        a = ease(u * (len(s) + 3) / 3 - i / 3); a = min(a, 1)
        if a > 0.02: d.text((x, xy[1]), ch, font=f, fill=lerp((5, 7, 15), col, a), anchor="lm")
        x += widths[i]
def reticle(d, c, r, col, u=1.0, ticks=36, w=2):
    a0 = -90
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), a0, a0 + 360 * u, fill=col, width=w)
    for i in range(ticks):
        if i / ticks <= u:
            a = math.radians(a0 + 360 * i / ticks); l = 14 if i % 3 == 0 else 7
            d.line([(c[0] + (r - 2) * math.cos(a), c[1] + (r - 2) * math.sin(a)), (c[0] + (r + l) * math.cos(a), c[1] + (r + l) * math.sin(a))], fill=col, width=w)
def leader(d, p0, p1, p2, col, u=1.0, w=2):
    """Линия-выноска p0 → p1 → p2 (горизонталь), растёт с u."""
    segs = [(p0, p1), (p1, p2)]; tot = sum(math.dist(a, b) for a, b in segs); run = u * tot
    for a, b in segs:
        L = math.dist(a, b); f = min(max(run / L, 0), 1) if L else 1
        d.line([a, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)], fill=col, width=w); run -= L
    if u > 0.02: d.ellipse((p0[0] - 6, p0[1] - 6, p0[0] + 6, p0[1] + 6), outline=col, width=w)
def glow_polyline(im, pts, col, width=6, blur=10, a=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.line(pts, fill=col + (int(255 * a),), width=width, joint="curve")
    g = lay.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(g); im.alpha_composite(g); im.alpha_composite(lay)
def dot_glow(im, p, r, col, a=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col + (int(255 * a),)); g = lay.filter(ImageFilter.GaussianBlur(r * 1.2)); im.alpha_composite(g); im.alpha_composite(lay)

_GAL = None
def galaxy_img():
    """Спиральная галактика, нарисованная кодом (1400x1400, RGB float): ядро, рукава, пыль."""
    global _GAL
    if _GAL is None:
        rng = np.random.default_rng(8); N = 1400; img = np.zeros((N, N, 3), np.float32)
        n = 90000; arm = rng.integers(0, 2, n); rr = rng.exponential(0.22, n) + 0.02; th = arm * math.pi + 3.1 * np.log(rr * 6 + 1) * 1.6 + rng.normal(0, 0.28, n) / (rr * 3 + 0.6)
        x = rr * np.cos(th) + rng.normal(0, 0.012, n); y = rr * np.sin(th) + rng.normal(0, 0.012, n)
        ix = (N / 2 + x * N * 0.95).astype(int); iy = (N / 2 + y * N * 0.95).astype(int); ok = (ix >= 1) & (ix < N - 1) & (iy >= 1) & (iy < N - 1)
        b = rng.pareto(2.5, n) * 0.2 + 0.1; warm = np.exp(-rr * 7)
        col = np.stack([0.55 + 0.45 * warm, 0.65 + 0.2 * warm, 1.0 - 0.55 * warm], -1)
        np.add.at(img, (iy[ok], ix[ok]), (b[ok, None] * col[ok]))
        m = 160000; rr2 = np.abs(rng.normal(0, 0.05, m)); a = rng.uniform(0, 2 * math.pi, m)
        ix = (N / 2 + rr2 * np.cos(a) * N).astype(int); iy = (N / 2 + rr2 * np.sin(a) * N).astype(int)
        np.add.at(img, (np.clip(iy, 0, N - 1), np.clip(ix, 0, N - 1)), np.array([1.0, 0.85, 0.55], np.float32) * 0.09)
        for c in range(3): img[..., c] = gaussian_filter(img[..., c], 0.9) * 1.0 + gaussian_filter(img[..., c], 6) * 2.0
        img = 1 - np.exp(-img * 1.4); _GAL = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    return _GAL
def galaxy_layer(zoom, rot_deg, tilt=0.5, cx=540, cy=620, size=1100):
    """RGBA-слой с галактикой: масштаб zoom, поворот, наклон tilt (сплющивание по вертикали)."""
    g = Image.fromarray(galaxy_img()).rotate(rot_deg, Image.BICUBIC)
    w = int(size * zoom); h = int(size * zoom * tilt); g = g.resize((w, h), Image.BILINEAR)
    lay = Image.new("RGB", (W, H), (0, 0, 0)); lay.paste(g, (int(cx - w / 2), int(cy - h / 2)))
    return lay
def eht_ring(S, u=1.0, cx=540, cy=600, asym=0.8):
    """Схематичное «первое изображение»: нечёткое кольцо света с яркой нижней частью (нарисовано кодом)."""
    y = (_yy - cy / 2); x = (_xx - cx / 2); r = np.hypot(x, y) / (S / 2); ang = np.arctan2(y, x)
    prof = np.exp(-((r - 1.0) / 0.20) ** 2) * (0.35 + asym * (0.5 + 0.5 * np.sin(ang + 0.5))) * u
    rng = np.random.default_rng(2); n = gaussian_filter(rng.normal(0, 1, (HH, HW)).astype(np.float32), 5) * 4; prof = prof * (1 + 0.35 * np.clip(n, -1, 1))
    prof = np.clip(prof, 0, 1.4); out = np.stack([np.clip(prof * 1.3, 0, 1), np.clip(prof * 0.95 - 0.05, 0, 1), np.clip(prof * 0.55 - 0.18, 0, 1)], -1)
    return Image.fromarray((out * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
