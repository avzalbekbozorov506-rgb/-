"""«Ещё пять минут» — 2D-мультфильм без слов, всё рисуется кодом (PIL/numpy). Сценарий: scripts/snooze_1.md.
Запуск: python3 cartoon/snooze.py            → hq/snooze_1_hq.mp4 + covers/72_snooze_click.jpg
        python3 cartoon/snooze.py 5.3 17.4   → превью кадров work/snooze_1/pv_*.png"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
S = 1.5; W, H = 1080, 1920; CW, CH = int(W * S), int(H * S); FPS = 30; DUR = 20.0
INK = (24, 22, 34); SKIN = (255, 236, 190); WHITE = (255, 255, 255)
def F(size, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", max(int(size * S), 6))
def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def seg(t, a, b): return ease((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def lerp2(p, q, k): return (lerp(p[0], q[0], k), lerp(p[1], q[1], k))
def mix(c1, c2, k): return tuple(int(lerp(c1[i], c2[i], k)) for i in range(3))

class Cv:
    def __init__(s, im): s.im = im; s.d = ImageDraw.Draw(im, "RGBA")
    def P(s, pts): return [(x * S, y * S) for x, y in pts]
    def poly(s, pts, fill, outline=None, w=0):
        s.d.polygon(s.P(pts), fill=fill)
        if outline: s.d.line(s.P(list(pts) + [pts[0]]), fill=outline, width=max(int(w * S), 1), joint="curve")
    def ell(s, c, rx, ry, fill=None, outline=None, w=0):
        s.d.ellipse(((c[0] - rx) * S, (c[1] - ry) * S, (c[0] + rx) * S, (c[1] + ry) * S), fill=fill, outline=outline, width=max(int(w * S), 1) if outline else 0)
    def rr(s, box, r, fill=None, outline=None, w=0):
        s.d.rounded_rectangle((box[0] * S, box[1] * S, box[2] * S, box[3] * S), r * S, fill=fill, outline=outline, width=max(int(w * S), 1) if outline else 0)
    def rect(s, box, fill): s.d.rectangle((box[0] * S, box[1] * S, box[2] * S, box[3] * S), fill=fill)
    def line(s, pts, fill, w, caps=True):
        s.d.line(s.P(pts), fill=fill, width=max(int(w * S), 1), joint="curve")
        if caps:
            for p in (pts[0], pts[-1]): s.ell(p, w / 2, w / 2, fill=fill)
    def arc(s, c, rx, ry, a0, a1, fill, w): s.d.arc(((c[0] - rx) * S, (c[1] - ry) * S, (c[0] + rx) * S, (c[1] + ry) * S), a0, a1, fill=fill, width=max(int(w * S), 1))
    def text(s, xy, t, size, fill, stroke=0, anchor="mm", w="Black"):
        s.d.text((xy[0] * S, xy[1] * S), t, font=F(size, w), fill=fill, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=(0, 0, 0, 255))

_GL = None
def glow(im, c, r, col, a):
    global _GL
    if a < 0.01 or r < 4: return
    if _GL is None:
        n = 128; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32); d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
        _GL = Image.fromarray((np.clip(1 - d, 0, 1) ** 2 * 255).astype(np.uint8), "L")
    sz = int(2 * r * S); g = _GL.resize((sz, sz), Image.BILINEAR).point(lambda v: int(v * min(a, 1)))
    layer = Image.new("RGBA", (sz, sz), tuple(col) + (0,)); layer.putalpha(g)
    im.alpha_composite(layer, (int(c[0] * S - sz / 2), int(c[1] * S - sz / 2))) if (0 <= c[0] * S - sz / 2 and 0 <= c[1] * S - sz / 2 and c[0] * S + sz / 2 <= im.width and c[1] * S + sz / 2 <= im.height) else _paste_clip(im, layer, (int(c[0] * S - sz / 2), int(c[1] * S - sz / 2)))
def _paste_clip(im, layer, pos):
    x, y = pos; x0, y0 = max(x, 0), max(y, 0); x1, y1 = min(x + layer.width, im.width), min(y + layer.height, im.height)
    if x1 <= x0 or y1 <= y0: return
    im.alpha_composite(layer.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))

# ---------------- статика
_cache = {}
def sky_day():
    im = Image.new("RGB", (CW, CH), (0, 0, 0)); c = Cv(im)
    for y in range(WIN[1], WIN[3]): c.rect((WIN[0], y, WIN[2], y + 1), mix((120, 190, 245), (214, 234, 250), (y - WIN[1]) / (WIN[3] - WIN[1])))
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); o = Cv(ov); glow(ov, (850, 470), 230, (255, 236, 160), 0.9); o.ell((850, 470), 54, 54, fill=(255, 244, 190, 255)); im.paste(ov, (0, 0), ov); c = Cv(im)
    for cx, cy, w in ((720, 330, 70), (930, 280, 60), (800, 410, 50)): [c.ell((cx + dx, cy + dy), w * k, 26 * k, fill=(255, 255, 255, 235)) for dx, dy, k in ((0, 0, 1), (-40, 10, .7), (40, 12, .75))]
    c.poly([(640, 640), (700, 560), (790, 600), (880, 530), (1010, 610), (1010, 720), (640, 720)], (112, 152, 170))
    c.poly([(640, 690), (730, 630), (840, 670), (940, 620), (1010, 660), (1010, 720), (640, 720)], (90, 132, 110))
    return im
def sky_night():
    im = Image.new("RGB", (CW, CH), (0, 0, 0)); c = Cv(im)
    for y in range(WIN[1], WIN[3]): c.rect((WIN[0], y, WIN[2], y + 1), mix((8, 12, 38), (34, 44, 88), (y - WIN[1]) / (WIN[3] - WIN[1])))
    rng = np.random.default_rng(7)
    for _ in range(26): c.ell((rng.uniform(650, 1000), rng.uniform(190, 560)), 2.4, 2.4, fill=(255, 255, 230, 220))
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); glow(ov, (790, 320), 120, (200, 215, 255), 0.7); im.paste(ov, (0, 0), ov); c = Cv(im)
    c.ell((790, 320), 40, 40, fill=(244, 240, 206)); c.ell((804, 310), 34, 34, fill=(24, 32, 70))
    c.poly([(640, 640), (700, 580), (790, 620), (880, 560), (1010, 630), (1010, 720), (640, 720)], (14, 20, 44))
    c.poly([(640, 690), (730, 650), (840, 685), (940, 645), (1010, 675), (1010, 720), (640, 720)], (10, 14, 30))
    for x, y in ((700, 668), (770, 690), (890, 662), (960, 650)): c.rect((x, y, x + 8, y + 8), (255, 214, 120))
    return im
def room():
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); c = Cv(im)
    for y in range(0, 1330, 6): c.rect((0, y, W, y + 6), mix((238, 222, 192), (222, 200, 168), y / 1330))
    c.rect((0, 1300, W, 1330), (176, 134, 96)); c.rect((0, 1330, W, H), (214, 160, 102))
    for x in range(-200, W + 300, 150): c.line([(x, 1330), (x - 260, H)], (176, 120, 72), 4, caps=False)
    for y in (1480, 1650, 1800): c.line([(0, y), (W, y)], (176, 120, 72), 3, caps=False)
    c.poly([(150, 1580), (930, 1580), (1010, 1780), (60, 1780)], (122, 148, 200)); c.poly([(190, 1610), (890, 1610), (950, 1750), (120, 1750)], (140, 166, 214))
    ImageDraw.Draw(im).rectangle((WIN[0] * S, WIN[1] * S, WIN[2] * S, WIN[3] * S), fill=(0, 0, 0, 0))               # окно: дыра под небо
    c.rect((WIN[0] - 16, WIN[1] - 16, WIN[2] + 16, WIN[1]), (150, 100, 60)); c.rect((WIN[0] - 16, WIN[3], WIN[2] + 16, WIN[3] + 22), (150, 100, 60))
    c.rect((WIN[0] - 16, WIN[1], WIN[0], WIN[3]), (150, 100, 60)); c.rect((WIN[2], WIN[1], WIN[2] + 16, WIN[3]), (150, 100, 60))
    c.rect(((WIN[0] + WIN[2]) / 2 - 7, WIN[1], (WIN[0] + WIN[2]) / 2 + 7, WIN[3]), (150, 100, 60)); c.rect((WIN[0], 440, WIN[2], 454), (150, 100, 60))
    for x0, x1 in ((580, 700), (950, 1070)):
        c.poly([(x0, 130), (x1, 130), (x1 - 10, 800), (x0 + 10, 800)], (84, 112, 176))
        for k in range(1, 5): c.line([(x0 + (x1 - x0) * k / 5, 130), (x0 + (x1 - x0) * k / 5 - 4, 800)], (62, 88, 150), 5, caps=False)
    c.rect((560, 112, 1090, 134), (140, 96, 56))
    c.rect((80, 330, 340, 610), (192, 134, 72)); c.rect((98, 348, 322, 592), (244, 232, 204))                       # картина с кактусом
    c.poly([(170, 560), (250, 560), (240, 520), (180, 520)], (186, 98, 70)); c.rr((208, 420, 232, 524), 12, (86, 160, 96)); c.rr((178, 450, 202, 500), 12, (86, 160, 96)); c.rr((238, 460, 262, 506), 12, (86, 160, 96)); c.rect((178, 480, 232, 494), (86, 160, 96))
    # кровать
    c.rr((36, 840, 210, 1300), 60, (176, 98, 52), INK, 6); c.rr((56, 880, 190, 1280), 46, (196, 116, 64)); c.ell((124, 838), 28, 28, (214, 140, 74), INK, 5)
    c.rr((950, 1000, 1046, 1300), 30, (176, 98, 52), INK, 6); c.ell((998, 996), 24, 24, (214, 140, 74), INK, 5)
    c.rect((60, 1170, 1030, 1300), (176, 98, 52)); c.rect((60, 1170, 1030, 1184), (214, 140, 74)); c.line([(60, 1300), (1030, 1300)], INK, 6, caps=False)
    for x in (80, 990): c.rect((x, 1300, x + 36, 1390), (150, 80, 42))
    c.rr((150, 1070, 990, 1180), 28, (90, 126, 200), INK, 6); c.line([(170, 1100), (970, 1100)], (118, 152, 222), 6, caps=False)
    c.ell((330, 1050), 160, 58, (150, 196, 210), INK, 6); c.line([(220, 1050), (260, 1030)], (120, 168, 186), 5, caps=False)
    return im
def beam():
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); c = Cv(im)
    c.poly([(640, 720), (1010, 720), (780, 1330), (260, 1330)], (255, 240, 190, 46))
    return im.filter(ImageFilter.GaussianBlur(14 * S))

# ---------------- расписание (ритм по ревизии Avzaldoc: циклы сжимаются 1,6 → 1,0 с)
STEPS = [1.6, 1.4, 1.2, 1.0, 1.5]; T0 = 3.4; LABELS = ["6:45", "7:00", "7:15", "7:30", "7:45"]
def tk(k): return T0 + sum(STEPS[:k])
def cyc_len(k): return STEPS[k]
END_CYC = tk(4) + STEPS[4]                                   # 10,1
def hits(k):
    if k == 4: return [(tk(4) + 0.78, -42.0), (tk(4) + 1.12, 0.0)]            # первый удар мимо
    return [(tk(k) + 0.85 * STEPS[k] / 1.4 * 0.0 + min(0.9, STEPS[k] - 0.38), 0.0)]
def slap_t(k): return hits(k)[-1][0]
RING = [(tk(k) + 0.1, min(tk(k) + 0.8, slap_t(k) - 0.02) if k < 4 else slap_t(4) - 0.02) for k in range(5)]
ARM_S = (452, 1050); PH_POS = (250, 1122); HOLD = (470, 915); WIN = (640, 180, 1010, 720)
T_SLEEP = 10.7; T_BUB = 13.3; T_WAKE = 13.7; T_GRAB = 14.2; T_SHOCK = 14.8; T_CROUCH = 15.6; T_JUMP = 16.0; T_LAND = 17.6; T_LOOP = 19.4
BASE_Z, BASE_C = 1.25, (560, 1050)

def tint_at(t):
    if t < 1.2: return 0.0
    if t < 2.2: return 0.62
    if t < 2.8: return lerp(0.62, 1.0, seg(t, 2.2, 2.8))
    if t < 3.2: return 1.0
    if t < 3.6: return lerp(1.0, 0.0, seg(t, 3.2, 3.6))
    if 10.1 <= t < 10.3: return lerp(0.0, 0.95, seg(t, 10.1, 10.3))
    if 10.3 <= t < 10.7: return 0.95
    if 10.7 <= t < 11.1: return lerp(0.95, 0.0, seg(t, 10.7, 11.1))
    d = 0.0
    for k in range(1, 5): d = max(d, 0.75 * max(0.0, 1 - abs(t - (tk(k) - 0.12)) / 0.2))
    return d
def sky_k(t): return 0.0 if t < 3.0 else 1.0
def hand_state(t):
    """(hand_pos | None, strike_u) — замах, удар, возврат."""
    for k in range(5):
        for (h, off) in hits(k):
            tgt = (PH_POS[0] + 30 + off, PH_POS[1] - 10); back = (ARM_S[0] - 14, ARM_S[1] - 26)
            if h - 0.26 <= t < h - 0.14: return lerp2(ARM_S, back, seg(t, h - 0.26, h - 0.14)), 0.0
            if h - 0.14 <= t < h: u = (t - (h - 0.14)) / 0.14; return lerp2(back, tgt, u * u), 0.0
            if h <= t < h + 0.3:
                u = (t - h) / 0.3; ob = 1 + 1.7 * (u - 1) ** 3 + 2.7 * (u - 1) ** 2 if False else ease(u)
                return lerp2(tgt, ARM_S, ob), 1 - u
    if T_GRAB <= t < T_GRAB + 0.3: return lerp2(ARM_S, PH_POS, seg(t, T_GRAB, T_GRAB + 0.3)), 0.0
    if T_GRAB + 0.3 <= t < T_JUMP: return lerp2(PH_POS, HOLD, seg(t, T_GRAB + 0.3, T_GRAB + 0.62)), 0.0
    return None, 0.0
def last_hit(t):
    best = None
    for k in range(5):
        for (h, off) in hits(k):
            if h <= t < h + 0.6: best = (t - h, off)
    return best
def ringing(t, k): a, b = RING[k]; return a <= t <= b
def eyes_state(t):
    if t < 1.2: return "closed"
    if t < 1.9: return "half"
    if t < 2.2: return "half" if (t - 1.9) / 0.3 < 0.5 else "closed"
    for k in range(5):
        a, b = RING[k]; s = slap_t(k)
        if k == 4 and tk(4) + 0.4 <= t < s: return "half"
        if a <= t < s: return "squint"
    if T_WAKE <= t < T_WAKE + 0.5: return "half"
    if T_WAKE + 0.5 <= t < T_SHOCK: return "open"
    if T_SHOCK <= t < T_JUMP + 0.6: return "wide"
    return "closed"
def zoom_at(t):
    z, c = BASE_Z, BASE_C
    if 1.2 <= t < 2.8: z = lerp(1.25, 1.4, seg(t, 1.2, 2.8)); c = lerp2(BASE_C, (420, 1020), seg(t, 1.2, 2.8))
    for k in range(5):
        a, L = tk(k), STEPS[k]; s = slap_t(k)
        if not (a <= t < a + L): continue
        zA = [1.25, 1.3, 1.35, 1.5, 1.7][k]; zc = (520, 1040)
        b0 = s - 0.3 if k < 4 else tk(4) + 0.6
        if k == 4 and tk(4) + 0.4 <= t < tk(4) + 0.6: return 1.8, (330, 980)
        if b0 <= t < s + 0.25: return 2.0, (300, 1090)
        if t >= s + 0.25: return 1.8, (330, 980)
        return zA, zc
    if T_SLEEP <= t < T_WAKE: return lerp(1.5, 1.75, seg(t, T_SLEEP, T_WAKE)), (400, 1000)
    if T_WAKE <= t < T_SHOCK: return lerp(1.75, 1.4, seg(t, T_WAKE, T_SHOCK - 0.3)), (400, 1000)
    if T_SHOCK <= t < T_JUMP: return lerp(1.4, 1.9, seg(t, T_SHOCK, T_SHOCK + 0.12)), (400, 980)
    if T_JUMP <= t < T_JUMP + 0.7: return lerp(1.9, 1.25, seg(t, T_JUMP, T_JUMP + 0.7)), lerp2((400, 980), BASE_C, seg(t, T_JUMP, T_JUMP + 0.7))
    if t >= 18.7: u = seg(t, 18.7, T_LOOP); return lerp(1.25, 2.2, u), lerp2(BASE_C, (260, 1110), u)
    return z, c
def label_at(t):
    for k in range(5):
        if tk(k) <= t < tk(k) + STEPS[k]: return LABELS[k], t - tk(k)
    if T_SHOCK <= t < T_JUMP: return "8:59", t - T_SHOCK
    return None, 0

# ---------------- персонаж
def face(c, ctr, r, st, mouth, look=(0, 0), tt=0.0, sx=1.0, sy=1.0, skin=SKIN, sweat=0.0):
    x, y = ctr; rx, ry = r * sx, r * sy
    c.ell(ctr, rx, ry, skin, INK, 7)
    if skin != SKIN: c.ell((x - 40 * sx, y + 38 * sy), 22, 14, (255, 190, 170, 90))
    for k_ in (-1, 1):
        ex, ey = x + k_ * 38 * sx, y - 8 * sy
        if st == "closed": c.arc((ex, ey - 6), 20 * sx, 14 * sy, 20, 160, INK, 6)
        elif st == "squint": c.line([(ex - k_ * 18, ey - 12), (ex + k_ * 14, ey + 2), (ex - k_ * 18, ey + 12)], INK, 6)
        elif st == "half":
            c.ell((ex, ey), 22, 19, WHITE, INK, 4); c.ell((ex + look[0], ey + 4 + look[1]), 8, 8, INK); c.poly([(ex - 26, ey - 24), (ex + 26, ey - 24), (ex + 26, ey - 4), (ex - 26, ey - 4)], skin); c.line([(ex - 24, ey - 4), (ex + 24, ey - 4)], INK, 6)
        elif st == "open": c.ell((ex, ey), 24, 27, WHITE, INK, 4); c.ell((ex + look[0], ey + look[1]), 9, 9, INK)
        elif st == "wide": c.ell((ex, ey - 2), 32, 36, WHITE, INK, 4); c.ell((ex + look[0] * 0.3, ey - 2), 3.5, 3.5, INK)
    if st == "squint": [c.line([(x + k_ * 58 * sx, y - 36 * sy), (x + k_ * 20 * sx, y - 24 * sy)], INK, 7) for k_ in (-1, 1)]
    if st == "half": [c.line([(x + k_ * 58 * sx, y - 36 * sy - 6 * (k_ < 0)), (x + k_ * 20 * sx, y - 30 * sy)], INK, 6) for k_ in (-1, 1)]
    if st == "wide": [c.line([(x + k_ * 60 * sx, y - 54 * sy), (x + k_ * 20 * sx, y - 58 * sy)], INK, 7) for k_ in (-1, 1)]
    if mouth == "flat": c.line([(x - 22, y + 46 * sy), (x + 22, y + 46 * sy)], INK, 6)
    elif mouth == "frown": c.arc((x, y + 58 * sy), 26, 16, 200, 340, INK, 6)
    elif mouth == "o": rr = 14 + 8 * math.sin(tt * 5.2) ** 2; c.ell((x, y + 50 * sy), rr, rr + 6, (60, 24, 40), INK, 5)
    elif mouth == "big": c.ell((x, y + 56 * sy), 26, 34, (60, 24, 40), INK, 6); c.ell((x, y + 70 * sy), 16, 10, (214, 90, 100))
    if sweat > 0:
        for i, (dx, dy) in enumerate(((-r * 1.02, -30), (r * 1.0, -6), (-r * 0.9, 40))):
            p = (tt * 1.7 + i / 3) % 1; c.ell((x + dx, y + dy + 30 * p), 8, 13, (150, 210, 255, int(230 * sweat * (1 - p * 0.6))), INK, 3)
def phone_poly(ctr, w, h, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(ctr[0] + dx * ca - dy * sa, ctr[1] + dx * sa + dy * ca) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
def blanket_pts(t, wob=0.0, u_hit=None, sy=1.0):
    up = [(404, 1060)]
    for i in range(0, 25):
        x = 404 + i * 25.0; y = 1010 + 14 * math.sin(i * 0.5 + wob + t * 1.6) - 40 * math.sin(math.pi * min(i / 24, 1)) ** 0.5 + (28 if i > 20 else 0)
        y = 1040 + (y - 1010) * 0.9 - 14 * (i > 3)
        if u_hit is not None: y += 22 * math.exp(-u_hit / 0.22) * math.sin(i * 0.55 - u_hit * 18)
        up.append((x, 1180 - (1180 - y) * sy))
    up += [(1010, 1180), (404, 1180)]
    return up

def draw(t, cover=False):
    st = statics()
    img = Image.blend(st["night"], st["day"], sky_k(t)).convert("RGBA"); img.alpha_composite(st["room"]); c = Cv(img)
    tint = tint_at(t); jump = t >= T_JUMP + 0.0
    ring_k = next((k for k in range(5) if ringing(t, k)), None)
    # луч с пылью, рассвет
    if sky_k(t) > 0 and tint < 0.5:
        dx = 42 * min(max((t - T0) / 1.4, 0), 5) * S
        lb = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); lb.alpha_composite(st["beam"], (int(dx), 0)) if dx > 0 else lb.alpha_composite(st["beam"]); img.alpha_composite(lb)
        for i, (fx, fy, ph_) in enumerate(st["dust"]):
            x_ = 640 + fx * 370 * (1 - fy * 0.55) + 260 * fy + dx / S + 8 * t; y_ = 720 + fy * 600 - 5 * t % 40
            al = int((70 + 70 * math.sin(t * 3 + ph_)) * (0.6 + 0.4 * math.sin(t * 3 + i)) if True else 100); c.ell((x_, y_), 3.5, 3.5, (255, 248, 210, max(al, 30)))
    if 3.4 <= t < 4.6: img.alpha_composite(Image.new("RGBA", (CW, CH), (255, 170, 90, int(46 * (1 - seg(t, 3.4, 4.6))))))
    if tint < 0.5 and t > 4.6: img.alpha_composite(Image.new("RGBA", (CW, CH), (255, 250, 220, int(22 * min((t - 4.6) / 4.0, 1)))))
    if t >= T_JUMP + 0.3: c.ell((330, 1052), 90, 26, (120, 168, 186), None)
    ph_c = PH_POS; ph_ang = 0.12; ph_lit = 0.0; shake = 0.0; ph_sx, ph_sy = 1.0, 1.0
    if ring_k is not None:
        u = t - RING[ring_k][0]; shake = math.sin(u * 90) * 5; ph_lit = 0.55 + 0.45 * (math.sin(u * 26) > 0)
    lh = last_hit(t); head_sx, head_sy, head_dy = 1.0, 1.0, 0.0
    if lh is not None:
        u, off = lh
        if off == 0:
            hop = 46 * math.sin(min(u / 0.45, 1) * math.pi) * math.exp(-u * 2); ph_c = (PH_POS[0] + 40 * min(u * 6, 1), PH_POS[1] - hop); ph_ang = 0.12 + 1.4 * min(u / 0.45, 1) * (1 + 0.4 * math.sin(u * 30))
            if u < 0.1: ph_sx, ph_sy = 1.18, 0.78
        if u < 0.1: head_sx, head_sy, head_dy = 1.04, 0.94, 6
        elif u < 0.25: head_sx, head_sy = 0.97, 1.04
    if 1.2 <= t < 2.2: ph_lit = 0.5
    hand, strike_u = hand_state(t)
    es = eyes_state(t); hold = T_GRAB + 0.3 <= t < T_JUMP
    if not jump:
        bob = 3 * math.sin(t * 2.2) if (t >= 2.2 and not hold and es == "closed") else 0
        head = (320, 962 + bob + head_dy)
        if t >= T_SHOCK: head = (head[0] + 4 * math.sin(t * 60), head[1] + 4 * math.cos(t * 55))
        if T_CROUCH <= t < T_JUMP: head = (head[0], head[1] + 34 * ease((t - T_CROUCH) / 0.3)); head_sx, head_sy = 1 + 0.12 * ease((t - T_CROUCH) / 0.3), 1 - 0.14 * ease((t - T_CROUCH) / 0.3)
        if tk(4) + 0.35 <= t < tk(4) + 1.13:                                                                             # 7:45: приподнимается и падает
            u = t - (tk(4) + 0.35); up = 70 * (ease(u / 0.3) if u < 0.3 else (1 if u < 0.6 else 1 - ((u - 0.6) / 0.18) ** 2)); head = (head[0], head[1] - max(up, 0))
        if hand is not None:
            mid = lerp2(ARM_S, hand, 0.5); mid = (mid[0], mid[1] - 36)
            c.line([ARM_S, mid, hand], INK, 20); c.ell(hand, 22, 22, SKIN, INK, 6)
        if not hold:
            pc = (ph_c[0] + shake, ph_c[1]); lit = (200, 226, 255)
            c.poly(phone_poly(pc, 104 * ph_sx, 58 * ph_sy, ph_ang), (28, 30, 44), INK, 4)
            c.poly(phone_poly(pc, 92 * ph_sx, 46 * ph_sy, ph_ang), tuple(int(v * (0.35 + 0.65 * ph_lit)) for v in lit) if ph_lit > 0 else (44, 50, 72))
            if ph_lit > 0: glow(img, pc, 150, (190, 220, 255), 0.55 * ph_lit)
            if ring_k is not None:
                for i in range(3):
                    p = ((t * 2.2 + i / 3) % 1); c.ell((pc[0], pc[1] - 8), 70 + 120 * p, 36 + 70 * p, None, (255, 255, 255, int(190 * (1 - p))), 4)
        mouth = "frown" if es in ("squint", "half") else ("big" if es == "wide" else ("o" if (T_SLEEP + 0.2 <= t < T_WAKE) else "flat"))
        look = (-10, 8) if (es == "half" and t < 3.0) else ((6, -4) if es == "open" else (-6, 6))
        pale = t >= T_SHOCK
        face(c, head, 100, es, mouth, look, t, head_sx, head_sy, skin=((255, 246, 226) if pale else SKIN), sweat=(1.0 if pale else 0.0))
        c.line([(412, 1062), (440, 1052)], INK, 18, caps=True)
        if T_SLEEP + 0.2 <= t < T_BUB + 0.12 and es == "closed":                                                         # пузырь из носа
            r_ = 8 + 30 * seg(t, T_SLEEP + 0.2, T_BUB) + 3 * math.sin(t * 5.2)
            if t < T_BUB: c.ell((head[0] + 14, head[1] + 28 + r_ * 0.6), r_, r_, (200, 232, 255, 120), (150, 190, 230, 255), 3); c.ell((head[0] + 14 - r_ * 0.3, head[1] + 28 + r_ * 0.3), r_ * 0.2, r_ * 0.2, (255, 255, 255, 200))
            else:
                for i in range(6): a_ = i * math.pi / 3; q = (t - T_BUB) / 0.12; c.line([(head[0] + 14 + 36 * math.cos(a_), head[1] + 60 + 36 * math.sin(a_)), (head[0] + 14 + (36 + 30 * q) * math.cos(a_), head[1] + 60 + (36 + 30 * q) * math.sin(a_))], (255, 255, 255, 230), 5)
        if hold:
            hp = hand if hand else HOLD; pp = (hp[0] + 20, hp[1] - 30)
            c.poly(phone_poly(pp, 150, 250, 0.35), (28, 30, 44), INK, 5); c.poly(phone_poly(pp, 128, 224, 0.35), (216, 232, 255)); glow(img, pp, 200, (190, 220, 255), 0.5)
            c.text(pp, "8:59" if t >= T_SHOCK else "9:03", 52, (28, 32, 56), 0)
    # одеяло
    ob = 0.0; rot = 0.0; oy = 0.0; ox = 0.0; sy_b = 1.0; lift = 0.0
    if jump:
        tau = min(max((t - (T_JUMP + 0.1)) / 1.5, 0.0), 1.0)
        oy = -1400 * math.sin(math.pi * tau) * (1 + 0.12 * math.sin(3.5 * math.pi * tau) * (1 - tau)); ox = 260 * math.sin(math.pi * tau) * (1 - tau); rot = 0.5 * math.sin(math.pi * 2 * tau) * (1 - tau)
        u2 = t - T_LAND
        if 0 <= u2 < 0.12: sy_b = 1 - 0.18 * (1 - u2 / 0.12)
        elif 0.12 <= u2 < 0.42: lift = 18 * math.sin(math.pi * (u2 - 0.12) / 0.3)
    uh = lh[0] if lh else None
    bp = blanket_pts(t, wob=(0.6 * math.sin(t * 5) if (jump and t < T_LAND) else 0.0) + 0.0, u_hit=(uh if uh is not None and not jump else None), sy=sy_b)
    if ring_k is not None and not jump: bp = [(x, y + (2.5 * math.sin(t * 90) if y < 1100 else 0)) for x, y in bp]
    cx0, cy0 = 700, 1100
    bp = [(cx0 + (x - cx0) * math.cos(rot) - (y - cy0) * math.sin(rot) + ox, cy0 + (x - cx0) * math.sin(rot) + (y - cy0) * math.cos(rot) + oy - lift) for x, y in bp]
    if not jump and es == "closed" and t > 2.2: amp = 5 if (T_SLEEP <= t < T_WAKE) else 1.5; bp = [(x, y + (amp * math.sin(t * 2.2) if y < 1100 else 0)) for x, y in bp]
    c.poly(bp, (206, 104, 96), INK, 6)
    if not jump:
        for i in range(1, 6): xx = 480 + i * 90; c.line([(xx, 1060 - 10 * math.sin(i)), (xx + 20, 1160)], (170, 76, 76), 5, caps=False)
    # прыжок: летящий человечек (+ приседание уже выше)
    if T_JUMP <= t < T_JUMP + 0.55:
        u = (t - T_JUMP) / 0.55
        def pos(uu): return (320 - 640 * uu, 962 - 34 + 34 * min(uu * 6, 1) - 1500 * max(uu, 0) ** 1.35)
        hx, hy = pos(u); dv = (pos(u + 0.02)[0] - hx, pos(u + 0.02)[1] - hy); n = math.hypot(*dv) or 1; dv = (dv[0] / n, dv[1] / n)
        for gi, (du, al) in enumerate(((0.055, 45), (0.03, 90))):
            gx, gy = pos(max(u - du, 0)); c.ell((gx, gy), 100, 100, SKIN + (al,), None)
        for i in range(5): off = 60 + i * 60; c.line([(hx - dv[0] * off, hy - dv[1] * off), (hx - dv[0] * (off + 220), hy - dv[1] * (off + 220))], (30, 28, 40, 200), 5)
        tail = (hx - dv[0] * 230, hy - dv[1] * 230); c.line([(hx, hy), tail], INK, 14)
        c.line([(hx - dv[0] * 90 + dv[1] * 10, hy - dv[1] * 90 - dv[0] * 10), (hx - dv[0] * 150 + 110, hy - dv[1] * 150 - 40)], INK, 12); c.line([(hx - dv[0] * 90, hy - dv[1] * 90), (hx - dv[0] * 150 - 110, hy - dv[1] * 150 + 30)], INK, 12)
        c.line([tail, (tail[0] - dv[0] * 90 + 60, tail[1] - dv[1] * 90)], INK, 12); c.line([tail, (tail[0] - dv[0] * 90 - 60, tail[1] - dv[1] * 90)], INK, 12)
        face(c, (hx, hy), 100, "wide", "big", (0, 0), t, 0.88, 1.18, skin=(255, 246, 226))
    # телефон упал на кровать, тапочки, перья, пыль при посадке
    if jump:
        c.poly(phone_poly((250, 1122), 104, 58, 0.12 + 0.5 * (t > T_JUMP + 0.3)), (28, 30, 44), INK, 4)
        for i in range(3):
            p = seg(t, T_JUMP + 0.2 + 0.1 * i, T_LAND - 0.1 + 0.1 * i)
            if 0 < p < 1: c.ell((300 + 40 * i + 30 * math.sin(p * 9 + i), 760 + 340 * p), 5, 12, (255, 255, 255, int(255 * (1 - p * 0.3))))
        if T_LAND <= t < T_LAND + 0.5:
            q = (t - T_LAND) / 0.5
            for i in range(10): a_ = i * 0.628; c.ell((700 + (60 + 120 * q) * math.cos(a_) * 1.3, 1190 + 30 * math.sin(a_) * q), 14 + 16 * q, 14 + 16 * q, (190, 180, 170, int(80 * (1 - q))))
    c.ell((420, 1470), 36, 17, (150, 86, 60)); c.ell((520, 1470), 36, 17, (150, 86, 60))
    # Z над спящим
    if not jump and es == "closed" and (2.2 <= t < 2.8 or T_SLEEP + 0.2 <= t < T_BUB or any(slap_t(k) + 0.3 <= t < tk(k) + STEPS[k] for k in range(5))):
        for i in range(3):
            p = ((t * 0.9 + i / 3) % 1); c.text((420 + 40 * p + 20 * i, 850 - 190 * p), "Z", int(34 + 20 * p), (255, 255, 255, int(235 * (1 - p))), 2)
    for k in range(5):
        for (h, off) in hits(k):
            if abs(t - h) < 0.1 and off == 0:
                u = 1 - abs(t - h) / 0.1
                for i in range(8): a = i * math.pi / 4; c.line([(PH_POS[0] + 60 * math.cos(a), PH_POS[1] - 8 + 36 * math.sin(a)), (PH_POS[0] + (60 + 60 * u) * math.cos(a), PH_POS[1] - 8 + (36 + 40 * u) * math.sin(a))], (255, 255, 255, 230), 6)
    if tint > 0.01: img.alpha_composite(Image.new("RGBA", (CW, CH), (8, 12, 40, int(255 * min(tint, 1)))))
    if 1.2 <= t < 2.2: glow(img, (310, 1010), 260, (150, 190, 255), 0.35)
    lab, lu = label_at(t)
    if lab and tint < 0.9:
        sc = 1 + 0.4 * (1 - ease(lu / 0.16)) if lu < 0.16 else 1.0
        if lab == "8:59": sc *= 1.25
        col = (255, 64, 56, 255) if lab == "8:59" else (255, 255, 255, 255)
        Cv(img).text((330, 760 if lab != "8:59" else 700), lab, int(88 * sc), col, stroke=7)
    z, zc_ = zoom_at(t)
    if cover: z, zc_ = 1.75, (400, 990)
    bx0 = (zc_[0] - W / (2 * z)) * S; by0 = (zc_[1] - H / (2 * z)) * S
    bx0 = min(max(bx0, 0), CW - W * S / z); by0 = min(max(by0, 0), CH - H * S / z)
    img = img.crop((int(bx0), int(by0), int(bx0 + W * S / z), int(by0 + H * S / z)))
    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.asarray(out, dtype=np.float32) * vignette(0.62 if cover else 0.82)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
_vig = {}
def vignette(k):
    if k not in _vig:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _vig[k] = np.clip(1 - (1 - k) * np.clip(d - 0.55, 0, 1) ** 1.4 * 1.6, 0, 1)
    return _vig[k]
def statics():
    if not _cache:
        _cache.update(day=sky_day(), night=sky_night(), room=room(), beam=beam())
        rng = np.random.default_rng(3); _cache["dust"] = [(rng.uniform(), rng.uniform(), rng.uniform(0, 6)) for _ in range(36)]
    return _cache

# ---------------- крупный телефон: 0–1,2 с (4 будильника) и финал 19,4–20 с (петля, пятый «09:00»)
def phone_scene(t, end=False):
    im = Image.new("RGB", (CW, CH), (0, 0, 0)); c = Cv(im)
    for y in range(0, H, 8): c.rect((0, y, W, y + 8), mix((40, 44, 72), (22, 24, 40), y / H))
    sh = (3 * math.sin(t * 9), 2 * math.cos(t * 7)); ox, oy = sh
    c.rr((250 + ox, 300 + oy, 830 + ox, 1560 + oy), 80, (14, 16, 26), (86, 92, 130), 8); c.rr((276 + ox, 330 + oy, 804 + ox, 1530 + oy), 56, (22, 26, 42))
    bx, by = 340 + ox, 420 + oy; c.ell((bx, by + 4), 20, 22, (240, 244, 255)); c.poly([(bx - 28, by + 22), (bx + 28, by + 22), (bx + 20, by + 12), (bx - 20, by + 12)], (240, 244, 255)); c.ell((bx, by + 30), 7, 7, (240, 244, 255))
    c.ell((740 + ox, 420 + oy), 30, 30, (60, 140, 255)); c.line([(740 + ox, 404 + oy), (740 + ox, 436 + oy)], WHITE, 6); c.line([(724 + ox, 420 + oy), (756 + ox, 420 + oy)], WHITE, 6)
    times = ["05:30", "06:00", "06:30", "07:00"] + (["09:00"] if end else []); n = len(times); gap = 175 if end else 220
    ons = [0.0, 0.25, 0.5, 0.75] if not end else [-1, -1, -1, -1, 0.35]
    for i, tm in enumerate(times):
        y = 590 + i * gap - (20 if end else 0); c.rr((306 + ox, y - 80 + oy, 774 + ox, y + 80 + oy), 34, (32, 38, 60)); c.text((350 + ox, y - 14 + oy), tm, 76, (250, 252, 255), anchor="lm", w="Bold")
        for d_ in range(5): c.ell((356 + ox + d_ * 26, y + 48 + oy), 6, 6, (120, 134, 176))
        k = 1.0 if ons[i] < 0 else seg(t, ons[i], ons[i] + 0.12); col = mix((80, 86, 110), (60, 150, 255), k); tx0 = 650 + ox
        c.rr((tx0, y - 30 + oy, tx0 + 100, y + 26 + oy), 28, col); c.ell((tx0 + 28 + 44 * k, y - 2 + oy), 22, 22, WHITE)
    ti = min(int(t / 0.25), 3) if not end else n - 1; ty = 590 + ti * gap - (20 if end else 0); tp = (690 + ox + 20 * math.sin(t * 3), ty + 10 + oy)
    ph_ = (t % 0.25) if not end else (t - 0.3)
    tip = (tp[0] + 14 * (1 if 0 <= ph_ < 0.1 else 0), tp[1] + 10); base_ = (420, 1760)
    for i in range(0, 21):
        k = i / 20; pc = (lerp(base_[0], tip[0], k) - 30 * math.sin(k * math.pi), lerp(base_[1], tip[1], k)); rr_ = lerp(70, 44, k); c.ell(pc, rr_ + 6, rr_ + 6, INK)
    for i in range(0, 21):
        k = i / 20; pc = (lerp(base_[0], tip[0], k) - 30 * math.sin(k * math.pi), lerp(base_[1], tip[1], k)); rr_ = lerp(70, 44, k); c.ell(pc, rr_, rr_, SKIN)
    c.poly([(120, 1560), (460, 1600), (560, 1920), (90, 1920)], SKIN, INK, 7)
    for i in range(4): c.rr((150, 1230 + i * 78, 290, 1296 + i * 78), 30, SKIN, INK, 6)
    return im.resize((W, H), Image.LANCZOS)

def frame_at(t, cover=False):
    if t < 1.2: return phone_scene(t)
    if t >= T_LOOP: return phone_scene(t - T_LOOP, end=True)
    return draw(t, cover)

# ---------------- звук
SR = 44100
def build_audio():
    n = int(DUR * SR); a = np.zeros(n, np.float32); rng = np.random.default_rng(11)
    def add(t0, x, g=1.0):
        i = int(t0 * SR); j = min(i + len(x), n)
        if i < n and j > i: a[i:j] += x[:j - i] * g
    def env(nn, att=0.005, dec=0.1): t = np.arange(nn) / SR; return np.minimum(t / att, 1) * np.exp(-t / dec)
    def tone(f, d, g=0.3, dec=None):
        t = np.arange(int(d * SR)) / SR; x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 3 * f * t); return g * x * env(len(t), 0.003, dec or d / 3)
    def noise(d, g=0.3, dec=None): x = rng.standard_normal(int(d * SR)).astype(np.float32); return g * x * env(len(x), 0.002, dec or d / 3)
    def lp(x, k=0.2):
        y = np.zeros_like(x); s_ = 0.0
        for i in range(len(x)): s_ += k * (x[i] - s_); y[i] = s_
        return y
    def whoosh(t0, d=0.35, g=0.5): add(t0, lp(noise(d, 1, d / 2), 0.08) * np.hanning(int(d * SR)), g)
    def sweep(f0, f1, d, g, dec=None):
        t = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * t / d; return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.005, dec or d / 2) * g).astype(np.float32)
    for tt_ in (0.0, 0.25, 0.5, 0.75): add(tt_ + 0.02, tone(1800, 0.03, 0.4, 0.01))
    for ph in (1.3, 1.7, 2.1): add(ph, tone(720, 0.05, 0.12, 0.02))
    for k0 in (1.4, 1.7, 2.0, 2.3, 2.55):
        for j in range(4): add(k0 + j * 0.045, tone(4300, 0.03, 0.035, 0.015))
    for tt_ in (2.6, 3.3, tk(1) - 0.2, tk(2) - 0.2, tk(3) - 0.2, tk(4) - 0.2, 10.1, 10.6): whoosh(tt_, 0.35, 0.45)
    for k in range(5):
        a0, b0 = RING[k]; nb = 3 if k < 3 else 4; f = 1000 + 90 * k
        t_ = np.arange(int((b0 - a0 + 0.05) * SR)) / SR; vib = np.sign(np.sin(2 * np.pi * 22 * t_)) * 0.5 + 0.5; add(a0, (np.sin(2 * np.pi * 110 * t_) * vib * 0.22).astype(np.float32))
        for j in range(nb):
            add(a0 + j * 0.2, tone(f, 0.12, 0.3, 0.09)); add(a0 + j * 0.2 + 0.01, tone(f * 1.5, 0.1, 0.1, 0.07))
        for (h, off) in hits(k):
            add(h - 0.14, lp(noise(0.14, 0.5, 0.06), 0.35))
            if off == 0: add(h, noise(0.07, 0.8, 0.02)); add(h, tone(95, 0.25, 0.7, 0.07)); add(h + 0.02, tone(260, 0.1, 0.25, 0.04)); add(h + 0.05, lp(noise(0.3, 1, 0.15), 0.1), 0.12)
            else: add(h, lp(noise(0.12, 1, 0.05), 0.15), 0.55); add(h, tone(70, 0.2, 0.4, 0.05))
    add(tk(4) + 0.35, sweep(180, 300, 0.2, 0.18)); add(tk(4) + 1.0, sweep(300, 150, 0.18, 0.18))                          # пружины кровати
    for tt_ in (3.6, 4.5, 6.2, 8.1, 9.2, 11.0, 11.8, 12.5, 14.0):
        for j in range(3):
            f0 = 2600 + 400 * j; x = np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f0 + 700, int(0.09 * SR))) / SR) * env(int(0.09 * SR), 0.01, 0.05)
            add(tt_ + j * 0.12, x.astype(np.float32), 0.09)
    for i, tt_ in enumerate((T_SLEEP + 0.3, T_SLEEP + 1.5, T_SLEEP + 2.7)):
        add(tt_, lp(noise(0.5, 0.9, 0.35), 0.06) * np.hanning(int(0.5 * SR)), 0.5); add(tt_ + 0.5, tone(78, 0.45, 0.3, 0.25))
    add(T_BUB, tone(2400, 0.02, 0.4, 0.01)); add(T_WAKE - 0.1, lp(noise(0.3, 1, 0.2), 0.1) * np.hanning(int(0.3 * SR)), 0.4)
    add(T_GRAB, lp(noise(0.3, 1, 0.2), 0.12), 0.25)
    # тишина 0,25 с перед «8:59», потом стинг
    for f, g in ((466, 0.3), (494, 0.3), (932, 0.12)): add(T_SHOCK, tone(f, 0.55, g, 0.35))
    add(T_SHOCK - 0.1, lp(noise(0.28, 1, 0.3), 0.18) * np.linspace(0, 1, int(0.28 * SR)), 0.5)
    add(T_CROUCH, sweep(200, 130, 0.35, 0.2))
    t = np.arange(int(0.55 * SR)) / SR; boing = np.sin(2 * np.pi * np.cumsum(180 + 900 * t / 0.55 + 60 * np.sin(2 * np.pi * 14 * t)) / SR) * np.exp(-t / 0.35) * 0.38
    add(T_JUMP, boing.astype(np.float32)); add(T_JUMP + 0.02, lp(noise(0.55, 1, 0.3), 0.12), 0.7)
    for tt_ in (T_JUMP + 0.9, T_JUMP + 1.2): add(tt_, lp(noise(0.14, 1, 0.07), 0.25), 0.3)
    add(T_LAND, lp(noise(0.2, 1, 0.1), 0.2), 0.6); add(T_LAND, tone(70, 0.3, 0.6, 0.1)); add(T_LAND + 0.15, lp(noise(0.4, 1, 0.2), 0.08), 0.3)
    add(T_LOOP + 0.3, tone(1800, 0.03, 0.4, 0.01))
    for f, g in ((880, 0.1), (1320, 0.07)): add(T_LOOP + 0.45, tone(f, 0.5, g, 0.2))
    pk = np.abs(a).max() or 1; return a / pk * 0.9
def write_wav(path):
    import scipy.io.wavfile as w; a = build_audio(); w.write(path, SR, (np.stack([a, a], 1) * 32767).astype(np.int16))

# ---------------- сборка
_worker_ready = False
def _render(i):
    global _worker_ready
    t = i / FPS
    return frame_at(t).tobytes()

if __name__ == "__main__":
    wd = f"{ROOT}/work/snooze_1"; os.makedirs(wd, exist_ok=True)
    if len(sys.argv) > 1:
        for tt_ in sys.argv[1:]: frame_at(float(tt_)).save(f"{wd}/pv_{tt_}.png")
        sys.exit(0)
    import multiprocessing as mp
    N = int(DUR * FPS); write_wav(f"{wd}/snooze.wav")
    cover = frame_at(15.1, cover=True); cover.save(f"{ROOT}/covers/72_snooze_click.jpg", quality=94)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{wd}/snooze.wav",
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-shortest",
                           f"{wd}/snooze_raw.mp4"], stdin=subprocess.PIPE)
    cb = cover.tobytes()
    with mp.Pool(4) as pool:
        for i, fb in enumerate(pool.imap(_render, range(N), chunksize=4)):
            ff.stdin.write(cb if i < 3 else fb)                                                                                # обложка — первые 3 кадра
    ff.stdin.close(); ff.wait()
    os.makedirs(f"{ROOT}/hq", exist_ok=True); subprocess.run(["cp", f"{wd}/snooze_raw.mp4", f"{ROOT}/hq/snooze_1_hq.mp4"], check=True); print("done")
