"""Неделя «ВЕСЫ» · ролик 2.3 · «Телефон завибрировал. Но молчал». Источники: Drouin, Kaiser, Miller, Computers in Human Behavior 28(4), 2012 (опрос 290 студентов, 89 %);
Rothberg et al., BMJ 341:c6914, 2010 (сотрудники больницы, ≈ 68 %); Stothart, Mitchum, Yehnert, J Exp Psychol: HPP 41(4), 893–897, 2015.
«Мозг выдаёт сигнал сам» — гипотеза. Графика своя."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *; from _dw import *

HEAD = ("НАУКА О ЖЕЛАНИЯХ", "ФАНТОМНАЯ ВИБРАЦИЯ")
TITLE = ("", "", "")
HOOK = ("ТЕЛЕФОН ЗАВИБРИРОВАЛ.\nНО ОН МОЛЧАЛ", 2.6)
HOOK_SIZE = 80
HOOK_Y = 520
TAIL = 1.4
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0
SAY = {}

def empty(lt, D):                                          # экран пуст, телефон «дрожит»
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); sh = int(8 * math.sin(lt * 40)) if lt < 1.2 else 0
    phone(d, 540 + sh, 960, 420, 800, fill=(12, 12, 16, 255)); tc(d, (540, 960), "пусто", 70, GREY + (int(255 * ease((lt - 1.2) / 0.6)),), "Bold"); return im
def stats(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); rows = [("9 из 10", "студентов", "опрос 2012", GOLD), ("2 из 3", "сотрудников больницы", "опрос 2010", BLUE)]
    for i, (a, b, c, col) in enumerate(rows):
        y = 620 + i * 430; k = ease((lt - i * D * 0.4) / 0.5)
        d.rounded_rectangle((100, y - 170, 980, y + 170), 26, fill=(32, 28, 38, int(240 * k)), outline=col + (int(255 * k),), width=4)
        tc(d, (540, y - 70), a, 120, col + (int(255 * k),)); tc(d, (540, y + 50), b, 52, WHITE + (int(255 * k),), "Bold"); tc(d, (540, y + 115), c, 36, GREY + (int(255 * k),), "Bold")
    tc(d, (540, 1520), "фантомная вибрация", 50, WHITE + (255,)); return im
def head(lt, D):                                           # голова «ждёт сигнала»
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((340, 560, 740, 1000), fill=(60, 56, 78, 255)); d.rounded_rectangle((460, 980, 620, 1120), 20, fill=(60, 56, 78, 255))
    for i in range(3): d.arc((300 - i * 50, 680 - i * 50, 440 + i * 50, 820 + i * 50), 140, 220, fill=GOLD + (int(255 * abs(math.sin(lt * 4 - i * 0.7))),), width=8)
    phone(d, 540, 1360, 220, 380, fill=(12, 12, 16, 255)); tc(d, (540, 1360), "?", 90, GOLD + (255,))
    tc(d, (540, 1650), "одно из объяснений — не доказанный факт", 38, GREY + (255,), "Bold"); return im
def attention(lt, D):                                      # линия внимания ломается после сообщения
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / (D * 0.8)); pts = []
    for i in range(101):
        u = i / 100; y = 900 + (0 if u < 0.5 else 80 * math.sin((u - 0.5) * 60) * min(1, (u - 0.5) * 4))
        pts.append((100 + 880 * u, y))
    n = max(2, int(101 * k))
    for a, b in zip(pts[:n - 1], pts[1:n]): d.line((a, b), fill=(GOLD if a[0] < 540 else (230, 120, 100)) + (255,), width=12)
    if k > 0.5: d.rounded_rectangle((420, 640, 660, 740), 20, fill=(50, 90, 160, 255)); tc(d, (540, 690), "сообщение", 38, WHITE + (255,), "Bold")
    tc(d, (540, 1250), "не отвечали — а ошибок больше", 46, WHITE + (255,)); tc(d, (540, 1330), "лабораторный опыт, 2015", 38, GREY + (255,), "Bold"); return im
def notif(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.6)
    rows = [("Люди", True), ("Лента", False), ("Игры", False), ("Магазины", False)]
    for i, (a, on) in enumerate(rows):
        y = 620 + i * 150; d.rounded_rectangle((120, y - 55, 960, y + 55), 20, fill=(32, 28, 38, int(240 * k)))
        tc(d, (330, y), a, 48, WHITE + (int(255 * k),)); d.rounded_rectangle((780, y - 28, 900, y + 28), 28, fill=((GOLD if on else (70, 66, 80)) + (int(255 * k),)))
        d.ellipse(((860 if on else 790), y - 22, (894 if on else 824), y + 22), fill=(250, 250, 250, int(255 * k)))
    k2 = ease((lt - D * 0.5) / 0.6); tc(d, (540, 1400), "ЛЮДИ — ДА.", 80, GOLD + (int(255 * k2),)); tc(d, (540, 1510), "ОСТАЛЬНОЕ — НЕТ.", 80, WHITE + (int(255 * k2),)); return im
def room(lt, D):                                           # телефон уезжает в другую комнату
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / (D * 0.8))
    d.rectangle((80, 700, 480, 1300), outline=GREY + (255,), width=6); d.rectangle((600, 700, 1000, 1300), outline=GOLD + (255,), width=6)
    tc(d, (280, 1360), "ты", 44, WHITE + (255,), "Bold"); tc(d, (800, 1360), "телефон", 44, GOLD + (255,), "Bold")
    phone(d, int(280 + 520 * k), 1000, 120, 200, fill=(40, 40, 54, 255)); tc(d, (540, 1560), "на час работы", 56, WHITE + (255,)); return im

SCENES = [
    ("Телефон завибрировал. Но он молчал. | Знакомо? Достаёшь — а там пусто.", "SUB", "", empty, "", None),
    ("Это называют фантомной вибрацией. | В опросе американских студентов её чувствовали почти девять из десяти. | У сотрудников одной больницы — примерно две трети. | Это очень распространено.", "SUB", "", stats, "", None),
    ("Мозг так привык ждать сигнала, что иногда выдаёт его сам. | Это одно из объяснений, не доказанный факт.", "SUB", "", head, "", None),
    ("А вот что измерено. | Студентам давали задание на внимание. | Приходило сообщение, они не отвечали, | но ошибок становилось больше. | Даже неотвеченное уведомление отвлекает.", "SUB", "", attention, "", None),
    ("Поэтому сегодня оставь уведомления только от людей.", "SUB", "", notif, "", None),
    ("И на час работы унеси телефон в другую комнату.", "SUB", "", room, "", None),
    ("Отправь тому, кому вечно «кажется». | Подпишись — будут ещё ролики.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ,", "КОМУ ВЕЧНО «КАЖЕТСЯ»"), "ПОДПИШИСЬ", ("будут ещё", "ролики")), "", None),
]
