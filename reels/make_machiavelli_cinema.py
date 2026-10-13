"""Reels для взрослой аудитории: «Макиавелли. Государь — 5 мыслей».
Картины эпохи — открытые коллекции The Met и Art Institute of Chicago (CC0); медленный наезд камеры, плёночное зерно,
виньетка, шрифт с засечками. Перевод цитат — собственный, с итальянского оригинала. Голос — Silero TTS v5 (офлайн)."""
import json, math, os, subprocess, sys
import numpy as np, scipy.io.wavfile as wavfile, torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "machiavelli_cinema.mp4"
SILERO = os.environ.get("SILERO_MODEL", "v5_ru.pt")
WORK = os.path.join(HERE, "machiavelli"); os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
GOLD, WHITE, GREY = (214, 178, 112), (246, 240, 228), (150, 140, 128)
def serif(style, size): return ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-{style}.ttf", size)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

# сцены: (озвучка с ударениями, текст на экране, метка, картина, подпись, наезд: (zoom0, zoom1, (fx0, fy0), (fx1, fy1)))
SCENES = [
    ("Никк+оло Макиав+елли. «Госуд+арь», тысяча пятьсот тринадцатый год. Пять мыслей, которые работают до сих пор.",
     None, None, "giuliano", "Рафаэль. Джулиано Медичи, герцог Немурский", (1.05, 1.18, (0.5, 0.42), (0.5, 0.30))),
    ("Первая. Если приходится выбирать, гораздо надёжнее внушать страх, чем любовь. Но ненависти правитель должен избегать.",
     "Если приходится выбирать,\nгораздо надёжнее\nвнушать страх, чем любовь", "ГЛАВА XVII  ·  I / V", "bronzino", "Бронзино. Портрет юноши, 1530-е", (1.22, 1.05, (0.52, 0.28), (0.5, 0.36))),
    ("Вторая. Правитель должен быть лисой, чтобы распознать капканы, и львом, чтобы отпугнуть волков.",
     "Будь лисой, чтобы распознать\nкапканы, и львом —\nчтобы отпугнуть волков", "ГЛАВА XVIII  ·  II / V", "lion", "Эжен Делакруа. Охота на львов, 1860–1861", (1.0, 1.12, (0.5, 0.5), (0.42, 0.45))),
    ("Третья. Каждый видит, каким ты кажешься. Но мало кто знает, каков ты на самом деле.",
     "Каждый видит, каким ты кажешься.\nНо мало кто знает,\nкаков ты на самом деле", "ГЛАВА XVIII  ·  III / V", "titian", "Тициан. Портрет мужчины, ок. 1515", (1.05, 1.2, (0.5, 0.4), (0.48, 0.3))),
    ("Четвёртая. Судьба распоряжается половиной наших дел. Но другую половину она оставляет нам самим.",
     "Судьба распоряжается\nполовиной наших дел.\nДругую половину — оставляет нам", "ГЛАВА XXV  ·  IV / V", "nemesis", "Альбрехт Дюрер. Немезида (Большая Фортуна), 1501–1502", (1.1, 1.25, (0.5, 0.5), (0.5, 0.3))),
    ("Пятая. Об уме правителя прежде всего судят по людям, которых он держит рядом.",
     "Об уме правителя судят\nпо людям, которых\nон держит рядом", "ГЛАВА XXII  ·  V / V", "chess", "Томас Икинс. Шахматисты, 1876", (1.0, 1.12, (0.5, 0.5), (0.55, 0.5))),
    ("Какая мысль вам ближе? Напишите в комментариях. И сохраните, чтобы не забыть.",
     "Какая мысль\nвам ближе?", "НАПИШИТЕ НОМЕР В КОММЕНТАРИЯХ", "bronzino", "Бронзино. Портрет юноши, 1530-е", (1.35, 1.45, (0.5, 0.25), (0.5, 0.25))),
]
LEAD, TAIL, XF = 0.6, 1.0, 0.7

# ---------------- озвучка ----------------
model = torch.package.PackageImporter(SILERO).load_pickle("tts_models", "model"); model.to("cpu")
SR = 48000
voice, STARTS, DURS, t0 = [], [], [], 0.0
for sc in SCENES:
    a = model.apply_tts(text=sc[0], speaker="aidar", sample_rate=SR, put_accent=True, put_yo=True).numpy()
    STARTS.append(t0); DURS.append(LEAD + len(a) / SR + TAIL); voice.append((t0 + LEAD, a)); t0 += DURS[-1]
DUR = t0
track = np.zeros(int(DUR * SR) + SR)
for st, a in voice: track[int(st * SR):int(st * SR) + len(a)] += a
wavfile.write(f"{WORK}/voice_c.wav", SR, (track / np.abs(track).max() * 0.9 * 32767).astype(np.int16))

# ---------------- музыка: медленный тёмный эмбиент (струнный пэд + низкая педаль) ----------------
N = len(track); tt = np.arange(N) / SR; mus = np.zeros(N)
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = [[50, 57, 62, 65], [46, 53, 58, 62], [43, 55, 58, 62], [45, 52, 57, 61]]; bar = 6.0
for i in range(int(DUR / bar) + 1):
    s0, s1 = int(i * bar * SR), min(int((i + 1) * bar * SR + 2 * SR), N)
    if s0 >= N: break
    seg = tt[s0:s1] - i * bar; env = np.minimum(seg / 2.5, 1) * np.clip((bar + 2 - seg) / 2.5, 0, 1)
    vib = 1 + 0.002 * np.sin(2 * np.pi * 5 * seg)
    for m in prog[i % 4]:
        f = note(m)
        mus[s0:s1] += env * (0.05 * np.sin(2 * np.pi * f * seg * vib) + 0.02 * np.sin(4 * np.pi * f * seg) + 0.01 * np.sin(6 * np.pi * f * seg))
    mus[s0:s1] += env * 0.06 * np.sin(2 * np.pi * note(prog[i % 4][0] - 12) * seg)
mus *= np.minimum(np.minimum(tt / 3, 1), np.clip((DUR - tt) / 3, 0, 1))
wavfile.write(f"{WORK}/music_c.wav", SR, (mus / np.abs(mus).max() * 0.8 * 32767).astype(np.int16))

# ---------------- картинка ----------------
def grade(im):
    im = ImageEnhance.Color(im).enhance(0.82); im = ImageEnhance.Contrast(im).enhance(1.08)
    a = np.asarray(im).astype(np.float32); a[..., 0] *= 1.04; a[..., 2] *= 0.94          # тёплый «музейный» тон
    return Image.fromarray(np.clip(a * 0.9, 0, 255).astype(np.uint8))

BIG = (int(W * 1.5), int(H * 1.5))
def prepare(name):
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB")
    if im.width / im.height > 1.0:                     # горизонтальная картина: размытый фон + полотно в рамке
        bg = im.copy(); s = max(BIG[0] / bg.width, BIG[1] / bg.height)
        bg = bg.resize((int(bg.width * s), int(bg.height * s))).filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg.crop(((bg.width - BIG[0]) // 2, (bg.height - BIG[1]) // 2, (bg.width + BIG[0]) // 2, (bg.height + BIG[1]) // 2))).enhance(0.45)
        fw = int(BIG[0] * 0.92); fg = im.resize((fw, int(im.height * fw / im.width)), Image.LANCZOS)
        y = int(BIG[1] * 0.36) - fg.height // 2
        sh = Image.new("RGBA", BIG, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle(((BIG[0] - fw) // 2 + 10, y + 20, (BIG[0] + fw) // 2 + 10, y + fg.height + 20), fill=(0, 0, 0, 200))
        bg = bg.convert("RGBA"); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25))); bg = bg.convert("RGB")
        bg.paste(fg, ((BIG[0] - fw) // 2, y)); ImageDraw.Draw(bg).rectangle(((BIG[0] - fw) // 2 - 3, y - 3, (BIG[0] + fw) // 2 + 2, y + fg.height + 2), outline=GOLD, width=3)
        return grade(bg)
    s = max(BIG[0] / im.width, BIG[1] / im.height)
    return grade(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS))
CACHE = {}
def plate(name):
    if name not in CACHE: CACHE[name] = prepare(name)
    return CACHE[name]

def camera(im, z, fx, fy):
    cw, ch = W * im.width / BIG[0] / z * (BIG[0] / W) / (im.width / BIG[0]), 0
    cw = BIG[0] / 1.5 / z * (im.width / BIG[0]) * (BIG[0] / im.width) * 1.5 * (im.width / BIG[0])
    # окно кадра в координатах картинки: при z=1 видна область W*1.5/1.5 = полное «покрытие» по меньшей стороне
    base = min(im.width / W, im.height / H); cw, ch = W * base / z, H * base / z
    cx = min(max(fx * im.width, cw / 2), im.width - cw / 2); cy = min(max(fy * im.height, ch / 2), im.height - ch / 2)
    return im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

# оверлей: затемнение снизу и сверху + виньетка
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
bot = np.clip((yy - 880) / 620, 0, 1) ** 1.3 * 238; top = np.clip((380 - yy) / 380, 0, 1) * 150
vig = np.clip(((xx - W / 2) ** 2 / (W * 0.75) ** 2 + (yy - H * 0.45) ** 2 / (H * 0.7) ** 2) - 0.35, 0, 1) * 170
OVER = Image.fromarray(np.dstack([np.full((H, W), 8), np.full((H, W), 6), np.full((H, W), 6), np.clip(np.maximum(np.maximum(bot, top), vig), 0, 245)]).astype(np.uint8), "RGBA")
rng = np.random.default_rng(1); GRAIN = [rng.normal(0, 7, (H // 2, W // 2)).astype(np.int16) for _ in range(6)]

def spaced(d, xy, text, f, fill, sp=6, anchor="mm"):
    w = sum(d.textlength(c, font=f) + sp for c in text) - sp
    x = xy[0] - w / 2 if anchor == "mm" else xy[0]
    for c in text: d.text((x, xy[1]), c, font=f, fill=fill, anchor="lm"); x += d.textlength(c, font=f) + sp

HEAD = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); hd = ImageDraw.Draw(HEAD)
spaced(hd, (W // 2, 150), "НИККОЛО МАКИАВЕЛЛИ", sans("Medium", 26), GOLD + (230,), 7)
hd.line(((W // 2 - 230, 190), (W // 2 + 230, 190)), fill=GOLD + (120,), width=1)
spaced(hd, (W // 2, 222), "«ГОСУДАРЬ», 1513", sans("Medium", 22), GREY + (220,), 5)
F_Q, F_TAG, F_CR = serif("MediumItalic", 80), sans("SemiBold", 24), sans("Medium", 22)

def text_layer(i, lt, D):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    say, text, tag, _, credit, _ = SCENES[i]
    out = ease((D - lt - 0.15) / 0.5)
    if text is None:                                                   # титульная сцена
        a = ease((lt - 0.4) / 1.0) * out
        spaced(d, (W // 2, 1240), "ГОСУДАРЬ", serif("Bold", 150), WHITE + (int(255 * a),), 14)
        d.line(((W // 2 - 120, 1345), (W // 2 + 120, 1345)), fill=GOLD + (int(200 * a),), width=2)
        b = ease((lt - 1.4) / 1.0) * out
        d.text((W // 2, 1410), "Никколо Макиавелли, 1513", font=serif("MediumItalic", 60), fill=WHITE + (int(235 * b),), anchor="mm")
        c = ease((lt - 3.0) / 1.0) * out
        spaced(d, (W // 2, 1500), "ПЯТЬ МЫСЛЕЙ, КОТОРЫЕ РАБОТАЮТ ДО СИХ ПОР", sans("Medium", 24), GOLD + (int(230 * c),), 4)
    else:
        a = ease((lt - 0.2) / 0.6) * out
        spaced(d, (W // 2, 1135), tag, F_TAG, GOLD + (int(240 * a),), 6)
        lines = text.split("\n"); speak = D - LEAD - TAIL
        size = 80
        while size > 56 and max(d.textlength(l, font=serif("MediumItalic", size)) for l in lines) > 960: size -= 2
        fq = serif("MediumItalic", size)
        for k, line in enumerate(lines):                              # строки проявляются в такт речи
            st = LEAD + speak * (0.12 + 0.62 * k / len(lines))
            b = ease((lt - st) / 0.7) * out
            if b <= 0: continue
            y = 1215 + k * 92 + int((1 - b) * 18)
            d.text((W // 2 + 2, y + 3), line, font=fq, fill=(0, 0, 0, int(120 * b)), anchor="mm")
            d.text((W // 2, y), line, font=fq, fill=WHITE + (int(255 * b),), anchor="mm")
    cr = ease((lt - 1.0) / 0.8) * out
    d.text((W // 2, 1640), credit, font=F_CR, fill=GREY + (int(200 * cr),), anchor="mm")
    return lay

def scene_frame(i, lt):
    D = DURS[i]; z0, z1, (fx0, fy0), (fx1, fy1) = SCENES[i][5]; u = ease(lt / D) * 0.85 + (lt / D) * 0.15
    im = camera(plate(SCENES[i][3]), z0 + (z1 - z0) * u, fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u).convert("RGBA")
    im.alpha_composite(OVER); im.alpha_composite(HEAD, (0, 0)); im.alpha_composite(text_layer(i, lt, D))
    return im.convert("RGB")

def frame(t, n):
    i = max(k for k in range(len(STARTS)) if STARTS[k] <= t); lt = t - STARTS[i]
    im = scene_frame(i, lt)
    if lt < XF and i > 0: im = Image.blend(scene_frame(i - 1, lt + DURS[i - 1]), im, ease(lt / XF))
    if t < 0.8: im = Image.blend(Image.new("RGB", (W, H)), im, ease(t / 0.8))
    if DUR - t < 1.0: im = Image.blend(Image.new("RGB", (W, H)), im, ease((DUR - t) / 1.0))
    a = np.asarray(im).astype(np.int16); g = GRAIN[n % len(GRAIN)]
    a += np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]                # плёночное зерно
    return np.clip(a, 0, 255).astype(np.uint8)

if len(sys.argv) > 2:
    for k, x in enumerate(map(float, sys.argv[2].split(","))): Image.fromarray(frame(x, k)).resize((360, 640)).save(f"{WORK}/c_{k}.png")
    print("durations", [round(d, 1) for d in DURS]); sys.exit()
p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", f"{WORK}/video_c.mp4"], stdin=subprocess.PIPE)
for n in range(int(DUR * FPS)): p.stdin.write(frame(n / FPS, n).tobytes())
p.stdin.close(); p.wait()
fc = ("[1:a]highpass=f=80,equalizer=f=3500:t=q:w=1.5:g=1.5,deesser=i=0.2,asplit[v][vk];"
      "[2:a]volume=0.14[m];[m][vk]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=600[md];"
      "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{WORK}/video_c.mp4", "-i", f"{WORK}/voice_c.wav", "-i", f"{WORK}/music_c.wav",
                "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.2f}", "-movflags", "+faststart", OUT], check=True)
print("done", OUT, f"{DUR:.1f} c")
