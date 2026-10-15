"""Обложка «Кнопка счастья»: кадр мультфильма (мальчик и кнопка в конфетти) + плашка, штамп, название."""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
sp = importlib.util.spec_from_file_location("k", f"{HERE}/configs/knopka.py"); k = importlib.util.module_from_spec(sp); sp.loader.exec_module(k)
bg = k.s_press(1.3, 6.0).crop((203, 720, 878, 1920)).resize((1080, 1920))   # крупно: мальчик и кнопка над плашкой
make_click(bg, "ОН НАШЁЛ\nКНОПКУ СЧАСТЬЯ", "ЛОВУШКА", "КНОПКА СЧАСТЬЯ", "притча о дофамине", "15_knopka_click", y=1080)
print("ok")
