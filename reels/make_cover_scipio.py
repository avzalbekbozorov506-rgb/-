"""Обложка вне плана: Сципион — «Он спас Рим. Рим его выгнал». Бюст римлянина XVII в. (The Met, CC0)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop
make_click(crop("met_204856", 0.5, 0.30, 2500), "ОН СПАС РИМ.\nРИМ ЕГО ВЫГНАЛ", "НЕБЛАГОДАРНОСТЬ", "СЦИПИОН", "фраза на его могиле", "48_scipio_ingrate_click", y=1180, stamp_pos="bottom")
print("ok")
