"""Обложка «Налог на туалет в Риме»: кадр сцены Веспасиан + плашка (стиль обложек формата «Клод»)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/cubes")
from PIL import Image
import cuberender as R
import scenes_toilet as T
from make_covers_click import make_click
st = dict(talk={}, blink={}, bob={}, arm={}, book=0)
sc = T.SCENES[2]
shot = R.Shot(sc["static"](), sc["camera"](), lights=sc["lights"](), region=sc["region"], dof=sc["dof"])
bg = Image.fromarray(shot.render(sc["dyn"](st)))
make_click(bg, "В РИМЕ БРАЛИ\nНАЛОГ НА ТУАЛЕТ", "ПРАВДА", "КЛОД", "Откуда «деньги не пахнут»", "claude_toilet_click", y=400, dark_top=True, stamp_pos="bottom")
print("ok")
