"""Рендер «кубических» 3D-сцен на numpy (без Blender), уровень «студийный мультфильм».
Мир: x вправо, y вглубь, z вверх. Лица смотрят в −y.
Что внутри: перспектива, G-буфер, карта теней от солнца (мягкие, PCF), экранное затемнение у предметов (SSAO),
скруглённые рёбра (нормали), полусфера неба/пола, заполняющий и точечные тёплые огни, блик пластика, свечение (bloom),
глубина резкости, тональная кривая, зерно, виньетка, сглаживание краёв (4 подвыборки на краях).
Фон (Shot) считается один раз за план, персонажи дорисовываются покадрово только в своём прямоугольнике."""
import numpy as np, math
from PIL import Image, ImageFilter

class Box:
    __slots__ = ("c", "s", "col", "yaw", "decals", "tex", "glow", "shadow", "cs", "sn", "gloss", "rad", "glowk")
    def __init__(self, c, s, col, yaw=0.0, decals=(), tex=None, glow=False, shadow=True, gloss=0.0, rad=0.03, glowk=1.5):
        self.c = np.array(c, np.float32); self.s = np.array(s, np.float32) / 2; self.col = np.array(col, np.float32) / 255
        self.yaw = yaw; self.decals = decals; self.tex = tex; self.glow = glow; self.shadow = shadow
        self.cs, self.sn = math.cos(yaw), math.sin(yaw); self.gloss = gloss; self.rad = min(rad, float(self.s.min()) * .9); self.glowk = glowk

def _rot(v, cs, sn):
    return np.stack([v[..., 0] * cs + v[..., 1] * sn, -v[..., 0] * sn + v[..., 1] * cs, v[..., 2]], -1)
def _unrot(v, cs, sn):
    return np.stack([v[..., 0] * cs - v[..., 1] * sn, v[..., 0] * sn + v[..., 1] * cs, v[..., 2]], -1)

def hit_box(o, d, b):
    """o: (3,) или (N,3); d: (N,3). Возвращает t (inf если нет)."""
    o = np.asarray(o, np.float32)
    lo = _rot((o - b.c)[None] if o.ndim == 1 else o - b.c, b.cs, b.sn)
    ld = _rot(d, b.cs, b.sn)
    inv = 1.0 / np.where(np.abs(ld) < 1e-9, 1e-9, ld)
    t1 = (-b.s - lo) * inv; t2 = (b.s - lo) * inv
    tmin = np.minimum(t1, t2).max(-1); tmax = np.maximum(t1, t2).min(-1)
    ok = (tmax >= tmin) & (tmin > 1e-4)
    return np.where(ok, tmin, np.inf).astype(np.float32)

def corners(b, pad=0.0):
    s = b.s + pad; pts = np.array([[sx * s[0], sy * s[1], sz * s[2]] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], np.float32)
    return _unrot(pts, b.cs, b.sn) + b.c

# ---------- шум для текстур ----------
def _h(ix, iy, seed=0):
    n = (ix * 374761393 + iy * 668265263 + seed * 144665) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0
def vnoise(x, y, seed=0):
    xi, yi = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64); fx, fy = x - xi, y - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b_, c, d = _h(xi, yi, seed), _h(xi + 1, yi, seed), _h(xi, yi + 1, seed), _h(xi + 1, yi + 1, seed)
    return (a * (1 - fx) + b_ * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
def fbm(x, y, seed=0, o=3):
    s, a, tot = 0, 1.0, 0
    for i in range(o): s = s + a * vnoise(x * 2 ** i, y * 2 ** i, seed + i); tot += a; a *= .5
    return s / tot

class Camera:
    def __init__(self, pos, target, fov=40, up=(0, 0, 1)):
        self.pos = np.array(pos, np.float32); f = np.array(target, np.float32) - self.pos; f /= np.linalg.norm(f)
        r = np.cross(f, np.array(up, np.float32)); r /= np.linalg.norm(r); u = np.cross(r, f)
        self.f, self.r, self.u, self.fov = f, r, u, fov
    def rays(self, px, py, W, H):
        """px, py — координаты в пикселях (центр пикселя = i+.5). Любая форма массивов."""
        k = math.tan(math.radians(self.fov) / 2)
        X = (px / W * 2 - 1) * k * W / H; Y = (1 - py / H * 2) * k
        d = self.f + X[..., None] * self.r + Y[..., None] * self.u
        return (d / np.linalg.norm(d, axis=-1, keepdims=True)).astype(np.float32)
    def project(self, pts, W, H):
        v = pts - self.pos; z = v @ self.f; k = math.tan(math.radians(self.fov) / 2)
        z = np.maximum(z, 1e-3)
        x = (v @ self.r) / z / (k * W / H); y = (v @ self.u) / z / k
        return (x + 1) / 2 * W, (1 - y) / 2 * H, z

def _surf(b, p):
    """Альбедо, сглаженная нормаль (скруглённые рёбра), блеск для точек p на коробке b."""
    lp = _rot(p - b.c, b.cs, b.sn); rel = lp / b.s
    ax = np.abs(rel).argmax(-1); sgn = np.sign(np.take_along_axis(rel, ax[:, None], 1)[:, 0]); sgn[sgn == 0] = 1
    n = np.zeros_like(lp); n[np.arange(len(lp)), ax] = sgn
    r = b.rad
    for a in range(3):                                           # скругление: нормаль наклоняется к ближайшему ребру
        e = np.clip((np.abs(lp[:, a]) - (b.s[a] - r)) / r, 0, 1) * (ax != a)
        n[:, a] += np.sign(lp[:, a]) * e
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    nw = _unrot(n, b.cs, b.sn)
    col = np.tile(b.col, (len(p), 1))
    if b.tex: col = b.tex(p, ax, sgn, col)
    front = (ax == 1) & (sgn < 0)
    for (u0, u1, v0, v1, dc) in b.decals:
        uu = lp[:, 0] / (2 * b.s[0]); vv = lp[:, 2] / (2 * b.s[2])
        mm = front & (uu >= u0) & (uu <= u1) & (vv >= v0) & (vv <= v1)
        if mm.any(): col[mm] = np.array(dc, np.float32) / 255
    return col, nw

class Lights:
    def __init__(self, sun_dir=(-.45, -.55, .70), sun=(1.0, .90, .76), sky=(.60, .66, .86), ground=(.42, .32, .26),
                 fill_dir=(.6, -.5, .3), fill=(.20, .26, .36), points=(), shadow_soft=1.0):
        self.L = np.array(sun_dir, np.float32); self.L /= np.linalg.norm(self.L)
        self.Lf = np.array(fill_dir, np.float32); self.Lf /= np.linalg.norm(self.Lf)
        self.sun, self.sky, self.ground, self.fill = (np.asarray(v, np.float32) for v in (sun, sky, ground, fill))
        self.points = list(points); self.soft = shadow_soft

class ShadowMap:
    """Карта теней вдоль солнца: для каждой клетки — наибольшее w=p·L среди закрывающих предметов."""
    def __init__(self, L, region, texel=0.0028, maxres=2200):
        self.L = L; up = np.array([0, 0, 1], np.float32)
        U = np.cross(L, up); U /= np.linalg.norm(U); V = np.cross(L, U); self.U, self.V = U, V
        x0, x1, y0, y1, z0, z1 = region
        pts = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], np.float32)
        u, v, w = pts @ U, pts @ V, pts @ L
        self.u0, self.v0, self.w0 = float(u.min()), float(v.min()), float(w.max()) + 2.0
        self.texel = max(texel, max(u.max() - u.min(), v.max() - v.min()) / maxres)
        self.nu, self.nv = int(math.ceil((u.max() - u.min()) / self.texel)) + 1, int(math.ceil((v.max() - v.min()) / self.texel)) + 1
        self.w = np.full((self.nv, self.nu), -1e9, np.float32)
    def rect(self, b, pad=0.01):
        c = corners(b, pad); u = (c @ self.U - self.u0) / self.texel; v = (c @ self.V - self.v0) / self.texel
        return (max(int(u.min()) - 1, 0), min(int(u.max()) + 2, self.nu), max(int(v.min()) - 1, 0), min(int(v.max()) + 2, self.nv))
    def add(self, boxes):
        for b in boxes:
            if not b.shadow or b.glow: continue
            x0, x1, y0, y1 = self.rect(b)
            if x1 <= x0 or y1 <= y0: continue
            uu, vv = np.meshgrid((np.arange(x0, x1) + .5) * self.texel + self.u0, (np.arange(y0, y1) + .5) * self.texel + self.v0)
            o = (uu[..., None] * self.U + vv[..., None] * self.V + self.w0 * self.L).reshape(-1, 3).astype(np.float32)
            d = np.broadcast_to(-self.L, o.shape)
            t = hit_box(o, d, b).reshape(y1 - y0, x1 - x0)
            w = np.where(np.isfinite(t), self.w0 - t, -1e9).astype(np.float32)
            sub = self.w[y0:y1, x0:x1]; np.maximum(sub, w, out=sub)
    def lookup(self, p, nrm, extra=None, soft=1.0):
        """Доля света 0..1 в точках p: 9 отсчётов, шаг ~ мягкая полутень."""
        u = (p @ self.U - self.u0) / self.texel; v = (p @ self.V - self.v0) / self.texel; w = p @ self.L
        lam = np.clip(nrm @ self.L, 0, 1); bias = 0.007 + 0.016 * (1 - lam)
        step = 3.5 * soft; vis = np.zeros(len(p), np.float32); cnt = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                iu = np.clip((u + dx * step).astype(np.int32), 0, self.nu - 1); iv = np.clip((v + dy * step).astype(np.int32), 0, self.nv - 1)
                vis += (self.w[iv, iu] <= w + bias).astype(np.float32); cnt += 1
        return vis / cnt

def _ssao(depth, fpx, R=0.30, taps=16):
    h, w = depth.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rot = (np.sin(xx * 12.9898 + yy * 78.233) * 43758.5453) % 1.0 * 6.2832
    occ = np.zeros_like(depth)
    for k in range(taps):
        ang = rot + k * 2.399963; rad = math.sqrt((k + .5) / taps) * R * fpx / depth
        sx = np.clip((xx + np.cos(ang) * rad).astype(np.int32), 0, w - 1); sy = np.clip((yy + np.sin(ang) * rad).astype(np.int32), 0, h - 1)
        diff = depth - depth[sy, sx]
        occ += np.clip((diff - 0.015) / 0.05, 0, 1) * (diff < R * 1.3)
    ao = 1 - 1.15 * occ / taps
    im = Image.fromarray((np.clip(ao, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))
    return np.asarray(im, np.float32) / 255

def light_shade(lt, p, n, alb, gloss, glow, glowk, ao, sh, V):
    """Освещение: небо/пол, солнце (с тенью), заполняющий свет, точечные огни, блик, свечение."""
    nz = n[:, 2:3] * .5 + .5
    amb = lt.ground[None] + (lt.sky - lt.ground)[None] * nz
    lam = np.clip(n @ lt.L, 0, 1)[:, None]
    lamf = np.clip(n @ lt.Lf, 0, 1)[:, None]
    dif = amb * ao[:, None] * .78 + lt.sun[None] * lam * sh[:, None] * .86 + lt.fill[None] * lamf * (.5 + .5 * ao[:, None])
    for (pos, col, rad) in lt.points:
        dv = np.asarray(pos, np.float32)[None] - p; dist = np.linalg.norm(dv, axis=1, keepdims=True)
        att = np.clip(1 - dist / rad, 0, 1) ** 2 * np.clip((n * dv / np.maximum(dist, 1e-4)).sum(1, keepdims=True), 0, 1)
        dif = dif + np.asarray(col, np.float32)[None] * att * ao[:, None]
    out = alb * dif
    if np.any(gloss > 0):
        h = lt.L[None] + V; h /= np.linalg.norm(h, axis=1, keepdims=True)
        spec = (np.clip((n * h).sum(1), 0, 1) ** 48) * gloss * sh
        out = out + (lt.sun[None] * spec[:, None] * .9)
    out = np.where(glow[:, None], alb * glowk[:, None], out)
    return out

class Shot:
    """Один план: камера, статичный фон (G-буфер, карта теней, SSAO) считаются один раз."""
    def __init__(self, static, cam, W=1080, H=1920, lights=None, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(2.6, 1.4), grade=None, bloom=.35, grain=1.6, exposure=.50):
        self.exposure = exposure
        self.static, self.cam, self.W, self.H = list(static), cam, W, H
        self.lt = lights or Lights(); self.dof, self.bloom, self.grain = dof, bloom, grain
        self.fpx = H / 2 / math.tan(math.radians(cam.fov) / 2)
        self.sm = ShadowMap(self.lt.L, region); self.sm.add(self.static)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.D = cam.rays(xx + .5, yy + .5, W, H); self.xx, self.yy = xx, yy
        self.dfz = self.D @ cam.f
        N = H * W; Df = self.D.reshape(-1, 3)
        tb = np.full(N, np.inf, np.float32); idx = np.full(N, -1, np.int32)
        for k, b in enumerate(self.static):
            r = self._rect(b)
            if r is None: continue
            x0, x1, y0, y1 = r; sub = np.s_[y0:y1, x0:x1]
            t = hit_box(cam.pos, self.D[sub].reshape(-1, 3), b).reshape(y1 - y0, x1 - x0)
            cur = tb.reshape(H, W)[sub]; m = t < cur
            cur[m] = t[m]; idc = idx.reshape(H, W)[sub]; idc[m] = k
        self.tb = tb.reshape(H, W); self.idx = idx.reshape(H, W)
        self.depth = self.tb * self.dfz
        P = cam.pos + self.D * self.tb[..., None]; self.P = P.astype(np.float32)
        self.alb = np.zeros((H, W, 3), np.float32); self.n = np.zeros((H, W, 3), np.float32)
        self.gloss = np.zeros((H, W), np.float32); self.glow = np.zeros((H, W), bool); self.glowk = np.ones((H, W), np.float32)
        for k, b in enumerate(self.static):
            m = self.idx == k
            if not m.any(): continue
            col, nw = _surf(b, self.P[m]); self.alb[m] = col; self.n[m] = nw; self.gloss[m] = b.gloss; self.glow[m] = b.glow; self.glowk[m] = b.glowk
        self.ao = _ssao(self.depth, self.fpx)
        self.base = self._shade_region((0, H, 0, W), None)
        self.base_id = self.idx.copy()

    def _rect(self, b, pad=0.0, margin=2):
        c = corners(b, pad); x, y, z = self.cam.project(c, self.W, self.H)
        v = c - self.cam.pos
        if (v @ self.cam.f).min() < 0.05: return 0, self.W, 0, self.H
        x0, x1 = max(int(x.min()) - margin, 0), min(int(x.max()) + margin + 1, self.W); y0, y1 = max(int(y.min()) - margin, 0), min(int(y.max()) + margin + 1, self.H)
        return (x0, x1, y0, y1) if x1 > x0 and y1 > y0 else None

    def _shade_region(self, rect, dyn):
        y0, y1, x0, x1 = rect; sl = np.s_[y0:y1, x0:x1]; h, w = y1 - y0, x1 - x0
        t = self.tb[sl].copy(); ids = self.idx[sl].copy()
        P, n, alb, gloss, glow, glowk = (a[sl].copy() for a in (self.P, self.n, self.alb, self.gloss, self.glow, self.glowk))
        D = self.D[sl]
        if dyn:
            tb2 = np.full((h, w), np.inf, np.float32); ik = np.full((h, w), -1, np.int32)
            for k, b in enumerate(dyn):
                r = self._rect(b)
                if r is None: continue
                bx0, bx1, by0, by1 = max(r[0], x0), min(r[1], x1), max(r[2], y0), min(r[3], y1)
                if bx1 <= bx0 or by1 <= by0: continue
                s2 = np.s_[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0]
                tt = hit_box(self.cam.pos, D[s2].reshape(-1, 3), b).reshape(by1 - by0, bx1 - bx0)
                cur = tb2[s2]; m = tt < cur; cur[m] = tt[m]; ik[s2][m] = k
            vis = tb2 < t
            for k, b in enumerate(dyn):
                m = vis & (ik == k)
                if not m.any(): continue
                p = self.cam.pos + D[m] * tb2[m][:, None]; col, nw = _surf(b, p)
                P[m] = p; alb[m] = col; n[m] = nw; gloss[m] = b.gloss; glow[m] = b.glow; glowk[m] = b.glowk; ids[m] = 1000 + k
            t = np.where(vis, tb2, t)
        depth = t * self.dfz[sl]
        if dyn:
            dm = ShadowMap.__new__(ShadowMap); dm.__dict__.update(self.sm.__dict__); dm.w = np.full_like(self.sm.w, -1e9)
            dm.add(dyn)
            # AO по глубине в прямоугольнике с запасом
            ao = _ssao(depth, self.fpx)
        else:
            dm = None; ao = self.ao[sl]
        Pf, nf = P.reshape(-1, 3), n.reshape(-1, 3)
        sh = self.sm.lookup(Pf, nf, soft=self.lt.soft)
        if dm is not None: sh = np.minimum(sh, dm.lookup(Pf, nf, soft=self.lt.soft))
        V = -D.reshape(-1, 3)
        hdr = light_shade(self.lt, Pf, nf, alb.reshape(-1, 3), gloss.reshape(-1), glow.reshape(-1), glowk.reshape(-1), ao.reshape(-1), sh, V).reshape(h, w, 3)
        self._last = dict(ids=ids, depth=depth, ao=ao, sh=sh.reshape(h, w), hdr=hdr, dyn=dyn, rect=rect, t=t)
        self._aa(hdr, ids, ao, sh.reshape(h, w), rect, dyn)
        return hdr, ids, depth

    def _aa(self, hdr, ids, ao, sh, rect, dyn):
        """Сглаживание краёв: на границах объектов и наклеек — 4 подвыборки."""
        y0, y1, x0, x1 = rect; h, w = ids.shape
        luma = hdr.mean(-1); e = np.zeros((h, w), bool)
        e[:, 1:] |= ids[:, 1:] != ids[:, :-1]; e[:, :-1] |= ids[:, 1:] != ids[:, :-1]
        e[1:] |= ids[1:] != ids[:-1]; e[:-1] |= ids[1:] != ids[:-1]
        gx = np.abs(np.diff(luma, axis=1)) > .08; gy = np.abs(np.diff(luma, axis=0)) > .08
        e[:, 1:] |= gx; e[:, :-1] |= gx; e[1:] |= gy; e[:-1] |= gy
        py, px = np.nonzero(e)
        if len(py) == 0: return
        boxes_all = self.static + (list(dyn) if dyn else [])
        gid = lambda k: k if k < 1000 else len(self.static) + (k - 1000)
        idp = np.pad(ids, 1, mode="edge"); nb = np.stack([idp[py + 1, px + 1], idp[py + 1, px], idp[py + 1, px + 2], idp[py, px + 1], idp[py + 2, px + 1]], 1)
        acc = np.zeros((len(py), 3), np.float32); offs = [(-.25, -.25), (.25, -.25), (-.25, .25), (.25, .25)]
        for ox, oy in offs:
            D = self.cam.rays(px + x0 + .5 + ox, py + y0 + .5 + oy, self.W, self.H)
            tb = np.full(len(py), np.inf, np.float32); ik = np.full(len(py), -1, np.int32)
            for k in np.unique(nb):
                if k < 0: continue
                b = boxes_all[gid(int(k))]; m = (nb == k).any(1)
                t = hit_box(self.cam.pos, D[m], b); cur = tb[m]; better = t < cur
                sub = np.nonzero(m)[0][better]; tb[sub] = t[better]; ik[sub] = gid(int(k))
            ok = ik >= 0; col = hdr[py, px].copy()
            for kk in np.unique(ik[ok]):
                m = ik == kk; b = boxes_all[kk]; p = self.cam.pos + D[m] * tb[m][:, None]
                alb, nw = _surf(b, p)
                col[m] = light_shade(self.lt, p, nw, alb, np.full(len(p), b.gloss, np.float32), np.full(len(p), b.glow), np.full(len(p), b.glowk, np.float32),
                                     ao[py[m], px[m]], sh[py[m], px[m]], -D[m])
            acc += col
        hdr[py, px] = acc / 4

    def render(self, dyn):
        H, W = self.H, self.W
        hdr, dep, ids = self.base.copy() if False else self.base[0].copy(), self.base[2].copy(), self.base[1]
        if dyn:
            pts = np.concatenate([corners(b) for b in dyn]); sh = pts - self.lt.L * 1.4
            x, y, z = self.cam.project(np.concatenate([pts, sh]), W, H)
            x0, x1 = max(int(x.min()) - 110, 0), min(int(x.max()) + 110, W); y0, y1 = max(int(y.min()) - 110, 0), min(int(y.max()) + 110, H)
            h2, i2, d2 = self._shade_region((y0, y1, x0, x1), dyn)
            fw = np.ones((y1 - y0, x1 - x0), np.float32); ramp = np.linspace(0, 1, 36, dtype=np.float32)
            if y0 > 0: fw[:36] *= ramp[:, None]
            if y1 < H: fw[-36:] *= ramp[::-1, None]
            if x0 > 0: fw[:, :36] *= ramp[None]
            if x1 < W: fw[:, -36:] *= ramp[::-1][None]
            hdr[y0:y1, x0:x1] = hdr[y0:y1, x0:x1] * (1 - fw[..., None]) + h2 * fw[..., None]; dep[y0:y1, x0:x1] = np.where(fw > .5, d2, dep[y0:y1, x0:x1])
        return self._post(hdr, dep)

    def _post(self, hdr, depth):
        H, W = self.H, self.W
        # свечение ярких мест
        br = np.clip(hdr - 1.0, 0, None)
        if self.bloom > 0 and br.max() > 0:
            sm = Image.fromarray((np.clip(br / 1.5, 0, 1) * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
            hdr = hdr + np.asarray(sm, np.float32) / 255 * 1.5 * self.bloom
        # тональная кривая (фильмовая) + мягкий контраст
        x = hdr * self.exposure
        a, b_, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
        ldr = np.clip((x * (a * x + b_)) / (x * (c * x + d) + e), 0, 1)
        ldr = ldr ** (1 / 2.2)
        g = ldr.mean(-1, keepdims=True); ldr = np.clip(g + (ldr - g) * 1.14, 0, 1)
        # глубина резкости: фон за предметом чуть размыт
        focus, rng = self.dof
        wgt = np.clip((depth - focus) / rng, 0, 1)[..., None] * .85
        if wgt.max() > 0.02:
            im = Image.fromarray((ldr * 255 + .5).astype(np.uint8))
            bl = np.asarray(im.filter(ImageFilter.GaussianBlur(3.2)), np.float32) / 255
            ldr = ldr * (1 - wgt) + bl * wgt
        # виньетка и зерно
        v = 1 - 0.20 * (((self.xx / W - .5) ** 2 + (self.yy / H - .5) ** 2) * 2.0)
        ldr = ldr * v[..., None]
        rs = np.random.RandomState(7); ldr = ldr + rs.randn(H, W, 1).astype(np.float32) * self.grain / 255
        return (np.clip(ldr, 0, 1) * 255 + .5).astype(np.uint8)
