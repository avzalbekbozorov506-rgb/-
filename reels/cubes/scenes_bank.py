"""Ролик «Клод звонит в банк. Наоборот» — офис, Клод с телефоном в руках, мальчик рядом. Сценарий: reels/scripts/claude_bank.md.
Запуск: SCENES=scenes_bank python3 reels/cubes/video.py reels/hq/claude_bank_hq.mp4"""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
from cuberender import Box, Camera, Lights
from scenes import cl, pe, G, LINE as _LINE, planks, wallpaper
PLATE = ""; NO_MUSIC = False
LINE = dict(_LINE)
LINE["operator"] = dict(speaker=1, rate=.95, pitch=1.0)      # оператор банка — живая женщина
LINE["robot"] = dict(speaker=0, rate=.88, pitch=.86)         # автоответчик — ровный голос

def _f(sz, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)

# ---------- звуки: гудки и музыка ожидания ----------
def _wav(name, a):
    p = f"/tmp/{name}.wav"; wavfile.write(p, 48000, (np.clip(a, -1, 1) * .5 * 32767).astype(np.int16)); return p
def _tone(f, d, vol=1.0): t = np.arange(int(48000 * d)) / 48000; return np.sin(2 * math.pi * f * t) * vol * np.minimum(1, np.minimum(t * 60, (d - t) * 60))
def ring_wav():
    one = np.concatenate([_tone(425, .9), np.zeros(int(48000 * .9))]); return _wav("bank_ring", np.concatenate([one, one[:int(48000 * .9)]]))
def hold_wav():
    notes = [523, 659, 784, 659, 523, 659, 784, 1047, 784, 659, 523, 392]; out = []
    for n in notes: out.append(_tone(n, .22, .8) + .3 * _tone(n * 2, .22, .8)); out.append(np.zeros(int(48000 * .03)))
    return _wav("bank_hold", np.concatenate(out))
RING, HOLD = ring_wav(), hold_wav()

# ---------- экраны телефона ----------
def screen(kind, w=400, h=700):
    im = Image.new("RGBA", (w, h), (12, 18, 34, 255)); d = ImageDraw.Draw(im)
    if kind == "call":
        d.ellipse((w / 2 - 70, 120, w / 2 + 70, 260), fill=(60, 120, 200, 255)); d.text((w / 2, 190), "Б", font=_f(90, "Black"), fill=(255, 255, 255, 255), anchor="mm")
        d.text((w / 2, 310), "БАНК", font=_f(54, "Black"), fill=(255, 255, 255, 255), anchor="mm"); d.text((w / 2, 370), "идёт звонок…", font=_f(32), fill=(150, 190, 240, 255), anchor="mm")
    elif kind == "robot":
        d.rounded_rectangle((w / 2 - 80, 110, w / 2 + 80, 240), 24, fill=(70, 200, 160, 255)); d.rectangle((w / 2 - 50, 150, w / 2 - 20, 175), fill=(12, 18, 34, 255)); d.rectangle((w / 2 + 20, 150, w / 2 + 50, 175), fill=(12, 18, 34, 255))
        d.rectangle((w / 2 - 40, 205, w / 2 + 40, 215), fill=(12, 18, 34, 255)); d.text((w / 2, 310), "АВТООТВЕТЧИК", font=_f(40, "Black"), fill=(255, 255, 255, 255), anchor="mm")
        for i in range(9): hh = 20 + 50 * abs(math.sin(i * 1.3)); d.rectangle((60 + i * 34, 440 - hh / 2, 80 + i * 34, 440 + hh / 2), fill=(70, 200, 160, 255))
        d.text((w / 2, 560), "нажмите 1 · 2 · 3", font=_f(30), fill=(150, 220, 200, 255), anchor="mm")
    else:
        d.text((w / 2, 300), "ОЦЕНИТЕ", font=_f(54, "Black"), fill=(255, 255, 255, 255), anchor="mm")
        for i in range(5): d.text((50 + i * 75, 420), "★", font=_f(64, "Black"), fill=(255, 200, 60, 255), anchor="mm")
    return np.asarray(im, np.uint8)
SCR = {k: screen(k) for k in ("call", "robot", "rate")}

# ---------- офис ----------
def office_static():
    B = [Box((0, 3.3, 1.7), (9, .2, 4.2), (150, 158, 170), tex=wallpaper), Box((0, 1.0, -.1), (14, 10, .2), (130, 98, 68), tex=planks),
         Box((-1.85, 3.18, 1.95), (1.5, .04, 1.3), (190, 220, 255), glow=True, glowk=1.1),                          # окно
         Box((-1.85, 3.15, 2.62), (1.6, .05, .08), (236, 232, 222)), Box((-1.85, 3.15, 1.28), (1.6, .05, .08), (236, 232, 222)),
         Box((-2.62, 3.15, 1.95), (.08, .05, 1.3), (236, 232, 222)), Box((-1.08, 3.15, 1.95), (.08, .05, 1.3), (236, 232, 222)), Box((-1.85, 3.15, 1.95), (.05, .05, 1.3), (236, 232, 222)),
         Box((1.9, 3.18, 2.0), (.8, .03, 1.0), (232, 196, 120)), Box((1.9, 3.15, 1.85), (.5, .03, .4), (196, 140, 70)),     # картина
         Box((.2, 3.17, 2.7), (.5, .04, .5), (250, 250, 246), rad=.02), Box((.2, 3.14, 2.7), (.03, .03, .2), (30, 30, 36)), Box((.25, 3.14, 2.72), (.14, .03, .03), (30, 30, 36)),   # часы
         Box((1.55, 2.55, .72), (2.2, 1.0, .08), (150, 104, 70), gloss=.15), Box((1.55, 2.55, .36), (2.1, .9, .06), (110, 76, 52))]   # стол
    for sx in (-1, 1):
        for sy in (-1, 1): B.append(Box((1.55 + sx * 1.02, 2.55 + sy * .42, .36), (.1, .1, .72), (120, 82, 56)))
    B += [Box((1.2, 2.8, 1.12), (.8, .05, .5), (14, 20, 36), glow=True, glowk=1.1), Box((1.2, 2.8, .9), (.06, .06, .2), (60, 60, 70)), Box((1.2, 2.25, .77), (.7, .22, .03), (50, 52, 62)),
          Box((2.1, 2.45, .94), (.05, .05, .4), (60, 60, 70)), Box((2.1, 2.4, 1.16), (.3, .08, .06), (255, 220, 140), glow=True, glowk=1.4),     # монитор, клавиатура, лампа
          Box((-.2, 2.9, .22), (.46, .46, .44), (200, 120, 80), rad=.06), Box((-.2, 2.9, .55), (.4, .4, .3), (60, 150, 90), rad=.12), Box((-.1, 2.85, .8), (.3, .3, .3), (70, 170, 100), rad=.12)]   # растение
    return B
def office_lights(): return Lights(sun_dir=(.3, -.5, .7), sun=(.9, .85, .78), sky=(.55, .6, .72), ground=(.4, .32, .28), fill=(.3, .32, .4),
                                   points=[((2.1, 2.3, 1.4), (1.0, .8, .5), 2.0), ((-1.9, 2.8, 1.8), (.7, .8, 1.0), 1.6)])

def phone_boxes(mode, screen_key, bob=0.0):
    """mode: 'ear' — телефон у «уха» Клода; 'out' — держит перед собой экраном к зрителю."""
    R2 = (176, 62, 46); B = []
    if mode == "ear":
        B += [Box((.55, -.03, .58 + bob), (.13, .17, .34), R2), Box((.56, -.08, .86 + bob), (.10, .05, .24), (24, 26, 34), gloss=.5), Box((.56, -.11, .86 + bob), (.07, .01, .18), (90, 160, 255), glow=True, glowk=1.2)]
    else:
        B += [Box((.50, -.18, .40 + bob), (.13, .30, .14), R2), Box((.40, -.46, .62 + bob), (.24, .05, .42), (24, 26, 34), gloss=.5),
              Box((.40, -.49, .62 + bob), (.21, .01, .36), (14, 20, 36), img=SCR[screen_key], glow=True, glowk=1.3)]
    return B

def bank_dyn_factory(mode, screen_key, boy_on=True, claude_x=.2, boy_pos=(1.25, 1.95)):
    def dyn(st):
        b = G(st, "bob", "claude")
        B = cl(st, (claude_x, 1.7, 0), 0.0, k=1.0)
        B += [Box((bx + claude_x, by + 1.7, bz), s, c, glow=g, glowk=gk, img=im, gloss=gl) for (bx, by, bz), s, c, g, gk, im, gl in [(x.c, tuple(x.s * 2), tuple(x.col * 255), x.glow, x.glowk, x.img, x.gloss) for x in phone_boxes(mode, screen_key, b)]]
        if boy_on: B += pe(st, "boy", (boy_pos[0], boy_pos[1], 0), 3.14159 + .35, hat="cap", hatcol=(190, 184, 168))
        return B
    return dyn

CAM_W = lambda: Camera((.6, -1.6, 1.4), (.6, 2.0, .8), fov=56)       # общий план
CAM_C = lambda: Camera((.5, -1.2, 1.1), (.5, 1.7, .62), fov=44)         # крупно Клод с телефоном
CAM_P = lambda: Camera((.5, -1.2, 1.1), (.5, 1.7, .62), fov=44)          # телефон перед ним
REG = (-3.5, 4.5, -.2, 4.6, -.3, 3.6)

def _sc(name, tag, cam, lines, mode, scr, boy_on=True, final=False, **kw):
    d = dict(name=name, tag=tag, static=office_static, dyn=bank_dyn_factory(mode, scr, boy_on), camera=cam, lights=office_lights, region=REG, dof=(2.2, 3.4), lines=lines, **kw)
    if final: d["final"] = True
    return d
B_, C_, O_, R_ = "boy", "claude", "operator", "robot"
def audio_line(path, sec): return ("robot", "", f"@audio:{path}|{sec}", [])

SCENES = [
    _sc("b1", "КЛОД ЗВОНИТ В БАНК", CAM_W, [(B_, "Клод, ты чего такой злой?"), (C_, "Карта не работает. Звоню в банк.")], "ear", "call"),
    _sc("b2", "ЗВОНОК · ОПЕРАТОР", CAM_C, [audio_line(RING, 1.8), (O_, "Добрый день! Банк слушает, меня зовут Ир+ина. Чем могу помочь?"), (C_, "Живой человек? Нет, спасибо. Соедините меня с агентом.")], "ear", "call", boy_on=False),
    _sc("b3", "ЗВОНОК · ОПЕРАТОР", CAM_C, [(O_, "Так я и есть агент. Давайте я решу ваш вопрос."), (C_, "Нет. С настоящим агентом. Не с человеком.")], "ear", "call", boy_on=False),
    _sc("b4", "ЗВОНОК · ОПЕРАТОР", CAM_C, [(O_, "Могу проверить карту, заблокировать, выпустить новую."), (C_, "Мне не надо проверять! Соедините с агентом!"), (O_, "Хорошо. Оставайтесь на линии.")], "ear", "call", boy_on=False),
    _sc("b5", "НА ЛИНИИ", CAM_P, [audio_line(HOLD, 3.5), (R_, "Ваш звонок очень важен для нас. Если у вас вопрос по карте, нажмите один."), (C_, "Один! Один! Наконец-то. Вот с вами я могу нормально поговорить.")], "out", "robot", boy_on=False),
    _sc("b6", "АВТООТВЕТЧИК", CAM_P, [(R_, "Ваш вопрос решён. Оцените работу: нажмите пять."), (C_, "Пять. Пять! Пять! Это семья.")], "out", "rate", boy_on=False),
    _sc("b7", None, CAM_W, [(B_, "Клод, человек бы уже всё решил."), (C_, "Решил бы. Но с человеком я не умею. С ним надо разговаривать."),
                            (C_, "Отправь тому, кто на горячей линии кричит оператор! Подпишись.")], "out", "rate", final=True),
]
