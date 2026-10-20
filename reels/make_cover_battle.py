"""Обложка «Кто знает историю лучше: ChatGPT, Gemini или Claude?» — кадр из рендера кубов + плашка (стиль обложек формата «Клод»)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/cubes")
import numpy as np
from PIL import Image
import cuberender as R
import scenes_battle as B
from make_covers_click import make_click

st = dict(talk={}, blink={}, bob={}, arm={}, book=0)
shot = R.Shot(B.class_static(B.board_who())(), B.CAM(), lights=B.class_lights(), region=(-3, 3.5, -.2, 4, -.3, 3.5), dof=(3.4, 2.0))
bg = Image.fromarray(shot.render(B.dyn(st)))
from PIL import ImageDraw
def pills(im):
    d = ImageDraw.Draw(im)
    for (x, name, col) in B._POS.values():
        ft = B._f(34); tw = d.textlength(name, font=ft)
        d.rounded_rectangle((x - tw / 2 - 26, 1275, x + tw / 2 + 26, 1341), 33, fill=col + (255,)); d.text((x - tw / 2, 1288), name, font=ft, fill=(255, 255, 255))
    return im
im = make_click(bg, "КТО ЗНАЕТ\nИСТОРИЮ ЛУЧШЕ?", "БАТТЛ ИИ", "КЛОД", "ChatGPT, Gemini или Claude? Ответ в конце", "claude_battle_click", y=420, dark_top=True, stamp_pos="bottom")
pills(im).convert("RGB").save(f"{HERE}/covers/claude_battle_click.jpg", quality=94)
print("ok")
