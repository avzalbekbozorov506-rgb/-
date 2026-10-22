"""Обложка plane_lift_1 (№67): фото NASA (747 взлетает на закате, общественное достояние) + плашка-хук."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from PIL import Image
import plane_kit as K, bh_cine as B
from make_covers_click import make_click
from make_covers_day2 import crop
im = B.finish_c(K.photo("nasa_sofia_sunset", 2.0, 4.0, z0=1.05, z1=1.05, fx=0.62, cy=760).convert("RGBA"), k=0.45, streak=0.3).convert("RGB")
im.resize((1620, 2880), Image.LANCZOS).save(f"{HERE}/art/plane_cover.jpg", quality=93)
make_click(crop("plane_cover", 0.5, 0.5, 2880), "СОТНИ ТОНН.\nПОЧЕМУ НЕ ПАДАЮТ?", "ФИЗИКА", "ПРОСТЫМ ЯЗЫКОМ", "как держится самолёт", "67_plane_lift_click", y=1180, stamp_pos="bottom")
print("ok")
