"""Лепка формой расстояния (SDF): примитивы с плавным слиянием → меш через marching cubes.
Все функции принимают массив точек P (N,3) и возвращают расстояние (N,)."""
import numpy as np
from skimage.measure import marching_cubes

def _rot(P, c, rot):
    Q = P - np.asarray(c, float)
    if rot is None: return Q
    from mathutils import Euler
    import math
    M = np.array(Euler([math.radians(a) for a in rot]).to_matrix())
    return Q @ M                                                         # обратный поворот (M ортогональна)
def sph(P, c, r): return np.linalg.norm(P - np.asarray(c, float), axis=1) - r
def ell(P, c, r, rot=None):
    Q = _rot(P, c, rot); r = np.asarray(r, float)
    k0 = np.linalg.norm(Q / r, axis=1); k1 = np.linalg.norm(Q / (r * r), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)
def cap(P, a, b, r):
    a = np.asarray(a, float); b = np.asarray(b, float); pa = P - a; ba = b - a
    h = np.clip(pa @ ba / (ba @ ba), 0, 1); return np.linalg.norm(pa - h[:, None] * ba, axis=1) - r
def rcone(P, a, b, ra, rb):
    """Конус со скруглёнными концами (радиус ra у a, rb у b) — для носа, челюсти, рук."""
    a = np.asarray(a, float); b = np.asarray(b, float); ba = b - a; l2 = ba @ ba; rr = ra - rb; a2 = l2 - rr * rr; il2 = 1.0 / l2
    pa = P - a; y = pa @ ba; z = y - l2
    x = pa * l2 - y[:, None] * ba; x2 = (x * x).sum(1); y2 = y * y * l2; z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d = np.where(np.sign(z) * a2 * z2 > k, np.sqrt(x2 + z2) * il2 - rb,
        np.where(np.sign(y) * a2 * y2 < k, np.sqrt(x2 + y2) * il2 - ra, (np.sqrt(x2 * a2 * il2) + y * rr) * il2 - ra))
    return d
def rbox(P, c, half, r=0.0, rot=None):
    Q = np.abs(_rot(P, c, rot)) - (np.asarray(half, float) - r)
    return np.linalg.norm(np.maximum(Q, 0), axis=1) + np.minimum(Q.max(1), 0) - r
def plane(P, n, o):
    n = np.asarray(n, float); n = n / np.linalg.norm(n); return (P - np.asarray(o, float)) @ n
def smin(a, b, k):
    if k <= 0: return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)
def smax(a, b, k): return -smin(-a, -b, k)
def sub(a, b, k=0.0): return smax(a, -b, k)                          # a минус b

def mesh(name, fn, lo, hi, step, material=None, parent=None, smooth_iter=2):
    import bpy
    lo = np.asarray(lo, float); hi = np.asarray(hi, float); n = np.ceil((hi - lo) / step).astype(int) + 1
    xs, ys, zs = [lo[i] + np.arange(n[i]) * step for i in range(3)]
    G = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    V = np.empty(len(G), np.float32)
    for i in range(0, len(G), 2_000_000): V[i:i + 2_000_000] = fn(G[i:i + 2_000_000])
    V = V.reshape(n)
    V[0, :, :] = V[-1, :, :] = V[:, 0, :] = V[:, -1, :] = V[:, :, 0] = V[:, :, -1] = step     # закрытые края
    v, f, _, _ = marching_cubes(V, 0.0, spacing=(step, step, step))
    v = v + lo
    me = bpy.data.meshes.new(name); me.from_pydata(v.tolist(), [], f[:, ::-1].tolist()); me.update()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    if smooth_iter:
        m = ob.modifiers.new("s", "SMOOTH"); m.iterations = smooth_iter; m.factor = 0.5
    if material: me.materials.append(material)
    if parent: ob.parent = parent
    return ob
