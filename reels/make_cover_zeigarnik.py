"""Обложка пробного Reels «Недоделанное не отпускает»: Вермеер 437881 (The Met, CC0) с тёмным полем сверху."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop, pad_top
pad_top("met_437881", "met_437881_pad", 500)
make_click(crop("met_437881_pad", 0.5, 0.5, 2300), "НЕДОДЕЛАННОЕ\nНЕ ОТПУСКАЕТ", "МИФ И ПРАВДА", "ЭФФЕКТ ЗЕЙГАРНИК", "что на самом деле помогает", "trial_zeigarnik_click", y=1180, stamp_pos="bottom")
print("ok")
