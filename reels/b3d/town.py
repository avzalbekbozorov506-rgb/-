"""Город Возрождения: дома с черепичными крышами, ставни, окна, колокольня; снег; холмы Романьи."""
import math, random
import bpy
import kit

PLASTER = [(0.78, 0.6, 0.42), (0.72, 0.45, 0.32), (0.82, 0.72, 0.56), (0.66, 0.52, 0.4), (0.76, 0.56, 0.36), (0.6, 0.4, 0.3)]
def mats(snow):
    M = {}
    M["roof"] = kit.mat("roof", (0.55, 0.27, 0.17), rough=0.75, noise=0.35, nscale=6)
    M["snow"] = kit.mat("snow", (0.9, 0.92, 0.96), rough=0.45, sss=0.3, noise=0.08, nscale=10)
    M["wood"] = kit.mat("shutter", (0.3, 0.2, 0.12), rough=0.7, noise=0.4, nscale=20)
    M["dark"] = kit.mat("win", (0.03, 0.025, 0.02), rough=0.3)
    M["warm"] = kit.mat("winw", (1, 0.7, 0.4), emit=(1, 0.62, 0.3), emit_k=6)
    M["stone"] = kit.mat("tstone", (0.55, 0.5, 0.44), rough=0.85, noise=0.4, nscale=5)
    M["ground"] = M["snow"] if snow else kit.mat("cobble", (0.42, 0.38, 0.34), rough=0.7, noise=0.5, nscale=14)
    M["pl"] = [kit.mat(f"pl{k}", c, rough=0.9, noise=0.25, nscale=3) for k, c in enumerate(PLASTER)]
    return M

def house(M, x, y, w, d, h, rot=0, snow=False, lit=0.3, rnd=random):
    pl = rnd.choice(M["pl"]); g = bpy.data.objects.new("house", None); bpy.context.scene.collection.objects.link(g); g.location = (x, y, 0); g.rotation_euler[2] = math.radians(rot)
    b = kit.box("hb", (w, d, h), (0, 0, h / 2), pl); b.parent = g
    r = kit.prism_roof("roof", w, d, 0.32 * d, (0, 0, h), M["roof"]); r.parent = g
    if snow:
        s = kit.prism_roof("sroof", w * 0.98, d * 0.98, 0.32 * d, (0, 0, h + 0.13), M["snow"], over=0.2); s.parent = g
    floors = max(1, int(h / 2.6))
    for fl in range(floors):
        zz = 1.6 + fl * 2.6 if fl else 1.3
        n = max(1, int(w / 1.6))
        for k in range(n):
            xx = -w / 2 + (k + 0.5) * w / n
            if fl == 0 and k == n // 2:                                         # дверь
                kit.box("door", (0.9, 0.08, 1.9), (xx, -d / 2 - 0.02, 0.95), M["wood"]).parent = g; continue
            lit_ = rnd.random() < lit
            kit.box("win", (0.62, 0.1, 0.95), (xx, -d / 2 - 0.01, zz), M["warm"] if lit_ else M["dark"]).parent = g
            for s_ in (-1, 1):
                if rnd.random() < 0.7: kit.box("sh", (0.33, 0.06, 1.0), (xx + s_ * 0.5, -d / 2 - 0.05, zz), M["wood"]).parent = g
            kit.box("sill", (0.8, 0.18, 0.08), (xx, -d / 2 - 0.06, zz - 0.52), M["stone"]).parent = g
            if lit_: kit.point("wl", (xx, -d / 2 - 0.6, zz), 25, (1, 0.62, 0.3), radius=0.3).parent = g
    return g

def tower(M, x, y, h=22, w=3.2, snow=False):
    kit.box("tower", (w, w, h), (x, y, h / 2), M["stone"])
    for k in range(4):
        a = k * math.pi / 2; kit.box("bell", (0.8, 0.3, 1.8), (x + math.sin(a) * w / 2, y - math.cos(a) * w / 2, h - 2.2), M["dark"], rot=(0, 0, math.degrees(a)))
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=w * 0.78, depth=4.0, location=(x, y, h + 2.0), rotation=(0, 0, math.pi / 4))
    c = bpy.context.object; c.data.materials.append(M["roof"])

def street(M, snow=False, seed=3, length=40, width=7, lit=0.35):
    """Улица вдоль +Y: дома с двух сторон, фасадами к улице."""
    rnd = random.Random(seed); kit.box("ground", (60, 120, 0.2), (0, length / 2, -0.1), M["ground"])
    for side in (-1, 1):
        y = -4
        while y < length:
            w = rnd.uniform(4, 6.5); h = rnd.uniform(6, 10)
            house(M, side * (width / 2 + 3), y + w / 2, w, 6, h, rot=-90 * side, snow=snow, lit=lit, rnd=rnd); y += w + rnd.uniform(0, 0.3)

def square(M, snow=True, seed=5, R=13, lit=0.25):
    """Площадь: дома по кругу, фасадами к центру; колокольня за ними."""
    rnd = random.Random(seed); kit.box("ground", (120, 120, 0.2), (0, 0, -0.1), M["ground"])
    a = -150
    while a < 150:
        w = rnd.uniform(5, 7.5); h = rnd.uniform(7, 11); ar = math.radians(a)
        house(M, R * math.sin(ar), R * math.cos(ar), w, 6, h, rot=-a, snow=snow, lit=lit, rnd=rnd)
        a += math.degrees(w / R) + 1
    tower(M, -6, 20, snow=snow)

def hill_town(M):
    """Общий план: город-крепость на холме, слои дальних холмов в дымке."""
    grass = kit.mat("grass", (0.42, 0.42, 0.26), rough=0.9, noise=0.45, nscale=0.4)
    far = kit.mat("farhill", (0.36, 0.38, 0.36), rough=0.95, noise=0.3, nscale=0.2)
    kit.sphere("hill", 1.0, (0, 90, -38), grass, scale=(70, 45, 52), seg=96)
    for k, (x, y, sx, sz) in enumerate(((-120, 260, 140, 60), (140, 300, 160, 70), (0, 420, 260, 90), (-260, 460, 200, 80))):
        kit.sphere(f"fh{k}", 1.0, (x, y, -sz * 0.55), far, scale=(sx, sx * 0.6, sz), seg=64)
    rnd = random.Random(11)
    for k in range(34):                                                       # дома по склону и вершине
        a = rnd.uniform(-1.4, 1.4); r = rnd.uniform(4, 30); x = r * math.sin(a); y = 90 - 45 * 0.55 + r * 0.4 * math.cos(a) * -1 + rnd.uniform(-4, 8)
        z = 52 * math.sqrt(max(0.0, 1 - (x / 70) ** 2 - ((y - 90) / 45) ** 2)) - 38 - 0.5
        house(M, x, y, rnd.uniform(4, 6), 5, rnd.uniform(5, 8), rot=rnd.uniform(-25, 25), lit=0.4, rnd=rnd).location.z = z
    tower(M, 4, 92, h=24); tower(M, -10, 95, h=18, w=2.6)
    kit.box("wallR", (40, 2, 6), (0, 104, 15), M["stone"])
