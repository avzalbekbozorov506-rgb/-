"""Неделя «ВЕСЫ» · ролик 1.1 · «Дофамин — не гормон счастья». Источник: Berridge & Robinson, Brain Research Reviews, 1998
(https://pubmed.ncbi.nlm.nih.gov/9858756/): после почти полного истощения дофамина крысы перестают сами искать еду, но реакции «нравится» на сладкое сохраняют.
Картины — The Met (CC0): Эль Греко и Виллем Калф. Графика (крыса, стрелки, телефон) — своя, рисуется кодом."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from _voice3 import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
HEAD = ("НАУКА О ЖЕЛАНИЯХ", "ДОФАМИН")
TITLE = ("", "", "")
HOOK = ("ДОФАМИН —\nНЕ ГОРМОН СЧАСТЬЯ", 2.8)
HOOK_SIZE = 80
HOOK_Y = 520
TAIL = 1.0
GAP = 0.35
PROG = [[50, 57, 62, 65], [46, 53, 58, 62]]
MUSIC = ("music/ogv_aria.mp3", 0)   # Bach, Goldberg Aria — Kimiko Ishizaka, The Open Goldberg Variations, CC0 1.0 (archive.org/details/The_Open_Goldberg_Variations-11823)
SAY = {"Берридж": "Б+ерридж"}

GOLD, WHITE, GREY, RED = (214, 178, 112), (246, 240, 228), (150, 140, 128), (200, 40, 46)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bg():
    im = Image.new("RGBA", (W, H), (16, 14, 20, 255)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = abs(y - 900) / 900; d.rectangle((0, y, W, y + 4), fill=(int(26 - 12 * k), int(22 - 10 * k), int(30 - 12 * k), 255))
    return im
def text_c(d, xy, t, f, fill, anchor="mm"): d.text(xy, t, font=f, fill=fill, anchor=anchor)

# --- сцена 0: «гормон счастья» перечёркивается ---
def card_strike(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA"); f = sans("Black", 112)
    a = 255 if lt < 1.4 else int(255 - 150 * ease((lt - 1.4) / 0.6))
    text_c(d, (W // 2, 1010), "ГОРМОН", f, WHITE + (a,)); text_c(d, (W // 2, 1140), "СЧАСТЬЯ", f, WHITE + (a,))
    k = ease((lt - 1.2) / 0.35)
    if k > 0: d.line((150, 1160, 150 + (W - 300) * k, 990), fill=RED + (255,), width=18)
    return im

# --- сцена 2: крыса, миска, лампочки «хорошо / хочу» ---
def rat(d, x, y, lt, lick):
    body = (150, 146, 154, 255); dark = (96, 92, 100, 255); pink = (226, 150, 160, 255)
    bob = 2 * math.sin(lt * 3)
    d.line([(x - 150, y - 20), (x - 230, y - 80 + 10 * math.sin(lt * 2)), (x - 300, y - 40)], fill=pink, width=9, joint="curve")   # хвост
    d.ellipse((x - 170, y - 105 + bob, x + 60, y + 40), fill=body)                                                               # тело
    d.polygon([(x + 20, y - 95 + bob), (x + 150, y - 50 + bob), (x + 175, y - 28 + bob), (x + 140, y - 4 + bob), (x + 30, y + 20 + bob)], fill=body)  # голова
    d.ellipse((x + 160, y - 38 + bob, x + 182, y - 18 + bob), fill=pink)                                                          # нос
    d.ellipse((x + 18, y - 135 + bob, x + 78, y - 80 + bob), fill=dark); d.ellipse((x + 30, y - 124 + bob, x + 66, y - 90 + bob), fill=pink)   # ухо
    d.ellipse((x + 98, y - 62 + bob, x + 114, y - 46 + bob), fill=(10, 10, 12, 255))                                              # глаз
    if lick > 0: d.ellipse((x + 150, y - 8 + bob, x + 150 + 46 * lick, y + 14 + bob), fill=(236, 90, 110, 255))                   # язык
    for lx in (-100, 10): d.rounded_rectangle((x + lx, y + 20, x + lx + 22, y + 74), 8, fill=dark)                                # лапы
def lamp(d, x, y, label, on, col):
    for r, a in ((95, 40), (70, 70)) if on else ():
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))
    d.ellipse((x - 48, y - 48, x + 48, y + 48), fill=(col if on else (58, 54, 62)) + (255,), outline=(220, 215, 205, 255), width=4)
    text_c(d, (x, y + 125), label, sans("Black", 46), WHITE + ((255 if on else 120),))
def rat_scene(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 1010, W, 1030), fill=(60, 52, 48, 255))
    lamp(d, 330, 470, "ХОРОШО", lt > 0.6, (120, 200, 120)); lamp(d, 750, 470, "ХОЧУ", False, (230, 90, 70))
    lick = 0.5 + 0.5 * math.sin(lt * 14) if 0.6 < lt < D * 0.5 else 0.0
    rat(d, 380, 970, lt, max(lick, 0))
    d.pieslice((690, 930, 930, 1090), 0, 180, fill=(140, 180, 200, 255)); d.ellipse((690, 930, 930, 990), fill=(236, 226, 196, 255))
    k = ease((lt - D * 0.5) / 0.6)
    if k > 0:
        for i in range(8): d.line((520 + i * 20, 940, 530 + i * 20, 940), fill=GREY + (int(220 * k),), width=5)
        text_c(d, (W // 2, 1180), "любит — но не идёт", sans("Black", 62), GOLD + (int(255 * k),))
    return im

# --- сцена 3: «хочу» тянется вперёд, «хорошо» остаётся на месте ---
def wants_scene(lt, D):
    im = bg(); d = ImageDraw.Draw(im, "RGBA")
    k = ease(lt / (D * 0.55)); x1 = 220 + (W - 360) * k
    text_c(d, (W // 2, 480), "ХОЧУ", sans("Black", 100), (240, 120, 100, 255))
    d.line((200, 600, x1, 600), fill=(240, 120, 100, 255), width=16); d.polygon([(x1, 560), (x1 + 50, 600), (x1, 640)], fill=(240, 120, 100, 255))
    text_c(d, (W // 2, 800), "ХОРОШО", sans("Black", 100), (140, 210, 140, 255))
    d.ellipse((200 - 22, 910 - 22, 200 + 22, 910 + 22), fill=(140, 210, 140, 255))
    k2 = ease((lt - D * 0.6) / 0.5)
    if k2 > 0: text_c(d, (W // 2, 1110), "ХОЧУ ≠ ХОРОШО", sans("Black", 86), GOLD + (int(255 * k2),))
    return im

# --- сцена 4: натюрморт + светящийся телефон на столе ---
def phone_on_table(im):
    im = im.convert("RGBA"); w, h = im.size; lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pw, ph = int(w * 0.12), int(h * 0.22); x0, y0 = int(w * 0.70), int(h * 0.58)
    for r in (3.2, 2.2, 1.5):
        d.rounded_rectangle((x0 - pw * (r - 1) / 2, y0 - ph * (r - 1) / 2, x0 + pw + pw * (r - 1) / 2, y0 + ph + ph * (r - 1) / 2), 40, fill=(150, 190, 255, int(26)))
    lay = lay.filter(ImageFilter.GaussianBlur(w * 0.03)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), 22, fill=(20, 22, 28, 255))
    d.rounded_rectangle((x0 + 7, y0 + 9, x0 + pw - 7, y0 + ph - 9), 16, fill=(188, 214, 255, 255))
    for k in range(4): d.rounded_rectangle((x0 + 18, y0 + 30 + k * ph * 0.2, x0 + pw - 18, y0 + 30 + k * ph * 0.2 + ph * 0.12), 8, fill=(120, 150, 205, 255))
    lay = lay.rotate(6, center=(x0 + pw / 2, y0 + ph / 2), resample=Image.BICUBIC)
    im.alpha_composite(lay); return im
PREP = {"met_436805": phone_on_table}

# --- сцена 5: призыв ---
def cta_card(l1, l2, l3):                                  # финальная сцена: «отправь» + «подпишись»
    def f(lt, D):
        im = bg(); d = ImageDraw.Draw(im, "RGBA"); k = ease(lt / 0.7)
        for i, (t, sz, col) in enumerate(((l1[0], 56, GOLD), (l1[1], 56, GOLD), (l2, 92, WHITE), (l3[0], 46, GREY), (l3[1], 46, GREY))):
            text_c(d, (W // 2, (700, 800, 980, 1100, 1170)[i]), t, sans("Black", sz), col + (int(255 * k),))
        return im
    return f

C_G = "Эль Греко. Святой Иероним, около 1610. The Met"
C_K = "В. Калф. Натюрморт, 1659. The Met (телефон дорисован)"
SCENES = [
    ("Дофамин — не гормон счастья. | Так говорят все, но учёные видят иначе.", "SUB", "", card_strike, "", None),
    ("Нейробиолог Кент Берридж почти полностью лишал крыс дофамина.", "SUB", "ОПЫТЫ КЕНТА БЕРРИДЖА", "_greco_v", C_G, (1.0, 1.08, (0.5, 0.5), (0.5, 0.47))),
    ("Вливал им в рот сладкий раствор, | и они облизывались, как от удовольствия. | Но сами к нему не шли. | Даже голодные.", "SUB", "", rat_scene, "", None),
    ("Значит, радость — одно, а желание — другое. | Дофамин отвечает за «хочу», | а не за «хорошо». | Он гонит тебя к награде, | а будет ли она приятной, ему всё равно.", "SUB", "", wants_scene, "", None),
    ("Поэтому можно хотеть и хотеть — | и не радоваться, когда получил. | Это не твоя слабость. | Так устроен мозг. | Хотеть — не значит радоваться.", "SUB", "", "met_436805", C_K, (1.0, 1.15, (0.5, 0.52), (0.62, 0.64))),
    ("Отправь тому, кто вечно чего-то хочет. | Подпишись — дальше про пустоту после радости.", "SUB", SUB_PLATE, cta_card(("ОТПРАВЬ ТОМУ,", "КТО ВЕЧНО ЧЕГО-ТО ХОЧЕТ"), "ПОДПИШИСЬ", ("следующий ролик:", "почему после радости пусто")), "", None),
]
