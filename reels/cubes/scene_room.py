"""Сцена 1: комната мальчика вечером. build(t, st) -> (boxes, camera)."""
import numpy as np
from cuberender import Box, Camera, Lights
from cast import claude, boy

def planks(p, ax, sgn, col):
    s = (np.floor(p[:, 0] / .28) % 2)
    out = col.copy(); out[s == 1] *= .93
    seam = (np.abs((p[:, 0] / .28) % 1 - .5) > .47); out[seam] *= .78
    return out
def wall(p, ax, sgn, col):
    out = col.copy(); stripe = (np.floor(p[:, 0] / .35) % 2 == 1); out[stripe] *= .965; return out
def checker(p, ax, sgn, col):
    c = (np.floor(p[:, 0] / .5) + np.floor(p[:, 1] / .5)) % 2
    out = col.copy(); out[c == 1] = np.array([236, 222, 196], np.float32) / 255; return out

def build_static():
    B = []
    B.append(Box((0, 3.2, 1.6), (9, .2, 4), (88, 112, 128), tex=wall))                    # задняя стена (сине-серая)
    B.append(Box((0, 1.2, -.1), (9, 6.2, .2), (176, 128, 86), tex=planks))               # пол
    B.append(Box((-2.9, 1.2, 1.6), (.2, 6.2, 4), (96, 120, 136)))                         # левая стена
    # окно с ночным небом и огоньками
    B.append(Box((-.2, 3.08, 1.9), (1.5, .04, 1.2), (28, 36, 74), glow=True))
    for (sx, sz) in [(-.7, 2.2), (-.35, 1.7), (.2, 2.35), (.4, 1.6), (-.05, 1.95), (.6, 2.1)]:
        B.append(Box((sx, 3.05, sz), (.05, .02, .05), (255, 240, 180), glow=True))
    B.append(Box((-.2, 3.05, 2.55), (1.6, .06, .08), (240, 232, 214)))                   # рама
    B.append(Box((-.2, 3.05, 1.25), (1.6, .06, .08), (240, 232, 214)))
    B.append(Box((-.98, 3.05, 1.9), (.08, .06, 1.3), (240, 232, 214)))
    B.append(Box((.58, 3.05, 1.9), (.08, .06, 1.3), (240, 232, 214)))
    B.append(Box((-.2, 3.05, 1.9), (.06, .06, 1.3), (240, 232, 214)))
    # плакат с «пирамидкой» и лампа-гирлянда
    B.append(Box((1.9, 3.08, 1.9), (.8, .03, 1.0), (232, 196, 120)))
    B.append(Box((1.9, 3.05, 1.75), (.5, .03, .4), (196, 140, 70)))
    # стол
    B.append(Box((1.0, 1.9, .70), (2.2, 1.0, .08), (150, 104, 70)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.append(Box((1.0 + sx * 1.0, 1.9 + sy * .42, .33), (.1, .1, .66), (120, 82, 56)))
    # учебник: толстый, обложка зелёная, страницы
    B.append(Box((1.75, 1.85, .79), (.6, .44, .10), (60, 112, 96), yaw=.25))
    B.append(Box((1.75, 1.85, .82), (.55, .40, .08), (244, 236, 214), yaw=.25))
    # лампа
    B.append(Box((1.45, 2.3, .76), (.22, .22, .05), (70, 70, 80)))
    B.append(Box((1.45, 2.3, 1.02), (.05, .05, .5), (70, 70, 80)))
    B.append(Box((1.45, 2.22, 1.30), (.36, .30, .20), (255, 214, 120), glow=True))
    # кровать/ковёр слева на полу
    B.append(Box((-1.8, 1.4, .02), (1.6, 1.2, .04), (150, 70, 70), shadow=False))
    return B

def build_dyn(st):
    B = []
    B += claude((.95, 1.85, .74), yaw=-.3, talk=st.get("claude_talk", 0), blink=st.get("claude_blink", 0), bob=st.get("claude_bob", 0), k=.8)
    B += boy((.22, 1.25, 0), yaw=.30, talk=st.get("boy_talk", 0), blink=st.get("boy_blink", 0), bob=st.get("boy_bob", 0), arm=st.get("boy_arm", 0))
    return B

def camera(t=0, T=1):
    return Camera((.55, -1.25, 1.25), (.5, 1.9, .78), fov=60)

def lights():
    return Lights(sun_dir=(-.45, -.55, .70), sun=(1.0, .88, .72), sky=(.46, .52, .74), ground=(.36, .27, .22),
                  points=[((1.45, 2.1, 1.25), (1.0, .72, .38), 1.8)])
