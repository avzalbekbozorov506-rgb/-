"""Кликбейт-обложки: крупная красная плашка-хук + штамп + название. Всё важное — в зоне 3:4 (y 240–1680) для сетки профиля."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers import cover_crop, spaced, serif, sans, cfg, W, H, GOLD, WHITE

def stamp(text, size=96):
    st = Image.new("RGBA", (620, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((10, 10, 610, 190), 18, outline=(214, 40, 44, 235), width=12); sd.rounded_rectangle((30, 30, 590, 170), 10, outline=(214, 40, 44, 200), width=4)
    while size > 40 and sd.textlength(text, font=sans("Black", size)) > 520: size -= 4
    sd.text((310, 102), text, font=sans("Black", size), fill=(214, 40, 44, 235), anchor="mm")
    al = np.asarray(st.getchannel("A")).astype(np.float32) * (np.random.default_rng(3).random((200, 620)) > 0.12)
    st.putalpha(Image.fromarray(al.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    st = st.rotate(-12, expand=True, resample=Image.BICUBIC); return st.resize((int(st.width * 0.72), int(st.height * 0.72)), Image.LANCZOS)

def make_click(bg, hook, stamp_text, title, sub, out, y=1010, dark_top=False, stamp_pos="top", logo_y=300):
    im = ImageEnhance.Contrast(ImageEnhance.Color(bg.convert("RGB")).enhance(0.95)).enhance(1.1).convert("RGBA")
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.clip((yy - 1150) / 500, 0, 1) ** 1.1 * 235 + np.clip((300 - yy) / 300, 0, 1) * 120
    if dark_top: a = np.maximum(a, np.clip((760 - yy) / 500, 0, 1) * 150)
    a = np.maximum(a, np.clip(((xx - W / 2) ** 2 / (W * 0.72) ** 2 + (yy - H * 0.42) ** 2 / (H * 0.55) ** 2) - 0.45, 0, 1) * 200)
    im.alpha_composite(Image.fromarray(np.dstack([np.full((H, W), 10), np.full((H, W), 6), np.full((H, W), 6), np.clip(a, 0, 245)]).astype(np.uint8), "RGBA"))
    d = ImageDraw.Draw(im)
    spaced(d, (W // 2, logo_y), "МЫСЛИ ВЕКОВ", sans("SemiBold", 28), GOLD, 9); d.line(((W // 2 - 70, logo_y + 38), (W // 2 + 70, logo_y + 38)), fill=GOLD, width=2)
    size = 118
    while size > 70 and max(d.textlength(l, font=sans("Black", size)) for l in hook.split("\n")) > 900: size -= 4
    f = sans("Black", size)
    x0, y0, x1, y1 = d.multiline_textbbox((W // 2, y), hook, font=f, anchor="ma", align="center", spacing=10)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 - 50, y0 - 12, x1 + 50, y1 + 68), 34, fill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0 - 50, y0 - 30, x1 + 50, y1 + 50), 34, fill=(176, 22, 30)); d.rounded_rectangle((x0 - 50, y0 - 30, x1 + 50, y1 + 50), 34, outline=GOLD, width=4)
    d.multiline_text((W // 2, y), hook, font=f, fill=(255, 250, 240), anchor="ma", align="center", spacing=10)
    if stamp_text:
        st = stamp(stamp_text); sy = int(y0) - st.height + 40 if stamp_pos == "top" else int(y1) + 10
        im.alpha_composite(st, (min(W - st.width - 24, int(x1) - st.width + 90), sy)); d = ImageDraw.Draw(im)
    yb = max(y1 + (140 if stamp_pos == "top" else 250), 1420)
    spaced(d, (W // 2, yb), title, serif("Bold", 92 if len(title) < 12 else 80), WHITE, 8)
    d.text((W // 2, yb + 82), sub, font=serif("MediumItalic", 50), fill=(225, 212, 190), anchor="mm")
    im.convert("RGB").save(f"{HERE}/covers/{out}.jpg", quality=94); return im

if __name__ == "__main__":
    dp = cfg("dopamine_scale"); make_click(dp.s_gremlins(6.6, 8.0), "ПОЧЕМУ ТЕБЯ\nНИЧЕГО\nНЕ РАДУЕТ?", "ДОФАМИН", "ВЕСЫ", "Притча о дофамине", "07_vesy_click", y=960, stamp_pos="bottom")
    fl = cfg("fox_lion"); make_click(fl.s_lesson(3.0, 10.0), "СИЛА\nТЕБЯ\nНЕ СПАСЁТ", "МАКИАВЕЛЛИ", "ЛИСИЦА И ЛЕВ", "Притча из «Государя»", "01_lisitsa_click", y=420, dark_top=True, stamp_pos="bottom")
    np_ = cfg("nails_parable"); make_click(np_.s_holes(2.0, 9.0), "СКАЗАЛ\nВ ГНЕВЕ —\nПОЖАЛЕЕШЬ", "ПРИТЧА", "ГВОЗДИ", "Покажи тому, кто вспыльчив", "02_gvozdi_click", y=420, dark_top=True, stamp_pos="bottom")
    make_click(cover_crop(Image.open(f"{HERE}/art/bronzino.jpg"), 0.5, 0.3, 1.35), "ЛУЧШЕ СТРАХ,\nЧЕМ ЛЮБОВЬ?", "ЖЕСТОКО", "МАКИАВЕЛЛИ", "«Государь» — 5 мыслей", "03_makiavelli_click", y=1060)
    print("ok")
