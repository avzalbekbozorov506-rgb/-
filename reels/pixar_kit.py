"""Псевдо-3D «под Pixar»: сферическое освещение, контровой свет, блики, большие глаза, эмоции.
Персонажи рисуются в двойном разрешении и уменьшаются — края получаются гладкими."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LIGHT = np.array([-0.55, -0.65, 0.52]); LIGHT = LIGHT / np.linalg.norm(LIGHT)
RIM = np.array([255, 196, 130])

@lru_cache(maxsize=512)
def ball(w, h, color, rim=0.55, spec=0.22, amb=0.64):
    """Эллипс с объёмным освещением: рассеянный свет слева сверху, тёплый контровой свет справа, блик."""
    w, h = max(w, 2), max(h, 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx + 0.5 - w / 2) / (w / 2); ny = (yy + 0.5 - h / 2) / (h / 2); r2 = nx * nx + ny * ny
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    dif = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    col = np.array(color, np.float32)
    lit = (amb + 0.48 * dif)[..., None]
    warm = np.array([1.0, 0.86, 0.8], np.float32)                                # тёплые «подповерхностные» тени, как у кожи в мультфильмах
    rgb = col * lit * (warm + (1 - warm) * np.clip(lit, 0, 1))
    rimk = (np.clip(nx * 0.8 - ny * 0.1, 0, 1) * (1 - nz) ** 2.2 * rim)[..., None]
    rgb = rgb * (1 - rimk) + RIM * rimk
    hx = nx - LIGHT[0] * 0.55; hy = ny - LIGHT[1] * 0.55
    rgb += (np.exp(-(hx * hx + hy * hy) / 0.035) * spec * 255)[..., None]
    a = np.clip((1 - np.sqrt(r2)) * min(w, h) / 2.2, 0, 1) * 255                   # мягкий сглаженный край
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a]).astype(np.uint8), "RGBA")

def put(canvas, sprite, cx, cy, angle=0):
    if angle: sprite = sprite.rotate(angle, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2)))

def shade(c, k): return tuple(int(min(255, max(0, v * k))) for v in c)

def limb(d, p0, p1, w, color):
    """Конечность-цилиндр: тень снизу, основной тон, блик сверху; круглые концы."""
    for off, k, ww in ((w * 0.12, 0.7, w), (0, 1.0, w * 0.82), (-w * 0.16, 1.22, w * 0.32)):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
        ox, oy = -dy / L * off, dx / L * off
        a, b = (p0[0] + ox, p0[1] + oy), (p1[0] + ox, p1[1] + oy); c = shade(color, k)
        d.line((a, b), fill=c, width=int(ww))
        for q in (a, b): d.ellipse((q[0] - ww / 2, q[1] - ww / 2, q[0] + ww / 2, q[1] + ww / 2), fill=c)

def polar(p, ang, L, f):                                                       # угол от вертикали вниз, + вперёд
    a = math.radians(ang); return (p[0] + math.sin(a) * L * f, p[1] + math.cos(a) * L)

def eye(canvas, cx, cy, rx, ry, look=(0, 0), blink=0.0, iris=(96, 62, 34), skin=(240, 190, 150), mood="neutral"):
    d = ImageDraw.Draw(canvas)
    lay = Image.new("RGBA", (int(rx * 2 + 8), int(ry * 2 + 8)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ox, oy = rx + 4, ry + 4
    ld.ellipse((4, 4, 4 + rx * 2, 4 + ry * 2), fill=(250, 248, 244))
    ld.ellipse((4, 4 + ry * 0.9, 4 + rx * 2, 4 + ry * 2.1), fill=(226, 222, 220))  # тень внизу белка
    ld.arc((4, 4, 4 + rx * 2, 4 + ry * 2), 195, 345, fill=(40, 26, 24), width=6)          # линия ресниц сверху
    ir = rx * 0.66; ix, iy = ox + look[0] * rx * 0.35, oy + look[1] * ry * 0.3 + ry * 0.08
    ld.ellipse((ix - ir, iy - ir, ix + ir, iy + ir), fill=shade(iris, 0.7)); ld.ellipse((ix - ir * 0.82, iy - ir * 0.7, ix + ir * 0.82, iy + ir * 0.9), fill=iris)
    pr = ir * (0.62 if mood == "surprised" else 0.5); ld.ellipse((ix - pr, iy - pr, ix + pr, iy + pr), fill=(18, 12, 12))
    ld.ellipse((ix - ir * 0.62, iy - ir * 0.7, ix - ir * 0.1, iy - ir * 0.18), fill=(255, 255, 255))   # большой блик
    ld.ellipse((ix + ir * 0.25, iy + ir * 0.25, ix + ir * 0.5, iy + ir * 0.5), fill=(255, 255, 255, 220))
    m = Image.new("L", lay.size, 0); ImageDraw.Draw(m).ellipse((4, 4, 4 + rx * 2, 4 + ry * 2), fill=255)
    lid = 0.2 if mood == "tired" else (0.35 if mood == "sad" else (0.18 if mood == "angry" else 0.0))
    b = max(blink, lid)
    if b > 0:                                                                  # веко
        lidl = Image.new("RGBA", lay.size, skin + (255,)); lm = Image.new("L", lay.size, 0)
        ImageDraw.Draw(lm).rectangle((0, 0, lay.width, 4 + ry * 2 * b), fill=255)
        lay.paste(lidl, (0, 0), Image.fromarray(np.minimum(np.asarray(lm), np.asarray(m))))
        ImageDraw.Draw(lay).line(((6, 4 + ry * 2 * b), (lay.width - 6, 4 + ry * 2 * b)), fill=(50, 32, 28), width=4)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
    canvas.alpha_composite(lay, (int(cx - ox), int(cy - oy)))

def brow(d, cx, cy, w, side, mood, color):
    tilt = {"angry": -0.55, "sad": 0.5, "surprised": -0.15, "happy": -0.2}.get(mood, 0.0)
    lift = {"surprised": -18, "happy": -8, "sad": -4}.get(mood, 0)
    inner, outer = (cx - side * w * 0.5, cy + lift - tilt * w * 0.35 * -1), (cx + side * w * 0.5, cy + lift)
    if mood == "angry": inner = (cx - side * w * 0.5, cy + 14)
    if mood == "sad": inner = (cx - side * w * 0.5, cy - 14)
    d.line((inner, outer), fill=color, width=int(w * 0.24)); [d.ellipse((p[0] - w * 0.12, p[1] - w * 0.12, p[0] + w * 0.12, p[1] + w * 0.12), fill=color) for p in (inner, outer)]

def mouth(d, cx, cy, w, mood, talk=0.0):
    dark, tongue, teeth = (90, 30, 34), (226, 110, 110), (252, 250, 246)
    if talk > 0.05 or mood == "talk":
        h = w * (0.12 + 0.38 * talk); d.ellipse((cx - w * 0.38, cy - h * 0.3, cx + w * 0.38, cy + h), fill=dark)
        d.ellipse((cx - w * 0.22, cy + h * 0.35, cx + w * 0.22, cy + h * 0.95), fill=tongue)
        d.chord((cx - w * 0.34, cy - h * 0.3, cx + w * 0.34, cy + h * 0.5), 180, 360, fill=teeth)
    elif mood == "happy":
        d.chord((cx - w * 0.5, cy - w * 0.32, cx + w * 0.5, cy + w * 0.42), 0, 180, fill=dark)
        d.chord((cx - w * 0.44, cy - w * 0.28, cx + w * 0.44, cy + w * 0.05), 0, 180, fill=teeth)
        d.ellipse((cx - w * 0.2, cy + w * 0.14, cx + w * 0.2, cy + w * 0.36), fill=tongue)
    elif mood == "angry":
        d.rounded_rectangle((cx - w * 0.4, cy - w * 0.08, cx + w * 0.4, cy + w * 0.16), 10, fill=teeth, outline=dark, width=5)
        d.line(((cx - w * 0.36, cy + w * 0.04), (cx + w * 0.36, cy + w * 0.04)), fill=(200, 190, 186), width=3)
    elif mood == "sad": d.arc((cx - w * 0.32, cy, cx + w * 0.32, cy + w * 0.4), 200, 340, fill=dark, width=7)
    elif mood == "surprised": d.ellipse((cx - w * 0.14, cy - w * 0.06, cx + w * 0.14, cy + w * 0.26), fill=dark)
    else: d.arc((cx - w * 0.3, cy - w * 0.22, cx + w * 0.3, cy + w * 0.16), 20, 160, fill=dark, width=7)

def tool(canvas, hand, ang, kind, f):
    d = ImageDraw.Draw(canvas); tip = hand
    if kind == "hammer":
        tip = polar(hand, ang, 120, f); limb(d, hand, tip, 22, (150, 98, 58))
        hx, hy = tip; a = math.radians(ang); px, py = math.cos(a) * f, -math.sin(a)      # головка перпендикулярно рукоятке
        limb(d, (hx - px * 42, hy - py * 42), (hx + px * 34, hy + py * 34), 40, (150, 156, 168))
    elif kind == "bag":
        put(canvas, ball(150, 170, (176, 140, 96), rim=0.4, spec=0.1), hand[0], hand[1] + 80)
        d.line(((hand[0] - 20, hand[1] + 6), (hand[0] + 20, hand[1] + 6)), fill=(120, 90, 60), width=8)
    elif kind == "pliers":
        tip = polar(hand, ang, 90, f); limb(d, hand, tip, 16, (120, 126, 140))
    return tip

class Character:
    def __init__(self, P): self.P = P
    def render(self, mood="neutral", t=0.0, blink=0.0, look=(0, 0), f=1, arms=((10, 10), (-8, 12)), bounce=0.0, squash=0.0,
               talk=0.0, item=None, item_ang=None, anger=0.0, legs=(0, 0), lean=0.0, head_tilt=0.0, scale=1.0):
        P = self.P; S = 2; Wc, Hc = P["canvas"]
        cv = Image.new("RGBA", (Wc * S, Hc * S), (0, 0, 0, 0)); d = ImageDraw.Draw(cv)
        u = lambda v: v * S
        feet = (u(Wc / 2), u(Hc - 12) - u(bounce)); hip = (feet[0], feet[1] - u(P["leg"]))
        th, tw = u(P["torso_h"]) * (1 - squash), u(P["torso_w"]) * (1 + squash * 0.6)
        tc = (hip[0] + u(lean) * f, hip[1] - th * 0.42); top = tc[1] - th / 2
        sh_y = top + th * 0.16; shoulders = [(tc[0] + u(P["sh"]) * s * f, sh_y) for s in (1, -1)]   # ближнее, дальнее плечо
        skin = P["skin"]
        if anger: skin = tuple(int(lerp_c(skin[i], (232, 92, 72)[i], anger * 0.55)) for i in range(3))
        def arm(i, back):
            a1, a2 = arms[i]; sp = shoulders[i]; el = polar(sp, a1, u(P["arm_up"]), f); hd = polar(el, a1 + a2, u(P["arm_low"]), f)
            col_up = P["sleeve"]; k = 0.8 if back else 1.0
            limb(d, sp, el, u(P["limb"]), shade(col_up, k)); limb(d, el, hd, u(P["limb"]) * 0.9, shade(skin if P.get("short_sleeve") else P["sleeve"], k))
            put(cv, ball(int(u(P["limb"]) * 1.25), int(u(P["limb"]) * 1.25), shade(skin, k), rim=0.4), hd[0], hd[1])
            return hd, a1 + a2
        hb, angb = arm(1, True)                                                 # дальняя рука
        if item and item_ang is not None and len(arms) > 2: pass
        for s, la in ((-1, legs[1]), (1, legs[0])):                             # ноги
            hp = (hip[0] + u(P["hipw"]) * s, hip[1]); kn = polar(hp, la, u(P["leg"]) * 0.55, f); ft = (kn[0], feet[1] - u(10))
            limb(d, hp, kn, u(P["limb"]) * 1.15, P["pants"]); limb(d, kn, ft, u(P["limb"]) * (0.95 if P.get("short_pants") else 1.1), skin if P.get("short_pants") else P["pants"])
            put(cv, ball(int(u(P["limb"]) * 2.3), int(u(P["limb"]) * 1.15), P["shoes"], rim=0.3, spec=0.3), ft[0] + u(8) * f, ft[1])
        put(cv, ball(int(tw), int(th), P["shirt"]), tc[0], tc[1])
        if P.get("short_pants"): put(cv, ball(int(tw * 0.92), int(th * 0.42), P["pants"], spec=0.1), tc[0], tc[1] + th * 0.36)
        hr = u(P["head_r"]); hc = (tc[0] + u(head_tilt * 0.4) * f, top - hr * 0.78)
        put(cv, ball(int(hr * 2), int(hr * 2 * 1.02), skin, rim=0.6, spec=0.18), hc[0], hc[1])
        for s in (1, -1): put(cv, ball(int(hr * 0.34), int(hr * 0.46), shade(skin, 0.92), rim=0.4, spec=0.1), hc[0] + hr * 0.96 * s, hc[1] + hr * 0.08)  # уши
        P["hair_fn"](cv, hc, hr, f)
        ex = hr * 0.38; ey = hc[1] + hr * 0.02; erx, ery = hr * P["eye"], hr * P["eye"] * 1.18; off = hr * 0.07 * f
        for s in (1, -1): eye(cv, hc[0] + ex * s + off, ey, erx, ery, look, blink, P["iris"], skin, mood)
        d = ImageDraw.Draw(cv)
        for s in (1, -1): brow(d, hc[0] + ex * s + off, ey - ery * 1.35, erx * 1.6, s, mood, P["brow"])
        put(cv, ball(int(hr * 0.28), int(hr * 0.24), shade(skin, 1.02), rim=0.2, spec=0.35), hc[0] + off * 1.5, ey + ery * 0.95)   # нос
        for s in (1, -1):                                                       # румянец
            bl = Image.new("RGBA", (int(hr * 0.5), int(hr * 0.3)), (0, 0, 0, 0)); ImageDraw.Draw(bl).ellipse((0, 0, bl.width - 1, bl.height - 1), fill=(240, 120, 110, 90 + int(anger * 80)))
            put(cv, bl.filter(ImageFilter.GaussianBlur(hr * 0.05)), hc[0] + ex * 1.25 * s + off, ey + ery * 1.1)
        if P.get("beard_fn"): P["beard_fn"](cv, hc, hr, off)
        mouth(d, hc[0] + off * 1.5, hc[1] + hr * 0.52, hr * 0.62, mood, talk)
        hf, angf = arm(0, False)                                                # ближняя рука
        self.tip = None
        if item:
            tp = tool(cv, hf, item_ang if item_ang is not None else angf, item, f); self.tip = (tp[0] / S * scale, tp[1] / S * scale)
        out = cv.resize((int(Wc * scale), int(Hc * scale)), Image.LANCZOS)
        return out

def lerp_c(a, b, t): return a + (b - a) * t

def boy_hair(cv, hc, hr, f):
    col = (96, 58, 36)
    put(cv, ball(int(hr * 2.08), int(hr * 1.3), col, rim=0.5, spec=0.25), hc[0], hc[1] - hr * 0.5)
    for k, (dx, dy, a) in enumerate([(-0.55, -0.95, 30), (-0.1, -1.08, -5), (0.4, -1.0, -30), (0.85, -0.6, -60), (-0.9, -0.5, 60)]):
        put(cv, ball(int(hr * 0.5), int(hr * 0.8), col, rim=0.5, spec=0.25), hc[0] + hr * dx * f, hc[1] + hr * dy, a * f)
def dad_hair(cv, hc, hr, f):
    col = (88, 66, 50); put(cv, ball(int(hr * 2.06), int(hr * 1.16), col, rim=0.5, spec=0.2), hc[0], hc[1] - hr * 0.56)
def dad_beard(cv, hc, hr, off):
    col = (98, 72, 54); put(cv, ball(int(hr * 1.5), int(hr * 0.62), col, rim=0.5, spec=0.12), hc[0], hc[1] + hr * 0.8)
    put(cv, ball(int(hr * 0.8), int(hr * 0.22), shade(col, 0.9), rim=0.3, spec=0.1), hc[0] + off * 1.5, hc[1] + hr * 0.4)

BOY = Character(dict(canvas=(360, 500), leg=60, torso_h=100, torso_w=92, head_r=64, sh=38, hipw=18, arm_up=44, arm_low=40, limb=17,
                     skin=(242, 192, 152), shirt=(232, 112, 62), sleeve=(232, 112, 62), pants=(64, 96, 156), shoes=(170, 70, 50),
                     iris=(110, 70, 40), brow=(80, 46, 30), eye=0.33, hair_fn=boy_hair, short_sleeve=True, short_pants=True))
DAD = Character(dict(canvas=(450, 800), leg=150, torso_h=180, torso_w=122, head_r=66, sh=54, hipw=26, arm_up=85, arm_low=80, limb=27,
                     skin=(232, 180, 140), shirt=(58, 128, 120), sleeve=(58, 128, 120), pants=(104, 80, 62), shoes=(80, 54, 40),
                     iris=(70, 96, 70), brow=(74, 54, 40), eye=0.27, hair_fn=dad_hair, beard_fn=dad_beard))
