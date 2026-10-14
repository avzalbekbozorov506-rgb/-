"""Обложки роликов 17.10 (план 3.0, день 1): льстец (Макиавелли), миф о росте Наполеона, Борджиа — часть 2."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
import importlib.util as _u
_spec = _u.spec_from_file_location("d2", os.path.join(HERE, "make_covers_day2.py"))
exec(open(os.path.join(HERE, "make_covers_day2.py")).read().split("pad_top(\"wm_machiavelli_tito\"")[0])   # только функции crop и pad_top
pad_top("bronzino", "_bronzino_pad", 300)
make_click(crop("_bronzino_pad", 0.5, 0.0, 2500), "ТЕБЕ ЛЬСТЯТ?\nПРОВЕРЬ", "3 ПРИЗНАКА", "МАКИАВЕЛЛИ", "как распознать льстеца", "32_mach_flatter_click", y=1060)
pad_top("wm_david_napoleon_study", "_napoleon_pad", 420)
make_click(crop("_napoleon_pad", 0.5, 0.0, 2300), "НАПОЛЕОН БЫЛ\nКОРОТЫШКОЙ?", "ПРОВЕРИМ", "НАПОЛЕОН", "миф или правда", "33_myth_napoleon_click", y=1060)
pad_top("met_435948", "_borgia_pad", 520)
make_click(crop("_borgia_pad", 0.5, 0.0, 2500), "ОН ОБНЯЛ ВРАГОВ.\nНОЧЬЮ ИХ ЗАДУШИЛИ", "ЧАСТЬ 2", "БОРДЖИА", "западня в Сенигаллии", "34_borgia2_click", y=1060)
print("ok")
