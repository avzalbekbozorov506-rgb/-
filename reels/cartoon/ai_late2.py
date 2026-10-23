"""«Сделай так, чтобы никто не опаздывал» v2 — по scripts/ai_late_1_visual_v2.md (Avzaldoc): одна непрерывная 3D-камера, облако точек → город из 120 тыс. точек,
слова отмен из людей-точек на земле, часы 07:58, стекло-терминал; bloom, хроматика, тряска, зерно. Всё кодом (numpy/PIL), звук — синтез. Без озвучки.
Запуск: python3 cartoon/ai_late2.py → ai_late_1.mp4 (затем finalize.py ai_late_1);  python3 cartoon/ai_late2.py 2.5 5.5 → превью work/ai_late_1/pv_*.png"""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W, H, SW, SH, FPS, DUR, SR = 1080, 1920, 540, 960, 24, 38.0, 44100
NAME = "ai_late_1"; WK = f"work/{NAME}"; os.makedirs(WK, exist_ok=True)
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-{}.ttf"; INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_F = {}
def font(kind, w, size):
    k = (kind, w, size)
    if k not in _F: _F[k] = ImageFont.truetype((MONO if kind == "m" else INTER).format(w), size)
    return _F[k]
def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def eo5(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 5
def seg(t, a, b): return min(max((t - a) / (b - a), 0.0), 1.0)
def mixc(a, b, k): k = min(max(k, 0), 1); return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
def ic(c): return tuple(int(min(255, max(0, v))) for v in c)

# ---------------- тайминги и тексты
REQ = "Сделай так, чтобы никто не опаздывал."; LINES = [REQ[:17], REQ[18:26], REQ[27:]]; CUM = [0, 18, 27]
T_CUT, T_CUT2, T_FALL, T_CRUISE, T_CLOCK, T_SPIN_END, T_GLASS, T_DONE, T_END, T_CARD = 5.85, 5.92, 7.3, 8.6, 16.4, 19.0, 24.5, 31.0, 33.2, 33.4
EV = [(9.4, "ПОЕЗД", "поезд 07:42", 87.62), (10.5, "АВТОБУС", "автобус №12", 64.08), (11.6, "РАБОТА", "работа 09:00", 41.37), (12.6, "ШКОЛА", "школа 08:30", 18.90),
      (13.5, "ВСТРЕЧИ", "встречи", 4.26), (14.3, "РАСПИСАНИЕ", "расписание", 0.01)]
REPLY = [("Готово.", 26.4), ("Расписание удалено.", 27.6), ("Опозданий: 0.", 28.8), ("Чем ещё помочь?", 30.0)]
_r = np.random.RandomState(5); _d = _r.uniform(0.07, 0.16, len(REQ)); _d[[REQ.index(",")]] += 0.35
CT = 0.6 + np.cumsum(_d) / _d.sum() * 3.8 - _d[0] * 0   # время появления каждого символа
def counter(t):
    v = 100.0; prev = 100.0
    for t0, _, _, tgt in EV:
        v = prev + (tgt - prev) * ease(seg(t, t0 + 0.65, t0 + 1.15)); prev = tgt if t >= t0 + 1.15 else prev
        if t < t0 + 1.15: break
    return 0.0 if t >= 15.6 else v
LOG0 = [("› задача: опоздания", 8.8, 0), ("› причина: расписание", 9.0, 1), ("› кратчайший путь: найден", 9.2, 0), ("› выполняю…", 9.35, 0)] + [(f"› отмена: {e[2]}", e[0], 1) for e in EV]

# ---------------- камера
_v = lambda t: float(np.interp(t, [8.6, 9.2, 14.5, 15.4, 16.4, 16.5, 19.4, 22.0, 26.0, 26.1, 38], [0, 140, 60, 0, 0, 70, 50, 30, 30, 5, 5]))
_TT = np.arange(8.6, 38.01, 0.01); _ZS = np.cumsum([_v(x) for x in _TT]) * 0.01
def zc(t): return float(np.interp(t, _TT, _ZS))
CL = np.array([0.0, 900.0, -200.0])
def orbit(t):
    th = math.radians(40 + 55 * seg(t, T_CUT2, T_FALL)); pos = CL + np.array([230 * math.sin(th), 24, -230 * math.cos(th)]); f = CL - pos; f /= np.linalg.norm(f)
    return pos, math.degrees(math.atan2(f[0], f[2])), math.degrees(math.asin(f[1])), 0.0, 50.0
def pose(t):
    """pos, yaw, pitch, roll (градусы), fov"""
    if t < T_CUT:
        p = seg(t, 5.0, T_CUT) ** 3; z = 12 * min(t, 5.0) + (465 - 60) * p; fov = 50 - 4 * seg(t, 0.4, 4.6) + (68 - 46) * p
        return np.array([0.0, 0.0, z]), -3 + 5 * seg(t, 0.4, 4.6), 0.0, -3 + 8 * p, fov
    if t < T_FALL: return orbit(t)
    ye = orbit(T_FALL - 1e-3); y0 = ye[1]
    if t < T_CRUISE:
        a = ease(seg(t, T_FALL, T_CRUISE)); pos = ye[0] * (1 - a) + np.array([0.0, 38.0, 0.0]) * a
        pos[1] = ye[0][1] + (38 - ye[0][1]) * eo5(seg(t, T_FALL, T_CRUISE) * 1.0) ** 1
        pitch = float(np.interp(t, [T_FALL, 7.8, 8.6], [ye[2], -78, -18])); fov = float(np.interp(t, [T_FALL, 8.0, 8.6], [55, 72, 66]))
        return pos, y0 * (1 - a), pitch, 0.0, fov
    ramp = ease(seg(t, 9.2, 10.0)) * (1 - ease(seg(t, 14.6, 15.4)))
    y = float(np.interp(t, [8.6, 16.4, 19.4, 22, 26, 38], [38, 38, 52, 52, 95, 95])) + 2.0 * math.sin(t * 0.9)
    pitch = float(np.interp(t, [8.6, 9.2, 16.4, 19.4, 22, 26, 38], [-18, -10, -9, -6, -6, -23, -23]))
    fov = float(np.interp(t, [8.6, 9.2, 15.4, 16.4, 19.4, 22, 26, 38], [66, 62, 62, 58, 58, 54, 50, 50]))
    yaw = 4 * math.sin(2 * math.pi * t / 8) * ramp + (1.5 * math.sin(t * 0.7) if t > 15.4 else 0); roll = 3 * math.sin(2 * math.pi * t / 5.5) * ramp
    return np.array([0.0, y, zc(t)]), yaw, pitch, roll, fov
def basis(yaw, pitch, roll):
    y, p, r = map(math.radians, (yaw, pitch, roll)); f = np.array([math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)]); r0 = np.array([math.cos(y), 0, -math.sin(y)])
    u0 = np.cross(f, r0); right = r0 * math.cos(r) + u0 * math.sin(r); up = u0 * math.cos(r) - r0 * math.sin(r); return f, right, up
class Cam:
    def __init__(s, t):
        s.pos, yaw, pitch, roll, s.fov = pose(t); s.f, s.r, s.u = basis(yaw, pitch, roll); s.fl = (SH / 2) / math.tan(math.radians(s.fov) / 2)
    def proj(s, P):
        pc = P - s.pos; z = pc @ s.f; return SW / 2 + s.fl * (pc @ s.r) / np.maximum(z, 1e-3), SH / 2 - s.fl * (pc @ s.u) / np.maximum(z, 1e-3), z

# ---------------- мир (всё из RandomState(7))
R7 = np.random.RandomState(7)
NP = 75000; LANES = np.arange(-390, 391, 60); ZLO, ZHI = -200.0, 3400.0
lon = R7.rand(NP) < 0.8
PX = np.where(lon, LANES[R7.randint(0, len(LANES), NP)] + R7.uniform(-3, 3, NP), R7.uniform(-420, 420, NP))
PZ0 = np.where(lon, R7.uniform(ZLO, ZHI, NP), ZLO + 65 * R7.randint(0, 56, NP) + R7.uniform(-3, 3, NP)); PDIR = np.where(R7.rand(NP) < 0.5, 1, -1); PTW = R7.rand(NP)
UKILL = R7.rand(NP); UKILL[0] = 0.0
KILL = np.full(NP, 99.0)
AF = [1.0] + [e[3] / 100 for e in EV]
for k, (t0, _, _, _) in enumerate(EV): KILL = np.where((UKILL > AF[k + 1]) & (KILL > 98), t0 + 0.65 + R7.uniform(0, 0.8, NP), KILL)
KILL[0] = 15.6
CLOUD = R7.randn(3500, 3) * np.array([110, 34, 50]) * 0.55; _a = math.radians(12); CLOUD = CLOUD @ np.array([[math.cos(_a), -math.sin(_a), 0], [math.sin(_a), math.cos(_a), 0], [0, 0, 1]])
CLOUD += CL; CRED = R7.rand(3500) < 0.2; CRANK = np.arange(3500) / 3500.0
NB = 360; BCX = -360 + 60 * R7.randint(0, 13, NB) + R7.uniform(-8, 8, NB); BCZ = ZLO + 32.5 + 65 * R7.randint(0, 55, NB); BW = R7.uniform(20, 40, NB); BD = R7.uniform(20, 40, NB); BHT = R7.uniform(40, 220, NB)
WB = R7.randint(0, NB, 43000); _face = R7.rand(43000)
WX = np.where(_face < 0.6, BCX[WB] + R7.uniform(-0.5, 0.5, 43000) * BW[WB], BCX[WB] + np.where(_face < 0.8, -1, 1) * BW[WB] / 2)
WZ = np.where(_face < 0.6, BCZ[WB] - BD[WB] / 2, BCZ[WB] + R7.uniform(-0.5, 0.5, 43000) * BD[WB]); WY = R7.uniform(4, 1, 43000) * BHT[WB] * 0.9 + 3
WON = 8.6 + (WZ + 100) / 700 + R7.uniform(0, 0.4, 43000); WOFF = 15.5 + (WZ - zc(15.5)) / 600 + R7.uniform(0, 0.4, 43000)
DUST = np.stack([R7.uniform(-300, 300, 1800), R7.uniform(-200, 200, 1800), R7.uniform(0, 900, 1800)], 1); DTW = R7.rand(1800)
DUST2 = np.stack([R7.uniform(-200, 200, 600), R7.uniform(-300, 300, 600), R7.uniform(100, 700, 600)], 1)
AMB, CORE, RED, BLU = np.array([255, 194, 122]) / 255, np.array([255, 241, 214]) / 255, np.array([255, 75, 62]) / 255, np.array([92, 200, 255]) / 255

def word_pts(word, seed):
    """локальные координаты (x, z) точек слова, лежащего на земле: ширина ~70 u, глубина растянута ×2,2"""
    f = font("i", "Black", 150); bb = f.getbbox(word); im = Image.new("L", (bb[2] + 10, bb[3] + 10), 0); ImageDraw.Draw(im).text((5, 0), word, font=f, fill=255)
    a = np.asarray(im.crop(im.getbbox())) > 128; h, w = a.shape; ys, xs = np.nonzero(a); r = np.random.RandomState(seed); sel = r.choice(len(xs), 2200, replace=len(xs) < 2200)
    wu = 70.0 if len(word) < 9 else 78.0; xs, ys = xs[sel], ys[sel]
    return (xs / w - 0.5) * wu, 105 + ((h - ys) / w) * wu * 2.2, r.uniform(-90, 90, (2200, 2)), r.uniform(0, 28, 2200)
WORDS = [word_pts(e[1], 30 + i) for i, e in enumerate(EV)]

def splat(acc, sx, sy, w, col):
    m = (sx >= 0) & (sx < SW - 1) & (sy >= 0) & (sy < SH - 1)
    if not m.any(): return
    sx, sy, w = sx[m], sy[m], w[m]; c = col[m] if col.ndim == 2 else np.broadcast_to(col, (len(sx), 3)); ix, iy = sx.astype(int), sy.astype(int); fx, fy = sx - ix, sy - iy
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        idx = (iy + dy) * SW + ix + dx
        for ch in range(3): acc[:, ch] += np.bincount(idx, weights=ww * w * c[:, ch], minlength=SW * SH)

def people_pos(t):
    z = ZLO + np.mod(PZ0 - ZLO + PDIR * 12.0 * min(t, 14.5) * lon, ZHI - ZLO); return np.stack([PX, np.full(NP, 0.6) + PTW * 0.8, z], 1)

def world(t, cam):
    acc = np.zeros((SW * SH, 3), np.float32); lines = Image.new("RGB", (SW, SH)); ld = ImageDraw.Draw(lines); near = Image.new("RGB", (SW, SH)); nd = ImageDraw.Draw(near)
    cnt = counter(t); tint = mixc(tuple(AMB), (1.0, 0.45, 0.3), 0.55 * (1 - cnt / 100)); tint = np.array(tint)
    def add(P, col, inten, streak=False):
        sx, sy, z = cam.proj(P); fog = np.exp(-np.maximum(z, 0) / 900); w = np.where(z > 2, inten * fog, 0.0); splat(acc, sx, sy, w, col)
        if streak and t < 8.9 or streak == 2:
            c0 = Cam(t - 0.04); sx0, sy0, _ = c0.proj(P)
            for j in (0.25, 0.5, 0.75): splat(acc, sx + (sx0 - sx) * j, sy + (sy0 - sy) * j, w * 0.35, col)
        m = (z > 2) & (z < 170) & (w > 0.25)
        if m.any():
            ii = np.nonzero(m)[0]; ii = ii[np.argsort(z[ii])][:160]
            for i in ii:
                if 0 < sx[i] < SW and 0 < sy[i] < SH:
                    r = float(np.clip(1500 / z[i], 2, 14)); cc = (col[i] if np.ndim(col) == 2 else col) * min(w[i], 1.0) * 70
                    nd.ellipse((sx[i] - r, sy[i] - r, sx[i] + r, sy[i] + r), fill=ic(cc))
    # пыль
    if t < T_CUT or t >= T_END:
        if t < T_CUT: add(DUST, np.array([0.62, 0.7, 0.78]), (0.35 + 0.5 * DTW) * (0.7 + 0.3 * np.sin(DTW * 40 + t * 8)) * ease(t / 0.4), streak=2 if t > 5.0 else False)
        else: add(DUST2 + np.array([0, 0, 0]) + np.array([4 * math.sin(t * 0.5), 3 * t % 5 * 0, 0]), np.array([0.62, 0.7, 0.78]), 0.22 * (0.7 + 0.3 * np.sin(DTW[:600] * 40 + t * 3)))
        # облако
    if T_CUT2 <= t < 8.9:
        a = np.clip((t - 7.4 - CRANK * 0.5) / 0.7, 0, 1); a = a * a * (3 - 2 * a); street = people_pos(t)[:3500]
        P = CLOUD * (1 - a[:, None]) + street * a[:, None]; col = np.where(CRED[:, None], RED, np.array([0.75, 0.9, 1.0])); add(P, col, 0.9 * np.where(CRED, 1.1, 1.0), streak=2 if t > 7.3 else False)
        if t < T_FALL + 0.1:
            r = np.random.RandomState(3); pi = r.randint(0, 400, (60, 2))
            for i, j in pi:
                if np.linalg.norm(CLOUD[i] - CLOUD[j]) < 45:
                    sx, sy, z = cam.proj(np.stack([CLOUD[i], CLOUD[j]]))
                    if (z > 1).all(): ld.line((sx[0], sy[0], sx[1], sy[1]), fill=(40, 70, 90), width=1)
    # город
    if t >= T_FALL:
        P = people_pos(t); dt = t - KILL; alive = dt < 0; dying = (dt >= 0) & (dt < 0.3)
        vis = np.clip((t - 7.5) / 0.7, 0, 1) * np.where(np.arange(NP) < 3500, np.clip((t - 7.4 - CRANK[np.minimum(np.arange(NP), 3499)] * 0.5) / 0.7, 0, 1) * 0 + 1, 1)
        m = np.arange(NP) >= 3500; m = m & (alive | dying)
        fl = np.where(dying, 1 - dt / 0.3, 1.0); flash = (dying & (dt < 0.08))[:, None]
        col = np.where(flash, RED, tint) * (0.85 + 0.3 * np.sin(PTW * 30 + t * 4))[:, None]; col = col * np.where(dt > -2, 1, 1)[:, None]
        inten = 0.9 * fl * vis; inten[0] = 0.0
        sel = np.nonzero(m & (inten > 0))[0]
        if t > 15.6: sel = sel[:0]
        if len(sel): add(P[sel], col[sel] if col.ndim == 2 else col, inten[sel] * 2.6, streak=2 if t < 8.9 else False)
        # выживший
        if 14.3 <= t < 15.6:
            a = ease(seg(t, 14.3, 14.8)) * (1 if t < 15.5 else 0.5) * (1 + 0.15 * math.sin(t * 6)); P0 = np.array([[cam.pos[0], 4.0, cam.pos[2] + 300]]); sx, sy, z = cam.proj(P0)
            if 0 < sx[0] < SW and 0 < sy[0] < SH and z[0] > 1: nd.ellipse((sx[0] - 9, sy[0] - 9, sx[0] + 9, sy[0] + 9), fill=ic(np.array([255, 233, 200]) * a))
        # окна
        if t >= 8.6:
            on = (t > WON) & ((t < WOFF - 0.5) | ((t < WOFF) & (np.sin(t * 40 + WX) > 0)))
            ww = np.nonzero(on)[0]
            if len(ww): add(np.stack([WX[ww], WY[ww], WZ[ww]], 1), np.array([255, 210, 138]) / 255, np.full(len(ww), 0.8))
        # рёбра зданий
        ea = 0.14 + 0.5 * ease(seg(t, 15.4, 16.4)) if t >= 8.6 else 0.0
        if ea > 0:
            sel = np.nonzero((BCZ > cam.pos[2] + 25) & (BCZ < cam.pos[2] + 1500))[0]
            if len(sel):
                cs = np.array([[-1, 0, -1], [1, 0, -1], [1, 0, 1], [-1, 0, 1]], float); V = []
                for i in sel:
                    for yy in (0, BHT[i]):
                        for c in cs: V.append([BCX[i] + c[0] * BW[i] / 2, yy, BCZ[i] + c[2] * BD[i] / 2])
                sx, sy, z = cam.proj(np.array(V)); colr = ic((27 * ea * 1.5, 79 * ea * 1.5, 114 * ea * 1.5))
                for k in range(len(sel)):
                    b = k * 8
                    for j in range(4):
                        for a_, b_ in ((b + j, b + (j + 1) % 4), (b + 4 + j, b + 4 + (j + 1) % 4), (b + j, b + 4 + j)):
                            if z[a_] > 1 and z[b_] > 1: ld.line((sx[a_], sy[a_], sx[b_], sy[b_]), fill=colr, width=1)
        # улицы-оранжевые линии
        if t >= 8.6:
            for xl in LANES[::1]:
                P2 = np.array([[xl, 0, cam.pos[2] + 4], [xl, 0, cam.pos[2] + 2500]]); sx, sy, z = cam.proj(P2)
                if (z > 1).all(): ld.line((sx[0], sy[0], sx[1], sy[1]), fill=ic((201 * 0.16, 116 * 0.16, 42 * 0.16)), width=1)
        # красный сканер
        if 9.0 <= t < 15.6:
            k = ease(seg(t, 9.0, 9.6)) * (1 - ease(seg(t, 15.0, 15.6))); xs = np.linspace(-900, 900, 40); ys = 2 * np.sin(xs * 0.01 + t * 3) + 1.2 * np.sin(xs * 0.03 - t * 2)
            sx, sy, z = cam.proj(np.stack([xs, ys, np.full(40, cam.pos[2] + 2400)], 1)); ld.line(list(zip(sx, sy)), fill=ic(np.array([255, 75, 62]) * (0.4 + 0.5 * (1 - cnt / 100)) * k), width=2)
        # слова отмен
        for k, (t0, wd, lg, _) in enumerate(EV):
            if t0 + 0.0 <= t < t0 + 1.6:
                tx, tz, sc, hy = WORDS[k]; a = ease(seg(t, t0 + 0.25, t0 + 0.65)); fall = max(0, t - (t0 + 0.75)); base = np.array([cam.pos[0], 0.0, cam.pos[2]])
                loc = np.stack([sc[:, 0] * (1 - a) + tx * a, hy * (1 - a) - 40 * fall * fall, sc[:, 1] * (1 - a) + tz * a], 1); P = loc + base
                lif = ease(seg(t, t0 + 0.2, t0 + 0.4)) * (1 - ease(seg(t, t0 + 0.9, t0 + 1.4)))
                col = RED * (0.35 if (t0 + 0.65 <= t < t0 + 0.7) else 1.0) if True else RED
                cw = np.array([1.0, 0.9, 0.85]) if t0 + 0.65 <= t < t0 + 0.72 else RED
                add(P, cw, np.full(2200, 1.4 * lif))
                tau = t - (t0 + 0.65)
                if 0 <= tau < 0.8:
                    r = tau * 480; ang = np.linspace(0, 2 * math.pi, 800, endpoint=False); Pr = base + np.stack([np.cos(ang) * r, np.full(800, 0.5), 120 + np.sin(ang) * r], 1)
                    add(Pr, RED, np.full(800, 1.2 * (1 - r / 380 if r < 380 else 0)))
    out = 1 - np.exp(-1.7 * acc); img = np.clip(out.reshape(SH, SW, 3) * 255, 0, 255)
    img += np.asarray(lines, np.float32) * 0.9 + np.asarray(near.filter(ImageFilter.GaussianBlur(1.5)), np.float32)
    return np.clip(img, 0, 255).astype(np.uint8)

# ---------------- 3D-текст и слои
def quad_warp(src, dst, size):
    A = []; B = []; w, h = src.size
    for (x, y), (u, v) in zip(dst, ((0, 0), (w, 0), (w, h), (0, h))):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    c = np.linalg.solve(np.array(A, float), np.array(B, float)); return src.transform(size, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
def wide(text, size, fill, stretch=1.3, weight="Black"):
    f = ImageFont.truetype(INTER.format(weight), size); bb = f.getbbox(text); w, h = bb[2] + 24, int(size * 1.35)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).text((12, 0), text, font=f, fill=fill); return im.resize((int(w * stretch), h), Image.BICUBIC)
def put(layer, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0, blur=0.0):
    if alpha <= 0.003: return
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if blur > 0.3: im = im.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    layer.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def plate_img(t):
    im = Image.new("RGBA", (960, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, 959, 459), 14, fill=(10, 16, 26, 160), outline=(60, 80, 104, 255), width=2)
    d.text((40, 30), "новый запрос · 07:58", font=font("m", "Regular", 32), fill=(138, 151, 166, 255))
    n = int((CT <= t).sum()); fn = font("m", "Medium", 82); y = 100
    for li, ln in enumerate(LINES):
        part = REQ[CUM[li]:CUM[li] + len(ln)] if n > CUM[li] else ""; d.text((90, y), part[:max(0, n - CUM[li])], font=fn, fill=(232, 238, 245, 255)); y += 112
    last = n - 1; cur = 0 if n <= 18 else 1 if n <= 27 else 2; part = REQ[CUM[cur]:n] if n > CUM[cur] else ""
    if n < len(REQ) or int(t * 2.2) % 2 == 0:
        wc = d.textlength(part, font=fn); d.rectangle((90 + wc + 6, 100 + 112 * cur + 10, 90 + wc + 36, 100 + 112 * cur + 90), fill=(191, 239, 255, 255))
    d.text((44, 100), "›", font=font("m", "Bold", 82), fill=(92, 200, 255, 255)) if False else None
    return im

def frame(t):
    cam = Cam(min(t, T_CUT - 1e-3)) if T_CUT <= t < T_CUT2 else Cam(t)
    if T_CUT <= t < T_CUT2: return np.zeros((H, W, 3), np.uint8)
    base = world(t, cam); F = np.asarray(Image.fromarray(base).resize((W, H), Image.BICUBIC), np.float32) + np.array([2, 4, 10], np.float32)
    # дым красный сверху
    cnt = counter(t)
    if 9.2 <= t < 15.7:
        k = 0.5 * (1 - cnt / 100) * ease(seg(t, 9.2, 10)) * (1 - ease(seg(t, 15.0, 15.7))); gy = np.clip(1 - np.arange(H) / (H * 0.45), 0, 1)[:, None] ** 1.5; F += gy[:, :, None] * np.array([58, 13, 8]) * k * 2.2
    if t >= 22:
        k = ease(seg(t, 22, 26)); blur = np.asarray(Image.fromarray(np.clip(F, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * k)), np.float32); my = np.clip((np.arange(H) / H - 0.38) / 0.2, 0, 1)[:, None, None]
        F = F * (1 - my) + blur * my
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fl = cam.fl * 2
    def P3(p): sx, sy, z = cam.proj(np.array([p], float)); return sx[0] * 2, sy[0] * 2, z[0]
    glitch = 0.0; chroma = 1.5; shake = 0.9 * math.sin(t * 7.3); hit_amp = 0.0; red_v = 0.0
    # --- A/B: плашка в 3D
    if t < T_CUT:
        a = math.radians(-9); p = math.radians(4); Rx = np.array([math.cos(a), 0, -math.sin(a)]); Ry = np.array([0, math.cos(p), math.sin(p)]); C0 = np.array([0.0, 10.0, 520.0])
        dst = []
        for lx, ly in ((-100, 48), (100, 48), (100, -48), (-100, -48)):
            q = C0 + lx * Rx + ly * Ry; sx, sy, z = P3(q); dst.append((sx, sy))
        al = ease(seg(t, 0.2, 0.8)) * (1 - ease(seg(t, 5.55, 5.84))) if t < 5.0 else 1.0
        wp = quad_warp(plate_img(t), dst, (W, H))
        if al < 1: wp.putalpha(wp.getchannel("A").point(lambda v: int(v * al)))
        tl.alpha_composite(wp)
        if 5.0 <= t < T_CUT:
            k = seg(t, 5.0, T_CUT); glitch = k; chroma = 1.5 + 12.5 * k; shake += 6 * k * math.sin(t * 90)
            r = np.random.RandomState(int(t * FPS) // 2 + 5)
            for _ in range(14):
                tl.alpha_composite(Image.new("RGBA", (1, 1)), (0, 0)); d = ImageDraw.Draw(tl)
                d.text((int(r.uniform(40, 900)), int(r.uniform(300, 1600))), f"{r.randint(1000, 999999):,}".replace(",", " "), font=font("m", "Regular", 26), fill=(150, 200, 240, int(200 * k)))
    # --- B: «понял»
    if T_CUT2 <= t < 7.7:
        al = 1 - ease(seg(t, 7.3, 7.65)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); word = "понял"; x0 = 540 - 300
        f150 = ImageFont.truetype(INTER.format("Black"), 150); adv = [f150.getlength(c) * 1.3 for c in word]; tot = sum(adv); xx = 540 - tot / 2
        for i, c in enumerate(word):
            ti = T_CUT2 + 0.15 + i * 0.12; k = ease(seg(t, ti, ti + 0.25)); put(lay, wide(c, 150, (232, 238, 245, 255)), xx + adv[i] / 2 + (1 - k) * 160, 1150, alpha=k, blur=(1 - k) * 12)
            xx += adv[i]
        lay = lay.rotate(-3, resample=Image.BICUBIC, center=(540, 1150)); ImageDraw.Draw(lay)
        kk = ease(seg(t, T_CUT2 + 0.65, T_CUT2 + 0.95)); d = ImageDraw.Draw(lay); d.rectangle((540 - tot / 2, 1250, 540 - tot / 2 + tot * kk, 1256), fill=(255, 75, 62, 255))
        kt = seg(t, 6.5, 6.9); txt = "цель: опоздания →"[:int(kt * 17)]; d.text((540 - tot / 2, 1290), txt, font=font("m", "Regular", 36), fill=(255, 75, 62, 255))
        if al < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * al)))
        tl.alpha_composite(lay)
    # --- отмены: стикеры, удары
    for k, (t0, wd, lg, _) in enumerate(EV):
        th = t0 + 0.65
        if th <= t < th + 0.3: hit_amp = max(hit_amp, 9 * math.exp(-(t - th) / 0.1)); red_v = max(red_v, 0.12 * (1 - (t - th) / 0.3)); chroma = max(chroma, 12 * math.exp(-(t - th) / 0.08)); glitch = max(glitch, 0.5 if t - th < 0.12 else 0)
        if t0 + 0.75 <= t < t0 + 1.35:
            tt = t - (t0 + 0.75); al = ease(tt / 0.1) * (1 - ease((tt - 0.4) / 0.2)); label = "РАСПИСАНИЕ УДАЛЕНО" if k == 5 else "ОТМЕНЕНО"
            st = wide(label, 70 if k == 5 else 84, (255, 75, 62, 255)); bx = Image.new("RGBA", (st.width + 70, st.height + 20), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
            bd.rectangle((0, 0, bx.width - 1, bx.height - 1), fill=(30, 6, 5, 190), outline=(255, 75, 62, 255), width=4); bx.alpha_composite(st, (35, 6))
            put(tl, bx, 540, 900, scale=1.4 - 0.4 * ease(tt / 0.12), rot=4, alpha=al)
    # --- часы
    if T_CLOCK <= t < 26.5:
        sx, sy, z = P3(np.array([0.0, 150.0, 2100.0])); R = float(220 * fl / z); sx, sy = float(sx), float(sy); a = ease(seg(t, T_CLOCK, T_CLOCK + 0.5))
        if -R < sy < H + R:
            q = eo5(seg(t, T_CLOCK, T_SPIN_END)); tau = max(0, t - T_SPIN_END); spring = 9 * math.exp(-tau / 0.1) * math.cos(2 * math.pi * tau / 0.25) if tau > 0 else 0
            mn = 348 - 2160 * (1 - q) + spring; hr = 7 * 30 + 29 - 180 * (1 - q) + spring / 12
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); aa = int(255 * a)
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((sx - R * 1.9, sy - R * 1.9, sx + R * 1.9, sy + R * 1.9), fill=(40, 120, 190, int(60 * a)))
            lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(R * 0.5)))
            d.ellipse((sx - R, sy - R, sx + R, sy + R), fill=(2, 8, 18, int(210 * a)), outline=(191, 239, 255, aa), width=max(3, int(R * 0.03)))
            for i in range(60):
                an = math.radians(i * 6); big = i % 5 == 0; r1 = R * (0.84 if big else 0.92)
                d.line((sx + math.sin(an) * r1, sy - math.cos(an) * r1, sx + math.sin(an) * R * 0.97, sy - math.cos(an) * R * 0.97), fill=(191, 239, 255, aa), width=max(2, int(R * (0.03 if big else 0.015))))
            st = t >= T_SPIN_END and t < T_SPIN_END + 0.5; hc = (255, 75, 62, aa) if st else (232, 238, 245, aa)
            for ang, ln, wd in ((hr, 0.52, 0.06), (mn, 0.8, 0.035)):
                r = math.radians(ang); d.line((sx, sy, sx + math.sin(r) * R * ln, sy - math.cos(r) * R * ln), fill=hc, width=max(3, int(R * wd)))
            d.ellipse((sx - R * 0.06, sy - R * 0.06, sx + R * 0.06, sy + R * 0.06), fill=hc)
            tl.alpha_composite(lay)
            if t >= T_SPIN_END:
                b = ease(seg(t, T_SPIN_END, T_SPIN_END + 0.3)); dg = Image.new("RGBA", (700, 200), (0, 0, 0, 0)); ImageDraw.Draw(dg).text((350, 100), "07:58", font=font("m", "Bold", 150), fill=(232, 238, 245, 255), anchor="mm")
                am = np.array(dg); am[::4, :, 3] = (am[::4, :, 3] * 0.45).astype(np.uint8); put(tl, Image.fromarray(am), sx, sy + R + 140, alpha=b * a)
            if T_SPIN_END <= t < T_SPIN_END + 0.5:
                rr = (t - T_SPIN_END) / 0.5 * 300; ImageDraw.Draw(tl).ellipse((sx - R - rr, sy - R - rr, sx + R + rr, sy + R + rr), outline=(92, 200, 255, int(160 * (1 - (t - T_SPIN_END) / 0.5))), width=4)
        if T_SPIN_END <= t < T_SPIN_END + 0.3: hit_amp = max(hit_amp, 4)
    # --- дуга атмосферы
    if t >= 22:
        k = ease(seg(t, 22, 25)) * (1 - ease(seg(t, 32.6, T_END))); gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((540 - 2400, 160, 540 + 2400, 160 + 4800), outline=(47, 143, 216, int(200 * k)), width=8)
        tl.alpha_composite(gl); tl.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)))
    # --- ЗАДАЧА ВЫПОЛНЕНА
    if T_DONE <= t < T_END:
        tt = t - T_DONE; al = ease(tt / 0.2); sl = 300 * (1 - eo5(tt / 0.35)); gh = 1 - ease(tt / 0.3)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, wd in enumerate(("ЗАДАЧА", "ВЫПОЛНЕНА")):
            im = wide(wd, 96, (232, 238, 245, 255)); put(lay, im, 540 - sl, 940 + i * 130)
        gst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, wd in enumerate(("ЗАДАЧА", "ВЫПОЛНЕНА")): put(gst, wide(wd, 96, (180, 220, 255, 255)), 540 + 70 * gh, 940 + i * 130 + 18 * gh, alpha=0.45)
        tl.alpha_composite(gst); tl.alpha_composite(lay); ImageDraw.Draw(tl).rectangle((540 - 360 * ease(tt / 0.3), 1170, 540 + 360 * ease(tt / 0.3), 1176), fill=(92, 200, 255, 255))
        if tt < 0.4: chroma = max(chroma, 6 * (1 - tt / 0.4)); hit_amp = max(hit_amp, 3 * (1 - tt / 0.4)); glitch = max(glitch, 0.4 if tt < 0.2 else 0)
        tl.putalpha(tl.getchannel("A").point(lambda v: int(v * al)))
    # --- призыв
    if t >= T_CARD:
        for i, wd in enumerate(("Отправь тому,", "кто вечно", "опаздывает")):
            ti = T_CARD + 0.1 + i * 0.4; k = ease(seg(t, ti, ti + 0.25)); put(tl, wide(wd, 92, (232, 238, 245, 255), 1.0, "Bold"), 540, 760 + i * 130 + 40 * (1 - k), alpha=k, blur=14 * (1 - k))
        ti = 35.2; k = seg(t, ti, 36.6)
        if k > 0:
            sp = 0.7 + 0.3 * (1 - math.exp(-6 * k) * math.cos(10 * k)); pill = Image.new("RGBA", (560, 140), (0, 0, 0, 0)); pd_ = ImageDraw.Draw(pill)
            pd_.rounded_rectangle((0, 0, 559, 139), 70, fill=(92, 200, 255, 255)); pd_.text((280, 70), "Подпишись", font=font("i", "Bold", 62), fill=(2, 4, 10, 255), anchor="mm"); put(tl, pill, 540, 1180, scale=sp, alpha=min(1, k * 4))
        if t >= 37.6 and int(t * 2.2) % 2 == 0: ImageDraw.Draw(tl).rectangle((528, 1440, 552, 1480), fill=(191, 239, 255, 255))
    # --- сборка: слой текста → кадр
    a = np.asarray(tl, np.float32); F = F * (1 - a[:, :, 3:4] / 255) + a[:, :, :3] * (a[:, :, 3:4] / 255)
    if 5.0 <= t < T_CUT:                                           # радиальное размытие наезда
        k = seg(t, 5.0, T_CUT); img = Image.fromarray(np.clip(F, 0, 255).astype(np.uint8)); acc = np.zeros_like(F)
        for j in range(7):
            s = 1 + 0.05 * k * j / 6 * 2; w2, h2 = int(W * s), int(H * s); im2 = img.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H)); acc += np.asarray(im2, np.float32)
        F = acc / 7
    # bloom
    thr = np.clip(F / 255 - 0.5, 0, 1); sm = Image.fromarray((thr * 255).astype(np.uint8)).resize((270, 480), Image.BILINEAR)
    bl = sum(np.asarray(sm.filter(ImageFilter.GaussianBlur(s)).resize((W, H), Image.BILINEAR), np.float32) * w for s, w in ((2, 0.55), (6, 0.5), (18, 0.45)))
    F = F + bl * (1.6 if 5.0 <= t < T_CUT else 1.0)
    F = np.clip(F, 0, 255)
    # хроматика, тряска, глитч
    ch = int(round(chroma)); 
    if ch > 0: F = F.copy(); F[:, :, 0] = np.roll(F[:, :, 0], ch, 1); F[:, :, 2] = np.roll(F[:, :, 2], -ch, 1)
    sh = int(round(shake + hit_amp * math.cos(t * 120))); sv = int(round(0.6 * shake + hit_amp * math.sin(t * 97)))
    if sh or sv: F = np.roll(F, (sv, sh), (0, 1))
    r = np.random.RandomState(int(t * FPS) // 2 + 3)
    if glitch > 0:
        for _ in range(int(8 * glitch) + 1): y0 = r.randint(250, 1650); hh = r.randint(20, 90); F[y0:y0 + hh] = np.roll(F[y0:y0 + hh], r.randint(-40, 40), 1)
    yy, xx = np.mgrid[0:H, 0:W]; vg = 1 - 0.55 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) * 0.5; vg = np.clip(vg, 0.35, 1)
    F = F * vg[:, :, None] + np.array([255, 20, 10]) * red_v * (1 - vg)[:, :, None]
    F = np.clip(F, 0, 255)
    # --- HUD (чёткий, после тряски)
    im = Image.fromarray(F.astype(np.uint8)); 
    if T_GLASS <= t < T_END + 0.5:
        a = ease(seg(t, T_GLASS, T_GLASS + 0.5)) * (1 - ease(seg(t, 32.6, T_END))); bx = (70, 420, 1010, 750); crop = im.crop(bx).filter(ImageFilter.GaussianBlur(14)); ov = Image.new("RGB", crop.size, (8, 18, 32))
        crop = Image.blend(crop, ov, 0.55); crop = Image.blend(im.crop(bx), crop, a); im.paste(crop, bx[:2])
        d = ImageDraw.Draw(im); col = lambda c: ic(np.array(c) * a)
        d.rectangle(bx, outline=col((60, 80, 104)), width=2); d.text((100, 440), "› Сделай так, чтобы никто не опаздывал.", font=font("m", "Regular", 24), fill=col((138, 151, 166)))
        y = 500
        for i, (s, ts) in enumerate(REPLY):
            if t >= ts:
                n = int(min(len(s), (t - ts) / 0.05)); pre = "• " if i == 0 else "  "; ff = font("m", "Medium", 38); d.text((100, y), pre + s[:n], font=ff, fill=col((232, 238, 245) if i < 3 else (191, 239, 255)))
                if (i == len(REPLY) - 1 or n < len(s)) and (n < len(s) or int(t * 2.2) % 2 == 0):
                    wc = d.textlength(pre + s[:n], font=ff); d.rectangle((100 + wc + 4, y + 2, 100 + wc + 24, y + 46), fill=col((191, 239, 255)))
            y += 58
    d = ImageDraw.Draw(im)
    if t < T_END: d.text((70, 262), "ВЫМЫШЛЕННЫЙ СЦЕНАРИЙ", font=font("m", "Regular", 22), fill=(110, 124, 142))
    if T_CRUISE <= t < 17.6:                                      # счётчик
        a = ease(seg(t, 8.6, 9.2)) * (1 - ease(seg(t, 16.6, 17.5))); dy = -120 * ease(seg(t, 15.6, 17.4)); cv = counter(t)
        col = mixc((232, 238, 245), (255, 75, 62), min(1, (1 - cv / 100) ** 0.6 * 1.3)) if t < 15.6 else (191, 239, 255)
        jit = 3 if any(0 <= t - (e[0] + 0.65) < 0.15 for e in EV) else 0
        x0, y0 = 60 + jit, 300 + dy; bx = (x0, y0, x0 + 520, y0 + 160); cc = ic(np.array((92, 200, 255)) * a * 0.6); L = 20
        for (xa, ya, sx_, sy_) in ((bx[0], bx[1], 1, 1), (bx[2], bx[1], -1, 1), (bx[0], bx[3], 1, -1), (bx[2], bx[3], -1, -1)): d.line((xa, ya, xa + sx_ * L, ya), fill=cc, width=3); d.line((xa, ya, xa, ya + sy_ * L), fill=cc, width=3)
        d.text((x0 + 22, y0 + 18), "ЦЕЛЬ · ОПОЗДАНИЯ", font=font("m", "Regular", 24), fill=ic(np.array((138, 151, 166)) * a))
        s = f"{cv:.2f}".replace(".", ",") + " %"
        if t < 9.2:
            s = "100,00 %"; xx = x0 + 22
            for i, chh in enumerate(s):
                k = ease(seg(t, 8.8 + i * 0.05, 8.8 + i * 0.05 + 0.2)); d.text((xx, y0 + 60 - 30 * (1 - k)), chh, font=font("m", "Bold", 76), fill=ic(np.array(col) * k * a)); xx += 46
        else: d.text((x0 + 22, y0 + 60), s, font=font("m", "Bold", 76), fill=ic(np.array(col) * a))
    if 8.8 <= t < 15.7:                                           # лог
        a = 1 - ease(seg(t, 15.3, 15.7)); shown = [l for l in LOG0 if t >= l[1]][-5:]; y = 1480
        for s, ts, red in shown:
            n = int(min(len(s), (t - ts) / 0.025)); d.text((70, y), s[:n], font=font("m", "Regular", 27), fill=ic(np.array((255, 110, 100) if red else (138, 151, 166)) * a)); y += 36
    # затухание и зерно
    F = np.asarray(im, np.float32); g = 1.0
    if t < 0.4: g = ease(t / 0.4)
    if 32.6 <= t < T_END: g = min(g, 1 - 0.9 * ease(seg(t, 32.6, T_END)))
    F = F * g + np.random.RandomState(int(t * FPS) % 8).randn(H, W, 1) * 5.0
    return np.clip(F, 0, 255).astype(np.uint8)

# ---------------- звук
def audio():
    n = int(DUR * SR); a = np.zeros(n, np.float32); tt = np.arange(n) / SR; r = np.random.RandomState(11)
    def add(t0, x, g=1.0):
        i = int(t0 * SR); x = x[:max(0, n - i)]; a[i:i + len(x)] += x * g
    def env(m, atk, dec): return (np.minimum(np.arange(m) / (atk * SR + 1), 1) * np.exp(-np.arange(m) / (dec * SR))).astype(np.float32)
    def click(g=1.0, f=2200): m = int(0.03 * SR); return (r.randn(m) * 0.6 + np.sin(2 * np.pi * f * np.arange(m) / SR)) * env(m, 0.0005, 0.006) * g
    def tone(f, d, g=1.0, atk=0.01, dec=None): m = int(d * SR); return np.sin(2 * np.pi * f * np.arange(m) / SR) * env(m, atk, dec or d / 3) * g
    lv = np.interp(tt, [0, 4, 5.85, 6, 15, 15.4, 26, 33, 38], [0.0, 0.10, 0.2, 0.12, 0.30, 0.08, 0.10, 0.12, 0.0])
    a += ((np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 82.4 * tt + np.sin(tt * 0.4)) + 0.3 * np.sin(2 * np.pi * 110.5 * tt)) * (0.7 + 0.3 * np.sin(tt * 0.9)) * lv * 0.35).astype(np.float32)
    for c in CT: add(float(c), click(0.35, 1800 + int(r.randint(0, 3)) * 300))
    m = int(0.85 * SR); sw = np.cumsum(np.linspace(300, 4000, m)) / SR; add(5.0, (np.sin(2 * np.pi * sw) * 0.25 + r.randn(m) * 0.2) * np.linspace(0, 1, m) ** 2 * 0.8)
    add(T_CUT, tone(55, 0.35, 1.2, 0.002, 0.12)); add(T_CUT2, tone(55, 0.25, 0.8, 0.002, 0.1))
    for i in range(5): add(T_CUT2 + 0.15 + i * 0.12, tone(600, 0.1, 0.25, 0.002, 0.03))
    m = int(1.25 * SR); sw = np.cumsum(np.linspace(4000, 200, m)) / SR; add(T_FALL, (np.sin(2 * np.pi * sw) * 0.22 + r.randn(m) * 0.15) * np.sin(np.linspace(0, math.pi, m)) * 0.8)
    add(8.55, (r.randn(int(0.4 * SR)) * env(int(0.4 * SR), 0.15, 0.2) * 0.25).astype(np.float32))
    for s, ts, _ in LOG0:
        for i in range(len(s)): add(ts + i * 0.025, click(0.18, 2400))
    tc = 9.2
    while tc < 15.2: add(tc, click(0.1, 3200), 1.0); tc += 1 / 14
    for t0, *_ in EV: add(t0 + 0.65, tone(55, 0.7, 1.1, 0.002, 0.18)); add(t0 + 0.65, click(0.6, 900)); add(t0 + 0.65, (r.randn(int(0.35 * SR)) * env(int(0.35 * SR), 0.001, 0.07) * 0.3).astype(np.float32))
    add(15.0, tone(38, 2.5, 1.0, 0.003, 0.7)); add(15.0, tone(1200, 0.8, 0.15, 0.01, 0.4)); add(15.6, click(1.2, 700))
    tc = 16.2
    while tc < T_SPIN_END: p = seg(tc, 16.4, T_SPIN_END); add(tc, click(0.3, 1500)); tc += 1.0 / (1 + 17 * (1 - p) ** 1.5) if p < 1 else 1
    add(T_SPIN_END, tone(60, 1.2, 1.0, 0.003, 0.35)); [add(T_SPIN_END, tone(f, 2.0, 0.18, 0.003, 0.6)) for f in (523, 784, 1568)]
    for f, g in ((220, 0.2), (261.6, 0.16), (329.6, 0.14)):
        m = int(4.0 * SR); add(22.0, np.sin(2 * np.pi * f * np.arange(m) / SR) * np.sin(np.linspace(0, math.pi, m)) * g * 0.7)
    for s, ts in REPLY:
        for i in range(len(s)): add(ts + i * 0.05, click(0.25, 2000))
    for f, g in ((440, 0.3), (554.4, 0.24), (659.3, 0.22), (880, 0.14)): add(T_DONE, tone(f, 2.4, g, 0.005, 0.9))
    add(T_DONE, tone(48, 1.5, 0.8, 0.003, 0.5)); add(35.2, tone(1046, 0.8, 0.2, 0.003, 0.25))
    a *= np.minimum(1, (DUR - tt) / 1.5).astype(np.float32); a = np.tanh(a * 1.3) * 0.8; st = np.stack([a, a], 1); fn = f"{WK}/audio.wav"
    with wave.open(fn, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())
    return fn

def job(i):
    Image.fromarray(frame(i / FPS)).save(f"{WK}/f_{i:05d}.png", compress_level=1); return i

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import time
        for s in sys.argv[1:]:
            t0 = time.time(); Image.fromarray(frame(float(s))).save(f"{WK}/pv_{float(s):05.2f}.png"); print(s, round(time.time() - t0, 2), flush=True)
        sys.exit()
    wav = audio(); nf = int(DUR * FPS)
    with Pool(4) as p:
        for k, _ in enumerate(p.imap_unordered(job, range(nf))):
            if k % 100 == 0: print(k, flush=True)
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-framerate", str(FPS), "-i", f"{WK}/f_%05d.png", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"{NAME}.mp4"], check=True)
    subprocess.run(f"rm -f {WK}/f_*.png", shell=True); print("END")
