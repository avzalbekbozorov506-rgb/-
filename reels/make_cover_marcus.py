"""Кликбейт-обложка для «Марк Аврелий — 5 правил»: бюст крупно, красная плашка-хук, штамп «ЛИЧНОЕ».
Всё важное — в центральной зоне 3:4 (y 240–1680), которую показывает сетка профиля."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers import cover_crop, spaced, serif, sans, W, H, GOLD, WHITE

import importlib.util
sp = importlib.util.spec_from_file_location("cfg", f"{HERE}/configs/marcus_rules.py"); cfg = importlib.util.module_from_spec(sp); sp.loader.exec_module(cfg)
im = cover_crop(cfg.PREP["ma_bronze"](Image.open(f"{HERE}/art/ma_bronze.jpg").convert("RGB")), 0.48, 0.30, 1.15)
im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(0.95)).enhance(1.12).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
a = np.clip((yy - 900) / 600, 0, 1) ** 1.1 * 240 + np.clip((300 - yy) / 300, 0, 1) * 120
a = np.maximum(a, np.clip(((xx - W / 2) ** 2 / (W * 0.72) ** 2 + (yy - H * 0.38) ** 2 / (H * 0.55) ** 2) - 0.45, 0, 1) * 220)
im.alpha_composite(Image.fromarray(np.dstack([np.full((H, W), 10), np.full((H, W), 6), np.full((H, W), 6), np.clip(a, 0, 245)]).astype(np.uint8), "RGBA"))
d = ImageDraw.Draw(im)
spaced(d, (W // 2, 300), "МЫСЛИ ВЕКОВ", sans("SemiBold", 28), GOLD, 9); d.line(((W // 2 - 70, 338), (W // 2 + 70, 338)), fill=GOLD, width=2)

# штамп «ЗАПРЕЩЕНО» — повёрнут, с неровными краями
st = Image.new("RGBA", (620, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle((10, 10, 610, 190), 18, outline=(214, 40, 44, 235), width=12); sd.rounded_rectangle((30, 30, 590, 170), 10, outline=(214, 40, 44, 200), width=4)
f = sans("Black", 84); sd.text((310, 100), "ЛИЧНОЕ", font=f, fill=(214, 40, 44, 235), anchor="mm")
rng = np.random.default_rng(3); al = np.asarray(st.getchannel("A")).astype(np.float32) * (rng.random((200, 620)) > 0.12)
st.putalpha(Image.fromarray(al.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
st = st.rotate(-12, expand=True, resample=Image.BICUBIC); st = st.resize((int(st.width * 0.72), int(st.height * 0.72)), Image.LANCZOS)

# красная плашка-хук
txt = "ИМПЕРАТОР\nПИСАЛ ЭТО\nТОЛЬКО СЕБЕ"; f = sans("Black", 118); y = 1010
x0, y0, x1, y1 = d.multiline_textbbox((W // 2, y), txt, font=f, anchor="ma", align="center", spacing=10)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 - 50, y0 - 30 + 18, x1 + 50, y1 + 50 + 18), 34, fill=(0, 0, 0, 170))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); d = ImageDraw.Draw(im)
d.rounded_rectangle((x0 - 50, y0 - 30, x1 + 50, y1 + 50), 34, fill=(176, 22, 30)); d.rounded_rectangle((x0 - 50, y0 - 30, x1 + 50, y1 + 50), 34, outline=GOLD, width=4)
d.multiline_text((W // 2, y), txt, font=f, fill=(255, 250, 240), anchor="ma", align="center", spacing=10)
im.alpha_composite(st, (W - st.width - 24, y0 - st.height + 10)); d = ImageDraw.Draw(im)
yb = y1 + 140
spaced(d, (W // 2, yb), "МАРК АВРЕЛИЙ", serif("Bold", 84), WHITE, 8)
d.text((W // 2, yb + 82), "5 правил, которые он не собирался показывать", font=serif("MediumItalic", 44), fill=(225, 212, 190), anchor="mm")
im.convert("RGB").save(f"{HERE}/covers/10_marcus_click.jpg", quality=94)
g = im.convert("RGB").crop((0, 240, W, 1680)).resize((360, 480), Image.LANCZOS); g.save(f"{HERE}/covers/10_marcus_click_grid.jpg", quality=92)
print("ok")
