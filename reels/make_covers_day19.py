"""Обложки роликов 19.10 (план 3.0, день 3): Грасиан об уважении, миф о Цезаре-императоре, последние 24 часа Цезаря."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop, pad_top  # импорт заодно пересобирает обложки дня 2 (детерминированно)
pad_top("wm_gracian", "_gracian_pad", 170)
make_click(crop("_gracian_pad", 0.45, 0.0, 1100), "ТЕБЯ НЕ\nУВАЖАЮТ?", "3 ОШИБКИ", "ГРАСИАН", "«Карманный оракул», 1647", "39_gracian_respect_click", y=1180, dark_top=True, stamp_pos="bottom")
make_click(crop("met_337195", 0.48, 0.33, 1500), "ЦЕЗАРЬ БЫЛ\nИМПЕРАТОРОМ?", "МИФ ИЛИ ПРАВДА", "ЮЛИЙ ЦЕЗАРЬ", "ответ — в ролике", "40_myth_caesar_click", y=1180, stamp_pos="bottom")
make_click(crop("wm_gerome_death_caesar_v", 0.4, 0.6, 1057), "ЕГО ПРЕДУПРЕДИЛИ\nТРИ РАЗА", "ПОСЛЕДНИЕ 24 ЧАСА", "ЮЛИЙ ЦЕЗАРЬ", "последние 24 часа · 1", "41_caesar_24h_click", y=560, stamp_pos="bottom")
print("ok")
