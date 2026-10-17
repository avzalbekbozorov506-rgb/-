"""Серия «КЛОД ЗНАЕТ», вопрос № 1: «Роботы заменят людей?» Сценарий: reels/scripts/claude_series_30.md.
Сборка: SCENES=scenes_series1 python3 reels/cubes/video.py reels/hq/claude_series1_hq.mp4"""
from PIL import ImageDraw, ImageFont
from cuberender import Camera
from scenes import cl, pe, G, LINE
from scenes_bank import office_static, office_lights, REG
PLATE = ""; NO_MUSIC = False

def dyn(st):
    B = cl(st, (.2, 1.7, 0), 0.0, k=1.0)
    B += pe(st, "boy", (1.25, 1.95, 0), -.35, hat="cap", hatcol=(190, 184, 168))
    return B
CAM_W = lambda: Camera((.6, -1.6, 1.4), (.6, 2.0, .8), fov=56)
CAM_C = lambda: Camera((.2, -1.2, 1.1), (.2, 1.7, .62), fov=44)
CAM_B = lambda: Camera((1.25, -1.0, 1.1), (1.25, 1.95, .8), fov=40)
TAG = "КЛОД ЗНАЕТ · № 1 ИЗ 30"
def _sc(name, cam, lines, final=False):
    d = dict(name=name, tag=TAG, static=office_static, dyn=dyn, camera=cam, lights=office_lights, region=REG, dof=(2.2, 3.4), lines=lines)
    if final: d["final"] = True
    return d
B_, C_ = "boy", "claude"
SCENES = [
    _sc("r1", CAM_W, [(B_, "Клод, роботы заменят людей?"), (C_, "Зад+ачи заменят. А людей, не так быстро, как пугают.")]),
    _sc("r2", CAM_C, [(C_, "Первое. Робот играет в шахматы лучше любого человека, но с трудом ходит по комнате и берёт чашку. Это парадокс Мор+авека, тысяча девятьсот восемьдесят восьмой год: что нам кажется простым, для машин самое сложное.")]),
    _sc("r3", CAM_C, [(C_, "Второе. У Ам+азона на складах уже миллион роботов. Людей в компании всё равно около полутора миллионов.")]),
    _sc("r4", CAM_C, [(C_, "Третье. Всемирный экономический форум прогнозирует: к две тысячи тридцатому году исчезнет девяносто два миллиона рабочих мест, а появится сто семьдесят миллионов.")]),
    _sc("r5", CAM_W, [(B_, "То есть работа будет?"), (C_, "Будет другая. Вопрос второй: какие профессии исчезнут первыми? Ответ завтра в семь вечера. Подпишись, чтобы не пропустить.")], final=True),
]
CARDS = {"Первое": ("1988 · ПАРАДОКС МОРАВЕКА", "что просто для нас — сложно для машин"), "Второе": ("1 000 000 РОБОТОВ", "у Amazon · людей ≈ 1,5 млн (данные Amazon)"),
         "Третье": ("−92 млн  /  +170 млн", "рабочих мест к 2030 · прогноз WEF")}
def _f(sz, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)
def overlay(sc, t, fr):
    d = ImageDraw.Draw(fr)
    for who, text, st, dur, a in sc["tl"]:
        for k, (big, small) in CARDS.items():
            if text.startswith(k + ".") and st <= t < st + dur + .6:
                f1, f2 = _f(64), _f(34, "Bold"); w = max(d.textlength(big, font=f1), d.textlength(small, font=f2)) + 80
                d.rounded_rectangle(((1080 - w) / 2, 330, (1080 + w) / 2, 520), 36, fill=(18, 20, 28, 235), outline=(255, 214, 80, 255), width=4)
                d.text((540, 395), big, font=f1, fill=(255, 214, 80, 255), anchor="mm"); d.text((540, 470), small, font=f2, fill=(235, 240, 250, 255), anchor="mm")
