"""Обложка ролика feelings_flatter_1 (№64)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("page_flatter_0", 0.5, 0.5, 2880), "ТЕБЕ СКАЗАЛИ:\nОНИ ТЕБЯ\nНЕ ДОСТОЙНЫ", "КРЫЛОВ", "«КУКУШКА И ПЕТУХ»", "басня", "64_feelings_flatter_click", y=1180, stamp_pos="bottom")
print("ok")
