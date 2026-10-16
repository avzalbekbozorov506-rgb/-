"""Шесть сцен ролика «Клод, а что было бы тысячу лет назад?». Каждая сцена: static(), dyn(st), camera, lights, region, tag, lines."""
import numpy as np, random
from cuberender import Box, Camera, Lights, fbm, vnoise
from cast import claude, boy, person
import props

# ---------- текстуры ----------
def lerp(a, b, t): return a + (b - a) * t[:, None]
def sand(p, ax, sgn, col):
    n = fbm(p[:, 0] * 9, p[:, 1] * 9, 3); r = np.sin(p[:, 1] * 38 + n * 6) * .5 + .5
    return col * (0.9 + 0.12 * n[:, None] + 0.04 * r[:, None])
def limestone(p, ax, sgn, col):
    u = np.where(ax == 1, p[:, 0], p[:, 1]) ; v = np.where(ax == 2, p[:, 1], p[:, 2])
    out = col * (0.93 + .1 * fbm(p[:, 0] * 14, p[:, 2] * 14 + p[:, 1] * 3, 5)[:, None])
    seam = (np.abs((v / .26) % 1 - .5) > .485) | (np.abs((u / .42 + np.floor(v / .26) * .5) % 1 - .5) > .49)
    out[seam] *= .72; return out
def slabs(p, ax, sgn, col):
    cx, cy = np.floor(p[:, 0] / .45), np.floor(p[:, 1] / .45)
    tint = 0.9 + 0.14 * np.array([vnoise(np.array([a]), np.array([b]), 3)[0] for a, b in zip(cx[:1], cy[:1])]) if False else 0.9 + .14 * ((np.sin(cx * 12.9 + cy * 78.2) * 43758.5) % 1)
    out = col * tint[:, None]
    seam = (np.abs((p[:, 0] / .45) % 1 - .5) > .47) | (np.abs((p[:, 1] / .45) % 1 - .5) > .47)
    out[seam] *= .7; return out
def snow(p, ax, sgn, col):
    n = fbm(p[:, 0] * 6, p[:, 1] * 6, 8); return col * (0.94 + .08 * n[:, None]) * np.array([.97, .99, 1.03], np.float32)
def logs(p, ax, sgn, col):
    z = p[:, 2]; row = np.floor(z / .17); seam = np.abs((z / .17) % 1 - .5) > .46
    tint = .86 + .24 * ((np.sin(row * 7.7) * 4375.5) % 1)
    out = col * tint[:, None] * (0.95 + .1 * fbm(p[:, 0] * 22, z * 4, 2)[:, None]); out[seam] *= .55; return out
def planks(p, ax, sgn, col):
    s = np.floor(p[:, 0] / .28) % 2; out = col * (0.96 + .1 * fbm(p[:, 0] * 5, p[:, 1] * 40, 1)[:, None]); out[s == 1] *= .93
    out[np.abs((p[:, 0] / .28) % 1 - .5) > .47] *= .78; return out
def wallpaper(p, ax, sgn, col):
    out = col.copy(); out[np.floor(p[:, 0] / .35) % 2 == 1] *= .965; return out
def graffiti(p, ax, sgn, col):
    """Штукатурка с надписями: тонкие «каракули» из контуров шума + пара крупных строк."""
    x, z = p[:, 0], p[:, 2]
    base = col * (0.93 + .12 * fbm(x * 6, z * 6, 2)[:, None])
    n = fbm(x * 8 + 3, z * 8, 7, 3); line = np.abs(n - .5) < .022
    n2 = fbm(x * 15, z * 13 + 9, 11, 2); line |= np.abs(n2 - .5) < .015
    mask = fbm(x * 2.4, z * 2.4, 5) > .45
    out = base.copy(); out[line & mask & (z > .15)] = np.array([84, 40, 32], np.float32) / 255 * 1.0; return out
def gradient(top, hor, z0=.0, z1=3.0):
    top = np.array(top, np.float32) / 255; hor = np.array(hor, np.float32) / 255
    def f(p, ax, sgn, col):
        t = np.clip((p[:, 2] - z0) / (z1 - z0), 0, 1); return lerp(hor, top, t)
    return f

SKY = (3.0, 1.0)  # заглушка

def wall_box(y, w=14, h=4, col=(88, 112, 128), tex=wallpaper, c=0.0, z=1.6):
    return Box((c, y, z), (w, .2, h), col, tex=tex)
def floor_box(col, tex, y=1.2, d=7.0, w=14):
    return Box((0, y, -.1), (w, d, .2), col, tex=tex)

LINE = {  # озвучка: роль -> параметры Vosk
    "boy": dict(speaker=2, rate=.98, pitch=1.14), "claude": dict(speaker=4, rate=.9, pitch=1.0),
    "egypt": dict(speaker=3, rate=.95, pitch=.90), "roman": dict(speaker=3, rate=.9, pitch=.80),
    "girl": dict(speaker=1, rate=.95, pitch=1.0),
}
def G(st, key, who, d=0.0): return st.get(key, {}).get(who, d)
def cl(st, pos, yaw, k=1.0, **kw):
    return claude(pos, yaw=yaw, talk=G(st, "talk", "claude"), blink=G(st, "blink", "claude"), bob=G(st, "bob", "claude"), k=k, **kw)
def pe(st, who, pos, yaw, **kw):
    arm = kw.pop("arm", G(st, "arm", who))
    return person(pos, yaw=yaw, talk=G(st, "talk", who), blink=G(st, "blink", who), bob=G(st, "bob", who), arm=arm, **kw)

CAM = lambda: Camera((.55, -1.25, 1.25), (.5, 1.9, .78), fov=60)
CAM2 = lambda: Camera((.5, -1.5, 1.35), (.5, 1.9, .70), fov=62)

# ======================= 1 и 6. Комната =======================
def room_static():
    B = [wall_box(3.2, 9, 4, (88, 112, 128)), floor_box((176, 128, 86), planks, 1.2, 6.2, 9),
         Box((-2.9, 1.2, 1.6), (.2, 6.2, 4), (96, 120, 136)), Box((-.2, 3.08, 1.9), (1.5, .04, 1.2), (28, 36, 74), glow=True, glowk=1.0)]
    for (sx, sz) in [(-.7, 2.2), (-.35, 1.7), (.2, 2.35), (.4, 1.6), (-.05, 1.95), (.6, 2.1)]:
        B.append(Box((sx, 3.05, sz), (.05, .02, .05), (255, 240, 180), glow=True))
    F = (240, 232, 214)
    B += [Box((-.2, 3.05, 2.55), (1.6, .06, .08), F), Box((-.2, 3.05, 1.25), (1.6, .06, .08), F), Box((-.98, 3.05, 1.9), (.08, .06, 1.3), F),
          Box((.58, 3.05, 1.9), (.08, .06, 1.3), F), Box((-.2, 3.05, 1.9), (.06, .06, 1.3), F)]
    B += [Box((1.9, 3.08, 1.9), (.8, .03, 1.0), (232, 196, 120)), Box((1.9, 3.05, 1.75), (.5, .03, .4), (196, 140, 70))]
    B.append(Box((1.0, 1.9, .70), (2.2, 1.0, .08), (150, 104, 70), gloss=.15))
    for sx in (-1, 1):
        for sy in (-1, 1): B.append(Box((1.0 + sx * 1.0, 1.9 + sy * .42, .33), (.1, .1, .66), (120, 82, 56)))
    B += [Box((1.45, 2.3, .76), (.22, .22, .05), (70, 70, 80)), Box((1.45, 2.3, 1.02), (.05, .05, .5), (70, 70, 80)), Box((1.45, 2.22, 1.30), (.36, .30, .20), (255, 214, 120), glow=True)]
    B.append(Box((-1.8, 1.4, .02), (1.6, 1.2, .04), (150, 70, 70), shadow=False))
    return B
def room_dyn(st):
    B = cl(st, (.95, 1.85, .74), -.3, k=.8)
    B += pe(st, "boy", (.22, 1.25, 0), .30, hat="cap", hatcol=(190, 184, 168))
    if st.get("book", 0): B.append(Box((1.75, 1.85, .83), (.6, .44, .14), (60, 112, 96), yaw=.25, gloss=.2))
    else: B += [Box((1.75, 1.85, .79), (.6, .44, .10), (60, 112, 96), yaw=.25), Box((1.75, 1.85, .83), (.55, .40, .06), (244, 236, 214), yaw=.25)]
    return B
room_lights = lambda: Lights(sun_dir=(-.45, -.55, .70), sun=(1.0, .88, .72), sky=(.46, .52, .74), ground=(.36, .27, .22), points=[((1.45, 2.1, 1.25), (1.0, .72, .38), 1.8)])

# ======================= 2. Египет =======================
def egypt_static():
    B = [Box((0, 9, 2.5), (40, .2, 12), (120, 180, 230), tex=gradient((70, 130, 215), (250, 228, 180), 0, 5), glow=True, glowk=.95),
         Box((0, 3, -.1), (40, 12, .2), (226, 190, 120), tex=sand)]
    for i in range(6):                                               # недостроенная пирамида ступенями
        s = 4.6 - i * .68; B.append(Box((.9, 5.0, .26 + i * .5), (s, s, .5), (232, 210, 160), tex=limestone, rad=.05))
    B.append(Box((.9, 5.0, 3.4), (.9, .9, .02), (200, 180, 130)))
    for (x, y, z, w) in [(-1.0, 2.2, .22, .5), (-1.25, 2.5, .22, .5), (-1.1, 2.3, .66, .5), (2.1, 2.3, .22, .55), (1.9, 3.1, .22, .5), (2.3, 2.8, .22, .5)]:
        B.append(Box((x, y, z), (w, w, .44), (228, 206, 156), tex=limestone, rad=.04))
    B.append(Box((-.4, 3.0, .12), (1.6, .5, .1), (130, 90, 56)))        # деревянные полозья
    for (x, y) in [(-1.6, 3.6), (-.7, 3.9), (.2, 3.5), (1.6, 3.7), (2.4, 3.4)]:   # крошечные рабочие
        B += person((x, y, 0), yaw=.2, k=.22, skin=(176, 120, 90), bare=True, bottom=(240, 236, 220), hat="none", hair=(30, 24, 22))
    B.append(Box((2.3, 8.5, 4.2), (1.3, .1, 1.3), (255, 244, 200), glow=True, glowk=2.4))   # солнце
    return B
def egypt_dyn(st):
    B = cl(st, (-.05, 1.55, 0), .3, k=.72)
    B += pe(st, "egypt", (.95, 1.8, 0), -.35, bare=True, bottom=(240, 236, 220), trim=(214, 170, 60), hat="nemes", hair=(30, 24, 22), skin=(190, 130, 96),
            shoes=(190, 150, 90), holding=("papyrus", props.papyrus()), brows=True)
    return B
egypt_lights = lambda: Lights(sun_dir=(-.5, -.35, .8), sun=(1.0, .9, .72), sky=(.55, .66, .92), ground=(.62, .5, .34), fill=(.22, .22, .26))

# ======================= 3. Помпеи =======================
def pompeii_static():
    B = [Box((0, 12, 3), (60, .2, 14), (150, 190, 230), tex=gradient((96, 150, 220), (245, 230, 200), 0, 5), glow=True, glowk=.95),
         Box((0, 3, -.1), (30, 10, .2), (160, 150, 138), tex=slabs),
         Box((0, 3.1, .95), (14, .3, 1.9), (200, 100, 70), tex=graffiti), Box((0, 3.1, .08), (14, .32, .16), (110, 70, 56)),
         Box((0, 3.1, 1.95), (14, .34, .1), (234, 224, 200))]
    for (x, y, z, w, h) in [(-5, 11, 1.5, 7, 3), (-4.4, 11, 4.3, 4.2, 3), (-3.9, 11, 6.4, 2.4, 2)]:   # Везувий
        B.append(Box((x, y, z), (w, 3, h), (110, 86, 70), rad=.1))
    B += [Box((-3.6, 11, 7.9), (4.5, 2.5, 1.6), (150, 140, 138), glow=False, rad=.2), Box((-2.4, 11, 8.6), (3.8, 2.2, 1.0), (180, 172, 170), rad=.2)]
    for cx in (-1.15, 2.25):
        B += [Box((cx, 2.55, .08), (.5, .5, .16), (236, 224, 200)), Box((cx, 2.55, 1.15), (.34, .34, 2.0), (240, 230, 208), tex=limestone), Box((cx, 2.55, 2.2), (.5, .5, .14), (236, 224, 200))]
    B += [Box((-.5, 2.7, .25), (.3, .3, .5), (170, 96, 60), gloss=.2), Box((-.5, 2.7, .55), (.14, .14, .14), (170, 96, 60))]
    return B
def pompeii_dyn(st):
    B = cl(st, (-.05, 1.55, 0), .3, k=.72)
    B += pe(st, "roman", (.95, 1.8, 0), -.35, top=(240, 234, 222), bottom=(240, 234, 222), sleeves=(228, 166, 132), skirt=True, shoes=(150, 100, 60),
            hat="laurel", hair=(70, 52, 40), trim=(150, 30, 40), arm=.9)
    return B
pompeii_lights = lambda: Lights(sun_dir=(-.5, -.4, .75), sun=(1.0, .92, .78), sky=(.55, .66, .9), ground=(.56, .44, .36))

# ======================= 4. Новгород, береста =======================
def nov_static():
    B = [Box((0, 12, 3), (60, .2, 14), (190, 200, 230), tex=gradient((130, 140, 190), (250, 214, 196), 0, 5), glow=True, glowk=.9),
         Box((0, 3, -.1), (30, 10, .2), (238, 244, 250), tex=snow),
         Box((0, 3.3, .85), (9, .5, 1.7), (140, 96, 60), tex=logs), Box((0, 3.3, 1.8), (9.4, .8, .22), (240, 246, 252), tex=snow),
         Box((.6, 3.02, .95), (.7, .06, .6), (255, 200, 110), glow=True, glowk=1.4), Box((.6, 3.0, 1.28), (.82, .08, .06), (90, 60, 40)),
         Box((.6, 3.0, .62), (.82, .08, .06), (90, 60, 40)), Box((.6, 3.0, .95), (.06, .08, .6), (90, 60, 40))]
    for x in np.arange(-2.4, -.2, .35): B.append(Box((x, 2.2, .35), (.14, .14, .7), (120, 82, 56)))   # забор
    B.append(Box((-1.3, 2.2, .5), (2.4, .1, .1), (120, 82, 56)))
    for (x, y) in [(-1.9, 3.9), (2.4, 4.2)]:                           # кубические ёлки со снегом
        for i, s in enumerate((1.3, 1.0, .7, .4)): B.append(Box((x, y, .5 + i * .45), (s, s, .45), (40, 94, 70), rad=.05)); B.append(Box((x, y, .66 + i * .45), (s * .98, s * .98, .06), (240, 246, 252)))
    rnd = random.Random(2)
    for _ in range(70):
        B.append(Box((rnd.uniform(-1.8, 2.8), rnd.uniform(.8, 2.8), rnd.uniform(.3, 2.3)), (.035, .035, .035), (255, 255, 255), glow=True, shadow=False))
    return B
def nov_dyn(st):
    B = cl(st, (-.05, 1.55, 0), .3, k=.72)
    B += pe(st, "girl", (.95, 1.8, 0), -.35, top=(244, 240, 228), bottom=(176, 40, 44), skirt=True, sleeves=(244, 240, 228), shoes=(110, 70, 44), hat="kerchief",
            hatcol=(210, 70, 60), hair=(120, 80, 48), holding=("bark", props.bark_letter()), blush=True)
    return B
nov_lights = lambda: Lights(sun_dir=(-.4, -.5, .6), sun=(1.0, .86, .72), sky=(.62, .68, .9), ground=(.66, .66, .78), fill=(.2, .24, .34), points=[((.6, 2.7, 1.0), (1.0, .7, .35), 2.0)])

# ======================= 5. Онфим =======================
def onfim_static():
    B = [Box((0, 3.3, 1.5), (9, .4, 3.4), (140, 96, 60), tex=logs), Box((0, 1.2, -.1), (9, 6.4, .2), (150, 106, 70), tex=planks),
         Box((-2.9, 1.2, 1.5), (.2, 6.4, 3.4), (130, 90, 56), tex=logs),
         Box((-.9, 3.08, 1.5), (.9, .05, .8), (240, 230, 190), glow=True, glowk=1.5), Box((-.9, 3.05, 1.5), (1.0, .06, .06), (90, 60, 40)), Box((-.9, 3.05, 1.5), (.06, .06, .9), (90, 60, 40))]
    B += [Box((.95, 2.1, .60), (1.9, .85, .07), (150, 104, 70), gloss=.1)]
    for sx in (-1, 1):
        for sy in (-1, 1): B.append(Box((.95 + sx * .85, 2.1 + sy * .33, .28), (.1, .1, .56), (110, 74, 50)))
    B += [Box((.15, 2.0, .68), (.07, .07, .1), (250, 240, 200)), Box((.15, 2.0, .76), (.025, .025, .05), (255, 190, 80), glow=True, glowk=3.0)]
    B += [Box((.78, 2.25, 1.15), (.92, .04, .6), (224, 198, 152), img=props.onfim(), rad=.01),
          Box((.5, 2.25, .8), (.04, .04, .5), (110, 74, 50)), Box((1.06, 2.25, .8), (.04, .04, .5), (110, 74, 50))]
    B += [Box((1.75, 2.8, .45), (.7, .5, .9), (130, 90, 60), tex=logs), Box((-1.7, 1.2, .02), (1.6, 1.4, .04), (120, 60, 52), shadow=False)]
    return B
def onfim_dyn(st):
    B = cl(st, (1.38, 2.0, .64), -.4, k=.6)
    B += pe(st, "onfim", (-.05, 1.5, 0), .5, k=.88, top=(74, 106, 170), bottom=(110, 84, 60), skin=(232, 176, 140), hat="kolpak", hatcol=(150, 110, 70), hair=(150, 106, 60), arm=.6)
    return B
onfim_lights = lambda: Lights(sun_dir=(-.5, -.3, .55), sun=(.9, .84, .76), sky=(.34, .34, .44), ground=(.36, .28, .22), fill=(.14, .14, .2),
                              points=[((.15, 1.95, .95), (1.0, .66, .3), 2.2), ((-.9, 2.6, 1.6), (.7, .7, .6), 1.8)])
onfim_cam = lambda: Camera((.45, -1.0, 1.15), (.5, 2.0, .85), fov=56)

SCENES = [
    dict(name="room1", tag=None, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5),
         lines=[("boy", "Клод, а что было бы, если бы ты появился тысячи лет назад?"), ("claude", "Я бы остался без работы. Там уже всё было.")]),
    dict(name="egypt", cam2=1, tag="ЕГИПЕТ  ·  2560 г. до н. э.", static=egypt_static, dyn=egypt_dyn, camera=CAM2, lights=egypt_lights, region=(-3, 3.5, -.2, 6, -.3, 4), dof=(3.6, 2.4),
         lines=[("claude", "Я бы предложил вести журнал перевозок камня."), ("egypt", "Уже ведём."),
                ("claude", "Чиновник Мерер четыре с половиной тысячи лет назад записывал, сколько камня привёз к пирамиде.")]),
    dict(name="pompeii", cam2=1, tag="ПОМПЕИ  ·  I век", static=pompeii_static, dyn=pompeii_dyn, camera=CAM2, lights=pompeii_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.0), dof=(3.3, 1.6),
         lines=[("claude", "Тогда я бы открыл комментарии."), ("roman", "Удивляюсь, стена, что ты не рухнула под тяжестью стольких глупых надписей."),
                ("claude", "Две тысячи лет назад люди уже жаловались на комментаторов.")]),
    dict(name="nov1", cam2=1, tag="НОВГОРОД  ·  XI–XII век", static=nov_static, dyn=nov_dyn, camera=CAM2, lights=nov_lights, region=(-3, 3.5, -.2, 4.5, -.3, 3.0), dof=(3.3, 1.6),
         lines=[("claude", "Ладно. Тогда я придумаю сообщ+ения."), ("girl", "Я посылала к тебе трижды. Почему ты не приходил ко мне всю неделю?"),
                ("claude", "Первое сообщение без ответа. Девятьсот лет назад.")]),
    dict(name="onfim", tag="НОВГОРОД  ·  XIII век", static=onfim_static, dyn=onfim_dyn, camera=onfim_cam, lights=onfim_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.2), dof=(3.0, 1.4),
         lines=[("claude", "А это твой коллега. Он+фим, семь лет."), ("claude", "Вместо уроков рисовал себя богатырём. Семьсот шестьдесят лет назад.")]),
    dict(name="room2", tag=None, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5), book_after=0,
         lines=[("boy", "Значит, мне тоже можно не делать уроки?"), ("claude", "Он+фим буквы всё-таки выводил. Они тоже сохранились."),
                ("boy", "Даже тут не повезло…"), ("claude", "Подпишись — тут история смешнее, чем в учебнике.")]),
]
