"""Формат «Объясняем» — 2D-анимация в стиле тёмной научной презентации (HUD, голубые линии, жёлтые цифры, слова-субтитры).
Ролик: «Tesla Roadster едет по потолку» (показ 15.10.2026). Сборка: python3 reels/explainer/build.py [out.mp4] [t1,t2,...]  (превью кадров по секундам)."""
import os, sys, math, re, hashlib, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile
import scipy.signal as ss
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "cubes"))
from subs_sync import sync
W, H, FPS, SR = 1080, 1920, 24, 48000
TMP = "/tmp/expl"; os.makedirs(TMP, exist_ok=True)
FD = "/usr/share/fonts/opentype/inter/"
def F(sz, w="Bold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", sz)
VOICE = dict(speaker=4, rate=.9)
GAP, LEAD, TAIL = .45, .3, .8

BG, CY, CY2, YEL, RED, GRN, WHITE = (6, 10, 22), (60, 200, 255), (30, 110, 160), (255, 176, 40), (255, 80, 80), (60, 230, 150), (240, 244, 250)

# ---------- сценарий: (озвучка для синтеза, субтитры без ударений, сцена) ----------
SCRIPT = [
 ("hook",   "Эта машина едет по потолку. И не падает."),
 ("event",  "Пятнадцатого октября Т+эсла показала новый Р+оудстер. Он въехал вверх колёсами по рампе, оторвался от неё, перевернулся в воздухе и сел на асфальт. Как это возможно?"),
 ("ceil",   "Начнём с потолка. Его не присасывает. Его прижимает воздух."),
 ("tons",   "На каждый квадратный метр давит около десяти тонн воздуха. Мы не замечаем, потому что давит одинаково со всех сторон."),
 ("fans",   "Под кузовом стоят вентиляторы. Они откачивают воздух из зазора, и там давление падает. Снизу давление прежнее, и оно прижимает машину. Маск говорит: до двух джи."),
 ("tanks",  "Теперь полёт. Ракетного топлива здесь нет. В машине два баллона: шестьсот литров сжатого воздуха, это около двухсот пятидесяти килограммов. И десять с+опел."),
 ("jets",   "Воздух вылетает в одну сторону, машину толкает в другую. Так же поворачивают космические аппараты."),
 ("end",    "Выпуск обещают в две тысячи двадцать восьмом году. Сел бы в такую? Пиши в комментариях. И отправь тому, кто любит машины."),
]
SUBTXT = {"hook": None}  # субтитры берём из озвучки, убирая «+»

_SYN = None
def tts(text):
    f = f"{TMP}/t_{hashlib.md5((text+str(VOICE)).encode()).hexdigest()}.wav"
    if os.path.exists(f): return wavfile.read(f)[1].astype(np.float32) / 32768
    global _SYN
    if _SYN is None:
        from vosk_tts import Model, Synth
        _SYN = Synth(Model(model_name="vosk-model-tts-ru-0.9-multi"))
    parts = [p for p in re.split(r"(?<=[.:!?])\s+", text) if p.strip()]; segs = []
    for k, p in enumerate(parts):
        a = np.asarray(_SYN.synth_audio(p, speaker_id=VOICE["speaker"], speech_rate=VOICE["rate"]), np.float32) / 32768
        segs.append(ss.resample_poly(a, SR, 22050).astype(np.float32))
        if k < len(parts) - 1: segs.append(np.zeros(int(SR * .5), np.float32))
    a = np.concatenate(segs); wavfile.write(f, SR, (a * 32767).astype(np.int16)); return a

def timeline():
    t0 = 0.0; sc = []
    for name, text in SCRIPT:
        a = tts(text); dur = LEAD + len(a) / SR + TAIL
        subs = [(t0 + LEAD + c0, t0 + LEAD + c1, ct) for c0, c1, ct in sync(text.replace("+", ""), a, SR)]
        nf = int(round(dur * FPS)); sc.append(dict(name=name, a=a, t0=t0, dur=nf / FPS, subs=subs, nf=nf)); t0 += nf / FPS
    return sc, t0

# ---------- примитивы (рисуем в 2x, затем уменьшаем) ----------
K = 2
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def rot(p, a): c, s = math.cos(a), math.sin(a); return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)

BODY = [(-222, -40), (-208, -92), (-92, -122), (-10, -132), (112, -82), (228, -64), (224, -38)]
GLASS = [(-84, -112), (-8, -122), (84, -86), (-78, -86)]
def car(d, x, y, a=0, s=1.0, xd=1, ys=1.0, glow=None, fans=False, tt=0):
    """Вид сбоку: центр колёсной базы на земле (x,y); a — поворот, xd=-1 — едет влево, ys=-1 — вверх колёсами (между — крен)."""
    def T(p):
        q = (p[0] * xd * s, p[1] * ys * s); q = rot(q, a); return ((x + q[0]) * K, (y + q[1]) * K)
    d.polygon([T(p) for p in BODY], fill=(236, 240, 246), outline=(255, 255, 255))
    d.polygon([T(p) for p in [(-222, -40), (-208, -62), (226, -52), (224, -38)]], fill=(150, 160, 175))
    d.polygon([T(p) for p in GLASS], fill=(18, 26, 48))
    for cx in (-132, 142):
        c = T((cx, -36)); r = 34 * s * K
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(14, 16, 24), outline=(90, 100, 120), width=3)
        r2 = 14 * s * K; d.ellipse([c[0] - r2, c[1] - r2, c[0] + r2, c[1] + r2], fill=(120, 130, 150))
    h = T((222, -56)); d.ellipse([h[0] - 7 * K, h[1] - 5 * K, h[0] + 7 * K, h[1] + 5 * K], fill=YEL)
    tl = T((-214, -70)); d.ellipse([tl[0] - 5 * K, tl[1] - 5 * K, tl[0] + 5 * K, tl[1] + 5 * K], fill=RED)
    if fans:                                                # вентиляторы на днище (голубое свечение + вращение)
        for cx in (-110, -40, 40, 110):
            c = T((cx, -42)); r = 22 * s * K
            d.ellipse([c[0] - r, c[1] - r * .5, c[0] + r, c[1] + r * .5], fill=(20, 60, 90), outline=CY)
            ang = tt * 22 + cx
            for b in range(3):
                th = ang + b * 2.094; dx = math.cos(th) * r * .9; dy = math.sin(th) * r * .45
                d.line([c[0], c[1], c[0] + dx, c[1] + dy], fill=CY, width=3)

def seed_pts(n, sd=1):
    r = random.Random(sd); return [(r.random(), r.random(), r.random()) for _ in range(n)]

def arrow(d, x0, y0, x1, y1, col=CY, w=6, hd=22):
    d.line([x0 * K, y0 * K, x1 * K, y1 * K], fill=col, width=w * K)
    a = math.atan2(y1 - y0, x1 - x0)
    for sg in (-1, 1):
        d.line([x1 * K, y1 * K, (x1 - hd * math.cos(a - sg * .5)) * K, (y1 - hd * math.sin(a - sg * .5)) * K], fill=col, width=w * K)

def tag(d, x, y, text, col=CY, fs=26, fill=(8, 22, 40), anchor="l"):
    f = F(fs * K, "Bold"); b = d.textbbox((0, 0), text, font=f); tw, th = b[2] - b[0], b[3] - b[1]
    pad = 12 * K; x0 = x * K if anchor == "l" else x * K - tw / 2 - pad
    d.rectangle([x0 - pad if anchor == "l" else x0, y * K - pad, x0 + tw + (pad if anchor == "l" else 2 * pad) + (pad if anchor == "l" else 0), y * K + th + pad], fill=fill, outline=col, width=2 * K)
    d.text((x0 + (0 if anchor == "l" else pad), y * K - b[1]), text, font=f, fill=col)

def big(d, x, y, text, col=YEL, fs=110, a=1.0):
    f = F(fs * K, "ExtraBold"); b = d.textbbox((0, 0), text, font=f)
    c = tuple(int(v * a) for v in col)
    d.text((x * K - (b[2] - b[0]) / 2, y * K), text, font=f, fill=c)

def ceiling(d, y, x0=0, x1=W):
    d.rectangle([x0 * K, (y - 70) * K, x1 * K, y * K], fill=(196, 202, 212))
    d.rectangle([x0 * K, (y - 6) * K, x1 * K, y * K], fill=(235, 238, 245))
    for px in range(60, W, 360): d.rectangle([px * K, y * K, (px + 14) * K, (y + 360) * K], fill=(80, 90, 105))

def ground(d, y):
    d.line([0, y * K, W * K, y * K], fill=(70, 84, 110), width=3 * K)

def dots(d, t, n, x0, y0, x1, y1, col=CY, sd=3, vx=0, vy=0, r=2.5):
    for (a, b, c) in seed_pts(n, sd):
        x = x0 + ((a * (x1 - x0) + vx * t) % (x1 - x0)); y = y0 + ((b * (y1 - y0) + vy * t) % (y1 - y0))
        rr = r * (.6 + c) * K; d.ellipse([x * K - rr, y * K - rr, x * K + rr, y * K + rr], fill=tuple(int(v * (.4 + .6 * c)) for v in col))

# ---------- сцены (t — секунды сцены, T — длительность) ----------
Y0, Y1 = 250, 1400                                           # зона сцены
def sc_hook(d, t, T):
    cy = 520; ceiling(d, cy)
    x = lerp(-250, 540, ease(t / 2.6)) + max(0, t - 2.6) * 40
    car(d, x, cy, 0, 1.05, 1, -1, fans=True, tt=t)
    dots(d, t, 90, 0, cy, W, cy + 520, vy=-40, sd=5)
    if t > .5: tag(d, 90, 880, "ВВЕРХ НОГАМИ", CY, 34)
    if t > 1.6: tag(d, 90, 960, "✓  НЕ ПАДАЕТ", GRN, 34, fill=(6, 40, 30))
    ground(d, 1250)

def sc_event(d, t, T):
    G = 1180; R = 420; cx0 = 640; ground(d, G)
    d.arc([(cx0 - R) * K, (G - 2 * R) * K, (cx0 + R) * K, G * K], 200, 90, fill=(190, 198, 210), width=14 * K)  # рампа: правая половина петли + верх
    t1, t2, t3 = 2.2, 6.2, T - 5.0
    if t < t1: x, y, a, xd, ys = lerp(-200, cx0, ease(t / t1)), G, 0, 1, 1
    elif t < t1 + 3.0:
        th = ease((t - t1) / 3.0) * math.pi; x, y, a, xd, ys = cx0 + R * math.sin(th), G - R + R * math.cos(th), th, 1, 1   # едет внутри петли; a — против часовой
        a = -th
    else:
        u = min(1.0, (t - t1 - 3.0) / 3.0); topx, topy = cx0, G - 2 * R
        x = topx - 520 * u; y = topy + (G - topy) * u * u; a = 0; xd = -1; ys = -math.cos(min(1, u * 1.15) * math.pi)
    # корректное положение внутри петли: поворачиваем машину колёсами к стенке
    car(d, x, y, a if t < t1 + 3.0 else 0, .78, xd, ys)
    if t > .6: tag(d, 60, 330, "15 ОКТЯБРЯ · ПОКАЗ", YEL, 30)
    if t1 + 1 < t < t1 + 3: tag(d, 60, 400, "ВВЕРХ КОЛЁСАМИ", CY, 30)
    if t1 + 3.0 < t < t1 + 6.0: tag(d, 60, 400, "ПЕРЕВОРОТ В ВОЗДУХЕ", CY, 30)
    if t > T - 3.2: big(d, W / 2, 560, "КАК?", WHITE, 220, ease((t - (T - 3.2)) / .5))

def sc_ceil(d, t, T):
    cy = 560; ceiling(d, cy); car(d, 540, cy, 0, 1.25, 1, -1, fans=True, tt=t)
    tag(d, 60, 330, "ПРИСАСЫВАЕТ?", RED, 36, fill=(40, 10, 14))
    if t > 1.4:
        d.line([60 * K, 335 * K, 520 * K, 380 * K], fill=RED, width=6 * K)
        tag(d, 60, 440, "НЕТ — ПРИСОСКИ ТУТ НЕТ", RED, 28, fill=(40, 10, 14))
    if t > 2.6:
        tag(d, 60, 1000, "ЕЁ ПРИЖИМАЕТ ВОЗДУХ", GRN, 40, fill=(6, 40, 30))
        for xx in (300, 540, 780): arrow(d, xx, 1180 - 8 * math.sin(t * 6 + xx), xx, 900, CY, 6)
    dots(d, t, 120, 0, cy + 200, W, 1400, vy=-30, sd=7)

def sc_tons(d, t, T):
    cx, cy = 540, 760; s = 300
    d.rectangle([(cx - s / 2) * K, (cy - s / 2) * K, (cx + s / 2) * K, (cy + s / 2) * K], outline=CY, width=4 * K, fill=(10, 30, 50))
    tag(d, cx - 60, cy - 18, "1 м²", CY, 36)
    p = ease(t / 1.2)
    for ang in range(0, 360, 45):
        a = math.radians(ang); r1 = 420 - 28 * math.sin(t * 5 + ang); r0 = 190
        arrow(d, cx + r1 * math.cos(a) * p, cy + r1 * math.sin(a) * p, cx + r0 * math.cos(a), cy + r0 * math.sin(a), CY, 6)
    big(d, cx, 270, "≈ 10 ТОНН", YEL, 120, ease(t / .6))
    if t > T - 4.6: tag(d, 540, 1220, "ОДИНАКОВО СО ВСЕХ СТОРОН", CY, 32, anchor="c")
    dots(d, t, 80, 0, 300, W, 1250, sd=2, vx=20, vy=10)

def sc_fans(d, t, T):
    cy = 520; ceiling(d, cy); car(d, 540, cy, 0, 1.3, 1, -1, fans=True, tt=t)
    for k, xx in enumerate((300, 400, 500, 600, 700, 780)):                       # воздух из зазора втягивается в вентиляторы
        yy = cy + 8 + ((t * 40 + k * 15) % 30); d.ellipse([xx * K - 4 * K, yy * K - 4 * K, xx * K + 4 * K, yy * K + 4 * K], fill=CY)
    tag(d, 60, 330, "ЗАЗОР · ДАВЛЕНИЕ МЕНЬШЕ", GRN, 28, fill=(6, 40, 30))
    d.line([420 * K, 375 * K, 440 * K, (cy + 14) * K], fill=GRN, width=3 * K)
    for xx in (250, 400, 540, 680, 830):
        arrow(d, xx, 1250 - 10 * math.sin(t * 5 + xx), xx, 880, CY, 8)
    tag(d, 540, 1290, "ВОЗДУХ СНИЗУ ЖМЁТ СИЛЬНЕЕ", CY, 30, anchor="c")
    if t > T - 4: big(d, 540, 1040 - 380, "до 2 g", YEL, 110, ease((t - (T - 4)) / .5))
    dots(d, t, 100, 0, cy + 300, W, 1250, sd=11, vy=-25)

def sc_tanks(d, t, T):
    cy = 780; car(d, 540, cy + 120, 0, 1.0, 1, 1)
    p = ease(t / .8)
    for k, xx in enumerate((380, 700)):                                                   # два баллона
        d.rounded_rectangle([(xx - 110) * K, (cy - 40) * K, (xx + 110) * K, (cy + 20) * K], 28 * K, fill=(214, 150, 40), outline=(255, 210, 120), width=3 * K)
    for k in range(10):                                                                   # 10 сопел по периметру
        xx = 180 + k * 80; vis = t > 2.0 + k * .18
        if vis: d.ellipse([(xx - 9) * K, (cy + 250) * K, (xx + 9) * K, (cy + 268) * K], fill=CY)
    tag(d, 60, 300, "РАКЕТНОГО ТОПЛИВА НЕТ", RED, 34, fill=(40, 10, 14))
    if t > 3.0: tag(d, 60, 1060, "2 БАЛЛОНА · 600 Л · ≈ 250 КГ ВОЗДУХА", YEL, 30)
    if t > 6.0: tag(d, 60, 1140, "10 СОПЕЛ", CY, 34)

def sc_jets(d, t, T):
    cy = 640
    # слева: машина-сопло; справа: космический аппарат
    ground(d, 1250)
    x = lerp(320, 560, ease(t / (T - 1))); car(d, x, 560, 0, .9, 1, 1)
    for k in range(16):
        u = ((t * 2.2 + k / 16) % 1); d.ellipse([(x - 230 - 160 * u) * K, (500 + 40 * math.sin(k * 3)) * K, (x - 215 - 160 * u) * K, (515 + 40 * math.sin(k * 3)) * K], fill=tuple(int(v * (1 - u)) for v in WHITE))
    arrow(d, x - 70, 880, x - 340, 880, WHITE, 8); tag(d, x - 340, 910, "ВОЗДУХ ←", WHITE, 30)
    arrow(d, x + 40, 960, x + 300, 960, CY, 8); tag(d, x + 40, 990, "МАШИНА →", CY, 30)
    if t > 4.5:
        bx, by = 540, 1130; a = (t - 4.5) * .8
        pts = [rot((px, py), a) for px, py in [(-60, -60), (60, -60), (60, 60), (-60, 60)]]
        d.polygon([((bx + px) * K, (by + py) * K) for px, py in pts], fill=(214, 150, 40), outline=(255, 210, 120))
        tag(d, 60, 1330, "ТАК ПОВОРАЧИВАЮТ КОСМИЧЕСКИЕ АППАРАТЫ", YEL, 26)

def sc_end(d, t, T):
    cx, cy = 540, 600
    d.rounded_rectangle([(cx - 190) * K, (cy - 210) * K, (cx + 190) * K, (cy + 130) * K], 30 * K, fill=(20, 28, 48), outline=YEL, width=5 * K)
    d.rectangle([(cx - 190) * K, (cy - 210) * K, (cx + 190) * K, (cy - 140) * K], fill=YEL)
    big(d, cx, cy - 120, "2028", WHITE, 170, ease(t / .6)) if False else None
    f = F(60 * K, "ExtraBold"); d.text((cx * K - 100 * K, (cy - 205) * K), "ВЫПУСК", font=f, fill=(20, 20, 20))
    big(d, cx, cy - 120, "2028", WHITE, 170, ease(t / .6))
    car(d, 540, 1000, 0, .9, 1, 1)
    if t > 5.0:
        tag(d, 280, 1130, "СЕЛ БЫ?", WHITE, 54, fill=(10, 20, 36));
        tag(d, 330, 1290, "ДА", GRN, 44, fill=(6, 40, 30)); tag(d, 560, 1290, "НЕТ", RED, 44, fill=(40, 10, 14))

SCENES = dict(hook=sc_hook, event=sc_event, ceil=sc_ceil, tons=sc_tons, fans=sc_fans, tanks=sc_tanks, jets=sc_jets, end=sc_end)

# ---------- кадр ----------
_BG = None
def background():
    global _BG
    if _BG is None:
        y = np.linspace(0, 1, H)[:, None, None]; base = np.array(BG, np.float32)[None, None, :]
        img = np.broadcast_to(base * (1 + .8 * y), (H, W, 3)).copy()
        _BG = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return _BG.copy()

def frame(i, SC, DUR):
    t = i / FPS; sc = next(s for s in SC if s["t0"] <= t < s["t0"] + s["dur"] + 1e-6) if t < DUR else SC[-1]
    lt = t - sc["t0"]
    img = background()
    lay = Image.new("RGBA", (W * K, (Y1 + 120) * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    SCENES[sc["name"]](d, lt, sc["dur"])
    lay = lay.resize((W, Y1 + 120), Image.LANCZOS); img.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(img)
    # шапка: HUD
    d.text((54, 70), "ФИЗИКА · ПРЕЗЕНТАЦИЯ 15.10.2026", font=F(22, "Medium"), fill=(110, 140, 170))
    d.rectangle([54, 130, W - 54, 134], fill=(20, 40, 64)); d.rectangle([54, 130, 54 + (W - 108) * min(1, t / DUR), 134], fill=CY)
    # субтитры (мягкие, пословные фразы)
    cur = next((s for s in sc["subs"] if s[0] <= t <= s[1]), None)
    if cur:
        f = F(46, "Bold"); words = cur[2]; ws = words.split(); lines = [words]
        if d.textlength(words, font=f) > W - 120:
            k = len(ws) // 2; lines = [" ".join(ws[:k]), " ".join(ws[k:])]
        for li, ln in enumerate(lines):
            x = (W - d.textlength(ln, font=f)) / 2; yy = 1480 + li * 62
            d.text((x + 3, yy + 3), ln, font=f, fill=(0, 0, 0)); d.text((x, yy), ln, font=f, fill=WHITE)
    return img

def _job(args): i, SC, DUR = args; return i, frame(i, SC, DUR)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/expl/out.mp4"; prev = sys.argv[2] if len(sys.argv) > 2 else ""
    SC, DUR = timeline(); NF = int(round(DUR * FPS)); print("длина", round(DUR, 1), "с, кадров", NF, [round(s["dur"], 1) for s in SC], flush=True)
    if prev:
        for t in prev.split(","): frame(int(float(t) * FPS), SC, DUR).save(f"{TMP}/pv_{t}.png"); print("pv", t)
        sys.exit()
    # звук
    track = np.zeros(int(DUR * SR) + SR, np.float32)
    for s in SC: i0 = int((s["t0"] + LEAD) * SR); track[i0:i0 + len(s["a"])] += s["a"]
    track = track / max(np.abs(track).max(), 1e-6) * .85
    mp = os.path.join(HERE, "..", "music", "suk_meditation.mp3")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", "4", "-t", str(DUR + 1), "-i", mp, "-ar", str(SR), "-ac", "1", f"{TMP}/_m.wav"], check=True)
    m = wavfile.read(f"{TMP}/_m.wav")[1].astype(np.float32) / 32768; m = np.pad(m, (0, max(0, len(track) - len(m))))[:len(track)]
    fade = np.minimum(1, np.minimum(np.arange(len(track)) / (SR * 1.5), (len(track) - np.arange(len(track))) / (SR * 2.5)))
    track = track + m / max(np.abs(m).max(), 1e-6) * .2 * fade
    wavfile.write(f"{TMP}/_a.wav", SR, (np.clip(track / np.abs(track).max(), -1, 1) * .9 * 32767).astype(np.int16))
    # кадры
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{TMP}/_a.wav",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for n, (i, im) in enumerate(pool.imap(_job, [(i, SC, DUR) for i in range(NF)], chunksize=4)):
            p.stdin.write(im.convert("RGB").tobytes())
            if n % 120 == 0: print("кадр", n, "/", NF, flush=True)
    p.stdin.close(); p.wait(); print("готово", out)
