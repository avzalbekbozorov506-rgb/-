"""Ролик «Кто знает историю лучше: ChatGPT, Gemini или Claude?» (сценарий reels/scripts/ai_history_battle.md).
Запуск: SCENES=scenes_battle python3 video.py reels/hq/ai_battle_hq.mp4"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from cuberender import Camera
from scenes import cl, pe, LINE as BASE_LINE
from scenes_quiz import class_static, class_lights
import props
from props import _board, _chalk, _arr, WHITE, YEL, PINK
from cast_ai import ai_bot

PLATE = "КТО ЗНАЕТ ИСТОРИЮ ЛУЧШЕ?\nОТВЕТ — В КОНЦЕ"; MUSIC = None
LINE = dict(BASE_LINE)
LINE["gemini"] = dict(speaker=0, rate=.98, pitch=.92)
LINE["chatgpt"] = dict(speaker=3, rate=1.0, pitch=1.12)
CAM = lambda: Camera((.5, -1.5, 1.35), (.5, 1.9, .70), fov=74)

# ---------- доски ----------
def _frame(title, tsz=38):
    im = _board(); d = ImageDraw.Draw(im); d.rectangle((6, 6, 753, 493), outline=(120, 80, 50, 255), width=8)
    d.text((380, 52), title, font=_chalk(tsz), fill=YEL, anchor="mm"); return im, d
def board_who():
    im, d = _frame("КТО ЗНАЕТ ИСТОРИЮ ЛУЧШЕ?", 34)
    for x, n, c in [(130, "CLAUDE", (214, 100, 74, 255)), (380, "GEMINI", (110, 150, 240, 255)), (630, "CHATGPT", (40, 190, 150, 255))]:
        d.text((x, 200), n, font=_chalk(34), fill=c, anchor="mm"); d.text((x, 300), "?", font=_chalk(100), fill=WHITE, anchor="mm")
    d.text((380, 430), "3 вопроса · 1 победитель", font=_chalk(34), fill=WHITE, anchor="mm"); return _arr(im)
def board_sparta():
    im, d = _frame("ФЕРМОПИЛЫ, 480 до н. э.")
    d.text((380, 190), "300 спартанцев", font=_chalk(62), fill=WHITE, anchor="mm")
    d.text((380, 290), "а греков всего?", font=_chalk(44), fill=YEL, anchor="mm"); d.text((380, 400), "300  ?  5000", font=_chalk(60), fill=PINK, anchor="mm"); return _arr(im)
def board_napoleon():
    im, d = _frame("РОСТ НАПОЛЕОНА")
    d.line((190, 440, 190, 130), fill=WHITE, width=6)
    for y, t in [(440, "0"), (360, "150"), (290, "169"), (200, "180")]:
        d.line((190, y, 240, y), fill=WHITE, width=5); d.text((300, y), t + (" см" if t != "0" else ""), font=_chalk(30), fill=YEL if t == "169" else WHITE, anchor="lm")
    d.text((560, 250), "?", font=_chalk(130), fill=PINK, anchor="mm"); return _arr(im)
def board_cleo():
    return props.board_cleo()
def board_blitz():
    im, d = _frame("БЛИЦ", 46)
    d.text((380, 200), "Колумб, Америка", font=_chalk(54), fill=WHITE, anchor="mm"); d.text((380, 330), "год?", font=_chalk(110), fill=PINK, anchor="mm"); return _arr(im)
def board_end():
    im, d = _frame("ИТОГ", 46)
    for x, n, v, c in [(130, "CLAUDE", "2", (214, 100, 74, 255)), (380, "GEMINI", "0", (110, 150, 240, 255)), (630, "CHATGPT", "3", (40, 190, 150, 255))]:
        d.text((x, 190), n, font=_chalk(32), fill=c, anchor="mm"); d.text((x, 300), v, font=_chalk(120), fill=WHITE, anchor="mm")
    d.text((380, 430), "победил ChatGPT", font=_chalk(40), fill=YEL, anchor="mm"); return _arr(im)

# ---------- герои ----------
def G(st, key, who): return st.get(key, {}).get(who, 0.0)
def dyn(st):
    k = .62
    return (cl(st, (-.55, 1.8, 0), .35, k=k)
            + ai_bot("gemini", (.2, 1.5, 0), .1, k=k, talk=G(st, "talk", "gemini"), blink=G(st, "blink", "gemini"), bob=G(st, "bob", "gemini"))
            + ai_bot("chatgpt", (.95, 1.7, 0), -.2, k=k, talk=G(st, "talk", "chatgpt"), blink=G(st, "blink", "chatgpt"), bob=G(st, "bob", "chatgpt"))
            + pe(st, "boy", (1.7, 2.0, 0), -.4, hat="cap", hatcol=(190, 184, 168)))

SC0 = (0, 0, 0)
def _sc(name, img, lines, score0, score=(), final=False):
    d = dict(name=name, tag=None, static=class_static(img), dyn=dyn, camera=CAM, lights=class_lights, region=(-3, 3.5, -.2, 4, -.3, 3.5), dof=(3.4, 2.0),
             lines=lines, score0=score0, score=list(score))
    if final: d["final"] = True
    return d
T = ("_t", "2.4")        # таймер 3-2-1
BOY1 = ("boy", "Кто знает историю лучше: ChatGPT, Gemini или Claude? Пиши в комментариях, на кого ставишь. Ответ — в конце.",
        "Кто знает историю лучше: Чат джи пи ти, Джемини или Клод? Пиши в комментариях, на кого ставишь. Ответ — в конце.")
SCENES = [
    _sc("b_hook", board_who(), [BOY1, ("claude", "Три вопроса. Верный ответ — балл."), ("gemini", "Я выиграю."), ("chatgpt", "Нет, я.")], SC0),
    _sc("b_sparta", board_sparta(), [("boy", "Триста спартанцев остановили армию персов. Сколько греков там было на самом деле?"), T,
        ("gemini", "Триста!"), ("chatgpt", "Триста, это же фильм!"),
        ("claude", "Триста — это спартанцы. С ними стояли ещё несколько тысяч греков. Балл мне.")], SC0, [(4, (1, 0, 0))]),
    _sc("b_napoleon", board_napoleon(), [("boy", "Какой рост был у Наполеона?"), T,
        ("gemini", "Полтора метра, он же карлик!"), ("chatgpt", "Метр шестьдесят девять. Карикатуры рисовали англичане.")], (1, 0, 0), [(3, (1, 0, 1))]),
    _sc("b_cleo", board_cleo(), [("boy", "Счёт один-один. Последний вопрос. Тут ломаются все. Клеопатра жила ближе к пирамидам или к высадке на Луну?"), T,
        ("gemini", "К пирамидам!"), ("chatgpt", "К Луне!"), ("claude", "К Луне. Две тысячи лет против двух с половиной.")], (1, 0, 1), [(3, (1, 0, 2)), (4, (2, 0, 2))]),
    _sc("b_blitz", board_blitz(), [("boy", "Ничья. Решает блиц: в каком году Колумб открыл Америку? Кто первый, тот и победил."),
        ("chatgpt", "Тысяча четыреста девяносто второй!"), ("claude", "В тысяча четыреста девяносто втором, но викинги были там на пятьсот лет раньше."), ("boy", "Время!")],
        (2, 0, 2), [(1, (2, 0, 3))]),
    _sc("b_end", board_end(), [("boy", "Победил ChatGPT. Клод, ты чего?", "Победил Чат джи пи ти. Клод, ты чего?"), ("claude", "Слишком много объяснял."),
        ("boy", "А ты как думаешь, кто на самом деле лучше? Пиши в комментариях. Отправь тому, кто спорит про нейросети. Подпишись — тут история смешнее, чем в учебнике.")],
        (2, 0, 3), final=True),
]

# ---------- накладки: имена со счётом под героями, таймер, оговорка ----------
def _f(sz, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)
_POS = {"claude": (150, "CLAUDE", (214, 100, 74)), "gemini": (416, "GEMINI", (96, 140, 238)), "chatgpt": (710, "CHATGPT", (30, 170, 135))}
def overlay(sc, t, fr):
    d = ImageDraw.Draw(fr); sc_now = sc["score0"]
    for idx, val in sc["score"]:
        who, text, st, dur, a = sc["tl"][idx]
        if t >= st + dur: sc_now = val
    speaking = {w for w, text, st, dur, a in sc["tl"] if st - .05 <= t <= st + dur + .15}
    for i, (who, (x, name, col)) in enumerate(_POS.items()):
        label = f"{name}  {sc_now[i]}"; ft = _f(34); tw = d.textlength(label, font=ft); on = who in speaking
        d.rounded_rectangle((x - tw / 2 - 26, 1300, x + tw / 2 + 26, 1366), 33, fill=(255, 214, 80, 250) if on else col + (235,))
        d.text((x - tw / 2, 1313), label, font=ft, fill=(30, 24, 20, 255) if on else (255, 255, 255, 255))
    for who, text, st, dur, a in sc["tl"]:
        if who == "_t" and st <= t < st + dur:
            n = 3 - min(2, int((t - st) / (dur / 3))); ft = _f(90)
            d.ellipse((540 - 62, 920 - 62, 540 + 62, 920 + 62), fill=(18, 18, 20, 235), outline=(255, 214, 80, 255), width=6)
            d.text((540, 920), str(n), font=ft, fill=(255, 255, 255, 255), anchor="mm")
    ft = _f(28, "Bold"); msg = "скетч: ответы нейросетей смоделированы"; tw = d.textlength(msg, font=ft)
    d.text(((1080 - tw) / 2, 1850), msg, font=ft, fill=(255, 255, 255, 235), stroke_width=4, stroke_fill=(20, 20, 24, 255))
