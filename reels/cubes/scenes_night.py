"""Ролик «Заказчик сказал: идеально» — ночная комната, мальчик-дизайнер с кофе и Клод; по мотивам ролика @canwebuildthis, текст свой, на русском.
Сценарий: reels/scripts/claude_designer_night.md. Запуск: SCENES=scenes_night python3 video.py reels/hq/claude_night_hq.mp4"""
import random, numpy as np
from PIL import Image, ImageDraw
from cuberender import Box, Camera, Lights
from scenes import cl, pe, G, LINE as _LINE, planks
PLATE = ""; NO_MUSIC = False
LINE = dict(_LINE); LINE["client"] = dict(speaker=1, rate=.95, pitch=.9)      # голос заказчика в телефоне

def code_img():
    im = Image.new("RGBA", (640, 400), (14, 20, 36, 255)); d = ImageDraw.Draw(im); rnd = random.Random(5)
    for r in range(18):
        x = 24 + (r % 3) * 26; cols = [(110, 170, 255), (120, 220, 190), (255, 190, 110), (200, 150, 255)]
        for _ in range(rnd.randint(2, 5)):
            w = rnd.randint(40, 150); d.rounded_rectangle((x, 20 + r * 20, x + w, 30 + r * 20), 4, fill=rnd.choice(cols) + (255,)); x += w + 12
    return np.asarray(im, np.uint8)

def night_static():
    B = [Box((0, 9.5, 3), (40, .2, 14), (14, 20, 48), glow=True, glowk=.55),                 # ночное небо в окне
         Box((0, 1.0, -.1), (14, 10, .2), (34, 26, 24), tex=planks),                       # пол
         Box((-4.4, 2.0, 2.2), (.3, 6, 4.6), (22, 28, 52)), Box((4.4, 2.0, 2.2), (.3, 6, 4.6), (22, 28, 52))]
    rnd = random.Random(7)
    for _ in range(46):                                                                    # огни города: размытые пятна (глубина резкости)
        c = rnd.choice([(255, 206, 120), (255, 180, 90), (120, 210, 255), (255, 110, 110), (255, 240, 200)])
        B.append(Box((rnd.uniform(-3.4, 3.4), 8.6, rnd.uniform(.6, 3.6)), (.26, .1, .26), c, glow=True, glowk=2.2, shadow=False, rad=.04))
    B.append(Box((.5, 1.55, .36), (3.4, .06, .72), (92, 64, 44)))                                                  # передняя панель стола
    B += [Box((.5, 2.0, .72), (3.4, 1.0, .07), (112, 78, 52), gloss=.2), Box((-1.1, 1.65, .36), (.1, .1, .72), (80, 56, 40)), Box((2.1, 1.65, .36), (.1, .1, .72), (80, 56, 40)),
          Box((-1.1, 2.35, .36), (.1, .1, .72), (80, 56, 40)), Box((2.1, 2.35, .36), (.1, .1, .72), (80, 56, 40))]       # стол
    B += [Box((1.35, 2.9, 1.1), (.9, .06, .56), (12, 16, 28), img=code_img(), glow=True, glowk=1.3), Box((1.35, 2.9, .9), (.08, .08, .2), (50, 50, 60)),
          Box((1.2, 2.2, .77), (.7, .24, .03), (40, 42, 52))]                              # монитор и клавиатура
    B += [Box((-1.0, 2.25, .9), (.06, .06, .36), (60, 60, 70)), Box((-.9, 2.2, 1.1), (.28, .08, .06), (255, 214, 120), glow=True, glowk=1.6)]   # лампа
    B += [Box((.4, 1.75, .8), (.2, .2, .14), (236, 232, 224), rad=.02), Box((.4, 1.75, .875), (.16, .16, .015), (74, 46, 30))]                  # кружка кофе
    B += [Box((-.45, 1.7, .75), (.18, .18, .01), (255, 232, 120)), Box((1.0, 1.65, .75), (.18, .18, .01), (255, 150, 170))]                      # стикеры
    return B
def night_dyn(st):
    B = cl(st, (.02, 1.95, .74), .25, k=.62)
    B += pe(st, "boy", (.78, 2.7, .36), 0, k=1.12, hat="none", hair=(70, 50, 40), top=(238, 196, 48), sleeves=(238, 196, 48), bottom=(60, 66, 100))
    return B
night_lights = lambda: Lights(sun_dir=(-.3, -.6, .6), sun=(.34, .4, .7), sky=(.34, .4, .66), ground=(.26, .22, .22), fill=(.3, .34, .5),
                              points=[((-.9, 2.1, 1.15), (1.0, .72, .38), 3.4), ((1.4, 1.9, 1.0), (.42, .62, 1.0), 2.2), ((.5, 1.0, 1.5), (.9, .72, .55), 1.6)])
CAM_W = lambda: Camera((.45, -.4, 1.45), (.45, 2.4, 1.0), fov=48)       # общий план
CAM_B = lambda: Camera((.78, .3, 1.3), (.78, 2.6, 1.25), fov=38)       # крупно мальчик
CAM_C = lambda: Camera((-.05, .2, 1.1), (-.1, 2.0, .93), fov=38)        # крупно Клод
REG = (-3, 3.5, -.2, 4.6, -.3, 3.6)

def _sc(name, cam, lines, final=False, **kw):
    d = dict(name=name, tag=None, static=night_static, dyn=night_dyn, camera=cam, lights=night_lights, region=REG, dof=(2.2, 3.2), lines=lines, **kw)
    if final: d["final"] = True
    return d
B_, C_ = "boy", "claude"
SCENES = [
    _sc("n1", CAM_W, [(B_, "Клод, заказчик прислал правки."), (C_, "Читай."), (B_, "Первое: сделай логотип больше."), (C_, "Сделано."),
                      (B_, "Второе: чтобы он не бросался в глаза."), (C_, "Это противоречит первому."), (B_, "Я знаю.")]),
    _sc("n2", CAM_C, [(B_, "Третье: добавь воздуха, но ничего не убирай."), (C_, "Воздух — это пустое место. А ничего не убирать — это всё оставить."), (B_, "Именно.")]),
    _sc("n3", CAM_B, [(B_, "Четвёртое: сделай по-другому, но как раньше."), (C_, "Давай я покажу ему все версии сразу."), (B_, "Как же всё это согласовать?")]),
    _sc("n4", CAM_W, [(C_, "Это не ко мне. Я сделаю любой вариант. Но решить, чего хочет заказчик, — работа человека."), (B_, "Тогда позвоню ему.")]),
    _sc("n5", CAM_C, [(B_, "Алло. Мы всё сделали, как вы просили."), ("client", "Ой, а я ничего не просил. Мне просто было интересно, что получится."), (C_, "Вот и вся работа.")]),
    _sc("n6", CAM_W, [(B_, "Клод, а что я ему отвечу?"), (C_, "Что получилось отлично. Какую самую нелепую правку тебе присылали? Пиши в комментариях. Отправь тому, кто так ставит задачи. Подпишись.")], final=True),
]

from PIL import ImageFont
def _f(sz, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)
def overlay(sc, t, fr):
    """Номер правки крупно на репликах «Первое… Четвёртое»."""
    d = ImageDraw.Draw(fr); nums = {"Первое": 1, "Второе": 2, "Третье": 3, "Четвёртое": 4}
    for who, text, st, dur, a in sc["tl"]:
        for w, n in nums.items():
            if text.startswith(w + ":") and st <= t < st + dur + .8:
                tx = f"ПРАВКА № {n}"; ft = _f(84); tw = d.textlength(tx, font=ft)
                d.rounded_rectangle(((1080 - tw) / 2 - 44, 330, (1080 + tw) / 2 + 44, 460), 40, fill=(255, 214, 80, 245)); d.text((540, 395), tx, font=ft, fill=(30, 24, 20, 255), anchor="mm")
