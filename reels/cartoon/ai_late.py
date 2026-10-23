"""«Сделай так, чтобы никто не опаздывал» — ИИ исполняет приказ буквально. Без озвучки, 38 с, 24 к/с, всё кодом (numpy/PIL), звук синтезирован.
Сценарий scripts/ai_late_1.md. Запуск: python3 cartoon/ai_late.py            → ai_late_1.mp4 (затем finalize.py ai_late_1)
                                      python3 cartoon/ai_late.py 3 7 12 20   → превью work/ai_late_1/pv_*.png"""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W, H, FPS, DUR, SR = 1080, 1920, 24, 38.0, 44100
NAME = "ai_late_1"; WK = f"work/{NAME}"; os.makedirs(WK, exist_ok=True)
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-{}.ttf"; INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_F = {}
def font(kind, w, size):
    k = (kind, w, size)
    if k not in _F: _F[k] = ImageFont.truetype((MONO if kind == "m" else INTER).format(w), size)
    return _F[k]
def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def seg(t, a, b): return min(max((t - a) / (b - a), 0.0), 1.0)
def mixc(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
rng = np.random.RandomState(7)

# ---------- тайминги
REQ = "Сделай так, чтобы никто не опаздывал."
T_TYPE0, T_TYPE1, T_BIG, T_UNDERSTOOD, T_B, T_C, T_D, T_DONE, T_END, T_CARD = 0.6, 4.2, 4.5, 5.5, 6.6, 15.0, 25.8, 31.3, 33.4, 34.2
ROWS = [("ПОЕЗД 07:42", 8.2), ("АВТОБУС №12", 9.3), ("РАБОТА 09:00", 10.4), ("ШКОЛА 08:30", 11.5), ("ВСТРЕЧИ", 12.6), ("РАСПИСАНИЕ", 13.7)]
CNT = [(6.6, 100), (8.2, 100), (9.3, 86.0), (10.4, 73.43), (11.5, 52.0), (12.6, 31.5), (13.7, 12.0), (15.0, 0.01), (15.5, 0.0)]
REPLY = [("Готово.", 26.4), ("Расписание удалено.", 27.6), ("Опозданий: 0.", 28.8), ("Чем ещё помочь?", 30.0)]
def counter(t):
    if t < CNT[0][0]: return 100.0
    for (a, va), (b, vb) in zip(CNT, CNT[1:]):
        if a <= t < b: return va + (vb - va) * ease(seg(t, a, b))
    return 0.0
def moving(t): return 1.0 if t < 8.0 else 1 - ease(seg(t, 8.0, 14.5))
_TT = np.cumsum(np.array([moving(i * 0.01) for i in range(int(DUR * 100) + 2)])) * 0.01
def travel(t): return float(np.interp(t, np.arange(len(_TT)) * 0.01, _TT))
def char_t(i): return T_TYPE0 + (T_TYPE1 - T_TYPE0) * i / len(REQ)

# ---------- мир: улицы в перспективе, люди-огни, силуэт города
N = 5500; LANE = 1.5
lane = rng.randint(-9, 10, N); dx = rng.uniform(-0.28, 0.28, N); DX = lane * LANE + dx
Z0 = rng.uniform(0, 1, N); DIR = np.where(rng.rand(N) < 0.5, 1, -1); SPD = rng.uniform(0.9, 1.5, N); ZMIN, ZMAX = 1.3, 42.0
TW = rng.rand(N)
BLD = []; x = -900
while x < W + 900:
    w = rng.randint(70, 190); h = rng.randint(120, 400); BLD.append((x, w, h, [(rng.rand(), i, j) for i in range(w // 26) for j in range(h // 34)])); x += w + rng.randint(0, 22)
def dot_col(c):
    amber, red, blue = (255, 200, 120), (255, 70, 60), (120, 190, 255)
    if c > 70: return mixc(amber, red, (100 - c) / 60)
    if c > 5: return mixc(red, red, 0) if c > 30 else mixc(red, blue, (30 - c) / 25 * 0.6)
    return blue

def world(t, dim, cnt):
    k = 1 + 0.10 * t / DUR; f = 900 * k; hor = 1010 + 20 * math.sin(t * 0.3); hc = 1.0
    base = np.zeros((H, W, 3), np.float32); base[:] = (5, 8, 14)
    grad = np.linspace(0, 1, H)[:, None, None]; base += grad * np.array([2, 5, 10], np.float32) * (1 - dim * 0.4)
    im = Image.fromarray(base.astype(np.uint8)); d = ImageDraw.Draw(im)
    lights = Image.new("RGB", (W, H)); ld = ImageDraw.Draw(lights)
    # силуэт города + окна
    p = 0.55 * (1 - ease(seg(t, 8.0, 14.8))) + (0.04 * (rng.rand() < 0) if t > 15 else 0)
    for bx, bw, bh, win in BLD:
        sx = (bx - W / 2) * (k * 0.5 + 0.5) + W / 2
        d.rectangle((sx, hor - bh, sx + bw, hor), fill=(10, 17, 30)); d.line((sx, hor - bh, sx + bw, hor - bh), fill=(30, 48, 78), width=2)
        for r, i, j in win:
            if r < p * (0.8 + 0.2 * math.sin(t * 3 + r * 40)): ld.rectangle((sx + 10 + i * 26, hor - bh + 12 + j * 34, sx + 19 + i * 26, hor - bh + 25 + j * 34), fill=(255, 196, 110))
    # сетка улиц
    g = Image.new("RGB", (W, H)); gd = ImageDraw.Draw(g)
    for L in range(-12, 13):
        x = L * LANE; far, near = ZMAX, ZMIN
        gd.line((W / 2 + x * f / far, hor + hc * f / far, W / 2 + x * f / near, hor + hc * f / near), fill=(16, 40, 72), width=2)
    for zz in np.arange(2.0, 42, 2.4):
        c = int(70 / (zz ** 0.55)); gd.line((0, hor + hc * f / zz, W, hor + hc * f / zz), fill=(c // 3, int(c // 1.6), c), width=2)
    # красные волны «отмены»
    for _, ts in ROWS:
        a = t - ts
        if 0 <= a < 1.4:
            zz = ZMAX - (ZMAX - ZMIN) * ease(a / 1.4) ** 1.3; gd.line((0, hor + hc * f / zz, W, hor + hc * f / zz), fill=(255, 60, 50), width=5)
    # люди
    Tm = travel(t); z = ZMIN + (ZMAX - ZMIN) * np.mod(Z0 + DIR * SPD * Tm * 0.09, 1.0) ** 2.4
    sx = W / 2 + DX * f / z; sy = hor + hc * f / z
    col = np.array(dot_col(cnt), np.float32)
    inten = np.clip(3.0 / z ** 0.7, 0.25, 1.8) * (0.75 + 0.25 * np.sin(t * 4 + TW * 30)) * (0.8 if cnt < 5 else 1.0)
    ok = (sx > 1) & (sx < W - 2) & (sy > hor) & (sy < H - 2)
    cvi = Image.new("RGB", (W, H)); cd = ImageDraw.Draw(cvi)
    rad = np.clip(7.0 / z, 1.2, 8.0)
    for x_, y_, r_, i_ in zip(sx[ok], sy[ok], rad[ok], inten[ok]):
        cd.ellipse((x_ - r_, y_ - r_, x_ + r_, y_ + r_), fill=tuple(int(min(255, v * i_)) for v in col))
    near = np.asarray(cvi.filter(ImageFilter.GaussianBlur(1.2)), np.float32); wide = np.asarray(cvi.filter(ImageFilter.GaussianBlur(7)), np.float32)
    lw = np.asarray(lights.filter(ImageFilter.GaussianBlur(6)), np.float32); ls = np.asarray(lights, np.float32)
    out = np.asarray(im, np.float32) + np.asarray(g, np.float32) * (0.7 - 0.2 * dim) + np.asarray(cvi, np.float32) * 1.0 + near * 0.8 + wide * 2.0 + ls * 0.75 + lw * 1.1
    return out * dim, hor

# ---------- интерфейс
def ig_icon(d, x, y, s, fill=(255, 255, 255)):
    fill = tuple(int(v) for v in fill)
    d.rounded_rectangle((x, y, x + s, y + s), radius=s * 0.3, outline=fill, width=max(2, s // 12))
    d.ellipse((x + s * .28, y + s * .28, x + s * .72, y + s * .72), outline=fill, width=max(2, s // 12)); d.ellipse((x + s * .72, y + s * .2, x + s * .82, y + s * .3), fill=fill)
def tw(d, xy, s, fnt, fill, anchor="la"): d.text(xy, s, font=fnt, fill=tuple(int(v) for v in fill), anchor=anchor)
def brk(d, b, a=1.0, c=(150, 215, 255)):
    x0, y0, x1, y1 = b; col = tuple(int(v * a * 0.55) for v in c); L = 34
    d.rectangle(b, outline=tuple(int(v * a * 0.18) for v in c), width=1)
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=col, width=3); d.line((x, y, x, y + sy * L), fill=col, width=3)
def cursor_on(t): return int(t * 2.2) % 2 == 0

def frame(t):
    cnt = counter(t)
    # затемнение мира
    if t < T_B: dim = 0.18 + 0.1 * ease(seg(t, T_BIG, T_B))
    elif t < T_D: dim = 1.0
    elif t < T_END: dim = 0.55 - 0.1 * ease(seg(t, T_DONE, T_END))
    else: dim = 0.45 * (1 - ease(seg(t, T_END, T_CARD)))
    if t < 0.4: dim *= ease(t / 0.4)
    out, hor = world(t, dim, cnt)
    ui = Image.new("RGB", (W, H)); d = ImageDraw.Draw(ui); pan = Image.new("L", (W, H)); pd = ImageDraw.Draw(pan)
    WH, GR, RD, CY = (240, 245, 255), (110, 125, 150), (255, 70, 62), (150, 215, 255)
    glitch = 0.0
    # плашка и значок аккаунта
    if t < T_END:
                tw(d, (70, 262), "вымышленный сценарий", font("m", "Regular", 26), GR)
    # --- A: терминал
    if t < T_UNDERSTOOD + 1.1:
        if t < T_BIG:
            a = ease(seg(t, 0.2, 0.8)); pd.rectangle((60, 560, 1020, 920), fill=int(120 * a)); brk(d, (60, 560, 1020, 920), a)
            tw(d, (90, 590), "новый запрос · 07:58", font("m", "Regular", 30), mixc((0, 0, 0), GR, a))
            n = sum(1 for i in range(len(REQ)) if char_t(i) <= t); s = REQ[:n]; ff = font("m", "Medium", 62)
            lines = ["Сделай так, чтобы", "никто не", "опаздывал."]; shown, pos = [], 0
            for ln in lines:
                part = s[pos:pos + len(ln) + 1].strip() if False else None
            wrapped = [REQ[:17], REQ[18:26], REQ[27:]]; cum = [0, 18, 27]
            y = 680
            for li, ln in enumerate(wrapped):
                part = s[cum[li]:cum[li] + len(ln)] if n > cum[li] else ""
                tw(d, (120, y), part, ff, WH)
                if li == (0 if n <= 18 else 1 if n <= 27 else 2) and cursor_on(t):
                    wcur = d.textlength(part, font=ff); d.rectangle((120 + wcur + 4, y + 6, 120 + wcur + 30, y + 68), fill=CY)
                y += 92
            tw(d, (86, 680), "›", font("m", "Bold", 62), CY)
            if t >= T_TYPE1 and t < T_BIG: glitch = 0.0
        elif t < T_UNDERSTOOD:
            a = seg(t, T_BIG, T_UNDERSTOOD); sc = 1 + 0.08 * a; glitch = 1.0 if (t - T_BIG) < 0.35 else 0.0
            for i, ln in enumerate(["Сделай так,", "чтобы никто", "не опаздывал."]):
                tw(d, (W / 2, 640 + i * 120), ln, font("m", "Bold", int(84 * sc)), WH, "mm")
            if 0.35 < t - T_BIG < 0.55: glitch = 0.7
        else:
            a = seg(t, T_UNDERSTOOD, T_UNDERSTOOD + 1.0); fa = 1 - ease(seg(t, T_UNDERSTOOD + 0.7, T_UNDERSTOOD + 1.1))
            glitch = 1.0 if t - T_UNDERSTOOD < 0.25 else 0.0
            if fa > 0:
                col = tuple(int(c * fa) for c in WH); tw(d, (W / 2, 700), "понял", font("i", "Black", 150), col, "mm")
                d.rectangle((W / 2 - 230, 790, W / 2 + 230, 800), fill=tuple(int(c * fa) for c in RD))
    # --- B/C: счётчик
    if T_B <= t < T_D + 0.5:
        a = ease(seg(t, T_B, T_B + 0.5)) * (1 - ease(seg(t, T_D - 0.3, T_D + 0.5)))
        cc = mixc(WH, RD, min(1, (100 - cnt) / 25)) if cnt > 3 else mixc(RD, CY, ease(seg(t, 14.6, 15.6)))
        cc = tuple(int(c * a) for c in cc); pd.rectangle((60, 330, 640, 490), fill=int(150 * a))
        tw(d, (80, 345), "ЦЕЛЬ · ОПОЗДАНИЯ", font("m", "Regular", 28), tuple(int(c * a) for c in GR))
        tw(d, (80, 390), f"{cnt:.2f}".replace(".", ",") + " %", font("m", "Bold", 84), cc)
    # --- B: табло отмен
    if T_B <= t < T_C + 1.2:
        a = ease(seg(t, 7.6, 8.1)) * (1 - ease(seg(t, T_C, T_C + 1.0)))
        if a > 0:
            pd.rectangle((60, 1080, 1020, 1090 + 46 + 66 * len(ROWS)), fill=int(170 * a)); brk(d, (60, 1080, 1020, 1090 + 46 + 66 * len(ROWS)), a)
            tw(d, (90, 1100), "ТАБЛО · ОТПРАВЛЕНИЕ", font("m", "Regular", 28), tuple(int(c * a) for c in GR))
            for i, (nm, ts) in enumerate(ROWS):
                y = 1150 + i * 66; done = t >= ts; flash = max(0, 1 - (t - ts) / 0.35) if done else 0
                tw(d, (90, y), nm, font("m", "Bold", 40), tuple(int(c * a * (0.55 if done else 1)) for c in WH))
                if done:
                    c = mixc(RD, (255, 255, 255), flash); tw(d, (990, y), "ОТМЕНЕНО" if i < 5 else "УДАЛЕНО", font("m", "Bold", 40), tuple(int(v * a) for v in c), "ra")
                    d.line((90, y + 24, 90 + d.textlength(nm, font=font("m", "Bold", 40)), y + 24), fill=tuple(int(v * a) for v in RD), width=3)
                else: tw(d, (990, y), "по расписанию", font("m", "Regular", 32), tuple(int(v * a) for v in (90, 200, 140)), "ra")
        for nm, ts in ((None, 9.9), (None, 13.9)):
            pass
        if 9.7 <= t < 10.9:
            a2 = ease(seg(t, 9.7, 9.85)) * (1 - ease(seg(t, 10.5, 10.9))); glitch = max(glitch, 0.6 if t < 9.9 else 0.0)
            tw(d, (W / 2, 780), "ОТМЕНЕНО", font("i", "Black", 150), tuple(int(c * a2) for c in RD), "mm")
        if 13.8 <= t < 15.0:
            a2 = ease(seg(t, 13.8, 13.95)) * (1 - ease(seg(t, 14.6, 15.0))); glitch = max(glitch, 0.6 if t < 14.0 else 0.0)
            tw(d, (W / 2, 780), "РАСПИСАНИЕ", font("i", "Black", 118), tuple(int(c * a2) for c in RD), "mm"); tw(d, (W / 2, 900), "УДАЛЕНО", font("i", "Black", 118), tuple(int(c * a2) for c in RD), "mm")
    # --- C: часы
    if T_C + 0.4 <= t < T_D + 1.0:
        a = ease(seg(t, T_C + 0.4, T_C + 1.4)) * (1 - ease(seg(t, T_D - 0.4, T_D + 1.0)))
        cx, cy, R = W // 2, 730, 210; p = ease(seg(t, 15.8, 21.6)); spin = (1 - p) ** 2
        mn = 58 * 6 - 360 * 16 * spin; hr = (7 * 30 + 58 / 2) - 360 * 16 / 12 * spin
        pd.ellipse((cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30), fill=int(190 * a))
        rc = tuple(int(c * a) for c in CY); d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=rc, width=5)
        for i in range(60):
            ang = math.radians(i * 6); r1 = R - (26 if i % 5 == 0 else 12)
            d.line((cx + math.sin(ang) * r1, cy - math.cos(ang) * r1, cx + math.sin(ang) * (R - 4), cy - math.cos(ang) * (R - 4)), fill=rc, width=4 if i % 5 == 0 else 2)
        stop = t >= 21.6; hc_ = RD if (stop and t < 22.4) else WH
        for ang, ln, wd in ((hr, R * 0.5, 12), (mn, R * 0.78, 7)):
            r = math.radians(ang); d.line((cx, cy, cx + math.sin(r) * ln, cy - math.cos(r) * ln), fill=tuple(int(c * a) for c in hc_), width=wd)
        d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=tuple(int(c * a) for c in hc_))
        if stop:
            tw(d, (cx, cy + R + 70), "07:58", font("m", "Bold", 64), tuple(int(c * a) for c in WH), "mm")
            b = ease(seg(t, 22.6, 23.2)) * a; tw(d, (cx, cy + R + 150), "опозданий: 0", font("m", "Medium", 40), tuple(int(c * b) for c in CY), "mm")
    # --- D: ответ терминала
    if T_D <= t < T_END + 0.5:
        a = ease(seg(t, T_D, T_D + 0.5)) * (1 - ease(seg(t, T_DONE + 2.0, T_END + 0.5)))
        pd.rectangle((60, 600, 1020, 1040), fill=int(190 * a)); brk(d, (60, 600, 1020, 1040), a)
        for i, ln in enumerate(["› Сделай так, чтобы никто", "  не опаздывал."]): tw(d, (100, 630 + i * 46), ln, font("m", "Regular", 32), tuple(int(c * a * 0.55) for c in GR if True) if False else tuple(int(c * a) for c in (120, 135, 160)))
        y = 760
        for i, (s, ts) in enumerate(REPLY):
            if t < ts: continue
            n = int(min(len(s), (t - ts) / 0.045)); part = s[:n]; ff = font("m", "Medium", 56)
            tw(d, (100, y), ("• " if i == 0 else "  ") + part, ff, WH if i < 3 else CY)
            if i == len(REPLY) - 1 or n < len(s):
                if n < len(s) or cursor_on(t):
                    wcur = d.textlength(("• " if i == 0 else "  ") + part, font=ff); d.rectangle((100 + wcur + 4, y + 4, 100 + wcur + 28, y + 62), fill=CY)
            y += 80
    if T_DONE <= t < T_END + 0.5:
        a = ease(seg(t, T_DONE, T_DONE + 0.25)) * (1 - ease(seg(t, T_END - 0.3, T_END + 0.5))); glitch = max(glitch, 0.8 if t - T_DONE < 0.2 else 0.0)
        pd.rectangle((0, 1180, W, 1480), fill=int(170 * a))
        tw(d, (W / 2, 1270), "ЗАДАЧА", font("i", "Black", 130), tuple(int(c * a) for c in WH), "mm"); tw(d, (W / 2, 1400), "ВЫПОЛНЕНА", font("i", "Black", 130), tuple(int(c * a) for c in WH), "mm")
        d.rectangle((W / 2 - 300, 1470 - 10, W / 2 + 300, 1470 - 4), fill=tuple(int(c * a) for c in RD))
    # --- E: призыв
    if t >= T_CARD:
        a = ease(seg(t, T_CARD, T_CARD + 0.6))
        for i, ln in enumerate(["Отправь тому,", "кто вечно", "опаздывает"]): tw(d, (W / 2, 640 + i * 130), ln, font("i", "Black", 108), tuple(int(c * a) for c in WH), "mm")
        b = ease(seg(t, T_CARD + 1.2, T_CARD + 1.8))
        tw(d, (W / 2, 1120), "Подпишись", font("i", "Black", 72), tuple(int(c * b) for c in CY), "mm")
    # композиция
    uf = np.asarray(ui, np.float32); gl = np.asarray(ui.filter(ImageFilter.GaussianBlur(14)), np.float32); pa = np.asarray(pan, np.float32)[:, :, None] / 255.0
    res = out * (1 - pa) + uf + gl * 0.75
    # виньетка + зерно
    yy, xx = np.mgrid[0:H, 0:W]; vg = 1 - 0.45 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
    res = res * vg[:, :, None] + np.random.RandomState(int(t * FPS)).randn(H, W, 1) * 3.0
    fade = ease(t / 0.35) if t < 0.35 else 1.0
    res *= fade
    im8 = np.clip(res, 0, 255).astype(np.uint8)
    if glitch > 0:
        r = np.random.RandomState(int(t * FPS) + 3); im8 = im8.copy()
        for _ in range(int(10 * glitch) + 2):
            y0 = r.randint(300, 1500); h = r.randint(8, 70); im8[y0:y0 + h] = np.roll(im8[y0:y0 + h], r.randint(-70, 70), axis=1)
        im8[:, :, 0] = np.roll(im8[:, :, 0], int(8 * glitch), axis=1); im8[:, :, 2] = np.roll(im8[:, :, 2], -int(8 * glitch), axis=1)
    return im8

# ---------- звук (свой синтез)
def audio():
    n = int(DUR * SR); a = np.zeros(n, np.float32); tt = np.arange(n) / SR; r = np.random.RandomState(11)
    def add(t0, x, g=1.0):
        i = int(t0 * SR); x = x[:max(0, n - i)]; a[i:i + len(x)] += x * g
    def env(m, atk, dec): e = np.minimum(np.arange(m) / (atk * SR + 1), 1) * np.exp(-np.arange(m) / (dec * SR)); return e.astype(np.float32)
    def click(g=1.0, f=2200): m = int(0.03 * SR); x = (r.randn(m) * 0.6 + np.sin(2 * np.pi * f * np.arange(m) / SR)) * env(m, 0.0005, 0.006); return x * g
    def tone(f, d, g=1.0, atk=0.01, dec=None): m = int(d * SR); x = np.sin(2 * np.pi * f * np.arange(m) / SR) * env(m, atk, dec or d / 3); return x * g
    # дрон
    lv = np.interp(tt, [0, 4, 6.6, 15, 15.4, 26, 33, 38], [0.0, 0.10, 0.28, 0.34, 0.12, 0.10, 0.14, 0.0])
    drone = (np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 82.4 * tt + np.sin(tt * 0.4)) + 0.3 * np.sin(2 * np.pi * 110.5 * tt)) * (0.7 + 0.3 * np.sin(tt * 0.9))
    a += (drone * lv * 0.35).astype(np.float32)
    # нарастание шума 6,6–15
    nz = r.randn(n).astype(np.float32); k = np.convolve(nz, np.ones(60) / 60, "same"); a += k * np.interp(tt, [6.6, 15, 15.2], [0, 0.35, 0]).astype(np.float32) * 0.5
    for i in range(len(REQ)): add(char_t(i), click(0.35, 1800 + 300 * (i % 3)))
    add(T_BIG, tone(70, 0.9, 0.9, 0.002, 0.3)); add(T_UNDERSTOOD, tone(880, 0.25, 0.3, 0.002, 0.05)); add(T_UNDERSTOOD, tone(1320, 0.3, 0.2, 0.002, 0.07))
    tc = T_B
    while tc < 15.3: add(tc, click(0.12, 3200 if tc < 14 else 2400)); tc += 0.065
    for _, ts in ROWS: add(ts, tone(55, 0.7, 1.0, 0.002, 0.18)); add(ts, (r.randn(int(0.4 * SR)) * env(int(0.4 * SR), 0.001, 0.07) * 0.35).astype(np.float32))
    add(9.7, tone(110, 0.8, 0.7, 0.002, 0.25)); add(13.8, tone(80, 1.2, 0.9, 0.002, 0.35))
    add(15.0, tone(40, 2.5, 1.1, 0.003, 0.7))
    # часы: тиканье ускоренное → замедляется → стоп
    tc = 15.8
    while tc < 21.6:
        p = ease(seg(tc, 15.8, 21.6)); add(tc, click(0.3, 1500)); tc += 0.04 + 0.5 * p ** 2.2
    add(21.6, tone(60, 1.5, 0.9, 0.003, 0.4))
    for ln, ts in REPLY:
        for i in range(len(ln)): add(ts + i * 0.045, click(0.28, 2000))
    add(T_DONE, tone(440, 2.2, 0.35, 0.005, 0.9)); add(T_DONE, tone(659.3, 2.2, 0.28, 0.005, 0.9)); add(T_DONE, tone(880, 2.2, 0.2, 0.005, 0.9)); add(T_DONE, tone(48, 1.5, 0.9, 0.003, 0.5))
    add(T_CARD + 1.2, tone(1046, 0.8, 0.22, 0.003, 0.25))
    a *= np.minimum(1, (DUR - tt) / 1.5).astype(np.float32); a = np.tanh(a * 1.3) * 0.8
    st = np.stack([a, a], 1); fn = f"{WK}/audio.wav"
    with wave.open(fn, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())
    return fn

def job(i):
    Image.fromarray(frame(i / FPS)).save(f"{WK}/f_{i:05d}.png", compress_level=1); return i

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]: Image.fromarray(frame(float(s))).save(f"{WK}/pv_{float(s):05.2f}.png")
        sys.exit()
    wav = audio(); nf = int(DUR * FPS)
    with Pool(4) as p:
        for k, _ in enumerate(p.imap_unordered(job, range(nf))):
            if k % 100 == 0: print(k, flush=True)
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-framerate", str(FPS), "-i", f"{WK}/f_%05d.png", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"{NAME}.mp4"], check=True)
    subprocess.run(f"rm -f {WK}/f_*.png", shell=True); print("END")
