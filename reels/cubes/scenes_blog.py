"""Ролик «Клод, что делать, если я сомневаюсь вести блог?» — ответ Клода = аудио пользователя БЕЗ ИЗМЕНЕНИЙ (reels/audio/blog_doubt_user.mp3).
Запуск: SCENES=scenes_blog python3 video.py reels/hq/claude_blog_hq.mp4"""
import os
from scenes import room_static, room_dyn, room_lights, CAM, LINE as _LINE
PLATE = ""; NO_MUSIC = True                       # без верхней плашки; без своей музыки (в аудио пользователя уже есть звук)
LINE = dict(_LINE)
AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audio", "blog_doubt_user.mp3")
L0 = .3                                            # LEAD: начало первой реплики в сцене
SUBS = [(2.3, 4.1, "Чтобы стать царём зверей,"), (4.6, 7.3, "мало вести себя по-царски."), (9.8, 11.8, "Надо быть царём."),
        (12.6, 14.5, "Нельзя сомневаться."), (15.9, 18.1, "Сомнения порождают хаос"), (18.1, 19.9, "и ведут тебя к гибели.")]
GATE = [(a - .1 + L0, b + .1 + L0) for a, b, _ in SUBS]            # рот открывается только на словах, а не на фоновом звуке

def _sc(name, lines, final=False, **kw):
    d = dict(name=name, tag=None, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5), lines=lines, **kw)
    if final: d["final"] = True
    return d
SCENES = [
    _sc("rb_q", [("boy", "Клод, что делать, если я сомневаюсь, вести ли мне блог?")]),
    _sc("rb_ans", [("claude", "Ответ Клода", "@audio:" + os.path.abspath(AUDIO) + "|25", SUBS)], gate={"claude": GATE}),
    _sc("rb_end", [("boy", "Всё. Начинаю снимать. Сохрани этот ролик, если тоже сомневаешься. Подпишись.")], final=True),
]
