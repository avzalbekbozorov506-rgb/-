"""Обложка ролика blackhole_1 (№65)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("bh_cover", 0.5, 0.5, 2880), "ЧЁРНАЯ ДЫРА —\nЭТО НЕ ДЫРА", "КОСМОС", "ОБЪЯСНЯЕМ", "за минуту", "65_blackhole_click", y=1180, stamp_pos="bottom")
print("ok")
