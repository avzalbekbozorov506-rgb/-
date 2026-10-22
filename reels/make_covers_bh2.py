"""Обложка blackhole_2 «Место без возврата» (№66): чёрный круг, красный пунктир, падающая точка."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from PIL import Image, ImageDraw
from blackhole_1 import canvas, finish, circ, ring
from make_covers_click import make_click
from make_covers_day2 import crop
im = canvas(); d = ImageDraw.Draw(im); c = (540, 640)
circ(d, c, 250, fill=(0, 0, 0))
for i in range(0, 56, 2): d.arc((c[0] - 285, c[1] - 285, c[0] + 285, c[1] + 285), i * 360 / 56, (i + 0.9) * 360 / 56, fill=(235, 60, 50), width=10)
ring(d, c, 256, col=(255, 90, 50), w=10, a=0.6)
for k in range(1, 7): circ(d, (540 + 14 * k, 160 + 45 * k), 4 + k, fill=(255, 255, 255, 40 + 30 * k))
circ(d, (640, 480 - 160 + 130), 16, fill=(255, 255, 255))
finish(im, 1.1).convert("RGB").resize((1620, 2880), Image.LANCZOS).save(f"{HERE}/art/bh2_cover.jpg", quality=93)
make_click(crop("bh2_cover", 0.5, 0.5, 2880), "МЕСТО\nБЕЗ ВОЗВРАТА", "КОСМОС", "ЧТО СКРЫВАЕТ", "чёрная дыра", "66_blackhole2_click", y=1180, stamp_pos="bottom")
print("ok")
