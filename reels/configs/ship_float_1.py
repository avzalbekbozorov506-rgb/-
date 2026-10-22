"""«Больше 27 000 тонн. Почему не тонет?» — формат «Простым языком», моушен-графика кодом (закон Архимеда).
Фото: NASA Image and Video Library (общественное достояние): KSC-2012-2818 (авианосец-музей «Интрепид»).
Факты и текст: scripts/ship_float_1.md."""
import os, sys, math; sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter1d
import bh_cine as B, plane_kit as K
from bh_cine import W, H, ease, seg, lerp, fnt
HEAD = ("ПРОСТЫМ ЯЗЫКОМ", "ПОЧЕМУ КОРАБЛЬ НЕ ТОНЕТ")
TITLE = ("", "", "")
HOOK = ("БОЛЕЕ 27 000 ТОНН.\nПОЧЕМУ НЕ ТОНЕТ?", 2.6)
HOOK_Y = 1010
MUSIC = ("music/ogv_aria.mp3", 0)
SUB_STYLE = "words"; WORDS_TAG = False; WORDS_Y = 1300; WORDS_SIZE = 92
AA = 0.35
GRAIN = 4.5
TAIL = 0.3; XF = 0.35; LEAD_N = 0.2; GAP = 0.28
RED = (255, 80, 60); GOLD = (255, 214, 60); ICE = (170, 215, 255); WHT = (240, 244, 255); DIM = (130, 150, 190); BLUE = (60, 150, 255); ORNG = (255, 140, 50)
BG = (6, 9, 18)
def ph(i, k):
    import __main__ as E
    return E.PHRASES[i][k]
def T(i, k, f=0.0): st, en, _ = ph(i, k); return st + f * (en - st)
def P(i, lt, k, f0=0.0, f1=1.0): return seg(lt, T(i, k, f0), T(i, k, f1))
def layer(): lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)
def fin(base, lay=None, lt=0.0, shake=1.5, k=0.6, streak=0.08, ca=2):
    base = base.convert("RGBA")
    if lay is not None: base.alpha_composite(lay)
    return B.finish_c(base, k=k, streak=streak, shake=shake, lt=lt, ca=ca)
def tx(d, xy, s, size, col=WHT, a=1.0, w="Bold", anchor="mm"):
    if a < 0.03: return
    d.text(xy, s, font=fnt(size, w), fill=col + (int(255 * min(a, 1)),), anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0, int(140 * min(a, 1))))
def pill(d, xy, s, size, col, a=1.0, w="Bold"):
    size = max(size, 34)
    if a < 0.03: return
    f = fnt(size, w); tw = d.textlength(s, font=f); x, y = xy
    d.rounded_rectangle((x - tw / 2 - 18, y - size * 0.75, x + tw / 2 + 18, y + size * 0.75), int(size * 0.75), fill=(6, 9, 18, int(200 * a)), outline=col + (int(200 * a),), width=2)
    d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor="mm")
def dark(): return Image.new("RGBA", (W, H), BG + (255,))
def grid_bg(lt, a=1.0):
    im = dark(); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(20, 30, 52, int(255 * a)), width=1)
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(20, 30, 52, int(255 * a)), width=1)
    return im
CX = 540; WL = 800          # центр и уровень воды
SEA = (20, 70, 130); STEEL = (112, 122, 138); AIRC = (150, 205, 255)
def hull_poly(cy_bot, w=560, h=210, bw=0.82, cx=CX):
    top = cy_bot - h; return [(cx - w / 2, top), (cx + w / 2, top), (cx + w / 2 * bw, cy_bot), (cx - w / 2 * bw, cy_bot)]
_SKY = {}
def sky_bg(lt):
    """Фон над водой: размытое небо с настоящего фото NASA, затемнённое, с лёгким дрейфом."""
    if "bg" not in _SKY:
        im = Image.open(f"{K.HERE}/art/nasa_intrepid.jpg").convert("RGB"); w0, h0 = im.size
        top = im.crop((0, 0, w0, int(h0 * 0.32))).resize((int(W * 1.3), int(WL * 1.05)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(28))
        arr = np.asarray(top).astype(np.float32) * np.array([0.22, 0.3, 0.45], np.float32); yy = np.linspace(0.35, 1.0, arr.shape[0], dtype=np.float32)[:, None, None]
        _SKY["bg"] = Image.fromarray(np.clip(arr * (0.45 + 0.55 * yy), 0, 255).astype(np.uint8))
    bg = _SKY["bg"]; ox = int((bg.width - W) * (0.5 + 0.4 * math.sin(lt * 0.15)))
    im = Image.new("RGBA", (W, H), BG + (255,)); im.paste(bg.crop((ox, 0, ox + W, bg.height)).convert("RGBA"), (0, 0))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(0, 300): d.line([(0, y), (W, y)], fill=(4, 6, 14, int(170 * (1 - y / 300))))
    im.alpha_composite(ov); return im
def water_over(im, lt, wl=WL, a=0.62, bottom=1180, tint=SEA):
    """Вода поверх объектов: градиент глубины, каустика, лучи света, пузыри, бегущая волна с бликом."""
    y0 = wl - 30; hh = bottom - y0; sw, sh = W // 2, hh // 2
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32); X = xx * 2; Y = yy * 2 + y0
    dep = np.clip((Y - wl) / 420.0, 0, 1)[..., None]
    top = np.array([40, 125, 185], np.float32); deep = np.array([4, 16, 42], np.float32); col = top * (1 - dep) + deep * dep
    c1 = np.sin(X * 0.021 + lt * 0.9 + np.sin(Y * 0.017 + lt * 0.6) * 2.0) + np.sin(Y * 0.029 - lt * 0.7 + np.sin(X * 0.013 + lt * 0.4) * 2.5)
    cau = np.exp(-6.0 * np.abs(c1))[..., None] * (1 - dep) ** 1.4 * np.array([120, 190, 230], np.float32)
    ray = np.clip(np.sin((X + Y * 0.45) * 0.017 + np.sin(lt * 0.5 + X * 0.004) * 1.5), 0, 1) ** 3 * (1 - dep[..., 0]) ** 1.6
    col = col + cau * 0.55 + ray[..., None] * np.array([60, 95, 120], np.float32)
    wave = 7 * np.sin(X / 85.0 + lt * 2.2) + 3 * np.sin(X / 33.0 - lt * 3.1); inside = (Y >= wl + wave)[..., None]
    alpha = np.where(inside, 255 * a * (0.9 + 0.1 * dep), 0.0)
    rgba = np.concatenate([np.clip(col, 0, 255), alpha], -1).astype(np.uint8)
    ov = Image.fromarray(rgba, "RGBA").resize((W, hh), Image.BILINEAR); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.paste(ov, (0, y0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(7)
    for k in range(70):
        px = rng.uniform(0, W) + 14 * math.sin(lt * 0.8 + k); sp = rng.uniform(25, 70); py = wl + 40 + (bottom - wl - 60) * (1 - ((rng.uniform(0, 1) + lt * sp / 600.0) % 1)); r = rng.uniform(1.5, 4.2)
        d.ellipse((px - r, py - r, px + r, py + r), outline=(190, 230, 255, 120), width=1)
    xs = np.arange(0, W + 20, 20); ys = wl + 7 * np.sin(xs / 85.0 + lt * 2.2) + 3 * np.sin(xs / 33.0 - lt * 3.1)
    line = [(int(x), float(y)) for x, y in zip(xs, ys)]; d.line(line, fill=(210, 240, 255, 240), width=4)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(line, fill=(150, 215, 255, 255), width=10); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(9))); im.alpha_composite(lay)
    fd = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fdd = ImageDraw.Draw(fd)
    for y in range(bottom - 90, bottom + 1): fdd.line([(0, y), (W, y)], fill=BG + (int(255 * (y - (bottom - 90)) / 90),))
    im.alpha_composite(fd)
_GR = {}
def hull_draw(im, bot, lt, air=1.0, wl=WL, fill_in=0.0, ghost=0.0, tilt=0.0, cav=True, w=560, h=210, label=None, bob=True, cx=CX):
    """Корпус в разрезе: стальной градиент, подсветка кромок, окна, воздух внутри (светящиеся точки). ghost — вытесненная вода."""
    if bob: bot = bot + 5 * math.sin(lt * 1.7); tilt = tilt + 1.1 * math.sin(lt * 1.3)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    P = hull_poly(bot, w, h, cx=cx); top = bot - h; t = 26
    key = (w, h)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(P, fill=255)
    grad = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; yv = np.clip((np.arange(H)[:, None, None] - top) / max(h, 1), 0, 1)
    base = (np.array([150, 162, 182], np.float32) * (1 - yv) + np.array([58, 66, 84], np.float32) * yv) * np.ones((1, W, 1), np.float32)
    g = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA"); lay.paste(g, (0, 0), m); d = ImageDraw.Draw(lay)
    d.line([P[0], P[1]], fill=(235, 242, 255, 255), width=4); d.line([P[0], P[3]], fill=(190, 205, 230, 255), width=3); d.line([P[1], P[2]], fill=(120, 135, 160, 255), width=3); d.line([P[3], P[2]], fill=(90, 105, 135, 255), width=3)
    inner = [(P[0][0] + t, top + t), (P[1][0] - t, top + t), (P[2][0] - t * 1.4, bot - t), (P[3][0] + t * 1.4, bot - t)]
    if cav:
        d.polygon(inner, fill=(7, 12, 26, 255)); rng = np.random.default_rng(3)
        for k in range(46):
            px = rng.uniform(inner[0][0] + 10, inner[1][0] - 10); py = rng.uniform(top + t + 8, bot - t - 8) + 5 * math.sin(lt * 2 + k)
            if air > 0.02 and rng.random() < air + 0.02: r = 3; d.ellipse((px - r, py - r, px + r, py + r), fill=AIRC + (int(200 * air),))
        if fill_in > 0.01:
            yy_ = (bot - t) - fill_in * (bot - t - (top + t)); d.polygon([(inner[3][0], bot - t), (inner[2][0], bot - t), (inner[2][0], yy_), (inner[3][0], yy_)], fill=SEA + (230,))
    d.rectangle((cx - 70, top - 62, cx + 70, top), fill=(120, 132, 154, 255), outline=(225, 235, 255, 255), width=2); d.rectangle((cx - 8, top - 120, cx + 8, top - 62), fill=(120, 132, 154, 255))
    for k in range(5): d.rectangle((cx - 56 + k * 24, top - 46, cx - 42 + k * 24, top - 34), fill=(255, 214, 120, 255))
    if tilt: lay = lay.rotate(tilt, center=(cx, bot - h / 2), resample=Image.BICUBIC)
    glow = lay.filter(ImageFilter.GaussianBlur(14)); glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.25))); im.alpha_composite(glow); im.alpha_composite(lay)
    if ghost > 0.01:
        m2 = Image.new("L", (W, H), 0); ImageDraw.Draw(m2).polygon(P, fill=255); wm = Image.new("L", (W, H), 0); ImageDraw.Draw(wm).rectangle((0, wl, W, H), fill=255)
        mk = ImageChops.multiply(m2, wm); gh = Image.new("RGBA", (W, H), (255, 214, 60, 255)); gh.putalpha(mk.point(lambda v: int(v * 0.55 * ghost))); im.alpha_composite(gh)
        ol = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ol).polygon(P, outline=(255, 226, 120, int(255 * ghost)), width=4); ol.putalpha(ImageChops.multiply(ol.getchannel("A"), wm)); im.alpha_composite(ol)
    return P
def sea_scene(lt, bot, **kw):
    im = sky_bg(lt); ImageDraw.Draw(im).text((W - 40, 1150), "СХЕМА · НЕ В МАСШТАБЕ", font=fnt(24, "Medium"), fill=(150, 175, 215, 200), anchor="rm"); P = hull_draw(im, bot, lt, **{k: v for k, v in kw.items() if k not in ("wl_a",)}); water_over(im, lt, a=kw.get("wl_a", 0.55)); return im, P
def force_arrows(im, bot, up, down, a=1.0):
    K.arrow_glow(im, (CX, bot - 105), (CX, bot - 105 - up), (110, 215, 255), w=14, head=46, a=a)
    K.arrow_glow(im, (CX - 150, bot - 105), (CX - 150, bot - 105 + down), GOLD, w=14, head=46, a=a)
# ---------- 0. хук: фото авианосца
def s0(lt, D):
    im = K.photo("nasa_intrepid", lt, D, z0=1.0, z1=1.1, fx=0.5, fy=0.55, dx=0.05, cy=700).convert("RGBA"); lay, d = layer()
    a = P(0, lt, 0, 0.2, 0.7)
    if a > 0:
        B.reticle(d, (400, 800), 170, GOLD + (int(220 * a),), u=a, ticks=36, w=2)
        B.leader(d, (330, 690), (300, 560), (90, 560), GOLD + (220,), u=a); pill(d, (270, 520), "БОЛЕЕ 27 000 Т", 28, GOLD, a=P(0, lt, 0, 0.5, 1.0))
        tx(d, (540, 330), "«ИНТРЕПИД», НЬЮ-ЙОРК · СТАНДАРТНОЕ ВОДОИЗМЕЩЕНИЕ", 30, WHT, a=P(0, lt, 1, 0.2, 0.8), w="Medium")
    return fin(im, lay, lt, shake=2.0 * P(0, lt, 1, 0.5, 1.0) + 1.0, k=0.45, streak=0.3)
# ---------- 1. сталь + воздух
def s1(lt, D):
    im, Pp = sea_scene(lt, WL + 120, air=1.0); lay, d = layer()
    a0 = P(1, lt, 0, 0.3, 0.8); a1 = P(1, lt, 1, 0.3, 0.8)
    B.tracked(d, (540, 350), "СТАЛЬ + ВОЗДУХ", 50, ICE, u=P(1, lt, 0, 0.0, 0.7))
    if a0 > 0: B.leader(d, (CX - 262, WL - 20), (CX - 340, WL - 160), (80, WL - 160), GOLD + (230,), u=a0); pill(d, (200, WL - 200), "СТАЛЬ", 28, GOLD, a=a0)
    if a1 > 0: B.leader(d, (CX + 20, WL - 40), (CX + 160, WL - 250), (CX + 360, WL - 250), ICE + (230,), u=a1); pill(d, (CX + 290, WL - 292), "ВОЗДУХ", 28, ICE, a=a1)
    return fin(im, lay, lt, k=0.7)
# ---------- 2. «Простым языком»
def s2(lt, D):
    im = dark(); lay, d = layer(); u = P(2, lt, 0, 0.0, 0.7)
    B.tracked(d, (540, 700), "ПРОСТЫМ ЯЗЫКОМ", 64, WHT, u=u, w="Bold", sp=0.18); d.line([(540 - 300 * u, 760), (540 + 300 * u, 760)], fill=GOLD + (230,), width=3)
    return fin(im, lay, lt, shake=0, k=0.7)
# ---------- 3. кусок стали тонет
def s3(lt, D):
    im = sky_bg(lt); lay, d = layer(); fall = P(3, lt, 0, 0.1, 1.0) * 0 + seg(lt, T(3, 0, 0.2), T(3, 1, 0.55))
    y = 470 + 560 * fall ** 1.6; d.rounded_rectangle((CX - 110, y - 110, CX + 110, y + 110), 14, fill=STEEL + (255,), outline=(205, 215, 235, 255), width=3)
    im.alpha_composite(lay); water_over(im, lt, a=0.5); lay, d = layer()
    B.tracked(d, (540, 350), "СТАЛЬ ТОНЕТ", 50, ICE, u=P(3, lt, 0, 0.0, 0.7))
    u = P(3, lt, 1, 0.2, 0.9)
    if u > 0: tx(d, (300, 1010), "СТАЛЬ", 34, WHT, a=u); tx(d, (300, 1075), "7,8 т/м³", 60, GOLD, a=u); tx(d, (780, 1010), "ВОДА", 34, WHT, a=u); tx(d, (780, 1075), "1,0 т/м³", 60, ICE, a=u)
    return fin(im, lay, lt, k=0.7)
# ---------- 4. закон Архимеда
def s4(lt, D):
    bot = WL + 130; gh = P(4, lt, 0, 0.3, 0.9); im, Pp = sea_scene(lt, bot, ghost=gh); lay, d = layer()
    tx(d, (780, WL + 190), "ВЫТЕСНЕННАЯ ВОДА", 28, GOLD, a=gh)
    u = P(4, lt, 1, 0.2, 0.8); u2 = P(4, lt, 2, 0.2, 0.8)
    if u > 0: K.arrow_glow(im, (CX, WL + 60), (CX, WL + 60 - 340 * u), (110, 215, 255), w=16, head=50); pill(d, (CX + 220, WL - 170), "ВЫТАЛКИВАНИЕ", 28, (110, 215, 255), a=u)
    if u2 > 0: K.arrow_glow(im, (CX - 190, WL - 140), (CX - 190, WL - 140 + 340 * u2), GOLD, w=14, head=46); pill(d, (CX - 300, WL - 170), "ВЕС", 28, GOLD, a=u2)
    B.tracked(d, (540, 350), "ЗАКОН АРХИМЕДА", 50, WHT, u=P(4, lt, 3, 0.0, 0.7))
    if u2 > 0.6: pill(d, (CX, WL - 330), "СИЛЫ РАВНЫ", 34, WHT, a=min(1, (u2 - 0.6) * 2.5))
    return fin(im, lay, lt, k=0.7)
# ---------- 5. та же сталь: брусок тонет, корпус плывёт
def s5(lt, D):
    im = sky_bg(lt); lay, d = layer(); k0 = P(5, lt, 0, 0.0, 0.7)
    y = 760 + 220 * ease(P(5, lt, 0, 0.1, 0.9)); d.rounded_rectangle((250 - 70, y - 70, 250 + 70, y + 70), 10, fill=STEEL + (255,), outline=(205, 215, 235, 255), width=3)
    im.alpha_composite(lay); P_ = hull_draw(im, WL + 70 + 40 * (1 - P(5, lt, 1, 0.1, 0.8)), lt, w=440, h=150, cav=True, cx=CX + 170)
    # корпус сдвигаем вправо: рисуем отдельно
    water_over(im, lt, a=0.5); lay, d = layer()
    tx(d, (250, 1040), "ТА ЖЕ СТАЛЬ", 34, WHT, a=k0); tx(d, (CX + 170, 1040), "ТА ЖЕ СТАЛЬ", 34, WHT, a=k0)
    B.tracked(d, (540, 350), "ФОРМА РЕШАЕТ", 50, GOLD, u=P(5, lt, 1, 0.1, 0.8))
    return fin(im, lay, lt, k=0.7)
# ---------- 6. ватерлиния
def s6(lt, D):
    s = P(6, lt, 0, 0.0, 0.9); bot = WL - 20 + 150 * s; kg = 27000 * (s ** 1.0)
    im, Pp = sea_scene(lt, bot, ghost=0.7 * s, bob=False); lay, d = layer()
    tx(d, (300, 420), "ВЫТЕСНЕНО", 30, DIM, a=1); tx(d, (300, 450), f"{kg:,.0f} Т".replace(",", " "), 70, GOLD, a=1)
    u = P(6, lt, 1, 0.3, 0.9)
    if u > 0: d.rounded_rectangle((120, 1010, 960, 1110), 16, fill=(10, 14, 26, int(230 * u)), outline=GOLD + (int(220 * u),), width=2); tx(d, (540, 1060), "ВЫТЕСНЕНО  =  ВЕС", 44, GOLD, a=u)
    w3 = P(6, lt, 2, 0.2, 0.8)
    if w3 > 0:
        d.line([(60, WL), (60 + 960 * w3, WL)], fill=RED + (230,), width=3); pill(d, (780, WL - 60), "ВАТЕРЛИНИЯ", 34, RED, a=w3)
    return fin(im, lay, lt, k=0.7)
# ---------- 7. десять олимпийских бассейнов
def s7(lt, D):
    im = grid_bg(lt); lay, d = layer(); B.tracked(d, (540, 350), "ВОДА НА 27 000 Т", 50, ICE, u=P(7, lt, 0, 0.0, 0.7))
    n = P(7, lt, 1, 0.1, 0.8) * 10.4
    for i in range(11):
        r, c = divmod(i, 3); x0 = 140 + c * 280; y0 = 440 + r * 150; fill = min(max(n - i, 0), 1)
        d.rounded_rectangle((x0, y0, x0 + 250, y0 + 110), 10, outline=ICE + (200,), width=3, fill=(10, 20, 40, 255))
        if fill > 0: d.rounded_rectangle((x0 + 6, y0 + 6, x0 + 6 + 238 * fill, y0 + 104), 8, fill=(40, 130, 220, 230))
    tx(d, (540, 1110), f"≈ {26000 * min(n / 10.4, 1):,.0f} М³".replace(",", " "), 64, GOLD, a=P(7, lt, 1, 0.2, 0.7))
    tx(d, (540, 1190), "10 ОЛИМПИЙСКИХ БАССЕЙНОВ", 32, ICE, a=P(7, lt, 2, 0.1, 0.6), w="Medium")
    return fin(im, lay, lt, k=0.7)
# ---------- 8. пробоина
def s8(lt, D):
    sink = P(8, lt, 1, 0.1, 1.0) * 0 + seg(lt, T(8, 0, 0.5), T(8, 2, 1.0)); fi = P(8, lt, 1, 0.0, 0.9); bot = WL + 130 + 330 * sink
    im, Pp = sea_scene(lt, bot, fill_in=fi, air=1 - fi); lay, d = layer()
    hx, hy = CX + 250, bot - 70; u0 = P(8, lt, 0, 0.5, 0.95)
    if u0 > 0:
        d.polygon([(hx - 20, hy - 40), (hx + 18, hy - 10), (hx - 8, hy + 8), (hx + 14, hy + 40), (hx - 26, hy + 24)], fill=RED + (int(255 * u0),))
        pill(d, (CX + 250, bot - 190), "ПРОБОИНА", 28, RED, a=u0)
    if lt >= T(8, 2, 0.15): bl = 0.6 + 0.4 * (int(lt * 5) % 2); d.rounded_rectangle((250, 330, 830, 420), 16, fill=(60, 8, 8, int(220 * bl)), outline=RED + (255,), width=3); tx(d, (540, 375), "ЗАПАС ИСЧЕЗ", 42, (255, 230, 230), a=1, w="Black")
    return fin(im, lay, lt, k=0.7, shake=1.0 + 3 * sink)
# ---------- 9. пресная и морская
def s9(lt, D):
    im = sky_bg(lt); lay, d = layer(); u = P(9, lt, 0, 0.1, 0.8)
    d_f = 160 + 14 * u; d_s = 160
    for cx_, dr, col, nm, rho in ((290, d_f, (90, 200, 140), "ПРЕСНАЯ", "1,000"), (790, d_s, ICE, "МОРЕ", "1,025")):
        hp = [(cx_ - 190, WL + dr - 150), (cx_ + 190, WL + dr - 150), (cx_ + 150, WL + dr), (cx_ - 150, WL + dr)]; d.polygon(hp, fill=STEEL + (255,), outline=(205, 215, 235, 255))
        d.rectangle((cx_ - 45, WL + dr - 205, cx_ + 45, WL + dr - 150), fill=(96, 106, 124, 255))
        tx(d, (cx_, WL + 225), nm, 34, WHT, a=u); tx(d, (cx_, WL + 280), rho + " т/м³", 44, col, a=u)
    im.alpha_composite(lay); water_over(im, lt, a=0.5); lay, d = layer()
    B.tracked(d, (540, 350), "ГЛУБЖЕ В ПРЕСНОЙ", 50, GOLD, u=P(9, lt, 0, 0.0, 0.7)); tx(d, (540, 1130), "(РАЗНИЦА ПОКАЗАНА С ЗАПАСОМ)", 24, DIM, a=P(9, lt, 1, 0.4, 0.9), w="Medium")
    return fin(im, lay, lt, k=0.7)
# ---------- 10. финал: тот же авианосец
def s10(lt, D):
    im = K.photo("nasa_intrepid", lt + 4, D + 4, z0=1.12, z1=1.2, fx=0.6, fy=0.62, cy=700).convert("RGBA"); lay, d = layer(); a = P(10, lt, 1, 0.2, 0.8)
    for k in range(7):
        x = 180 + k * 120; y0 = 900; K.arrow_glow(im, (x, y0 + 120), (x, y0 + 120 - 90 * a), (110, 215, 255), w=8, head=26, a=a)
    B.tracked(d, (540, 350), "ДЕРЖИТ ВОДА", 50, ICE, u=a)
    return fin(im, lay, lt, k=0.45, streak=0.3)
# ---------- 11. концовка
def s11(lt, D):
    im = K.photo("nasa_intrepid", lt + 9, D + 9, z0=1.2, z1=1.24, fx=0.6, fy=0.62, cy=700).convert("RGBA"); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * P(11, lt, 0, 0.0, 0.4)))))
    lay, d = layer(); b = P(11, lt, 0, 0.1, 0.5); s_ = 1 + 0.04 * math.sin(lt * 6); w_, h_ = 480 * s_, 120 * s_
    if b > 0: d.rounded_rectangle((540 - w_ / 2, 760 - h_ / 2, 540 + w_ / 2, 760 + h_ / 2), 60, fill=(255, 200, 60, int(255 * b))); tx(d, (540, 760), "ОТПРАВЬ", 58, (20, 14, 6), a=b)
    return fin(im, lay, lt, k=0.45)
SCENES = [
    ("Больше двадцати семи тысяч тонн. | Почему он не тонет?", "SUB", "", s0, "", None),
    ("Ответ: корабль — это не просто сталь. | Это ещё и огромный объём воздуха.", "SUB", "", s1, "", None),
    ("Простым языком.", "SUB", "", s2, "", None),
    ("Кусок стали тонет: | она почти в восемь раз плотнее воды.", "SUB", "", s3, "", None),
    ("Тело в воде вытесняет воду. | Вода выталкивает его вверх | с силой, равной весу вытесненной воды. | Это закон Архим+еда, великого учёного.", "SUB", "", s4, "", None),
    ("Сделай корпус из стали, а внутри оставь воздух — | и вытеснять станет намного больше воды.", "SUB", "", s5, "", None),
    ("Корабль погружается ровно настолько, | чтобы вытесненная вода весила как он сам. | Эту границу называют ватерл+инией.", "SUB", "", s6, "", None),
    ("А сколько воды держит такой вес? | Около двадцати шести тысяч кубометров. | Это около десяти олимпийских бассейнов.", "SUB", "", s7, "", None),
    ("А если в корпусе пробоина, | внутрь входит вода, а воздуха меньше. | Воды слишком много, силы выталкивания не хватает, и корабль тонет.", "SUB", "", s8, "", None),
    ("В пресной воде корабль сидит чуть глубже: | она легче морской.", "SUB", "", s9, "", None),
    ("Больше двадцати семи тысяч тонн. | Держит не сталь, а вода, которую корабль вытеснил.", "SUB", "", s10, "", None),
    ("Отправь тому, кто думал, что железо всегда тонет. | Подпишись.", "SUB", SUB_PLATE, s11, "", None),
]
def SFX(STARTS, PHRASES, DURS, SR):
    out = []; rng = np.random.default_rng(1)
    def tm(i, k, f=0.0): st, en, _ = PHRASES[i][k]; return STARTS[i] + st + f * (en - st)
    def swash(dur, a=0.10):
        n = rng.normal(0, 1, int(SR * dur)); x = gaussian_filter1d(n, 8) * 2.5; t = np.arange(len(x)) / SR
        return a * x * np.sin(np.pi * t / dur) ** 2
    def click(a=0.25): t = np.arange(int(SR * 0.04)) / SR; return a * np.exp(-t * 120) * np.sin(2 * np.pi * 2200 * t)
    def thud(a=0.5): t = np.arange(int(SR * 0.6)) / SR; return a * np.exp(-t * 7) * np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 20)) * t)
    def beep(dur=1.4, a=0.12): t = np.arange(int(SR * dur)) / SR; g = (np.floor(t * 6) % 2 == 0); return a * g * np.sin(2 * np.pi * 880 * t)
    out += [(tm(0, 0, 0.0), swash(DURS[0], 0.12)), (tm(2, 0, 0.0), click(0.35)), (tm(3, 0, 0.5), thud(0.5)), (tm(3, 0, 0.6), swash(1.4, 0.12))]
    out += [(tm(4, 1, 0.3), click()), (tm(6, 2, 0.2), click()), (tm(7, 1, 0.1), click(0.2)), (tm(8, 0, 0.6), thud(0.5)), (tm(8, 2, 0.1), beep()), (tm(8, 1, 0.1), swash(2.0, 0.14)), (tm(10, 0, 0.0), swash(DURS[10], 0.1)), (tm(11, 0, 0.1), click(0.25))]
    return out
