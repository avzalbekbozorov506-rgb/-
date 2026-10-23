"""«Ещё пять минут» v2 — киноверсия по scripts/snooze_1_visual_v2.md (Avzaldoc): герой с телом, одеяло по контуру тела,
плоские тени (cel-shading), камера с дрейфом, размытие фона, motion blur, киноцвет, зерно. Всё кодом (PIL/numpy), бесплатно.
Запуск: python3 cartoon/snooze2.py            → hq/snooze_1_hq.mp4 + covers/72_snooze_click.jpg
        python3 cartoon/snooze2.py 4.3 14.85  → превью work/snooze_1/pv2_*.png"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import snooze as V1
from snooze import ease, seg, lerp, lerp2, mix, glow as _unused, phone_scene, build_audio, sky_day, sky_night, SR
W, H = 1080, 1920; S1 = 1.5; CW, CH = int(W * S1), int(H * S1); S0 = 3.0; FPS = 24; DUR = 20.0
# --- расписание из v1 (ритм не менялся)
STEPS = V1.STEPS; T0 = V1.T0; LABELS = V1.LABELS; tk = V1.tk; hits = V1.hits; slap_t = V1.slap_t; RING = V1.RING
T_SLEEP, T_BUB, T_WAKE, T_GRAB, T_SHOCK, T_CROUCH, T_JUMP, T_LAND, T_LOOP = 10.7, 13.3, 13.7, 14.2, 14.8, 15.6, 16.0, 17.6, 19.4
tint_at = V1.tint_at; sky_k = V1.sky_k; ringing = V1.ringing; label_at = V1.label_at
# --- палитра (HEX из спецификации)
def hx(s): s = s.lstrip("#"); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
INK = hx("1B1726"); SKIN, SKIN_S, SKIN_H = hx("FBD9B0"), hx("E5A67E"), hx("FFEBD0"); HAIR, HAIR_S = hx("4A3228"), hx("2E1D18")
PJ, PJ_S, PJ_H, PJ_ST = hx("F2C14E"), hx("C99633"), hx("FFE08A"), hx("E49B2B"); PANT, PANT_S, PANT_H = hx("6C87C9"), hx("4F68A6"), hx("8EA6DD")
BL, BL_S, BL_H, BL_F = hx("C95F58"), hx("9E3F42"), hx("E58A7E"), hx("8C3440"); PIL_, PIL_S, PIL_H = hx("A7D0DC"), hx("7FAAB9"), hx("D8EEF3")
MAT, MAT_S, MAT_H = hx("7C9BE0"), hx("5A78C0"), hx("A5BEF0"); BED, BED_S, BED_H = hx("B8652F"), hx("8A4520"), hx("D98B4C")
WALL, WALL_S = hx("E8D6B2"), hx("CDB890"); FLOOR, FLOOR_S, FLOOR_H = hx("D49A5E"), hx("A9703E"), hx("E6B27A")
WIN = (640, 180, 1010, 720)

# ===================== камера и рисование в координатах камеры
class Cam:
    def __init__(s, z, cx, cy): s.z, s.cx, s.cy = z, cx, cy
    @property
    def k(s): return s.z * S1
    def T(s, p): return ((p[0] - s.cx) * s.k + CW / 2, (p[1] - s.cy) * s.k + CH / 2)
class CvC:
    def __init__(s, im, cam): s.im = im; s.cam = cam; s.d = ImageDraw.Draw(im, "RGBA")
    def T(s, p): return s.cam.T(p)
    def poly(s, pts, fill, outline=None, w=0):
        P = [s.T(p) for p in pts]; s.d.polygon(P, fill=fill)
        if outline: s.d.line(P + [P[0]], fill=outline, width=max(int(w * s.cam.k), 1), joint="curve")
    def ell(s, c, rx, ry, fill=None, outline=None, w=0):
        x, y = s.T(c); k = s.cam.k; s.d.ellipse((x - rx * k, y - ry * k, x + rx * k, y + ry * k), fill=fill, outline=outline, width=max(int(w * k), 1) if outline else 0)
    def line(s, pts, fill, w, caps=True):
        P = [s.T(p) for p in pts]; wp = max(int(w * s.cam.k), 1); s.d.line(P, fill=fill, width=wp, joint="curve")
        if caps:
            for p in (P[0], P[-1]): s.d.ellipse((p[0] - wp / 2, p[1] - wp / 2, p[0] + wp / 2, p[1] + wp / 2), fill=fill)
    def arc(s, c, rx, ry, a0, a1, fill, w): x, y = s.T(c); k = s.cam.k; s.d.arc((x - rx * k, y - ry * k, x + rx * k, y + ry * k), a0, a1, fill=fill, width=max(int(w * k), 1))
    def text(s, xy, t, size, fill, stroke=0, w="Black"):
        s.d.text(s.T(xy), t, font=ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", max(int(size * s.cam.k), 6)), fill=fill, anchor="mm", stroke_width=int(stroke * s.cam.k), stroke_fill=(0, 0, 0, 255))

# --- формы для cel-shading: функция (draw, grow_px, off_px) → рисует белым на маске
def shp_ell(c, ctr, rx, ry):
    x, y = c.T(ctr); k = c.cam.k
    return lambda d, g, o: d.ellipse((x - rx * k - g + o[0], y - ry * k - g + o[1], x + rx * k + g + o[0], y + ry * k + g + o[1]), fill=255)
def shp_poly(c, pts):
    P = [c.T(p) for p in pts]
    def f(d, g, o):
        Q = [(p[0] + o[0], p[1] + o[1]) for p in P]; d.polygon(Q, fill=255)
        if g > 0: d.line(Q + [Q[0]], fill=255, width=int(2 * g), joint="curve")
    return f
def shp_cap(c, p0, p1, w0, w1):
    a, b = c.T(p0), c.T(p1); k = c.cam.k
    def f(d, g, o):
        for p, w in ((a, w0), (b, w1)): r = w * k / 2 + g; d.ellipse((p[0] - r + o[0], p[1] - r + o[1], p[0] + r + o[0], p[1] + r + o[1]), fill=255)
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1; nx, ny = -dy / n, dx / n; r0, r1 = w0 * k / 2 + g, w1 * k / 2 + g
        d.polygon([(a[0] + nx * r0 + o[0], a[1] + ny * r0 + o[1]), (b[0] + nx * r1 + o[0], b[1] + ny * r1 + o[1]), (b[0] - nx * r1 + o[0], b[1] - ny * r1 + o[1]), (a[0] - nx * r0 + o[0], a[1] - ny * r0 + o[1])], fill=255)
    return f
def shp_rr(c, ctr, w, h, r):
    x, y = c.T(ctr); k = c.cam.k
    return lambda d, g, o: d.rounded_rectangle((x - w * k / 2 - g + o[0], y - h * k / 2 - g + o[1], x + w * k / 2 + g + o[0], y + h * k / 2 + g + o[1]), r * k + g, fill=255)
def shp_union(*shapes):
    def f(d, g, o):
        for s_ in shapes: s_(d, g, o)
    return f
def _mask(shape, g=0, o=(0, 0)):
    m = Image.new("L", (CW, CH), 0); shape(ImageDraw.Draw(m), g, o); return m
def cel(c, shape, base, shadow, hi, ds=(14, 10), dh=(6, 4), outline=INK, ow=6, extra=None, alpha=255):
    """Контур + база + тень-серп (сдвиг маски к свету) + блик-серп. ds, dh — в единицах мира (свет справа-сверху)."""
    k = c.cam.k; im = c.im
    if outline:
        mo = _mask(shape, g=ow * k / 2); im.paste(outline + (255,), (0, 0), mo)
    m0 = _mask(shape); im.paste(base + (alpha,), (0, 0), m0)
    if shadow:
        ms = _mask(shape, 0, (ds[0] * k, -ds[1] * k)); sh = ImageChops.subtract(m0, ms); im.paste(shadow + (alpha,), (0, 0), sh)
    if hi:
        mh = _mask(shape, 0, (-dh[0] * k, dh[1] * k)); hl = ImageChops.subtract(m0, mh); im.paste(hi + (alpha,), (0, 0), hl)
    if extra: extra(m0)
    return m0
def stripes(c, m0, ang, gap, wid, col, origin=(0, 0)):
    k = c.cam.k; L = Image.new("L", (CW, CH), 0); d = ImageDraw.Draw(L); a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    ox, oy = c.T(origin)
    for i in range(-80, 80):
        px, py = ox + nx * i * gap * k, oy + ny * i * gap * k; d.line([(px - ux * 3000, py - uy * 3000), (px + ux * 3000, py + uy * 3000)], fill=255, width=max(int(wid * k), 1))
    c.im.paste(col + (255,), (0, 0), ImageChops.multiply(L, m0))
def smooth_closed(pts, n=8):
    """Catmull-Rom по ломаной (открытая)."""
    out = []; P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n; t2, t3 = t * t, t * t * t
            out.append((0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                        0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(pts[-1]); return out

# ===================== статика мира: рисуется один раз в S0=3 и режется камерой
_ST = {}
class WorldCv:
    """Рисование в мировых координатах на большом холсте S0 (для статики)."""
    def __init__(s, im): s.im = im; s.cam = Cam(S0 / S1, W / 2, H / 2)
    def _w(s): return s
def world_canvas(): return Image.new("RGBA", (int(W * S0), int(H * S0)), (0, 0, 0, 0))
class SC:
    def __init__(s, im): s.im = im; s.d = ImageDraw.Draw(im, "RGBA")
    def P(s, pts): return [(x * S0, y * S0) for x, y in pts]
    def poly(s, pts, fill, outline=None, w=0):
        s.d.polygon(s.P(pts), fill=fill)
        if outline: s.d.line(s.P(list(pts) + [pts[0]]), fill=outline, width=max(int(w * S0), 1), joint="curve")
    def ell(s, c, rx, ry, fill=None, outline=None, w=0): s.d.ellipse(((c[0] - rx) * S0, (c[1] - ry) * S0, (c[0] + rx) * S0, (c[1] + ry) * S0), fill=fill, outline=outline, width=max(int(w * S0), 1) if outline else 0)
    def rr(s, b, r, fill=None, outline=None, w=0): s.d.rounded_rectangle((b[0] * S0, b[1] * S0, b[2] * S0, b[3] * S0), r * S0, fill=fill, outline=outline, width=max(int(w * S0), 1) if outline else 0)
    def rect(s, b, fill): s.d.rectangle((b[0] * S0, b[1] * S0, b[2] * S0, b[3] * S0), fill=fill)
    def line(s, pts, fill, w, caps=True):
        s.d.line(s.P(pts), fill=fill, width=max(int(w * S0), 1), joint="curve")
        if caps:
            for p in (pts[0], pts[-1]): s.ell(p, w / 2, w / 2, fill=fill)
def soft(im, r): return im.filter(ImageFilter.GaussianBlur(r * S0))
def build_far():
    im = world_canvas(); c = SC(im); BG = (60, 40, 50)
    for y in range(0, 1330, 4): c.rect((0, y, W, y + 4), tuple(int(v) for v in mix(WALL, WALL_S, (y / 1330) ** 1.3)) + (255,))
    ImageDraw.Draw(im).rectangle((WIN[0] * S0, WIN[1] * S0, WIN[2] * S0, WIN[3] * S0), fill=(0, 0, 0, 0))
    fr = hx("96643C"); fr_s = hx("6E4528"); fr_h = hx("B5835A"); ol = mix(fr, (42, 36, 56), 0.5)
    for b in ((WIN[0] - 16, WIN[1] - 16, WIN[2] + 16, WIN[1]), (WIN[0] - 16, WIN[3], WIN[2] + 16, WIN[3] + 22), (WIN[0] - 16, WIN[1], WIN[0], WIN[3]), (WIN[2], WIN[1], WIN[2] + 16, WIN[3]), ((WIN[0] + WIN[2]) / 2 - 7, WIN[1], (WIN[0] + WIN[2]) / 2 + 7, WIN[3]), (WIN[0], 440, WIN[2], 454)): c.rect(b, fr)
    c.rect((WIN[0] - 16, WIN[3] + 14, WIN[2] + 16, WIN[3] + 22), fr_s); c.rect((WIN[0] - 16, WIN[1] - 16, WIN[2] + 16, WIN[1] - 10), fr_h)
    cur = hx("5470B0"); cur_s = hx("3E5890"); cur_h = hx("7E98D0")
    for x0, x1 in ((580, 700), (950, 1070)):
        c.poly([(x0, 130), (x1, 130), (x1 - 10, 800), (x0 + 10, 800)], cur, mix(cur, (42, 36, 56), 0.5) + (255,), 3)
        c.poly([(x0, 130), (x0 + (x1 - x0) * 0.35, 130), (x0 + (x1 - x0) * 0.35 - 6, 800), (x0 + 10, 800)], cur_s)
        for k in range(1, 5): c.line([(x0 + (x1 - x0) * k / 5, 130), (x0 + (x1 - x0) * k / 5 - 4, 800)], cur_s, 6, caps=False)
        c.line([(x1 - 14, 140), (x1 - 22, 790)], cur_h, 5, caps=False)
    c.rect((560, 108, 1090, 134), fr); c.rect((560, 108, 1090, 116), fr_h)
    c.rect((80, 330, 340, 610), hx("C0864A")); c.rect((98, 348, 322, 592), hx("F4E8CC")); c.rect((98, 348, 322, 360), hx("D8C8A0")); c.rect((80, 330, 340, 338), hx("DDA56C"))
    c.poly([(170, 560), (250, 560), (240, 520), (180, 520)], hx("BA6246")); c.rr((208, 420, 232, 524), 12, hx("56A060")); c.rr((178, 450, 202, 500), 12, hx("56A060")); c.rr((238, 460, 262, 506), 12, hx("56A060")); c.rect((178, 480, 232, 494), hx("56A060"))
    c.rr((222, 424, 232, 520), 5, hx("78BE80"))
    glow_im = Image.new("RGBA", im.size, (0, 0, 0, 0)); g = SC(glow_im); g.ell((820, 450), 330, 420, (255, 240, 190, 70)); im.alpha_composite(soft(glow_im, 40))
    return im
def build_near():
    im = world_canvas(); c = SC(im)
    c.rect((0, 1300, W, 1330), hx("B08A60")); c.rect((0, 1300, W, 1312), hx("C8A074"))
    for y in range(1330, H, 4): c.rect((0, y, W, y + 4), tuple(int(v) for v in mix(FLOOR, hx("C48850"), (y - 1330) / 590)) + (255,))
    for xb in range(-1400, 2500, 190): c.line([(560 + (xb - 560) * 0.30, 1330), (xb, H)], FLOOR_S, 4, caps=False)
    for y, wdt in ((1400, 3), (1500, 4), (1640, 5), (1800, 6)): c.line([(0, y), (W, y)], FLOOR_S, wdt, caps=False)
    c.poly([(150, 1580), (930, 1580), (1010, 1780), (60, 1780)], hx("7A94C8"), hx("56688F") + (255,), 4); c.poly([(190, 1610), (890, 1610), (950, 1750), (120, 1750)], hx("8DA6D6"))
    for tx_ in (420, 520): c.ell((tx_, 1480), 38, 18, hx("96563C"), INK + (255,), 4); c.ell((tx_ - 6, 1474), 28, 10, hx("B87650"))
    # окклюзия под кроватью и тени от ножек
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); s = SC(sh)
    for i in range(0, 120, 4): s.rect((0, 1300 + i, W, 1304 + i), hx("1A0F0A") + (int(190 * (1 - i / 120) ** 1.4),))
    s.ell((120, 1400), 70, 14, hx("2A1810") + (130,)); s.ell((1010, 1400), 70, 14, hx("2A1810") + (130,))
    im.alpha_composite(soft(sh, 5))
    # кровать: изголовье, изножье, каркас, матрас, подушка (cel: база/тень/блик)
    def part(shape_poly, base, shadow, hi, ow=4, ol=INK):
        c.poly(shape_poly, base, ol + (255,), ow)
    c.rr((36, 840, 210, 1300), 60, BED, INK + (255,), 5); c.rr((56, 880, 190, 1280), 46, hx("C97A44")); c.rr((56, 880, 74, 1280), 9, BED_H); c.rr((176, 880, 190, 1280), 7, BED_S)
    c.ell((124, 838), 28, 28, hx("D98B4C"), INK + (255,), 4); c.ell((118, 832), 12, 12, hx("F0B070"))
    c.rr((950, 1000, 1046, 1300), 30, BED, INK + (255,), 5); c.rr((962, 1010, 1034, 1290), 24, hx("C97A44")); c.ell((998, 996), 24, 24, hx("D98B4C"), INK + (255,), 4); c.ell((992, 990), 10, 10, hx("F0B070"))
    c.rect((60, 1170, 1030, 1300), BED); c.rect((60, 1170, 1030, 1184), BED_H); c.rect((60, 1284, 1030, 1300), BED_S); c.line([(60, 1300), (1030, 1300)], INK, 5, caps=False)
    for x in (80, 990): c.rect((x, 1300, x + 36, 1390), hx("96502A")); c.rect((x + 26, 1300, x + 36, 1390), BED_S)
    c.rr((150, 1070, 990, 1180), 28, MAT, INK + (255,), 5); c.rr((156, 1150, 984, 1178), 14, MAT_S); c.line([(172, 1092), (968, 1092)], MAT_H, 6, caps=False)
    c.ell((330, 1050), 160, 58, PIL_, INK + (255,), 5); c.ell((350, 1060), 150, 44, PIL_S); c.ell((330, 1046), 154, 52, PIL_); c.ell((366, 1030), 100, 22, PIL_H)
    return im
def build_beam():
    im = world_canvas(); c = SC(im)
    for ang, a in ((18, 26), (26, 40), (34, 18)):
        sh_ = math.tan(math.radians(ang)) * 610; c.poly([(640, 720), (1010, 720), (1010 - sh_ + 110, 1330), (640 - sh_ - 80, 1330)], (255, 240, 192, a))
    return soft(im, 18)
def statics():
    if not _ST:
        _ST["far"] = build_far(); _ST["far_b"] = {r: _ST["far"].filter(ImageFilter.GaussianBlur(r * S0 * 0.7)) for r in (1.5, 3.5, 5.0)}
        _ST["near"] = build_near(); _ST["beam"] = build_beam()
        def big(img): return img.resize((int(W * S0), int(H * S0)), Image.LANCZOS)
        d, n = sky_day(), sky_night()
        _ST["sky_d"] = Image.new("RGBA", (int(W * S0), int(H * S0)), (0, 0, 0, 0)).convert("RGB"); _ST["sky_n"] = None
        _ST["sky_d"] = big(d.convert("RGB")); _ST["sky_n"] = big(n.convert("RGB"))
        rng = np.random.default_rng(3); _ST["dust"] = [(rng.uniform(), rng.uniform(), rng.uniform(0, 6)) for _ in range(40)]
    return _ST
def view(img_big, cam):
    """Вырезать вид камеры из большого статического холста и привести к CW×CH."""
    z = cam.z; vw, vh = W / z, H / z; x0, y0 = cam.cx - vw / 2, cam.cy - vh / 2
    a = vw * S0 / CW
    return img_big.transform((CW, CH), Image.AFFINE, (a, 0, x0 * S0, 0, a, y0 * S0), Image.BILINEAR)

# ===================== персонаж
def face(c, ctr, st, mouth, look=(0, 0), tt=0.0, sx=1.0, sy=1.0, scare=0.0, pale=0.0, side=1.0, hair_up=0.0, brow="neutral", sweat=0.0):
    x, y = ctr; skin = mix(SKIN, (255, 246, 226), pale); sk_s = mix(SKIN_S, (240, 214, 190), pale); R = 66
    head = shp_ell(c, ctr, 67 * sx, 64 * sy)
    cel(c, head, skin, sk_s, SKIN_H, ds=(12, 9), dh=(5, 4), ow=6)
    # ухо (слева)
    cel(c, shp_ell(c, (x - 64 * sx, y + 6), 10, 15), skin, sk_s, None, ow=4); c.arc((x - 62 * sx, y + 6), 5, 8, 100, 260, hx("E8A98A"), 3)
    # волосы: шапка (верхняя левая часть головы) + хохолок
    mh = _mask(head); hair_poly = Image.new("L", (CW, CH), 0); dh_ = ImageDraw.Draw(hair_poly)
    dh_.polygon([c.T(p) for p in [(x - 80, y - 10), (x - 64, y - 46), (x - 10, y - 70 * sy), (x + 56, y - 56), (x + 66, y - 30), (x + 26, y - 40), (x - 10, y - 30), (x - 40, y - 4)]], fill=255)
    hm = ImageChops.multiply(mh, hair_poly); c.im.paste(HAIR + (255,), (0, 0), hm); c.im.paste(HAIR_S + (255,), (0, 0), ImageChops.subtract(hm, ImageChops.multiply(_mask(head, 0, (6 * c.cam.k, -4 * c.cam.k)), hm)))
    for i, (dx, L_, a_) in enumerate(((-14, 26, 8), (0, 20, 2), (-26, 16, 10))):
        L2 = L_ * (1 + 0.4 * hair_up); tipx = x + dx - a_ + 3 * math.sin(tt * 40 + i) * (hair_up > 0); tipy = y - 66 * sy - L2
        cel(c, shp_cap(c, (x + dx, y - 62 * sy), (tipx, tipy), 14, 4), HAIR, None, None, ow=3)
    # брови
    bro = {"neutral": ((0, 0), (0, 0)), "sleepy": ((0, 6), (0, 0)), "angry": ((0, 8), (0, -8)), "scared": ((0, -14), (0, -14))}[brow]
    for sgn in (-1, 1):
        ex = x + sgn * 26 * sx; ey = y - 28 * sy; inner = bro[0][1] if True else 0
        a0 = (ex - 12, ey + (bro[1][1] if sgn == -1 else bro[1][1])); a1 = (ex + 12, ey)
        if brow == "angry": a0, a1 = ((ex - 12 * sgn * -1 * -1, ey - 6), (ex + 12 * sgn * -1, ey + 6)) if False else ((ex - 12 * sgn, ey + 4 * 0 - 5 * 0 + 6) if False else (ex + 12 * sgn * -1, ey - 4), (ex - 12 * sgn * -1, ey + 8))
        if brow == "scared": a0, a1 = (ex - 12, ey - 14 + (6 if sgn == -1 else 0)), (ex + 12, ey - 14 + (0 if sgn == -1 else 6))
        if brow == "sleepy": a0, a1 = (ex - 12, ey + 2 + (0 if sgn == 1 else 6)), (ex + 12, ey + 2 + (6 if sgn == 1 else 0))
        c.line([a0, a1], HAIR, 7)
    # глаза
    for sgn in (-1, 1):
        ex, ey = x + sgn * 24 * sx, y - 2 * sy
        if st == "closed": c.arc((ex, ey - 4), 14, 9, 25, 155, INK, 5)
        elif st == "squint": c.line([(ex - sgn * 12, ey - 8), (ex + sgn * 10, ey + 1), (ex - sgn * 12, ey + 8)], INK, 5)
        elif st == "half":
            c.ell((ex, ey), 15, 13, (255, 255, 255), INK, 3); c.ell((ex + look[0], ey + 3 + look[1]), 6.5, 6.5, INK); c.ell((ex + look[0] + 2.5, ey + look[1]), 2, 2, (255, 255, 255))
            c.poly([(ex - 18, ey - 18), (ex + 18, ey - 18), (ex + 18, ey - 3), (ex - 18, ey - 3)], skin); c.line([(ex - 15, ey - 3), (ex + 15, ey - 3)], INK, 4)
        elif st == "open": c.ell((ex, ey), 15, 17, (255, 255, 255), INK, 3); c.ell((ex + look[0], ey + look[1]), 7.5, 7.5, INK); c.ell((ex + look[0] + 3, ey + look[1] - 3), 2.5, 2.5, (255, 255, 255))
        elif st == "wide": c.ell((ex, ey - 2), 19, 23, (255, 255, 255), INK, 3); c.ell((ex + look[0] * 0.3, ey - 2), 3.5, 3.5, INK)
    # нос-кнопка
    cel(c, shp_ell(c, (x + 6 * side, y + 14 * sy), 7, 7), hx("F0B88E"), None, None, ow=3)
    # румянец
    for dx in (-40, 38): c.ell((x + dx * sx, y + 26 * sy), 11, 6, (240, 138, 122, 90))
    # рот
    my = y + 32 * sy
    if mouth == "flat": c.line([(x - 9, my), (x + 9, my)], INK, 4)
    elif mouth == "frown": c.arc((x, my + 10), 13, 7, 200, 340, INK, 4)
    elif mouth == "o": rr_ = 10 + 5 * math.sin(tt * 5.2) ** 2; cel(c, shp_ell(c, (x, my + 4), rr_, rr_ + 3), hx("4A1C28"), None, None, ow=3); c.ell((x, my + 10), rr_ * 0.6, rr_ * 0.35, hx("D9606E"))
    elif mouth == "big": cel(c, shp_ell(c, (x, my + 6), 15, 20), hx("4A1C28"), None, None, ow=4); c.ell((x, my + 16), 9, 6, hx("D9606E")); c.rr_ = None if False else None; c.line([(x - 10, my - 8), (x + 10, my - 8)], (255, 255, 255), 5, caps=False)
    elif mouth == "yawn": cel(c, shp_ell(c, (x, my + 6), 10, 15), hx("4A1C28"), None, None, ow=3)
    if sweat > 0:
        for i, (dx, dy) in enumerate(((-76, -36), (74, -10), (-70, 30))):
            p = (tt * 1.7 + i / 3) % 1; c.ell((x + dx * sx, y + dy + 30 * p), 5, 8, (150, 210, 255, int(230 * sweat * (1 - 0.6 * p))), INK, 2)
def mitten(c, pos, ang=0.0, fist=False, skin=SKIN):
    x, y = pos; ca, sa = math.cos(ang), math.sin(ang)
    def R(dx, dy): return (x + dx * ca - dy * sa, y + dx * sa + dy * ca)
    w_, h_ = (52, 48) if fist else (60, 50)
    body = shp_poly(c, [R(-w_ / 2, -h_ / 2), R(w_ / 2, -h_ / 2), R(w_ / 2, h_ / 2), R(-w_ / 2, h_ / 2)])
    cel(c, shp_union(body, shp_ell(c, R(0, -h_ / 2 + 4), w_ / 2 - 2, h_ / 2 - 6), shp_ell(c, R(-w_ / 2 + 6, 0), 14, h_ / 2 - 4)), skin, SKIN_S, SKIN_H, ds=(8, 6), dh=(3, 3), ow=4)
    if not fist:
        cel(c, shp_ell(c, R(-4, -h_ / 2 - 6), 13, 9), skin, SKIN_S, None, ow=3)
        for i in range(3): c.line([R(w_ / 2 - 6 - i * 12, h_ / 2 - 2), R(w_ / 2 - 6 - i * 12 - 2, -4)], hx("C98A62"), 3, caps=False)
    else:
        for i in range(4): c.arc(R(w_ / 2 - 8 - i * 11, -2), 7, 9, 200, 340, hx("C98A62"), 3)
def ik(S, W_, l1=140.0, l2=120.0):
    dx, dy = W_[0] - S[0], W_[1] - S[1]; d = min(math.hypot(dx, dy), l1 + l2 - 1) or 1; a = math.atan2(dy, dx)
    cosb = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d); b = math.acos(max(-1, min(1, cosb)))
    ang = a + b                                                                                                       # локоть вниз
    return (S[0] + l1 * math.cos(ang), S[1] + l1 * math.sin(ang))
def arm(c, S, wrist, hand_pos, ang=0.0, fist=False, pj=True):
    E = ik(S, wrist)
    cel(c, shp_cap(c, S, E, 34, 30), PJ, PJ_S, PJ_H, ds=(10, 8), dh=(4, 3), ow=5, extra=lambda m: stripes(c, m, 70, 18, 6, PJ_ST, S))
    cel(c, shp_cap(c, E, wrist, 28, 24), PJ, PJ_S, PJ_H, ds=(10, 8), dh=(4, 3), ow=5, extra=lambda m: stripes(c, m, 70, 18, 6, PJ_ST, E))
    cel(c, shp_ell(c, wrist, 14, 14), PJ_ST, None, None, ow=4); mitten(c, hand_pos, ang, fist)
def phone_pts(ctr, w, h, skew=12):
    return [(ctr[0] - w / 2 + skew, ctr[1] - h / 2), (ctr[0] + w / 2 + skew, ctr[1] - h / 2), (ctr[0] + w / 2 - skew, ctr[1] + h / 2), (ctr[0] - w / 2 - skew, ctr[1] + h / 2)]
def draw_phone(c, ctr, w=110, h=44, lit=0.0, ang=0.0, sx=1.0, sy=1.0, img=None):
    pts = phone_pts((0, 0), w * sx, h * sy); ca, sa = math.cos(ang), math.sin(ang); pts = [(ctr[0] + p[0] * ca - p[1] * sa, ctr[1] + p[0] * sa + p[1] * ca) for p in pts]
    cel(c, shp_poly(c, pts), hx("1E202C"), None, hx("3A3E54"), dh=(3, 3), ow=4)
    inner = phone_pts((0, 0), (w - 12) * sx, (h - 10) * sy); inner = [(ctr[0] + p[0] * ca - p[1] * sa, ctr[1] + p[0] * sa + p[1] * ca) for p in inner]
    c.poly(inner, mix(hx("2C3248"), hx("BFD9FF"), lit))
    if lit > 0.05 and img is not None: glow(img, c, ctr, 190 * c.cam.k / S1, (190, 220, 255), 0.5 * lit)
_GL = None
def glow(im, c, ctr, r_px, col, a):
    global _GL
    if a < 0.01: return
    if _GL is None:
        n = 128; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32); d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2); _GL = Image.fromarray((np.clip(1 - d, 0, 1) ** 2 * 255).astype(np.uint8), "L")
    x, y = c.T(ctr); sz = int(2 * r_px * S1 / S1 * 1.0)
    if sz < 4: return
    g = _GL.resize((sz, sz), Image.BILINEAR).point(lambda v: int(v * min(a, 1))); layer = Image.new("RGBA", (sz, sz), tuple(col) + (0,)); layer.putalpha(g)
    px, py = int(x - sz / 2), int(y - sz / 2); x0, y0 = max(px, 0), max(py, 0); x1, y1 = min(px + sz, im.width), min(py + sz, im.height)
    if x1 > x0 and y1 > y0: im.alpha_composite(layer.crop((x0 - px, y0 - py, x1 - px, y1 - py)), (x0, y0))

# --- полноростовой герой (прыжок)
POSES = {   # относительно таза; лицом влево
    "A": dict(sh=(-40, -208), hd=(-58, -300), el=(-100, -110), hand=(-160, -190), kn=(-150, -40), an=(-60, 80), el2=(-10, -130), hand2=(-30, -60)),
    "B": dict(sh=(-125, -176), hd=(-158, -268), el=(-30, -110), hand=(80, -50), kn=(-150, -90), an=(-70, 66), el2=(20, -130), hand2=(105, -85)),
    "C": dict(sh=(-12, -212), hd=(-20, -306), el=(-28, -300), hand=(-30, -420), kn=(-10, 170), an=(-5, 340), el2=(10, -290), hand2=(20, -415)),
    "D": dict(sh=(0, -215), hd=(0, -310), el=(-60, -330), hand=(-90, -450), kn=(-12, 172), an=(-28, 345), el2=(60, -330), hand2=(90, -450)),
    "E": dict(sh=(-8, -215), hd=(-12, -310), el=(-70, -325), hand=(-100, -440), kn=(-22, 172), an=(-45, 350), el2=(52, -325), hand2=(80, -440))}
def pose_lerp(a, b, k): return {key: lerp2(POSES[a][key], POSES[b][key], k) for key in POSES[a]}
def full_hero(c, P, pose, es, mouth, tt, sx=1.0, sy=1.0, scare=1.0, rot=0.0):
    def W_(p):
        x, y = p[0] * sx, p[1] * sy; return (P[0] + x * math.cos(rot) - y * math.sin(rot), P[1] + x * math.sin(rot) + y * math.cos(rot))
    sh, hd, el, hand, kn, an, el2, hand2 = [W_(pose[k]) for k in ("sh", "hd", "el", "hand", "kn", "an", "el2", "hand2")]; pel = W_((0, 0))
    ln = lambda p, q: (q[0] - p[0], q[1] - p[1])
    # дальняя нога и рука
    kn2 = (kn[0] + 24, kn[1] - 4); an2 = (an[0] + 30, an[1] - 2)
    cel(c, shp_cap(c, pel, kn2, 44, 36), PANT_S, None, None, ow=5); cel(c, shp_cap(c, kn2, an2, 36, 28), PANT_S, None, None, ow=5)
    cel(c, shp_cap(c, an2, (an2[0] - 24, an2[1] + 14), 28, 22), SKIN_S, None, None, ow=4)
    cel(c, shp_cap(c, sh, el2, 30, 26), PJ_S, None, None, ow=5); cel(c, shp_cap(c, el2, hand2, 26, 22), PJ_S, None, None, ow=5); mitten(c, hand2, 0.0, True, SKIN_S)
    # ближняя нога
    cel(c, shp_cap(c, pel, kn, 46, 38), PANT, PANT_S, PANT_H, ow=6); cel(c, shp_cap(c, kn, an, 38, 30), PANT, PANT_S, PANT_H, ow=6)
    cel(c, shp_cap(c, (an[0], an[1] - 4), (an[0] - 40, an[1] + 14), 30, 24), SKIN, SKIN_S, SKIN_H, ow=5)
    # торс
    sp = (sh[0] + 0, sh[1]); tor = shp_poly(c, [(sh[0] - 36, sh[1]), (sh[0] + 40, sh[1] + 4), (pel[0] + 38, pel[1] - 4), (pel[0] - 40, pel[1])])
    cel(c, tor, PJ, PJ_S, PJ_H, ds=(12, 8), dh=(5, 3), ow=6, extra=lambda m: stripes(c, m, 80, 16, 5, PJ_ST, sh))
    cel(c, shp_cap(c, (sh[0], sh[1] - 4), (hd[0], hd[1] + 62), 34, 30), SKIN, SKIN_S, None, ow=4)
    # ближняя рука
    cel(c, shp_cap(c, sh, el, 32, 28), PJ, PJ_S, PJ_H, ow=6, extra=lambda m: stripes(c, m, 70, 18, 6, PJ_ST, sh)); cel(c, shp_cap(c, el, hand, 28, 24), PJ, PJ_S, PJ_H, ow=6, extra=lambda m: stripes(c, m, 70, 18, 6, PJ_ST, el)); mitten(c, hand, 0.0, False)
    face(c, hd, es, mouth, (0, 0), tt, sx=0.94 if sy > 1.05 else 1.0, sy=1.04 if sy > 1.05 else 1.0, pale=1.0, hair_up=1.0, brow="scared" if es == "wide" else "neutral", sweat=0.0)

# ===================== состояние кадра
def eyes_state(t): return V1.eyes_state(t)
def ph_state(t):
    ring = next((k for k in range(5) if ringing(t, k)), None); lit = 0.0; shake = 0.0
    if ring is not None: u = t - RING[ring][0]; shake = math.sin(u * 90) * 4; lit = 0.55 + 0.45 * (math.sin(u * 26) > 0)
    return ring, lit, shake
def hand_target(t):
    """(wrist-hand center, ang, fist, strike_u(0..), smear) — кисть и положение руки."""
    REST = (262, 1118); WIND = (330, 1050)
    for k in range(5):
        for (h, off) in hits(k):
            tgt = (REST[0] + off, REST[1])
            if h - 0.125 <= t < h:
                u = (t - (h - 0.125)) / 0.125
                return (lerp2(REST, WIND, ease(min(u * 1.6, 1))) if u < 0.65 else lerp2(WIND, lerp2(WIND, tgt, 0.4), (u - 0.65) / 0.35)), -0.35, True, u, 0.0
            if h <= t < h + 0.083: u = (t - h) / 0.083; return lerp2(WIND, tgt, u * u), 0.0, True, u, 1.0 if u < 0.7 else 0.0
            if h + 0.083 <= t < h + 0.125: return tgt, 0.0, True, 1.0, 0.0
            if h + 0.125 <= t < h + 0.42: u = (t - (h + 0.125)) / 0.295; ov = 1 + 0.08 * math.sin(u * math.pi); return lerp2(tgt, REST, ease(u) * (1 if u < 1 else 1)), 0.0, u < 0.4, 1.0, 0.0
    if T_GRAB <= t < T_GRAB + 0.3: return lerp2(REST, REST, 0), 0.0, False, 0.0, 0.0
    return REST, 0.0, False, 0.0, 0.0
def last_hit(t):
    best = None
    for k in range(5):
        for (h, off) in hits(k):
            if h <= t < h + 0.6: best = (t - h, off)
    return best
def breath(t):
    if t < 2.2: return 0.0
    if T_SLEEP <= t < T_WAKE: u = (t / 2.4) % 1; return 9 * (math.sin(math.pi * u / 0.4 / 1.0) if u < 0.4 else 0.0 if False else (1 - (u - 0.4) / 0.6) * 1.0) * (1 if u >= 0.4 else math.sin(math.pi / 2 * u / 0.4))
    return (6 if t < tk(0) else 4) * math.sin(t * 2 * math.pi / 2.8)
def cam_for(t):
    z, c = V1.zoom_at(t)
    # более крупные планы (герой по спецификации меньше): увеличиваем зум крупных планов
    k = 1.0
    if z >= 1.7: k = 1.28
    elif z >= 1.4: k = 1.12
    z = z * k
    if T_CROUCH <= t < T_CROUCH + 1.0: z, c = 1.2, (600, 820 - 400 * seg(t, T_JUMP + 0.12, T_JUMP + 0.55))
    if T_JUMP + 1.0 <= t < 18.7: z, c = 1.25, (560, 1050)
    # ручная камера
    dx = 5 * math.sin(2 * math.pi * 0.35 * t) + 2.5 * math.sin(2 * math.pi * 0.9 * t + 1.3); dy = 4 * math.sin(2 * math.pi * 0.27 * t + 0.5) + 2 * math.sin(2 * math.pi * 1.1 * t)
    z *= 1 + 0.004 * math.sin(2 * math.pi * 0.36 * t)
    for k_ in range(5):
        for (h, off) in hits(k_):
            u = t - h
            if 0 <= u < 0.4: dx += 14 * math.exp(-u / 0.08) * math.cos(2 * math.pi * 18 * u); dy += 14 * math.exp(-u / 0.08) * math.sin(2 * math.pi * 18 * u + 1)
    if T_SHOCK <= t < T_SHOCK + 0.4: u = t - T_SHOCK; dx += 6 * math.cos(2 * math.pi * 20 * u); dy += 6 * math.sin(2 * math.pi * 20 * u)
    if t >= T_LAND and t < T_LAND + 0.4: u = t - T_LAND; dy += 14 * math.exp(-u / 0.08) * math.cos(2 * math.pi * 18 * u)
    roll = 0.25 * math.sin(2 * math.pi * 0.2 * t)
    for k_ in range(5):
        if slap_t(k_) - 0.3 <= t < slap_t(k_) + 0.25: roll += 1.5
    if T_SHOCK <= t < T_SHOCK + 0.4: roll -= 3.0
    z = min(max(z, 1.0), 3.2); cxx = min(max(c[0] + dx, W / z / 2), W - W / z / 2); cyy = min(max(c[1] + dy, H / z / 2), H - H / z / 2)
    return Cam(z, cxx, cyy), roll

# ===================== кадр
def render(t, cover=False):
    st = statics(); cam, roll = cam_for(t); z = cam.z
    if cover: cam, roll = Cam(2.35, 395, 1000), 0.0; z = cam.z
    sky = Image.blend(view(st["sky_n"], cam), view(st["sky_d"], cam), sky_k(t)).convert("RGBA")
    rb = 1.5 if z <= 1.4 else (3.5 if z < 1.9 else 5.0)
    sky.alpha_composite(view(st["far_b"][rb], cam)); tint = tint_at(t)
    if sky_k(t) > 0 and tint < 0.5:
        dxs = 42 * min(max((t - T0) / 1.4, 0), 5); bm = view(st["beam"], Cam(cam.z, cam.cx - dxs, cam.cy)); sky.alpha_composite(bm)
    sky.alpha_composite(view(st["near"], cam)); img = sky; c = CvC(img, cam)
    # пыль в луче
    if sky_k(t) > 0 and tint < 0.5:
        for i, (fx, fy, ph_) in enumerate(st["dust"]):
            x_ = 640 + fx * 370 * (1 - fy * 0.55) + 260 * fy + 8 * ((t * 1.0) % 20) - 42 * min(max((t - T0) / 1.4, 0), 5) * 0; y_ = 720 + fy * 600 - 6 * (t % 40)
            al = int(max(30, (70 + 70 * math.sin(t * 3 + ph_)) * (0.6 + 0.4 * math.sin(t * 3 + i)))); c.ell((x_, y_), 3, 3, (255, 248, 210, al))
    jump = t >= T_JUMP; ring, lit, shake = ph_state(t); lh = last_hit(t); es = eyes_state(t)
    hold = T_GRAB + 0.3 <= t < T_CROUCH
    sit = T_CROUCH <= t < T_JUMP + 0.0
    # --- голова/тело
    hand_pos, hang, fist, su, smear = hand_target(t); hsx, hsy, hdy = 1.0, 1.0, 0.0
    if lh is not None:
        u, off = lh
        if u < 0.083: hsx, hsy, hdy = 1.04, 0.94, 6
        elif u < 0.25: hsx, hsy = 0.97, 1.04
    bob = breath(t)
    hc = (300, 988 + hdy - 0.0 * bob)
    if 2.2 <= t < 2.8: hc = (300, hc[1] + 6 * seg(t, 1.9, 2.2))
    if tk(4) + 0.35 <= t < tk(4) + 1.13:
        u = t - (tk(4) + 0.35); up = 40 * (ease(u / 0.3) if u < 0.3 else (1 if u < 0.6 else 1 - ((u - 0.6) / 0.18) ** 2)); hc = (hc[0] - 10 * up / 40, hc[1] - max(up, 0))
    if T_WAKE <= t < T_WAKE + 0.3: hc = (300, 988 - 30 * ease((t - T_WAKE) / 0.3))
    if T_SHOCK <= t < T_CROUCH: hc = (hc[0] + 4 * math.sin(2 * math.pi * 9 * t), hc[1] + 3 * math.cos(2 * math.pi * 9 * t))
    pale = seg(t, T_SHOCK, T_SHOCK + 0.25) if t >= T_SHOCK else 0.0
    mouth = "frown" if es in ("squint", "half") else ("big" if es == "wide" else ("o" if (T_SLEEP + 0.2 <= t < T_WAKE) else "flat"))
    if tk(4) + 0.55 <= t < tk(4) + 0.78 and es == "half": mouth = "yawn"
    brow = {"squint": "angry", "half": "sleepy", "wide": "scared"}.get(es, "neutral")
    look = (-6, 6) if es == "half" and t < 3.0 else ((5, -3) if es == "open" else (-4, 4))
    dent = ringing and False
    if not jump:
        if not sit:
            c.ell((300, 1062), 82, 20, PIL_S + (230,))                                                                              # вмятина подушки
            # плечо и шея
            cel(c, shp_cap(c, (318, 1040), (362, 1030), 34, 34), SKIN, SKIN_S, None, ow=4)
            sh_poly = smooth_closed([(356, 1034), (392, 992), (428, 985), (452, 1020), (446, 1062), (386, 1066)], 6)
            m = cel(c, shp_poly(c, sh_poly), PJ, PJ_S, PJ_H, ds=(12, 8), dh=(5, 3), ow=5, extra=lambda m: stripes(c, m, 70, 18, 6, PJ_ST, (392, 992)))
            c.ell((366, 1031), 22, 12, PJ_ST); c.ell((376, 1046), 4, 4, (255, 255, 255))
            # рука (до одеяла)
            S_ = (430, 1032); wrist = (hand_pos[0] + 44, hand_pos[1] + 8)
            if ring is not None or su > 0 or T_GRAB <= t: pass
            if T_GRAB <= t < T_GRAB + 0.3: hand_pos = lerp2((262, 1118), (262, 1118), 0)
            if hold:
                u = seg(t, T_GRAB + 0.3, T_GRAB + 0.62); hp = lerp2((262, 1118), (400, 905), u); wrist = (hp[0] + 40, hp[1] + 12); hand_pos = hp
            elif T_GRAB <= t < T_GRAB + 0.3:
                pass
            if smear > 0:
                for i, a in enumerate((0.5, 0.3, 0.15)): hp = (hand_pos[0] + 40 * (i + 1) * 0.9, hand_pos[1] - 34 * (i + 1) * 0.7); mitten(c, hp, hang, True) if False else c.ell(hp, 28, 24, SKIN + (int(255 * a),))
            if not (ring is None and t < 1.2):
                arm(c, S_, wrist, hand_pos, hang, fist)
            # телефон
            if not hold:
                pc = (250 + shake, 1122); ang_ = 0.0; sxp, syp = 1.0, 1.0
                if lh and lh[1] == 0:
                    u = lh[0]; pc = (250 + 36 * min(u * 6, 1), 1122 - 46 * math.sin(min(u / 0.375, 1) * math.pi) * math.exp(-u * 2)); ang_ = 1.4 * min(u / 0.45, 1) * (1 + 0.4 * math.sin(u * 30))
                    if u < 0.083: sxp, syp = 1.18, 0.78
                draw_phone(c, pc, 110, 44, 0.5 if 1.2 <= t < 2.2 else lit, ang_, sxp, syp, img)
                if ring is not None:
                    for i in range(3): p = ((t * 2.2 + i / 3) % 1); c.ell((pc[0], pc[1] - 6), 70 + 120 * p, 30 + 60 * p, None, (255, 255, 255, int(190 * (1 - p))), 3)
            # голова
            face(c, hc, es, mouth, look, t, hsx, hsy, brow=brow, pale=pale, sweat=(1.0 if t >= T_SHOCK else 0.0), hair_up=(1.0 if t >= T_SHOCK else 0.0), scare=0)
            if T_SLEEP + 0.2 <= t < T_BUB + 0.12 and es == "closed":
                r_ = 8 + 30 * seg(t, T_SLEEP + 0.2, T_BUB) + 3 * math.sin(t * 5.2)
                if t < T_BUB: c.ell((hc[0] + 6, hc[1] + 22 + r_ * 0.7), r_, r_, (200, 232, 255, 120), (150, 190, 230, 255), 3); c.ell((hc[0] + 6 - r_ * 0.3, hc[1] + 22 + r_ * 0.4), r_ * 0.2, r_ * 0.2, (255, 255, 255, 220))
                else:
                    for i in range(6): a_ = i * math.pi / 3; q = (t - T_BUB) / 0.12; c.line([(hc[0] + 6 + 36 * math.cos(a_), hc[1] + 55 + 36 * math.sin(a_)), (hc[0] + 6 + (36 + 30 * q) * math.cos(a_), hc[1] + 55 + (36 + 30 * q) * math.sin(a_))], (255, 255, 255, 230), 4)
            if hold:
                hp = hand_pos; pp = (hp[0] + 40, hp[1] - 70); c.poly([(pp[0] - 60, pp[1] - 100), (pp[0] + 60, pp[1] - 100), (pp[0] + 60, pp[1] + 100), (pp[0] - 60, pp[1] + 100)], hx("1E202C"), INK, 4); c.poly([(pp[0] - 52, pp[1] - 92), (pp[0] + 52, pp[1] - 92), (pp[0] + 52, pp[1] + 92), (pp[0] - 52, pp[1] + 92)], hx("D8E8FF")); glow(img, c, pp, 220, (190, 220, 255), 0.45)
                c.text(pp, "8:59" if t >= T_SHOCK else "9:03", 40, (28, 32, 56))
        else:
            P = (650, 1010); k = seg(t, T_CROUCH, T_CROUCH + 0.3); pose = pose_lerp("A", "B", k) if t < T_CROUCH + 0.3 else POSES["B"]
            if t >= T_CROUCH + 0.4: pose = POSES["B"]; P = (650 + 1.5 * math.sin(t * 90), 1010 + 1.5 * math.sin(t * 80))
            draw_blanket(c, t, jump, ring, es, lh, body_k=1.0 - 0.7 * seg(t, T_CROUCH, T_CROUCH + 0.3))
            full_hero(c, P, pose, "wide", "big", t, sy=0.9 + 0.1 * (1 - k * 0.5), scare=1.0)
            draw_phone(c, (250, 1122), 110, 44, 0, 0.12)
    # --- прыжок
    if jump and t < T_JUMP + 0.6:
        u = t - T_JUMP
        if u < 0.04: P = (650, 1010); pose = POSES["B"]
        elif u < 0.12: k = (u - 0.04) / 0.08; P = (650 - 8 * k, 1010 - 280 * ease(k)); pose = pose_lerp("B", "C", k)
        elif u < 0.30: k = (u - 0.12) / 0.18; P = (642 - 40 * k, 730 - 420 * k ** 1.2); pose = pose_lerp("C", "D", k)
        else: k = (u - 0.30) / 0.30; P = (602 - 120 * k, 310 - 1100 * k ** 1.5); pose = pose_lerp("D", "E", min(k * 2, 1))
        sy_ = 1.12 if 0.04 < u < 0.3 else 1.05
        draw_blanket(c, t, jump, ring, es, lh, body_k=0.0 if u > 0.1 else 0.3)
        for i in range(5):
            off = 90 + i * 70; c.line([(P[0] + 20 * (i - 2), P[1] + 150 + off), (P[0] + 20 * (i - 2), P[1] + 150 + off + 220)], INK + (200,), 5)
        full_hero(c, P, pose, "wide", "big", t, sy=sy_, rot=-0.1 * seg(u, 0.12, 0.6))
        draw_phone(c, (250, 1122 + 40 * 0), 110, 44, 0, 0.12 + 0.5 * (u > 0.3))
    elif jump:
        draw_blanket(c, t, jump, ring, es, lh, body_k=0.0)
        draw_phone(c, (250, 1122), 110, 44, 0, 0.62)
        c.ell((330, 1052), 90, 20, PIL_S + (200,))
        for i in range(3):
            p = seg(t, T_JUMP + 0.2 + 0.1 * i, T_LAND - 0.1 + 0.1 * i)
            if 0 < p < 1: c.ell((300 + 40 * i + 30 * math.sin(p * 9 + i), 760 + 340 * p), 5, 12, (255, 255, 255, 255))
        if T_LAND <= t < T_LAND + 0.5:
            q = (t - T_LAND) / 0.5
            for i in range(10): a_ = i * 0.628; c.ell((700 + (60 + 120 * q) * math.cos(a_) * 1.3, 1190 + 30 * math.sin(a_) * q), 14 + 16 * q, 14 + 16 * q, (190, 180, 170, int(80 * (1 - q))))
    if not jump and not sit:
        draw_blanket(c, t, jump, ring, es, lh, body_k=1.0, drawn_after=True)
    # Z, звёзды удара
    if not jump and es == "closed" and (2.2 <= t < 2.8 or T_SLEEP + 0.2 <= t < T_BUB or any(slap_t(k) + 0.3 <= t < tk(k) + STEPS[k] for k in range(5))):
        for i in range(3): p = ((t * 0.9 + i / 3) % 1); c.text((400 + 40 * p + 20 * i, 850 - 190 * p), "Z", 34 + 20 * p, (255, 255, 255, int(235 * (1 - p))), 2)
    for k in range(5):
        for (h, off) in hits(k):
            if abs(t - h) < 0.1 and off == 0:
                u = 1 - abs(t - h) / 0.1
                for i in range(8): a = i * math.pi / 4; c.line([(250 + 60 * math.cos(a), 1114 + 36 * math.sin(a)), (250 + (60 + 60 * u) * math.cos(a), 1114 + (36 + 40 * u) * math.sin(a))], (255, 255, 255, 230), 5)
    # ночь/тон
    if tint > 0.01: img.alpha_composite(Image.new("RGBA", (CW, CH), (8, 12, 40, int(255 * min(tint, 1)))))
    if 1.2 <= t < 2.2: glow(img, c, (310, 1010), 300, (150, 190, 255), 0.35)
    if 3.4 <= t < 4.6: img.alpha_composite(Image.new("RGBA", (CW, CH), (255, 170, 90, int(46 * (1 - seg(t, 3.4, 4.6))))))
    # метка времени (поверх, в экранных координатах, чтобы оставалась крупной)
    lab, lu = label_at(t)
    if lab and tint < 0.9:
        sc = 1 + 0.4 * (1 - ease(lu / 0.16)) if lu < 0.16 else 1.0
        if lab == "8:59": sc *= 1.3
        col = (255, 64, 56, 255) if lab == "8:59" else (255, 255, 255, 255)
        d = ImageDraw.Draw(img); anchor = c.T((330, 690 if lab != "8:59" else 640)); sz = int(120 * sc * S1 / 1.5 * max(0.9, min(z, 1.5)) / 1.0 / 1.0)
        f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", int(130 * sc))
        ay = min(max(anchor[1], 380 * S1), 900 * S1); ax = min(max(anchor[0], 270 * S1), 800 * S1)
        d.text((ax, ay), lab, font=f, fill=col, anchor="mm", stroke_width=int(9 * S1 / 1.5 * 1.5), stroke_fill=(0, 0, 0, 255))
    if roll != 0:
        im2 = img.rotate(roll, resample=Image.BICUBIC, center=(CW / 2, CH / 2)); sc2 = 1.0 + abs(math.radians(roll)) * 1.2 + 0.01
        w_, h_ = CW / sc2, CH / sc2; img = im2.resize((CW, CH), Image.BILINEAR, box=((CW - w_) / 2, (CH - h_) / 2, (CW + w_) / 2, (CH + h_) / 2))
    return post(img.convert("RGB").resize((W, H), Image.LANCZOS), t, tint, z, cover)
_vig = {}
def vignette(k):
    if k not in _vig:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2); _vig[k] = np.clip(1 - (1 - k) * np.clip(d - 0.55, 0, 1) ** 1.4 * 1.6, 0, 1)
    return _vig[k]
def post(im, t, tint, z, cover=False):
    a = np.asarray(im, dtype=np.float32) / 255.0; lum = (a * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    dk = np.clip((0.5 - lum) / 0.5, 0, 1); dk = dk * dk * (3 - 2 * dk); hl = np.clip((lum - 0.55) / 0.45, 0, 1); hl = hl * hl * (3 - 2 * hl)
    night = 0.3 + 0.7 * min(1.0, tint * 1.5); teal = np.array([0.86, 1.0, 1.08], np.float32) * (1 - night) + np.array([0.78, 0.98, 1.12], np.float32) * night
    a = a * (1 + dk * (teal - 1)); a = a * (1 + hl * (np.array([1.07, 1.0, 0.90], np.float32) - 1))
    a = a + 0.12 * (a - 0.5) * (1 - np.abs(2 * a - 1)) * 0 + 0.12 * (np.clip(a, 0, 1) - 0.5) * 0.6
    l2 = (a * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True); a = l2 + (a - l2) * 1.08
    # bloom
    br = np.clip((lum - 0.82) / 0.18, 0, 1); bi = Image.fromarray((br[..., 0] * 255).astype(np.uint8)).resize((W // 2, H // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    a = a + (np.asarray(bi, dtype=np.float32) / 255.0)[..., None] * (0.2 if tint > 0.4 else 0.35) * np.array([1.0, 0.95, 0.8], np.float32)
    a = a * vignette(0.62 if (cover or z > 2.0) else 0.78)[..., None]
    rng = np.random.default_rng(int(t * 24 + 5) * 7919); sig = (7 if tint > 0.4 else 5) / 255.0; a = a + rng.standard_normal(a.shape[:2] + (1,)).astype(np.float32) * sig
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def draw_blanket(c, t, jump, ring, es, lh, body_k=1.0, drawn_after=False):
    TOP = [(392, 1016), (432, 968), (480, 982), (540, 950), (600, 982), (676, 944), (752, 966), (830, 898), (898, 972), (950, 1004), (984, 1020), (1012, 1070)]
    BOT = [(1010, 1200), (960, 1222), (860, 1212), (760, 1228), (660, 1210), (560, 1226), (470, 1215)]
    W_ = [0.6, 1.0, 0.6, 1.0, 0.5, 0.3, 0.3, 0.1, 0.0, 0.0, 0.0, 0.0]
    if body_k is None: body_k = 1.0
    amp = breath(t); base_y = 1040
    pts = []
    for i, (x, y) in enumerate(TOP):
        yy = base_y + (y - base_y) * body_k; yy -= amp * (0.2 if i in (0, 1) else 1.0) * [0.6, 1.0, 0.6, 1.0, 0.5, 0.3, 0.3, 0.1, 0, 0, 0, 0][i] * body_k
        if lh is not None and not jump: yy += 22 * math.exp(-lh[0] / 0.22) * math.sin(i * 0.55 * 2 - lh[0] * 18)
        if ring is not None and not jump: yy += 2.5 * math.sin(t * 90 + i)
        pts.append((x, yy))
    ys = [q[1] for q in pts]
    for _ in range(2): ys = [ys[0]] + [0.25 * ys[i - 1] + 0.5 * ys[i] + 0.25 * ys[i + 1] for i in range(1, len(ys) - 1)] + [ys[-1]]
    pts = [(q[0], ys[i]) for i, q in enumerate(pts)]
    top = smooth_closed(pts, 8)
    outline = top + BOT
    rot = 0.0; ox = oy = 0.0; sy_b = 1.0; lift = 0.0
    if jump:
        tau = min(max((t - (T_JUMP + 0.1)) / 1.5, 0.0), 1.0)
        oy = -1400 * math.sin(math.pi * tau) * (1 + 0.12 * math.sin(3.5 * math.pi * tau) * (1 - tau)); ox = 260 * math.sin(math.pi * tau) * (1 - tau); rot = 0.5 * math.sin(2 * math.pi * tau) * (1 - tau)
        u2 = t - T_LAND
        if 0 <= u2 < 0.12: sy_b = 1 - 0.18 * (1 - u2 / 0.12)
        elif 0.12 <= u2 < 0.42: lift = 18 * math.sin(math.pi * (u2 - 0.12) / 0.3)
    cx0, cy0 = 700, 1100
    def tr(p):
        x, y = p[0], 1200 - (1200 - p[1]) * sy_b
        return (cx0 + (x - cx0) * math.cos(rot) - (y - cy0) * math.sin(rot) + ox, cy0 + (x - cx0) * math.sin(rot) + (y - cy0) * math.cos(rot) + oy - lift)
    poly = [tr(p) for p in outline]; shape = shp_poly(c, poly)
    def folds(m0):
        for src, ii in (((540, 950), 3), ((676, 944), 5), ((830, 898), 7)):
            src = (src[0], pts[ii][1] - 10)
            a = tr((src[0], src[1] + 20)); b = tr((src[0] + 90, 1190)); mid = tr((src[0] + 30, (src[1] + 1190) / 2 - 10)); c.line([a, mid, b], BL_F, 3, caps=False)
        c.line([tr((392, 1016)), tr((470, 1215))], BL_S, 5, caps=False)
    cel(c, shape, BL, BL_S, BL_H, ds=(26, 18), dh=(8, 6), ow=6, extra=folds)
def frame(t, cover=False):
    if t < 1.2: return V1.phone_scene(t)
    if t >= T_LOOP: return V1.phone_scene(t - T_LOOP, end=True)
    return render(t, cover)
def mb_offsets(t):
    for k in range(5):
        for (h, off) in hits(k):
            if h - 0.125 <= t <= h + 0.1: return 8
    if T_JUMP <= t < T_JUMP + 0.55: return 12
    if T_JUMP + 0.55 <= t < T_LAND: return 5
    return 1
def render_mb(i):
    t = i / FPS; n = mb_offsets(t)
    if n == 1 or t < 1.2 or t >= T_LOOP: return frame(t).tobytes()
    acc = None
    for j in range(n): tj = t + ((j + 0.5) / n - 0.5) * (1 / 48); f = np.asarray(frame(tj), dtype=np.float32); acc = f if acc is None else acc + f
    return Image.fromarray((acc / n).astype(np.uint8)).tobytes()

if __name__ == "__main__":
    wd = f"{ROOT}/work/snooze_1"; os.makedirs(wd, exist_ok=True); statics()
    if len(sys.argv) > 1:
        for tt_ in sys.argv[1:]: frame(float(tt_)).save(f"{wd}/pv2_{tt_}.png")
        sys.exit(0)
    import multiprocessing as mp
    N = int(DUR * FPS)
    V1.write_wav(f"{wd}/snooze.wav"); cover = frame(15.1, cover=True); cover.save(f"{ROOT}/covers/72_snooze_click.jpg", quality=94)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{wd}/snooze.wav",
                           "-af", "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-2.5:LRA=7", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-shortest",
                           f"{wd}/snooze_raw.mp4"], stdin=subprocess.PIPE)
    cb = cover.tobytes()
    with mp.Pool(4) as pool:
        for i, fb in enumerate(pool.imap(render_mb, range(N), chunksize=2)): ff.stdin.write(cb if i < 3 else fb)
    ff.stdin.close(); ff.wait(); os.makedirs(f"{ROOT}/hq", exist_ok=True); subprocess.run(["cp", f"{wd}/snooze_raw.mp4", f"{ROOT}/hq/snooze_1_hq.mp4"], check=True); print("done")
