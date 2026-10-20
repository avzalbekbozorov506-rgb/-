"""Обложка вне плана: «Крейцерова соната» (эксперимент, ч/б). Фото Толстого 1897 (Library of Congress)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import ImageOps, ImageEnhance
from make_covers_click import make_click
from make_covers_day2 import crop
bg = crop("loc_tolstoy_1897_crop", 0.5, 0.38, 640)
bg = ImageEnhance.Contrast(ImageOps.grayscale(bg).convert("RGB")).enhance(1.15)
make_click(bg, "ЖЕНА ТОЛСТОГО\nУЗНАЛА СЕБЯ", "СПРЯТАЛИ НА 100 ЛЕТ", "ЛЕВ ТОЛСТОЙ", "«Крейцерова соната»", "45_tolstoy_sonata_click", y=1180, stamp_pos="bottom")
print("ok")
