"""Обложка glare_1 (№71): кадр хука (встречные фары на ночной трассе, графика кодом) + плашка-хук."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
from PIL import Image
from make_covers_click import make_click
from make_covers_day2 import crop
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2.5", "-i", f"{HERE}/glare_1.mp4", "-frames:v", "1", f"{HERE}/art/glare_cover_raw.png"], check=True)
import numpy as np
_r = np.asarray(Image.open(f"{HERE}/art/glare_cover_raw.png").convert("RGB"), dtype=np.float32)   # шапка движка закрыта затемнением сверху
_g = np.clip((np.arange(_r.shape[0]) - 255) / 90.0, 0, 1)[:, None, None]
Image.fromarray((_r * (0.0 + 1.0 * _g)).astype(np.uint8)).resize((1620, 2880), Image.LANCZOS).save(f"{HERE}/art/glare_cover.jpg", quality=93)
make_click(crop("glare_cover", 0.5, 0.5, 2880), "ВСТРЕЧНЫЕ ФАРЫ\nСЛЕПЯТ. ПОЧЕМУ?", "РАСЧЁТ", "ПРОСТЫМ ЯЗЫКОМ", "ослепление фарами", "71_glare_click", y=1130, stamp_pos="bottom")
print("ok")
