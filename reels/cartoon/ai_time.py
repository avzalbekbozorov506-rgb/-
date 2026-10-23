"""«Создай машину времени» — ИИ исполняет приказ буквально, с озвучкой. По scripts/ai_time_1_visual.md (Avzaldoc), техника ai_late2.py (3D-камера, точки, bloom).
Голос: cartoon/ai_time_voice.py → work/ai_time_1/v_NN.wav. Запуск: python3 cartoon/ai_time.py → ai_time_1.mp4;  python3 cartoon/ai_time.py 1.0 5.5 … → превью."""
import os, sys, json, math, subprocess, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.interpolate import PchipInterpolator
from scipy.io import wavfile
from multiprocessing import Pool
import ai_late2 as L
from ai_late2 import ease, eo5, seg, mixc, ic, font, INTER, MONO, splat, quad_warp, wide, put, basis, W, H, SW, SH, FPS, SR
NAME = "ai_time_1"; WK = f"work/{NAME}"; os.makedirs(WK, exist_ok=True)

# ---------------- фразы, тайминги, слова
PH = ["Создай машину времени.", "Нейросеть не спорит. Она проверяет физику.", "Назад — способа никто не нашёл.", "Вперёд — всё проверено.",
      "В тысяча девятьсот семьдесят первом атомные часы облетели Землю на обычных самолётах. И вернулись с другим временем.",
      "Сергей Крикалёв провёл на орбите восемьсот три дня. И улетел в будущее примерно на две сотых доли секунды.",
      "Спутники навигации делают это каждые сутки. Их часы уходят вперёд на тридцать восемь миллионных долей секунды. Без поправки навигатор ошибался бы на километры.",
      "Нейросеть делает вывод.", "Готово. Машина времени уже работает.", "Она едет вперёд. Одна секунда за секунду.", "Пассажир — ты. Остановки нет.",
      "Вернуться нельзя. Зато можно успеть.", "Отправь тому, кто мечтает вернуться в прошлое. Подпишись."]
MINS = [2.1, 3.0, 2.4, 1.9, 7.0, 7.4, 9.8, 1.6, 2.6, 3.2, 2.4, 2.4, 3.6]
VOXD = json.load(open(f"{WK}/durations.json")); VO = 0.05
D = [max(VOXD[str(i + 1)] + 0.35, MINS[i]) for i in range(13)]; S = [0.0]
for d_ in D[:-1]: S.append(S[-1] + d_)
TOTAL = S[-1] + D[-1]
def s(n): return S[n - 1]
def words(n): return [w.strip(".,!?") for w in PH[n - 1].split() if w != "—"]
def word_times(n):
    sr, a = wavfile.read(f"{WK}/v_{n:02d}.wav"); a = a.astype(np.float32); a = a.mean(1) if a.ndim > 1 else a; a = np.abs(a) / (np.abs(a).max() + 1e-6)
    hop = int(sr * 0.01); env = np.convolve(a[:len(a) // hop * hop].reshape(-1, hop).max(1), np.ones(5) / 5, "same"); on = env > 0.06
    segs = []; i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and (on[j] or (on[j:j + 40].any())): j += 1
            segs.append([i * 0.01, j * 0.01]); i = j
        else: i += 1
    sents = [x for x in __import__("re").split(r"(?<=[.!?])\s+", PH[n - 1]) if x.strip()]; ws = words(n); out = []
    if len(segs) != len(sents): segs = [[segs[0][0], segs[-1][1]]]; sents = [PH[n - 1]]
    for sg, st in zip(segs, sents):
        wl = [w.strip(".,!?") for w in st.split() if w != "—"]; ch = np.array([len(w) + 2 for w in wl], float); cum = np.concatenate([[0], np.cumsum(ch)]) / ch.sum()
        for k in range(len(wl)): out.append((sg[0] + (sg[1] - sg[0]) * cum[k], sg[0] + (sg[1] - sg[0]) * cum[k + 1]))
    return out
_WT = None
def WT():
    global _WT
    if _WT is None:
        fn = f"{WK}/words.json"
        if os.path.exists(fn): _WT = {int(k): v for k, v in json.load(open(fn)).items()}
        else: _WT = {n: word_times(n) for n in range(1, 14)}; json.dump(_WT, open(fn, "w"))
    return _WT
def ev(n, k, lead=0.06): return s(n) + VO + WT()[n][k - 1][0] - lead
def evend(n, k): return s(n) + VO + WT()[n][k - 1][1]
def phase(t):
    for n in range(13, 0, -1):
        if t >= S[n - 1]: return n
    return 1

# ---------------- камера
G = np.array([0.0, -20.0, 4200.0]); RG = 300.0; CCL = np.array([0.0, 24.0, 0.0]); TC = np.array([0.0, 10.0, 520.0])
def look(pos, tg): f = np.asarray(tg, float) - pos; f = f / np.linalg.norm(f); return math.degrees(math.atan2(f[0], f[2])), math.degrees(math.asin(f[1]))
def orbit(c, dist, yaw, elev, fov, roll=0.0):
    y, e = math.radians(yaw), math.radians(elev); pos = np.asarray(c, float) + dist * np.array([math.sin(y) * math.cos(e), math.sin(e), -math.cos(y) * math.cos(e)]); yw, pt = look(pos, c); return (pos, yw, pt, roll, fov)
def key(t, p): return (t, *p)
def build_segments():
    t_b = s(2) + 1.33; tdive = s(2) + D[1] - 1.1; tfl = ev(7, 2, 0.0); t8 = s(8) + 0.6
    K2 = [key(t_b, orbit(CL_, 230, 40, 6, 50)), key(tdive, orbit(CL_, 230, 95, 6, 50)), key(tdive + 0.55, ((150, 300, 150), 60, -62, 4, 70)), key(s(3), ((0, 10, 500), 0, -3, 0, 62)),
          key(s(3) + 0.5 * D[2], ((0, 0, 900), 0, 0, 2, 62)), key(s(4), ((0, 0, 1400), 0, 0, -2, 66)), key(s(4) + 0.6 * D[3], ((0, 0, 2300), 0, 0, 0, 72)),
          key(s(5), orbit(G, 1200, -40, 8, 50)), key(s(5) + 0.5 * D[4], orbit(G, 1100, -5, 8, 50)), key(s(6), orbit(G, 1000, 30, 8, 50)),
          key(s(6) + 0.4 * D[5], orbit(G, 1700, 45, 14, 46)), key(s(7), orbit(G, 1300, 62, 14, 40)), key(tfl, orbit(G, 650, 70, 10, 70))]
    K3 = [key(tfl, ((0, 60, 50), 0, -12, 0, 70)), key(ev(7, 8), ((0, 60, 350), 8, -12, 3, 70)), key(ev(7, 16), ((0, 90, 700), -8, -15, -3, 70)), key(ev(7, 17), ((0, 120, 900), 0, -15, 0, 70)),
          key(ev(7, 19), ((0, 300, 1090), 0, -88, 0, 56)), key(t8, ((0, 300, 1095), 0, -88, 0, 62))]
    K4 = [key(t8, ((0, 0, 0), 0, 0, 0, 50)), key(s(10), ((0, 8, -20), 0, 0, 0, 48)), key(s(11), orbit(TC, 520, 0, 0, 48)),
          key(s(12), orbit(TC, 520, -12, 0, 48)), key(s(12) + D[11], orbit(TC, 720, -12, 0, 50))]
    def mk(K):
        ts = [k[0] for k in K]; V = np.array([[*np.asarray(k[1], float), k[2], k[3], k[4], k[5]] for k in K]); f = PchipInterpolator(ts, V, axis=0); return ts[0], ts[-1], f
    return [mk(K2), mk(K3), mk(K4)], t_b, tfl, t8
CL_ = L.CL
SEGS, T_B, T_FL, T_8 = build_segments()
def pose(t):
    if t < T_B:
        sp = seg(t, s(2), s(2) + 1.25) ** 3; z = 12 * min(t, s(2)) + 440 * sp; return np.array([0.0, 0.0, z]), -3 + 5 * seg(t, 0, s(2)), 0.0, -3 + 8 * sp, 50 - 3 * seg(t, 0, s(2)) + 21 * sp
    if t >= s(13): return np.array([0.0, 0.0, 0.0]), 0.0, 0.0, 0.0, 50.0
    for t0, t1, f in SEGS:
        if t0 <= t <= t1 + 1e-6: v = f(t); return v[:3], float(v[3]), float(v[4]), float(v[5]), float(v[6])
    if t < SEGS[0][0]: v = SEGS[0][2](SEGS[0][0])
    else: v = SEGS[2][2](min(t, SEGS[2][1]))
    return v[:3], float(v[3]), float(v[4]), float(v[5]), float(v[6])
class Cam:
    def __init__(c, t): c.pos, yaw, pitch, roll, c.fov = pose(t); c.f, c.r, c.u = basis(yaw, pitch, roll); c.fl = (SH / 2) / math.tan(math.radians(c.fov) / 2)
    def proj(c, P):
        pc = np.asarray(P, float) - c.pos; z = pc @ c.f; return SW / 2 + c.fl * (pc @ c.r) / np.maximum(z, 1e-3), SH / 2 - c.fl * (pc @ c.u) / np.maximum(z, 1e-3), z

# ---------------- накопитель мира
class Acc:
    def __init__(a, cam): a.cam = cam; a.acc = np.zeros((SW * SH, 3), np.float32); a.lines = Image.new("RGB", (SW, SH)); a.ld = ImageDraw.Draw(a.lines); a.near = Image.new("RGB", (SW, SH)); a.nd = ImageDraw.Draw(a.near)
    def pts(a, P, col, inten, fog=900.0, boke=True):
        sx, sy, z = a.cam.proj(P); w = np.where(z > 2, inten * np.exp(-np.maximum(z, 0) / fog), 0.0); splat(a.acc, sx, sy, w, np.asarray(col, np.float32))
        if boke:
            m = (z > 2) & (z < 170) & (w > 0.25)
            if m.any():
                ii = np.nonzero(m)[0]; ii = ii[np.argsort(z[ii])][:120]
                for i in ii:
                    if 0 < sx[i] < SW and 0 < sy[i] < SH:
                        r = float(np.clip(1500 / z[i], 2, 14)); cc = (col[i] if np.ndim(col) == 2 else np.asarray(col)) * min(w[i], 1.0) * 70; a.nd.ellipse((sx[i] - r, sy[i] - r, sx[i] + r, sy[i] + r), fill=ic(cc))
    def disc(a, p, col, r=5.0, k=1.0):
        sx, sy, z = a.cam.proj(np.array([p], float))
        if z[0] > 1 and 0 < sx[0] < SW and 0 < sy[0] < SH: a.nd.ellipse((sx[0] - r, sy[0] - r, sx[0] + r, sy[0] + r), fill=ic(np.array(col) * 255 * k))
    def line(a, p0, p1, col, width=1):
        sx, sy, z = a.cam.proj(np.array([p0, p1], float))
        if (z > 1).all(): a.ld.line((sx[0], sy[0], sx[1], sy[1]), fill=ic(col), width=width)
    def poly(a, P, col, width=1):
        sx, sy, z = a.cam.proj(P); ok = z > 1
        for i in range(len(P) - 1):
            if ok[i] and ok[i + 1]: a.ld.line((sx[i], sy[i], sx[i + 1], sy[i + 1]), fill=ic(col), width=width)
    def out(a, glow=None):
        img = np.clip((1 - np.exp(-1.7 * a.acc)).reshape(SH, SW, 3) * 255, 0, 255)
        img += np.asarray(a.lines, np.float32) * 0.9 + np.asarray(a.near.filter(ImageFilter.GaussianBlur(1.5)), np.float32)
        return np.clip(img, 0, 255).astype(np.uint8)

# ---------------- мир: данные (RandomState 21)
R = np.random.RandomState(21)
BLU, CYA, WHT, AMB, REDC = np.array([0.18, 0.56, 0.85]), np.array([0.36, 0.78, 1.0]), np.array([0.75, 0.9, 1.0]), np.array([1.0, 0.76, 0.48]), np.array([1.0, 0.29, 0.24])
NC = 1800; CC = np.stack([R.uniform(-500, 500, NC), R.uniform(-350, 350, NC), R.uniform(700, 3200, NC)], 1); CORDER = np.argsort(CC[:, 2])
CC[:60] = np.stack([R.uniform(-260, 260, 60), R.uniform(-160, 160, 60), R.uniform(850, 1500, 60)], 1)       # красные часы — ближе к камере
CRING = np.stack([np.cos(np.linspace(0, 2 * math.pi, 14, endpoint=False)), np.sin(np.linspace(0, 2 * math.pi, 14, endpoint=False)), np.zeros(14)], 1) * 6
CBASE = R.uniform(0, 2 * math.pi, NC); COM = R.uniform(0.8, 1.8, NC)
KILLT = np.where(np.arange(NC) < 60, np.argsort(np.argsort(CC[:60, 2].tolist() + [0] * (NC - 60))) / 60.0, 0)
def clock_field(A, t, vis):
    t0r = ev(3, 1); tk = ev(3, 2); t4 = ev(4, 1); red = np.arange(NC) < 60
    kill = np.where(red, tk + 0.1 + KILLT * 0.8, 1e9); dead = red & (t > kill)
    ang = CBASE + COM * (t * 1.5) * np.where(red & (t > t0r), -(1 + 5 * seg(t, t0r, tk)) * (t > t0r), 1)
    if t > t4: ang = ang + COM * 3.0 * (t - t4) * (1 + 1.5 * seg(t, t4, t4 + 1.5)) * np.where(red, 0.4, 1)
    h = np.stack([np.cos(ang), np.sin(ang), np.zeros(NC)], 1)
    P = np.concatenate([(CC[:, None, :] + CRING[None, :, :]).reshape(-1, 3), CC + h * 3.5, CC + h * 5.5]); n_ = len(CRING) + 2
    mc = np.array(mixc(tuple(WHT), tuple(CYA), ease(seg(t, t4, t4 + 0.4))))
    cols = np.where(red[:, None] & (t > t0r) & ~dead[:, None], REDC, np.where(dead[:, None], np.array([0.3, 0.3, 0.36]), mc)); allc = np.concatenate([np.repeat(cols, 14, 0), cols, cols])
    fade = np.where(dead, 0.25 * (1 - np.clip((t - kill) / 0.4, 0, 1)) + 0.1, 1.0); fa = np.concatenate([np.repeat(fade, 14), fade, fade])
    A.pts(P, allc, fa * 2.2 * vis * (1.4 if t > t4 else 1.0) * (0.8 + 0.2 * np.sin(np.arange(len(P)) * 0.37 + t * 5)), fog=1800, boke=False)
def sphere_pts(n, seed):
    r = np.random.RandomState(seed); v = r.randn(n, 3); return v / np.linalg.norm(v, axis=1)[:, None]
NOISEK = np.random.RandomState(9).randn(14, 3) * 1.6; NOISEP = np.random.RandomState(8).uniform(0, 6.28, 14)
def land(v): return (np.sin(v @ NOISEK.T + NOISEP) * np.array([1.0, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.4, 0.3, 0.3, 0.25, 0.25, 0.2, 0.2])).sum(1)
EV_ = sphere_pts(90000, 12); ELAND = land(EV_) > 0.5; _keep = ELAND | (np.random.RandomState(4).rand(90000) < 0.25); EV_, ELAND = EV_[_keep], ELAND[_keep]
MER = [np.stack([np.cos(np.radians(la)) * np.cos(np.radians(lo)), np.sin(np.radians(la)), np.cos(np.radians(la)) * np.sin(np.radians(lo))], 1) for lo in range(0, 360, 30) for la in [np.linspace(-90, 90, 40)]]
PAR = [np.stack([np.cos(np.radians(la)) * np.cos(np.radians(lo)), np.full(60, np.sin(np.radians(la))), np.cos(np.radians(la)) * np.sin(np.radians(lo))], 1) for la in range(-80, 81, 20) for lo in [np.linspace(0, 360, 60)]]
NODES = np.concatenate([np.stack([np.cos(np.radians(la)) * np.cos(np.radians(lo)), np.full(12, np.sin(np.radians(la))), np.cos(np.radians(la)) * np.sin(np.radians(lo))], 1) for la in range(-80, 81, 20) for lo in [np.arange(0, 360, 30)]])
def rotz(v, a): c, s_ = math.cos(a), math.sin(a); return np.stack([v[:, 0] * c - v[:, 2] * s_, v[:, 1], v[:, 0] * s_ + v[:, 2] * c], 1)
def plane_shape():
    im = Image.new("L", (96, 96), 0); d = ImageDraw.Draw(im); d.ellipse((6, 40, 90, 56), fill=255); d.polygon([(40, 48), (62, 4), (68, 4), (56, 48)], fill=255); d.polygon([(40, 48), (62, 92), (68, 92), (56, 48)], fill=255)
    d.polygon([(10, 48), (22, 28), (26, 28), (20, 48)], fill=255); d.polygon([(10, 48), (22, 68), (26, 68), (20, 48)], fill=255)
    ys, xs = np.nonzero(np.asarray(im) > 128); r = np.random.RandomState(2).choice(len(xs), 420); return (xs[r] - 48) / 48.0, (ys[r] - 48) / 48.0
PLX, PLY = plane_shape()
E1 = np.array([1.0, 0.0, 0.0]); E2 = np.array([0.0, math.cos(math.radians(30)), math.sin(math.radians(30))])
def gc(th, rr=RG + 14): return G + rr * (math.cos(th) * E1 + math.sin(th) * E2)
def tang(th): return -math.sin(th) * E1 + math.cos(th) * E2
def plane_world(th, sgn):
    p = gc(th); tg = tang(th) * sgn; up = (p - G) / np.linalg.norm(p - G); w = np.cross(up, tg); w /= np.linalg.norm(w); return p + (PLX[:, None] * tg[None, :] + PLY[:, None] * w[None, :]) * 55
def clock_sprite(c, nrm, tvec, ang, r=18):
    a = np.linspace(0, 2 * math.pi, 20, endpoint=False); ring = c + r * (np.cos(a)[:, None] * tvec + np.sin(a)[:, None] * np.cross(nrm, tvec)); h = c + r * 0.7 * (math.cos(ang) * tvec + math.sin(ang) * np.cross(nrm, tvec)); return np.concatenate([ring, [h, c]])

def globe(A, t, vis, mode):
    """mode 0 — сетка, 1 — точки Земли"""
    cam = A.cam; rot = 0.12 * t
    if mode == 0:
        for P in MER + PAR:
            Pw = G + RG * P; n = P; vis_m = ((cam.pos - Pw) * n).sum(1) > 0; sx, sy, z = cam.proj(Pw)
            for i in range(len(P) - 1):
                if vis_m[i] and vis_m[i + 1] and z[i] > 1 and z[i + 1] > 1: A.ld.line((sx[i], sy[i], sx[i + 1], sy[i + 1]), fill=ic(np.array([27, 79, 114]) * vis * 1.3), width=1)
        Pw = G + RG * NODES; m = ((cam.pos - Pw) * NODES).sum(1) > 0; A.pts(Pw[m], CYA, np.full(m.sum(), 1.6 * vis), fog=2500, boke=False)
    else:
        v = rotz(EV_, rot); Pw = G + RG * v; m = ((cam.pos - Pw) * v).sum(1) > -20; light = np.clip(0.55 + 0.45 * (v @ np.array([0.6, 0.3, -0.7])), 0.25, 1.0)
        col = np.where(ELAND[:, None], np.array([0.4, 0.8, 1.0]), np.array([0.14, 0.4, 0.8])); A.pts(Pw[m], col[m], (np.where(ELAND, 3.2, 1.6) * light * vis)[m], fog=3500, boke=False)
    # атмосфера: ободок
    sx, sy, z = cam.proj(np.array([G])); dist = np.linalg.norm(cam.pos - G); rr = cam.fl * RG / math.sqrt(max(dist * dist - RG * RG, 1)); 
    if z[0] > 0: A.nd.ellipse((sx[0] - rr, sy[0] - rr, sx[0] + rr, sy[0] + rr), outline=ic(np.array([47, 143, 216]) * vis * 0.55), width=2)

def draw_world(t, A, cam):
    n = phase(t); wt = WT()
    tdive = s(2) + D[1] - 1.1
    # пыль (терминальный мир)
    if t < T_B or t >= T_8:
        if t >= s(13): A.pts(L.DUST2 + np.array([4 * math.sin(t * 0.5), 0, 0]), np.array([0.62, 0.7, 0.78]), 0.22 * (0.7 + 0.3 * np.sin(L.DTW[:600] * 40 + t * 3)), boke=False)
        else: A.pts(L.DUST, np.array([0.62, 0.7, 0.78]), (0.35 + 0.5 * L.DTW) * (0.7 + 0.3 * np.sin(L.DTW * 40 + t * 8)) * ease(t / 0.4), boke=False)
    if T_B <= t < tdive + 1.2:                                             # облако
        a = 1 - ease(seg(t, tdive, tdive + 1.0)); col = np.where(L.CRED[:, None], L.RED, np.array([0.75, 0.9, 1.0])); A.pts(L.CLOUD, col, 0.9 * a * np.where(L.CRED, 1.1, 1.0))
    if s(2) + D[1] * 0.5 <= t < s(5) + 3:                                  # поле часов
        clock_field(A, t, ease(seg(t, s(2) + D[1] * 0.55, s(2) + D[1] * 0.55 + 0.8)) * (1 - ease(seg(t, s(5) + 0.5, s(5) + 2.5))))
    if s(4) + D[3] * 0.4 <= t < s(6) + 0.8: globe(A, t, ease(seg(t, s(4) + D[3] * 0.4, s(5))) * (1 - ease(seg(t, s(6), s(6) + 0.7))), 0)
    if s(6) <= t < T_FL + 0.1: globe(A, t, ease(seg(t, s(6), s(6) + 0.8)), 1)
    # орбита и станция
    if s(6) <= t < T_FL + 0.1:
        vo = ease(seg(t, s(6) + 0.3, s(6) + 1.0)) * (1 - ease(seg(t, ev(6, 10), ev(6, 12)))); U1 = np.array([1.0, 0, 0]); U2 = np.array([0, math.cos(math.radians(50)), math.sin(math.radians(50))]); ph = np.linspace(0, 2 * math.pi, 400, endpoint=False)
        ring = G + 1.18 * RG * (np.cos(ph)[:, None] * U1 + np.sin(ph)[:, None] * U2)
        if vo > 0: A.pts(ring, CYA, np.full(400, 1.2 * vo), fog=4000, boke=False); A.poly(np.vstack([ring, ring[:1]]), np.array([27, 79, 114]) * 1.4 * vo, 1)
        q = t - s(6); phi = 2 * math.pi * (0.12 * q + 0.07 * q * q); pos = G + 1.18 * RG * (math.cos(phi) * U1 + math.sin(phi) * U2); tr = [G + 1.18 * RG * (math.cos(phi - 0.05 * j) * U1 + math.sin(phi - 0.05 * j) * U2) for j in range(1, 30)]
        A.pts(np.array([pos] + tr), np.array([1.0, 0.95, 0.85]), np.array([12.0] + [4.0 * (1 - j / 30) for j in range(29)]), fog=4000, boke=False)
        tg = -math.sin(phi) * U1 + math.cos(phi) * U2; A.line(tuple(pos + 22 * np.cross(tg, U1 * 0 + np.array([0, 0, 1]))), tuple(pos - 22 * np.cross(tg, np.array([0, 0, 1]))), np.array([255, 240, 200]), 2)
    # самолёты и часы-спрайты
    if s(5) + 0.3 <= t < s(6) + 0.7:
        base = G + (RG + 34) * E1; vis = ease(seg(t, ev(5, 6), ev(5, 6) + 0.4)) * (1 - ease(seg(t, s(6), s(6) + 0.6)))
        if vis > 0:
            nrm = E1; tv = E2; A.pts(clock_sprite(base, nrm, tv, 0.4 * t), np.array([0.6, 0.62, 0.7]), np.full(22, 2.2 * vis), fog=4000, boke=False)
            A.pts(clock_sprite(base + 70 * E2, nrm, tv, 1.2 * t), CYA, np.full(22, 2.4 * vis), fog=4000, boke=False); A.pts(clock_sprite(base - 70 * E2, nrm, tv, 0.8 * t), AMB, np.full(22, 2.4 * vis), fog=4000, boke=False)
        a = ease(seg(t, ev(5, 8), ev(5, 14))) * 2 * math.pi
        if t >= ev(5, 8) - 0.2:
            for sgn, col in ((1, CYA), (-1, AMB)):
                A.pts(plane_world(sgn * a, sgn), col, np.full(420, 1.6), fog=4000, boke=False)
                th = np.linspace(0, a, max(2, int(a * 14)))
                if len(th) > 1: A.poly(np.array([gc(sgn * x) for x in th]), col * 255 * 0.8, 2)
    # спутники и город
    if T_FL <= t < s(8) + 0.62:
        cities(A, t, cam)
    # терминал-мир: часы
    if s(10) - 0.3 <= t < s(13) and True: clock3d(A, t)
def cities(A, t, cam):
    kill_t = s(8) + 0.0; dt = t - kill_t; ea = 0.5
    P = L.people_pos(8.0 + 0.3 * (t - T_FL)); sel = np.arange(0, L.NP, 2); sel = sel[(P[sel, 2] > cam.pos[2] - 20) & (P[sel, 2] < cam.pos[2] + 2400)]
    fl = np.clip(1 - dt / 0.6, 0, 1) if dt > 0 else 1.0; ck = np.array([1.0, 0.76, 0.48])
    A.pts(P[sel], ck, np.full(len(sel), 1.7 * fl) * (0.85 + 0.3 * np.sin(L.PTW[sel] * 30 + t * 4)), fog=900)
    ww = np.arange(0, 43000, 2); ww = ww[(L.WZ[ww] > cam.pos[2] - 20) & (L.WZ[ww] < cam.pos[2] + 2200)]
    A.pts(np.stack([L.WX[ww], L.WY[ww], L.WZ[ww]], 1), np.array([1.0, 0.82, 0.54]), np.full(len(ww), 0.8 * fl), fog=900)
    selb = np.nonzero((L.BCZ > cam.pos[2] + 25) & (L.BCZ < cam.pos[2] + 1500))[0]; colr = np.array([27, 79, 114]) * ea * 1.5
    for i in selb[:90]:
        cs = np.array([[-1, 0, -1], [1, 0, -1], [1, 0, 1], [-1, 0, 1]], float); V = [[L.BCX[i] + c[0] * L.BW[i] / 2, yy, L.BCZ[i] + c[2] * L.BD[i] / 2] for yy in (0, L.BHT[i]) for c in cs]; sx, sy, z = cam.proj(np.array(V))
        for j in range(4):
            for a_, b_ in ((j, (j + 1) % 4), (4 + j, 4 + (j + 1) % 4), (j, 4 + j)):
                if z[a_] > 1 and z[b_] > 1: A.ld.line((sx[a_], sy[a_], sx[b_], sy[b_]), fill=ic(colr), width=1)
    for xl in L.LANES: A.line((xl, 0, cam.pos[2] + 4), (xl, 0, cam.pos[2] + 2200), np.array([201, 116, 42]) * 0.14)
    # спутники 5×4
    sa = (1 - ease(seg(t, ev(7, 17), ev(7, 18)))) * 0.0 + 1.0
    for xi, xx in enumerate((-300, -150, 0, 150, 300)):
        for j in range(4):
            zz = cam.pos[2] + 300 + j * 230; p = np.array([xx, 380.0, zz]); pulse = (t * 0.8 - (xi * 0.15) - j * 0.05) % 1.2
            ring = p + 14 * np.stack([np.cos(np.linspace(0, 6.28, 16)), np.zeros(16), np.sin(np.linspace(0, 6.28, 16))], 1) * (1 + pulse); A.pts(ring, np.array([1.0, 0.76, 0.48]), np.full(16, 2.0 * (1 - pulse / 1.2)), fog=1500, boke=False)
            A.pts(np.array([p, p + [10, 0, 0], p - [10, 0, 0], p + [20, 0, 0], p - [20, 0, 0]]), CYA * 0 + np.array([1.0, 0.94, 0.84]), np.array([14.0, 6, 6, 4, 4]), fog=2500, boke=False)
            alive = not (t > ev(7, 17) + 0.3 * (xi + j) and not (xi == 2 and j == 1))
            if alive and t < ev(7, 17) + 2.5 or (xi == 2 and j == 1):
                A.line(tuple(p), (xx, 0, zz), np.array([255, 75, 62]) * 0.5)
                sg = ((t * 3.3 + xi * 0.3 + j * 0.2) % 1.0); A.pts(np.array([[xx, 380 * (1 - sg), zz]]), np.array([1.0, 0.6, 0.5]), np.array([2.2]), fog=1500, boke=False)
    # карта: точка-машина и навигатор
    if t >= ev(7, 17):
        k = ease(seg(t, ev(7, 17), ev(7, 18))); zc = cam.pos[2]; 
        for gz in np.arange(zc - 200, zc + 200, 65): A.line((-390, 0.2, gz), (390, 0.2, gz), np.array([27, 79, 114]) * 0.8 * k)
        prog = seg(t, ev(7, 17), s(8)); car = np.array([30.0, 0.8, zc - 40 + 60 * prog]); disp = ease(seg(t, ev(7, 19), evend(7, 23))); nav = car + np.array([95.0 * disp, 0, 20 * disp])
        A.disc(car, CYA, 6 + math.sin(t * 6), k)
        if disp > 0.02:
            A.disc(nav, REDC, 6)
            for q in np.linspace(0.1, 0.95, 12): A.disc(car + (nav - car) * q, REDC, 2)
def clock3d(A, t):
    ring_k = ease(seg(t, ev(10, 1), ev(10, 4))); a = np.linspace(0, 2 * math.pi, 360, endpoint=False); rad = 100.0; vis = ease(seg(t, ev(10, 1), ev(10, 1) + 0.5))
    ringp = np.stack([TC[0] + np.sin(a) * rad, TC[1] + np.cos(a) * rad, np.full(360, TC[2])], 1); tick = np.stack([TC[0] + np.sin(np.radians(np.arange(60) * 6)) * (rad - 10), TC[1] + np.cos(np.radians(np.arange(60) * 6)) * (rad - 10), np.full(60, TC[2])], 1)
    # текст «ГОТОВО» → кольцо
    if t < ev(10, 4) + 0.2:
        tx, tz, sc, hy = L.WORDS[0]; src = np.stack([TC[0] + (tx - 0) * 2.4, TC[1] + (tz - 105 - 12) * -1.6, np.full(2200, TC[2])], 1); tgt = np.stack([TC[0] + np.sin(L.R7.rand(2200) * 0 + a[np.arange(2200) % 360]) * rad, TC[1] + np.cos(a[np.arange(2200) % 360]) * rad, np.full(2200, TC[2])], 1)
        P = src * (1 - ring_k) + tgt * ring_k; A.pts(P, np.array([0.75, 0.94, 1.0]), np.full(2200, 1.1 * (1 - 0.85 * ring_k)), fog=3000, boke=False)
    A.pts(ringp, np.array([0.75, 0.94, 1.0]), np.full(360, 3.5 * ring_k), fog=3000, boke=False); A.pts(tick, np.array([0.75, 0.94, 1.0]), np.full(60, 5.0 * ring_k), fog=3000, boke=False)
    refl = ringp.copy(); refl[:, 1] = 2 * (TC[1] - rad - 15) - refl[:, 1]; A.pts(refl, np.array([0.5, 0.8, 1.0]), np.full(360, 0.35 * ring_k), fog=3000, boke=False)
    ticks = [ev(10, 4), ev(10, 5), ev(10, 7)]; tt = ev(10, 7); 
    while tt < s(13): tt += 1.0; ticks.append(tt)
    nt = sum(1 for x in ticks if t >= x); lastt = max([x for x in ticks if t >= x], default=-9); spring = 3 * math.exp(-(t - lastt) / 0.08) * math.cos((t - lastt) * 40) if nt else 0
    sec = 6 * nt + spring; minu = 348 + (-12 * math.exp(-(t - ev(12, 2)) / 0.15) if t > ev(12, 2) and t < ev(12, 2) + 0.4 else 0) + 0.1 * t; hour = 7 * 30 + 29
    if ring_k > 0.5:
        for ang, ln, col, w in ((hour, 0.5, (232, 238, 245), 3), (minu, 0.78, (232, 238, 245), 3), (sec, 0.9, (92, 200, 255), 2)):
            r_ = math.radians(ang); A.line(tuple(TC), (TC[0] + math.sin(r_) * rad * ln, TC[1] + math.cos(r_) * rad * ln, TC[2]), np.array(col) * ring_k, w)
        A.pts(np.array([TC]), np.array([0.75, 0.94, 1.0]), np.array([4.0]), fog=3000, boke=False)

# ---------------- текст и плашка
def plate_img(t, lines):
    im = Image.new("RGBA", (960, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, 959, 459), 14, fill=(10, 16, 26, 160), outline=(60, 80, 104, 255), width=2); y = 96
    for txt, sz, col, t0, cps in lines:
        n = int(max(0, (t - t0) * cps)); part = txt[:min(len(txt), n)]
        if n > 0 or t >= t0:
            fn = font("m", "Medium", sz); d.text((60, y), part, font=fn, fill=col + (255,))
            if (n < len(txt) and n > 0) or (txt == lines[-1][0] and int(t * 2.2) % 2 == 0 and n >= len(txt)): wc = d.textlength(part, font=fn); d.rectangle((60 + wc + 6, y + 4, 60 + wc + sz * 0.45, y + sz + 4), fill=(191, 239, 255, 255))
        y += int(sz * 1.35)
    return im
PLATE_DST = None
def plate_quad(cam, yawd=0.0, pitchd=0.0, center=(0.0, 10.0, 520.0)):
    a = math.radians(yawd); p = math.radians(pitchd); Rx = np.array([math.cos(a), 0, -math.sin(a)]); Ry = np.array([0, math.cos(p), math.sin(p)]); C0 = np.array(center); dst = []
    for lx, ly in ((-100, 48), (100, 48), (100, -48), (-100, -48)):
        q = C0 + lx * Rx + ly * Ry; sx, sy, z = cam.proj(np.array([q])); dst.append((sx[0] * 2, sy[0] * 2))
    return dst

WORDS_KEY = {"физику", "Назад", "Вперёд", "первом", "дня", "ты", "прошлое"}
def frame(t):
    n = phase(t); cam = Cam(t); fl2 = cam.fl * 2
    black = s(2) + 1.25 <= t < T_B
    if black: return np.zeros((H, W, 3), np.uint8)
    A = Acc(cam); draw_world(t, A, cam); base = A.out(); F = np.asarray(Image.fromarray(base).resize((W, H), Image.BICUBIC), np.float32) + np.array([2, 4, 10], np.float32)
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); glitch = 0.0; chroma = 1.5; shake = 0.9 * math.sin(t * 7.3); hit = 0.0; flash = 0.0
    # --- плашка (фразы 1–2, 8–9)
    pl = None
    if t < T_B:
        wt1 = WT()[1]; tend = s(1) + VO + wt1[2][1]; tstart = 0.1
        pl = plate_img(t, [("Создай", 82, (232, 238, 245), tstart, 6 / max(tend - tstart, 0.5) * 1.6 * 0 + 6.5), ("машину", 82, (232, 238, 245), tstart + 0.55, 9), ("времени.", 82, (232, 238, 245), tstart + 1.1, 9)])
        # добавим подпись запроса
        pl2 = Image.new("RGBA", (960, 460), (0, 0, 0, 0)); ImageDraw.Draw(pl2).text((40, 24), "новый запрос · 07:58", font=font("m", "Regular", 30), fill=(138, 151, 166, 255)); pl.alpha_composite(pl2)
        a = math.radians(-9); pitchd = 4; yawd = -9
        dst = plate_quad(cam, yawd, pitchd); al = ease(seg(t, 0.15, 0.6)) * (1 - ease(seg(t, T_B - 0.1 - 0.15, s(2) + 1.24)))
        wp = quad_warp(pl, dst, (W, H)); wp.putalpha(wp.getchannel("A").point(lambda v: int(v * al))); tl.alpha_composite(wp)
        if s(2) <= t < s(2) + 1.25:
            k = seg(t, s(2), s(2) + 1.25); glitch = k; chroma = 1.5 + 12.5 * k; shake += 6 * k * math.sin(t * 90); r = np.random.RandomState(int(t * FPS) // 2 + 5); d = ImageDraw.Draw(tl)
            for _ in range(14): d.text((int(r.uniform(40, 900)), int(r.uniform(300, 1600))), f"{r.randint(1000, 999999):,}".replace(",", " "), font=font("m", "Regular", 26), fill=(150, 200, 240, int(200 * k)))
    if s(8) + 0.6 <= t < s(10) + 0.4:
        tt0 = s(8) + 0.6
        lines = [("› вывод: найден", 40, (138, 151, 166), s(8) + 0.9, 28)]
        if t >= ev(9, 1): lines += [("Готово.", 82, (232, 238, 245), ev(9, 1), 22), ("Машина времени запущена.", 44, (232, 238, 245), ev(9, 2), 40)]
        pl = plate_img(t, lines); al = ease(seg(t, tt0, tt0 + 0.5)) * (1 - ease(seg(t, ev(10, 2), ev(10, 4)))); dst = plate_quad(cam, 0, 0)
        wp = quad_warp(pl, dst, (W, H)); wp.putalpha(wp.getchannel("A").point(lambda v: int(v * al))); tl.alpha_composite(wp)
    # --- надписи «НАЗАД / ВПЕРЁД»
    d = ImageDraw.Draw(tl)
    if ev(3, 1) <= t < s(4) + 0.2:
        k = ease(seg(t, ev(3, 1), ev(3, 1) + 0.2)) * (1 - ease(seg(t, s(4) - 0.2, s(4) + 0.2))); jit = 4 * math.sin(t * 80) if ev(3, 2) <= t < ev(3, 5) else 0
        d.text((540 + jit, 760), "НАЗАД · не найдено", font=font("m", "Bold", 64), fill=(255, 75, 62, int(255 * k)), anchor="mm")
    if ev(4, 1) <= t < s(5) + 0.4:
        k = ease(seg(t, ev(4, 1), ev(4, 1) + 0.2)) * (1 - ease(seg(t, s(5) - 0.1, s(5) + 0.4))); d.text((540, 760), "ВПЕРЁД · проверено", font=font("m", "Bold", 64), fill=(92, 200, 255, int(255 * k)), anchor="mm")
    # --- фраза 5: плашка 1971 и цифры
    if s(5) <= t < s(6) + 0.3:
        k = ease(seg(t, s(5) + 0.2, s(5) + 0.9)) * (1 - ease(seg(t, ev(5, 15) + 1.4, s(6)))); bx = Image.new("RGBA", (860, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
        bd.rounded_rectangle((0, 0, 859, 149), 12, fill=(10, 16, 26, 170), outline=(60, 80, 104, 255), width=2); bd.text((30, 24), "1971 · самолёты · атомные часы", font=font("m", "Medium", 40), fill=(232, 238, 245, 255))
        if t >= ev(5, 5):
            if int(t * 12) % 7: bd.text((30, 78), "1971", font=font("m", "Bold", 56), fill=(92, 200, 255, 255))
        put(tl, bx, 540, 600 - 30 * (1 - k), alpha=k)
        k2 = ease(seg(t, ev(5, 15), ev(5, 15) + 0.35)) * (1 - ease(seg(t, s(6) - 0.1, s(6) + 0.3)))
        if k2 > 0:
            d.text((300, 1020 - 20 * (1 - k2)), "на восток −59 нс", font=font("i", "Black", 56), fill=(92, 200, 255, int(255 * k2)), anchor="mm"); d.text((780, 1180 + 20 * (1 - k2)), "на запад +273 нс", font=font("i", "Black", 56), fill=(255, 194, 122, int(255 * k2)), anchor="mm")
    # --- фраза 6: календарь, +0,02
    if s(6) <= t < s(7) + 0.4:
        if t >= ev(6, 1) and t < ev(6, 2) + 1.0:
            kk = ease(seg(t, ev(6, 1), ev(6, 1) + 0.3)) * (1 - ease(seg(t, ev(6, 2) + 0.6, ev(6, 2) + 1.0))); d.text((540, 640), "Сергей Крикалёв · орбита", font=font("m", "Regular", 40), fill=(138, 151, 166, int(255 * kk)), anchor="mm")
        if t >= ev(6, 6):
            q = eo5(seg(t, ev(6, 6), ev(6, 7) + 0.4)); val = int(803 * q); al = 1 - ease(seg(t, ev(6, 10), ev(6, 11))); bx = (150, 760, 930, 1040)
            if al > 0:
                dd = ImageDraw.Draw(tl); cc = (92, 200, 255, int(150 * al)); L_ = 28
                for (xa, ya, sx_, sy_) in ((bx[0], bx[1], 1, 1), (bx[2], bx[1], -1, 1), (bx[0], bx[3], 1, -1), (bx[2], bx[3], -1, -1)): dd.line((xa, ya, xa + sx_ * L_, ya), fill=cc, width=4); dd.line((xa, ya, xa, ya + sy_ * L_), fill=cc, width=4)
                put(tl, wide(f"{val:03d}", 190, (232, 238, 245, 255)), 540, 880, alpha=al); d.text((540, 1000), "суток", font=font("m", "Regular", 44), fill=(138, 151, 166, int(255 * al)), anchor="mm")
                if q >= 0.999 and t < ev(6, 7) + 0.6: hit = max(hit, 3)
        if t >= ev(6, 15):
            k = ease(seg(t, ev(6, 15), ev(6, 15) + 0.1)) * (1 - ease(seg(t, ev(6, 15) + 1.3, ev(6, 15) + 1.8))); put(tl, wide("+0,02 с", 150, (191, 239, 255, 255)), 540, 860, alpha=k)
            if k > 0.5: chroma = max(chroma, 5)
    # --- фраза 7: вспышка, плашка +38, 10 км
    fl_ = max(0.0, 1 - abs(t - T_FL) / 0.35); flash = fl_
    if ev(7, 7) <= t < ev(7, 16) + 1.0:
        k = ease(seg(t, ev(7, 7), ev(7, 7) + 0.3)) * (1 - 0.3 * ease(seg(t, ev(7, 14), ev(7, 16)))); val = int(38 * eo5(seg(t, ev(7, 12), ev(7, 13) + 0.2)))
        bx = Image.new("RGBA", (860, 300), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx); bd.rounded_rectangle((0, 0, 859, 299), 12, fill=(10, 16, 26, 150), outline=(60, 80, 104, 255), width=2)
        bd.text((430, 105), f"+{val}", font=font("i", "Black", 150), fill=(191, 239, 255, 255), anchor="mm"); bd.text((430, 235), "мкс в сутки", font=font("m", "Medium", 52), fill=(138, 151, 166, 255), anchor="mm")
        if t < ev(7, 15): put(tl, bx, 540, 780, alpha=k)
        else:
            kk = ease(seg(t, ev(7, 14), ev(7, 16))); put(tl, bx, 540 + (-200 - 0) * kk, 780 - 200 * kk, scale=1 - 0.5 * kk, alpha=0.8 * (1 - 0.3 * kk) * k)
    if ev(7, 23) <= t < s(8) + 0.6:
        k = ease(seg(t, ev(7, 23), ev(7, 23) + 0.15)); put(tl, wide("≈ 10 км", 110, (255, 120, 108, 255)), 540, 640, alpha=k)
        if t < ev(7, 23) + 0.3: hit = max(hit, 7 * math.exp(-(t - ev(7, 23)) / 0.1))
    # --- фраза 11: силуэт в стекле
    if ev(11, 2) <= t < ev(11, 2) + 0.9:
        k = ease(seg(t, ev(11, 2), ev(11, 2) + 0.15)) * (1 - ease(seg(t, ev(11, 2) + 0.4, ev(11, 2) + 0.9))); gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
        gd.rectangle((140, 480, 940, 1380), fill=(4, 8, 14, 215)); sil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sil)
        sd.ellipse((420, 700, 660, 960), fill=(92, 200, 255, 170)); sd.ellipse((260, 940, 820, 1500), fill=(92, 200, 255, 130)); sil = sil.filter(ImageFilter.GaussianBlur(26)); gl.alpha_composite(sil)
        gd.line((140, 480, 940, 480), fill=(120, 160, 190, 180), width=3); gd.line((140, 1380, 940, 1380), fill=(120, 160, 190, 180), width=3)
        gl.putalpha(gl.getchannel("A").point(lambda v: int(v * k))); tl.alpha_composite(gl); hit = max(hit, 4 * math.exp(-(t - ev(11, 2)) / 0.1))
    # --- ЗАДАЧА ВЫПОЛНЕНА
    t3 = ev(12, 3)
    if t3 <= t < s(13):
        tt = t - t3; al = ease(tt / 0.2) * (1 - ease(seg(t, s(13) - 0.4, s(13)))); sl = 300 * (1 - eo5(tt / 0.35)); gh = 1 - ease(tt / 0.3); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, wd in enumerate(("ЗАДАЧА", "ВЫПОЛНЕНА")): put(lay, wide(wd, 96, (232, 238, 245, 255)), 540 - sl, 940 + i * 130); put(gst, wide(wd, 96, (180, 220, 255, 255)), 540 + 70 * gh, 940 + i * 130 + 18 * gh, alpha=0.45)
        ImageDraw.Draw(lay).rectangle((540 - 360 * ease(tt / 0.3), 1170, 540 + 360 * ease(tt / 0.3), 1176), fill=(92, 200, 255, 255)); tl2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tl2.alpha_composite(gst); tl2.alpha_composite(lay)
        tl2.putalpha(tl2.getchannel("A").point(lambda v: int(v * al)))
        if t >= ev(12, 5): d2 = ImageDraw.Draw(tl2); k5 = ease(seg(t, ev(12, 5), ev(12, 5) + 0.3)) * al; d2.text((540, 1280), "Чем ещё помочь?" + ("▌" if int(t * 2.2) % 2 == 0 else ""), font=font("m", "Medium", 40), fill=(191, 239, 255, int(255 * k5)), anchor="mm")
        tl.alpha_composite(tl2)
        if tt < 0.4: chroma = max(chroma, 6 * (1 - tt / 0.4)); hit = max(hit, 3 * (1 - tt / 0.4)); glitch = max(glitch, 0.4 if tt < 0.2 else 0)
    # --- призыв
    if t >= s(13):
        for i, (wd, k0) in enumerate((("Отправь тому,", 1), ("кто мечтает", 3), ("вернуться в прошлое", 5))):
            ti = ev(13, k0); k = ease(seg(t, ti, ti + 0.25)); put(tl, wide(wd, 84 if i == 2 else 92, (232, 238, 245, 255), 1.0, "Bold"), 540, 760 + i * 130 + 40 * (1 - k), alpha=k, blur=14 * (1 - k))
        ti = ev(13, 8); k = seg(t, ti, ti + 1.2)
        if k > 0:
            sp = 0.7 + 0.3 * (1 - math.exp(-6 * k) * math.cos(10 * k)); pill = Image.new("RGBA", (560, 140), (0, 0, 0, 0)); pd_ = ImageDraw.Draw(pill); pd_.rounded_rectangle((0, 0, 559, 139), 70, fill=(92, 200, 255, 255))
            pd_.text((280, 70), "Подпишись", font=font("i", "Bold", 62), fill=(2, 4, 10, 255), anchor="mm"); put(tl, pill, 540, 1180, scale=sp, alpha=min(1, k * 4))
        if t >= TOTAL - 0.4 and int(t * 2.2) % 2 == 0: ImageDraw.Draw(tl).rectangle((528, 1440, 552, 1480), fill=(191, 239, 255, 255))
    # --- композиция
    a = np.asarray(tl, np.float32); F = F * (1 - a[:, :, 3:4] / 255) + a[:, :, :3] * (a[:, :, 3:4] / 255)
    if s(2) <= t < s(2) + 1.25:
        k = seg(t, s(2), s(2) + 1.25); img = Image.fromarray(np.clip(F, 0, 255).astype(np.uint8)); acc = np.zeros_like(F)
        for j in range(7):
            sc = 1 + 0.05 * k * j / 6 * 2; w2, h2 = int(W * sc), int(H * sc); im2 = img.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H)); acc += np.asarray(im2, np.float32)
        F = acc / 7
    if flash > 0: F = F + 255 * flash * 0.85
    thr = np.clip(F / 255 - 0.5, 0, 1); sm = Image.fromarray((thr * 255).astype(np.uint8)).resize((270, 480), Image.BILINEAR)
    bl = sum(np.asarray(sm.filter(ImageFilter.GaussianBlur(sg)).resize((W, H), Image.BILINEAR), np.float32) * w_ for sg, w_ in ((2, 0.55), (6, 0.5), (18, 0.45)))
    F = np.clip(F + bl * (1.6 + 1.4 * flash), 0, 255); ch = int(round(chroma))
    if ch > 0: F = F.copy(); F[:, :, 0] = np.roll(F[:, :, 0], ch, 1); F[:, :, 2] = np.roll(F[:, :, 2], -ch, 1)
    sh = int(round(shake + hit * math.cos(t * 120))); sv = int(round(0.6 * shake + hit * math.sin(t * 97)))
    if sh or sv: F = np.roll(F, (sv, sh), (0, 1))
    r = np.random.RandomState(int(t * FPS) // 2 + 3)
    if glitch > 0:
        for _ in range(int(8 * glitch) + 1): y0 = r.randint(250, 1650); hh = r.randint(20, 90); F[y0:y0 + hh] = np.roll(F[y0:y0 + hh], r.randint(-40, 40), 1)
    yy, xx = np.mgrid[0:H, 0:W]; vg = np.clip(1 - 0.28 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0.35, 1); F = np.clip(F * vg[:, :, None], 0, 255)
    im = Image.fromarray(F.astype(np.uint8)); d = ImageDraw.Draw(im)
    # --- HUD
    d.text((70, 262), "ВЫМЫШЛЕННЫЙ СЦЕНАРИЙ", font=font("m", "Regular", 22), fill=(110, 124, 142))
    cv = counter(t)
    if ev(2, 6) <= t < s(10) + 1.2:
        a = ease(seg(t, ev(2, 6), ev(2, 6) + 0.5)) * (1 - ease(seg(t, s(10), s(10) + 1.0))); dy = -120 * ease(seg(t, s(10), s(10) + 1.0)); jit = 3 if (ev(3, 2) <= t < ev(3, 5) and int(t * 20) % 2) else 0
        col = (255, 255, 255) if cv >= 99.99 else mixc((232, 238, 245), (92, 200, 255), cv / 100); x0, y0 = 60 + jit, 300 + dy; bx = (x0, y0, x0 + 560, y0 + 160); cc = ic(np.array((92, 200, 255)) * a * 0.6); L_ = 20
        for (xa, ya, sx_, sy_) in ((bx[0], bx[1], 1, 1), (bx[2], bx[1], -1, 1), (bx[0], bx[3], 1, -1), (bx[2], bx[3], -1, -1)): d.line((xa, ya, xa + sx_ * L_, ya), fill=cc, width=3); d.line((xa, ya, xa, ya + sy_ * L_), fill=cc, width=3)
        d.text((x0 + 22, y0 + 18), "ЦЕЛЬ · МАШИНА ВРЕМЕНИ", font=font("m", "Regular", 24), fill=ic(np.array((138, 151, 166)) * a))
        xx_ = x0 + 22; st = f"{cv:.2f}".replace(".", ",") + " %"
        if t < ev(2, 6) + 0.6:
            for i, chh in enumerate(st): k = ease(seg(t, ev(2, 6) + i * 0.05, ev(2, 6) + i * 0.05 + 0.2)); d.text((xx_, y0 + 60 - 30 * (1 - k)), chh, font=font("m", "Bold", 76), fill=ic(np.array(col) * k * a)); xx_ += 46
        else: d.text((xx_, y0 + 60), st, font=font("m", "Bold", 76), fill=ic(np.array(col) * a))
    LOG = [("› задача: машина времени", ev(2, 4) - 0.6, 0), ("› проверяю: физика", ev(2, 5), 0), ("› назад: не найдено", ev(3, 1), 1), ("› вперёд: проверено", ev(4, 1), 2), ("› сверка: самолёты 1971", ev(5, 6), 0),
           ("› сверка: орбита, 803 суток", ev(6, 3), 0), ("› сверка: спутники, +38 мкс в сутки", ev(7, 9), 0), ("› вывод: найден", s(8) + 0.9, 0)]
    if ev(2, 4) - 0.6 <= t < s(8) + 0.6:
        shown = [l for l in LOG if t >= l[1]][-4:]; y = 1500
        for sx_, ts, kind in shown:
            nn = int(min(len(sx_), (t - ts) / 0.025)); d.text((70, y), sx_[:nn], font=font("m", "Regular", 27), fill=(255, 110, 100) if kind == 1 else (92, 200, 255) if kind == 2 else (138, 151, 166)); y += 36
    if 2 <= n <= 12 and not (s(8) + 0.6 <= t < s(10)) and not (n == 12 and t >= ev(12, 3) - 0.1):
        wl = words(n); tms = WT()[n]; chunks = [(k, min(k + 2, len(wl))) for k in range(0, len(wl), 2)]
        for a0, b0 in chunks:
            tt0 = s(n) + VO + tms[a0][0] - 0.05; tt1 = (s(n) + VO + tms[chunks[chunks.index((a0, b0)) + 1][0]][0] - 0.05) if chunks.index((a0, b0)) + 1 < len(chunks) else s(n) + VO + tms[-1][1] + 0.25
            if tt0 <= t < tt1:
                txt = " ".join(wl[a0:b0]); keyw = any(w in WORDS_KEY for w in wl[a0:b0]); fnt = font("i", "Bold", 56); wlen = d.textlength(txt, font=fnt); xt = 540 - wlen / 2
                d.text((xt + 3, 1243), txt, font=fnt, fill=(0, 0, 0)); d.text((xt, 1240), txt, font=fnt, fill=(92, 200, 255) if keyw else (232, 238, 245))
    F = np.asarray(im, np.float32); g = ease(t / 0.4) if t < 0.4 else 1.0
    if t > TOTAL - 0.3: g = min(g, (TOTAL - t) / 0.3)
    if ev(12, 5) + 1.3 <= t < s(13): g = min(g, 1 - ease(seg(t, ev(12, 5) + 1.3, s(13))))
    F = F * g + np.random.RandomState(int(t * FPS) % 8).randn(H, W, 1) * 5.0
    return np.clip(F, 0, 255).astype(np.uint8)

def counter(t):
    prev = 0.0
    for te, tv in ((ev(4, 3), 12.4), (ev(5, 15), 31.6), (ev(6, 13), 58.1), (ev(7, 16), 91.7), (ev(9, 4), 100.0)):
        if t < te: return prev
        if t < te + 0.5: return prev + (tv - prev) * eo5(seg(t, te, te + 0.5))
        prev = tv
    return prev

# ---------------- звук
def audio():
    n = int((TOTAL + 0.3) * SR); a = np.zeros(n, np.float32); tt = np.arange(n) / SR; r = np.random.RandomState(11)
    def add(t0, x, g=1.0):
        i = int(t0 * SR); x = x[:max(0, n - i)]; a[i:i + len(x)] += x * g
    def env(m, atk, dec): return (np.minimum(np.arange(m) / (atk * SR + 1), 1) * np.exp(-np.arange(m) / (dec * SR))).astype(np.float32)
    def click(g=1.0, f=2200): m = int(0.03 * SR); return (r.randn(m) * 0.6 + np.sin(2 * np.pi * f * np.arange(m) / SR)) * env(m, 0.0005, 0.006) * g
    def tone(f, d, g=1.0, atk=0.01, dec=None): m = int(d * SR); return np.sin(2 * np.pi * f * np.arange(m) / SR) * env(m, atk, dec or d / 3) * g
    def sweep(f0, f1, d, g=1.0, noise=0.2):
        m = int(d * SR); ph = np.cumsum(np.linspace(f0, f1, m)) / SR; return (np.sin(2 * np.pi * ph) * 0.25 + r.randn(m) * noise) * np.sin(np.linspace(0, math.pi, m)) * g
    # голос
    vox = np.zeros(n, np.float32)
    for i in range(13):
        sr, v = wavfile.read(f"{WK}/v_{i + 1:02d}.wav"); v = v.astype(np.float32) / 32768; v = v.mean(1) if v.ndim > 1 else v
        import scipy.signal as ss
        if sr != SR: v = ss.resample_poly(v, SR, sr).astype(np.float32)
        j = int((S[i] + VO) * SR); v = v[:max(0, n - j)]; vox[j:j + len(v)] += v
    # фон: дрон и пад
    env_v = np.convolve(np.abs(vox), np.ones(int(0.08 * SR)) / int(0.08 * SR), "same"); duck = 1 - 0.5 * np.clip(env_v / 0.1, 0, 1)
    lv = np.interp(tt, [0, s(2), s(3), s(6), s(8), s(8) + 0.6, s(9), s(12), s(13), TOTAL], [0.05, 0.2, 0.28, 0.2, 0.05, 0.08, 0.1, 0.1, 0.1, 0.0])
    bed = (np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 82.4 * tt + np.sin(tt * 0.4)) + 0.3 * np.sin(2 * np.pi * 110.5 * tt)) * (0.7 + 0.3 * np.sin(tt * 0.9)) * lv * 0.3
    a += (bed * duck).astype(np.float32)
    for i in range(int(2.5 * 6)): add(0.1 + i * 0.09, click(0.3, 1800 + 300 * (i % 3)))
    add(s(2), sweep(300, 4000, 1.25, 0.8)); add(s(2) + 1.25, tone(55, 0.35, 1.2, 0.002, 0.12)); add(ev(2, 4), tone(55, 0.6, 1.0, 0.002, 0.2))
    tc = ev(2, 6)
    while tc < ev(7, 16): add(tc, click(0.06, 3200)); tc += 1 / 14
    add(ev(3, 1), sweep(1200, 200, 0.8, 0.5)); add(ev(3, 5), tone(55, 0.8, 1.2, 0.002, 0.2)); add(ev(4, 1), sweep(200, 3000, 1.2, 0.5))
    for k in (6,): add(ev(5, k), click(0.5, 1500))
    add(ev(5, 14), tone(880, 1.2, 0.3, 0.003, 0.4)); add(ev(5, 15), sweep(400, 3000, 0.4, 0.4)); add(ev(5, 15) + 0.1, sweep(400, 3000, 0.4, 0.4))
    m = int((s(6) - s(5)) * SR); add(s(5), (np.convolve(r.randn(m), np.ones(40) / 40, "same") * 0.25 * np.sin(np.linspace(0, math.pi, m))).astype(np.float32))
    for q in range(8): add(ev(6, 3) + q * (0.7 - 0.06 * q), tone(660 + 60 * q, 0.25, 0.25, 0.002, 0.08))
    add(ev(6, 7), tone(65, 0.9, 1.1, 0.002, 0.25)); add(ev(6, 15), tone(1568, 1.5, 0.28, 0.003, 0.5)); add(ev(6, 15), tone(2093, 1.5, 0.15, 0.003, 0.5))
    add(s(7), sweep(4000, 200, ev(7, 2, 0) - s(7), 0.6)); tc = T_FL
    while tc < s(8): add(tc, click(0.25, 3400)); tc += 0.3
    add(ev(7, 17), tone(880, 0.8, 0.15, 0.003, 0.4)); add(ev(7, 19), tone(932, 1.0, 0.12, 0.003, 0.5)); add(ev(7, 23), tone(70, 0.8, 1.2, 0.002, 0.2))
    add(s(8) + 0.5, tone(1200, 0.8, 0.12, 0.01, 0.4))
    for f, g in ((440, 0.28), (554.4, 0.22), (659.3, 0.2), (880, 0.12)): add(ev(9, 1), tone(f, 3.5, g, 0.01, 1.4))
    add(ev(9, 4), click(1.0, 900)); add(ev(9, 4), tone(60, 0.6, 0.6, 0.002, 0.2))
    tk = [ev(10, 4), ev(10, 5), ev(10, 7)]; x = ev(10, 7)
    while x < s(13): x += 1.0; tk.append(x)
    for x in tk: add(x, click(0.5, 1300))
    add(ev(11, 2), tone(50, 0.7, 1.1, 0.002, 0.2)); add(ev(12, 2), sweep(1500, 300, 0.4, 0.4)); add(ev(12, 2) + 0.4, click(0.8, 1000))
    for f, g in ((440, 0.3), (554.4, 0.24), (659.3, 0.22), (880, 0.14)): add(ev(12, 3), tone(f, 2.6, g, 0.005, 1.0))
    add(ev(13, 8), tone(1046, 0.8, 0.2, 0.003, 0.25))
    a = np.tanh(a * 1.2) * 0.7 + vox * 1.0; a = np.tanh(a * 1.1) * 0.85; st = np.stack([a, a], 1); fn = f"{WK}/audio.wav"
    with wave.open(fn, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())
    return fn

def job(i):
    Image.fromarray(frame(i / FPS)).save(f"{WK}/f_{i:05d}.png", compress_level=1); return i

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import time
        print("TOTAL", round(TOTAL, 2), "S", [round(x, 2) for x in S])
        for x in sys.argv[1:]:
            t0 = time.time(); Image.fromarray(frame(float(x))).save(f"{WK}/pv_{float(x):05.2f}.png"); print(x, round(time.time() - t0, 2), flush=True)
        sys.exit()
    wav = audio(); nf = int(TOTAL * FPS)
    with Pool(4) as p:
        for k, _ in enumerate(p.imap_unordered(job, range(nf))):
            if k % 100 == 0: print(k, flush=True)
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-framerate", str(FPS), "-i", f"{WK}/f_%05d.png", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"{NAME}.mp4"], check=True)
    subprocess.run(f"rm -f {WK}/f_*.png", shell=True); print("END")
