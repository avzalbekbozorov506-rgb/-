"""Ролик «Клод, правда ли, что в Риме брали налог на туалет?» (сценарий reels/scripts/claude_tax_urine.md).
Запуск: SCENES=scenes_toilet python3 video.py reels/hq/claude_toilet_hq.mp4"""
import numpy as np
from cuberender import Box, Camera, Lights
from cast import _place
from scenes import (cl, pe, G, CAM, room_static, room_dyn, room_lights, pompeii_static, pompeii_lights, gradient, LINE as _LINE)
import scenes as S0

PLATE = "В РИМЕ БРАЛИ НАЛОГ\nНА ТУАЛЕТ. ЭТО ПРАВДА"
LINE = dict(_LINE); MUSIC = None
CAMW = lambda: Camera((.5, -1.5, 1.35), (.5, 1.9, .70), fov=70)

# ---------- прачечная (валяльщики), Рим I века ----------
def laundry_static():
    B = pompeii_static()
    B += [Box((1.55, 1.95, .3), (.95, .85, .6), (146, 100, 62), rad=.06), Box((1.55, 1.95, .62), (.82, .72, .06), (236, 228, 205), rad=.03),
          Box((1.55, 1.95, .72), (.5, .4, .14), (250, 246, 232), rad=.05), Box((1.4, 1.9, .78), (.3, .26, .1), (240, 232, 205), rad=.04)]       # чан с тканью
    B += [Box((-.15, 2.7, .26), (.8, .7, .52), (146, 100, 62), rad=.06), Box((-.15, 2.7, .54), (.68, .58, .06), (230, 222, 200), rad=.03)]
    return B
def laundry_dyn(st):
    B = cl(st, (-.4, 1.5, 0), .3, k=.72)
    B += pe(st, "fuller", (.7, 1.8, 0), -.2, top=(214, 206, 180), bottom=(150, 120, 90), sleeves=(228, 166, 132), shoes=(150, 100, 60), hat="none", hair=(70, 52, 40), arm=.8)
    return B

# ---------- Веспасиан и Тит ----------
def court_static(): return pompeii_static()
def court_dyn(st):
    B = cl(st, (-.55, 1.5, 0), .3, k=.66)
    B += pe(st, "titus", (.3, 1.75, 0), -.15, k=.92, top=(240, 234, 222), bottom=(240, 234, 222), sleeves=(228, 166, 132), skirt=True, shoes=(150, 100, 60), hat="none", hair=(70, 52, 40), trim=(150, 30, 40))
    B += pe(st, "roman", (1.2, 1.95, 0), -.35, top=(140, 34, 70), bottom=(140, 34, 70), sleeves=(228, 166, 132), skirt=True, shoes=(150, 100, 60),
            hat="laurel", hair=(150, 140, 130), trim=(214, 170, 60), arm=.9)
    B += [Box((.98, 1.82, 1.18), (.12, .03, .12), (255, 214, 90), glow=True, glowk=1.6, rad=.02)]                                          # монета в поднятой руке
    return B

def _sc(name, tag, static, dyn, cam, lights, lines, final=False, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.6)):
    d = dict(name=name, tag=tag, static=static, dyn=dyn, camera=cam, lights=lights, region=region, dof=dof, lines=lines)
    if final: d["final"] = True
    return d
SCENES = [
    _sc("t_room1", None, room_static, room_dyn, CAM, room_lights, [("boy", "Клод, правда ли, что в Риме брали налог на туалет?"), ("claude", "Правда. Хуже: налог на мочу."), ("boy", "На что?!")]),
    _sc("t_laundry", "РИМ  ·  I век", laundry_static, laundry_dyn, CAMW, pompeii_lights,
        [("claude", "Прачки стирали тоги мочой. Она отбеливает ткань. Император Веспас+иан обложил налогом общественные туалеты, и казна заработала.")]),
    _sc("t_court", "РИМ  ·  70-е годы", court_static, court_dyn, CAMW, pompeii_lights,
        [("claude", "Сын Тит возмутился: отец, как не стыдно? Веспас+иан поднёс ему монету из первой выручки."), ("roman", "Пахнет?"), ("claude", "Тит ответил: нет."),
         ("roman", "А она ведь из мочи."), ("claude", "Так появилось выражение «деньги не пахнут».")]),
    _sc("t_room2", None, room_static, room_dyn, CAM, room_lights,
        [("boy", "А сегодня что-то осталось?"), ("claude", "Во Франции уличные туалеты до сих пор зовут веспасьенами. В честь императора."),
         ("claude", "Какой самый странный налог знаешь ты? Пиши в комментариях. Отправь тому, кто любит платить налоги. Подпишись.")], final=True),
]
