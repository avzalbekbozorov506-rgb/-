"""Набор для роликов «Чтение страницы»: страница книги с маркером и простые карточки (чат, календарь, тарелки, расстояние).
Все картинки 1620x2880 (как gen_book_page.py), сохраняются в art/<имя>.jpg."""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1620, 2880
def F(name, size):
    p = {"m": "CormorantGaramond-Medium.ttf", "b": "CormorantGaramond-Bold.ttf", "i": "CormorantGaramond-MediumItalic.ttf"}.get(name)
    return ImageFont.truetype(f"{HERE}/fonts/{p}", size) if p else ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{name}.otf", size)
FONT, FB, FS = F("m", 84), F("b", 96), F("i", 70)
ML = MR = 270; TOP = 540
def paper():
    r = np.random.default_rng(3); a = np.zeros((H, W, 3), np.float32); a[:] = (238, 228, 205)
    a += r.normal(0, 4, (H, W, 1)); yy, xx = np.mgrid[0:H, 0:W]
    a *= (1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2)[..., None]
    a[:, :60] *= np.linspace(0.8, 1, 60)[None, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def layout(text):
    words = text.split(" "); lines = []; cur = []
    for w in words:
        if FONT.getlength(" ".join(cur + [w])) > W - ML - MR and cur: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur); out = []; y = TOP; pos = 0
    for ln in lines:
        x = ML; just = ln is not lines[-1]; wsum = sum(FONT.getlength(w) for w in ln)
        gap = ((W - ML - MR) - wsum) / max(len(ln) - 1, 1) if just else FONT.getlength(" ")
        for w in ln:
            st = text.index(w, pos); pos = st + len(w); out.append((w, x, y, st, pos)); x += FONT.getlength(w) + gap
        y += 118
    return out
def page(name, title, sub, text, span, footer):
    """span = (начало, конец) подсвечиваемого куска (конец None — до конца текста). Печатает/возвращает вертикальный центр маркера."""
    words = layout(text); im = paper().convert("RGBA"); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s, e = span; i0 = text.index(s); i1 = len(text) if e is None else text.index(e, i0) + len(e)
    hl = [(x, y, FONT.getlength(w)) for w, x, y, a, b in words if a >= i0 and b <= i1]
    for x, y, wl in hl: d.rectangle((x - 8, y + 6, x + wl + 8, y + 104), fill=(255, 214, 40, 150))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2))); d = ImageDraw.Draw(im)
    d.text((W // 2, 200), title, font=FB, fill=(40, 30, 24), anchor="mm")
    d.text((W // 2, 330), sub, font=FS, fill=(70, 56, 46), anchor="mm")
    d.line((W // 2 - 160, 410, W // 2 + 160, 410), fill=(120, 90, 60), width=3)
    for w, x, y, a, b in words: d.text((x, y), w, font=FONT, fill=(34, 26, 22))
    d.text((W // 2, H - 200), footer, font=FS, fill=(120, 104, 90), anchor="mm")
    cy = sum(y + 55 for x, y, wl in hl) / len(hl) / H
    im.convert("RGB").save(f"{HERE}/art/{name}.jpg", quality=92); return round(cy, 3)
# ---------- карточки на тёмном фоне ----------
def dark():
    yy = np.linspace(0, 1, H)[:, None]; a = np.zeros((H, W, 3), np.float32)
    a[:] = (np.array([18, 22, 34]) * (1 - yy) + np.array([8, 10, 18]) * yy)[:, None, :].reshape(H, 1, 3)
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")
def wrap(d, text, font, maxw):
    out = []; cur = ""
    for w in text.split(" "):
        if d.textlength((cur + " " + w).strip(), font=font) > maxw and cur: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + [cur]
def chat(name, who, msgs, typing=None, stamp=None, note=None):
    """msgs: [(от_кого 'me'|'them', текст, метка_времени)], typing — строка в поле ввода, note — подпись «ПРИМЕР» сверху."""
    im = dark(); d = ImageDraw.Draw(im); f = F("Medium", 70); fs = F("Regular", 44); fh = F("SemiBold", 64)
    d.rounded_rectangle((170, 560, W - 170, 1560), 70, fill=(28, 34, 50, 255))
    d.text((W // 2, 650), who, font=fh, fill=(235, 238, 245), anchor="mm")
    d.line((230, 720, W - 230, 720), fill=(60, 68, 90), width=3)
    y = 800
    for frm, t, ts in msgs:
        lines = wrap(d, t, f, 800); hh = 100 + 86 * len(lines) - 20
        x1 = W - 250 if frm == "me" else 250 + 900
        x0 = x1 - 900 if frm == "me" else 250
        d.rounded_rectangle((x0, y, x1, y + hh), 50, fill=(54, 108, 190, 255) if frm == "me" else (52, 60, 82, 255))
        for k, ln in enumerate(lines): d.text((x0 + 45, y + 40 + 86 * k), ln, font=f, fill=(245, 247, 252))
        if ts: d.text((x1 - 40 if frm == "me" else x0 + 45, y + hh + 14), ts, font=fs, fill=(130, 140, 165), anchor="ra" if frm == "me" else "la")
        y += hh + 100
    if typing is not None:
        d.rounded_rectangle((230, 1380, W - 230, 1510), 65, fill=(40, 48, 68, 255)); ft = f; sz = 70
        while d.textlength(typing + "|", font=ft) > W - 560 and sz > 36: sz -= 4; ft = F("Medium", sz)
        d.text((290, 1445), typing + "|", font=ft, fill=(245, 247, 252), anchor="lm")
    if note: d.text((W // 2, 460), note, font=F("SemiBold", 56), fill=(255, 214, 40), anchor="mm")
    im.convert("RGB").save(f"{HERE}/art/{name}.jpg", quality=92)
def calendar(name, rows, note=None, big=None):
    """rows: [(текст, зачёркнут, пометка)] — список «приеду на …»."""
    im = dark(); d = ImageDraw.Draw(im); f = F("SemiBold", 82); fs = F("Medium", 54)
    d.rounded_rectangle((170, 600, W - 170, 600 + 260 * len(rows) + 160), 70, fill=(28, 34, 50, 255))
    y = 700
    for t, cross, mark in rows:
        d.text((260, y), t, font=f, fill=(235, 238, 245) if not cross else (120, 128, 150), anchor="lm")
        if cross: w_ = d.textlength(t, font=f); d.line((255, y + 4, 265 + w_, y + 4), fill=(220, 70, 70), width=8)
        if mark: d.text((W - 260, y + 100), mark, font=fs, fill=(230, 90, 90) if cross else (120, 220, 150), anchor="rm")
        y += 260
    if big: d.text((W // 2, 600 + 260 * len(rows) + 330), big, font=F("Black", 110), fill=(120, 220, 150), anchor="mm")
    if note: d.text((W // 2, 480), note, font=F("SemiBold", 56), fill=(255, 214, 40), anchor="mm")
    im.convert("RGB").save(f"{HERE}/art/{name}.jpg", quality=92)
def plates(name, filled, total=30, caption=None, note=None):
    im = dark(); d = ImageDraw.Draw(im); cols = 6; r = 100; gx = 220; gy = 260
    x0 = (W - (cols - 1) * gx) // 2; y0 = 800
    for k in range(total):
        cx = x0 + (k % cols) * gx; cy = y0 + (k // cols) * gy
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(200, 205, 220), width=6, fill=(250, 244, 230) if k < filled else None)
        d.ellipse((cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), outline=(200, 205, 220) if k >= filled else (190, 180, 160), width=3)
    if caption: d.text((W // 2, 800 + (total // cols) * gy + 40), caption, font=F("Black", 96), fill=(255, 214, 40), anchor="mm")
    if note: d.text((W // 2, 520), note, font=F("SemiBold", 56), fill=(255, 214, 40), anchor="mm")
    im.convert("RGB").save(f"{HERE}/art/{name}.jpg", quality=92)
def distance(name, left, right, mid, bottom=None):
    im = dark(); d = ImageDraw.Draw(im); f = F("SemiBold", 70)
    for cx, t in ((380, left), (W - 380, right)):
        d.polygon([(cx - 130, 1050), (cx, 900), (cx + 130, 1050)], fill=(250, 244, 230)); d.rectangle((cx - 110, 1050, cx + 110, 1220), fill=(250, 244, 230))
        d.rectangle((cx - 28, 1120, cx + 28, 1220), fill=(18, 22, 34)); d.text((cx, 1320), t, font=f, fill=(235, 238, 245), anchor="mm")
    d.line((560, 1135, W - 560, 1135), fill=(255, 214, 40), width=8)
    d.text((W // 2, 1030), mid, font=F("Black", 96), fill=(255, 214, 40), anchor="mm")
    if bottom: d.text((W // 2, 1560), bottom, font=F("Black", 110), fill=(230, 90, 90), anchor="mm")
    im.convert("RGB").save(f"{HERE}/art/{name}.jpg", quality=92)
