"""Обложка ship_float_1 (№68): фото NASA (авианосец-музей «Интрепид», общественное достояние) + плашка-хук."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from PIL import Image
import plane_kit as K, bh_cine as B
from make_covers_click import make_click
from make_covers_day2 import crop
im = B.finish_c(K.photo("nasa_intrepid", 2.0, 4.0, z0=1.1, z1=1.1, fx=0.5, fy=0.55, cy=760).convert("RGBA"), k=0.45, streak=0.3).convert("RGB")
im.resize((1620, 2880), Image.LANCZOS).save(f"{HERE}/art/ship_cover.jpg", quality=93)
make_click(crop("ship_cover", 0.5, 0.5, 2880), "БОЛЕЕ 27 000 ТОНН.\nПОЧЕМУ НЕ ТОНЕТ?", "ФИЗИКА", "ПРОСТЫМ ЯЗЫКОМ", "как держится корабль", "68_ship_float_click", y=1180, stamp_pos="bottom")
print("ok")
