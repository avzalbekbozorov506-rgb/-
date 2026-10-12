"""Демо «лекция в анимированной карточке»: 5 сцен по 5 с, движущиеся люди и предметы, 9:16, без звука."""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SCENE_LEN, XF = 5.0, 0.6                       # длина сцены и перехода
OUT = sys.argv[1] if len(sys.argv) > 1 else "scenes_demo.mp4"
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
BG = (13, 16, 38)
CX0, CY0, CW, CH = 70, 360, 940, 1040
GY = 820                                       # линия земли внутри карточки
SKIN, CAP, BEARD = (222, 176, 144), (246, 246, 250), (70, 60, 70)
random.seed(5)

def font(w, s): return ImageFont.truetype(F.format(w), s)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def glow(size, color, radius, alpha):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((radius, radius, size[0] - radius, size[1] - radius), fill=color + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(radius / 2))
def vgrad(w, h, top, bot):
    im = Image.new("RGBA", (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h; d.line((0, y, w, y), fill=tuple(int(lerp(top[i], bot[i], t)) for i in range(3)))
    return im

# ---------------- шарнирная фигура ----------------
POSES = {  # углы в градусах: torso от вертикали вверх (+ вперёд), бедро/плечо от вертикали вниз (+ вперёд), колено/локоть — сгиб
    "stand": dict(torso=0, th1=0, kn1=0, th2=0, kn2=0, ua1=6, el1=8, ua2=-4, el2=8),
    "qiyam": dict(torso=0, th1=0, kn1=0, th2=0, kn2=0, ua1=18, el1=105, ua2=14, el2=100),
    "ruku":  dict(torso=88, th1=0, kn1=0, th2=0, kn2=0, ua1=-38, el1=0, ua2=-34, el2=0),
    "sujud": dict(torso=118, th1=12, kn1=102, th2=12, kn2=102, ua1=40, el1=60, ua2=36, el2=60),
    "jalsa": dict(torso=0, th1=82, kn1=170, th2=82, kn2=170, ua1=28, el1=55, ua2=24, el2=55),
}

def figure(d, x, ground, p, s=1.0, f=1, robe=(84, 96, 160), robe2=(60, 70, 128), umbrella=None):
    T, NK, R, L1, L2, A1, A2 = 150 * s, 30 * s, 52 * s, 120 * s, 115 * s, 92 * s, 86 * s
    rad = math.radians
    def leg(th, kn):
        k = (L1 * math.sin(rad(th)) * f, L1 * math.cos(rad(th)))
        a = rad(th - kn); return k, (k[0] + L2 * math.sin(a) * f, k[1] + L2 * math.cos(a))
    ta = rad(p["torso"]); sh = (T * math.sin(ta) * f, -T * math.cos(ta))
    hd = (sh[0] + (NK + R) * math.sin(ta) * f, sh[1] - (NK + R) * math.cos(ta))
    def arm(ua, el):
        e = (sh[0] + A1 * math.sin(rad(ua)) * f, sh[1] + A1 * math.cos(rad(ua)))
        a = rad(ua + el); return e, (e[0] + A2 * math.sin(a) * f, e[1] + A2 * math.cos(a))
    k1, f1 = leg(p["th1"], p["kn1"]); k2, f2 = leg(p["th2"], p["kn2"])
    e1, h1 = arm(p["ua1"], p["el1"]); e2, h2 = arm(p["ua2"], p["el2"])
    low = max(f1[1], f2[1], k1[1], k2[1], hd[1] + R, h1[1], h2[1]) + 12 * s
    P = lambda q: (x + q[0], ground - low + q[1])
    def cap(a, b, w, c):
        a, b = P(a), P(b); d.line((a, b), fill=c, width=int(w))
        for q in (a, b): d.ellipse((q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2), fill=c)
    cap((0, 0), k2, 44 * s, robe2); cap(k2, f2, 36 * s, robe2)                     # дальняя нога
    cap(sh, e2, 30 * s, robe2); cap(e2, h2, 26 * s, robe2)                          # дальняя рука
    cap((0, 0), sh, 92 * s, robe)                                                   # туловище-халат
    cap((0, 0), k1, 46 * s, robe); cap(k1, f1, 38 * s, robe)                        # ближняя нога
    hx, hy = P(hd)
    d.ellipse((hx - R, hy - R, hx + R, hy + R), fill=SKIN)                          # голова
    ox, oy = math.sin(ta) * f, -math.cos(ta)                                        # «верх» головы
    cx, cy = hx + ox * R * 0.55, hy + oy * R * 0.55
    d.ellipse((cx - R * 0.95, cy - R * 0.62, cx + R * 0.95, cy + R * 0.62), fill=CAP)  # такья
    bx, by = hx - ox * R * 0.45 + f * R * 0.25, hy - oy * R * 0.45
    d.ellipse((bx - R * 0.7, by - R * 0.5, bx + R * 0.7, by + R * 0.5), fill=BEARD)    # борода
    cap(sh, e1, 32 * s, robe); cap(e1, h1, 28 * s, robe)                            # ближняя рука
    hp = P(h1); d.ellipse((hp[0] - 15 * s, hp[1] - 15 * s, hp[0] + 15 * s, hp[1] + 15 * s), fill=SKIN)
    if umbrella:
        top = (hp[0], hp[1] - 210 * s)
        d.line((hp, top), fill=(40, 40, 50), width=int(8 * s))
        d.pieslice((top[0] - 170 * s, top[1] - 110 * s, top[0] + 170 * s, top[1] + 110 * s), 180, 360, fill=umbrella)

def walk_pose(ph, amp=26):
    sn = math.sin(ph)
    return dict(torso=4, th1=amp * sn, kn1=max(0, 34 * math.sin(ph + 1.2)), th2=-amp * sn, kn2=max(0, 34 * math.sin(ph + 1.2 + math.pi)),
                ua1=-22 * sn, el1=18, ua2=22 * sn, el2=18)

def blend(a, b, t): return {k: lerp(a[k], b[k], ease(t)) for k in a}

# ---------------- сцены ----------------
def bird(d, x, y, t, s=1.0, col=(30, 30, 50)):
    w = 18 * math.sin(t * 9) * s
    d.line(((x - 26 * s, y - w), (x, y), (x + 26 * s, y - w)), fill=col, width=int(5 * s), joint="curve")

# 1. Ночная комната: чтение, перелистывание страницы, свеча
S1 = vgrad(CW, CH, (54, 42, 100), (30, 24, 66)); _d = ImageDraw.Draw(S1)
_d.rectangle((0, GY - 60, CW, CH), fill=(44, 32, 74))
WX, WY, WW, WHh = 600, 70, 270, 340
_d.rounded_rectangle((WX - 14, WY - 14, WX + WW + 14, WY + WHh + 14), 10, fill=(70, 56, 120)); _d.rectangle((WX, WY, WX + WW, WY + WHh), fill=(16, 18, 48))
_d.rectangle((70, 250, 330, 262), fill=(80, 64, 130))
for i, (h, c) in enumerate([(70, (150, 110, 200)), (52, (110, 90, 180)), (84, (180, 130, 170)), (60, (120, 120, 200))]):
    _d.rectangle((90 + i * 46, 250 - h, 124 + i * 46, 250), fill=c)
_d.ellipse((140, 800, 800, 930), fill=(122, 58, 96)); _d.ellipse((170, 815, 770, 915), outline=(170, 90, 130), width=6)
STARS1 = [(WX + random.randint(10, WW - 10), WY + random.randint(10, WHh - 10), random.random() * 6) for _ in range(14)]

def scene1(t):
    im = S1.copy(); d = ImageDraw.Draw(im)
    for x, y, ph in STARS1:
        a = 0.5 + 0.5 * math.sin(t * 2.4 + ph); r = 2 + 2 * a; d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 230))
    mx = WX + 60 + t * 18; my = WY + 80 + t * 4                                        # луна плывёт по окну
    im.alpha_composite(glow((200, 200), (255, 240, 200), 55, 90), (int(mx) - 100, int(my) - 100)); d.ellipse((mx - 30, my - 30, mx + 30, my + 30), fill=(255, 248, 220))
    fl = math.sin(t * 13) * 4 + math.sin(t * 7) * 3                                      # свеча
    im.alpha_composite(glow((300, 300), (255, 180, 90), 80, int(110 + fl * 4)), (650, 590))
    d.rectangle((785, 720, 815, 800), fill=(240, 230, 210)); d.ellipse((786 + fl / 2, 670, 814 + fl / 2, 722), fill=(255, 200, 90)); d.ellipse((794 + fl / 2, 690, 806 + fl / 2, 718), fill=(255, 250, 220))
    nod = math.sin(t * 1.8) * 4                                                          # сидящий читатель
    cx, base = 430, 830
    d.ellipse((cx - 150, base - 70, cx + 150, base + 40), fill=(52, 58, 110))
    d.polygon([(cx - 95, base - 10), (cx + 95, base - 10), (cx + 70, base - 250), (cx - 70, base - 250)], fill=(84, 96, 160))
    d.ellipse((cx - 58, base - 390 + nod, cx + 58, base - 270 + nod), fill=SKIN)
    d.chord((cx - 60, base - 412 + nod, cx + 60, base - 330 + nod), 180, 360, fill=CAP)
    d.ellipse((cx - 50, base - 318 + nod, cx + 50, base - 262 + nod), fill=BEARD)
    d.polygon([(cx - 120, base - 125), (cx, base - 100), (cx, base - 70), (cx - 120, base - 92)], fill=(240, 228, 200))
    d.polygon([(cx + 120, base - 125), (cx, base - 100), (cx, base - 70), (cx + 120, base - 92)], fill=(228, 214, 186))
    pf = (t % 2.5) / 0.7                                                                 # перелистывание страницы
    if pf < 1:
        px = cx + 120 * math.cos(math.pi * ease(pf)); lift = 40 * math.sin(math.pi * ease(pf))
        d.polygon([(cx, base - 100), (px, base - 125 - lift), (px, base - 92 - lift), (cx, base - 70)], fill=(255, 248, 230))
    d.ellipse((cx - 132, base - 128, cx - 92, base - 88), fill=SKIN); d.ellipse((cx + 92, base - 128, cx + 132, base - 88), fill=SKIN)
    return im

# 2. Мечеть на закате: солнце садится, птицы, люди идут к мечети
S2 = vgrad(CW, CH, (60, 40, 110), (250, 150, 110)); _d = ImageDraw.Draw(S2)
_d.rectangle((0, GY, CW, CH), fill=(60, 40, 70))
def mosque(d, ox, col):
    d.rectangle((ox, 560, ox + 380, GY), fill=col); d.ellipse((ox + 80, 400, ox + 300, 640), fill=col)
    d.rectangle((ox + 186, 360, ox + 194, 410), fill=col); d.ellipse((ox + 178, 340, ox + 202, 364), fill=col)
    for mx in (ox - 70, ox + 420):
        d.rectangle((mx, 330, mx + 40, GY), fill=col); d.polygon([(mx - 6, 330), (mx + 46, 330), (mx + 20, 270)], fill=col); d.rectangle((mx - 8, 430, mx + 48, 446), fill=col)
    for i in range(4): d.rounded_rectangle((ox + 40 + i * 85, 660, ox + 80 + i * 85, 740), 18, fill=(255, 200, 120))
BIRDS = [(random.uniform(-200, CW), random.uniform(150, 380), random.uniform(60, 110), random.random() * 6) for _ in range(6)]

def scene2(t):
    im = S2.copy(); d = ImageDraw.Draw(im)
    sy = 480 + t * 40
    im.alpha_composite(glow((420, 420), (255, 220, 140), 100, 140), (60, int(sy) - 210)); d.ellipse((190, sy - 80, 350, sy + 80), fill=(255, 214, 130))
    d.rectangle((0, GY, CW, CH), fill=(60, 40, 70))
    mosque(d, 470, (44, 28, 60))
    for bx, by, sp, ph in BIRDS: bird(d, (bx + t * sp) % (CW + 200) - 100, by + 10 * math.sin(t + ph), t + ph)
    for i, (x0, sp, s) in enumerate([(-60, 95, 0.62), (-260, 95, 0.62), (60, 80, 0.45)]):
        x = x0 + t * sp
        figure(d, x, GY + 20 + i * 6, walk_pose(t * 6.5 + i), s=s, f=1, robe=(70, 60, 110), robe2=(52, 44, 86))
    return im

# 3. Дождливая улица: дождь, фонарь, человек с зонтом, круги на лужах
S3 = vgrad(CW, CH, (26, 34, 60), (46, 58, 88)); _d = ImageDraw.Draw(S3)
WINS = []
for bx, bw, bh in [(0, 230, 520), (250, 200, 640), (470, 260, 470), (750, 200, 600)]:
    _d.rectangle((bx, GY - bh, bx + bw, GY), fill=(34, 40, 66))
    for wy in range(GY - bh + 40, GY - 60, 90):
        for wx in range(bx + 30, bx + bw - 40, 70): WINS.append((wx, wy, random.random() < 0.45, random.random() * 9))
_d.rectangle((0, GY, CW, CH), fill=(40, 46, 70))
RAIN = [(random.uniform(0, CW), random.uniform(0, CH), random.uniform(900, 1300)) for _ in range(140)]
PUDDLES = [(random.uniform(60, CW - 60), random.uniform(GY + 40, CH - 60), random.random() * 1.2) for _ in range(9)]

def scene3(t):
    im = S3.copy(); d = ImageDraw.Draw(im)
    for wx, wy, lit, ph in WINS:
        on = lit and math.sin(t * 0.8 + ph) > -0.7
        d.rectangle((wx, wy, wx + 34, wy + 46), fill=(255, 210, 120) if on else (52, 60, 92))
    im.alpha_composite(glow((360, 360), (255, 210, 130), 90, 110), (30, 300))         # фонарь
    d.rectangle((205, 420, 215, GY + 30), fill=(20, 22, 36)); d.rounded_rectangle((180, 400, 240, 450), 10, fill=(255, 220, 140))
    for px, py, ph in PUDDLES:                                                          # круги на лужах
        k = ((t + ph) % 1.2) / 1.2
        d.ellipse((px - 20 - 60 * k, py - 6 - 16 * k, px + 20 + 60 * k, py + 6 + 16 * k), outline=(150, 170, 220, int(200 * (1 - k))), width=3)
    x = -150 + t * 230
    figure(d, x, GY + 70, walk_pose(t * 7, 22), s=0.85, f=1, robe=(60, 90, 140), robe2=(44, 66, 110), umbrella=(220, 70, 90))
    for rx, ry, sp in RAIN:
        y = (ry + t * sp) % CH; xx = (rx - t * 120) % CW
        d.line((xx, y, xx - 6, y + 34), fill=(180, 200, 240, 150), width=3)
    return im

# 4. Молитва: человек совершает намаз, фонарь-светильник качается
S4 = vgrad(CW, CH, (16, 70, 74), (10, 44, 52)); _d = ImageDraw.Draw(S4)
_d.rectangle((0, GY - 20, CW, CH), fill=(14, 40, 48))
_d.rounded_rectangle((540, 170, 840, GY - 20), 150, fill=(22, 96, 98)); _d.rounded_rectangle((570, 200, 810, GY - 20), 120, fill=(12, 58, 64))  # михраб
for i in range(12): _d.ellipse((60 + i * 72, 120, 76 + i * 72, 136), fill=(230, 190, 90))                                          # орнамент
_d.polygon([(120, GY + 10), (620, GY + 10), (680, GY + 90), (60, GY + 90)], fill=(150, 40, 60)); _d.line(((150, GY + 30), (610, GY + 30)), fill=(220, 170, 90), width=5)
PRAY = [(0.0, "qiyam"), (1.0, "qiyam"), (1.5, "ruku"), (2.2, "ruku"), (2.7, "qiyam"), (3.0, "qiyam"), (3.5, "sujud"), (4.3, "sujud"), (4.8, "jalsa")]
def pray_pose(t):
    for (a, pa), (b, pb) in zip(PRAY, PRAY[1:]):
        if t <= b: return blend(POSES[pa], POSES[pb], (t - a) / (b - a))
    return POSES[PRAY[-1][1]]

def scene4(t):
    im = S4.copy(); d = ImageDraw.Draw(im)
    ang = math.sin(t * 2.0) * 0.18; ax, ay = 220, 0                                    # качающийся светильник
    lx, ly = ax + math.sin(ang) * 300, ay + math.cos(ang) * 300
    d.line(((ax, ay), (lx, ly)), fill=(200, 170, 90), width=4)
    im.alpha_composite(glow((280, 280), (255, 210, 120), 70, 120), (int(lx) - 140, int(ly) - 100))
    d.polygon([(lx - 30, ly), (lx + 30, ly), (lx + 40, ly + 50), (lx, ly + 80), (lx - 40, ly + 50)], fill=(255, 210, 120))
    figure(d, 330, GY + 40, pray_pose(t), s=0.95, f=1, robe=(235, 235, 240), robe2=(200, 200, 210))
    return im

# 5. Утро: восход, облака, качающееся дерево, отец с сыном идут по дороге
S5 = vgrad(CW, CH, (120, 180, 240), (255, 220, 180)); _d = ImageDraw.Draw(S5)
CLOUDS = [(random.uniform(0, CW), random.uniform(80, 330), random.uniform(12, 30), random.uniform(0.8, 1.3)) for _ in range(5)]
def scene5(t):
    im = S5.copy(); d = ImageDraw.Draw(im)
    sy = 640 - t * 50
    im.alpha_composite(glow((460, 460), (255, 230, 150), 110, 160), (560, int(sy) - 230)); d.ellipse((700, sy - 90, 880, sy + 90), fill=(255, 226, 140))
    for cx, cy, sp, s in CLOUDS:
        x = (cx + t * sp) % (CW + 300) - 150
        for dx, dy, r in [(0, 0, 50), (50, -20, 60), (110, 0, 48)]: d.ellipse((x + dx * s - r * s, cy + dy * s - r * s, x + dx * s + r * s, cy + dy * s + r * s), fill=(255, 255, 255))
    d.ellipse((-200, 600, 600, 1000), fill=(110, 180, 120)); d.ellipse((350, 640, 1200, 1060), fill=(90, 160, 110))   # холмы
    d.rectangle((0, GY - 10, CW, CH), fill=(96, 170, 110)); d.polygon([(0, GY + 60), (CW, GY + 20), (CW, GY + 120), (0, GY + 170)], fill=(220, 200, 160))  # дорога
    sw = math.sin(t * 2.2) * 14                                                         # дерево качается
    d.polygon([(130, GY), (170, GY), (162 + sw * 0.3, 520), (140 + sw * 0.3, 520)], fill=(110, 76, 60))
    for dx, dy, r, c in [(-70, 470, 110, (60, 140, 90)), (60, 450, 120, (70, 160, 100)), (0, 380, 120, (80, 170, 110))]:
        x = 150 + dx + sw * (1.2 if dy < 460 else 0.8); d.ellipse((x - r, dy - r, x + r, dy + r), fill=c)
    for i, (sp, ph) in enumerate([(70, 0.0), (85, 1.5)]): bird(d, (200 + t * sp + i * 160) % CW, 230 + i * 40 + 12 * math.sin(t * 1.4 + ph), t + ph, 0.9, (60, 60, 90))
    x = 120 + t * 95
    figure(d, x, GY + 105, walk_pose(t * 6.2, 24), s=0.8, f=1, robe=(80, 110, 170), robe2=(60, 84, 136))
    figure(d, x + 110, GY + 120, walk_pose(t * 8.5 + 1, 28), s=0.5, f=1, robe=(230, 140, 80), robe2=(190, 110, 60))
    return im

SCENES = [(scene1, "Ilm — qalbning nuri"), (scene2, "Namoz — dinning ustuni"),
          (scene3, "Har bir qiyinchilikdan keyin\nyengillik bor"), (scene4, "Sajdada banda Robbiga\neng yaqin bo‘ladi"),
          (scene5, "Har bir tong —\nyangi imkoniyat")]
DUR = SCENE_LEN * len(SCENES)

# ---------------- страница ----------------
page = Image.new("RGBA", (W, H), BG + (255,)); pd = ImageDraw.Draw(page)
for (x, y, r) in [(-200, 300, 700), (1200, 1500, 800)]: page.alpha_composite(glow((r, r), (60, 50, 140), r // 4, 60), (x - r // 2 + 200, y - r // 2))
logo = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); ld = ImageDraw.Draw(logo)
ld.ellipse((10, 10, 110, 110), fill=(186, 160, 255)); ld.ellipse((38, 2, 128, 92), fill=(0, 0, 0, 0))
tw = pd.textbbox((0, 0), "sizning nomingiz", font=font("Bold", 58))[2]; lx0 = (W - (96 + 18 + tw)) // 2
page.alpha_composite(logo.resize((96, 96)), (lx0, 196))
pd.text((lx0 + 114, 200), "sizning nomingiz", font=font("Bold", 58), fill=(240, 240, 255))
pd.text((lx0 + 116, 266), "ma’ruzalar zamonaviy uslubda", font=font("Medium", 30), fill=(170, 160, 230))
pd.text((W // 2, 1790), "@sizning_sahifa", font=font("Medium", 34), fill=(150, 150, 190), anchor="mm")
shadow = Image.new("RGBA", (CW + 80, CH + 80), (0, 0, 0, 0)); ImageDraw.Draw(shadow).rounded_rectangle((40, 50, CW + 40, CH + 50), 46, fill=(0, 0, 0, 150))
page.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)), (CX0 - 40, CY0 - 40))
MASK = Image.new("L", (CW, CH), 0); ImageDraw.Draw(MASK).rounded_rectangle((0, 0, CW - 1, CH - 1), 46, fill=255)
F_SUB = font("SemiBold", 56)

def frame(t):
    i = min(int(t // SCENE_LEN), len(SCENES) - 1); lt = t - i * SCENE_LEN
    sc = SCENES[i][0](lt)
    if lt < XF and i > 0:                                                    # плавный переход из прошлой сцены
        sc = Image.blend(SCENES[i - 1][0](lt + SCENE_LEN), sc, ease(lt / XF))
    img = page.copy(); img.paste(sc.convert("RGB"), (CX0, CY0), MASK)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((CX0, CY0, CX0 + CW - 1, CY0 + CH - 1), 46, outline=(120, 100, 200), width=3)
    py = CY0 + CH + 50
    d.rounded_rectangle((CX0 + 20, py, CX0 + CW - 20, py + 8), 4, fill=(60, 60, 92))
    d.rounded_rectangle((CX0 + 20, py, CX0 + 20 + int((CW - 40) * t / DUR), py + 8), 4, fill=(186, 160, 255))
    al = min(ease((lt - 0.3) / 0.5), ease((SCENE_LEN - lt - 0.2) / 0.4))
    if al > 0:
        lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.multiline_text((W // 2 + 3, 24 + 4), SCENES[i][1], font=F_SUB, fill=(0, 0, 0, int(140 * al)), anchor="ma", align="center", spacing=16)
        ld.multiline_text((W // 2, 24), SCENES[i][1], font=F_SUB, fill=(255, 255, 255, int(255 * al)), anchor="ma", align="center", spacing=16)
        img = img.convert("RGBA"); img.alpha_composite(lay, (0, py + 60 + int((1 - al) * 16)))
    return img.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 2:                       # режим превью: кадры в указанные моменты
        for k, tt in enumerate(map(float, sys.argv[2].split(","))): frame(tt).resize((360, 640)).save(f"{OUT}_{k}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)): p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait(); print("done", OUT)
