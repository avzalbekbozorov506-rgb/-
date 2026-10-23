"""Обложка toilet_air_1 (№70): кадр ролика (санузел, линии вони, лицо с зажатым носом, баллончик) + плашка-хук."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from PIL import Image
from make_covers_click import make_click
from make_covers_day2 import crop
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.2", "-i", f"{HERE}/toilet_air_1.mp4", "-frames:v", "1", f"{HERE}/art/toilet_cover_raw.png"], check=True)
Image.open(f"{HERE}/art/toilet_cover_raw.png").convert("RGB").resize((1620, 2880), Image.LANCZOS).save(f"{HERE}/art/toilet_cover.jpg", quality=93)
make_click(crop("toilet_cover", 0.5, 0.5, 2880), "ПОСЛЕ ТУАЛЕТА\nНАЖИМАЕШЬ\nОСВЕЖИТЕЛЬ?", "ПРАВДА", "ПРОСТЫМ ЯЗЫКОМ", "что делает освежитель", "70_toilet_air_click", y=1130, stamp_pos="bottom")
print("ok")
