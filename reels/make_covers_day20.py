"""Обложки роликов 20.10 (план 3.0, день 4): Макиавелли о предательстве, Эпиктет, Борджиа · часть 3."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
from make_covers_day2 import crop, pad_top
make_click(crop("giuliano", 0.5, 0.42, 1500), "ТЕБЯ\nПРЕДАЛИ?", "3 ПРИЧИНЫ", "МАКИАВЕЛЛИ", "«Государь», гл. XV и XVII", "42_mach_betrayed_click", y=1180, stamp_pos="bottom")
make_click(crop("aic_philosopher", 0.5, 0.36, 2250), "ТЕБЯ МУЧАЕТ\nНЕ ЭТО", "ОДНА ФРАЗА", "ЭПИКТЕТ", "«Энхиридион», 5", "43_epictetus_mind_click", y=1180, stamp_pos="bottom")
make_click(crop("met_435948", 0.5, 0.35, 1900), "ОН ПРЕДУСМОТРЕЛ\nВСЁ. КРОМЕ ОДНОГО", "ЧАСТЬ 3", "БОРДЖИА", "финал серии", "44_borgia3_click", y=1180, stamp_pos="bottom")
print("ok")
