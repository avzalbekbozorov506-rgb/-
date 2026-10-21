"""Пробный Reels вне плана · «Недоделанное не отпускает» (эффект Зейгарник: миф и что работает).
Источники: Zeigarnik, Psychologische Forschung 9 (1927); Ghibellini & Meier, Humanit Soc Sci Commun 12 (2025), doi 10.1057/s41599-025-05000-w;
Masicampo & Baumeister, J Pers Soc Psychol 101(4), 2011, 667–683, doi 10.1037/a0024192.
Картины — The Met (CC0): Вермеер ×2, де Хох, Дрост. Графика (список, вкладки, титры) — своя, рисуется кодом. Музыка — Open Goldberg (CC0)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
HEAD = ("ПСИХОЛОГИЯ", "НЕДОДЕЛАННОЕ")
TITLE = ("", "", "")
HOOK = ("НЕДОДЕЛАННОЕ\nНЕ ОТПУСКАЕТ", 2.2)
HOOK_SIZE = 84
HOOK_Y = 1000
TAIL = 0.7
GAP = 0.35
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0
SAY = {"Зейгарник": "Зейг+арник", "Блюма": "Бл+юма"}

GOLD, WHITE, GREY, RED, GREEN = (214, 178, 112), (246, 240, 228), (150, 140, 128), (200, 40, 46), (140, 210, 140)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bg():
    im = Image.new("RGBA", (W, H), (16, 14, 20, 255)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = abs(y - 900) / 900; d.rectangle((0, y, W, y + 4), fill=(int(26 - 12 * k), int(22 - 10 * k), int(30 - 12 * k), 255))
    return im
def text_c(d, xy, t, f, fill, anchor="mm"): d.text(xy, t, font=f, fill=fill, anchor=anchor)

TASKS = ["ответить на письмо", "записаться к врачу", "разобрать шкаф", "позвонить маме", "оплатить счёт"]

# --- список дел: один пункт мигает (хук) и, в финале, получает время и галочку ---
def todo(lt, D, done=False):
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    text_c(d, (W // 2, 480), "СПИСОК ДЕЛ", sans("Black", 64), GREY + (255,))
    for i, t in enumerate(TASKS):
        y = 620 + i * 112; hot = (i == 0)
        a = 255
        if hot and not done: a = int(150 + 105 * (0.5 + 0.5 * math.sin(lt * 7)))
        d.rounded_rectangle((110, y - 56, W - 110, y + 56), 22, outline=(RED if hot and not done else GREY) + (a,), width=5)
        d.rounded_rectangle((140, y - 28, 196, y + 28), 10, outline=(GREEN if (hot and done) else GREY) + (255,), width=5)
        if hot and done: d.line((150, y, 165, y + 16, 190, y - 18), fill=GREEN + (255,), width=9)
        text_c(d, (240, y), t, sans("Black", 50), WHITE + (a,), "lm")
    if done:
        k = ease(lt / 0.6)
        text_c(d, (W // 2, 1150), "вт · 19:00 · за столом", sans("Black", 64), GOLD + (int(255 * k),))
    return im
def todo_done(lt, D): return todo(lt, D, True)

# --- вкладки в голове: множатся ---
def tabs(lt, D, stop=False):
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    n = 3 + int(min(lt * 2.2, 7)) if not stop else 10
    for i in range(n):
        col, row = i % 2, i // 2; x = 110 + col * 440; y = 520 + row * 170
        if row > 4: break
        d.rounded_rectangle((x, y, x + 400, y + 130), 24, fill=(38, 34, 46, 255), outline=(RED if not stop else GREY) + (255,), width=4)
        d.ellipse((x + 28, y + 50, x + 56, y + 78), fill=(RED if not stop else GREY) + (255,))
        d.rounded_rectangle((x + 80, y + 52, x + 330, y + 72), 8, fill=(86, 80, 96, 255))
    text_c(d, (W // 2, 430), "ВСЁ ЕЩЁ ОТКРЫТО", sans("Black", 56), GOLD + (255,))
    return im
def tabs_still(lt, D): return tabs(lt, D, True)

# --- титры-источники: год крупно, ниже короткая строка ---
def year_card(year, l1, l2, col=GOLD, strike=False):
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.6)
        text_c(d, (W // 2, 760), year, sans("Black", 220), col + (int(255 * k),))
        text_c(d, (W // 2, 1010), l1, sans("Black", 70), WHITE + (int(255 * k),))
        text_c(d, (W // 2, 1110), l2, sans("Black", 56), GREY + (int(255 * k),))
        if strike:
            k2 = ease((lt - 1.4) / 0.4)
            if k2 > 0: d.line((120, 1180, 120 + (W - 240) * k2, 960), fill=RED + (255,), width=18)
        return im
    return f

# --- что · где · когда ---
def www(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    for i, (a, b) in enumerate((("ЧТО", "ответить на письмо"), ("ГДЕ", "за столом"), ("КОГДА", "вторник, 19:00"))):
        k = ease((lt - 0.4 - i * 0.9) / 0.5)
        y = 520 + i * 250
        text_c(d, (W // 2, y), a, sans("Black", 120), GOLD + (int(255 * k),))
        text_c(d, (W // 2, y + 90), b, sans("Black", 54), WHITE + (int(255 * k),))
    return im

def cta_card(l1, l2, l3):
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.7)
        for i, (t, sz, col) in enumerate(((l1[0], 56, GOLD), (l1[1], 56, GOLD), (l2, 92, WHITE), (l3[0], 46, GREY), (l3[1], 46, GREY))):
            text_c(d, (W // 2, (700, 800, 980, 1100, 1170)[i]), t, sans("Black", sz), col + (int(255 * k),))
        return im
    return f

C_V1 = "Я. Вермеер. Молодая женщина с кувшином, ок. 1662. The Met"
C_V2 = "Я. Вермеер. Женщина с лютней, ок. 1662–63. The Met"
C_H = "П. де Хох. Женщина с кувшином и мужчина у кровати, ок. 1658. The Met"
C_D = "В. Дрост. Молодая женщина с жемчужным ожерельем, ок. 1654. The Met"
SCENES = [
    ("Недоделанное не отпускает.", "SUB", "", "met_437881", C_V1, (1.0, 1.1, (0.45, 0.45), (0.4, 0.4))),
    ("В тысяча девятьсот двадцать седьмом Блюма Зейгарник описала странность: | прерванные задания помнят лучше законченных.", "SUB", "1927 · ЗЕЙГАРНИК", "met_437880", C_V2, (1.0, 1.1, (0.5, 0.55), (0.55, 0.5))),
    ("Это пересказывают везде: | незаконченное сидит в голове.", "SUB", "", tabs, "", None),
    ("Но в две тысячи двадцать пятом году учёные не подтвердили: | прерванное помнят не лучше.", "SUB", "", year_card("2025", "НЕ ПОДТВЕРЖДЕНО", "память о прерванном", GOLD, True), "", None),
    ("Зато подтвердилось другое. | Тянет вернуться и доделать.", "SUB", "НО ЕСТЬ ДРУГОЕ", "met_436212", C_D, (1.0, 1.12, (0.5, 0.35), (0.5, 0.45))),
    ("Держит не память, а открытый вопрос: когда? | Помогает запись: что, где и во сколько.", "SUB", "ЧТО · ГДЕ · КОГДА", www, "", None),
    ("В исследовании студентов такой план снизил навязчивые мысли.", "SUB", "2011 · ИССЛЕДОВАНИЕ", "met_436676", C_H, (1.0, 1.12, (0.5, 0.6), (0.45, 0.55))),
    ("Недоделанное не отпускало: ему не хватало времени. | Дай этому время.", "SUB", "НАЗНАЧЬ ВРЕМЯ", todo_done, "", None),
    ("Отправь тому, кто не спит из-за списка дел. | Подпишись.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ, КТО НЕ СПИТ", "ИЗ-ЗА СПИСКА ДЕЛ"), "ПОДПИШИСЬ", ("Не медицинская", "рекомендация")), "", None),
]
