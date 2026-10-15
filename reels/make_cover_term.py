"""Спокойная обложка «понятие» (по образцу @prosvet.app): картина на весь кадр, затемнение снизу, две строки — ЗАГЛАВНЫМИ и курсивом.
Использование: python3 make_cover_term.py <картина> <cx> <cy> <высота_кадра> "СТРОКА 1" "строка 2" <имя_файла>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers import spaced, serif, sans, W, H, GOLD, WHITE
def crop(name, cx, cy, h):
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); w = int(h * 9 / 16)
    s = max(w / im.width, h / im.height, 1.0); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = min(max(int(cx * im.width - w / 2), 0), im.width - w); y0 = min(max(int(cy * im.height - h / 2), 0), im.height - h)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.LANCZOS)
def make_term(bg, line1, line2, out):
    im = bg.convert("RGBA"); yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    a = np.clip((yy - 900) / 700, 0, 1) ** 1.2 * 225 + np.clip((260 - yy) / 260, 0, 1) * 110
    im.alpha_composite(Image.fromarray(np.dstack([np.full((H, W), 8), np.full((H, W), 6), np.full((H, W), 6), a]).astype(np.uint8), "RGBA"))
    d = ImageDraw.Draw(im)
    spaced(d, (W // 2, 300), "МЫСЛИ ВЕКОВ", sans("SemiBold", 28), GOLD, 9); d.line(((W // 2 - 70, 338), (W // 2 + 70, 338)), fill=GOLD, width=2)
    size = 132
    while size > 70 and d.textlength(line1, font=sans("Black", size)) > 940: size -= 4
    d.text((W // 2, 1290), line1, font=sans("Black", size), fill=WHITE, anchor="mm")
    d.text((W // 2, 1290 + size * 0.95), line2, font=serif("MediumItalic", int(size * 0.72)), fill=(236, 226, 206), anchor="mm")
    im.convert("RGB").save(f"{HERE}/covers/{out}.jpg", quality=94)
if __name__ == "__main__":
    n, cx, cy, h, l1, l2, out = sys.argv[1:8]
    make_term(crop(n, float(cx), float(cy), int(h)), l1, l2, out); print("ok")
