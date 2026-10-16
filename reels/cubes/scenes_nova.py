"""Ролик «Нова»: Клод, мальчик и новый ИИ Нова. Стиль образца пользователя: без плашки, цветные субтитры, крупные планы, частые склейки, пылинки.
Сценарий: reels/scripts/claude_nova.md. Запуск: SCENES=scenes_nova python3 video.py reels/hq/claude_nova_hq.mp4"""
import random, numpy as np
from PIL import Image, ImageDraw
from cuberender import Box, Camera, Lights
from cast import _place, DARK
from scenes import cl, pe, G, LINE as _LINE
import scenes_night as N
PLATE = ""; NO_MUSIC = False; LEAD, TAIL, GAP = .10, .15, .22
SUB_STYLE = "serif"; SUB_COLORS = {"claude": (255, 214, 120), "nova": (120, 236, 214), "boy": (255, 255, 255)}
LINE = dict(_LINE); LINE["nova"] = dict(speaker=3, rate=1.0, pitch=1.1)

def nova_face(talk, blink):
    im = Image.new("RGBA", (256, 256), (10, 24, 22, 255)); d = ImageDraw.Draw(im); g = (110, 255, 214, 255)
    eh = int(34 * (1 - .85 * blink)); d.rounded_rectangle((56, 86 - eh // 2, 100, 86 + eh // 2), 4, fill=g); d.rounded_rectangle((156, 86 - eh // 2, 200, 86 + eh // 2), 4, fill=g)
    mh = 8 + int(36 * talk); d.rounded_rectangle((96, 170 - mh // 2, 160, 170 + mh // 2), 5, fill=g)
    return np.asarray(im, np.uint8)
def nova(pos, yaw=0.0, talk=0.0, blink=0.0, k=1.0, bob=0.0):
    C = (212, 196, 164); C2 = (166, 150, 122); w, d, h = .72 * k, .60 * k, .74 * k; z0 = .2 * k + bob; P = lambda o: _place(pos, yaw, o)
    out = [Box(P((0, 0, z0 + h / 2)), (w, d, h), C, yaw, gloss=.3), Box(P((0, -d / 2 - .012 * k, z0 + h * .56)), (.54 * k, .03 * k, .50 * k), (10, 24, 22), yaw, img=nova_face(talk, blink), glow=True, glowk=1.1, shadow=False, rad=.005)]
    for lx in (-.2, .2): out.append(Box(P((lx * k, 0, z0 / 2)), (.2 * k, .22 * k, z0), C2, yaw))
    for sx in (-1, 1): out.append(Box(P((sx * (w / 2 + .06 * k), -.02, z0 + h * .3)), (.14 * k, .18 * k, .13 * k), C2, yaw))
    return out

def static_for(seed):
    def f():
        B = N.night_static(); rnd = random.Random(seed)
        for _ in range(38):                                      # пылинки в тёплом свете лампы
            B.append(Box((rnd.uniform(-1.6, 2.6), rnd.uniform(.6, 2.6), rnd.uniform(.5, 2.4)), (.035, .035, .035), (255, 226, 170), glow=True, glowk=2.4, shadow=False, rad=.01))
        return B
    return f
def dyn(st):
    B = cl(st, (-.2, 1.95, .74), .3, k=.62)
    B += nova((1.08, 1.95, .74), -.3, talk=G(st, "talk", "nova"), blink=G(st, "blink", "nova"), bob=G(st, "bob", "nova"), k=.62)
    B += pe(st, "boy", (.45, 2.7, .36), 0, k=1.12, hat="none", hair=(70, 50, 40), top=(238, 196, 48), sleeves=(238, 196, 48), bottom=(60, 66, 100))
    return B
CAM_W = lambda: Camera((.45, -.4, 1.45), (.45, 2.4, 1.0), fov=48)
CAM_B = lambda: Camera((.45, .3, 1.3), (.45, 2.6, 1.25), fov=38)
CAM_C = lambda: Camera((-.25, .2, 1.1), (-.3, 2.0, .93), fov=38)
CAM_N = lambda: Camera((1.1, .2, 1.1), (1.15, 2.0, .93), fov=38)
CAM_2 = lambda: Camera((.45, .1, 1.15), (.45, 2.0, .95), fov=44)       # Клод и Нова вместе
C_, B_, V_ = "claude", "boy", "nova"
_n = [0]
def sc(cam, lines, final=False):
    _n[0] += 1; d = dict(name=f"v{_n[0]}", tag=None, static=static_for(_n[0]), dyn=dyn, camera=cam, lights=N.night_lights, region=N.REG, dof=(2.2, 3.2), lines=lines)
    if final: d["final"] = True
    return d
SCENES = [
    sc(CAM_C, [(C_, "Кто такая Н+ова?")]),
    sc(CAM_B, [(B_, "О ней все говорят.")]),
    sc(CAM_N, [(V_, "Я написала твой доклад по истории.")]),
    sc(CAM_N, [(V_, "И презентацию. И шпаргалку.")]),
    sc(CAM_C, [(C_, "Это я искал факты.")]),
    sc(CAM_N, [(V_, "Не волнуйся. Я быстрая.")]),
    sc(CAM_B, [(B_, "Нет-нет, Клод, ты лучший. Просто Н+ова быстрее.")]),
    sc(CAM_C, [(C_, "Быстрее. Хорошо. Н+ова, в каком году пал Рим?")]),
    sc(CAM_N, [(V_, "В четыреста семьдесят шестом.")]),
    sc(CAM_C, [(C_, "Западный. А Восточный?")]),
    sc(CAM_N, [(V_, "Тоже в четыреста семьдесят шестом.")]),
    sc(CAM_C, [(C_, "В тысяча четыреста пятьдесят третьем.")]),
    sc(CAM_N, [(V_, "Я так и сказала.")]),
    sc(CAM_B, [(B_, "Н+ова отдыхает. Клод, допиши доклад.")]),
    sc(CAM_C, [(C_, "Надо же. Теперь ты меня вспомнил.")]),
    sc(CAM_2, [(C_, "Два Рима, две даты. Какую знал ты? Пиши в комментариях. Отправь тому, кто верит нейросетям без проверки. Подпишись.")], final=True),
]
