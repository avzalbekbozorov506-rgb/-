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
