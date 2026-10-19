"""Анимированные сцены money_map: слои кэшируются, на каждом кадре — появление карточек, поток монет по трубам, наполнение вёдер,
счётчики, вращение вентиля. Функции (lt, D) -> RGBA 1080×1920 для cinema_engine (SCENES[i][3] = функция)."""
import sys, math, functools; sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from paper_kit import *
T0 = 300
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def back(x):  # выезд с лёгким перелётом
    x = min(max(x, 0), 1); c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
@functools.lru_cache(None)
def BGc(seed, light=False): return background(seed, light)
_cache = {}
def layer(key, fn):
    if key not in _cache:
        l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fn(l); _cache[key] = l
    return _cache[key]
def put(im, lay, a=1.0, dy=0, dx=0, scale=1.0, cx=W / 2, cy=H / 2):
    if a <= 0: return
    l = lay
    if scale != 1.0:
        s = max(scale, 0.01); w, h = int(W * s), int(H * s); l = lay.resize((w, h), Image.BILINEAR)
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tmp.alpha_composite(l, (int(cx - cx * s), int(cy - cy * s))) if True else None; l = tmp
    if a < 1:
        arr = np.asarray(l).copy(); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); l = Image.fromarray(arr)
    if dx or dy:
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tmp.alpha_composite(l, (int(dx), int(dy)) if dx >= 0 and dy >= 0 else (0, 0)) if dx >= 0 and dy >= 0 else tmp.paste(l, (int(dx), int(dy)), l); l = tmp
    im.alpha_composite(l)
def pop(im, key, fn, lt, t0, dur=0.45, slide=70):
    """Слой появляется в момент t0: выезд снизу + проявление."""
    u = (lt - t0) / dur
    if u <= 0: return
    put(im, layer(key, fn), a=ease(u), dy=slide * (1 - back(u)))
def tape_l(text, hl): return lambda l: tape(l, T0, text, hl=hl)
def flow(im, path, lt, speed=220, gap=70, r=10, t0=0.0, color=GOLD):
    """Монеты-капли текут по ломаной path [(x,y),...] начиная с t0."""
    if lt < t0: return
    d = ImageDraw.Draw(im); segs = [(path[k], path[k + 1]) for k in range(len(path) - 1)]
    L = [math.dist(a, b) for a, b in segs]; tot = sum(L); head = (lt - t0) * speed
    s = head % gap
    while s < min(head, tot):
        acc = 0
        for (a, b), l in zip(segs, L):
            if s <= acc + l:
                u = (s - acc) / l; x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
                d.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=(150, 110, 30), width=2); break
            acc += l
        s += gap
def counter(im, xy, v, fo, color=INK, suffix=" ₽"):
    ImageDraw.Draw(im).text(xy, f"{int(v):,}".replace(",", " ") + suffix, font=fo, fill=color, anchor="mm")
def base(seed, light=False): return BGc(seed, light).copy()

def a01(lt, D):
    im = base(1); pop(im, "t01", tape_l("Ты получаешь на руки 100 000", "100 000"), lt, 0.0)
    pop(im, "c01", lambda l: card(l, (150, 560), (780, 200), [" ", " "], seed=3), lt, 0.2)
    if lt > 0.2:
        u = ease((lt - 0.3) / 1.6); d = ImageDraw.Draw(im); d.text((540, 610), "НА РУКИ", font=F(40), fill=INK, anchor="mm"); counter(im, (540, 690), 100000 * u, S(96))
    pop(im, "p01", lambda l: person(l, (540, 980), 0.9), lt, 0.6); return im
def a02(lt, D):
    im = base(2); pop(im, "t02", tape_l("А работодатель платит почти 150 000", "150 000"), lt, 0)
    pop(im, "c02b", lambda l: card(l, (240, 760), (600, 190), ["НА РУКИ", "100 000 ₽"], fonts=[F(34), S(80)], seed=6), lt, 0.0)
    pop(im, "c02a", lambda l: card(l, (90, 420), (620, 230), [" ", " "], color=YEL, seed=5, angle=-2), lt, 0.6)
    if lt > 0.6:
        u = ease((lt - 0.7) / 1.8); d = ImageDraw.Draw(im); d.text((400, 480), "РАБОТОДАТЕЛЬ ПЛАТИТ", font=F(34), fill=INK, anchor="mm"); counter(im, (400, 570), 100000 + 49400 * u, S(80), suffix=" ₽")
    pop(im, "l02", lambda l: label(l, (850, 520), "−49 000", size=56, angle=4), lt, 2.8, slide=0)
    if lt > 2.8: ImageDraw.Draw(im).line((540, 690, 540, 750), fill=RED, width=8)
    return im
def a03(lt, D):
    im = base(3); pop(im, "t03", tape_l("Мы спросили Клода: куда?", "Клода:"), lt, 0)
    pop(im, "c03", lambda l: card(l, (160, 470), (760, 420), ["КАРТА ДЕНЕГ", "", "зарплата не исчезает —", "она утекает"], color=CREAM,
        fonts=[S(84), F(20), F(38), F(38)], colors=[RED, INK, INK, INK], seed=7, angle=1.5), lt, 0.9)
    flow(im, [(160, 1000), (920, 1000)], lt, t0=1.5, speed=260); return im
def a04(lt, D):
    im = base(4); d = ImageDraw.Draw(im); d.rectangle((0, 820, W, 1000), fill=(70, 55, 45))
    pop(im, "t04", tape_l("Кузнец заработал 150 монет", "150"), lt, 0)
    pop(im, "b04", lambda l: building(l, (830, 700), 260, "shop", "КУЗНИЦА"), lt, 0.2)
    pop(im, "p04", lambda l: person(l, (360, 900), 1.0, apron=(110, 70, 45)), lt, 0.5)
    pop(im, "an04", lambda l: (ImageDraw.Draw(l).rectangle((460, 760, 620, 800), fill=(70, 70, 75)), ImageDraw.Draw(l).rectangle((510, 800, 570, 880), fill=(70, 70, 75))), lt, 0.5)
    n = int(min(max((lt - 1.5) / 3.0, 0), 1) * 9); coins(im, (560, 740), n, seed=4)
    if lt > 4.5:   # искры от удара
        r = np.random.default_rng(int(lt * 8)); d = ImageDraw.Draw(im)
        for k in range(6): x, y = 540 + r.uniform(-60, 60), 740 + r.uniform(-50, 0); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 190, 80))
    pop(im, "l04", lambda l: label(l, (540, 470), "150 МОНЕТ", color=YEL, fg=INK, size=48), lt, 4.6, slide=0); return im
def a05(lt, D):
    im = base(5); pop(im, "t05", tape_l("Первые краны — до его кармана", "краны"), lt, 0)
    put(im, layer("p05", lambda l: (pipe(l, (80, 520), (1000, 520)), tap(l, (330, 520)), tap(l, (620, 520)))))
    flow(im, [(80, 520), (1000, 520)], lt, t0=0.3, speed=300, gap=90)
    flow(im, [(330, 600), (330, 900)], lt, t0=1.5, speed=200, gap=60); flow(im, [(620, 600), (620, 900)], lt, t0=4.5, speed=200, gap=60)
    pop(im, "k05", lambda l: building(l, (470, 960), 200, "bank", None), lt, 1.0)
    pop(im, "la05", lambda l: label(l, (330, 800), "ВЗНОСЫ  35", size=34), lt, 1.6, slide=0)
    pop(im, "lb05", lambda l: label(l, (620, 800), "НАЛОГ  15", size=34), lt, 4.6, slide=0)
    pop(im, "g05", lambda l: (label(l, (870, 450), "ГОРОД", color=INK, size=28), coin_big(l, (900, 640), 60)), lt, 1.0); return im
def a06(lt, D):
    im = base(6); pop(im, "t06", tape_l("До кузнеца дошло 100", "100"), lt, 0)
    put(im, layer("p06", lambda l: person(l, (300, 960), 1.0, apron=(110, 70, 45))))
    coins(im, (300, 680), int(min(lt / 1.2, 1) * 6), seed=2)
    pop(im, "c06", lambda l: card(l, (520, 520), (440, 300), ["ОН ДАЖЕ", "НЕ ВИДЕЛ", "ЭТИХ КРАНОВ"], color=YEL, fonts=[S(48)] * 3, seed=9, angle=-3), lt, 2.6); return im
def pipes3(l):
    pipe(l, (540, 440), (540, 560)); coin_big(l, (540, 440), 50); pipe(l, (180, 560), (900, 560))
    for k, (x, t) in enumerate([(180, "ЖИЗНЬ"), (540, "ДОЛГИ"), (900, "МЕЛКИЕ КРАНЫ")], 1):
        pipe(l, (x, 560), (x, 760)); tap(l, (x, 760)); badge(l, (x - 90, 640), k); label(l, (x, 960), t, color=INK, size=30)
def a07(lt, D):
    im = base(7); pop(im, "t07", tape_l("Дальше сотня течёт по трём трубам", "трём"), lt, 0); pop(im, "p07", pipes3, lt, 0.2, slide=0)
    for x in (180, 540, 900): flow(im, [(540, 470), (540, 560), (x, 560), (x, 840), (x, 900)], lt, t0=0.6, speed=320, gap=80)
    return im
def a08(lt, D):
    im = base(8); pop(im, "t08", tape_l("Первая — жизнь", "жизнь"), lt, 0)
    pop(im, "h08", lambda l: building(l, (300, 650), 260, "house", "ЖИЛЬЁ"), lt, 0.3)
    pop(im, "e08", lambda l: card(l, (560, 470), (400, 160), ["ЕДА • ДОРОГА"], fonts=[S(40)], seed=11), lt, 1.2)
    pop(im, "s08", lambda l: card(l, (560, 700), (400, 230), ["СУЗИТЬ ✓", "ПЕРЕКРЫТЬ ✗"], color=CREAM, fonts=[S(48), S(48)], colors=[GREEN, RED], seed=12, angle=2), lt, 4.4)
    flow(im, [(300, 380), (300, 520)], lt, t0=0.5, speed=150, gap=60); return im
def a09(lt, D):
    im = base(9); pop(im, "t09", tape_l("Вторая — долги", "долги"), lt, 0)
    pop(im, "c09", lambda l: card(l, (90, 460), (420, 300), ["МОЛОТ", "В ДОЛГ", "год назад"], color=YEL, fonts=[S(60), S(60), F(30)], seed=13, angle=-3), lt, 1.6)
    pop(im, "p09", lambda l: pipe(l, (560, 600), (1000, 600)), lt, 0.3, slide=0); pop(im, "b09", lambda l: building(l, (800, 850), 220, "bank", "РОСТОВЩИК"), lt, 0.6)
    pop(im, "l09", lambda l: label(l, (300, 900), "МОЛОТ СЛОМАН", size=34, angle=-2), lt, 5.0, slide=0)
    flow(im, [(560, 600), (800, 600), (800, 720)], lt, t0=5.4, speed=180, gap=60); return im
def a10(lt, D):
    im = base(10); pop(im, "t10", tape_l("Третья — мелкие краны", "мелкие"), lt, 0)
    put(im, layer("p10", lambda l: [(pipe(l, (60, 470), (1020, 470)) if k == 0 else None, tap(l, (x, 470))) for k, x in enumerate([190, 420, 650, 880])]))
    for k, x in enumerate([190, 420, 650, 880]):
        f = min(max((lt - 0.5 - 0.6 * k) / 6.0, 0), 1) * (0.5 + 0.12 * k); bucket(im, (x, 680), 140, 110, f)
        flow(im, [(x, 550), (x, 690)], lt, t0=0.5 + 0.6 * k, speed=160, gap=50, r=8)
    if lt > 4.0:
        pop(im, "c10", lambda l: card(l, (220, 870), (640, 140), [" "], color=YEL, seed=14), lt, 4.0)
        u = ease((lt - 4.2) / 3.0); ImageDraw.Draw(im).text((540, 940), f"КОФЕ 200 ₽ × {int(365 * u)} = {int(73000 * u):,} ₽".replace(",", " "), font=F(34), fill=INK, anchor="mm")
    return im
def a11(lt, D):
    im = base(11); pop(im, "t11", tape_l("По отдельности — мелочь", "мелочь"), lt, 0)
    for k, (x, t) in enumerate([(190, "КОФЕ"), (420, "ПОДПИСКИ"), (650, "ДОСТАВКА"), (880, "ТАКСИ")]):
        pop(im, f"l11{k}", lambda l, x=x, t=t: (label(l, (x, 470), t, color=INK, size=28), pipe(l, (x, 520), (x, 700))), lt, 0.3 + 0.7 * k)
    pop(im, "p11", lambda l: (pipe(l, (190, 700), (880, 700)), pipe(l, (540, 700), (540, 880))), lt, 3.2, slide=0)
    for x in (190, 420, 650, 880): flow(im, [(x, 520), (x, 700), (540, 700), (540, 1000)], lt, t0=3.4, speed=260, gap=70, r=9)
    pop(im, "w11", lambda l: label(l, (780, 900), "ВМЕСТЕ — КУСОК ЗАРПЛАТЫ", size=30, angle=-2), lt, 7.0, slide=0); return im
def a12(lt, D):
    im = base(12, True); pop(im, "t12", tape_l("Деньги никуда не пропадают", "не"), lt, 0)
    put(im, layer("p12", lambda l: (coin_big(l, (540, 460), 70), pipe(l, (540, 530), (540, 640)), pipe(l, (220, 640), (860, 640)), [pipe(l, (x, 640), (x, 760)) for x in (220, 540, 860)])))
    for k, (x, kd, t) in enumerate([(220, "bank", "БАНК"), (540, "shop", "МАГАЗИН"), (860, "house", "СЕРВИС")]):
        pop(im, f"b12{k}", lambda l, x=x, kd=kd, t=t: building(l, (x, 860), 170, kd, t), lt, 4.5 + 0.5 * k)
        flow(im, [(540, 530), (540, 640), (x, 640), (x, 780)], lt, t0=0.8, speed=260, gap=80)
    return im
def a13(lt, D):
    im = base(13); pop(im, "t13", tape_l("А тебе что-то остаётся?", "тебе"), lt, 0)
    bucket(im, (540, 520), 260, 230, 0.04 + 0.02 * math.sin(lt * 3)); pop(im, "l13", lambda l: label(l, (540, 830), "ТВОЁ БУДУЩЕЕ", color=RED, size=40), lt, 0.6)
    if lt > 2.0:
        a = 8 * math.sin((lt - 2) * 4); put(im, layer("q13", lambda l: label(l, (820, 470), "?", color=YEL, fg=INK, size=90)), dy=0)
    return im
def a14(lt, D):
    im = base(14); pop(im, "t14", tape_l("Краны закрывают в обратном порядке", "обратном"), lt, 0)
    put(im, layer("p14", lambda l: (pipe(l, (540, 410), (540, 470)), coin_big(l, (540, 415), 40), pipe(l, (240, 470), (900, 470)), pipe(l, (240, 470), (240, 600)))))
    for y, t in [(600, "ЖИЗНЬ"), (720, "ДОЛГИ"), (840, "МЕЛКИЕ КРАНЫ")]:
        pop(im, f"r14{y}", lambda l, y=y, t=t: (ImageDraw.Draw(l).rectangle((520, y, 940, y + 70), fill=(80, 84, 90)), ImageDraw.Draw(l).text((730, y + 35), t, font=S(30, "Bold"), fill=(230, 230, 230), anchor="mm")), lt, 0.5 + 0.3 * (y - 600) / 120)
    pop(im, "bd14", lambda l: badge(l, (130, 520), 1), lt, 3.0)
    f = min(max((lt - 3.2) / 5, 0), 1) * 0.7; bucket(im, (240, 610), 200, 160, f, "СЕБЕ 10 %" if lt > 3.2 else None)
    flow(im, [(540, 470), (240, 470), (240, 640)], lt, t0=3.2, speed=200, gap=60); return im
def a15(lt, D):
    im = base(15); pop(im, "t15", tape_l("Потом — самый дорогой долг", "дорогой"), lt, 0)
    put(im, layer("p15", lambda l: pipe(l, (80, 560), (1000, 560))))
    ang = min(lt / 2.5, 1) * 270; d = ImageDraw.Draw(im); d.ellipse((420, 460, 620, 660), outline=RED, width=18)
    a = math.radians(ang); d.line((520 - 100 * math.sin(a), 560 - 100 * math.cos(a), 520 + 100 * math.sin(a), 560 + 100 * math.cos(a)), fill=RED, width=14)
    if lt < 2.5: flow(im, [(80, 560), (1000, 560)], lt, speed=300, gap=90)
    pop(im, "bd15", lambda l: badge(l, (200, 450), 2), lt, 0.2); pop(im, "l15", lambda l: label(l, (520, 760), "ПЕРЕКРЫТЬ", size=44), lt, 2.5, slide=0)
    pop(im, "c15", lambda l: (badge(l, (200, 900), 3), card(l, (300, 850), (620, 130), ["МЕЛКИЕ КРАНЫ — РАЗ В МЕСЯЦ"], color=YEL, fonts=[F(30)], seed=16)), lt, 3.3); return im
def a16(lt, D):
    im = base(16); pop(im, "t16", tape_l("Нарисуй свою карту", "свою"), lt, 0)
    pop(im, "c16", lambda l: card(l, (140, 440), (800, 480), ["ЗАРПЛАТА", "НЕ ИСЧЕЗАЕТ.", "", "ОНА УТЕКАЕТ ТУДА,", "ГДЕ НЕТ КАРТЫ"], color=YEL,
        fonts=[S(70), S(70), F(16), S(44), S(44)], colors=[INK, INK, INK, RED, RED], seed=17, angle=-1.5), lt, 0.3)
    flow(im, [(140, 1000), (940, 1000)], lt, t0=1.0, speed=200); return im
SCENE_FUNCS = [a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15, a16]
