"""Обложка ego_betrayal_1: сетка старых фото с вопросами."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("card_ego_q", 0.5, 0.3, 2880), "СТАРЫЕ ФОТО.\nТЫ ИЩЕШЬ ЛОЖЬ", "ПРИМЕР", "ШЕКСПИР", "«Юлий Цезарь», III, 2", "63_ego_betrayal_click", y=1180, stamp_pos="bottom")
print("ok")
