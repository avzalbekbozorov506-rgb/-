"""Мягкие субтитры формата «Клод»: Inter SemiBold, тёплый белый, полупрозрачная скруглённая подложка, мягкая тень (без жирной обводки)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def _f(sz, w="SemiBold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)

def soft_sub_layer(text, cta, W, H):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); fs = _f(54); rows, cur = [], ""
    for w_ in text.split():
        if d.textlength((cur + " " + w_).strip(), font=fs) > 860: rows.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    rows.append(cur); lh = 76; y0 = 1500
    if cta: y0 = min(y0, 1672 - lh * len(rows) - 6)
    wmax = max(d.textlength(r, font=fs) for r in rows); bx0, bx1 = (W - wmax) / 2 - 44, (W + wmax) / 2 + 44; by0, by1 = y0 - 22, y0 + lh * len(rows) + 6
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((bx0, by0 + 6, bx1, by1 + 6), 40, fill=(0, 0, 0, 110)); pill = pill.filter(ImageFilter.GaussianBlur(14))      # мягкая тень подложки
    ov.alpha_composite(pill); d = ImageDraw.Draw(ov)
    d.rounded_rectangle((bx0, by0, bx1, by1), 40, fill=(22, 20, 28, 138))                                                              # подложка
    for i, r in enumerate(rows):
        x = (W - d.textlength(r, font=fs)) / 2; y = y0 + lh * i
        d.text((x, y + 2), r, font=fs, fill=(0, 0, 0, 90))                                                                            # лёгкая тень текста
        d.text((x, y), r, font=fs, fill=(255, 251, 243, 255))
    if cta:
        fc = _f(40, "Bold"); t = "Подписаться  ·  @mysli.vekov"; tw = d.textlength(t, font=fc)
        d.rounded_rectangle(((W - tw) / 2 - 38, 1700, (W + tw) / 2 + 38, 1782), 41, fill=(255, 226, 150, 245)); d.text(((W - tw) / 2, 1719), t, font=fc, fill=(48, 36, 28, 255))
    return ov
