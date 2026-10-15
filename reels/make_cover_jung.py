"""Обложка вне плана: «Ваш мозг — это сериал» (Юнг, Эго и Самость, эксперимент-аналог). Триптих как в ролике."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/configs")
sys.argv = [sys.argv[0], "configs/jung_ego.py"]
import jung_ego as J
from PIL import Image
from make_covers_click import make_click
bg = J._tri("aic_redon_waters")(Image.open(f"{HERE}/art/aic_redon_waters.jpg")).resize((1080, 1920), Image.LANCZOS)
make_click(bg, "ВАШ МОЗГ —\nЭТО СЕРИАЛ", "ЭГО ПРОТИВ САМОСТИ", "КАРЛ ЮНГ", "кто главный в вашей голове", "46_jung_ego_click", y=1230, stamp_pos="bottom")
print("ok")
