"""Л. Н. Толстой, «Много ли человеку земли нужно» (1886) — анимированный пересказ. Солнце идёт по небу от рассвета до заката через весь ролик."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from make_scenes_demo import figure, walk_pose, bird, POSES

W, H = 1080, 1920
INK, GY = (36, 30, 28), 990
HEAD = ("ЛЕВ ТОЛСТОЙ", "«МНОГО ЛИ ЧЕЛОВЕКУ ЗЕМЛИ НУЖНО», 1886")
TITLE = ("ТОЛСТОЙ", "«Много ли человеку земли нужно»", "РАССКАЗ О ТОМ, ГДЕ ПРОХОДИТ ЧЕРТА")
PROG = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 56]]
CREDIT = "Анимация · пересказ рассказа Л. Н. Толстого"
PAHOM = dict(robe=(116, 74, 52), robe2=(86, 54, 38), hat=(70, 48, 34), beard=(90, 66, 44))
ELDER = dict(robe=(70, 60, 54), robe2=(52, 44, 40), hat=(150, 100, 60), beard=(200, 196, 190))
WORKER = dict(robe=(90, 92, 80), robe2=(66, 68, 58), hat=(60, 56, 50), beard=None)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

SKIES = {"dawn": ((92, 96, 130), (236, 176, 128)), "morning": ((150, 176, 200), (238, 214, 170)), "noon": ((120, 162, 206), (226, 220, 196)),
         "evening": ((96, 92, 130), (240, 156, 90)), "sunset": ((70, 50, 92), (226, 92, 60)), "dusk": ((30, 30, 56), (96, 60, 80))}
def steppe(sky, ground=(150, 128, 82)):
    top, hor = SKIES[sky]; yy = np.linspace(0, 1, GY)[:, None, None]
    a = np.zeros((H, W, 3)); a[:GY] = np.array(top) * (1 - yy) + np.array(hor) * yy
    g = np.linspace(0, 1, H - GY)[:, None, None]; a[GY:] = np.array(ground) * (1 - g * 0.45) + np.array([60, 50, 36]) * g * 0.45
    a += np.random.default_rng(7).normal(0, 3, (H, W, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    r = random.Random(4)
    for k in range(220):                                                        # штрихи травы
        x, y = r.uniform(0, W), r.uniform(GY + 5, GY + 360); d.line(((x, y), (x + r.uniform(-4, 4), y - r.uniform(6, 16))), fill=(110, 92, 58), width=2)
    return im
def sun(im, x, y, r=70, col=(255, 214, 140)):
    g = Image.new("RGBA", (r * 6, r * 6), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((r * 1.5, r * 1.5, r * 4.5, r * 4.5), fill=col + (90,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.6)), (int(x - r * 3), int(y - r * 3)))
    ImageDraw.Draw(im).ellipse((x - r, y - r, x + r, y + r), fill=col)
def clip_horizon(im, sky):                                                       # солнце уходит за горизонт
    base = steppe(sky); im.paste(base.crop((0, GY, W, H)), (0, GY)); return im
def hill(d, cx, w=420, h=150, col=(118, 98, 62)): d.chord((cx - w, GY - h, cx + w, GY + h), 180, 360, fill=col)
def run_pose(ph, lean=14, amp=40):
    p = walk_pose(ph, amp); p["torso"] = lean; p["ua1"] *= 1.6; p["ua2"] *= 1.6; return p
def spade(d, hand, up=True):
    x, y = hand; d.line(((x, y), (x + (18 if up else 8), y - 150)), fill=(80, 60, 40), width=6) if up else None

BG = {k: steppe(k) for k in SKIES}

def s_title(lt, D):
    im = BG["dawn"].copy(); sun(im, 820, GY - 10 - lt * 6, 80, (255, 190, 120)); im = clip_horizon(im, "dawn"); d = ImageDraw.Draw(im)
    hill(d, 300); figure(d, 300, GY - 140, POSES["jalsa"], s=0.6, f=1, **ELDER)
    for i in range(3): bird(d, (100 + lt * 60 + i * 80) % (W + 100), 520 + i * 26, lt + i, 0.9, INK)
    figure(d, 560, GY + 30, POSES["stand"], s=0.75, f=-1, **PAHOM)
    return im.convert("RGB")

def s_deal(lt, D):
    im = BG["morning"].copy(); sun(im, 820, GY - 60 - lt * 22, 75); im = clip_horizon(im, "morning"); d = ImageDraw.Draw(im)
    hill(d, 300); figure(d, 300, GY - 140, POSES["jalsa"], s=0.6, f=1, **ELDER)
    d.ellipse((380, GY - 150, 430, GY - 128), fill=(150, 100, 60))                # шапка старшины на земле — точка старта
    u = ease((lt - D * 0.45) / (D * 0.55))
    if u <= 0: figure(d, 520, GY + 30, POSES["stand"], s=0.75, f=-1, **PAHOM)
    else: figure(d, 520 + u * 520, GY + 30, walk_pose(lt * 6, 26), s=0.75, f=1, **PAHOM)
    return im.convert("RGB")

STAKES = [140 + k * 150 for k in range(6)]
def s_greed(lt, D):
    im = BG["noon"].copy(); sun(im, 540 + lt * 20, 330, 70, (255, 236, 180)); d = ImageDraw.Draw(im)
    for c in range(3):
        cx = (c * 420 + lt * 30) % (W + 400) - 200; cy = 480 + c * 60
        for dx, r in [(0, 50), (60, 66), (130, 48)]: d.ellipse((cx + dx - r, cy - r * 0.6, cx + dx + r, cy + r * 0.6), fill=(246, 244, 236))
    x = -60 + lt / D * 1180
    for sx in STAKES:                                                           # отметки-ямки появляются за ним
        if sx < x - 40: d.rectangle((sx - 4, GY + 40, sx + 4, GY + 90), fill=(80, 60, 40)); d.ellipse((sx - 26, GY + 84, sx + 26, GY + 100), fill=(90, 70, 46))
    figure(d, x, GY + 100, walk_pose(lt * 6.5, 28), s=0.8, f=1, **PAHOM)
    return im.convert("RGB")

def s_turn(lt, D):
    im = BG["evening"].copy(); sun(im, 300, 560 + lt * 40, 80, (255, 180, 100)); im = clip_horizon(im, "evening"); d = ImageDraw.Draw(im)
    d.chord((60, GY - 26, 200, GY + 26), 180, 360, fill=(100, 78, 56))            # холм — далеко-далеко
    u = ease((lt - 1.4) / 1.0)
    x = 860 - max(0, lt - 1.4) / (D - 1.4) * 700
    if lt < 1.4: figure(d, 860, GY + 80, POSES["stand"], s=0.6, f=1, **PAHOM)
    else: figure(d, x, GY + 80, run_pose(lt * 9), s=0.6, f=-1, **PAHOM)
    if lt > 2.6: d.ellipse((800, GY + 70, 880, GY + 92), fill=(116, 74, 52))       # брошенный кафтан
    if lt > 3.6: d.rectangle((700, GY + 74, 716, GY + 92), fill=(40, 30, 24)); d.rectangle((722, GY + 76, 738, GY + 92), fill=(40, 30, 24))  # сапоги
    return im.convert("RGB")

def s_fall(lt, D):
    im = BG["sunset"].copy(); sy = GY - 40 + lt / D * 120; sun(im, 700, sy, 95, (255, 120, 70)); im = clip_horizon(im, "sunset"); d = ImageDraw.Draw(im)
    d.polygon([(0, GY + 60), (380, GY - 160), (520, GY - 170), (W, GY + 80), (W, H), (0, H)], fill=(84, 60, 52))   # склон холма
    figure(d, 400, GY - 158, POSES["jalsa"], s=0.6, f=1, **ELDER)
    u = min(lt / (D * 0.62), 1)
    if u < 1:
        x = lerp(980, 740, u); y = lerp(GY + 70, GY - 70, u)
        figure(d, x, y, run_pose(lt * 10, 22 + u * 14), s=0.72, f=-1, **PAHOM)
    else:
        k = ease((lt - D * 0.62) / 0.6)                                              # падает
        pose = dict(torso=lerp(30, 92, k), th1=lerp(20, 80, k), kn1=lerp(30, 0, k), th2=lerp(-20, 80, k), kn2=0, ua1=lerp(-40, 150, k), el1=0, ua2=lerp(40, 160, k), el2=0)
        figure(d, 740, GY - 66, pose, s=0.72, f=-1, **PAHOM)
    return im.convert("RGB")

def s_grave(lt, D):
    im = BG["dusk"].copy(); d = ImageDraw.Draw(im)
    for k in range(40):
        r = random.Random(k); x, y = r.uniform(0, W), r.uniform(260, 800); a = 0.5 + 0.5 * math.sin(lt * 2 + k)
        if lt > k * 0.12: d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(240, 230, 210, int(100 + 150 * a)))
    d.ellipse((760, 420, 840, 500), fill=(236, 228, 210))
    dig = lt < D * 0.55
    d.chord((380, GY + 40, 700, GY + 130), 180, 360, fill=(70, 52, 40))                 # холмик ровно в рост
    if dig:
        b = (math.sin(lt * 4) + 1) / 2
        pose = dict(torso=lerp(10, 60, b), th1=0, kn1=lerp(0, 20, b), th2=0, kn2=0, ua1=lerp(30, -20, b), el1=20, ua2=lerp(20, -30, b), el2=20)
        figure(d, 780, GY + 110, pose, s=0.75, f=-1, **WORKER)
    else:
        figure(d, 780, GY + 110, POSES["stand"], s=0.75, f=-1, **WORKER)
        d.line(((700, GY + 40), (712, GY - 120)), fill=(90, 70, 50), width=7)          # лопата воткнута у холмика
    return im.convert("RGB")

def s_outro(lt, D):
    im = BG["dusk"].copy(); d = ImageDraw.Draw(im); d.ellipse((760, 420, 840, 500), fill=(236, 228, 210))
    for k in range(40):
        r = random.Random(k); x, y = r.uniform(0, W), r.uniform(260, 800); a = 0.5 + 0.5 * math.sin(lt * 2 + k); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(240, 230, 210, int(100 + 150 * a)))
    d.chord((480, GY + 50, 600, GY + 90), 180, 360, fill=(60, 46, 36))
    return im.convert("RGB")

SCENES = [
    ("Лев Толст+ой. «Много ли человеку земли нужно». Короткая история о том, где проходит черта.",
     None, None, s_title, CREDIT, None),
    ("Крестьянину Пах+ому предложили сделку. Сколько земли он обойдёт за день — от восхода до заката, — вся будет его. Но если к закату не вернётся на холм — пропали деньги.",
     "Сколько обойдёшь за день —\nвсё твоё. Но к закату\nвернись на холм", "УТРО", s_deal, CREDIT, None),
    ("Пах+ом шёл и шёл. Здесь хорошая земля — жалко бросить. А там — ещё лучше. И он забирал всё дальше и дальше.",
     "Здесь хорошая земля —\nжалко бросить. А там —\nещё лучше", "ПОЛДЕНЬ", s_greed, CREDIT, None),
    ("А солнце уже клонилось к закату. Пах+ом понял, что зашёл слишком далеко. Он бросил кафтан, сапоги — и побежал.",
     "Солнце клонилось к закату.\nОн зашёл\nслишком далеко", "ВЕЧЕР", s_turn, CREDIT, None),
    ("Он добежал до холма в ту минуту, когда солнце село. Упал — и больше не поднялся.",
     "Он добежал,\nкогда солнце село.\nИ больше не поднялся", "ЗАКАТ", s_fall, CREDIT, None),
    ("Работник вырыл ему могилу. Ровно по росту — три арш+ина. Столько земли ему и было нужно.",
     "Три аршина —\nстолько земли ему\nи было нужно", "ФИНАЛ", s_grave, CREDIT, None),
    ("А где ваша черта, после которой — достаточно? Напишите в комментариях. И сохраните, чтобы помнить.",
     "Где ваша черта,\nпосле которой —\nдостаточно?", "НАПИШИТЕ В КОММЕНТАРИЯХ", s_outro, CREDIT, None),
]
