"""Ролик «Клод: сколько осталось от зарплаты римского солдата?» (сценарий — reels/scripts/claude_salary.md). Запуск: SCENES=scenes_salary python3 video.py ..."""
import random, math, numpy as np
from cuberender import Box, Camera, Lights, fbm
from cast import claude, person, _place
import props
from scenes import (sand, logs, gradient, cl, pe, G, CAM, CAM2, room_static, room_dyn, room_lights, LINE as _LINE)
import scenes as S0

PLATE = "СКОЛЬКО ОСТАЛОСЬ ОТ ЗАРПЛАТЫ\nРИМСКОГО СОЛДАТА?"
LINE = dict(_LINE); LINE["legion"] = dict(speaker=3, rate=.92, pitch=.84)
MUSIC = None

def legion_boxes(st, pos, yaw, k=1.0):
    B = pe(st, "legion", pos, yaw, k=k, hat="helmet", top=(184, 44, 40), sleeves=(184, 44, 40), bottom=(228, 166, 132), shoes=(110, 70, 44), hair=(80, 56, 40),
           trim=(120, 30, 28))
    B.append(Box(_place(pos, yaw, (-.42 * k, -.12 * k, .55 * k)), (.46 * k, .07 * k, .66 * k), (172, 34, 34), yaw, decals=[(-.18, .18, -.14, .14, (232, 190, 60))], rad=.03, gloss=.3))
    return B

def strata(p, ax, sgn, col):
    z = p[:, 2]; out = col * (0.9 + .14 * fbm(p[:, 0] * 3, z * 7, 4)[:, None]); out[(np.abs((z / .22) % 1 - .5) > .46)] *= .78; return out

def tent(x, y, w=1.1, h=.7, col=(222, 206, 170)):
    return [Box((x, y, h / 2), (w, w * 1.1, h), col, rad=.05), Box((x, y, h + .12), (w * .8, w * .9, .26), tuple(int(c * .93) for c in col), rad=.08),
            Box((x, y - w * .56, h * .45), (w * .3, .04, h * .8), (80, 60, 44))]

# ---------- Масада ----------
def masada_static():
    B = [Box((0, 12, 3), (60, .2, 14), (170, 200, 235), tex=gradient((110, 160, 225), (250, 226, 190), 0, 5), glow=True, glowk=.95),
         Box((0, 3, -.1), (30, 10, .2), (226, 190, 124), tex=sand),
         Box((-.3, 7.2, 1.7), (10, 3.6, 3.4), (168, 120, 84), tex=strata), Box((-.3, 7.2, 3.6), (9.4, 3.2, .4), (200, 176, 140), tex=strata),
         Box((-.3, 5.5, 3.95), (9.4, .25, .5), (220, 200, 168))]
    B += tent(-1.7, 3.5) + tent(2.5, 3.7, 1.2) + tent(-.6, 4.3, 1.0) + tent(1.5, 4.6, 1.0)
    for x in (-1.2, .1, 1.3, 2.3): B.append(Box((x, 2.9, .4), (.08, .08, .8), (110, 74, 50)))
    B += [Box((.1, 2.35, .5), (.05, .05, 1.0), (110, 74, 50)), Box((.9, 2.35, .5), (.05, .05, 1.0), (110, 74, 50)),
          Box((.5, 2.3, 1.1), (.9, .05, 1.0), (238, 220, 170), img=props.payslip(), rad=.01)]
    return B
def masada_dyn(st):
    return cl(st, (-.1, 1.55, 0), .3, k=.72) + legion_boxes(st, (1.0, 1.8, 0), -.35)
masada_lights = lambda: Lights(sun_dir=(-.5, -.35, .8), sun=(1.0, .9, .72), sky=(.55, .66, .92), ground=(.62, .5, .34), fill=(.22, .22, .26))

# ---------- Паннония, 14 г. ----------
def pann_static():
    B = [Box((0, 12, 3), (60, .2, 14), (160, 176, 205), tex=gradient((120, 140, 180), (214, 214, 214), 0, 5), glow=True, glowk=.9),
         Box((0, 3, -.1), (30, 10, .2), (110, 128, 72), tex=sand)]
    for x in np.arange(-3, 3.6, .32): B.append(Box((x, 3.6, .8), (.28, .28, 1.6 + (.1 if int(x * 10) % 2 else 0)), (122, 86, 56), tex=logs))   # частокол
    B.append(Box((.4, 3.55, 1.65), (7, .3, .12), (110, 76, 50)))
    B += tent(-1.6, 3.0, 1.1, col=(214, 200, 168)) + tent(2.4, 3.1, 1.2, col=(214, 200, 168))
    for (x, y) in [(-2.4, 5.5), (2.9, 5.2), (.4, 6.2)]:                                   # кубические деревья
        B += [Box((x, y, .6), (.3, .3, 1.2), (96, 66, 44)), Box((x, y, 1.6), (1.4, 1.4, 1.1), (178, 120, 52), rad=.08), Box((x, y, 2.4), (1.0, 1.0, .7), (196, 138, 60), rad=.08)]
    B += [Box((.55, 2.3, .26), (.7, .5, .52), (130, 90, 60), gloss=.1)]
    for i in range(10): B.append(Box((.55 - .29 + i * .065, 2.3, .56), (.055, .055, .04), (190, 118, 56), gloss=.5, rad=.01))   # десять медных монет
    return B
def pann_dyn(st):
    return cl(st, (-.1, 1.55, 0), .3, k=.72) + legion_boxes(st, (1.0, 1.8, 0), -.35)
pann_lights = lambda: Lights(sun_dir=(-.4, -.4, .6), sun=(.95, .88, .78), sky=(.6, .66, .82), ground=(.46, .42, .30), fill=(.2, .22, .28))

# ---------- Ночь затмения ----------
def night_static():
    B = [Box((0, 12, 3), (60, .2, 14), (20, 28, 60), tex=gradient((10, 14, 38), (46, 54, 96), 0, 5), glow=True, glowk=.9),
         Box((0, 3, -.1), (30, 10, .2), (40, 52, 46), tex=sand), Box((.4, 8, 4.0), (1.5, .1, 1.5), (200, 50, 34), glow=True, glowk=1.5)]
    rnd = random.Random(5)
    for _ in range(40): B.append(Box((rnd.uniform(-4, 5), 9, rnd.uniform(.8, 5)), (.05, .05, .05), (255, 244, 200), glow=True, shadow=False))
    for x in np.arange(-3, 3.6, .32): B.append(Box((x, 3.6, .8), (.28, .28, 1.6 + (.1 if int(x * 10) % 2 else 0)), (70, 52, 40), tex=logs))
    B += tent(-1.7, 3.0, 1.1, col=(120, 114, 100)) + tent(2.5, 3.1, 1.2, col=(120, 114, 100))
    B += [Box((.5, 2.2, .06), (.5, .5, .12), (60, 50, 44)), Box((.5, 2.2, .2), (.2, .2, .22), (255, 150, 50), glow=True, glowk=3.0)]   # костёр
    return B
def night_dyn(st):
    return cl(st, (-.1, 1.55, 0), .3, k=.72) + legion_boxes(st, (1.0, 1.8, 0), -.35)
night_lights = lambda: Lights(sun_dir=(.3, -.2, .7), sun=(.30, .36, .62), sky=(.16, .20, .36), ground=(.10, .08, .08), fill=(.08, .10, .18),
                             points=[((.5, 2.0, .6), (1.6, .8, .32), 3.0)])

def final_dyn(st):
    return room_dyn(st)

SCENES = [
    dict(name="room_a", tag=None, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5),
         lines=[("boy", "Клод, сколько оставалось от зарплаты римского солдата?"), ("claude", "У нас сохранился его настоящий расчётный листок. Смотри, что с него вычли, а ответ — в конце.")]),
    dict(name="masada", tag="МАСАДА  ·  73 г.", static=masada_static, dyn=masada_dyn, camera=CAM2, lights=masada_lights, region=(-3, 3.5, -.2, 8, -.3, 5), dof=(3.6, 2.4),
         lines=[("legion", "Мне начислили пятьдесят денариев."), ("claude", "Минус еда. Минус ячмень. Минус сапоги. Минус ремни. Минус рубаха."),
                ("legion", "Это всё?"), ("claude", "Это только половина истории.")]),
    dict(name="pann", tag="ПАННОНИЯ  ·  14 г.", static=pann_static, dyn=pann_dyn, camera=CAM2, lights=pann_lights, region=(-3, 3.5, -.2, 6.5, -.3, 3.5), dof=(3.4, 1.8),
         lines=[("claude", "За шестьдесят лет до него солдаты уже жаловались. Десять медных монет в день. Из них одежда, оружие, палатка и взятка командиру."),
                ("legion", "Узнаёшь свою зарплату?"),
                ("claude", "Если у тебя есть друг, у которого деньги кончаются раньше м+есяца, — отправь ему это прямо сейчас.")]),
    dict(name="night", tag="ПАННОНИЯ  ·  ночь затмения", static=night_static, dyn=night_dyn, camera=CAM2, lights=night_lights, region=(-3, 3.5, -.2, 9, -.3, 5), dof=(3.4, 1.8),
         lines=[("claude", "Тогда солдаты подняли бунт. Но случилось лунное затмение. Они испугались, что боги недовольны, и вернулись в строй.")]),
    dict(name="room_end", tag=None, final=True, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5),
         lines=[("boy", "А сколько осталось в итоге?"), ("claude", "Из пятидесяти денариев — почти ничего. Две тысячи лет, а вычеты всё те же."),
                ("boy", "Клод, не напоминай."), ("claude", "Отправь другу, у которого зарплата кончается раньше м+есяца. Подпишись — тут история смешнее, чем в учебнике.")]),
]
