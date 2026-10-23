"""Обложка wifi_1 (№69): кадр ролика (изометрическая комната с волнами, графика кодом) + плашка-хук."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from PIL import Image
from make_covers_click import make_click
from make_covers_day2 import crop
Image.open(f"{HERE}/art/wifi_cover_raw.png").convert("RGB").resize((1620, 2880), Image.LANCZOS).save(f"{HERE}/art/wifi_cover.jpg", quality=93)
make_click(crop("wifi_cover", 0.5, 0.5, 2880), "ВЫДЕРНУТЬ РОУТЕР\nНА НОЧЬ?", "РАСЧЁТ", "ПРОСТЫМ ЯЗЫКОМ", "вреден ли Wi-Fi", "69_wifi_click", y=1180, stamp_pos="bottom")
print("ok")
