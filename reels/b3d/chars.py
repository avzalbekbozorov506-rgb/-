"""Персонажи «под Pixar» (взрослые пропорции): голова лепится SDF, глаза с веками, «вылепленные» волосы и борода, одежда эпохи.
man(...) возвращает словарь: root (весь герой), head (шарнир шеи — поворот головы)."""
import math
import numpy as np
import sdf as S
from kit import sphere, empty, mat, eye_mat, link

EY, EZ, EX, ER = -0.083, 0.09, 0.037, 0.0175           # центр и радиус глаза (относительно шарнира шеи)

def head_sdf(P, jaw=1.0, nose=1.0, cheek=1.0, brow=1.0, thin=1.0, chin=1.0):
    d = S.ell(P, (0, 0.012, 0.13), (0.084 * thin, 0.1, 0.108))                                  # череп
    d = S.smin(d, S.ell(P, (0, -0.028, 0.065), (0.07 * thin, 0.074, 0.088)), 0.03)                # лицевая часть
    d = S.smin(d, S.rcone(P, (0, -0.005, 0.05), (0, -0.064, -0.012 * chin), 0.064 * jaw * thin, 0.028 * chin), 0.03)   # челюсть → подбородок
    for s in (1, -1):
        d = S.smin(d, S.sph(P, (0.05 * s * cheek * thin, -0.056, 0.07), 0.028), 0.022)             # скулы
        d = S.smin(d, S.ell(P, (0.08 * s * thin, 0.006, 0.078), (0.01, 0.02, 0.03), (0, 0, -12 * s)), 0.008)   # уши
    d = S.smin(d, S.cap(P, (-0.045, -0.079, 0.114), (0.045, -0.079, 0.114), 0.015 * brow), 0.02)   # надбровье
    d = S.smin(d, S.rcone(P, (0, -0.088, 0.104), (0, -0.115 - 0.01 * (nose - 1), 0.046), 0.011, 0.016 * nose), 0.012)  # нос
    for s in (1, -1): d = S.smin(d, S.sph(P, (0.016 * s, -0.101, 0.043), 0.012), 0.008)            # крылья носа
    d = S.smin(d, S.cap(P, (0, 0.0, -0.16), (0, 0.0, 0.04), 0.05), 0.03)                            # шея
    d = S.smin(d, S.ell(P, (0, -0.094, 0.012), (0.024, 0.011, 0.009)), 0.006)                       # губы
    d = S.smin(d, S.ell(P, (0, -0.091, -0.003), (0.021, 0.011, 0.008)), 0.006)
    d = S.sub(d, S.cap(P, (-0.018, -0.106, 0.0045), (0.018, -0.106, 0.0045), 0.0016), 0.0015)          # линия рта
    for s in (1, -1): d = S.sub(d, S.sph(P, (EX * s, EY - 0.012, EZ), 0.019), 0.006)                # глазницы
    return d

def hair_sdf(P, style="long", thin=1.0):
    d = S.ell(P, (0, 0.016, 0.142), (0.091 * thin, 0.108, 0.111))
    d = S.sub(d, S.plane(P, (0, -1, 1.1), (0, -0.04, 0.2)), 0.01)                                # линия лба
    if style == "long":                                                                               # до плеч, за ушами
        back = S.smax(S.ell(P, (0, 0.045, 0.04), (0.094 * thin, 0.07, 0.12)), -S.plane(P, (0, 1, 0), (0, 0.0, 0)), 0.02)
        d = S.smin(d, back, 0.03)
    elif style == "short":
        back = S.smax(S.ell(P, (0, 0.045, 0.08), (0.088 * thin, 0.066, 0.07)), -S.plane(P, (0, 1, 0), (0, 0.0, 0)), 0.02)
        d = S.smin(d, back, 0.02)
    for s in (1, -1): d = S.sub(d, S.sph(P, (0.086 * s * thin, 0.0, 0.075), 0.032), 0.01)               # открыть уши
    return d + 0.0013 * np.sin(np.arctan2(P[:, 0], P[:, 1]) * 55 + P[:, 2] * 30)                  # пряди

def beard_sdf(P, jaw=1.0, thin=1.0, chin=1.0):
    shell = S.smin(S.ell(P, (0, -0.028, 0.065), (0.078 * thin, 0.083, 0.094)), S.rcone(P, (0, -0.005, 0.05), (0, -0.07, -0.02 * chin), 0.074 * jaw * thin, 0.04 * chin), 0.03)
    d = S.smax(shell, S.plane(P, (0, 0.45, 1), (0, -0.09, 0.03)), 0.008)                                 # только ниже скул
    d = S.smax(d, S.plane(P, (0, 1, 0), (0, 0.012, 0)), 0.01)                                        # только спереди
    d = S.smin(d, S.cap(P, (-0.026, -0.104, 0.023), (0.026, -0.104, 0.023), 0.0075), 0.006)          # усы
    for s in (1, -1): d = S.smin(d, S.cap(P, (0.026 * s, -0.104, 0.023), (0.034 * s, -0.097, 0.0), 0.006), 0.006)
    return d + 0.0011 * np.sin(np.arctan2(P[:, 0], -P[:, 1]) * 70 + P[:, 2] * 40)              # пряди

def man(name, at=(0, 0, 0), rot_z=0, skin=(0.78, 0.52, 0.40), hair=(0.12, 0.07, 0.04), iris=(0.22, 0.14, 0.07),
        coat=(0.03, 0.03, 0.035), shirt=(0.85, 0.82, 0.76), beard=True, hair_style="long", hat="cap", hat_color=(0.025, 0.025, 0.03),
        jaw=1.0, nose=1.0, brow=1.0, cheek=1.0, thin=1.0, chin=1.0, bulk=1.0, lids=0.3, frown=0.0, gold=True, armor=False, step=0.0016, head_scale=1.18, cape=None, fur=(0.25, 0.2, 0.17)):
    sk = mat(name + "_skin", skin, rough=0.55, sss=0.3, noise=0.07, nscale=80, spec=0.35)
    hr = mat(name + "_hair", hair, rough=0.42, sheen=0.5, coat=0.1, noise=0.25, nscale=140)
    root = empty(name, at); root.rotation_euler[2] = math.radians(rot_z)
    hp = empty(name + "_head", (0, 0, 1.54), root); hp.scale = (head_scale,) * 3
    kw = dict(jaw=jaw, nose=nose, cheek=cheek, brow=brow, thin=thin, chin=chin)
    S.mesh(name + "_face", lambda P: head_sdf(P, **kw), (-0.12, -0.16, -0.16), (0.12, 0.13, 0.26), step, sk, hp)
    if hair_style: S.mesh(name + "_hair", lambda P: hair_sdf(P, hair_style, thin), (-0.12, -0.14, -0.08), (0.12, 0.14, 0.27), step * 1.4, hr, hp)
    if beard: S.mesh(name + "_beard", lambda P: beard_sdf(P, jaw, thin, chin), (-0.1, -0.13, -0.08), (0.1, 0.03, 0.08), step, hr, hp)
    em = eye_mat(name + "_eye", iris)
    up = 34 - 36 * lids                                                                                 # угол верхнего века: больше — глаз открыт шире
    for s in (1, -1):
        sphere(f"{name}_eye{s}", 1.0, (EX * s, EY, EZ), em, scale=(ER, ER, ER), parent=hp)
        sphere(f"{name}_lidU{s}", ER * 1.1, (EX * s, EY, EZ), sk, rot=(-up, 14 * frown * s, -4 * s), cut=0.0, parent=hp)
        sphere(f"{name}_lidL{s}", ER * 1.09, (EX * s, EY, EZ), sk, rot=(180 + 28, 0, 0), cut=0.0, parent=hp)
        S.mesh(f"{name}_brow{s}", lambda P, s=s: S.cap(P, (0.016 * s, -0.096, 0.118 - 0.006 * frown), (0.058 * s, -0.087, 0.123 + 0.004 * frown), 0.0062),
               (-0.07, -0.11, 0.1), (0.07, -0.07, 0.14), 0.0012, hr, hp, smooth_iter=1)
    if hat == "cap":                                                                                  # бархатный берет эпохи Возрождения
        hm = mat(name + "_hat", hat_color, rough=0.8, sheen=1.0, noise=0.1, nscale=300)
        S.mesh(name + "_cap", lambda P: S.smin(S.ell(P, (0.008, 0.012, 0.21), (0.114, 0.124, 0.042), (7, -7, 0)),
                                               S.ell(P, (0.0, 0.015, 0.185), (0.093, 0.108, 0.05)), 0.02), (-0.14, -0.13, 0.13), (0.14, 0.16, 0.28), step * 1.4, hm, hp)
    # тело: дублет из бархата (или латы), ворот рубашки, золотая цепь
    cl = mat(name + "_coat", coat, rough=0.65 if not armor else 0.3, sheen=0.9 if not armor else 0, metal=0.9 if armor else 0, noise=0.15, nscale=120 if not armor else 15)
    b = bulk
    def body(P):
        d = S.ell(P, (0, 0.02, 1.34), (0.2 * b, 0.12 * b, 0.12))                                      # плечевой пояс
        for s in (1, -1):
            d = S.smin(d, S.sph(P, (0.2 * s * b, 0.02, 1.33), 0.075 * b), 0.05)                     # дельты
            d = S.smin(d, S.rcone(P, (0.21 * s * b, 0.02, 1.31), (0.25 * s * b, 0.0, 1.02), 0.068 * b, 0.055 * b), 0.03)   # плечо
            d = S.smin(d, S.rcone(P, (0.25 * s * b, 0.0, 1.02), (0.2 * s * b, -0.14, 0.86), 0.055 * b, 0.045 * b), 0.02)   # предплечье
        d = S.smin(d, S.rcone(P, (0, 0.02, 1.3), (0, 0.03, 0.85), 0.16 * b, 0.15 * b), 0.08)       # торс
        d = S.smax(d, -S.ell(P, (0, -0.0, 1.47), (0.05, 0.06, 0.05)), 0.02)                        # вырез ворота
        if not armor: d = d + 0.004 * np.sin(np.arctan2(P[:, 0], -P[:, 1]) * 22) * np.clip((1.3 - P[:, 2]) * 4, 0, 1)   # складки ткани
        return d
    S.mesh(name + "_body", body, (-0.36 * b, -0.25 * b, 0.75), (0.36 * b, 0.22 * b, 1.5), 0.006, cl, root)
    if cape:                                                                                          # плащ с меховым воротником
        cm = mat(name + "_cape", cape, rough=0.7, sheen=1.0, noise=0.15, nscale=90)
        def capef(P):
            d = S.rcone(P, (0, 0.05, 1.36), (0, 0.1, 0.7), 0.27 * b, 0.42 * b)
            d = S.sub(d, S.rcone(P, (0, 0.03, 1.38), (0, 0.06, 0.6), 0.25 * b, 0.40 * b), 0.005)           # полый
            d = S.sub(d, S.plane(P, (0, 1, 0), (0, -0.05, 0)), 0.02)                                     # спереди открыт
            return d + 0.008 * np.sin(np.arctan2(P[:, 0], P[:, 1]) * 9) * np.clip((1.3 - P[:, 2]) * 3, 0, 1)
        S.mesh(name + "_capeM", capef, (-0.55 * b, -0.3, 0.6), (0.55 * b, 0.6, 1.62), 0.008, cm, root)
        fm = mat(name + "_fur", fur, rough=0.9, sheen=1.0, noise=0.5, nscale=400)
        S.mesh(name + "_fur", lambda P: S.sub(S.ell(P, (0, 0.04, 1.43), (0.24 * b, 0.17 * b, 0.07)), S.ell(P, (0, -0.05, 1.47), (0.11, 0.13, 0.12)), 0.03)
               + 0.006 * np.sin(P[:, 0] * 173 + 3 * np.sin(P[:, 2] * 140)) * np.sin(P[:, 1] * 151 + 3 * np.sin(P[:, 0] * 120)) * np.sin(P[:, 2] * 190), (-0.3 * b, -0.2 * b, 1.33), (0.3 * b, 0.25 * b, 1.53), 0.004, fm, root)
    sh = mat(name + "_shirt", shirt, rough=0.6, sheen=0.5)
    S.mesh(name + "_collar", lambda P: S.sub(S.rcone(P, (0, 0.01, 1.42), (0, 0.006, 1.5), 0.07 * b, 0.056), S.cap(P, (0, 0.01, 1.38), (0, 0.006, 1.56), 0.047), 0.004),
           (-0.1, -0.1, 1.38), (0.1, 0.1, 1.55), 0.003, sh, root)
    for s in (1, -1):                                                                                 # кисти рук
        S.mesh(f"{name}_hand{s}", lambda P, s=s: S.smin(S.ell(P, (0.19 * s * b, -0.17, 0.83), (0.03, 0.045, 0.05), (20, 0, 0)), S.cap(P, (0.2 * s * b, -0.19, 0.84), (0.205 * s * b, -0.21, 0.79), 0.01), 0.01),
               (-0.4, -0.3, 0.7), (0.4, -0.05, 0.92), 0.003, sk, root)
    if gold:
        gm = mat(name + "_gold", (0.95, 0.66, 0.28), rough=0.22, metal=1.0)
        for k in range(30):
            a = math.radians(-62 + 124 * k / 29)
            sphere(f"{name}_ch{k}", 0.0085, (0.15 * math.sin(a) * b, -0.12 * b - 0.03 * math.cos(a) + 0.015, 1.38 - 0.13 * math.cos(a)), gm, seg=12, parent=root)
    return dict(root=root, head=hp)
