"""Обложка «Чезаре и Рамиро»: портрет «Бородатый мужчина в чёрном» (Корнель де Лион, The Met) + плашка, штамп, название."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
im = Image.open(f"{HERE}/art/met_435948.jpg").convert("RGB")
sc = 2150 / im.height; big = im.resize((int(im.width * sc), 2150), Image.LANCZOS)          # крупнее, лицо по центру
x0 = int((big.width - 1080) * 0.62); bg = big.crop((x0, 60, x0 + 1080, 60 + 1920))
make_click(bg, "ОН КАЗНИЛ\nСВОЕГО ПАЛАЧА", "ГЛАВА VII", "ЧЕЗАРЕ БОРДЖИА", "история из «Государя»", "16_borgia_click", y=1060)
print("ok")
