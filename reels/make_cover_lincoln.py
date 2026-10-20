"""Обложка вне плана: письмо Линкольна, которое он не отправил. Фото — Энтони Бергер, 1864 (The Met, CC0)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("met_285876", 0.5, 0.33, 1200), "ОН НЕ ОТПРАВИЛ\nЭТО ПИСЬМО", "ЛИНКОЛЬН, 1863", "ЗЛОЕ ПИСЬМО", "и пометка на конверте", "47_lincoln_letter_click", y=1180, stamp_pos="bottom")
print("ok")
