"""Нейросети-кубики для роликов «баттл ИИ»: Gemini (сине-фиолетовый, значок-искра) и ChatGPT (зелёный, значок-розетка). Как claude() из cast.py."""
import math, numpy as np
from PIL import Image, ImageDraw
from cuberender import Box
from cast import _place, DARK

def _sparkle(col=(255, 255, 255), n=512):
    """Четырёхконечная искра (знак Gemini)."""
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = n / 2; pts = []
    for i in range(64):
        a = i / 64 * 2 * math.pi; r = c * .92 * (abs(math.cos(2 * a)) ** 1.0) ** .5 if False else None
    pts = []
    for i in range(240):
        a = i / 240 * 2 * math.pi; r = c * .95 / (abs(math.cos(a)) ** (2 / 3) + abs(math.sin(a)) ** (2 / 3)) ** 1.5   # астроида: вогнутые лучи
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=col + (255,)); return np.asarray(im, np.uint8)

def _rosette(col=(255, 255, 255), n=512):
    """Шестилепестковая розетка-узел (знак ChatGPT): шесть «петель», повёрнутых на 60°."""
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); c = n / 2
    for k in range(6):
        a = k * math.pi / 3; layer = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        d.rounded_rectangle((c - n * .13, c - n * .47, c + n * .13, c + n * .10), n * .13, outline=col + (255,), width=int(n * .085))
        layer = layer.rotate(-math.degrees(a), resample=Image.BICUBIC, center=(c, c)); im.alpha_composite(layer)
    return np.asarray(im, np.uint8)

def _tex(arr, bg):
    """Прозрачный значок -> непрозрачная картинка на фоне цвета тела (грань Box без альфы)."""
    a = arr[..., 3:4].astype(np.float32) / 255; out = arr[..., :3] * a + np.array(bg, np.float32) * (1 - a)
    return np.concatenate([out, np.full(out.shape[:2] + (1,), 255, np.float32)], -1).astype(np.uint8)

GEM = (74, 122, 232); GEM2 = (120, 92, 210); GPT = (16, 163, 127); GPT2 = (12, 120, 96)
_ICON = {}
def _icon(kind):
    if kind not in _ICON: _ICON[kind] = _tex(_sparkle() if kind == "gemini" else _rosette(), GEM if kind == "gemini" else GPT)
    return _ICON[kind]

def ai_bot(kind, pos, yaw=0.0, talk=0.0, blink=0.0, k=1.0, bob=0.0):
    """kind: 'gemini' | 'chatgpt'. Тело выше Клода (под значок), 4 ножки, ручки."""
    C, C2 = (GEM, GEM2) if kind == "gemini" else (GPT, GPT2)
    w, d, h = .92 * k, .62 * k, .78 * k
    z0 = .22 * k + bob
    eh = .15 * (1 - .9 * blink); ey = -.03
    dec = [(-.26, -.17, ey - eh / 2, ey + eh / 2, DARK), (.17, .26, ey - eh / 2, ey + eh / 2, DARK)]
    mh = .03 + .09 * talk; dec.append((-.07, .07, -.22 - mh / 2, -.22 + mh / 2, DARK))
    out = [Box(_place(pos, yaw, (0, 0, z0 + h / 2)), (w, d, h), C, yaw, dec, gloss=.35)]
    out.append(Box(_place(pos, yaw, (0, -d / 2 - .012 * k, z0 + h * .80)), (.30 * k, .03 * k, .30 * k), C, yaw, img=_icon(kind), shadow=False, rad=.005))   # значок на лбу
    for lx in (-.32, -.11, .11, .32):
        out.append(Box(_place(pos, yaw, (lx * k, 0, z0 / 2)), (.18 * k, .20 * k, z0), C2, yaw))
    for sx in (-1, 1):
        out.append(Box(_place(pos, yaw, (sx * (w / 2 + .06 * k), -.02, z0 + h * .30)), (.14 * k, .18 * k, .13 * k), C2, yaw))
    return out
