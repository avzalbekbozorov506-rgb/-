"""Обложки роликов дня 1 контент-плана: Сунь-цзы (правила и мысль), миф о «цели и средствах», вопрос дня о предательстве."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_covers_click import make_click
def crop(name, cx, cy, h=2300):
    """Кадр 9:16 из картины: высота h пикселей картины (после масштаба до 1920 по высоте кадра), центр (cx, cy) в долях."""
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB"); w = int(h * 9 / 16)
    s = max(w / im.width, h / im.height, 1.0); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = min(max(int(cx * im.width - w / 2), 0), im.width - w); y0 = min(max(int(cy * im.height - h / 2), 0), im.height - h)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 1920), Image.LANCZOS)
make_click(crop("met_62002", 0.55, 0.6, 2400), "ЕЙ БОЛЬШЕ\n2000 ЛЕТ", "5 ПРАВИЛ", "СУНЬ-ЦЗЫ", "«Искусство войны»", "17_suntzu_rules_click", y=1060)
make_click(crop("met_41185", 0.5, 0.62, 2600), "ЛУЧШАЯ ПОБЕДА —\nБЕЗ БОЯ", "ГЛАВА 3", "СУНЬ-ЦЗЫ", "одна мысль", "18_suntzu_thought_click", y=1060)
make_click(crop("met_437510", 0.5, 0.36, 2700), "ЭТО СКАЗАЛ\nМАКИАВЕЛЛИ?", "МИФ", "ЦЕЛЬ И СРЕДСТВА", "миф или правда", "19_myth_goal_click", y=1060)
make_click(crop("met_459131", 0.32, 0.45, 2400), "ДРУГ ТЕБЯ\nПРЕДАЛ", "ВОПРОС ДНЯ", "ЧТО СДЕЛАЕШЬ?", "ответь цифрой", "20_q_betrayal_click", y=1060)
print("ok")
# вне плана: «Его тоже бесили люди» (бюст на тёмном фоне — та же обработка, что в ролике)
import importlib.util
sp = importlib.util.spec_from_file_location("mp", f"{HERE}/configs/marcus_people.py"); mp = importlib.util.module_from_spec(sp); sp.loader.exec_module(mp)
bust = mp.dark_studio(Image.open(f"{HERE}/art/ma_bronze.jpg").convert("RGB")); bust.save("/tmp/_bust.jpg")
im = Image.open("/tmp/_bust.jpg"); w = int(im.height * 9 / 16 * 0.8); h = int(w * 16 / 9); x0 = (im.width - w) // 2
make_click(im.crop((x0, 0, x0 + w, h)).resize((1080, 1920), Image.LANCZOS), "ЕГО ТОЖЕ\nБЕСИЛИ ЛЮДИ", "КНИГА II", "МАРК АВРЕЛИЙ", "император о людях", "21_marcus_people_click", y=1060)
