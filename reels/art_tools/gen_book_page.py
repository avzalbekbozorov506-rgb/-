"""Страница книги для ролика mach_liar: бумага, сверху глава, текст «Государя» (свой перевод), жёлтый маркер на нужной фразе.
Запуск: python3 art_tools/gen_book_page.py  -> art/page_liar_<n>.jpg; печатает вертикальный центр маркера (доля высоты)."""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1620, 2880
FONT = ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-Medium.ttf", 84)
FB = ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-Bold.ttf", 96)
FS = ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-MediumItalic.ttf", 70)
TEXT = ("Александр VI только и делал, что обманывал людей, ни о чём другом не думал — и всегда находил тех, кто давал ему на это возможность. "
        "Не было человека, который с большей уверенностью давал бы заверения и клялся бы крепче — и соблюдал бы слово меньше. "
        "И всё же обманы всегда удавались ему, ибо он хорошо знал эту сторону мира. "
        "Люди так простодушны и так подчиняются нуждам минуты, что обманщик всегда найдёт того, кто позволит себя обмануть.")
SPANS = {   # номер страницы -> (начало, конец) подсвечиваемого куска
    0: ("только и делал, что обманывал людей", "возможность."),
    1: ("клялся бы крепче", "меньше."),
    2: ("Александр VI только и делал, что обманывал людей", "людей,"),
    3: ("И всё же обманы всегда удавались ему", "мира."),
    4: ("обманщик всегда найдёт того, кто позволит себя обмануть.", None),
    5: ("соблюдал бы слово меньше.", None),
    6: ("обманщик всегда найдёт того, кто позволит себя обмануть.", None),
}
ML, MR, TOP = 270, 270, 540
def layout():
    words = TEXT.split(" "); lines = []; cur = []; pos = 0; out = []
    for w in words:
        t = " ".join(cur + [w])
        if FONT.getlength(t) > W - ML - MR and cur: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur)
    idx = 0; y = TOP
    for ln in lines:
        x = ML; just = ln is not lines[-1]; wsum = sum(FONT.getlength(w) for w in ln)
        gap = ((W - ML - MR) - wsum) / max(len(ln) - 1, 1) if just else FONT.getlength(" ")
        for w in ln:
            out.append((w, x, y, idx)); x += FONT.getlength(w) + gap; idx += 1
        y += 118
    return out
def paper():
    r = np.random.default_rng(3); a = np.zeros((H, W, 3), np.float32); a[:] = (238, 228, 205)
    a += r.normal(0, 4, (H, W, 1)); yy, xx = np.mgrid[0:H, 0:W]
    a *= (1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2)[..., None]
    a[:, :60] *= np.linspace(0.8, 1, 60)[None, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def page(n):
    words = layout(); im = paper().convert("RGBA"); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s, e = SPANS[n]; i0 = TEXT.index(s); i1 = len(TEXT) if e is None else TEXT.index(e, i0) + len(e)
    c = 0; hl = []
    for w, x, y, k in words:
        a_, b_ = TEXT.index(w, c) if w in TEXT[c:] else c, 0; c = TEXT.index(w, c) + len(w); st = c - len(w)
        if st >= i0 and c <= i1: hl.append((x, y, FONT.getlength(w)))
    for x, y, wl in hl: d.rectangle((x - 8, y + 6, x + wl + 8, y + 104), fill=(255, 214, 40, 150))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 200), "ГЛАВА XVIII", font=FB, fill=(40, 30, 24), anchor="mm")
    d.text((W // 2, 330), "О том, как государи должны держать слово", font=FS, fill=(70, 56, 46), anchor="mm")
    d.line((W // 2 - 160, 410, W // 2 + 160, 410), fill=(120, 90, 60), width=3)
    for w, x, y, k in words: d.text((x, y), w, font=FONT, fill=(34, 26, 22))
    d.text((W // 2, H - 200), "Н. Макиавелли. «Государь». Перевод свой", font=FS, fill=(120, 104, 90), anchor="mm")
    cy = sum(y + 55 for x, y, wl in hl) / len(hl) / H
    im.convert("RGB").save(f"{HERE}/art/page_liar_{n}.jpg", quality=92); return cy
if __name__ == "__main__":
    for n in SPANS: print(n, round(page(n), 3))
