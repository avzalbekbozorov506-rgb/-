"""Обтекание крыла для моушен-графики: профиль Жуковского, потенциальный поток с циркуляцией по условию Кутты.
Поле давления (Cp = 1 - |V|^2/U^2), линии тока с частицами, подъёмная сила ∝ циркуляции (теорема Жуковского). Всё считается numpy.
Рисунок: поток слева направо горизонтально, крыло наклонено на угол атаки (картинка повёрнута на -α)."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H = 1080, 1920
MU = complex(-0.09, 0.09); C = 1.0; R = abs(C - MU); BETA = math.asin(MU.imag / R)
def set_camber(my=0.09, mx=-0.09):
    """Изгиб профиля (закрылки/предкрылки увеличивают кривизну): меняет MU, R, BETA."""
    global MU, R, BETA
    MU = complex(mx, my); R = abs(C - MU); BETA = math.asin(MU.imag / R)
def gamma(alpha, U=1.0): return 4 * math.pi * U * R * math.sin(alpha + BETA)
def lift_coef(alpha): return 2 * math.pi * math.sin(alpha + BETA) * R / 2.0      # ~ Cl (хорда ≈ 4)
def to_zeta(z):
    s = np.sqrt(z * z - 4 * C * C + 0j); z1 = (z + s) / 2; z2 = (z - s) / 2
    return np.where(np.abs(z1 - MU) >= np.abs(z2 - MU), z1, z2)
def vel(z, alpha, U=1.0):
    zt = to_zeta(z); G = gamma(alpha, U); d = zt - MU
    w = U * np.exp(-1j * alpha) - U * np.exp(1j * alpha) * R * R / (d * d) + 1j * G / (2 * math.pi * d)
    dz = 1 - C * C / (zt * zt); v = w / np.where(np.abs(dz) < 1e-3, 1e-3, dz)
    return np.conj(v), np.abs(d) < R * 1.0005                                    # скорость (u + iv), внутри профиля
def outline(n=240):
    th = np.linspace(0, 2 * math.pi, n); zt = MU + R * np.exp(1j * th); return zt + C * C / zt
class View:
    """Экран: центр (cx, cy), масштаб px на единицу, поворот картинки на -alpha (крыло наклоняется, поток горизонтален)."""
    def __init__(self, cx=540, cy=640, scale=215, alpha=0.0): self.cx, self.cy, self.s, self.a = cx, cy, scale, alpha
    def to_screen(self, z):
        z = np.asarray(z) * np.exp(-1j * self.a); return self.cx + z.real * self.s, self.cy - z.imag * self.s
    def from_screen(self, x, y): return ((x - self.cx) / self.s - 1j * (y - self.cy) / self.s) * np.exp(1j * self.a)
_YY, _XX = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
def pressure_layer(view, alpha, y0=250, y1=1100, strength=1.0):
    """RGBA-слой поля давления (половинное разрешение -> полное): синее = разрежение, оранжевое = избыточное давление."""
    z = view.from_screen(_XX * 2.0, _YY * 2.0); v, inside = vel(z, alpha)
    cp = 1 - np.abs(v) ** 2; cp = np.clip(cp, -3, 1)
    low = np.clip(-cp / 1.6, 0, 1) ** 0.8; high = np.clip(cp / 0.9, 0, 1) ** 1.1
    rgb = np.zeros(z.shape + (3,), np.float32)
    rgb += low[..., None] * np.array([40, 140, 255], np.float32); rgb += high[..., None] * np.array([255, 120, 40], np.float32)
    a = np.clip((low * 0.8 + high * 0.8), 0, 1) * 200 * strength; a[inside] = 0
    yy = _YY * 2; a *= np.clip((yy - y0) / 80, 0, 1) * np.clip((y1 - yy) / 80, 0, 1)
    im = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(3))
    return im.resize((W, H), Image.BILINEAR)
_CACHE = {}
def streamlines(alpha, n=34, steps=520, dt=0.016, ymin=-1.9, ymax=1.9, x0=-4.2):
    """Траектории частиц из набегающего потока (в системе крыла): массив [шаг, линия] комплексных координат."""
    key = (round(alpha, 4), n, steps, MU)
    if key in _CACHE: return _CACHE[key]
    ys = np.linspace(ymin, ymax, n); p = (x0 + 1j * ys) * np.exp(1j * alpha)       # стартовая линия перпендикулярно потоку
    out = np.zeros((steps, n), complex); alive = np.ones(n, bool)
    for k in range(steps):
        out[k] = p; v1, ins = vel(p, alpha); pm = p + 0.5 * dt * v1; v2, _ = vel(pm, alpha); p = p + dt * v2
    if len(_CACHE) > 40: _CACHE.clear()
    _CACHE[key] = out; return out
def draw_particles(lay, view, alpha, lt, rate=60, gap=22, trail=7, col_fast=(170, 225, 255), col_slow=(255, 255, 255), a=1.0, chaos=0.0, width=3):
    d = ImageDraw.Draw(lay); tr = streamlines(alpha); steps, n = tr.shape; rng = np.random.default_rng(3)
    base = int(lt * rate)
    for j in range(n):
        for k in range(0, steps, gap):
            idx = (base + k + j * 7) % steps
            if idx < trail: continue
            seg = tr[idx - trail:idx + 1, j]
            if chaos > 0:
                xx = seg.real
                jitter = chaos * np.clip(xx + 0.5, 0, None) * (np.sin(idx * 0.37 + j) * 0.25 + 1j * np.cos(idx * 0.29 + j * 1.7) * 0.25)
                seg = seg + jitter * (seg.imag > -0.1)
            sx, sy = view.to_screen(seg); sp = abs(seg[-1] - seg[0]) / (trail * 0.016)
            c = tuple(int(col_slow[i] + (col_fast[i] - col_slow[i]) * min(1, max(0, (sp - 0.7) / 0.9))) for i in range(3))
            if not (200 < sy[-1] < 1110): continue
            d.line(list(zip(sx, sy)), fill=c + (int(220 * a),), width=width)
def wing_shape(lay, view, col=(30, 36, 50), rim=(190, 205, 230), flap=0.0):
    d = ImageDraw.Draw(lay); z = outline(); sx, sy = view.to_screen(z); pts = list(zip(sx, sy))
    d.polygon(pts, fill=col + (255,)); d.line(pts + [pts[0]], fill=rim + (255,), width=4)
    return pts
