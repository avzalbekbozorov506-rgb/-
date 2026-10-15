"""Вне плана · эксперимент «аналог» (15.10): ролик-образец пользователя instagram.com/reel/DZlV701IH6w («Ваш мозг — это нейробиологический
сериал», Эго против Самости, 1:22). Повторено: схема «Представьте…» → Эго (быстрые награды, соревнование, забег) → «Но глубже…» → Самость
(Юнг: архетип целостности, Эрос как связующее начало, индивидуация); экран-триптих (верх и низ — синяя «нейронная» текстура, в центре
сменяющиеся картины), быстрая смена кадров, субтитры гротеском заглавными с подсветкой слова, женский низкий голос, без призыва.
Текст свой (чужой не копируем), голос — синтез Vosk (диктор 0), не клон. Картины — Art Institute of Chicago (CC0); текстура — своя генерация.
Юнг: Самость — архетип целостности и центр психики; Эрос — принцип связи (relatedness); индивидуация — становление самостью."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__)); from _voice2 import *
from PIL import Image, ImageDraw
HERE_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOSK = dict(speaker=0, rate=1.12, dot=240, stress=True)
VOICE_FX = "highpass=f=70,equalizer=f=180:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1.5:g=-2,acompressor=threshold=0.1:ratio=3,aecho=0.8:0.7:40:0.12"
GAP = 0.12
TAIL = 0.2
HEAD = ("КАРЛ ЮНГ", "ЭГО И САМОСТЬ")
TITLE = ("", "", "")
HOOK = ("ВАШ МОЗГ —\nЭТО СЕРИАЛ", 2.4)
HOOK_Y = 1330
TEXT_DY = 170
SUB_STYLE = "karaoke"
SUB_SANS = "ExtraBold"
SUB_CHARS = 20
QUOTE_SIZE = 62
BOT_ALPHA = 120
VIG = 80
GRAIN = 4.0
MUSIC = ("music/suk_meditation.mp3", 0)
PROG = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 63], [45, 52, 57, 61]]
# центр кадра: (имя, фокус x, фокус y) → триптих 1620×2880: текстура / картина / текстура
FOCUS = {"aic_encyc_anatomy": (0.5, 0.55), "aic_munch_omega_eyes": (0.5, 0.42), "aic_daumier_collector": (0.6, 0.45),
         "aic_stock_exchange": (0.5, 0.55), "aic_gerome_chariot": (0.5, 0.75), "aic_munch_scream": (0.5, 0.45),
         "aic_redon_waters": (0.5, 0.42), "aic_cock_labyrinth": (0.52, 0.55), "aic_redon_clouds": (0.5, 0.5),
         "aic_michelangelo_embrace": (0.55, 0.45), "aic_turner_boats": (0.4, 0.55), "aic_tangyin_tea": (0.15, 0.6),
         "aic_redon_shadow": (0.5, 0.4), "aic_eye_horus": (0.5, 0.5), "aic_etruscan_mirror": (0.5, 0.45), "aic_double_portrait": (0.5, 0.35), "aic_goya_maragato": (0.45, 0.5), "aic_munch_window": (0.55, 0.35)}
def _cover(im, w, h, fx, fy):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = min(max(int(fx * im.width - w / 2), 0), im.width - w); y = min(max(int(fy * im.height - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))
_k = [0]
def _tri(name):
    def f(im):
        W_, H_ = 1620, 2880; t0, t1 = 860, 1880; k = _k[0] = _k[0] + 1
        top = Image.open(f"{HERE_}/art/gen_neuro_{k % 4}.jpg").convert("RGB"); bot = Image.open(f"{HERE_}/art/gen_neuro_{(k + 2) % 4}.jpg").convert("RGB")
        c = Image.new("RGB", (W_, H_), (3, 6, 16))
        c.paste(_cover(top, W_, t0, 0.5, 0.5), (0, 0)); c.paste(_cover(bot, W_, H_ - t1, 0.5, 0.5), (0, t1))
        fx, fy = FOCUS.get(name, (0.5, 0.5)); c.paste(_cover(im.convert("RGB"), W_, t1 - t0, fx, fy), (0, t0))
        d = ImageDraw.Draw(c); d.rectangle((0, t0 - 6, W_, t0 + 2), fill=(0, 0, 0)); d.rectangle((0, t1 - 2, W_, t1 + 6), fill=(0, 0, 0))
        return c
    return f
Z = (1.0, 1.035, (0.5, 0.5), (0.5, 0.5))
C = {"aic_encyc_anatomy": "Энциклопедия Дидро. Анатомия лица, 1762–1777", "aic_munch_omega_eyes": "Эдвард Мунк. Глаза Омеги, 1908–1909",
     "aic_daumier_collector": "Оноре Домье. Коллекционер гравюр, около 1860", "aic_stock_exchange": "Адлер и Салливан. Зал Чикагской биржи, 1893–1894",
     "aic_gerome_chariot": "Жан-Леон Жером. Гонка колесниц, 1876", "aic_munch_scream": "Эдвард Мунк. Крик, 1895 (литография)",
     "aic_redon_waters": "Одилон Редон. Дух — хранитель вод, 1878", "aic_cock_labyrinth": "Иероним Кок. Критский лабиринт, 1558",
     "aic_redon_clouds": "Одилон Редон. Цветочные облака, около 1903", "aic_michelangelo_embrace": "Приписывается Микеланджело. Мать, обнимающая дитя, около 1550",
     "aic_turner_boats": "Уильям Тёрнер. Рыбацкие лодки, 1837–1838", "aic_tangyin_tea": "Тан Инь. Чаепитие под деревом утун, 1509",
     "aic_redon_shadow": "Одилон Редон. Профиль тени, около 1895", "aic_eye_horus": "Египет. Амулет «Око Гора», эпоха Птолемеев",
     "aic_etruscan_mirror": "Этрусское ручное зеркало, 470–450 до н. э.", "aic_double_portrait": "Британский художник. Двойной портрет, около 1845",
     "aic_goya_maragato": "Франсиско Гойя. Монах Педро стреляет в Марагато, около 1806", "aic_munch_window": "Эдвард Мунк. Девушка у окна, 1893"}
def S(text, img, tag=""): return (text, "SUB", tag, img, C[img], Z)
SCENES = [
    S("Представьте: ваш мозг — это сериал.", "aic_encyc_anatomy"),
    S("В главной роли — Эго.", "aic_munch_omega_eyes"),
    S("Строгий директор, который заперся в тесном кабинете.", "aic_daumier_collector"),
    S("Его топливо — дофамин быстрых наград:", "aic_stock_exchange"),
    S("лайки, цифры, галочки.", "aic_etruscan_mirror"),
    S("Эго обожает соревноваться.", "aic_gerome_chariot"),
    S("Оно сравнивает вас с другими | и доказывает, что вы чего-то стоите.", "aic_double_portrait"),
    S("Жизнь для него — вечный забег.", "aic_goya_maragato"),
    S("А проиграть — значит исчезнуть.", "aic_munch_scream"),
    S("Но глубже, в бессознательном, | живёт другой герой.", "aic_redon_waters"),
    S("Карл Юнг назвал его Самостью — | центром всей личности.", "aic_cock_labyrinth"),
    S("Самости не нужно побеждать.", "aic_munch_window"),
    S("Она знает: вы уже целый человек.", "aic_redon_clouds"),
    S("Её топливо — не дофамин, а близость.", "aic_michelangelo_embrace"),
    S("Эго учит выживать и подстраиваться.", "aic_turner_boats"),
    S("А Самость даёт то, чего не купишь лайками: | смысл и свободу.", "aic_tangyin_tea"),
    S("Юнг называл этот путь индивидуацией — | стать тем, кто ты есть.", "aic_redon_shadow"),
    ("Подпишись.", "SUB", SUB_PLATE, "aic_eye_horus", C["aic_eye_horus"], Z),
]
PREP = {s[3]: _tri(s[3]) for s in SCENES}
