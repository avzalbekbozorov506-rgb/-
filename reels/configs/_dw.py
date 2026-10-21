"""Общие помощники недели «ВЕСЫ»: фон, шрифты, финальная карточка."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1080, 1920
GOLD, WHITE, GREY, RED, BLUE = (214, 178, 112), (246, 240, 228), (150, 140, 128), (200, 40, 46), (130, 150, 230)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bg():
    im = Image.new("RGBA", (W, H), (16, 14, 20, 255)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = abs(y - 900) / 900; d.rectangle((0, y, W, y + 4), fill=(int(26 - 12 * k), int(22 - 10 * k), int(30 - 12 * k), 255))
    return im
def tc(d, xy, t, size, fill, style="Black"): d.text(xy, t, font=sans(style, size), fill=fill, anchor="mm")
def phone(d, x, y, w=300, h=560, fill=(30, 30, 40, 255), outline=(90, 90, 110, 255)):
    d.rounded_rectangle((x - w // 2, y - h // 2, x + w // 2, y + h // 2), 40, fill=fill, outline=outline, width=6)
def cta_card(l1, l2, l3):
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.7)
        for i, (t, sz, col) in enumerate(((l1[0], 56, GOLD), (l1[1], 56, GOLD), (l2, 92, WHITE), (l3[0], 46, GREY), (l3[1], 46, GREY))):
            tc(d, (W // 2, (700, 800, 980, 1100, 1170)[i]), t, sz, col + (int(255 * k),))
        return im
    return f
