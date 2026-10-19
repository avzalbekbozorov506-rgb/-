"""Обложки сериала «Портретист» (вымышленная история). Картины — The Met (CC0)."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
def fit(name, cy=0.4):
    im = Image.open(os.path.join(HERE, f"art/{name}.jpg")).convert("RGB"); w, h = im.size
    cw = int(h * 9 / 16)
    if cw <= w: im = im.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, h))
    else:
        ch = int(w * 16 / 9); bg = Image.new("RGB", (w, ch), (14, 11, 9)); bg.paste(im, (0, int((ch - h) * cy))); im = bg
    im = im.resize((1080, 1920), Image.LANCZOS)
    out = Image.new("RGB", (1080, 1920), (14, 11, 9)); out.paste(im.crop((0, 0, 1080, 1760)), (0, 160)); return out
make_click(fit("met_436709", 0.3), "3 ПОРТРЕТА —\n3 ПОКОЙНИКА", "СЕРИЯ 1", "ПОРТРЕТИСТ", "вымышленная история · Париж, 1869", "43_portraitist_1_click", y=1130)
print("ok")
