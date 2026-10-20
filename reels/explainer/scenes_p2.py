"""Часть 2: «Как Tesla Roadster разгоняется до 100 км/ч за 0,81 с» — физика: предел шин ≈1,26 g, нужно ≈3,4 g, вентиляторы, 4 сопла (>80 кН по заявлению Tesla), подвох с заправкой."""
import math
from scenes_x import *
HEADER = "ФИЗИКА · TESLA ROADSTER · ЧАСТЬ 2"
SCRIPT = [
 ("start",  "Почти сто километров в час меньше чем за секунду. Шины так не умеют."),
 ("tires",  "Шина толкает машину вперёд, пока не начнёт проскальзывать. Предел — около одного и трёх десятых джи."),
 ("need",   "Одними шинами до шестидесяти миль в час — больше двух секунд. А за восемьдесят одну сотую нужно почти три с половиной джи."),
 ("fans2",  "Первая добавка — вентиляторы. Они прижимают машину к асфальту, и шины держат сильнее."),
 ("noz",    "Вторая — четыре сопла сзади. По заявлению Т+эсла, тяга больше восьмидесяти килоньют+онов, а воздух вылетает быстрее звука."),
 ("math",   "Для машины примерно в тысячу семьсот килограммов это почти пять джи. С запасом."),
 ("slip",   "И эта тяга не зависит от сцепления. Шины могут скользить, а машина всё равно летит вперёд."),
 ("catch",  "Но есть подвох. Воздух хранится под давлением около семисот атмосфер, а заправка баллонов сейчас занимает шесть-семь часов."),
 ("end2",   "Цифры пока заявлены самой Т+эсла, независимой проверки не было. Верить ли им? Пиши в комментариях. Отправь тому, кто любит машины. Подпишись, будет ещё."),
]

def gmeter(d, x, y_top, y_bot, gmax, cur, marks=(), title="ПЕРЕГРУЗКА, g"):
    d.text((x * K, (y_top - 56) * K), title, font=F(22 * K, "Bold"), fill=(150, 170, 200))
    d.rectangle([x * K, y_top * K, (x + 70) * K, y_bot * K], outline=CY, width=2 * K)
    h = (y_bot - y_top) * min(cur, gmax) / gmax
    d.rectangle([x * K, (y_bot - h) * K, (x + 70) * K, y_bot * K], fill=(20, 110, 150))
    for g in range(int(gmax) + 1):
        yy = y_bot - (y_bot - y_top) * g / gmax; d.line([(x + 70) * K, yy * K, (x + 84) * K, yy * K], fill=CY, width=2 * K)
        d.text(((x + 92) * K, (yy - 14) * K), str(g), font=F(24 * K, "Bold"), fill=(150, 170, 200))
    for g, col, label in marks:
        yy = y_bot - (y_bot - y_top) * g / gmax; d.line([(x - 20) * K, yy * K, (x + 90) * K, yy * K], fill=col, width=4 * K)
        d.text(((x + 140) * K, (yy - 16) * K), label, font=F(26 * K, "ExtraBold"), fill=col)

def smoke(d, x, y, t, n=10):
    for k in range(n):
        u = (t * 2.0 + k / n) % 1; circ(d, ((x - 60 * u - 10 * k % 30) * K, (y - 20 - 50 * u) * K), (8 + 26 * u) * K, fill=dim((200, 205, 215), (1 - u) * .7))

def sc_start(d, t, T):
    G = 1180; ground(d, G); t0 = .6
    run = min(1.0, max(0.0, (t - t0) / .81)); x = 150 + 700 * run * run
    for k in range(14):                                          # линии скорости
        if run > 0.05: yy = G - 40 - 14 * k; L = 220 * run; d.line([(x - 240 - L) * K, yy * K, (x - 240) * K, yy * K], fill=dim(CY, .5), width=3 * K)
    car(d, x, G, 0, .85, 1, 1)
    sec = min(.81, max(0.0, t - t0)); big(d, 540, 430, f"{sec:.2f}".replace(".", ",") + " с", YEL, 200)
    if t > t0 + .81 + .2: tag(d, 540, 760, "0 → 60 миль/ч  ≈ 96 км/ч", CY, 40, anchor="c")
    if t > 3.0: tag(d, 540, 870, "ЗАЯВЛЕНО TESLA · ТОП-КОМПЛЕКТАЦИЯ", (110, 140, 170), 24, anchor="c")

def sc_tires(d, t, T):
    G = 1250; ground(d, G); x = 560
    car(d, x, G, 0, 1.0, 1, 1)
    cur = min(1.26, 1.26 * ease(t / 2.0))
    gmeter(d, 90, 330, 1180, 4.0, cur, marks=[(1.26, RED, "ПРЕДЕЛ ШИН ≈ 1,3 g")])
    if t > 2.2:
        smoke(d, x - 130, G, t); tag(d, 540, 400, "ШИНА ПРОСКАЛЬЗЫВАЕТ", RED, 36, fill=(40, 10, 14), anchor="c")
    else: tag(d, 540, 400, "СЦЕПЛЕНИЕ ШИНЫ", CY, 36, anchor="c")
    arrow(d, x - 40, G - 150, x + 160, G - 150, CY, 8)

def sc_need(d, t, T):
    gmeter(d, 90, 330, 1180, 4.0, 3.4 * ease(t / 1.5), marks=[(1.26, RED, "ШИНЫ ≈ 1,3"), (3.38, YEL, "НУЖНО ≈ 3,4")])
    if t > 1.8:
        a = 1.26 / 4.0; yy1 = 1180 - 850 * 1.26 / 4.0; yy2 = 1180 - 850 * 3.38 / 4.0
        d.line([560 * K, yy1 * K, 560 * K, yy2 * K], fill=WHITE, width=5 * K); tag(d, 590, (yy1 + yy2) / 2 - 20, "НЕ ХВАТАЕТ ≈ 2,1 g", WHITE, 30)
    for i, (lab, secs, col) in enumerate([("ТОЛЬКО ШИНЫ", 2.2, RED), ("ЗАЯВЛЕНО", .81, GRN)]):
        y0 = 1260 + i * 80; w = 680 * secs / 2.2 * ease((t - 1.0 - i * .6) / .8)
        d.rectangle([90 * K, y0 * K, (90 + max(0, w)) * K, (y0 + 54) * K], fill=dim(col, .75))
        if w > 40: d.text(((100) * K, (y0 + 8) * K), f"{lab} · {secs:.2f}".replace(".", ",") + " с", font=F(28 * K, "ExtraBold"), fill=WHITE)

def sc_fans2(d, t, T):
    G = 1240; ground(d, G); Tc = car(d, 560, G, 0, 1.55, 1, 1, xray=1, tt=t)
    for xx in (330, 450, 560, 670, 790):
        arrow(d, xx, 520 + 12 * math.sin(t * 6 + xx), xx, 760, GRN, 9, 26)
    tag(d, 540, 400, "ПРИЖИМ  ↓", GRN, 38, fill=(6, 40, 30), anchor="c")
    for k, fx in enumerate(FANS):
        p = Tc((fx, -44)); circ(d, p, 9 * K, fill=CY)
    gmeter(d, 90, 330, 1180, 4.0, 1.26 + .5 * ease((t - .8) / 1.5), marks=[(1.26, RED, "БЫЛ ПРЕДЕЛ")], title="ПРЕДЕЛ ШИН")
    if t > 2.3: tag(d, 540, 1330, "ШИНЫ ДЕРЖАТ СИЛЬНЕЕ", CY, 32, anchor="c")

def sc_noz(d, t, T):
    G = 1180; ground(d, G); Tc = car(d, 640, G, 0, 1.45, 1, 1, xray=1, tt=t)
    for j, zz in enumerate((-100, -76, -56, -38)):                   # четыре сопла сзади
        p = Tc((-222, zz)); circ(d, p, 9 * K, fill=ORG)
        if t > .7:
            for k in range(12):
                u = (t * 3 + k / 12 + j * .13) % 1; circ(d, (p[0] - (30 + 330 * u) * K, p[1] + (j - 1.5) * 10 * u * K), (7 - 5 * u) * K, fill=dim(WHITE, 1 - u))
    if t > 1.2: tag(d, 540, 340, "ТЯГА  > 80 кН", YEL, 56, fill=(40, 28, 6), anchor="c")
    if t > 2.8: tag(d, 540, 470, "ВОЗДУХ БЫСТРЕЕ ЗВУКА", ORG, 34, fill=(40, 22, 6), anchor="c")
    if t > 4.0: tag(d, 540, 1380, "ЗАЯВЛЕНИЕ TESLA, НЕ ПРОВЕРЕНО НЕЗАВИСИМО", (110, 140, 170), 22, anchor="c")

def sc_math(d, t, T):
    lines = [("80 000 Н", YEL), ("÷", WHITE), ("1 700 кг", CY), ("≈ 47 м/с²", WHITE), ("≈ 4,8 g", GRN)]
    for i, (s, col) in enumerate(lines):
        if t > .3 + i * .55: big(d, 540, 330 + i * 150, s, col, 100 if i != 4 else 130, ease((t - .3 - i * .55) / .3))
    if t > 3.6: tag(d, 540, 1150, "НУЖНО БЫЛО ≈ 3,4 g", WHITE, 36, anchor="c")
    if t > 4.2: tag(d, 540, 1250, "МАССА ≈ 1,7 т — ОЦЕНКА ELECTREK", (110, 140, 170), 24, anchor="c")

def sc_slip(d, t, T):
    G = 1240; ground(d, G); x = lerp(260, 760, ease(t / (T - .5))); car(d, x, G, 0, 1.1, 1, 1, xray=0.0)
    smoke(d, x - 140, G, t, 14)
    for k in range(10):
        u = (t * 3 + k / 10) % 1; circ(d, ((x - 245 - 260 * u) * K, (G - 80 - 12 * (k % 3)) * K), (7 - 5 * u) * K, fill=dim(WHITE, 1 - u))
    tag(d, 540, 400, "ШИНЫ СКОЛЬЗЯТ — МАШИНА ЛЕТИТ", ORG, 34, fill=(40, 22, 6), anchor="c")
    if t > 1.5: tag(d, 540, 520, "ТЯГА НЕ ЗАВИСИТ ОТ СЦЕПЛЕНИЯ", GRN, 34, fill=(6, 40, 30), anchor="c")

def sc_catch(d, t, T):
    cx, cy = 540, 680
    d.ellipse([(cx - 210) * K, (cy - 210) * K, (cx + 210) * K, (cy + 210) * K], outline=CY, width=6 * K, fill=(8, 22, 40))
    d.text((cx * K, (cy - 300) * K), "БАЛЛОН: ≈ 700 атм", font=F(40 * K, "ExtraBold"), fill=CY, anchor="mm")
    p = seg(t, .6, 2.6); a = math.radians(-215 + 250 * (1 - p))
    d.line([cx * K, cy * K, (cx + 170 * math.cos(a)) * K, (cy + 170 * math.sin(a)) * K], fill=RED, width=10 * K)
    d.text((cx * K, (cy + 110) * K), "ПУСТО" if p > .95 else "расход…", font=F(34 * K, "Bold"), fill=RED if p > .95 else (150, 170, 200), anchor="mm")
    if t > 3.4:
        ccx, ccy = 170, 1170; d.ellipse([(ccx - 120) * K, (ccy - 120) * K, (ccx + 120) * K, (ccy + 120) * K], outline=YEL, width=6 * K)
        a1 = (t - 3.4) * 9; d.line([ccx * K, ccy * K, (ccx + 80 * math.cos(a1)) * K, (ccy + 80 * math.sin(a1)) * K], fill=YEL, width=6 * K); d.line([ccx * K, ccy * K, (ccx + 60 * math.cos(a1 / 12)) * K, (ccy + 60 * math.sin(a1 / 12)) * K], fill=YEL, width=8 * K)
        tag(d, 330, 1130, "ЗАПРАВКА 6–7 ЧАСОВ", YEL, 34, fill=(40, 28, 6))
        if t > 5.4: tag(d, 330, 1215, "TESLA ХОЧЕТ — 30 МИН", GRN, 28, fill=(6, 40, 30))

def sc_end2(d, t, T):
    cx, cy = 540, 600
    d.rounded_rectangle([(cx - 250) * K, (cy - 200) * K, (cx + 250) * K, (cy + 150) * K], 30 * K, fill=(20, 28, 48), outline=YEL, width=5 * K)
    d.text((cx * K, (cy - 60) * K), "ЗАЯВЛЕНО TESLA", font=F(54 * K, "Black"), fill=YEL, anchor="mm")
    d.text((cx * K, (cy + 40) * K), "независимой проверки", font=F(36 * K, "Bold"), fill=WHITE, anchor="mm"); d.text((cx * K, (cy + 90) * K), "пока не было", font=F(36 * K, "Bold"), fill=WHITE, anchor="mm")
    car(d, 540, 1000, 0, .9)
    if t > 3.2:
        tag(d, 540, 1100, "ВЕРИШЬ?", WHITE, 54, fill=(10, 20, 36), anchor="c")
        tag(d, 360, 1260, "ДА", GRN, 44, fill=(6, 40, 30)); tag(d, 600, 1260, "НЕТ", RED, 44, fill=(40, 10, 14))

SCENES = dict(start=sc_start, tires=sc_tires, need=sc_need, fans2=sc_fans2, noz=sc_noz, math=sc_math, slip=sc_slip, catch=sc_catch, end2=sc_end2)
