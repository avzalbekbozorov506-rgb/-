"""Единые обложки для Reels (1080×1920, важное — в центральной зоне 3:4, которую показывает сетка профиля)."""
import importlib.util, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
W, H = 1080, 1920; GOLD, WHITE, GREY = (214, 178, 112), (248, 242, 230), (190, 180, 166)
def serif(s, z): return ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-{s}.ttf", z)
def sans(s, z): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{s}.otf", z)
def cfg(name):
    sp = importlib.util.spec_from_file_location(name, f"{HERE}/configs/{name}.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def cover_crop(im, fx=0.5, fy=0.4, zoom=1.0):
    s = max(W / im.width, H / im.height) * zoom; im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = min(max(int(fx * im.width - W / 2), 0), im.width - W); y = min(max(int(fy * im.height - H / 2), 0), im.height - H)
    return im.crop((x, y, x + W, y + H))
def spaced(d, xy, text, f, fill, sp=6):
    w = sum(d.textlength(c, font=f) + sp for c in text) - sp; x = xy[0] - w / 2
    for c in text: d.text((x, xy[1]), c, font=f, fill=fill, anchor="lm"); x += d.textlength(c, font=f) + sp
def make(bg, title, sub, tag, out):
    im = ImageEnhance.Color(bg.convert("RGB")).enhance(0.9)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.clip((yy - 820) / 700, 0, 1) ** 1.2 * 235 + np.clip((420 - yy) / 420, 0, 1) * 150
    a = np.maximum(a, np.clip(((xx - W / 2) ** 2 / (W * 0.7) ** 2 + (yy - H * 0.45) ** 2 / (H * 0.62) ** 2) - 0.4, 0, 1) * 200)
    ov = Image.fromarray(np.dstack([np.full((H, W), 10), np.full((H, W), 8), np.full((H, W), 8), np.clip(a, 0, 240)]).astype(np.uint8), "RGBA")
    im = im.convert("RGBA"); im.alpha_composite(ov); d = ImageDraw.Draw(im)
    spaced(d, (W // 2, 330), "МЫСЛИ ВЕКОВ", sans("SemiBold", 28), GOLD, 9)                      # бренд — внутри зоны 3:4
    d.line(((W // 2 - 70, 368), (W // 2 + 70, 368)), fill=GOLD, width=2)
    lines = title.split("\n"); size = 150
    while size > 80 and max(d.textlength(l, font=serif("Bold", size)) + 10 * len(l) for l in lines) > 960: size -= 6
    y = 1310 - (len(lines) - 1) * size * 0.98
    for l in lines:
        spaced(d, (W // 2 + 3, y + 4), l, serif("Bold", size), (0, 0, 0, 150), 10); spaced(d, (W // 2, y), l, serif("Bold", size), WHITE, 10); y += size * 0.98
    d.line(((W // 2 - 110, y - size * 0.3), (W // 2 + 110, y - size * 0.3)), fill=GOLD, width=3)
    d.text((W // 2, y + 10), sub, font=serif("MediumItalic", 54), fill=GREY, anchor="mm")
    tw = d.textlength(tag, font=sans("Bold", 26)) + 18 * len(tag) * 0.25 + 60                   # метка рубрики
    d.rounded_rectangle((W // 2 - tw / 2, 1555, W // 2 + tw / 2, 1611), 28, outline=GOLD, width=2)
    spaced(d, (W // 2, 1584), tag, sans("Bold", 26), GOLD, 5)
    im.convert("RGB").save(f"{HERE}/covers/{out}.jpg", quality=94); return im

covers = []
fl = cfg("fox_lion"); covers.append(make(fl.s_lesson(3.0, 10.0), "ЛИСИЦА\nИ ЛЕВ", "Макиавелли · «Государь»", "ПРИТЧА", "01_lisitsa_i_lev"))
np_ = cfg("nails_parable"); covers.append(make(np_.s_holes(2.0, 9.0), "ГВОЗДИ", "Притча о словах в гневе", "ПРИТЧА", "02_gvozdi"))
covers.append(make(cover_crop(Image.open(f"{HERE}/art/bronzino.jpg"), 0.5, 0.3, 1.35), "МАКИАВЕЛЛИ", "«Государь» — 5 мыслей", "5 МЫСЛЕЙ", "03_makiavelli"))
ma = cfg("marcus_aurelius"); covers.append(make(cover_crop(ma.dark_studio(Image.open(f"{HERE}/art/ma_bronze.jpg").convert("RGB")), 0.5, 0.32, 1.25), "МАРК\nАВРЕЛИЙ", "«Наедине с собой» — 5 мыслей", "5 МЫСЛЕЙ", "04_mark_avreliy"))
st = cfg("sun_tzu"); covers.append(make(st.s_intro(3.0, 9.0), "СУНЬ-ЦЗЫ", "«Искусство войны»", "5 ПРИНЦИПОВ", "05_sun_tszy"))
tl = cfg("tolstoy_land"); covers.append(make(tl.s_fall(5.5, 7.1), "ТОЛСТОЙ", "«Много ли человеку земли нужно»", "ИСТОРИЯ", "06_tolstoy"))
# превью сетки профиля: 3 колонки, кадр 3:4 по центру
grid = Image.new("RGB", (3 * 360 + 8, 2 * 480 + 4), (255, 255, 255))
for k, c in enumerate(covers):
    t = c.convert("RGB").crop((0, 240, W, 1680)).resize((360, 480), Image.LANCZOS); grid.paste(t, ((k % 3) * 364, (k // 3) * 484))
grid.save(f"{HERE}/covers/grid_preview.jpg", quality=92); print("ok")
