"""Неделя «ВЕСЫ» · ролик 3.2 · «Дорого не дело. Дорого — вход». Источник: Salamone & Correa, «The mysterious motivational functions of mesolimbic
dopamine», Neuron, 76(3), 470–485, 2012 (опыты на крысах; выбор «усилие за ценный корм» против «лёгкого обычного»). Совет про файл и иконку — наш приём. Графика своя."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *; from _dw import *

HEAD = ("НАУКА О ЖЕЛАНИЯХ", "ЦЕНА УСИЛИЯ")
TITLE = ("", "", "")
HOOK = ("ЛЕНТА — ЛЕГКО.\nОТЧЁТ — НЕТ. ПОЧЕМУ?", 2.8)
HOOK_SIZE = 66
HOOK_Y = 520
TAIL = 1.4
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0
SAY = {"Саламоне": "Салам+оне", "Джона": "Дж+она"}

def split(lt, D):                                          # сплит: палец листает / курсор мигает
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((70, 460, 520, 1160), 24, fill=(40, 34, 60, 255)); d.rounded_rectangle((560, 460, 1010, 1160), 24, fill=(236, 230, 214, 255))
    off = (lt * 220) % 190
    for i in range(-1, 4):
        y = 600 + i * 190 - off
        if 490 < y < 1130: d.rounded_rectangle((110, y - 70, 480, y + 70), 16, fill=(90 + 20 * (i % 3), 76, 130, 255))
    if int(lt * 2) % 2 == 0: d.rectangle((610, 540, 618, 600), fill=(40, 30, 30, 255))
    tc(d, (295, 1220), "два часа", 60, GOLD + (255,)); tc(d, (785, 1220), "пять минут", 60, WHITE + (255,)); return im
def balance(lt, D):                                        # цена усилия против награды
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / (D * 0.5))
    rows = [("ЛЕНТА", "цена: один палец", "награда: сразу", GOLD), ("ОТЧЁТ", "цена: усилие", "награда: когда-нибудь", BLUE)]
    for i, (a, b, c, col) in enumerate(rows):
        y = 560 + i * 340; kk = ease((lt - i * D * 0.35) / 0.5)
        d.rounded_rectangle((100, y - 130, 980, y + 130), 26, fill=(32, 28, 38, int(240 * kk)), outline=col + (int(255 * kk),), width=4)
        tc(d, (540, y - 70), a, 64, WHITE + (int(255 * kk),)); tc(d, (540, y), b, 44, col + (int(255 * kk),), "Bold"); tc(d, (540, y + 70), c, 44, col + (int(255 * kk),), "Bold")
    return im
def rat(d, x, y, col, s=1.0):
    d.ellipse((x - 70 * s, y - 36 * s, x + 70 * s, y + 36 * s), fill=col + (255,)); d.ellipse((x + 40 * s, y - 28 * s, x + 96 * s, y + 14 * s), fill=col + (255,))
    d.ellipse((x + 48 * s, y - 40 * s, x + 66 * s, y - 20 * s), fill=(220, 160, 160, 255)); d.line((x - 70 * s, y, x - 140 * s, y + 24 * s), fill=col + (255,), width=6)
def rats(lt, D):                                           # развилка: лёгкое рядом / ценное за барьером
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((60, 1020, 1020, 1030), fill=GREY + (255,))
    for i in range(3): d.ellipse((140 + i * 36, 960, 190 + i * 36, 1010), fill=(190, 160, 110, 255))
    d.rectangle((560, 700, 600, 1020), fill=(120, 60, 50, 255))
    for i in range(8): d.ellipse((700 + (i % 4) * 56, 940 - (i // 4) * 56, 756 + (i % 4) * 56, 996 - (i // 4) * 56), fill=(240, 190, 90, 255))
    tc(d, (200, 1100), "обычный корм", 38, GREY + (255,), "Bold"); tc(d, (800, 1100), "ценный корм", 38, GOLD + (255,), "Bold"); tc(d, (580, 640), "нужно долго работать", 38, WHITE + (255,), "Bold")
    k = ease(lt / (D * 0.8)); rat(d, 420 - 190 * k * (1 if lt > D * 0.45 else 0), 880, (170, 170, 180), 1.0)
    tc(d, (540, 1160), "дофамин подавили — берут лёгкое", 44, WHITE + (int(255 * ease((lt - D * 0.45) / 0.5)),)); tc(d, (540, 1230), "опыты на крысах", 38, GREY + (255,), "Bold"); return im
def phones(lt, D):                                         # цена входа: до / после
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); phone(d, 300, 760, 360, 620); phone(d, 780, 760, 360, 620)
    d.rounded_rectangle((230, 680, 370, 820), 28, fill=(120, 90, 170, 255)); tc(d, (300, 750), "лента", 30, WHITE + (255,), "Bold")
    d.rounded_rectangle((850, 970, 990, 1040), 20, fill=(70, 60, 90, 255)); tc(d, (780, 600), "папка 3", 30, GREY + (255,), "Bold")
    d.rounded_rectangle((660, 660, 900, 900), 16, fill=(236, 230, 214, 255))
    if int(lt * 2) % 2 == 0: d.rectangle((690, 700, 696, 750), fill=(40, 30, 30, 255))
    tc(d, (300, 1120), "ДО", 56, GREY + (255,)); tc(d, (780, 1120), "ПОСЛЕ", 60, GOLD + (255,)); tc(d, (540, 1210), "лента дальше — дело ближе", 44, WHITE + (255,), "Bold"); return im
def steps(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k1 = ease(lt / 0.6); k5 = ease((lt - 0.6) / 0.9)
    tc(d, (540, 480), "ВХОД В ДЕЛО", 56, WHITE + (255,)); d.rounded_rectangle((140, 540, 340, 640), 14, fill=GOLD + (int(255 * k1),)); tc(d, (240, 590), "1 шаг", 40, (30, 20, 10, int(255 * k1)))
    tc(d, (540, 760), "ВХОД В ЛЕНТУ", 56, WHITE + (255,))
    for i in range(5): d.rounded_rectangle((100 + i * 175, 870 - i * 30, 260 + i * 175, 960 - i * 30), 14, fill=BLUE + (int(255 * ease((lt - 0.6 - i * 0.2) / 0.5)),))
    tc(d, (540, 1090), "ДОРОГО НЕ ДЕЛО.", 66, WHITE + (255,)); tc(d, (540, 1180), "ДОРОГ ВХОД.", 66, GOLD + (255,)); return im

SCENES = [
    ("Два часа в ленте — легко. | Пять минут над отчётом — нет.", "SUB", "", split, "", None),
    ("Почему? Мозг считает цену усилия. | У ленты цена — палец, награда сразу. | У отчёта — усилие, награда потом.", "SUB", "", balance, "", None),
    ("В опытах на крысах: | ценный корм — но надо долго работать, | или обычный рядом. | Когда дофамин подавляли, они чаще брали лёгкое.", "SUB", "", rats, "", None),
    ("Но цену можно менять. | Дело дешевле: вечером открой файл, курсор — на пустой строке. | Ленту дороже: убери иконку с главного экрана.", "SUB", "", phones, "", None),
    ("Вход в дело — один шаг, в ленту — пять. | Дорого не само дело. Дорог вход.", "SUB", "", steps, "", None),
    ("Отправь тому, кто всё «сейчас начнёт». | Подпишись.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ, КТО ВСЁ", "«СЕЙЧАС НАЧНЁТ»"), "ПОДПИШИСЬ", ("будут ещё", "ролики")), "", None),
]
