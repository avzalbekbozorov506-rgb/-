"""Декорации: зал Чезаре (камень, арки, свечи, знамя), площадь Чезены (снег, дома, туман), кабинет Макиавелли."""
import math, random
import kit, sdf as S
import numpy as np

def candle(name, co, h=0.22, r=0.022, flame=1.0, light=True):
    wax = kit.mat(name + "_wax", (0.93, 0.86, 0.7), rough=0.5, sss=0.6)
    kit.cylinder(name, r, h, (co[0], co[1], co[2] + h / 2), wax, seg=24)
    fl = kit.mat(name + "_fl", (1, 0.7, 0.3), emit=(1, 0.62, 0.25), emit_k=40 * flame)
    kit.sphere(name + "_flame", 0.008, (co[0], co[1], co[2] + h + 0.014), fl, scale=(1, 1, 2.2), seg=16)
    if light: kit.point(name + "_L", (co[0], co[1], co[2] + h + 0.03), 3.5 * flame, (1, 0.62, 0.3), radius=0.02)

def hall(seed=1, window=True, banner=True, WX=1.0):
    random.seed(seed)
    stone = kit.mat("stone", (0.42, 0.36, 0.3), rough=0.85, noise=0.45, nscale=4)
    floor = kit.mat("floor", (0.3, 0.22, 0.17), rough=0.55, noise=0.4, nscale=3)
    wood = kit.mat("wood", (0.32, 0.18, 0.09), rough=0.5, noise=0.5, nscale=25)
    red = kit.mat("red", (0.55, 0.06, 0.05), rough=0.6, sheen=0.9, noise=0.15, nscale=60)
    gold = kit.mat("hgold", (0.95, 0.68, 0.3), rough=0.3, metal=1)
    kit.box("floor", (14, 14, 0.1), (0, 2, -0.05), floor)
    # задняя стена с арочным окном
    def wall(P):
        d = S.rbox(P, (0, 3.2, 2.5), (5, 0.25, 2.6), 0.0)
        if window:
            d = S.sub(d, S.smin(S.rbox(P, (WX, 3.2, 1.9), (0.32, 0.6, 0.55)), S.cap(P, (WX, 3.2, 2.45), (WX, 3.2, 2.45), 0.32), 0.0), 0.01)
        return d
    S.mesh("wall", wall, (-5.1, 2.9, -0.1), (5.1, 3.5, 5.2), 0.03, stone, smooth_iter=0)
    for x in (-1.9, 2.0):                                                    # колонны
        kit.cylinder(f"col{x}", 0.22, 4.4, (x, 2.7, 2.2), stone, seg=32)
        kit.cylinder(f"colb{x}", 0.3, 0.25, (x, 2.7, 0.12), stone, seg=32, bevel=0.03)
    if window:
        sky = kit.mat("moon", (0.5, 0.65, 1.0), emit=(0.45, 0.6, 1.0), emit_k=1.2)
        kit.box("sky", (0.9, 0.05, 1.8), (WX, 3.5, 2.1), sky)
        kit.area("moonL", (WX, 3.6, 2.4), (0.0, 0.0, 1.2), 160, size=0.7, color=(0.6, 0.72, 1.0))
    if banner:                                                               # алое знамя с золотой каймой
        for x in (-0.75,):
            kit.box(f"ban{x}", (0.55, 0.03, 1.7), (x, 2.9, 2.9), red, bevel=0.01)
            kit.box(f"banr{x}", (0.62, 0.06, 0.05), (x, 2.88, 3.77), gold, bevel=0.01)
    for x in (-1.3, 2.6):                                                    # факелы на стене: свет на камне
        kit.cylinder(f"sconce{x}", 0.04, 0.3, (x, 2.92, 2.0), gold, seg=16)
        fl = kit.mat(f"tf{x}", (1, 0.6, 0.2), emit=(1, 0.55, 0.2), emit_k=30); kit.sphere(f"torchf{x}", 0.05, (x, 2.9, 2.2), fl, scale=(1, 1, 1.8), seg=16)
        kit.point(f"torchL{x}", (x, 2.75, 2.25), 120, (1, 0.58, 0.28), radius=0.08)
    # стол с картой и свечами на переднем плане
    kit.box("table", (1.6, 0.8, 0.07), (0.25, -0.75, 0.86), wood, bevel=0.015)
    paper = kit.mat("map", (0.82, 0.72, 0.52), rough=0.8, noise=0.3, nscale=12)
    kit.box("mapp", (0.6, 0.45, 0.004), (0.15, -0.8, 0.9), paper, rot=(0, 0, 8))
    for k, (x, y, h) in enumerate(((-0.45, -0.95, 0.24), (-0.35, -0.75, 0.17), (0.7, -0.6, 0.2))):
        kit.cylinder(f"holder{k}", 0.04, 0.02, (x, y, 0.91), gold, seg=24); candle(f"c{k}", (x, y, 0.92), h=h)
    for k in range(9):                                                       # свечи вдали — боке
        x = random.uniform(-3, 3); y = random.uniform(1.6, 2.6); z = random.uniform(1.0, 2.2)
        candle(f"bg{k}", (x, y, z), h=0.12, light=(k % 3 == 0))
