"""Обложки серии «Макиавелли · часть 3–22»: портрет из хука, красная плашка с хуком, штамп, «МАКИАВЕЛЛИ · ЧАСТЬ N», подзаголовок.
FOCUS — где лицо (fx, fy, zoom) для cover_crop; лицо должно оказаться над плашкой."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers import cover_crop
from make_covers_click import make_click
from series_mach import SERIES
from series_art import ART
FOCUS = {9: (0.5, 0.72, 1.05), 12: (0.5, 0.8, 1.05), 13: (0.4, 0.75, 1.15), 15: (0.45, 0.8, 1.05), 18: (0.5, 0.62, 1.0), 21: (0.5, 0.62, 1.0), 22: (0.45, 0.62, 1.0)}
only = set(map(int, sys.argv[1:]))
for s in SERIES:
    n = s["n"]
    if only and n not in only: continue
    f = ART[n]["hook"][0]; name = f"met_{f}" if isinstance(f, int) else f
    fx, fy, z = FOCUS.get(n, (0.45, 0.42, 1.12))
    make_click(cover_crop(Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"), fx, fy, z), s["hook"], s["stamp"], f"МАКИАВЕЛЛИ · {n}", s["sub"], f"mach_{n:02d}_click")
print("ok")
