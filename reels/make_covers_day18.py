"""Обложки роликов 18.10 (план 3.0, день 2): Марк Аврелий о гневе, Макиавелли об имуществе, Сеян."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from make_covers_click import make_click
from make_covers_day2 import crop  # импорт заодно пересобирает обложки дня 2 (детерминированно)
from PIL import Image
import marcus_people
marcus_people.dark_studio(Image.open(f"{HERE}/art/ma_bronze.jpg").convert("RGB")).save(f"{HERE}/art/_ma_dark.jpg", quality=92)
make_click(crop("_ma_dark", 0.5, 0.42, 1500), "ТЕБЯ БЕСЯТ\nЛЮДИ?", "3 МЫСЛИ", "МАРК АВРЕЛИЙ", "против гнева", "36_marcus_anger_click", y=1060)
make_click(crop("_mach_pad", 0.5, 0.0, 2300), "ЧЕГО ЛЮДИ\nНЕ ПРОЩАЮТ?", "ГЛАВА XVII", "МАКИАВЕЛЛИ", "одна фраза", "37_mach_inherit_click", y=1060)
make_click(crop("wm_maccari_alone", 0.62, 1.0, 1000), "УТРОМ ПРАВИЛ РИМОМ.\nВЕЧЕРОМ КАЗНЁН", "18 ОКТЯБРЯ", "СЕЯН", "падение фаворита · 1", "38_sejanus_click", y=560, stamp_pos="bottom")
print("ok")
