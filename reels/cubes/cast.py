"""Персонажи-кубики: Клод (кирпично-красный) и мальчик. Каждый — список Box. pos=(x,y,z пола), yaw — поворот вокруг Z."""
import math, numpy as np
from cuberender import Box

def _place(pivot, yaw, off):          # смещение off в кадре персонажа -> мир
    c, s = math.cos(yaw), math.sin(yaw)
    return (pivot[0] + off[0] * c - off[1] * s, pivot[1] + off[0] * s + off[1] * c, pivot[2] + off[2])

DARK = (38, 30, 34)

def claude(pos, yaw=0.0, talk=0.0, blink=0.0, k=1.0, bob=0.0):
    """Клод: широкое кирпичное тело, 4 ножки, ручки-обрубки, прямоугольные глаза и рот. talk 0..1 — рот, blink 0..1 — глаза."""
    R = (206, 80, 58); R2 = (176, 62, 46)
    w, d, h = .95 * k, .62 * k, .56 * k
    z0 = .22 * k + bob
    eh = .17 * (1 - .9 * blink)                                    # высота глаза
    eyes = [(-.27, -.17, .02 - (.17 - eh) / 2 + .08, .02 + (.17 - eh) / 2 + .08 + eh * 0 + .0, DARK)]
    ey0, ey1 = .10 - eh / 2 + .02, .10 + eh / 2 + .02
    dec = [(-.27, -.20, ey0, ey1, DARK), (.20, .27, ey0, ey1, DARK)]
    mh = .03 + .09 * talk
    dec.append((-.07, .07, -.15 - mh / 2, -.15 + mh / 2, DARK))
    out = [Box(_place(pos, yaw, (0, 0, z0 + h / 2)), (w, d, h), R, yaw, dec, gloss=.35)]
    for lx in (-.34, -.12, .12, .34):                              # ножки
        out.append(Box(_place(pos, yaw, (lx * k, 0, (z0) / 2)), (.18 * k, .20 * k, z0), R2, yaw))
    for sx in (-1, 1):                                             # ручки
        out.append(Box(_place(pos, yaw, (sx * (w / 2 + .06 * k), -.02, z0 + h * .38)), (.14 * k, .18 * k, .13 * k), R2, yaw))
    return out

def boy(pos, yaw=0.0, talk=0.0, blink=0.0, bob=0.0, arm=0.0):
    """Мальчик: кепка, светлый свитер, тёмные брюки, белые кеды. arm 0..1 — поднятая рука."""
    SK = (228, 166, 132); SW = (226, 210, 170); PT = (44, 52, 86); SH = (240, 240, 244); CAP = (190, 184, 168)
    z = bob
    eh = .075 * (1 - .9 * blink)
    dec = [(-.26, -.17, .0 - eh / 2 + .0, .0 + eh / 2, DARK), (.17, .26, .0 - eh / 2, .0 + eh / 2, DARK),
           (-.38, -.24, -.18, -.08, (236, 150, 140)), (.24, .38, -.18, -.08, (236, 150, 140)),
           (-.28, -.15, .12, .15, (110, 78, 60)), (.15, .28, .12, .15, (110, 78, 60))]
    mh = .025 + .09 * talk
    dec.append((-.07, .07, -.30 - mh / 2 + .02, -.30 + mh / 2 + .02, (120, 56, 56)))
    out = []
    P = lambda o: _place(pos, yaw, o)
    out += [Box(P((-.09, 0, .12 + z)), (.15, .17, .24), PT, yaw), Box(P((.09, 0, .12 + z)), (.15, .17, .24), PT, yaw)]
    out += [Box(P((-.09, -.04, .03 + z)), (.17, .27, .07), SH, yaw), Box(P((.09, -.04, .03 + z)), (.17, .27, .07), SH, yaw)]
    out += [Box(P((0, 0, .52 + z)), (.38, .24, .50), SW, yaw)]                     # свитер
    out += [Box(P((0, 0, .27 + z)), (.38, .24, .04), PT, yaw)]
    out += [Box(P((-.26, 0, .50 + z)), (.12, .14, .42), SW, yaw)]                  # левая рука (с нашей стороны) — вниз
    ra = arm
    out += [Box(P((.26, -.03 * ra, .50 + z + .07 * ra)), (.12, .14, .42 - .10 * ra), SW, yaw)]
    out += [Box(P((0, 0, .90 + z)), (.50, .46, .50), SK, yaw, dec)]                 # голова
    out += [Box(P((0, .01, 1.19 + z)), (.54, .50, .10), CAP, yaw, shadow=False)]                  # верх кепки
    out += [Box(P((0, -.30, 1.14 + z)), (.50, .20, .035), CAP, yaw, shadow=False)]                # козырёк
    return out


def person(pos, yaw=0.0, talk=0.0, blink=0.0, bob=0.0, arm=0.0, k=1.0, skin=(228, 166, 132), top=(226, 210, 170), bottom=(44, 52, 86),
           shoes=(240, 240, 244), hair=(96, 66, 44), hat=None, hatcol=(190, 184, 168), skirt=False, bare=False, sleeves=None,
           brows=True, blush=True, trim=None, holding=None, arm_l=0.0):
    """Универсальный кубический человечек (рост ~1.3·k). hat: cap/kerchief/laurel/nemes/kolpak/none. skirt — длинная юбка/сарафан,
    bare — голый торс (набедренная повязка в bottom). holding: ('papyrus'|'bark', img) — предмет в правой руке перед собой."""
    z = bob * k; P = lambda o: _place(pos, yaw, (o[0] * k, o[1] * k, o[2] * k + z))
    S = lambda *a: tuple(v * k for v in a)
    eh = .075 * (1 - .9 * blink)
    dec = [(-.26, -.17, -eh / 2, eh / 2, DARK), (.17, .26, -eh / 2, eh / 2, DARK)]
    if blush: dec += [(-.38, -.24, -.18, -.08, (236, 150, 140)), (.24, .38, -.18, -.08, (236, 150, 140))]
    if brows: dec += [(-.28, -.15, .12, .15, hair), (.15, .28, .12, .15, hair)]
    mh = .025 + .09 * talk
    dec.append((-.07, .07, -.30 - mh / 2 + .02, -.30 + mh / 2 + .02, (120, 56, 56)))
    out = []
    sl = sleeves or top
    if skirt:
        out += [Box(P((0, 0, .26)), S(.56, .40, .50), bottom, yaw, rad=.04 * k)]
        out += [Box(P((0, 0, .03)), S(.20, .24, .06), shoes, yaw), ]
    else:
        out += [Box(P((-.09, 0, .12)), S(.15, .17, .24), bottom if not bare else skin, yaw), Box(P((.09, 0, .12)), S(.15, .17, .24), bottom if not bare else skin, yaw)]
        out += [Box(P((-.09, -.04, .03)), S(.17, .27, .07), shoes, yaw), Box(P((.09, -.04, .03)), S(.17, .27, .07), shoes, yaw)]
    if bare:
        out += [Box(P((0, 0, .52)), S(.38, .24, .50), skin, yaw, gloss=.1), Box(P((0, 0, .25)), S(.40, .27, .26), bottom, yaw)]
        if trim: out += [Box(P((0, -.02, .73)), S(.42, .27, .07), trim, yaw)]
    else:
        out += [Box(P((0, 0, .52)), S(.38, .24, .50), top, yaw)]
        if not skirt: out += [Box(P((0, 0, .27)), S(.38, .24, .04), bottom, yaw)]
        if trim: out += [Box(P((0, -.121, .52)), S(.38, .01, .50), trim, yaw)]
    out += [Box(P((-.26, 0, .50 - arm_l * .0)), S(.12, .14, .42), sl if not bare else skin, yaw), Box(P((-.26, -.01, .29)), S(.11, .13, .06), skin, yaw)]
    ra = arm
    out += [Box(P((.26, -.05 * ra, .50 + .10 * ra)), S(.12, .14, .42 - .12 * ra), sl if not bare else skin, yaw)]
    out += [Box(P((.26, -.06 * ra, .29 + .20 * ra)), S(.11, .13, .06), skin, yaw)]
    out += [Box(P((0, 0, .90)), S(.50, .46, .50), skin, yaw, dec, gloss=.12)]            # голова
    out += [Box(P((0, -.245, .84)), S(.07, .05, .10), tuple(int(v * .93) for v in skin), yaw)]   # нос
    out += [Box(P((-.26, 0, .90)), S(.04, .08, .10), skin, yaw), Box(P((.26, 0, .90)), S(.04, .08, .10), skin, yaw)]  # уши
    if hat in (None, "none"):
        out += [Box(P((0, .01, 1.17)), S(.52, .48, .08), hair, yaw, shadow=False)]
    elif hat == "cap":
        out += [Box(P((0, .01, 1.19)), S(.54, .50, .10), hatcol, yaw, shadow=False), Box(P((0, -.30, 1.14)), S(.50, .20, .035), hatcol, yaw, shadow=False)]
        out += [Box(P((-.26, .05, 1.02)), S(.04, .30, .12), hair, yaw)]
    elif hat == "kerchief":
        out += [Box(P((0, .01, 1.18)), S(.54, .50, .10), hatcol, yaw, shadow=False), Box(P((0, .26, .96)), S(.50, .06, .34), hatcol, yaw),
                Box(P((0, .30, .62)), S(.12, .08, .50), hair, yaw)]                  # платок и коса
        out += [Box(P((-.27, 0, 1.0)), S(.04, .46, .30), hatcol, yaw), Box(P((.27, 0, 1.0)), S(.04, .46, .30), hatcol, yaw)]
    elif hat == "laurel":
        out += [Box(P((0, .01, 1.17)), S(.52, .48, .08), hair, yaw, shadow=False), Box(P((0, -.01, 1.11)), S(.56, .52, .035), (96, 150, 64), yaw, shadow=False)]
    elif hat == "nemes":
        out += [Box(P((0, .01, 1.19)), S(.54, .50, .10), (40, 60, 120), yaw, shadow=False),
                Box(P((-.28, .0, .98)), S(.06, .46, .40), (214, 170, 60), yaw), Box(P((.28, .0, .98)), S(.06, .46, .40), (214, 170, 60), yaw),
                Box(P((0, .27, .98)), S(.50, .06, .40), (40, 60, 120), yaw), Box(P((0, -.02, 1.135)), S(.54, .5, .03), (214, 170, 60), yaw, shadow=False)]
    elif hat == "helmet":
        out += [Box(P((0, .01, 1.19)), S(.56, .52, .13), (150, 154, 164), yaw, gloss=.5), Box(P((0, -.27, 1.12)), S(.52, .05, .06), (150, 154, 164), yaw, gloss=.5),
                Box(P((-.28, .0, .98)), S(.05, .40, .26), (150, 154, 164), yaw, gloss=.5), Box(P((.28, .0, .98)), S(.05, .40, .26), (150, 154, 164), yaw, gloss=.5),
                Box(P((0, .01, 1.31)), S(.07, .42, .12), (190, 40, 40), yaw)]
    elif hat == "kolpak":
        out += [Box(P((0, .01, 1.18)), S(.54, .50, .10), hatcol, yaw, shadow=False), Box(P((0, .01, 1.26)), S(.40, .38, .08), hatcol, yaw, shadow=False)]
        out += [Box(P((-.26, .05, 1.0)), S(.04, .30, .14), hair, yaw)]
    if holding:
        kind, img = holding
        if kind == "papyrus": out += [Box(P((.30, -.20, .62)), S(.34, .04, .46), (240, 224, 180), yaw, img=img, rad=.01)]
        if kind == "bark": out += [Box(P((.30, -.20, .62)), S(.40, .04, .50), (222, 196, 150), yaw, img=img, rad=.01)]
    return out
