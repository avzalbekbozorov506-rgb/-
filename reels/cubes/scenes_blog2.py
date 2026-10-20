"""Ролик «Клод, что делать, если я сомневаюсь вести блог?» — ответ Клода своими словами, голос Клода (Vosk), музыка Баха.
Запуск: SCENES=scenes_blog2 python3 video.py reels/hq/claude_blog2_hq.mp4"""
from scenes import room_static, room_dyn, room_lights, CAM, LINE as _LINE
PLATE = ""
LINE = dict(_LINE)

def _sc(name, lines, final=False, **kw):
    d = dict(name=name, tag=None, static=room_static, dyn=room_dyn, camera=CAM, lights=room_lights, region=(-3, 3.5, -.2, 3.6, -.3, 3.5), dof=(3.3, 1.5), lines=lines, **kw)
    if final: d["final"] = True
    return d
SCENES = [
    _sc("rb2_q", [("boy", "Клод, что делать, если я сомневаюсь, вести ли мне блог?")]),
    _sc("rb2_ans", [("claude", "Сомнения есть у всех. Они не значат, что ты не готов. Они значат, что тебе не всё равно."),
                    ("claude", "Не жди уверенности. Она приходит после первого ролика, а не до него."),
                    ("claude", "Начни с одного. Остальное исправишь по дороге.")]),
    _sc("rb2_end", [("boy", "Всё. Начинаю снимать. Сохрани этот ролик, если тоже сомневаешься. Подпишись.")], final=True),
]
