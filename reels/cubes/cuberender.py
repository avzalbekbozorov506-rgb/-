"""Мини-рендер «кубических» 3D-сцен на numpy: коробки (можно поворачивать вокруг Z), перспектива, тень от солнца,
мягкое затемнение у предметов, блик на рёбрах (как скруглённые края), лица-«наклейки». Без Blender.
Мир: x вправо, y вглубь (от камеры), z вверх. Лица смотрят в −y (на камеру)."""
import numpy as np, math

class Box:
    __slots__ = ("c", "s", "col", "yaw", "decals", "tex", "glow", "shadow", "cs", "sn")
    def __init__(self, c, s, col, yaw=0.0, decals=(), tex=None, glow=False, shadow=True):
        self.c = np.array(c, np.float32); self.s = np.array(s, np.float32) / 2; self.col = np.array(col, np.float32) / 255
        self.yaw = yaw; self.decals = decals; self.tex = tex; self.glow = glow; self.shadow = shadow
        self.cs, self.sn = math.cos(yaw), math.sin(yaw)

def _rot(v, cs, sn):          # поворот вектора(ов) в локальный кадр коробки (на −yaw)
    return np.stack([v[..., 0] * cs + v[..., 1] * sn, -v[..., 0] * sn + v[..., 1] * cs, v[..., 2]], -1)
def _unrot(v, cs, sn):
    return np.stack([v[..., 0] * cs - v[..., 1] * sn, v[..., 0] * sn + v[..., 1] * cs, v[..., 2]], -1)

def hit_box(o, d, b):
    """o: (N,3) или (3,), d: (N,3). Возвращает t (N,) (inf если нет), ось и знак входа."""
    lo = _rot(o - b.c, b.cs, b.sn) if o.ndim > 1 else _rot((o - b.c)[None], b.cs, b.sn)[0]
    ld = _rot(d, b.cs, b.sn)
    with np.errstate(divide="ignore", invalid="ignore"):
        inv = 1.0 / np.where(np.abs(ld) < 1e-9, 1e-9, ld)
    t1 = (-b.s - lo) * inv; t2 = (b.s - lo) * inv
    tn = np.minimum(t1, t2); tf = np.maximum(t1, t2)
    tmin = tn.max(-1); tmax = tf.min(-1)
    ok = (tmax >= np.maximum(tmin, 1e-4)) & (tmin > 1e-4)
    return np.where(ok, tmin, np.inf), tn.argmax(-1), lo, ld

class Camera:
    def __init__(self, pos, target, fov=40, up=(0, 0, 1)):
        self.pos = np.array(pos, np.float32); f = np.array(target, np.float32) - self.pos; f /= np.linalg.norm(f)
        r = np.cross(f, np.array(up, np.float32)); r /= np.linalg.norm(r); u = np.cross(r, f)
        self.f, self.r, self.u, self.fov = f, r, u, fov
    def rays(self, W, H):
        k = math.tan(math.radians(self.fov) / 2)                      # fov — по вертикали
        xs = (np.arange(W, dtype=np.float32) + .5) / W * 2 - 1; ys = 1 - (np.arange(H, dtype=np.float32) + .5) / H * 2
        X, Y = np.meshgrid(xs * k * W / H, ys * k)
        d = self.f[None, None] + X[..., None] * self.r + Y[..., None] * self.u
        return (d / np.linalg.norm(d, axis=-1, keepdims=True)).reshape(-1, 3).astype(np.float32)

LIGHT = np.array([-0.45, -0.55, 0.70], np.float32); LIGHT /= np.linalg.norm(LIGHT)

def _surf(b, p, light):
    """Альбедо (с бликом на рёбрах), нормаль, lam для точек p на коробке b."""
    lp = _rot(p - b.c, b.cs, b.sn); rel = lp / b.s
    ax = np.abs(rel).argmax(-1); sgn = np.sign(np.take_along_axis(rel, ax[:, None], 1)[:, 0])
    nl = np.zeros_like(lp); nl[np.arange(len(lp)), ax] = sgn
    n = _unrot(nl, b.cs, b.sn)
    col = np.tile(b.col, (len(p), 1))
    if b.tex: col = b.tex(p, ax, sgn, col)
    front = (ax == 1) & (sgn < 0)
    for (u0, u1, v0, v1, dc) in b.decals:
        uu = lp[:, 0] / (2 * b.s[0]); vv = lp[:, 2] / (2 * b.s[2])
        mm = front & (uu >= u0) & (uu <= u1) & (vv >= v0) & (vv <= v1)
        col[mm] = np.array(dc, np.float32) / 255
    lam = np.clip(n @ light, 0, 1)
    if not b.glow:
        edge = np.abs(rel); edge[np.arange(len(lp)), ax] = 0
        de = (1 - edge.max(-1)) * b.s[np.argsort(-np.abs(rel), 1)[:, 1]]
        bev = np.clip(1 - de / 0.022, 0, 1)
        col = col * (1 + 0.16 * bev[:, None] * (lam[:, None] * .6 + .5))
    return col, n, lam

def _shadow(po, n, light, occ):
    sh = np.ones(len(po), np.float32)
    if not len(po): return sh
    sd = np.broadcast_to(light, po.shape)
    for b2 in occ:
        if not b2.shadow: continue
        t2, _, _, _ = hit_box(po, sd, b2)
        sh = np.where(np.isfinite(t2), 0.0, sh)
    return sh

def _bound(boxes):
    lo = np.array([1e9] * 3, np.float32); hi = -lo
    for b in boxes:
        r = np.abs(b.cs) * b.s[0] + np.abs(b.sn) * b.s[1], np.abs(b.sn) * b.s[0] + np.abs(b.cs) * b.s[1], b.s[2]
        lo = np.minimum(lo, b.c - r); hi = np.maximum(hi, b.c + r)
    return Box((lo + hi) / 2, hi - lo, (0, 0, 0))

class Shot:
    """Статичный фон одного плана: считается один раз; динамика (персонажи) дорисовывается покадрово."""
    def __init__(self, static, cam, W=360, H=640, sun=(1.0, .93, .82), amb=(.62, .64, .72), sun_k=.55, light=None):
        self.static, self.cam, self.W, self.H = static, cam, W, H
        self.L = LIGHT if light is None else (np.array(light, np.float32) / np.linalg.norm(light))
        self.sun, self.amb, self.sun_k = np.asarray(sun, np.float32), np.asarray(amb, np.float32), sun_k
        D = self.D = cam.rays(W, H); N = len(D)
        tb = np.full(N, np.inf, np.float32); idx = np.full(N, -1, np.int32)
        for k, b in enumerate(static):
            t, _, _, _ = hit_box(cam.pos, D, b); m = t < tb
            tb[m] = t[m]; idx[m] = k
        self.tb = tb; self.P = cam.pos + D * np.where(idx >= 0, tb, 0)[:, None]
        self.alb = np.zeros((N, 3), np.float32); self.alb[:] = (.1, .1, .14)
        self.n = np.zeros((N, 3), np.float32); self.lam = np.zeros(N, np.float32); self.sh = np.ones(N, np.float32)
        self.glow = np.zeros(N, bool)
        for k, b in enumerate(static):
            m = idx == k
            if not m.any(): continue
            col, n, lam = _surf(b, self.P[m], self.L)
            self.alb[m] = col; self.n[m] = n; self.lam[m] = lam; self.glow[m] = b.glow
            if not b.glow:
                self.sh[m] = _shadow(self.P[m] + n * 2e-3, n, self.L, [x for j, x in enumerate(static) if j != k])
        self.hit = idx >= 0

    def frame(self, dyn):
        N = len(self.D); alb, n, lam, sh, glow, tb = self.alb.copy(), self.n.copy(), self.lam.copy(), self.sh.copy(), self.glow.copy(), self.tb.copy()
        P = self.P
        if dyn:
            bb = _bound(dyn)
            # тень персонажей на фон
            cand = np.nonzero(self.hit & ~self.glow & (self.lam > 0))[0]
            po = P[cand] + n[cand] * 2e-3
            tt, _, _, _ = hit_box(po, np.broadcast_to(self.L, po.shape), bb)
            c2 = cand[np.isfinite(tt)]
            if len(c2):
                sh[c2] *= _shadow(P[c2] + n[c2] * 2e-3, n[c2], self.L, dyn)
            # сами персонажи
            tbb, _, _, _ = hit_box(self.cam.pos, self.D, bb); pix = np.nonzero(np.isfinite(tbb))[0]
            if len(pix):
                Dp = self.D[pix]; td = np.full(len(pix), np.inf, np.float32); ik = np.full(len(pix), -1)
                for k, b in enumerate(dyn):
                    t, _, _, _ = hit_box(self.cam.pos, Dp, b); m = t < td; td[m] = t[m]; ik[m] = k
                vis = np.isfinite(td) & (td < tb[pix])
                for k, b in enumerate(dyn):
                    m = vis & (ik == k)
                    if not m.any(): continue
                    q = pix[m]; p = self.cam.pos + Dp[m] * td[m][:, None]
                    col, nn, ll = _surf(b, p, self.L)
                    alb[q] = col; n[q] = nn; lam[q] = ll; glow[q] = b.glow
                    sh[q] = 1.0 if b.glow else _shadow(p + nn * 2e-3, nn, self.L, [x for x in self.static if x.shadow] + [x for j, x in enumerate(dyn) if j != k])
        shade = self.amb[None] * (0.78 + 0.22 * (n[:, 2:3] * .5 + .5)) + self.sun[None] * self.sun_k * (lam * sh)[:, None]
        img = np.where(glow[:, None], alb, alb * shade).reshape(self.H, self.W, 3)
        yy, xx = np.mgrid[0:self.H, 0:self.W]; v = 1 - 0.16 * (((xx / self.W - .5) ** 2 + (yy / self.H - .5) ** 2) * 2.2)
        img = np.clip(img * v[..., None], 0, 1) ** (1 / 1.05)
        return (img * 255 + .5).astype(np.uint8)
