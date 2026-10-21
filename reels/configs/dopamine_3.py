"""Неделя «ВЕСЫ» · ролик 1.3 · «Послевкусие: опыт на три дня». Простое самонаблюдение, без научных утверждений. Цифры в таблице — пример (подписано).
Картина — The Met (CC0), графика своя."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
HEAD = ("ОПЫТ НА ТРИ ДНЯ", "ПОСЛЕВКУСИЕ")
TITLE = ("", "", "")
HOOK = ("ТЕБЕ СТАЛО ЛУЧШЕ\nПОСЛЕ ЛЕНТЫ?", 2.8)
HOOK_SIZE = 80
HOOK_Y = 520
TAIL = 1.4
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0 (archive.org/details/The_Open_Goldberg_Variations-11823)

GOLD, WHITE, GREY = (214, 178, 112), (246, 240, 228), (150, 140, 128)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bg():
    im = Image.new("RGBA", (W, H), (16, 14, 20, 255)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = abs(y - 900) / 900; d.rectangle((0, y, W, y + 4), fill=(int(26 - 12 * k), int(22 - 10 * k), int(30 - 12 * k), 255))
    return im
def text_c(d, xy, t, f, fill): d.text(xy, t, font=f, fill=fill, anchor="mm")
def phone(d, x, y, w=330, h=620):
    d.rounded_rectangle((x - w // 2, y - h // 2, x + w // 2, y + h // 2), 44, fill=(22, 24, 30, 255), outline=(90, 96, 110, 255), width=6)
    d.rounded_rectangle((x - w // 2 + 14, y - h // 2 + 18, x + w // 2 - 14, y + h // 2 - 18), 32, fill=(30, 34, 46, 255))

def close_app(lt, D):                                      # сцена 0: палец закрывает приложение
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); phone(d, 540, 960)
    k = 1 - ease((lt - 0.8) / 0.6)
    d.rounded_rectangle((540 - 135, 960 - 270, 540 + 135, 960 + 270), 26, fill=(120, 80, 190, int(255 * k)))
    d.ellipse((540 - 38, 960 + 280 - 30 * (1 - k), 540 + 38, 960 + 356 - 30 * (1 - k)), fill=(230, 200, 170, 255))
    text_c(d, (540, 1330), "закрыл приложение", sans("Bold", 44), GREY + (255,)); return im

def notes(lt, D):                                          # сцена 1: две оценки в заметках
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((100, 520, 980, 1100), 28, fill=(244, 238, 222, 255))
    text_c(d, (540, 600), "ЗАМЕТКИ", sans("Black", 44), (120, 100, 60, 255))
    rows = [("Как я себя чувствую", "4"), ("Хочу ещё", "9")]
    for i, (a, b) in enumerate(rows):
        k = ease((lt - 0.4 - i * D * 0.3) / 0.6); y = 760 + i * 190
        d.text((150, y), a, font=sans("Bold", 48), fill=(40, 36, 30, int(255 * k)), anchor="lm"); d.text((910, y), b, font=sans("Black", 96), fill=(190, 50, 50, int(255 * k)), anchor="rm")
    text_c(d, (540, 1210), "от 0 до 10 · пример", sans("Bold", 38), GOLD + (255,)); return im

def table(lt, D):                                          # сцена 2: таблица на три дня (пример)
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    cols = [("", 150), ("чувствую", 600), ("хочу ещё", 850)]
    rows = [("лента", "4", "9"), ("сериал", "5", "8"), ("прогулка", "8", "3"), ("разговор", "9", "4")]
    d.text((120, 440), "день 1–3 · ПРИМЕР", font=sans("Black", 48), fill=GOLD + (255,), anchor="lm")
    for (t, x) in cols[1:]: d.text((x, 540), t, font=sans("Bold", 42), fill=WHITE + (255,), anchor="mm")
    for i, (a, b, c) in enumerate(rows):
        k = ease((lt - 0.3 - i * D * 0.17) / 0.5); y = 680 + i * 150
        d.rounded_rectangle((100, y - 55, 980, y + 55), 18, fill=(32, 28, 38, int(240 * k)))
        d.text((140, y), a, font=sans("Black", 52), fill=WHITE + (int(255 * k),), anchor="lm")
        d.text((600, y), b, font=sans("Black", 60), fill=(140, 210, 140, int(255 * k)), anchor="mm"); d.text((850, y), c, font=sans("Black", 60), fill=(240, 150, 110, int(255 * k)), anchor="mm")
    return im

def final(lt, D):                                          # сцена 4: «Сначала измерь. Потом решай.»
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.7)
    text_c(d, (540, 820), "СНАЧАЛА ИЗМЕРЬ.", sans("Black", 88), WHITE + (int(255 * k),)); text_c(d, (540, 960), "ПОТОМ РЕШАЙ.", sans("Black", 88), GOLD + (int(255 * k),)); return im

C_L = "Юлиус фон Лейпольд. Странник в бурю, 1835. The Met"
SCENES = [
    ("Тебе стало лучше после последней ленты? | Не просто приятно, а именно лучше.", "SUB", "", close_app, "", None),
    ("Вот простой опыт на три дня. | Каждый раз, закрывая приложение, | ставь две оценки от нуля до десяти. | Первое: как я себя чувствую. | Второе: хочу ли ещё. | Записывай в заметки.", "SUB", "", notes, "", None),
    ("Не ругай себя — просто собирай данные. | К третьему вечеру ты увидишь, какие занятия дают силы, а какие забирают.", "SUB", "", table, "", None),
    ("И это будет твой собственный ответ, а не чужой совет.", "SUB", "ТВОИ ДАННЫЕ", "met_439333", C_L, (1.0, 1.14, (0.5, 0.55), (0.45, 0.6))),
    ("Сначала измерь. Потом решай.", "SUB", "@MYSLI.VEKOV", final, "", None),
]
