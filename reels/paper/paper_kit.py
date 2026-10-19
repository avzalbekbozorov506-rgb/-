"""Бумажный стиль (вырезки на тёмном фоне): карточки, ленты-надписи, трубы с кранами, монеты, штампы. Рисует кадры 1080×1920 для cinema_engine."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
W, H = 1080, 1920
BG = (38, 33, 30); PAPER = (236, 228, 210); CREAM = (243, 236, 214); YEL = (238, 222, 150); RED = (196, 44, 38)
INK = (34, 30, 28); GOLD = (214, 170, 60); PIPE = (128, 132, 138); GREEN = (96, 160, 110)
def F(size, bold=True): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size)
def S(size, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", size)
def background(seed=1, light=False):
    r = np.random.default_rng(seed); base = np.array(CREAM if light else BG, np.float32)
    a = base + r.normal(0, 5, (H, W, 1)); yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.35 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    return Image.fromarray(np.clip(a * v[..., None], 0, 255).astype(np.uint8)).convert("RGBA")
def shadow(im, box, rad=18, off=(10, 14), alpha=150, angle=0):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rectangle(box, fill=(0, 0, 0, alpha))
    lay = lay.filter(ImageFilter.GaussianBlur(rad)); im.alpha_composite(lay, off)
def torn(w, h, color, seed=0, edge=6):
    r = random.Random(seed); im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(x, r.uniform(0, edge)) for x in range(0, w + 1, 12)] + [(w - r.uniform(0, edge), y) for y in range(0, h + 1, 12)] + \
          [(x, h - r.uniform(0, edge)) for x in range(w, -1, -12)] + [(r.uniform(0, edge), y) for y in range(h, -1, -12)]
    d.polygon(pts, fill=color)
    n = np.asarray(im).astype(np.float32); n[..., :3] += np.random.default_rng(seed).normal(0, 4, n[..., :3].shape); return Image.fromarray(np.clip(n, 0, 255).astype(np.uint8))
def card(im, xy, size, lines, color=PAPER, fonts=None, colors=None, angle=0, seed=0, pad=26, align="center"):
    w, h = size; c = torn(w, h, color + (255,), seed); d = ImageDraw.Draw(c)
    fonts = fonts or [F(48)] * len(lines); colors = colors or [INK] * len(lines)
    tot = sum(fo.getbbox("Ay")[3] + 10 for fo in fonts); y = (h - tot) / 2
    for t, fo, co in zip(lines, fonts, colors):
        hh = fo.getbbox("Ay")[3]
        if align == "center": d.text((w / 2, y), t, font=fo, fill=co, anchor="ma")
        else: d.text((pad, y), t, font=fo, fill=co)
        y += hh + 10
    c = c.rotate(angle, expand=True, resample=Image.BICUBIC); x, yv = xy
    shadow(im, (x, yv, x + c.width, yv + c.height), angle=angle); im.alpha_composite(c, (int(x), int(yv)))
    return (x, yv, x + c.width, yv + c.height)
def tape(im, y, text, hl=None, angle=-1.0):
    """Белая лента-надпись сверху кадра; hl — слово, выделенное красным."""
    fo = F(34); w = int(fo.getlength(text)) + 60; c = torn(w, 64, (240, 238, 232, 240), seed=len(text), edge=4); d = ImageDraw.Draw(c)
    x = 30
    for word in text.split(" "):
        col = RED if hl and word.strip(".,!?«»").lower() == hl.lower() else INK
        if col == RED:
            ww = fo.getlength(word); d.rectangle((x - 4, 14, x + ww + 4, 50), fill=(220, 70, 60, 255)); col = (255, 255, 255)
        d.text((x, 14), word, font=fo, fill=col); x += fo.getlength(word + " ")
    c = c.rotate(angle, expand=True, resample=Image.BICUBIC); im.alpha_composite(c, ((W - c.width) // 2, y))
def badge(im, xy, n, r=34):
    d = ImageDraw.Draw(im); x, y = xy; d.ellipse((x - r, y - r, x + r, y + r), fill=RED); d.text((x, y), str(n), font=S(40), fill=(255, 255, 255), anchor="mm")
def label(im, xy, text, color=RED, fg=(255, 255, 255), size=34, angle=0):
    fo = S(size, "Bold"); w = int(fo.getlength(text)) + 40; h = size + 26
    c = torn(w, h, color + (255,), seed=len(text), edge=3); ImageDraw.Draw(c).text((w / 2, h / 2), text, font=fo, fill=fg, anchor="mm")
    c = c.rotate(angle, expand=True, resample=Image.BICUBIC); x, y = xy
    shadow(im, (x - c.width / 2, y - c.height / 2, x + c.width / 2, y + c.height / 2), rad=8, off=(5, 7), alpha=120)
    im.alpha_composite(c, (int(x - c.width / 2), int(y - c.height / 2)))
def pipe(im, a, b, wdt=34, color=PIPE):
    """Труба от a до b (горизонтальная или вертикальная) с болтами."""
    d = ImageDraw.Draw(im); (x0, y0), (x1, y1) = a, b
    if y0 == y1: box = (min(x0, x1), y0 - wdt / 2, max(x0, x1), y0 + wdt / 2)
    else: box = (x0 - wdt / 2, min(y0, y1), x0 + wdt / 2, max(y0, y1))
    shadow(im, box, rad=6, off=(5, 6), alpha=140); d = ImageDraw.Draw(im)
    d.rectangle(box, fill=color); hi = tuple(min(255, c + 40) for c in color)
    if y0 == y1:
        d.rectangle((box[0], box[1] + 4, box[2], box[1] + 10), fill=hi)
        for x in range(int(box[0]) + 20, int(box[2]) - 10, 70): d.ellipse((x - 5, y0 - 5, x + 5, y0 + 5), fill=GOLD)
    else:
        d.rectangle((box[0] + 4, box[1], box[0] + 10, box[3]), fill=hi)
        for y in range(int(box[1]) + 20, int(box[3]) - 10, 70): d.ellipse((x0 - 5, y - 5, x0 + 5, y + 5), fill=GOLD)
def tap(im, xy, open_=True, color=GOLD):
    """Кран вниз из горизонтальной трубы в точке xy (y — ось трубы)."""
    d = ImageDraw.Draw(im); x, y = xy
    d.rectangle((x - 14, y, x + 14, y + 60), fill=color); d.rectangle((x - 26, y + 50, x + 26, y + 70), fill=color)
    d.rectangle((x - 30, y + 14, x + 30, y + 24), fill=RED if open_ else (90, 90, 90))
def drops(im, xy, n=3, color=GOLD, step=34):
    d = ImageDraw.Draw(im); x, y = xy
    for k in range(n): yy = y + k * step; d.ellipse((x - 9, yy - 9, x + 9, yy + 9), fill=color, outline=(150, 110, 30), width=2)
def coins(im, xy, n=6, r=26, seed=0):
    rr = random.Random(seed); d = ImageDraw.Draw(im); x, y = xy
    for k in range(n):
        cx, cy = x + rr.uniform(-60, 60), y - k * 12 + rr.uniform(-4, 4)
        d.ellipse((cx - r, cy - r * 0.45, cx + r, cy + r * 0.45), fill=GOLD, outline=(150, 110, 30), width=3)
def coin_big(im, xy, r=70, text="₽"):
    d = ImageDraw.Draw(im); x, y = xy; shadow(im, (x - r, y - r, x + r, y + r), rad=10, off=(6, 8), alpha=140); d = ImageDraw.Draw(im)
    d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD, outline=(150, 110, 30), width=6); d.text((x, y), text, font=S(int(r * 1.1)), fill=(120, 85, 20), anchor="mm")
def bucket(im, xy, w=150, h=130, fill_pct=0.0, label_txt=None, color=(240, 240, 236)):
    d = ImageDraw.Draw(im); x, y = xy
    poly = [(x - w / 2, y), (x + w / 2, y), (x + w / 2 - 18, y + h), (x - w / 2 + 18, y + h)]
    shadow(im, (x - w / 2, y, x + w / 2, y + h), rad=8, off=(6, 8), alpha=130); d = ImageDraw.Draw(im); d.polygon(poly, fill=color)
    if fill_pct > 0:
        fy = y + h * (1 - fill_pct); k = (fy - y) / h * 18
        d.polygon([(x - w / 2 + k, fy), (x + w / 2 - k, fy), (x + w / 2 - 18, y + h), (x - w / 2 + 18, y + h)], fill=GREEN)
    if label_txt: label(im, (x, y + h + 40), label_txt, color=INK, size=26)
def building(im, xy, w=220, kind="bank", txt=None):
    d = ImageDraw.Draw(im); x, y = xy; col = (232, 230, 224)
    shadow(im, (x - w / 2, y - w * 0.5, x + w / 2, y + w * 0.55), rad=10, off=(6, 8), alpha=120); d = ImageDraw.Draw(im)
    if kind == "bank":
        d.polygon([(x - w / 2, y - w * 0.15), (x, y - w * 0.5), (x + w / 2, y - w * 0.15)], fill=col)
        for k in range(5): cx = x - w * 0.4 + k * w * 0.2; d.rectangle((cx - 9, y - w * 0.1, cx + 9, y + w * 0.35), fill=col)
        d.rectangle((x - w / 2, y + w * 0.35, x + w / 2, y + w * 0.5), fill=col)
    elif kind == "house":
        d.polygon([(x - w / 2, y), (x, y - w * 0.45), (x + w / 2, y)], fill=(150, 90, 60)); d.rectangle((x - w * 0.4, y, x + w * 0.4, y + w * 0.5), fill=(214, 190, 150))
        d.rectangle((x - 22, y + w * 0.2, x + 22, y + w * 0.5), fill=(110, 70, 45))
    elif kind == "shop":
        d.rectangle((x - w / 2, y - w * 0.1, x + w / 2, y + w * 0.5), fill=(110, 70, 50))
        for k in range(6): d.rectangle((x - w / 2 + k * w / 6, y - w * 0.3, x - w / 2 + (k + 1) * w / 6, y - w * 0.1), fill=RED if k % 2 else (240, 240, 236))
    if txt: label(im, (x, y + w * 0.5 + 40), txt, color=RED, size=26)
def person(im, xy, scale=1.0, color=(236, 232, 222), apron=None, hat=None):
    """Бумажный человечек из прямоугольников."""
    d = ImageDraw.Draw(im); x, y = xy; s = scale
    parts = [((x - 40 * s, y - 230 * s, x + 40 * s, y - 150 * s), color), ((x - 55 * s, y - 145 * s, x + 55 * s, y - 10 * s), color),
             ((x - 80 * s, y - 140 * s, x - 58 * s, y - 40 * s), color), ((x + 58 * s, y - 140 * s, x + 80 * s, y - 40 * s), color),
             ((x - 45 * s, y - 8 * s, x - 10 * s, y + 110 * s), color), ((x + 10 * s, y - 8 * s, x + 45 * s, y + 110 * s), color)]
    for b, c in parts: shadow(im, b, rad=6, off=(5, 6), alpha=110)
    d = ImageDraw.Draw(im)
    for b, c in parts: d.rectangle(b, fill=c)
    if apron: d.rectangle((x - 45 * s, y - 120 * s, x + 45 * s, y - 15 * s), fill=apron)
    d.rectangle((x - 22 * s, y - 200 * s, x - 10 * s, y - 188 * s), fill=INK); d.rectangle((x + 10 * s, y - 200 * s, x + 22 * s, y - 188 * s), fill=INK)
    d.line((x - 15 * s, y - 170 * s, x + 15 * s, y - 170 * s), fill=INK, width=max(2, int(4 * s)))
    if hat: d.rectangle((x - 46 * s, y - 248 * s, x + 46 * s, y - 226 * s), fill=hat)
def save(im, name): im.convert("RGB").save(f"/home/user/-/reels/art/{name}.jpg", quality=94)
