"""Неделя «ВЕСЫ» · ролик 1.2 · «После радости — пустота». Источник: Solomon & Corbit, «An opponent-process theory of motivation. I. Temporal dynamics
of affect», Psychological Review, 81(2), 119–145, 1974 (https://pubmed.ncbi.nlm.nih.gov/4817611/). Применение к сериалам и ленте — аналогия авторов ролика (сказано в тексте).
Картина — The Met (CC0), графика своя."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
HEAD = ("НАУКА О ЖЕЛАНИЯХ", "ПРОТИВОПОЛОЖНЫЕ ПРОЦЕССЫ")
TITLE = ("", "", "")
HOOK = ("ПОСЛЕ СЕРИИ —\nПУСТОТА. ПОЧЕМУ?", 2.8)
HOOK_SIZE = 80
HOOK_Y = 520
TAIL = 1.4
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0 (archive.org/details/The_Open_Goldberg_Variations-11823)
SAY = {"Соломон": "С+оломон", "Корбит": "К+орбит"}

GOLD, WHITE, GREY, RED = (214, 178, 112), (246, 240, 228), (150, 140, 128), (200, 40, 46)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bg():
    im = Image.new("RGBA", (W, H), (16, 14, 20, 255)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = abs(y - 900) / 900; d.rectangle((0, y, W, y + 4), fill=(int(26 - 12 * k), int(22 - 10 * k), int(30 - 12 * k), 255))
    return im
def text_c(d, xy, t, f, fill): d.text(xy, t, font=f, fill=fill, anchor="mm")

def titles(lt, D):                                         # сцена 0: титры «Конец серии» гаснут на тёмной комнате
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow); a = int(90 * (1 - ease(lt / 3.0)) + 6)
    g.rectangle((250, 700, 830, 1100), fill=(120, 160, 255, a)); glow = glow.filter(ImageFilter.GaussianBlur(70)); im.alpha_composite(glow)
    d.rounded_rectangle((300, 760, 780, 1040), 18, fill=(10, 12, 18, 255), outline=(60, 70, 90, 255), width=5)
    k = 1 - ease((lt - 1.5) / 1.5); text_c(d, (540, 900), "КОНЕЦ СЕРИИ", sans("Black", 56), (230, 235, 245, int(255 * k)))
    k2 = ease((lt - 2.2) / 0.8); text_c(d, (540, 1180), "Серия закончилась. А радости нет.", sans("Bold", 44), GOLD + (int(255 * k2),))
    return im

def plaque(lt, D):                                         # сцена 2: «Соломон и Корбит · 1974» (без фото учёных)
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.8)
    d.rounded_rectangle((120, 700, 960, 1100), 24, outline=GOLD + (int(255 * k),), width=5, fill=(30, 26, 34, int(240 * k)))
    text_c(d, (540, 800), "СОЛОМОН И КОРБИТ", sans("Black", 74), WHITE + (int(255 * k),))
    text_c(d, (540, 910), "1974", sans("Black", 120), GOLD + (int(255 * k),))
    text_c(d, (540, 1020), "Psychological Review", sans("Bold", 40), GREY + (int(255 * k),))
    return im

def curve(lt, D):                                          # сцена 3: линия чувства: подъём → провал ниже линии → возврат
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); x0, x1, base = 120, 960, 900
    d.line((x0, base, x1, base), fill=GREY + (255,), width=4); text_c(d, (540, base + 45), "обычное состояние", sans("Bold", 34), GREY + (255,))
    pts = []
    for i in range(0, 101):
        u = i / 100; x = x0 + (x1 - x0) * u
        y = base - 330 * math.exp(-((u - 0.25) / 0.07) ** 2) + 210 * math.exp(-((u - 0.52) / 0.12) ** 2) * (1 if u > 0.35 else 0) - 20 * math.exp(-((u - 0.8) / 0.08) ** 2)
        pts.append((x, y))
    k = ease(lt / (D * 0.7)); n = max(2, int(len(pts) * k))
    for a, b in zip(pts[:n - 1], pts[1:n]): d.line((a, b), fill=((240, 200, 110) if b[1] < base - 5 else (130, 150, 230)) + (255,), width=12)
    if k > 0.3: text_c(d, (x0 + (x1 - x0) * 0.25, base - 400), "сильное чувство", sans("Black", 44), (240, 200, 110, 255))
    if k > 0.65: text_c(d, (x0 + (x1 - x0) * 0.52, base + 290), "противоположное", sans("Black", 44), (140, 160, 235, 255))
    if k > 0.95: text_c(d, (540, 380), "сначала чувство → потом противоположное", sans("Bold", 40), WHITE + (255,))
    return im

def person(d, x, y, col, scale=1.0, arms=0.0):             # простой силуэт парашютиста: купол, лямки, человек
    s = scale; d.pieslice((x - 150 * s, y - 330 * s, x + 150 * s, y - 30 * s), 180, 360, fill=col + (255,))
    for dx in (-140, -70, 70, 140): d.line((x + dx * s, y - 180 * s, x, y + 20 * s), fill=GREY + (255,), width=3)
    d.ellipse((x - 22 * s, y + 6 * s, x + 22 * s, y + 50 * s), fill=(230, 200, 170, 255)); d.rounded_rectangle((x - 22 * s, y + 52 * s, x + 22 * s, y + 140 * s), 8, fill=(70, 80, 110, 255))
def parachutists(lt, D):                                   # сцена 4: новичок и опытный
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    person(d, 300, 760, (230, 120, 90), 1.0); person(d, 780, 760, (110, 160, 230), 1.0)
    k = ease((lt - 0.8) / 0.8)
    text_c(d, (300, 1020), "НОВИЧОК", sans("Black", 48), WHITE + (255,)); text_c(d, (780, 1020), "ОПЫТНЫЙ", sans("Black", 48), WHITE + (255,))
    text_c(d, (300, 1090), "страх → облегчение", sans("Bold", 34), (240, 150, 130, int(255 * k)))
    text_c(d, (780, 1090), "страх слабее,", sans("Bold", 34), (140, 180, 245, int(255 * k))); text_c(d, (780, 1135), "удовольствие сильнее", sans("Bold", 34), (140, 180, 245, int(255 * k)))
    return im

def series(lt, D):                                         # сцена 5: 1 серия — радость, 3 — тянет, 5 — пустота (аналогия)
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); rows = [("1 СЕРИЯ", "радость", (240, 200, 110)), ("3 СЕРИЯ", "просто тянет", (230, 140, 100)), ("5 СЕРИЯ", "пустота", (130, 150, 230))]
    for i, (a, b, col) in enumerate(rows):
        k = ease((lt - i * D * 0.22) / 0.5); y = 520 + i * 200
        d.rounded_rectangle((120, y - 70, 960, y + 70), 22, fill=(32, 28, 38, int(240 * k)), outline=col + (int(255 * k),), width=4)
        text_c(d, (330, y), a, sans("Black", 56), WHITE + (int(255 * k),)); text_c(d, (720, y), b, sans("Bold", 50), col + (int(255 * k),))
    k = ease((lt - D * 0.7) / 0.5); text_c(d, (540, 1180), "наша аналогия, не вывод учёных", sans("Bold", 40), GOLD + (int(255 * k),))
    return im

def cta_card(l1, l2, l3):                                  # финальная сцена: «отправь» + «подпишись»
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.7)
        for i, (t, sz, col) in enumerate(((l1[0], 56, GOLD), (l1[1], 56, GOLD), (l2, 92, WHITE), (l3[0], 46, GREY), (l3[1], 46, GREY))):
            text_c(d, (W // 2, (700, 800, 980, 1100, 1170)[i]), t, sans("Black", sz), col + (int(255 * k),))
        return im
    return f

C_D = "Антон Диффенбах. Окно, 1856. The Met"
SCENES = [
    ("Досмотрел серию — и вместо радости пустота. | Почему?", "SUB", "", titles, "", None),
    ("Соломон и Корбит описали это в тысяча девятьсот семьдесят четвёртом году.", "SUB", "", plaque, "", None),
    ("Вот их теория: за сильным чувством следует противоположное.", "SUB", "", curve, "", None),
    ("Начинающие парашютисты боятся прыжка, а после приземления чувствуют облегчение. | У опытных страх слабее, а удовольствие после прыжка сильнее. | Это теория противоположных процессов.", "SUB", "", parachutists, "", None),
    ("Для ленты это лишь аналогия, не вывод учёных. | Первая серия — радость, третья — тянет, после пятой — пустота.", "SUB", "", series, "", None),
    ("У радости есть тень.", "SUB", "", "dieffenbach_window", C_D, (1.0, 1.12, (0.5, 0.45), (0.5, 0.4))),
    ("Отправь тому, кто после серии чувствует пустоту. | Подпишись — будут ещё ролики.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ, КТО ПОСЛЕ", "СЕРИИ ЧУВСТВУЕТ ПУСТОТУ"), "ПОДПИШИСЬ", ("будут ещё", "ролики")), "", None),
]
