"""Reels: «Макиавелли. Государь — 5 мыслей». Перевод отрывков — собственный, с итальянского оригинала (1513, общественное достояние).
Озвучка — Silero TTS (офлайн), сцены — Pillow, сборка — ffmpeg."""
import math, os, random, subprocess, sys
import numpy as np, scipy.io.wavfile as wavfile, torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_scenes_demo import glow, vgrad, ease, lerp, figure, walk_pose, bird, W, H, FPS, CX0, CY0, CW, CH, GY, SKIN

OUT = sys.argv[1] if len(sys.argv) > 1 else "machiavelli.mp4"
SILERO = os.environ.get("SILERO_MODEL", "v4_ru.pt")
WORK = "machiavelli"; os.makedirs(WORK, exist_ok=True)
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
def font(w, s): return ImageFont.truetype(F.format(w), s)
GOLD, BG, WINE = (226, 186, 110), (20, 12, 16), (120, 30, 40)
random.seed(11)

# (текст для озвучки с ударениями «+», текст на экране, метка)
LINES = [
    ("Никк+оло Макиав+елли. «Госуд+арь», тысяча пятьсот тринадцатый год. Пять мыслей, которые работают до сих пор.",
     "Никколо Макиавелли\n«Государь», 1513", "5 мыслей, которые работают до сих пор"),
    ("Первая. Если приходится выбирать, гораздо надёжнее внушать страх, чем любовь. Но ненависти правитель должен избегать.",
     "«Если приходится выбирать,\nгораздо надёжнее внушать страх,\nчем любовь»", "1 / 5"),
    ("Вторая. Правитель должен быть лисой, чтобы распознать капканы, и львом, чтобы отпугнуть волков.",
     "«Будь лисой, чтобы распознать\nкапканы, и львом, чтобы\nотпугнуть волков»", "2 / 5"),
    ("Третья. Каждый видит, каким ты кажешься. Но мало кто знает, каков ты на самом деле.",
     "«Каждый видит, каким ты кажешься,\nно мало кто знает,\nкаков ты на самом деле»", "3 / 5"),
    ("Четвёртая. Судьба распоряжается половиной наших дел. Но другую половину она оставляет нам самим.",
     "«Судьба распоряжается половиной\nнаших дел, но другую половину\nоставляет нам самим»", "4 / 5"),
    ("Пятая. Об уме правителя прежде всего судят по людям, которых он держит рядом.",
     "«Об уме правителя судят\nпо людям, которых он\nдержит рядом»", "5 / 5"),
    ("Какая мысль вам ближе? Напишите в комментариях. И сохраните, чтобы не забыть.",
     "Какая мысль вам ближе?", "Напишите в комментариях · Сохраните"),
]
LEAD, TAIL = 0.5, 0.9

# ---------------- озвучка ----------------
model = torch.package.PackageImporter(SILERO).load_pickle("tts_models", "model"); model.to("cpu")
SR = 48000
voice, STARTS, DURS, t0 = [], [], [], 0.0
for i, (say, _, _) in enumerate(LINES):
    a = model.apply_tts(text=say, speaker="aidar", sample_rate=SR, put_accent=True, put_yo=True).numpy()
    dur = LEAD + len(a) / SR + TAIL
    STARTS.append(t0); DURS.append(dur); voice.append((t0 + LEAD, a)); t0 += dur
DUR = t0
track = np.zeros(int(DUR * SR) + SR)
for st, a in voice: s0 = int(st * SR); track[s0:s0 + len(a)] += a
wavfile.write(f"{WORK}/voice.wav", SR, (track / np.abs(track).max() * 0.9 * 32767).astype(np.int16))
print(f"озвучка: {DUR:.1f} с, сцены: " + ", ".join(f"{d:.1f}" for d in DURS))

# ---------------- музыка: тёмный эмбиент Dm–B♭–F–A ----------------
N = len(track); tt = np.arange(N) / SR; mus = np.zeros(N)
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 53, 57, 60], [45, 52, 57, 61]]
bar = 4.0
for i in range(int(DUR / bar) + 1):
    s0, s1 = int(i * bar * SR), min(int((i + 1) * bar * SR + SR), N)
    if s0 >= N: break
    seg = tt[s0:s1] - i * bar; env = np.minimum(seg / 1.2, 1) * np.clip((bar + 1 - seg) / 1.5, 0, 1)
    mus[s0:s1] += env * sum(0.05 * np.sin(2 * np.pi * note(m) * seg) + 0.015 * np.sin(2 * np.pi * note(m) * 2.005 * seg) for m in prog[i % 4])
    for k in range(8):                                          # тихий перебор, как лютня
        a0 = s0 + int(k * 0.5 * SR); a1 = min(a0 + int(1.2 * SR), N)
        if a0 >= N: break
        sg = tt[a0:a1] - tt[a0]; m = prog[i % 4][[1, 2, 3, 2][k % 4]] + 12
        mus[a0:a1] += 0.035 * np.exp(-sg * 4) * (np.sin(2 * np.pi * note(m) * sg) + 0.3 * np.sin(4 * np.pi * note(m) * sg))
mus *= np.minimum(np.minimum(tt / 1.5, 1), np.clip((DUR - tt) / 2.0, 0, 1))
wavfile.write(f"{WORK}/music.wav", SR, (mus / np.abs(mus).max() * 0.8 * 32767).astype(np.int16))

# ---------------- сцены ----------------
def crown(d, x, y, s=1.0):
    d.polygon([(x - 40 * s, y), (x - 40 * s, y - 34 * s), (x - 20 * s, y - 14 * s), (x, y - 44 * s), (x + 20 * s, y - 14 * s), (x + 40 * s, y - 34 * s), (x + 40 * s, y)], fill=GOLD)
    d.ellipse((x - 6 * s, y - 50 * s, x + 6 * s, y - 38 * s), fill=(220, 60, 70))

# 0. Кабинет: перо пишет на пергаменте, свеча
S0 = vgrad(CW, CH, (70, 34, 40), (34, 16, 22)); _d = ImageDraw.Draw(S0)
_d.rectangle((0, 640, CW, CH), fill=(92, 52, 36)); _d.rectangle((0, 632, CW, 646), fill=(120, 72, 48))
for i, (w_, c) in enumerate([(300, (110, 40, 50)), (280, (60, 70, 110)), (310, (90, 80, 40))]):
    _d.rounded_rectangle((560, 600 - i * 46, 560 + w_, 640 - i * 46), 6, fill=c)
_d.polygon([(110, 700), (520, 680), (560, 960), (90, 990)], fill=(236, 220, 180))
for k in range(6): _d.line(((140, 740 + k * 38), (480, 728 + k * 38)), fill=(190, 170, 130), width=3)
def scene0(t, D):
    im = S0.copy(); d = ImageDraw.Draw(im)
    fl = math.sin(t * 13) * 4 + math.sin(t * 7) * 3
    im.alpha_composite(glow((420, 420), (255, 180, 90), 110, int(120 + fl * 4)), (620, 230))
    d.rectangle((815, 420, 845, 520), fill=(240, 230, 210)); d.ellipse((816 + fl / 2, 360, 844 + fl / 2, 422), fill=(255, 200, 90)); d.ellipse((824 + fl / 2, 384, 836 + fl / 2, 418), fill=(255, 250, 220))
    prog_ = min(t / (D * 0.8), 1); row = int(prog_ * 4); frac = (prog_ * 4) % 1   # строки текста появляются
    for r in range(row + 1):
        L = 300 if r < row else 300 * frac
        pts = [(150 + x, 742 + r * 38 - 12 * (r * 0) + 6 * math.sin(x / 9) - x * 0.035) for x in range(0, int(L), 6)]
        if len(pts) > 1: d.line(pts, fill=(60, 40, 40), width=3)
    qx = 150 + (300 * frac if row < 4 else 300); qy = 742 + min(row, 3) * 38 - qx * 0.035 + 6 * math.sin(t * 30)
    d.line(((qx, qy), (qx + 140, qy - 230)), fill=(250, 250, 250), width=6)                  # перо
    d.polygon([(qx + 60, qy - 90), (qx + 150, qy - 250), (qx + 175, qy - 225), (qx + 90, qy - 70)], fill=(245, 240, 235))
    return im

# 1. Тронный зал: правитель на троне, придворные кланяются, факелы
S1 = vgrad(CW, CH, (60, 20, 30), (30, 10, 16)); _d = ImageDraw.Draw(S1)
_d.rectangle((0, GY - 40, CW, CH), fill=(50, 22, 26))
for px in (80, 780): _d.rectangle((px, 60, px + 80, GY - 40), fill=(80, 36, 44))
_d.polygon([(370, GY - 40), (570, GY - 40), (600, CH), (340, CH)], fill=(150, 30, 40))     # ковровая дорожка
_d.rounded_rectangle((380, 180, 560, 560), 60, fill=(140, 100, 40)); _d.rounded_rectangle((400, 200, 540, 540), 50, fill=(110, 30, 40))
def scene1(t, D):
    im = S1.copy(); d = ImageDraw.Draw(im)
    for px in (120, 820):
        fl = math.sin(t * 11 + px) * 5
        im.alpha_composite(glow((260, 260), (255, 170, 80), 70, 120), (px - 130, 160))
        d.ellipse((px - 18 + fl / 2, 240, px + 18 + fl / 2, 300), fill=(255, 190, 80))
    cx, base = 470, 600                                                                      # правитель
    d.rectangle((cx - 80, base - 40, cx + 80, base + 60), fill=(90, 20, 40)); d.polygon([(cx - 90, base - 10), (cx + 90, base - 10), (cx + 65, base - 220), (cx - 65, base - 220)], fill=(130, 30, 60))
    d.ellipse((cx - 50, base - 330, cx + 50, base - 230), fill=SKIN); crown(d, cx, base - 312)
    d.line(((cx + 85, base - 40), (cx + 120, base - 250)), fill=GOLD, width=8); d.ellipse((cx + 108, base - 270, cx + 134, base - 244), fill=GOLD)
    for i, x in enumerate([120, 250, 690, 820]):                                              # придворные кланяются
        b = (math.sin(t * 1.6 + i * 0.8) + 1) / 2
        pose = dict(torso=lerp(5, 70, ease(b)), th1=0, kn1=0, th2=0, kn2=0, ua1=lerp(6, -30, b), el1=10, ua2=lerp(-4, -26, b), el2=10)
        f = 1 if x < 470 else -1
        figure(d, x, GY + 100, pose, s=0.5, f=f, robe=(70, 50, 90), robe2=(52, 36, 70), hat=(40, 30, 50), beard=None)
    return im

# 2. Лиса и лев: лиса обходит капканы, лев рычит, волки отступают
S2 = vgrad(CW, CH, (24, 34, 54), (14, 22, 34)); _d = ImageDraw.Draw(S2)
for x in range(-40, CW, 130):
    h = random.randint(260, 420); _d.polygon([(x, GY), (x + 70, GY - h), (x + 140, GY)], fill=(20, 44, 46))
_d.rectangle((0, GY, CW, CH), fill=(30, 46, 40)); _d.polygon([(640, GY), (700, 640), (900, 620), (CW, GY)], fill=(70, 70, 80))
TRAPS = [250, 450]
def fox(d, x, y, t):
    st = math.sin(t * 12) * 12
    for dx, ph in [(-40, 0), (30, math.pi)]: d.line(((x + dx, y - 40), (x + dx + st * math.cos(ph), y)), fill=(170, 70, 30), width=10)
    d.ellipse((x - 70, y - 90, x + 60, y - 30), fill=(230, 110, 40))
    d.polygon([(x - 60, y - 70), (x - 170, y - 110 + st), (x - 150, y - 60)], fill=(230, 110, 40)); d.polygon([(x - 150, y - 100 + st), (x - 175, y - 112 + st), (x - 160, y - 80)], fill=(250, 245, 240))
    d.polygon([(x + 40, y - 95), (x + 110, y - 70), (x + 40, y - 45)], fill=(235, 120, 50)); d.polygon([(x + 40, y - 95), (x + 52, y - 130), (x + 66, y - 88)], fill=(200, 90, 30))
    d.ellipse((x + 62, y - 82, x + 70, y - 74), fill=(20, 20, 20))
def lion(d, x, y, t):
    roar = (math.sin(t * 2.4) + 1) / 2
    for k in range(14):
        a = k / 14 * 2 * math.pi; r = 95 + 12 * roar
        d.polygon([(x - 40 + math.cos(a) * 50, y - 170 + math.sin(a) * 50), (x - 40 + math.cos(a + 0.25) * r, y - 170 + math.sin(a + 0.25) * r), (x - 40 + math.cos(a + 0.5) * 50, y - 170 + math.sin(a + 0.5) * 50)], fill=(170, 80, 30))
    d.ellipse((x - 20, y - 150, x + 170, y - 40), fill=(220, 170, 90))
    for dx in (0, 40, 120, 150): d.rectangle((x + dx, y - 70, x + dx + 22, y), fill=(210, 160, 80))
    d.ellipse((x - 105, y - 235, x + 25, y - 105), fill=(230, 180, 100)); d.ellipse((x - 92, y - 190, x - 80, y - 178), fill=(30, 20, 20))
    d.chord((x - 110, y - 170 - 10 * roar, x - 50, y - 120 + 10 * roar), 90, 270, fill=(80, 20, 20))
    for k in range(3):                                                                       # волны рыка
        r = 40 + ((t * 120 + k * 50) % 150)
        d.arc((x - 100 - r, y - 160 - r, x - 100 + r, y - 160 + r), 140, 220, fill=(255, 220, 160, int(200 * (1 - r / 190))), width=5)
def wolf(d, x, y, t, k):
    st = math.sin(t * 10 + k) * 10
    for dx in (-35, 30): d.line(((x + dx, y - 40), (x + dx + st, y)), fill=(90, 96, 110), width=10)
    d.ellipse((x - 70, y - 90, x + 60, y - 30), fill=(120, 126, 140)); d.polygon([(x - 60, y - 90), (x - 120, y - 90), (x - 70, y - 50)], fill=(130, 136, 150))
    d.polygon([(x - 110, y - 95), (x - 100, y - 125), (x - 85, y - 92)], fill=(110, 116, 130))
def scene2(t, D):
    im = S2.copy(); d = ImageDraw.Draw(im)
    for tx in TRAPS:
        d.rectangle((tx - 50, GY + 30, tx + 50, GY + 38), fill=(140, 140, 150))
        for k in range(6): d.polygon([(tx - 45 + k * 18, GY + 30), (tx - 36 + k * 18, GY + 5), (tx - 27 + k * 18, GY + 30)], fill=(170, 170, 180))
    fx = 60 + t / D * 520; hop = sum(max(0, 80 * math.sin(math.pi * (fx - (tx - 90)) / 180)) for tx in TRAPS if tx - 90 < fx < tx + 90)
    fox(d, fx, GY + 30 - hop, t)                                                             # лиса перепрыгивает капканы
    lion(d, 770, 640, t)
    for k, x0 in enumerate([300, 170]):
        wolf(d, x0 - t * 28, GY + 120 + k * 30, t, k)
    return im

# 3. Тень: обычный человек и тень короля на стене, дрожит свеча
S3 = vgrad(CW, CH, (70, 50, 46), (44, 30, 30)); _d = ImageDraw.Draw(S3)
_d.rectangle((0, GY, CW, CH), fill=(56, 36, 32))
def scene3(t, D):
    im = S3.copy(); d = ImageDraw.Draw(im)
    fl = math.sin(t * 9) * 6 + math.sin(t * 4.3) * 5; sw = math.sin(t * 1.3) * 10
    im.alpha_composite(glow((520, 520), (255, 190, 100), 130, 120), (int(-80 + fl), 380))
    sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)                  # большая тень короля
    ox = 520 + sw + fl
    sd.polygon([(ox - 170, GY), (ox + 170, GY), (ox + 120, 360), (ox - 120, 360)], fill=(20, 12, 14, 170))
    sd.ellipse((ox - 85, 180, ox + 85, 350), fill=(20, 12, 14, 170)); crown(sd, ox, 210, 2.2)
    sd.line(((ox + 160, 700), (ox + 230, 200)), fill=(20, 12, 14, 170), width=18)
    sh = sh.filter(ImageFilter.GaussianBlur(4)); sh.putalpha(sh.getchannel("A").point(lambda v: min(v, 170)))
    im.alpha_composite(sh)
    d.rectangle((140, GY - 70, 170, GY + 10), fill=(240, 230, 210)); d.ellipse((141 + fl / 3, GY - 120, 169 + fl / 3, GY - 66), fill=(255, 200, 90))
    b = math.sin(t * 1.8) * 3
    figure(d, 300, GY + 60, dict(torso=b, th1=0, kn1=0, th2=0, kn2=0, ua1=8, el1=10, ua2=-6, el2=10), s=0.75, f=1, robe=(110, 100, 90), robe2=(86, 78, 70), hat=(80, 70, 60), beard=None)
    return im

# 4. Колесо фортуны над рекой, лодка качается
S4 = vgrad(CW, CH, (40, 46, 80), (90, 70, 90)); _d = ImageDraw.Draw(S4)
_d.rectangle((0, 760, CW, CH), fill=(40, 70, 110))
CL4 = [(random.uniform(0, CW), random.uniform(80, 300), random.uniform(10, 25)) for _ in range(4)]
def scene4(t, D):
    im = S4.copy(); d = ImageDraw.Draw(im)
    for cx, cy, sp in CL4:
        x = (cx + t * sp) % (CW + 300) - 150
        for dx, r in [(0, 46), (50, 58), (105, 44)]: d.ellipse((x + dx - r, cy - r, x + dx + r, cy + r), fill=(120, 110, 150))
    wx, wy, R = 470, 420, 260; a0 = t * 0.5                                                  # колесо вращается
    d.line(((wx - 160, 760), (wx, wy)), fill=(90, 60, 40), width=18); d.line(((wx + 160, 760), (wx, wy)), fill=(90, 60, 40), width=18)
    d.ellipse((wx - R, wy - R, wx + R, wy + R), outline=GOLD, width=16)
    for k in range(8):
        a = a0 + k * math.pi / 4; ex, ey = wx + math.cos(a) * R, wy + math.sin(a) * R
        d.line(((wx, wy), (ex, ey)), fill=(200, 160, 90), width=8)
        if k % 2 == 0: d.ellipse((ex - 30, ey - 30, ex + 30, ey + 30), fill=(130, 40, 50)); crown(d, ex, ey + 4, 0.55) if k == 0 else d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), fill=SKIN)
    d.ellipse((wx - 40, wy - 40, wx + 40, wy + 40), fill=GOLD)
    for k in range(5):                                                                       # волны
        y = 800 + k * 50; pts = [(x, y + 10 * math.sin(x / 50 + t * 2 + k)) for x in range(0, CW + 10, 10)]
        d.line(pts, fill=(90, 130, 180), width=4)
    bx = 150 + t * 30; by = 860 + 12 * math.sin(t * 2); tilt = 8 * math.sin(t * 2.3)       # лодка
    d.polygon([(bx - 110, by - tilt), (bx + 110, by + tilt), (bx + 80, by + 50 + tilt), (bx - 80, by + 50 - tilt)], fill=(110, 60, 40))
    d.line(((bx, by), (bx, by - 170)), fill=(80, 50, 30), width=7); d.polygon([(bx + 4, by - 165), (bx + 90, by - 30), (bx + 4, by - 30)], fill=(240, 230, 210))
    return im

# 5. Шахматы: фигуры ходят, король в центре
S5 = vgrad(CW, CH, (30, 22, 34), (16, 12, 20)); _d = ImageDraw.Draw(S5)
BX, BY, CS = 110, 300, 90
for r in range(8):
    for c in range(8): _d.rectangle((BX + c * CS, BY + r * CS, BX + (c + 1) * CS, BY + (r + 1) * CS), fill=(230, 210, 170) if (r + c) % 2 == 0 else (110, 70, 50))
_d.rectangle((BX - 12, BY - 12, BX + 8 * CS + 12, BY + 8 * CS + 12), outline=(70, 44, 30), width=12)
def piece(d, c, r, kind, col):
    x, y = BX + c * CS + CS / 2, BY + r * CS + CS / 2
    d.ellipse((x - 30, y + 10, x + 30, y + 34), fill=col)
    if kind == "p": d.polygon([(x - 20, y + 16), (x + 20, y + 16), (x + 8, y - 10), (x - 8, y - 10)], fill=col); d.ellipse((x - 16, y - 36, x + 16, y - 4), fill=col)
    elif kind == "k":
        d.polygon([(x - 26, y + 16), (x + 26, y + 16), (x + 14, y - 30), (x - 14, y - 30)], fill=col); crown(d, x, y - 28, 0.6)
    else: d.polygon([(x - 24, y + 16), (x + 24, y + 16), (x + 18, y - 20), (x + 4, y - 44), (x - 22, y - 20)], fill=col)
MOVES = [((3, 7), (3, 5)), ((1, 7), (2, 5)), ((5, 7), (4, 5)), ((6, 6), (6, 4))]
def scene5(t, D):
    im = S5.copy(); d = ImageDraw.Draw(im)
    for c, r in [(0, 1), (2, 1), (5, 1), (7, 1)]: piece(d, c, r, "p", (40, 34, 40))
    piece(d, 4, 0, "k", (40, 34, 40))
    seg = D / (len(MOVES) + 1)
    for k, ((c0, r0), (c1, r1)) in enumerate(MOVES):
        u = ease((t - (k + 0.5) * seg) / 0.7); kind = "n" if k == 1 else ("p" if k != 0 else "p")
        piece(d, lerp(c0, c1, u), lerp(r0, r1, u) - 0.3 * math.sin(math.pi * u), kind, (245, 240, 230))
    piece(d, 4, 7, "k", (245, 240, 230))
    im.alpha_composite(glow((300, 300), (255, 220, 140), 70, int(60 + 30 * math.sin(t * 2))), (BX + 4 * CS + CS // 2 - 150, BY + 7 * CS + CS // 2 - 150))
    return im

SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene0]

# ---------------- страница ----------------
page = Image.new("RGBA", (W, H), BG + (255,)); pd = ImageDraw.Draw(page)
for (x, y, r) in [(-200, 300, 700), (1200, 1500, 800)]: page.alpha_composite(glow((r, r), (110, 40, 50), r // 4, 60), (x - r // 2 + 200, y - r // 2))
title = "Макиавелли · «Государь»"; tw = pd.textbbox((0, 0), title, font=font("Bold", 52))[2]
pd.text(((W - tw) // 2, 205), title, font=font("Bold", 52), fill=(245, 230, 200))
pd.text((W // 2, 290), "мысли, которым 500 лет", font=font("Medium", 32), fill=(200, 160, 120), anchor="mm")
pd.text((W // 2, 1840), "перевод с итальянского оригинала", font=font("Medium", 28), fill=(140, 110, 100), anchor="mm")
shadow = Image.new("RGBA", (CW + 80, CH + 80), (0, 0, 0, 0)); ImageDraw.Draw(shadow).rounded_rectangle((40, 50, CW + 40, CH + 50), 46, fill=(0, 0, 0, 160))
page.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)), (CX0 - 40, CY0 - 40))
MASK = Image.new("L", (CW, CH), 0); ImageDraw.Draw(MASK).rounded_rectangle((0, 0, CW - 1, CH - 1), 46, fill=255)
XF = 0.5

def fit(d, text, w, size, maxw):
    while size > 30 and d.multiline_textbbox((0, 0), text, font=font(w, size), spacing=14)[2] > maxw: size -= 2
    return font(w, size)

def frame(t):
    i = max(k for k in range(len(STARTS)) if STARTS[k] <= t) if t >= 0 else 0
    lt, D = t - STARTS[i], DURS[i]
    sc = SCENES[i](lt, D)
    if lt < XF and i > 0: sc = Image.blend(SCENES[i - 1](lt + DURS[i - 1], DURS[i - 1]), sc, ease(lt / XF))
    img = page.copy(); img.paste(sc.convert("RGB"), (CX0, CY0), MASK)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((CX0, CY0, CX0 + CW - 1, CY0 + CH - 1), 46, outline=(150, 110, 70), width=3)
    py = CY0 + CH + 40
    d.rounded_rectangle((CX0 + 20, py, CX0 + CW - 20, py + 8), 4, fill=(70, 50, 50))
    d.rounded_rectangle((CX0 + 20, py, CX0 + 20 + int((CW - 40) * t / DUR), py + 8), 4, fill=GOLD)
    al = min(ease((lt - 0.2) / 0.5), ease((D - lt - 0.1) / 0.4))
    if al > 0:
        lay = Image.new("RGBA", (W, 380), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        _, text, tag = LINES[i]
        tf = fit(ld, text, "SemiBold", 52, 960)
        ld.multiline_text((W // 2 + 3, 26), text, font=tf, fill=(0, 0, 0, int(150 * al)), anchor="ma", align="center", spacing=14)
        ld.multiline_text((W // 2, 22), text, font=tf, fill=(255, 250, 240, int(255 * al)), anchor="ma", align="center", spacing=14)
        tb = ld.multiline_textbbox((W // 2, 22), text, font=tf, anchor="ma", align="center", spacing=14)[3]
        ld.text((W // 2, tb + 34), tag, font=font("Medium", 34), fill=GOLD + (int(255 * al),), anchor="ma")
        img = img.convert("RGBA"); img.alpha_composite(lay, (0, py + 36 + int((1 - al) * 14)))
    return img.convert("RGB")

if len(sys.argv) > 2:
    for k, x in enumerate(map(float, sys.argv[2].split(","))): frame(x).resize((360, 640)).save(f"{WORK}/pv_{k}.png")
    sys.exit()
p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", f"{WORK}/video.mp4"], stdin=subprocess.PIPE)
for n in range(int(DUR * FPS)): p.stdin.write(frame(n / FPS).tobytes())
p.stdin.close(); p.wait()
fc = ("[1:a]highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=100:makeup=2,asplit[v][vk];"
      "[2:a]volume=0.32[m];[m][vk]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=500[md];"
      "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{WORK}/video.mp4", "-i", f"{WORK}/voice.wav", "-i", f"{WORK}/music.wav",
                "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.2f}", "-movflags", "+faststart", OUT], check=True)
print("done", OUT, f"{DUR:.1f} c")
