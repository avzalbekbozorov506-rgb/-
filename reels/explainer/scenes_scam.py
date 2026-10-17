"""Сатира «Как я заработал миллион за 2 недели с Claude Code» — и честный поворот: так не бывает, нужно работать."""
import math
from scenes_x import *
HEADER = "СЕКРЕТ ДЕНЕГ · РАЗБОР"
SCRIPT = [
 ("hook",   "Подпишись, и узнай, как я заработал миллион рублей за две недели с Клод Код."),
 ("day1",   "День первый. Я открыл Клод Код и написал: сделай сайт, который приносит деньги."),
 ("site",   "Он собрал сайт за двадцать минут. Красиво, быстро, как в рекламе."),
 ("money",  "Через неделю пошли заказы. Деньги капали каждую минуту. А на четырнадцатый день на счёте был миллион."),
 ("twist",  "Шучу. Так не бывает."),
 ("real",   "Нейросеть пишет код быстро. Но идею, клиентов и рекламу она за тебя не найдёт. На это уходят месяцы."),
 ("gurus",  "Те, кто обещает миллион за две недели, обычно продают курс про то, как заработать миллион."),
 ("end3",   "Хочешь результат, работай. Нейросеть поможет, но не заменит тебя. Подпишись, будем разбирать честно. И отправь тому, кто верит в быстрый миллион."),
]
def window(d, x0, y0, x1, y1, title, col=(20, 28, 48)):
    d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], 24 * K, fill=col, outline=CY, width=3 * K)
    d.rectangle([x0 * K, y0 * K, x1 * K, (y0 + 54) * K], fill=(30, 44, 74))
    for i, c in enumerate(((255, 95, 90), (255, 190, 50), (40, 200, 80))): circ(d, ((x0 + 36 + i * 36) * K, (y0 + 27) * K), 10 * K, fill=c)
    d.text(((x0 + 160) * K, (y0 + 12) * K), title, font=F(26 * K, "Bold"), fill=(150, 170, 200))
def sc_hook(d, t, T):
    big(d, 540, 400, "1 000 000 ₽", YEL, 150, ease(t / .5))
    if t > .5: tag(d, 540, 640, "ЗА 14 ДНЕЙ", WHITE, 54, fill=(10, 20, 36), anchor="c")
    if t > 1.2: tag(d, 540, 780, "С Claude Code", CY, 44, anchor="c")
    for k in range(18):
        u = (t * .6 + k / 18) % 1; x = 100 + (k * 53) % 880; y = 900 + 500 * u
        d.text((x * K, y * K), "₽", font=F(54 * K, "Black"), fill=dim(YEL, .6 * (1 - u)))
def sc_day1(d, t, T):
    window(d, 90, 330, 990, 1000, "claude-code — терминал")
    s = "› сделай сайт, который приносит деньги"; n = int(min(len(s), max(0, (t - .5) * 22)))
    d.text((140 * K, 450 * K), s[:n] + ("█" if int(t * 3) % 2 == 0 else " "), font=F(34 * K, "Bold"), fill=GRN)
    tag(d, 540, 1100, "ДЕНЬ № 1", YEL, 60, fill=(40, 28, 6), anchor="c")
def sc_site(d, t, T):
    window(d, 90, 330, 990, 1100, "мой-сайт.ru")
    p = ease(t / 3.0)
    d.rectangle([140 * K, 420 * K, (140 + 800) * K, (420 + 90 * p) * K], fill=(60, 120, 220))
    for i in range(3): d.rounded_rectangle([(140 + i * 275) * K, 560 * K, (140 + i * 275 + 250) * K, (560 + 260 * min(1, max(0, p * 3 - i * .8))) * K], 18 * K, fill=(36, 52, 84))
    d.rectangle([140 * K, 880 * K, (140 + 800 * min(1, p * 1.2)) * K, 920 * K], fill=(255, 190, 40))
    tag(d, 540, 1200, f"{int(20 * p)} МИНУТ", CY, 64, anchor="c")
def sc_money(d, t, T):
    v = int(1_000_000 * ease(t / (T - 1.0))); day = 1 + int(13 * ease(t / (T - 1.0)))
    big(d, 540, 380, f"{v:,}".replace(",", " ") + " ₽", GRN, 100)
    tag(d, 540, 600, f"ДЕНЬ № {day}", YEL, 48, fill=(40, 28, 6), anchor="c")
    pts = [(120 + 840 * i / 40, 1200 - 440 * (i / 40) ** 2 * ease(t / (T - 1.0) + .2)) for i in range(41)]
    d.line([(x * K, y * K) for x, y in pts], fill=GRN, width=8 * K)
    for k in range(10):
        u = (t * 1.5 + k / 10) % 1; circ(d, ((200 + k * 80) * K, (760 + 40 * math.sin(k)) * K), 14 * K, fill=dim(YEL, 1 - u * .8))
def sc_twist(d, t, T):
    v = int(1_000_000 * max(0, 1 - ease(t / 1.2))); big(d, 540, 420, f"{v:,}".replace(",", " ") + " ₽", GRN if v > 0 else RED, 100)
    if t > 1.0:
        d.rounded_rectangle([160 * K, 640 * K, 920 * K, 840 * K], 20 * K, outline=RED, width=10 * K)
        d.text((540 * K, 740 * K), "ШУЧУ", font=F(130 * K, "Black"), fill=RED, anchor="mm")
    if t > 1.7: tag(d, 540, 960, "ТАК НЕ БЫВАЕТ", WHITE, 60, fill=(40, 10, 14), anchor="c")
def sc_real(d, t, T):
    steps = [("ИДЕЯ", RED, "нужна твоя"), ("ПРОДУКТ", GRN, "Claude Code ускоряет"), ("КЛИЕНТЫ", RED, "ищешь ты"), ("РЕКЛАМА И ПОДДЕРЖКА", RED, "месяцы работы")]
    for i, (name, col, sub) in enumerate(steps):
        y = 360 + i * 210; a = ease((t - .4 - i * .9) / .5)
        if a <= 0: continue
        d.rounded_rectangle([140 * K, y * K, 940 * K, (y + 150) * K], 24 * K, fill=(16, 26, 46), outline=dim(col, a), width=5 * K)
        d.text((190 * K, (y + 28) * K), name, font=F(46 * K, "Black"), fill=dim(WHITE, a)); d.text((190 * K, (y + 92) * K), sub, font=F(30 * K, "Bold"), fill=dim(col, a))
        if i < 3: arrow(d, 540, y + 152, 540, y + 205, dim(CY, a), 5, 16)
def sc_gurus(d, t, T):
    a = ease(t / .6)
    d.text((540 * K, 420 * K), "ОБЕЩАЮТ", font=F(70 * K, "Black"), fill=dim(WHITE, a), anchor="mm"); big(d, 540, 480, "МИЛЛИОН", YEL, 120, a)
    if t > 2.5:
        arrow(d, 540, 780, 540, 940, RED, 10, 30)
        d.rounded_rectangle([140 * K, 960 * K, 940 * K, 1180 * K], 28 * K, fill=(40, 10, 14), outline=RED, width=6 * K)
        d.text((540 * K, 1030 * K), "ПРОДАЮТ", font=F(54 * K, "Black"), fill=WHITE, anchor="mm"); d.text((540 * K, 1110 * K), "КУРС", font=F(80 * K, "Black"), fill=RED, anchor="mm")
def sc_end3(d, t, T):
    big(d, 540, 400, "РАБОТА", GRN, 170, ease(t / .5))
    if t > 1.0: d.text((540 * K, 640 * K), "а не чудо", font=F(70 * K, "Bold"), fill=WHITE, anchor="mm")
    if t > 2.5: tag(d, 540, 800, "НЕЙРОСЕТЬ ПОМОЖЕТ, НО НЕ ЗАМЕНИТ ТЕБЯ", CY, 30, anchor="c")
    if t > 5.0: tag(d, 540, 1000, "ПОДПИШИСЬ · РАЗБИРАЕМ ЧЕСТНО", YEL, 44, fill=(40, 28, 6), anchor="c")
SCENES = dict(hook=sc_hook, day1=sc_day1, site=sc_site, money=sc_money, twist=sc_twist, real=sc_real, gurus=sc_gurus, end3=sc_end3)
