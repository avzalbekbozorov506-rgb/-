"""Неделя «ВЕСЫ» · ролик 2.1 · «У ленты нет конца». Аза Раскин: по его словам, придумал бесконечную прокрутку в 2006 г. и сожалеет об этом
(Masters of Scale; Rethinking with Adam Grant). Приоритет изобретения оспаривается (патентная заявка Microsoft от 14.02.2006) — в ролике сказано «по его словам».
Остальное — наблюдение о дизайне, не результат исследования. Графика своя, без картин и без фото."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *; from _dw import *

HEAD = ("НАУКА О ЖЕЛАНИЯХ", "БЕСКОНЕЧНАЯ ЛЕНТА")
TITLE = ("", "", "")
HOOK = ("АВТОР ЛЕНТЫ\nЖАЛЕЕТ О НЕЙ", 2.4)
HOOK_SIZE = 70
HOOK_Y = 520
TAIL = 1.4
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0
SAY = {"Раскин": "Р+аскин", "Аза": "А+за"}

def feed(lt, D, end=False):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); phone(d, 540, 820, 520, 760)
    off = (lt * 220) % 260
    for i in range(-1, 5):
        y = 520 + i * 260 - off
        if 480 < y < 1130: d.rounded_rectangle((330, y - 90, 750, y + 90), 22, fill=(60 + 18 * (i % 3), 56, 90, 255))
    return im
def hook_feed(lt, D):
    im = feed(lt, D); d = ImageDraw.Draw(im, "RGBA"); tc(d, (540, 1230), "лента не кончается", 52, GOLD + (255,), "Bold"); return im
def raskin(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.8)
    d.rounded_rectangle((120, 700, 960, 1120), 24, outline=GOLD + (int(255 * k),), width=5, fill=(30, 26, 34, int(240 * k)))
    tc(d, (540, 810), "АЗА РАСКИН", 84, WHITE + (int(255 * k),)); tc(d, (540, 940), "2006", 130, GOLD + (int(255 * k),))
    tc(d, (540, 1050), "по его словам, придумал прокрутку", 38, GREY + (int(255 * k),), "Bold"); return im
def pages(lt, D):                                          # страницы склеиваются в одну длинную полосу
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / (D * 0.7)); gap = int(40 * (1 - k))
    for i in range(4):
        y = 450 + i * (190 + gap)
        d.rounded_rectangle((300, y, 780, y + 190), 18, fill=(236, 230, 214, 255)); tc(d, (540, y + 95), f"стр. {i + 1}", 56, (60, 50, 40, 255))
    tc(d, (540, 1230), "«следующая страница» исчезла", 44, GOLD + (255,), "Bold"); return im
def endings(lt, D):                                        # у всего есть конец
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); rows = [("КНИГА", "последняя страница", GOLD), ("СЕРИЯ", "титры", (230, 140, 100)), ("ГАЗЕТА", "задняя полоса", BLUE)]
    for i, (a, b, col) in enumerate(rows):
        k = ease((lt - i * D * 0.25) / 0.5); y = 560 + i * 230
        d.rounded_rectangle((100, y - 85, 980, y + 85), 22, fill=(32, 28, 38, int(240 * k)), outline=col + (int(255 * k),), width=4)
        tc(d, (330, y), a, 56, WHITE + (int(255 * k),)); tc(d, (730, y), b, 40, col + (int(255 * k),), "Bold")
    k = ease((lt - D * 0.75) / 0.5); tc(d, (540, 1180), "сигнал: пора остановиться", 56, WHITE + (int(255 * k),)); return im
def nosig(lt, D):
    im = feed(lt, D); d = ImageDraw.Draw(im, "RGBA"); k = ease((lt - 0.5) / 0.6)
    d.rounded_rectangle((180, 1170, 900, 1290), 26, fill=(10, 10, 14, int(235 * k)), outline=RED + (int(255 * k),), width=5); tc(d, (540, 1230), "СИГНАЛА «ХВАТИТ» НЕТ", 52, WHITE + (int(255 * k),)); return im
def buttons(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.6)
    d.rounded_rectangle((140, 620, 940, 800), 30, fill=(150, 40, 46, int(255 * k))); tc(d, (540, 710), "ОСТАНОВИТЬСЯ — решение", 50, WHITE + (int(255 * k),))
    d.rounded_rectangle((140, 880, 940, 1060), 30, fill=(50, 50, 62, int(255 * k))); tc(d, (540, 970), "не делать ничего — само", 50, GREY + (int(255 * k),))
    k2 = ease((lt - D * 0.6) / 0.6); tc(d, (540, 1130), "не слабая воля —", 62, WHITE + (int(255 * k2),)); tc(d, (540, 1210), "устройство ленты", 62, GOLD + (int(255 * k2),)); return im
def timer(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.7)
    d.ellipse((290, 430, 790, 930), outline=GOLD + (int(255 * k),), width=14); tc(d, (540, 680), "10:00", 130, WHITE + (int(255 * k),))
    tc(d, (540, 1050), "«ТРИ ВИДЕО» ИЛИ ТАЙМЕР", 52, GOLD + (int(255 * k),)); tc(d, (540, 1140), "КОНЕЦ СТАВИШЬ ТЫ", 66, WHITE + (int(255 * k),)); return im

SCENES = [
    ("Автор бесконечной ленты о ней жалеет.", "SUB", "", hook_feed, "", None),
    ("Это Аза Р+аскин. | По его словам, в две тысячи шестом он придумал прокрутку без страниц.", "SUB", "", raskin, "", None),
    ("Хотел как лучше: чтобы не нажимать «следующая страница».", "SUB", "", pages, "", None),
    ("Но у книги есть последняя страница. | У серии — титры. | Это были сигналы: пора остановиться.", "SUB", "", endings, "", None),
    ("Сигнала в ленте нет. | Следующее видео начинается раньше, чем ты решил, смотреть ли его.", "SUB", "", nosig, "", None),
    ("Остановиться теперь — отдельное решение. | Поэтому дело не в слабой воле.", "SUB", "", buttons, "", None),
    ("Поставь конец сам, до того как открыл: | три видео или таймер на десять минут.", "SUB", "", timer, "", None),
    ("Отправь тому, кто зашёл на минутку. | Подпишись.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ,", "КТО ЗАШЁЛ НА МИНУТКУ"), "ПОДПИШИСЬ", ("будут ещё", "ролики")), "", None),
]
