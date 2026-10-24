"""Кликбейт-обложка ai_time_1 (74): часы из ролика + крупный текст. Запуск: python3 make_covers_time2.py → covers/74_ai_time_click.jpg"""
import sys, os
sys.path.insert(0, "cartoon"); os.chdir(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import ai_time as T
W, H = 1080, 1920
T.words = lambda n: []
bg = Image.fromarray(T.frame(T.ev(11, 3) + 0.2)).convert("RGB")
a = np.asarray(bg, np.float32); a[:240] *= 0.0
bg = Image.fromarray(np.clip(a * 1.0, 0, 255).astype(np.uint8))
# сдвиг часов вниз и увеличение
cl = bg.crop((60, 380, 1020, 1340)); cl = Image.fromarray(np.clip(np.asarray(cl, np.float32) * 1.9, 0, 255).astype(np.uint8)).resize((1200, 1200), Image.LANCZOS); canvas = Image.new("RGB", (W, H), (2, 4, 10)); canvas.paste(cl, (-60, 720))
# виньетка + затемнение сверху под текст
arr = np.asarray(canvas, np.float32); yy = np.arange(H)[:, None, None] / H; arr *= np.clip(0.35 + 1.1 * yy * 1.2, 0, 1.2) * 0 + 1
top = np.clip(1 - np.arange(H) / 900, 0, 1)[:, None, None]; arr = arr * (1 - 0.6 * top)
canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
def wide(text, size, fill, stretch=1.25, weight="Black", stroke=0):
    f = ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf", size); bb = f.getbbox(text); w, h = bb[2] + 40, int(size * 1.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.text((20, 0), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im.resize((int(w * stretch), h), Image.BICUBIC)
def put(layer, im, cx, cy, glow=None):
    if glow:
        g = Image.new("RGBA", layer.size, (0, 0, 0, 0)); g.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2))); a_ = g.filter(ImageFilter.GaussianBlur(24)); layer.alpha_composite(a_); layer.alpha_composite(a_)
    layer.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
YEL, CY, RD, WH = (255, 214, 10, 255), (92, 200, 255, 255), (255, 60, 50, 255), (255, 255, 255, 255)
put(canvas, wide("Я СПРОСИЛ ИИ:", 82, WH, 1.0, "Black", 6), 540, 330)
put(canvas, wide("СОЗДАЙ", 190, YEL, 1.05, "Black", 10), 540, 520, glow=1)
put(canvas, wide("МАШИНУ", 190, YEL, 1.05, "Black", 10), 540, 700, glow=1)
put(canvas, wide("ВРЕМЕНИ", 190, YEL, 1.0, "Black", 10), 540, 880, glow=1)
# красная плашка снизу
bar = Image.new("RGBA", (860, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar); bd.rounded_rectangle((0, 0, 859, 149), 24, fill=RD); bd.text((430, 78), "ОН СДЕЛАЛ ЭТО", font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 84), fill=WH, anchor="mm")
bar = bar.rotate(-3, expand=True, resample=Image.BICUBIC); put(canvas, bar, 540, 1520)
canvas.convert("RGB").save("covers/74_ai_time_click.jpg", quality=94); print("ok")
