"""Животные и принц для псевдо-3D сцен: лиса, лев, волк. Рисуются в двойном разрешении и уменьшаются."""
import math
from PIL import Image, ImageDraw, ImageFilter
from pixar_kit import ball, put, limb, eye, shade, Character, boy_hair, BOY

def _tri(cv, pts, col, k=1.0):
    ImageDraw.Draw(cv).polygon(pts, fill=shade(col, k))

def quadruped(kind, t=0.0, f=1, walk=0.0, talk=0.0, roar=0.0, blink=0.0, look=(0.6, 0), scale=1.0, mood="neutral", glow_eyes=False):
    """Четвероногий зверь. kind: fox | lion | wolf. walk — фаза ходьбы (0 — стоит)."""
    P = {"fox": dict(c=(222, 112, 46), belly=(250, 236, 220), w=300, h=160, head=150, leg=26, ears=True, tail=(232, 120, 50), tip=(250, 246, 240), iris=(214, 150, 40)),
         "wolf": dict(c=(118, 122, 136), belly=(170, 172, 182), w=320, h=165, head=150, leg=28, ears=True, tail=(110, 114, 128), tip=None, iris=(250, 210, 80)),
         "lion": dict(c=(218, 168, 92), belly=(236, 208, 160), w=380, h=210, head=190, leg=40, ears=False, tail=(212, 160, 86), tip=(120, 66, 30), iris=(180, 120, 40))}[kind]
    S = 2; Wc, Hc = 520, 420; cv = Image.new("RGBA", (Wc * S, Hc * S), (0, 0, 0, 0)); d = ImageDraw.Draw(cv)
    cx, gy = Wc * S / 2, Hc * S - 24; bw, bh = P["w"], P["h"]; by = gy - P["leg"] * 3.4 - bh * 0.35 + 6 * math.sin(walk * 2) * (walk > 0)
    for k, (dx, ph) in enumerate([(-0.32, 0), (0.3, math.pi), (-0.22, math.pi), (0.4, 0)]):      # ноги: дальние темнее
        sw = 26 * math.sin(walk + ph) if walk else 0; x = cx + bw * dx * f; back = k >= 2
        limb(d, (x, by + bh * 0.2), (x + sw * f, gy - 12), P["leg"] * 1.25, shade(P["c"], 0.75 if back else 0.95))
        put(cv, ball(int(P["leg"] * 2.2), int(P["leg"] * 1.1), shade(P["c"], 0.6 if back else 0.8), rim=0.2), x + sw * f + 8 * f, gy - 10)
    tx = cx - bw * 0.48 * f; ty = by - bh * 0.05                                        # хвост
    for k in range(5):
        a = math.radians((25 + k * 12 if kind == "wolf" else -30 - k * 16) + 10 * math.sin(t * 3 + k * 0.6)); r = 34 + (k * 8 if kind == "fox" else (k * 2 if kind == "wolf" else -k * 3))
        tx -= math.cos(a) * 42 * f; ty += math.sin(a) * 42
        col = P["tip"] if (k == 4 and P["tip"]) else P["tail"]
        put(cv, ball(int(r * 2), int(r * 1.6), col, rim=0.5), tx, ty)
    put(cv, ball(bw, bh, P["c"], rim=0.6), cx, by)                                     # туловище
    put(cv, ball(int(bw * 0.5), int(bh * 0.55), P["belly"], rim=0.2, spec=0.05), cx + bw * 0.28 * f, by + bh * 0.12)
    hx, hy = cx + bw * 0.46 * f, by - bh * 0.55 - (14 * roar); hr = P["head"]
    if kind == "lion":                                                                 # грива
        for k in range(16):
            a = k / 16 * 2 * math.pi + 0.15 * math.sin(t * 2); R = hr * (0.62 + 0.08 * roar + 0.03 * math.sin(t * 4 + k))
            put(cv, ball(int(hr * 0.5), int(hr * 0.5), (178, 98, 40) if k % 2 else (196, 112, 46), rim=0.5), hx + math.cos(a) * R, hy + math.sin(a) * R)
    if P["ears"]:
        for s in (-1, 1):
            ex = hx + s * hr * 0.32 - 10 * f; _tri(cv, [(ex - 34, hy - hr * 0.2), (ex + 34, hy - hr * 0.2), (ex + 4 * s, hy - hr * 0.78)], P["c"], 0.92)
            _tri(cv, [(ex - 18, hy - hr * 0.26), (ex + 18, hy - hr * 0.26), (ex + 3 * s, hy - hr * 0.6)], (60, 40, 40))
    put(cv, ball(hr, int(hr * 0.92), P["c"], rim=0.6), hx, hy)                          # голова
    mx = hx + hr * 0.3 * f; my = hy + hr * 0.16
    put(cv, ball(int(hr * (0.62 if kind != "lion" else 0.6)), int(hr * 0.42), P["belly"], rim=0.3, spec=0.15), mx, my)   # морда
    put(cv, ball(int(hr * 0.2), int(hr * 0.15), (40, 30, 30), rim=0.1, spec=0.6), mx + hr * 0.2 * f, my - hr * 0.08)   # нос
    if talk > 0.05 or roar > 0.05:
        o = max(talk * 0.5, roar); d = ImageDraw.Draw(cv)
        d.ellipse((mx - hr * 0.16, my + hr * 0.04, mx + hr * 0.2, my + hr * (0.1 + 0.32 * o)), fill=(90, 30, 34))
        if roar > 0.3:
            for s in (-1, 1): _tri(cv, [(mx + s * hr * 0.1 - 6, my + hr * 0.06), (mx + s * hr * 0.1 + 6, my + hr * 0.06), (mx + s * hr * 0.1, my + hr * 0.16)], (250, 250, 246))
    for s in (-1, 1):
        ex = hx + (hr * 0.2 * s + hr * 0.12) * f * (1 if s > 0 else 1); exx = hx + hr * 0.12 * f + hr * 0.2 * s
        eye(cv, exx, hy - hr * 0.08, hr * 0.13, hr * 0.15, look, blink, P["iris"], P["c"], mood)
        if glow_eyes:
            g = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((30, 30, 90, 90), fill=(255, 220, 90, 150)); put(cv, g.filter(ImageFilter.GaussianBlur(14)), exx, hy - hr * 0.08)
    return cv.resize((int(Wc * scale), int(Hc * scale)), Image.LANCZOS)

def prince_hair(cv, hc, hr, f):
    boy_hair(cv, hc, hr, f); d = ImageDraw.Draw(cv); y = hc[1] - hr * 0.95; w = hr * 0.8          # корона
    d.polygon([(hc[0] - w, y + 30), (hc[0] - w, y - 30), (hc[0] - w / 2, y), (hc[0], y - 48), (hc[0] + w / 2, y), (hc[0] + w, y - 30), (hc[0] + w, y + 30)], fill=(232, 186, 70))
    d.line(((hc[0] - w, y + 22), (hc[0] + w, y + 22)), fill=(250, 220, 120), width=8)
    for gx in (-w * 0.55, 0, w * 0.55): put(cv, ball(26, 26, (210, 50, 60), rim=0.2, spec=0.8), hc[0] + gx, y + 6)
PRINCE = Character(dict(BOY.P, shirt=(112, 64, 168), sleeve=(112, 64, 168), pants=(52, 44, 90), shoes=(90, 50, 40), hair_fn=prince_hair, short_sleeve=False, short_pants=False))
