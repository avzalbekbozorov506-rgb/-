"""Макиавелли, «Государь», гл. XVIII — притча о лисе и льве. Псевдо-3D «под Pixar», субтитры синхронно с голосом."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pixar_kit import ball, put
from pixar_animals import quadruped, PRINCE

W, H = 1080, 1920
HEAD = ("МАКИАВЕЛЛИ", "«ГОСУДАРЬ», ГЛАВА XVIII")
TITLE = ("ЛИСА И ЛЕВ", "Притча по книге Макиавелли", "СМОТРИ ДО КОНЦА")
CREDIT = "Анимация · по мотивам «Государя» Н. Макиавелли"
PROG = [[50, 57, 62, 65], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 57, 61]]
BOT_ALPHA, TOP_ALPHA, VIG, AA, GRAIN = 215, 160, 120, 0.35, 2.5
TEXT_DY, QUOTE_SIZE, SUB_CHARS = 262, 66, 26
OF = 255; GY = 1075 + OF; SP = 1.38
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(int(lerp(a[i], b[i], t)) for i in range(3))
def blink_at(t, ph=0.0): k = (t + ph) % 3.1; return max(0, 1 - abs(k - 0.08) / 0.08) if k < 0.16 else 0.0
def talk_amp(lt, on=True): return abs(math.sin(lt * 9)) * (0.6 + 0.4 * math.sin(lt * 2.3)) if on else 0.0

def glow(size, col, a):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((size * 0.25, size * 0.25, size * 0.75, size * 0.75), fill=col + (a,))
    return g.filter(ImageFilter.GaussianBlur(size / 7))
def build_far():
    yy = np.linspace(0, 1, GY)[:, None, None]; a = np.zeros((H, W, 3)); a[:GY] = np.array((110, 170, 228)) * (1 - yy) + np.array((255, 210, 160)) * yy
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA"); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(3)
    d.ellipse((-300, 860, 700, 1500), fill=(120, 150, 120)); d.ellipse((400, 820, 1500, 1500), fill=(108, 140, 116))     # холмы
    cx = 760; d.rectangle((cx - 120, 700, cx + 120, 1000), fill=(176, 160, 170))                                    # замок вдали
    for tx in (cx - 150, cx + 110): d.rectangle((tx, 620, tx + 40, 1000), fill=(166, 150, 162)); d.polygon([(tx - 10, 620), (tx + 50, 620), (tx + 20, 560)], fill=(150, 70, 80))
    d.polygon([(cx - 60, 700), (cx + 60, 700), (cx, 610)], fill=(150, 70, 80))
    for k in range(14): s = r.randint(150, 280); put(lay, ball(s, int(s * 1.1), (70 + r.randint(0, 30), 130 + r.randint(0, 30), 70), rim=0.5, spec=0.06), r.randint(-80, 1160), r.randint(1000, 1120))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6))); return im
FAR = build_far()
BUSHES = [(70, GY - 30, 230), (230, GY - 10, 170), (980, GY - 26, 220)]
FLOWERS = [(random.Random(k).uniform(0, W), random.Random(k + 7).uniform(GY + 30, GY + 260), random.Random(k + 3).choice([(255, 210, 90), (255, 140, 160), (250, 250, 250)])) for k in range(36)]
DUST = [(random.Random(k).uniform(0, W), random.Random(k + 50).uniform(400, 1300), random.Random(k + 90).uniform(0, 6)) for k in range(24)]

def world(lt, night=0.0, sun=(240, 760)):
    im = FAR.copy(); im.alpha_composite(glow(900, (255, 220, 150), int(160 * (1 - night))), (sun[0] - 450, sun[1] - 450))
    d = ImageDraw.Draw(im); d.ellipse((sun[0] - 66, sun[1] - 66, sun[0] + 66, sun[1] + 66), fill=lerpc((255, 240, 200), (236, 236, 246), night))
    g = np.zeros((H - GY, W, 3)); gg = np.linspace(0, 1, H - GY)[:, None, None]; g[:] = np.array((112, 166, 80)) * (1 - gg * 0.5)
    im.paste(Image.fromarray(g.astype(np.uint8)), (0, GY)); d = ImageDraw.Draw(im); r = random.Random(5)
    for k in range(240): x, y = r.uniform(0, W), r.uniform(GY - 10, GY + 300); d.line(((x, y), (x + r.uniform(-6, 6), y - r.uniform(10, 26))), fill=(78, 128, 60), width=3)
    for x, y, c in FLOWERS: put(im, ball(18, 18, c, rim=0.2, spec=0.4), x, y)
    for x, y, s in BUSHES: put(im, ball(s, int(s * 0.8), (64, 120, 62), rim=0.5, spec=0.08), x, y)
    if night:
        im.alpha_composite(Image.new("RGBA", (W, H), (16, 22, 64, int(165 * night)))); d = ImageDraw.Draw(im)
        for k in range(40): rr = random.Random(k); x, y = rr.uniform(0, W), rr.uniform(260, 800); a = 0.5 + 0.5 * math.sin(lt * 2 + k); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 230, int(220 * night * a)))
        im.alpha_composite(glow(300, (240, 240, 255), int(120 * night)), (780, 300)); d.ellipse((880, 400, 980, 500), fill=(240, 240, 250, int(255 * night)))
    return im
def dust(im, lt, k=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, ph in DUST:
        yy = y - (lt * 14 + ph * 40) % 200; xx = x + 18 * math.sin(lt * 0.6 + ph); a = 0.5 + 0.5 * math.sin(lt * 1.5 + ph)
        d.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=(255, 236, 190, int(110 * a * k)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2.5)))
def place(im, spr, x, feet, shadow=0.6):
    sh = Image.new("RGBA", (spr.width, 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((spr.width * 0.18, 10, spr.width * 0.82, 50), fill=(20, 30, 10, int(180 * shadow)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (int(x - spr.width / 2), int(feet - 34)))
    im.alpha_composite(spr, (int(x - spr.width / 2), int(feet - spr.height + 12)))
def trap(im, x, y, closed=0.0, glow_k=0.0):
    if glow_k: im.alpha_composite(glow(260, (255, 210, 90), int(200 * glow_k)), (int(x - 130), int(y - 130)))
    d = ImageDraw.Draw(im); put(im, ball(150, 40, (110, 112, 122), rim=0.3, spec=0.5), x, y)
    h = lerp(70, 18, closed)
    for s in (-1, 1):
        cx = x + s * lerp(48, 6, closed); d.arc((cx - 46, y - h, cx + 46, y + h * 0.4), 180, 360, fill=(150, 154, 166), width=8)
        for k in range(5): tx = cx - 34 + k * 17; d.polygon([(tx - 6, y - h * 0.5), (tx + 6, y - h * 0.5), (tx, y - h * 0.5 - 14)], fill=(196, 200, 210))

# ---------- сцены ----------
def s_title(lt, D):
    im = world(lt); p = PRINCE.render(scale=SP, mood="happy" if lt > 2 else "neutral", blink=blink_at(lt), squash=0.02 * math.sin(lt * 2.4))
    place(im, p, 540, GY + 20); dust(im, lt); return im.convert("RGB")
def s_strong(lt, D):
    im = world(lt); flex = abs(math.sin(lt * 2.2))
    p = PRINCE.render(scale=SP, mood="talk" if flex > 0.5 else "happy", talk=flex * 0.8, arms=((150 - 20 * flex, -60), (-150 + 20 * flex, 60)), bounce=flex * 10, blink=blink_at(lt))
    place(im, p, 540, GY + 20)
    sh = quadruped("lion", t=lt, roar=flex, scale=1.6); sh = Image.eval(sh.getchannel("A"), lambda v: v * 0.25)              # «тень льва» за спиной
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.paste(Image.new("RGBA", sh.size, (60, 40, 30, 255)), (int(540 - sh.width / 2 + 60), GY - sh.height - 80), sh)
    im2 = world(lt); im2.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10))); place(im2, p, 540, GY + 20); dust(im2, lt); return im2.convert("RGB")
def s_trap(lt, D):
    im = world(lt); u = min(lt / (D * 0.55), 1); x = lerp(260, 600, u); snap = ease((lt - D * 0.55) / 0.15)
    trap(im, 690, GY + 30, closed=snap)
    if snap < 0.5: p = PRINCE.render(scale=SP, mood="happy", legs=(20 * math.sin(lt * 7), -20 * math.sin(lt * 7)), arms=((-20 * math.sin(lt * 7), 15), (20 * math.sin(lt * 7), 15)), bounce=abs(math.sin(lt * 7)) * 8, blink=blink_at(lt), look=(0.6, 0.3))
    else: p = PRINCE.render(scale=SP, mood="surprised" if lt < D * 0.8 else "sad", bounce=30 * math.exp(-(lt - D * 0.55) * 6), arms=((120, 20), (-120, -20)), blink=0, look=(0.3, 0.8), lean=-6)
    place(im, p, x, GY + 20); dust(im, lt); return im.convert("RGB")
def s_fox(lt, D):
    im = world(lt); u = min(lt / 1.6, 1); fx = lerp(-150, 330, ease(u)); show = ease((lt - D * 0.6) / 0.6)
    for tx, ty in ((570, GY + 50), (960, GY + 20), (90, GY + 40)): trap(im, tx, ty, glow_k=show * (0.6 + 0.4 * math.sin(lt * 4)))
    fox_talk = lt > D * 0.3
    fox = quadruped("fox", t=lt, f=1, walk=lt * 8 if u < 1 else 0, talk=talk_amp(lt, fox_talk), blink=blink_at(lt, 0.4), look=(0.7, 0.1))
    place(im, fox, fx, GY + 60)
    p = PRINCE.render(scale=SP, mood="sad" if lt < D * 0.6 else "surprised", f=-1, look=(-0.8, 0.2) if lt < D * 0.6 else (0, 0.8), blink=blink_at(lt))
    place(im, p, 790, GY + 20); dust(im, lt); return im.convert("RGB")
def s_wolves(lt, D):
    im = world(lt, night=1.0); u = min(lt / D, 1)
    for k, x0 in enumerate((1020, 1200)):
        w = quadruped("wolf", t=lt + k, f=-1, walk=lt * 7 + k, glow_eyes=True, mood="angry", look=(-0.7, 0.1), scale=0.95)
        place(im, w, x0 - u * 420, GY + 30 + k * 40, shadow=0.4)
    p = PRINCE.render(scale=SP, mood="surprised", f=1, look=(0.9, 0.1), blink=0, arms=((60, 60), (-50, 40)), squash=0.03 * math.sin(lt * 20))
    place(im, p, 300, GY + 20); return im.convert("RGB")
def s_lion(lt, D):
    night = 1 - ease((lt - D * 0.6) / (D * 0.4)); im = world(lt, night=night)
    roar = max(0, math.sin(min(lt, D) * 3)) if lt > 0.6 else 0; run = max(0, lt - 1.0)
    for k, x0 in enumerate((730, 930)):
        w = quadruped("wolf", t=lt + k, f=1 if run else -1, walk=lt * 12 + k if run else 0, glow_eyes=night > 0.5, mood="surprised" if run else "angry", scale=0.95)
        place(im, w, x0 + run * 700, GY + 40 + k * 50, shadow=0.4)
    lion = quadruped("lion", t=lt, f=1, roar=roar, blink=blink_at(lt), scale=1.25, look=(0.8, 0))
    place(im, lion, 380, GY + 40)
    d = ImageDraw.Draw(im)
    for k in range(3):                                                                # волны рыка
        r = 60 + ((lt * 260 + k * 90) % 300)
        if roar > 0.2: d.arc((560 - r, GY - 330 - r, 560 + r, GY - 330 + r), -40, 40, fill=(255, 236, 190, int(220 * (1 - r / 360))), width=8)
    return im.convert("RGB")
def s_lesson(lt, D):
    im = world(lt)
    fox = quadruped("fox", t=lt, f=1, blink=blink_at(lt, 0.3), look=(0.5, -0.2), scale=0.95); place(im, fox, 190, GY + 60)
    lion = quadruped("lion", t=lt, f=-1, blink=blink_at(lt, 1.2), look=(-0.5, -0.2), scale=1.05); place(im, lion, 880, GY + 50)
    p = PRINCE.render(scale=SP, mood="happy", blink=blink_at(lt), look=(math.sin(lt * 0.8), -0.1)); place(im, p, 540, GY + 20)
    dust(im, lt); return im.convert("RGB")
def s_outro(lt, D):
    im = world(lt, sun=(240, 860))
    fox = quadruped("fox", t=lt, f=1, blink=blink_at(lt, 0.3), scale=0.95); place(im, fox, 190, GY + 60)
    lion = quadruped("lion", t=lt, f=-1, blink=blink_at(lt, 1.2), scale=1.05); place(im, lion, 880, GY + 50)
    p = PRINCE.render(scale=SP, mood="talk" if lt < D * 0.6 else "happy", talk=talk_amp(lt) * 0.0, blink=blink_at(lt), look=(0, 0)); place(im, p, 540, GY + 20)
    dust(im, lt); return im.convert("RGB")

SCENES = [
    ("Макиав+елли. «Госуд+арь». История о лисе и льве.", None, None, s_title, CREDIT, None),
    ("Жил-был молодой правитель. | Он верил, что всё решает сила. | И хотел быть только львом.", "SUB", "ГЛАВА XVIII", s_strong, CREDIT, None),
    ("Но однажды | он не заметил капкан.", "SUB", "", s_trap, CREDIT, None),
    ("Из кустов вышла лиса. | @xenia: Сила не видит ловушек. | @xenia: Смотри внимательно, правитель.", "SUB", "ЛИСА", s_fox, CREDIT, None),
    ("А ночью к замку пришли волки. | И хитрость их не остановила.", "SUB", "НОЧЬ", s_wolves, CREDIT, None),
    ("Тогда вышел лев — | и одним рыком прогнал их.", "SUB", "ЛЕВ", s_lion, CREDIT, None),
    ("Макиав+елли писал: | правитель должен быть лисой, | чтобы распознать капканы, | и львом, | чтобы отпугнуть волков.", "SUB", "«ГОСУДАРЬ», ГЛАВА XVIII", s_lesson, CREDIT, None),
    ("Тот, кто хочет быть только львом, | этого не понимает. | А вы сегодня — лиса или лев? | Напишите в комментариях.", "SUB", "ВАШ ОТВЕТ", s_outro, CREDIT, None),
]
