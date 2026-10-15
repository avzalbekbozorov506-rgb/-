"""Кликбейт-обложка для «Ты важнее, чем думаешь» (японская гравюра Хиросигэ, The Met CC0)."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers import cover_crop
from make_covers_click import make_click
bg = cover_crop(Image.open(f"{HERE}/art/hiroshige_snow_woman.jpg"), 0.45, 0.62, 1.35)
make_click(bg, "ТЫ ВАЖНЕЕ,\nЧЕМ ДУМАЕШЬ", "ПРАВДА", "ТЕБЯ ПОМНЯТ", "даже если ты этого не замечаешь", "11_vazhen_click")
print("ok")
