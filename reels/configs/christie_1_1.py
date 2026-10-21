"""Неделя «Кристи» · ролик 1.1 · «Ложь» (приём Пуаро). Источник: Bond C.F., DePaulo B.M., Accuracy of Deception Judgments,
Personality and Social Psychology Review, 2006 (мета-анализ, точность ≈ 54 %). Картины — The Met (CC0); графика своя."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
from dopamine_1 import bg, text_c, sans, ease, cta_card, GOLD, WHITE, GREY, RED
from PIL import Image, ImageDraw

W, H = 1080, 1920
HEAD = ("ПСИХОЛОГИЯ ЛЖИ", "ПРИЁМ ПУАРО")
TITLE = ("", "", "")
HOOK = ("ТЫ НЕ УМЕЕШЬ\nЛОВИТЬ ЛОЖЬ", 2.4)
HOOK_SIZE = 84
HOOK_Y = 520
TAIL = 1.0
GAP = 0.35
MUSIC = ("music/ogv_aria.mp3", 0)

def stat_scene(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    k = ease(lt / 1.4); k2 = ease((lt - 1.6) / 1.0)
    text_c(d, (W // 2, 520), "УГАДАЛИ", sans("Black", 70), GREY + (255,))
    text_c(d, (W // 2, 700), "%d%%" % round(54 * k), sans("Black", 220), GOLD + (255,))
    d.rounded_rectangle((140, 900, 940, 940), 20, fill=(50, 46, 56, 255))
    d.rounded_rectangle((140, 900, 140 + 800 * 0.54 * k, 940), 20, fill=GOLD + (255,))
    if k2 > 0:
        x = 140 + 800 * 0.5
        d.line((x, 870, x, 970), fill=WHITE + (int(255 * k2),), width=6)
        text_c(d, (W // 2, 1060), "монетка дала бы 50%", sans("Black", 58), WHITE + (int(255 * k2),))
    return im

def words_card(*lines):
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); n = len(lines)
        for i, (t, col) in enumerate(lines):
            k = ease((lt - i * 0.9) / 0.5)
            text_c(d, (W // 2, 860 + (i - (n - 1) / 2) * 130), t, sans("Black", 68), col + (int(255 * k),))
        return im
    return f

C_L = "Жорж де Латур. Гадалка, 1630-е. The Met"

C_M = "Г. Метсю. Женщина у окна, начало 1660-х. The Met"
SCENES = [
    ("Ты не умеешь ловить ложь. | Никто не умеет.", "SUB", "", "met_436838", C_L, (1.0, 1.12, (0.5, 0.5), (0.45, 0.5))),
    ("Учёные собрали больше двухсот исследований. | Людям показывали записи: | где-то человек врёт, где-то говорит правду. | Угадывали пятьдесят четыре процента. | Монетка дала бы пятьдесят.", "SUB", "", stat_scene, "", None),
    ("Бегающий взгляд, дрожащий голос — ничего это не доказывает.", "SUB", "", "met_435868", "П. Сезанн. Игроки в карты, 1890–92. The Met", (1.0, 1.1, (0.5, 0.5), (0.5, 0.45))),
    ("Поэтому Пуар+о проверял, а не гадал. | Ему говорят: «Я весь вечер был дома». | А он спрашивает: кто это видел? | Горел ли свет? | Кто открыл дверь?", "SUB", "", "met_437880", "Я. Вермеер. Молодая женщина с лютней, около 1662. The Met", (1.0, 1.12, (0.5, 0.5), (0.55, 0.5))),
    ("Слова — не доказательство. | Слова — повод для вопроса.", "SUB", "", words_card(("СЛОВА —", WHITE), ("НЕ ДОКАЗАТЕЛЬСТВО", WHITE), ("ПОВОД ДЛЯ ВОПРОСА", GOLD)), "", None),
    ("В следующий раз спроси себя не «верю или не верю». | А «что тут можно проверить?»", "SUB", "", "met_437073", C_M, (1.0, 1.12, (0.5, 0.45), (0.5, 0.55))),
    ("Отправь тому, кто верит на слово. | Подпишись.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ,", "КТО ВЕРИТ НА СЛОВО"), "ПОДПИШИСЬ", ("следующий ролик:", "Кристи и волны")), "", None),
]
