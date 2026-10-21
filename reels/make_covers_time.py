"""Обложки серии «Время ограничено»: Сенека — обида, Сенека — «приеду потом», Марк Аврелий — «спасибо»."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("page_grudge_2", 0.5, 0.5, 2880), "ТРИ ГОДА.\nИЗ-ЗА ОДНОЙ ФРАЗЫ", "ПРИМЕР", "СЕНЕКА", "«О гневе», III", "60_time_grudge_click", y=1180, stamp_pos="bottom")
make_click(crop("page_visits_1", 0.5, 0.5, 2880), "ТРИ РАЗА В ГОД —\nЭТО МАЛО", "СЕНЕКА", "ПИСЬМО LXIII", "«Нравственные письма»", "61_time_visits_click", y=1180, stamp_pos="bottom")
make_click(crop("page_thanks_0", 0.5, 0.5, 2880), "ПЕРВАЯ СТРАНИЦА —\nСПЛОШНОЕ «СПАСИБО»", "МАРК АВРЕЛИЙ", "«РАЗМЫШЛЕНИЯ»", "книга I", "62_time_thanks_click", y=1180, stamp_pos="bottom")
print("ok")
