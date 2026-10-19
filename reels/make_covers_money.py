"""Обложка money_map (новая тема «Спросили ИИ»)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop  # импорт заодно пересобирает обложки дня 2 (детерминированно)
make_click(crop("pp_02", 0.5, 0.36, 1500), "ГДЕ ТВОИ\n50 000 ₽?", "КАРТА ДЕНЕГ", "МЫ СПРОСИЛИ КЛОДА", "куда утекает зарплата", "42_money_map_click", y=1080)
print("ok")
