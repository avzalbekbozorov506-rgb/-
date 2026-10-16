"""Сцены для роликов про автомобили: «Кто такая Мерседес?» (scenes_merc) и «Логотип БМВ — пропеллер? Миф» (scenes_bmw). Сценарии — reels/scripts/claude_cars.md."""
import random, numpy as np
from cuberender import Box, Camera, Lights, fbm
from cast import claude, person, car, _place
import props
from scenes import (sand, logs, gradient, cl, pe, G, CAM, CAM2, room_static, room_dyn, room_lights, planks, LINE as _LINE)

LINE = dict(_LINE); LINE["jellinek"] = dict(speaker=3, rate=.93, pitch=.92); LINE["adman"] = dict(speaker=2, rate=.96, pitch=.88); LINE["worker"] = dict(speaker=3, rate=.95, pitch=.98)

def stone(p, ax, sgn, col):
    cx, cy = np.floor(p[:, 0] / .5), np.floor(p[:, 1] / .5); out = col * (0.92 + .12 * ((np.sin(cx * 12.9 + cy * 78.2) * 43758.5) % 1))[:, None]
    out[(np.abs((p[:, 0] / .5) % 1 - .5) > .47) | (np.abs((p[:, 1] / .5) % 1 - .5) > .47)] *= .75; return out
def asphalt(p, ax, sgn, col): return col * (0.9 + .14 * fbm(p[:, 0] * 8, p[:, 1] * 8, 4)[:, None])
def checker(p, ax, sgn, col):
    c = (np.floor(p[:, 0] / .3) + np.floor(p[:, 1] / .3)) % 2; out = col.copy(); out[c == 1] = (240, 240, 244); out[c == 1] = out[c == 1] / 255; return out
def bricks(p, ax, sgn, col):
    z = p[:, 2]; row = np.floor(z / .14); x = p[:, 0] + (row % 2) * .12
    out = col * (0.88 + .22 * ((np.sin(np.floor(x / .24) * 7.3 + row * 3.1) * 4375.5) % 1))[:, None]
    out[(np.abs((z / .14) % 1 - .5) > .45) | (np.abs((x / .24) % 1 - .5) > .46)] *= .6; return out
def lozenge(p, ax, sgn, col):
    u, v = p[:, 0] + p[:, 2], p[:, 0] - p[:, 2]; c = (np.floor(u / .24) + np.floor(v / .24)) % 2
    out = np.where(c[:, None] == 0, np.array([40, 100, 190], np.float32) / 255, np.array([244, 244, 248], np.float32) / 255); return out.astype(np.float32)
def panel(img, x, y, z, w, h): return Box((x, y, z), (w, .05, h), (236, 224, 196), img=img, rad=.01)
def easel(x, y, img, w, h, z0=.5):
    return [Box((x - w / 2 + .05, y + .02, z0 / 2 + .02), (.05, .05, z0 + .1), (110, 74, 50)), Box((x + w / 2 - .05, y + .02, z0 / 2 + .02), (.05, .05, z0 + .1), (110, 74, 50)), panel(img, x, y, z0 + h / 2 + .05, w, h)]
def palm(x, y, s=1.0):
    return [Box((x, y, .8 * s), (.18 * s, .18 * s, 1.6 * s), (120, 90, 60)), Box((x, y, 1.7 * s), (1.3 * s, .12 * s, .16 * s), (60, 140, 70)), Box((x, y, 1.78 * s), (.12 * s, 1.3 * s, .16 * s), (50, 126, 62)),
            Box((x, y, 1.62 * s), (.9 * s, .9 * s, .1 * s), (70, 150, 78))]
def crowd(xs, y, z0, rnd, cols, k=.26):
    B = []
    for x in xs:
        B += person((x, y, z0), yaw=rnd.uniform(-.3, .3), k=k, top=rnd.choice(cols), bottom=rnd.choice([(60, 60, 80), (90, 70, 50)]), hat=rnd.choice(["cap", "bowler", "none"]), hair=(70, 52, 40))
    return B
SK = (228, 166, 132)
def jel(st, pos, yaw, **kw): return pe(st, "jellinek", pos, yaw, k=1.0, top=(40, 40, 52), sleeves=(40, 40, 52), bottom=(52, 50, 60), trim=(240, 240, 244), hat="topper", mustache=True, shoes=(30, 26, 26), hair=(60, 44, 32), **kw)
def adm(st, pos, yaw, **kw): return pe(st, "adman", pos, yaw, top=(110, 114, 124), sleeves=(110, 114, 124), bottom=(96, 98, 108), trim=(180, 50, 50), hat="bowler", shoes=(40, 34, 30), hair=(50, 40, 34), **kw)
def clerk(st, pos, yaw): return pe(st, "clerk", pos, yaw, top=(236, 232, 220), sleeves=(236, 232, 220), bottom=(70, 70, 86), trim=(40, 40, 52), hat="bowler", shoes=(40, 34, 30), hair=(50, 40, 34))
def worker(st, pos, yaw): return pe(st, "worker", pos, yaw, top=(70, 94, 140), sleeves=(70, 94, 140), bottom=(60, 64, 76), trim=(210, 190, 140), hat="cap", hatcol=(120, 110, 100), shoes=(60, 44, 34), hair=(70, 52, 40))

# ---------- Ницца: набережная (1900) ----------
def nice_static():
    B = [Box((0, 12, 3), (60, .2, 14), (150, 200, 240), tex=gradient((100, 160, 230), (250, 232, 200), 0, 5), glow=True, glowk=.95), Box((0, 8, .0), (40, 6, .2), (50, 130, 190), glow=True, glowk=.85),
         Box((0, 2.4, -.1), (30, 5.6, .2), (222, 210, 184), tex=stone), Box((0, 5.5, .12), (30, .5, .3), (190, 180, 160))]
    for x, w, h, c in [(-2.4, 1.3, 2.2, (232, 210, 170)), (-1.0, 1.1, 2.7, (236, 190, 160)), (2.2, 1.3, 2.4, (222, 220, 196)), (3.4, 1.2, 2.0, (232, 200, 170))]:
        B.append(Box((x, 4.2, h / 2), (w, 1.1, h), c, rad=.06))
        for wy in (.7, 1.4): B.append(Box((x, 3.64, wy + .6), (.32, .04, .5), (70, 100, 150), glow=True, glowk=.6))
    B += palm(-1.7, 3.2, 1.0) + palm(2.0, 3.4, 1.1) + palm(.4, 4.6, .9)
    B += car((-1.9, 2.4, 0), yaw=.1, k=.9, num=True)
    return B
def nice_dyn(st): return cl(st, (-.05, 1.55, 0), .3, k=.72) + jel(st, (1.05, 1.8, 0), -.35)
nice_lights = lambda: Lights(sun_dir=(-.5, -.4, .75), sun=(1.0, .9, .74), sky=(.56, .68, .92), ground=(.60, .52, .40), fill=(.22, .24, .28))

# ---------- Ницца: гонки (1901) ----------
def race_static():
    rnd = random.Random(7)
    B = [Box((0, 12, 3), (60, .2, 14), (150, 200, 240), tex=gradient((100, 160, 230), (250, 232, 200), 0, 5), glow=True, glowk=.95), Box((0, 3, -.1), (30, 10, .2), (84, 84, 92), tex=asphalt),
         Box((.5, 2.9, .0), (14, .6, .04), (240, 240, 244), tex=checker, shadow=False)]
    for r, z in enumerate((.5, .95)):
        B.append(Box((.4, 4.0 + r * .6, z - .25), (9, .5, .5 + r * .5), (150, 120, 84)))
        B += crowd(np.arange(-3.6, 4.4, .55), 3.95 + r * .6, z, rnd, [(200, 60, 60), (60, 100, 170), (220, 200, 120), (90, 150, 90)])
    for x in (-2.6, -.5, 1.6, 3.4): B += [Box((x, 3.4, 1.0), (.05, .05, 2.0), (230, 230, 236)), Box((x + .25, 3.4, 1.8), (.5, .03, .3), (200, 50, 50))]
    B += easel(.0, 2.4, props.newspaper(), .9, 1.1, z0=.55)
    B += car((-2.2, 2.2, 0), yaw=.05, k=.9, num=True)
    return B
def race_dyn(st): return cl(st, (-.05, 1.55, 0), .3, k=.72) + jel(st, (1.05, 1.8, 0), -.35, arm=.9)

# ---------- Контора: документы ----------
def office_static():
    B = [Box((0, 3.2, 1.6), (9, .2, 4), (112, 78, 52), tex=planks), Box((0, 1.2, -.1), (9, 6.2, .2), (140, 100, 68), tex=planks), Box((-2.9, 1.2, 1.6), (.2, 6.2, 4), (100, 70, 48)),
         Box((.5, 2.6, .72), (2.4, .9, .08), (96, 64, 42), gloss=.2)]
    for sx in (-1, 1):
        for sy in (-1, 1): B.append(Box((.5 + sx * 1.1, 2.6 + sy * .36, .34), (.1, .1, .68), (80, 54, 38)))
    B += [Box((-.5, 2.6, .8), (.3, .22, .08), (240, 232, 210)), Box((-.5, 2.6, .86), (.04, .04, .1), (250, 250, 250)), Box((1.5, 2.55, .8), (.2, .2, .05), (60, 60, 70)), Box((1.5, 2.55, 1.02), (.04, .04, .4), (60, 60, 70)), Box((1.5, 2.48, 1.26), (.26, .24, .16), (255, 214, 120), glow=True)]
    B += [Box((-1.7, 3.08, 1.7), (.9, .04, 1.1), (160, 120, 80)), Box((-1.7, 3.05, 1.7), (.7, .03, .9), (90, 130, 170))]
    return B
def docs_static(img):
    return lambda: office_static() + [panel(img, .0, 2.2, 1.1, .95, 1.15), Box((-.4, 2.2, .5), (.04, .04, .9), (110, 74, 50)), Box((.4, 2.2, .5), (.04, .04, .9), (110, 74, 50))]
def office_dyn(st): return cl(st, (-.05, 1.55, 0), .3, k=.72) + jel(st, (1.05, 1.8, 0), -.35)
office_lights = lambda: Lights(sun_dir=(-.5, -.4, .6), sun=(.9, .8, .66), sky=(.44, .42, .40), ground=(.36, .28, .22), fill=(.14, .14, .18), points=[((1.5, 2.3, 1.2), (1.0, .72, .38), 2.4)])

# ---------- Мюнхен: цех (1917) ----------
def shop_static():
    B = [Box((0, 3.3, 1.6), (9, .4, 3.4), (150, 84, 62), tex=bricks), Box((0, 1.2, -.1), (9, 6.2, .2), (120, 118, 116), tex=asphalt), Box((-2.9, 1.2, 1.6), (.2, 6.2, 3.4), (140, 80, 60), tex=bricks),
         Box((-1.6, 3.08, 1.8), (1.1, .04, .9), (230, 236, 244), glow=True, glowk=1.2), Box((-1.6, 3.05, 1.8), (1.2, .06, .06), (60, 50, 44)), Box((-1.6, 3.05, 1.8), (.06, .06, 1.0), (60, 50, 44)),
         Box((1.9, 3.08, 1.5), (1.2, .04, 1.6), (200, 200, 204), tex=lozenge)]
    B += [Box((.5, 3.05, 2.5), (1.5, .06, .12), (100, 100, 108)), Box((.5, 3.05, 2.5), (.12, .06, 1.2), (100, 100, 108))]   # пропеллер на стене
    B += easel(.0, 2.4, props.sign_bmw(), 1.1, .65, z0=.8)
    for x in (-1.9, 2.6):                                                                      # моторы на столах
        B += [Box((x, 2.4, .35), (.9, .6, .7), (110, 86, 64)), Box((x, 2.4, .85), (.5, .4, .3), (90, 94, 104), gloss=.6)]
        for i in range(5): B.append(Box((x - .22 + i * .11, 2.4, 1.1), (.07, .07, .22), (140, 144, 152), gloss=.6))
    return B
def shop_dyn(st): return cl(st, (-.05, 1.55, 0), .3, k=.72) + worker(st, (1.05, 1.8, 0), -.35)
shop_lights = lambda: Lights(sun_dir=(-.4, -.5, .7), sun=(.95, .88, .78), sky=(.50, .52, .60), ground=(.40, .34, .30), fill=(.18, .18, .22))

# ---------- Реклама (1929) ----------
def ad_static():
    B = [Box((0, 12, 3), (60, .2, 14), (170, 200, 235), tex=gradient((110, 160, 225), (250, 232, 205), 0, 5), glow=True, glowk=.95), Box((0, 3, -.1), (30, 10, .2), (150, 148, 144), tex=stone),
         Box((-2.2, 4.6, 1.2), (1.6, 1.1, 2.4), (200, 170, 140), rad=.06), Box((3.0, 4.8, 1.5), (1.8, 1.2, 3.0), (180, 170, 160), rad=.06)]
    B += easel(.0, 2.8, props.ad_poster(), 1.4, 1.0, z0=.9)
    return B
def ad_dyn(st): return cl(st, (-.05, 1.55, 0), .3, k=.72) + adm(st, (1.05, 1.8, 0), -.35)
ad_lights = nice_lights

# ---------- Все сцены ----------
def _room(name, lines, final=False):
    d = dict(name=name, tag=None, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5), lines=lines)
    if final: d["final"] = True
    return d
def _sc(name, tag, st, dyn, cam, li, lines, reg=(-3, 3.5, -.2, 6, -.3, 4), dof=(3.4, 2.0)):
    return dict(name=name, tag=tag, static=st, dyn=dyn, camera=cam, lights=li, region=reg, dof=dof, lines=lines)

SCENES_MERC = [
    _room("m_room_a", [("boy", "Клод, кто такая Мерседес?"), ("claude", "Девочка. Ей было десять лет. И из-за неё ты сегодня ездишь на мерседесе. Сначала про её отца.")]),
    _sc("m_nice", "НИЦЦА  ·  1900 г.", nice_static, nice_dyn, CAM2, nice_lights,
        [("claude", "Эмиль Еллинек торговал автомобилями и сам ездил в гонки. Под псевдонимом Мерседес. Так звали его дочь."), ("jellinek", "Пусть на финише кричат её имя.")]),
    _sc("m_race", "НИЦЦА  ·  март 1901 г.", race_static, race_dyn, CAM2, nice_lights,
        [("claude", "В марте тысяча девятьсот первого года новая машина фирмы Даймлер выиграла гонки в Ницце. И газеты назвали её Мерседес.")]),
    _sc("m_docs", "ПАРИЖ  ·  1902–1903 гг.", docs_static(props.docs_merc()), office_dyn, CAM2, office_lights,
        [("claude", "В тысяча девятьсот втором году имя зарегистрировали как торговую марку. А в тысяча девятьсот третьем сам Еллинек официально стал Еллинек-Мерседес."), ("jellinek", "Фамилия дочери. Теперь она и моя.")]),
    _room("m_room_end", [("boy", "То есть я езжу на девочке?"), ("claude", "Ты едешь на имени десятилетней девочки из Ниццы. Отправь другу, который ездит на мерседесе: пусть знает, как её звали. Подпишись — тут история смешнее, чем в учебнике.")], final=True),
]
SCENES_BMW = [
    _room("b_room_a", [("boy", "Клод, логотип БМВ — это же пропеллер?"), ("claude", "Так думает полмира. Это миф. Сейчас узнаешь, кто его придумал.")]),
    _sc("b_shop", "МЮНХЕН  ·  1917 г.", shop_static, shop_dyn, CAM2, shop_lights,
        [("claude", "Компания начинала с авиационных моторов, поэтому в пропеллер так легко поверили. Но синий и белый на эмблеме — это цвета Бав+арии."), ("worker", "Моторы для самолётов — наша работа.")], reg=(-3, 3.5, -.2, 4, -.3, 4)),
    _sc("b_ad", "ГЕРМАНИЯ  ·  1929 г.", ad_static, ad_dyn, CAM2, ad_lights,
        [("claude", "Миф родился в рекламе. Эмблема там вращается внутри пропеллера: фирма продавала авиационные моторы."), ("adman", "Красиво же?"),
         ("claude", "Красиво. Настолько, что в это поверила и сама компания, и повторила в своём журнале.")]),
    _sc("b_flag", "МЮНХЕН  ·  1917 г.", docs_static(props.flag_vs_emblem()), office_dyn, CAM2, office_lights,
        [("claude", "А теперь самое странное. Цвета на эмблеме стоят в обратном порядке, чем на флаге Бав+арии. Закон тех лет запрещал использовать государственные знаки в торговой марке.")]),
    _room("b_room_end", [("boy", "Значит, я всю жизнь верил рекламе?"), ("claude", "Как и все. Отправь другу-бээмвэшнику, который знал это наверняка. Подпишись — тут история смешнее, чем в учебнике.")], final=True),
]
