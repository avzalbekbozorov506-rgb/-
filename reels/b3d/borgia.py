"""Ролик «Чезаре и Рамиро»: каждая сцена — отдельный 3D-кадр (Cycles) + кадр с закрытыми глазами для моргания.
Запуск: python3 borgia.py <сцена> [сэмплы] [процент разрешения]   → work/borgia/<сцена>.png (+ _blink.png, _blink.json)"""
import sys, os, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
import kit, sets, town, cast, chars

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "borgia"); os.makedirs(OUT, exist_ok=True)
RES = (1296, 2304)                                               # с запасом 1.2× под движение камеры
def rad(*a): return tuple(math.radians(x) for x in a)
def look(c, yaw=0, pitch=0, roll=0): c["head"].rotation_euler = rad(pitch, roll, yaw)

def torch(name, co, k=1.0):
    wood = kit.mat(name + "w", (0.3, 0.2, 0.12), rough=0.8); kit.cylinder(name, 0.025, 0.6, (co[0], co[1], co[2] - 0.3), wood, seg=12)
    fl = kit.mat(name + "f", (1, 0.6, 0.2), emit=(1, 0.5, 0.15), emit_k=25); kit.sphere(name + "_f", 0.06, (co[0], co[1], co[2] + 0.06), fl, scale=(1, 1, 1.9), seg=16)
    kit.point(name + "_L", (co[0], co[1], co[2] + 0.15), 160 * k, (1, 0.55, 0.25), radius=0.1)

def chess(at, white=False, knocked=False):
    m = kit.mat("chw" if white else "chb", (0.86, 0.8, 0.68) if white else (0.06, 0.05, 0.05), rough=0.25, coat=0.6)
    x, y, z = at; g = kit.empty("piece", at)
    kit.cylinder("pb", 0.03, 0.012, (0, 0, 0.006), m, parent=g); kit.cylinder("pt", 0.022, 0.07, (0, 0, 0.045), m, r2=0.012, parent=g)
    kit.sphere("ph", 0.016, (0, 0, 0.088), m, parent=g); kit.cylinder("pk", 0.004, 0.03, (0, 0, 0.115), m, parent=g); kit.box("pk2", (0.022, 0.006, 0.006), (0, 0, 0.118), m, parent=g)
    if knocked: g.rotation_euler = rad(0, 85, 30); g.location.z += 0.03
    return g

# ---------- сцены ----------
def s_hook():
    sets.hall(); c = cast.cesare(at=(0, 0.25, 0)); look(c, -10, 3)
    kit.area("key", (-0.9, -0.8, 1.2), (0, 0.25, 1.65), 28, size=0.6, color=(1.0, 0.7, 0.42))
    kit.area("fillw", (0, -2.5, 2.5), (0, 2.5, 1.5), 60, size=3, color=(0.5, 0.6, 0.85))
    kit.area("rim", (1.2, 1.4, 2.2), (0, 0.25, 1.6), 200, size=0.5, color=(0.65, 0.78, 1.0))
    kit.world((0.03, 0.035, 0.05), 1.0, fog=0.012, fog_color=(0.9, 0.85, 0.8))
    kit.camera((0.22, -0.95, 1.62), (0.0, 0.25, 1.6), lens=40, fstop=2.2, focus=(0, 0.17, 1.63)); return [c]

def s_cta():
    sets.hall(); c = cast.cesare(at=(0, 0.25, 0)); look(c, 4, -2)
    kit.area("key", (0.9, -0.9, 1.3), (0, 0.25, 1.65), 30, size=0.6, color=(1.0, 0.6, 0.35))
    kit.area("rim", (-1.2, 1.4, 2.2), (0, 0.25, 1.6), 200, size=0.5, color=(1.0, 0.35, 0.3))
    kit.world((0.02, 0.02, 0.03), 1.0, fog=0.014, fog_color=(0.9, 0.7, 0.65))
    kit.camera((-0.05, -0.6, 1.66), (0.0, 0.25, 1.64), lens=40, fstop=2.0, focus=(0, 0.16, 1.65)); return [c]

def s_romagna():
    M = town.mats(False); town.hill_town(M)
    kit.sky([(-1, (0.5, 0.36, 0.3)), (0.0, (1.0, 0.62, 0.36)), (0.08, (0.95, 0.55, 0.42)), (0.25, (0.45, 0.38, 0.55)), (0.6, (0.15, 0.17, 0.35))], 2.5)
    kit.sun("sun", (80, 0, 200), 3.0, (1, 0.62, 0.38), angle=3); kit.sun("fill", (50, 0, 20), 0.4, (0.6, 0.65, 0.9), angle=20)
    kit.camera((18, -95, 6), (-2, 80, 20), lens=55, fstop=0); return []

def s_remirro():
    M = town.mats(False); town.street(M, lit=0.4)
    c = cast.remirro(at=(0, 3, 0)); look(c, 8, 6)
    torch("t1", (-0.45, 2.7, 1.55), 0.35)
    kit.area("rim", (1.2, 4.5, 2.4), (0, 3, 1.6), 260, size=0.6, color=(0.55, 0.7, 1.0))
    kit.world((0.02, 0.03, 0.06), 1.0, fog=0.03, fog_color=(0.7, 0.75, 0.9))
    kit.camera((0.15, 2.05, 1.58), (0, 3, 1.64), lens=38, fstop=2.0, focus=(0, 2.9, 1.66)); return [c]

def s_fear():
    M = town.mats(False); town.street(M, seed=4, lit=0.15)
    r = cast.remirro(at=(0.4, 14, 0), rot_z=-8); look(r, 0, 6); torch("t1", (0.0, 13.6, 1.5), 0.6)
    for k, (x, y) in enumerate(((-1.3, 15.5), (2.0, 16.0))):
        g = chars.man(f"Guard{k}", at=(x, y, 0), skin=(0.7, 0.5, 0.38), coat=(0.45, 0.44, 0.43), armor=True, beard=k == 0, hair_style="short", hat=None, gold=False, lids=0.5, frown=0.8, step=0.003)
        torch(f"gt{k}", (x + 0.35, y - 0.3, 1.55), 0.5)
    t = cast.townsman(0, at=(3.1, 3.2, 0), rot_z=-150, step=0.0018); look(t, -20, 4)
    kit.box("doorframe", (0.2, 1.2, 2.6), (2.6, 3.0, 1.3), M["stone"])
    kit.area("moon", (-6, 30, 14), (0, 10, 0), 900, size=3, color=(0.5, 0.62, 1.0))
    kit.world((0.01, 0.015, 0.035), 1.0, fog=0.025, fog_color=(0.6, 0.7, 0.95))
    kit.camera((3.25, 1.4, 1.62), (1.2, 12, 1.4), lens=30, fstop=2.8, focus=(0.4, 14, 1.6)); return [t]

def s_move():
    sets.hall(window=False); c = cast.cesare(at=(0.1, 0.55, 0)); look(c, 0, 18)
    wood = kit.mat("board", (0.3, 0.17, 0.08), rough=0.4, coat=0.4, noise=0.4, nscale=30)
    kit.box("tableC", (1.4, 0.9, 0.06), (0, -0.2, 0.86), wood, bevel=0.01)
    lb = kit.mat("sqL", (0.82, 0.74, 0.6), rough=0.3, coat=0.5); db = kit.mat("sqD", (0.18, 0.1, 0.06), rough=0.3, coat=0.5)
    for i in range(8):
        for j in range(8): kit.box("sq", (0.05, 0.05, 0.01), (-0.2 + i * 0.05, -0.45 + j * 0.05, 0.895), lb if (i + j) % 2 else db)
    chess((0.0, -0.3, 0.9)); chess((0.1, -0.35, 0.9), white=True, knocked=True); chess((-0.1, -0.2, 0.9)); chess((0.05, -0.15, 0.9), white=True)
    sets.candle("cc", (-0.35, -0.3, 0.89), h=0.18)
    kit.area("key", (-0.6, -0.9, 1.4), (0, -0.3, 0.9), 25, size=0.5, color=(1, 0.7, 0.45))
    kit.world((0.02, 0.02, 0.03), 1.0, fog=0.015, fog_color=(0.9, 0.8, 0.7))
    kit.camera((0.25, -0.95, 1.12), (0.0, -0.25, 0.95), lens=45, fstop=1.6, focus=(0.02, -0.3, 0.95)); return []

def crowd(xy, rots, step=0.0024):
    out = []
    for k, ((x, y), rz) in enumerate(zip(xy, rots)): out.append(cast.townsman(k, at=(x, y, 0), rot_z=rz, step=step))
    return out

def dawn():
    kit.sky([(-1, (0.6, 0.62, 0.7)), (0.0, (0.95, 0.8, 0.75)), (0.15, (0.62, 0.68, 0.85)), (1, (0.25, 0.32, 0.55))], 1.6)
    kit.sun("sun", (78, 0, -150), 2.0, (1, 0.75, 0.55), angle=4); kit.sun("sky", (20, 0, 30), 0.8, (0.6, 0.7, 1.0), angle=40)

def block_props(at=(0, 0, 0), knife=True):
    x, y, z = at; wood = kit.mat("block", (0.42, 0.28, 0.16), rough=0.8, noise=0.5, nscale=12)
    kit.cylinder("blockC", 0.3, 0.45, (x, y, 0.22), wood, seg=32, bevel=0.02)
    blood = kit.mat("blood", (0.35, 0.02, 0.02), rough=0.15, coat=0.8)
    for k, (dx, dy, r) in enumerate(((0.45, -0.2, 0.25), (0.75, 0.1, 0.15), (-0.3, -0.4, 0.12), (0.2, 0.35, 0.18))):
        kit.cylinder(f"bl{k}", r, 0.006, (x + dx, y + dy, 0.004), blood, seg=24)
    if knife:
        steel = kit.mat("steel", (0.7, 0.7, 0.72), rough=0.2, metal=1)
        kit.box("blade", (0.04, 0.42, 0.006), (x + 0.5, y - 0.28, 0.012), steel, rot=(0, 0, 30)); kit.box("hilt", (0.035, 0.16, 0.03), (x + 0.38, y - 0.07, 0.02), kit.mat("hilt", (0.2, 0.12, 0.06)), rot=(0, 0, 30))
        kit.box("bladeblood", (0.042, 0.2, 0.007), (x + 0.56, y - 0.38, 0.0125), blood, rot=(0, 0, 30))
    cloth = kit.mat("cloak", (0.3, 0.06, 0.05), rough=0.8, sheen=0.8)                # край плаща — без тела
    kit.sphere("cloak", 1.0, (x - 0.7, y + 0.5, 0.0), cloth, scale=(0.6, 0.4, 0.12), rot=(0, 0, 30))

def s_square():
    M = town.mats(True); town.square(M, snow=True, lit=0.08); dawn()
    block_props((0, 2, 0))
    crowd([(-1.6, -1.2), (0.6, -1.6), (2.1, -0.4), (-2.8, 0.8), (3.0, 2.0), (-2.2, 3.6), (1.8, 4.6)], [165, 185, 215, 130, 240, 60, 330], step=0.003)
    kit.camera((0.8, -9.5, 5.5), (0, 2.5, 1.2), lens=30, fstop=0); return []

def s_block():
    M = town.mats(True); town.square(M, snow=True, lit=0.08); dawn(); block_props((0, 2, 0))
    crowd([(-1.0, 4.5), (0.8, 4.8), (2.2, 4.0)], [0, 10, -20], step=0.003)
    kit.camera((0.9, 0.6, 0.45), (0.1, 2.2, 0.25), lens=28, fstop=2.0, focus=(0.4, 1.8, 0.1)); return []

def s_crowd():
    M = town.mats(True); town.square(M, snow=True, lit=0.08); dawn()
    cs = crowd([(-0.42, 0.0), (0.38, 0.25), (0.0, 0.9)], [-160, 165, 180], step=0.0018)
    for c, (y, p) in zip(cs, ((15, 18), (-12, 20), (0, 15))): look(c, y, p)
    kit.camera((0.0, 1.85, 1.68), (0, 0.3, 1.62), lens=40, fstop=2.2, focus=(0, 0.1, 1.66)); return cs

def s_niccolo():
    sets.hall(window=False, banner=False); n = cast.niccolo(at=(0, 0.2, 0)); look(n, 12, 20)
    wood = kit.mat("desk", (0.32, 0.18, 0.09), rough=0.5, noise=0.5, nscale=25)
    kit.box("desk", (1.2, 0.6, 0.06), (0, -0.25, 0.86), wood, bevel=0.01)
    paper = kit.mat("paper", (0.9, 0.84, 0.7), rough=0.8, noise=0.2, nscale=15)
    kit.box("sheet", (0.32, 0.4, 0.003), (0.05, -0.3, 0.892), paper, rot=(0, 0, -8)); kit.box("sheet2", (0.32, 0.4, 0.003), (-0.3, -0.25, 0.891), paper, rot=(0, 0, 12))
    ink = kit.mat("ink", (0.02, 0.02, 0.03), rough=0.1, coat=1); kit.cylinder("inkwell", 0.035, 0.06, (0.32, -0.2, 0.92), ink, seg=24)
    feather = kit.mat("feather", (0.92, 0.9, 0.85), rough=0.7, sheen=1); kit.sphere("quill", 1.0, (0.18, -0.32, 0.96), feather, scale=(0.012, 0.1, 0.004), rot=(50, 0, -35))
    sets.candle("nc", (-0.32, -0.15, 0.89), h=0.2)
    kit.area("key", (-0.7, -0.6, 1.3), (0, 0.1, 1.5), 22, size=0.4, color=(1, 0.68, 0.4))
    kit.area("rim", (0.9, 1.2, 2.0), (0, 0.2, 1.6), 120, size=0.5, color=(0.6, 0.72, 1.0))
    kit.world((0.02, 0.02, 0.03), 1.0, fog=0.015, fog_color=(0.9, 0.8, 0.7))
    kit.camera((-0.35, -1.05, 1.5), (0.0, 0.1, 1.42), lens=38, fstop=2.2, focus=(0, 0.1, 1.64)); return [n]

SHOTS = dict(hook=s_hook, romagna=s_romagna, remirro=s_remirro, fear=s_fear, move=s_move, square=s_square, block=s_block, crowd=s_crowd, niccolo=s_niccolo, cta=s_cta)

def blink_box(chars_):
    """Прямоугольник вокруг глаз всех героев в кадре (доли кадра) — для дорендера с закрытыми глазами."""
    sc = bpy.context.scene; cam = sc.camera; xs, ys = [], []
    bpy.context.view_layer.update()
    for c in chars_:
        for ob in c["head"].children:
            if "_eye" in ob.name and not ob.name.endswith("_eye"):
                p = world_to_camera_view(sc, cam, ob.matrix_world.translation)
                if 0 < p.x < 1 and 0 < p.y < 1 and p.z > 0: xs.append(p.x); ys.append(p.y)
    if not xs: return None
    m = 0.05
    return (max(0, min(xs) - m), max(0, min(ys) - m * 0.6), min(1, max(xs) + m), min(1, max(ys) + m * 0.6))

if __name__ == "__main__":
    name = sys.argv[1]; samples = int(sys.argv[2]) if len(sys.argv) > 2 else 64; pct = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    kit.reset(); random.seed(1); cs = SHOTS[name]()
    kit.setup_render(samples=samples, res=RES, pct=pct)
    kit.render(f"{OUT}/{name}.png")
    box = blink_box(cs)
    if box and pct == 100:
        for c in cs:
            for ob in c["head"].children:
                if "_lidU" in ob.name: ob.rotation_euler[0] = math.radians(86)
                if "_lidL" in ob.name: ob.rotation_euler[0] = math.radians(180 + 10)
        r = bpy.context.scene.render; r.use_border = True; r.use_crop_to_border = True
        r.border_min_x, r.border_min_y, r.border_max_x, r.border_max_y = box
        kit.render(f"{OUT}/{name}_blink.png")
        json.dump(dict(box=box, res=RES), open(f"{OUT}/{name}_blink.json", "w"))
