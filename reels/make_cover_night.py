"""Обложка «Правки заказчика»: кадр ночной сцены + плашка (стиль обложек формата «Клод»)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/cubes")
from PIL import Image
import cuberender as R
import scenes_night as N
from make_covers_click import make_click
st = dict(talk={}, blink={}, bob={}, arm={}, book=0)
sc = N.SCENES[0]
shot = R.Shot(sc["static"](), sc["camera"](), lights=sc["lights"](), region=sc["region"], dof=sc["dof"])
bg = Image.fromarray(shot.render(sc["dyn"](st)))
make_click(bg, "СДЕЛАЙ БОЛЬШЕ,\nНО НЕЗАМЕТНЕЕ", "ЖИЗА", "КЛОД", "Правки заказчика", "claude_night_click", y=400, dark_top=True, stamp_pos="top")
print("ok")
