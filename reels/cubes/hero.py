"""Кубический герой по фото автора канала: короткая тёмная стрижка, густые брови, короткая борода с усами, крепкое телосложение, тёмно-синий свитшот."""
from cast import person, _place
from cuberender import Box

HAIR = (28, 24, 24); BEARD = (58, 42, 34); SKIN = (206, 158, 126); SWEAT = (26, 36, 62); PANTS = (74, 76, 86)

def hero(pos, yaw=0.0, talk=0.0, blink=0.0, bob=0.0, arm=0.0, k=1.0):
    out = person(pos, yaw=yaw, talk=talk, blink=blink, bob=bob, arm=arm, k=k, skin=SKIN, top=SWEAT, bottom=PANTS, hair=HAIR, hat="none", blush=False, mustache=False)
    P = lambda o: _place(pos, yaw, (o[0] * k, o[1] * k, o[2] * k + bob * k)); S = lambda *a: tuple(v * k for v in a)
    out += [Box(P((0, -.01, .52)), S(.46, .26, .50), SWEAT, yaw)]                                       # плечи шире — крепкое сложение
    out += [Box(P((-.255, .0, 1.02)), S(.03, .40, .2), HAIR, yaw), Box(P((.255, .0, 1.02)), S(.03, .40, .2), HAIR, yaw),   # виски
            Box(P((0, -.2, 1.12)), S(.50, .08, .07), HAIR, yaw)]                                          # чёлка-ёжик
    out += [Box(P((-.13, -.238, .995)), S(.20, .03, .055), HAIR, yaw), Box(P((.13, -.238, .995)), S(.20, .03, .055), HAIR, yaw)]   # густые брови
    out += [Box(P((0, -.225, .665)), S(.40, .05, .075), BEARD, yaw), Box(P((0, -.12, .64)), S(.46, .26, .06), BEARD, yaw),         # борода: подбородок
            Box(P((-.245, -.07, .74)), S(.03, .30, .20), BEARD, yaw), Box(P((.245, -.07, .74)), S(.03, .30, .20), BEARD, yaw),     # щёки
            Box(P((-.19, -.232, .72)), S(.07, .04, .17), BEARD, yaw), Box(P((.19, -.232, .72)), S(.07, .04, .17), BEARD, yaw),
            Box(P((0, -.250, .775)), S(.24, .03, .04), BEARD, yaw)]                                                               # усы
    return out

# ---------- версия «с настоящим лицом»: фото автора на передней грани головы ----------
import os, numpy as np
from PIL import Image
_FACE = None
def _face():
    global _FACE
    if _FACE is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "face_front_masked.png")
        _FACE = np.asarray(Image.open(p).convert("RGBA"), np.uint8)
    return _FACE
TEE = (22, 22, 26); TROUSERS = (84, 86, 94)
def hero_photo(pos, yaw=0.0, talk=0.0, blink=0.0, bob=0.0, arm=0.0, k=1.0):
    """Тело кубическое (чёрная футболка, серые брюки), голова — куб с настоящим фото лица спереди; рот открывается по громкости речи."""
    out = person(pos, yaw=yaw, talk=0, blink=0, bob=bob, arm=arm, k=k, skin=SKIN, top=TEE, bottom=TROUSERS, hair=HAIR, hat="none", blush=False, mustache=False)
    out = [b for b in out if not (abs(b.s[2] * 2 / k - .50) < 1e-3 and abs(b.s[0] * 2 / k - .50) < 1e-3)]       # убираем стандартную голову
    out = [b for b in out if not (abs(b.s[0] * 2 / k - .52) < 1e-3)]                                           # и волосы-шапку
    out = [b for b in out if not (abs(b.s[0] * 2 / k - .07) < 1e-3)]                                           # нос, уши
    out = [b for b in out if not (abs(b.s[0] * 2 / k - .04) < 1e-3 and abs(b.s[2] * 2 / k - .10) < 1e-3)]
    P = lambda o: _place(pos, yaw, (o[0] * k, o[1] * k, o[2] * k + bob * k)); S = lambda *a: tuple(v * k for v in a)
    W_, H_ = .54, .54 * 712 / 496; zc = .74 + H_ / 2 - .03
    out += [Box(P((0, -.01, .52)), S(.46, .26, .50), TEE, yaw)]                                                # плечи
    out += [Box(P((0, 0, zc)), S(W_, .46, H_), (30, 24, 22), yaw, img=_face(), gloss=.05)]                    # голова с фото
    mh = .008 + .05 * talk; fx, fy = .504, .75                                                                  # рот
    out += [Box(P(((fx - .5) * W_, -.234, zc + (.5 - fy) * H_)), S(.24 * W_, .006, mh), (52, 16, 20), yaw, shadow=False)]
    return out
