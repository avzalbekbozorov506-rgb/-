"""Движок «кинематографичных» Reels: сцены (картина или анимация) + цитаты с номером главы + голос Silero v5 + тёмный эмбиент.
Использование: python3 cinema_engine.py <конфиг.py> <out.mp4> [t1,t2,... — кадры-превью]
Конфиг задаёт HEAD (две строки шапки), TITLE (три строки титула), SCENES и, по желанию, PREP (обработка картин)."""
import importlib.util, math, os, subprocess, sys
import numpy as np, scipy.io.wavfile as wavfile, torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cfg", sys.argv[1]); cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
OUT = sys.argv[2]
SILERO = os.environ.get("SILERO_MODEL", "v5_ru.pt")
WORK = os.path.join(HERE, "work", os.path.splitext(os.path.basename(OUT))[0]); os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
GOLD, WHITE, GREY = (214, 178, 112), (246, 240, 228), (150, 140, 128)
GOLD_HI = (240, 200, 120)
def serif(style, size): return ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-{style}.ttf", size)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
SCENES = cfg.SCENES          # (озвучка, текст или None для титула, метка, картина|функция(lt, D), подпись, камера)
LEAD, TAIL, XF = 0.6, 1.0, 0.7
LEAD_N = LEAD
XF = getattr(cfg, "XF", XF)                 # длина наплыва между сценами (0 — жёсткая склейка)
TAIL = getattr(cfg, "TAIL", TAIL)

# ---------- озвучка ----------
model = torch.package.PackageImporter(SILERO).load_pickle("tts_models", "model"); model.to("cpu")
SR = 48000; voice, STARTS, DURS, t0 = [], [], [], 0.0
PHRASES = {}   # сцена -> [(начало, конец, текст)] — для субтитров, точно совпадающих с голосом
def clean(t): return t.replace("+", "")
def sentences(text):
    """Фрагменты субтитров (через |), сгруппированные в предложения: фрагмент на . ! ? … закрывает предложение."""
    out, cur = [], []
    for f in [p.strip() for p in text.split("|") if p.strip()]:
        cur.append(f)
        if f.rstrip("»\"”").endswith((".", "!", "?", "…")): out.append(cur); cur = []
    if cur: out.append(cur)
    return out
_VOSK = None
def tts(text, spk):
    for k_, v_ in getattr(cfg, "SAY", {}).items(): text = text.replace(k_, v_)      # как произносить (субтитры остаются как написано)
    xt = getattr(cfg, "XTTS", None)
    if xt:                                                               # XTTS: голос заранее синтезирован и проверен Whisper (xtts_prepare.py)
        import hashlib
        key = hashlib.md5(("xtts|" + xt["speaker"] + "|" + text).encode()).hexdigest(); f = f"{HERE}/work/tts/{key}.wav"
        if not os.path.exists(f): sys.exit(f"нет озвучки XTTS для: {text}\nзапусти: python3 xtts_prepare.py {sys.argv[1]}")
        return wavfile.read(f)[1].astype(np.float32) / 32768
    vk = getattr(cfg, "VOSK", None)
    if vk:                                                               # Vosk TTS: ударения по словарю, чистое произношение; паузы — между предложениями
        global _VOSK
        import re, scipy.signal as ss_
        if _VOSK is None:
            from vosk_tts import Model as VM, Synth as VS
            _VOSK = VS(VM(model_name=vk.get("model", "vosk-model-tts-ru-0.9-multi")))
        parts = [p for p in re.split(r"(?<=[.:!?])\s+", re.sub(r"[«»“”\"]", "", text if vk.get("stress") else text.replace("+", ""))) if p.strip()]; out = []
        for k, p in enumerate(parts):
            a = np.asarray(_VOSK.synth_audio(p, speaker_id=vk.get("speaker", 4), speech_rate=vk.get("rate", 1.0)), np.float32) / 32768.0
            out.append(ss_.resample_poly(a, SR, 22050).astype(np.float32))
            if k < len(parts) - 1: out.append(np.zeros(int(SR * vk.get("dot", 380) / 1000), np.float32))
        return np.concatenate(out)
    pr = getattr(cfg, "PROSODY", None)
    if pr:                                                               # «голос B»: темп и тон задаёт сам синтезатор (SSML), фраза целиком — живая интонация
        import re
        t = re.sub(r"([:.!?])\s+", lambda m: m.group(1) + f' <break time="{pr.get("dot", 380)}ms"/> ', text)
        t = re.sub(r",\s+", f', <break time="{pr.get("comma", 180)}ms"/> ', t).replace(" — ", f' <break time="{pr.get("dash", 260)}ms"/> ')
        return model.apply_tts(ssml_text=f'<speak><prosody rate="{pr.get("rate", "slow")}" pitch="{pr.get("pitch", "low")}">{t}</prosody></speak>',
                               speaker=spk, sample_rate=SR, put_accent=True, put_yo=True).numpy()
    sx = getattr(cfg, "SSML", None)
    if not sx: return model.apply_tts(text=text, speaker=spk, sample_rate=SR, put_accent=True, put_yo=True).numpy()
    # «естественный» режим: ударения ставит модель, паузы — тишина между частями фразы, темп и тон — через ffmpeg
    import re
    parts = [p for p in re.split(r"(?<=[.:!?])\s+|\s+—\s+", text) if p.strip()]
    seps = re.findall(r"(?<=[.:!?])\s+|\s+—\s+", text)
    out = []
    for k, p in enumerate(parts):
        out.append(model.apply_tts(text=p, speaker=spk, sample_rate=SR, put_accent=True, put_yo=True).numpy())
        if k < len(seps): out.append(np.zeros(int(SR * (sx.get("dash", 260) if "—" in seps[k] else sx.get("dot", 380)) / 1000)))
    a = np.concatenate(out); pf, tempo = sx.get("pitch", 1.0), sx.get("tempo", 1.0)
    if pf != 1.0 or tempo != 1.0:                                       # ниже тон (asetrate) и медленнее (atempo) без искажений
        src, dst = f"{WORK}/_t_in.wav", f"{WORK}/_t_out.wav"; wavfile.write(src, SR, (a / max(np.abs(a).max(), 1e-6) * 0.95 * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", src, "-af", f"asetrate={int(SR * pf)},aresample={SR},atempo={tempo / pf:.4f}", dst], check=True)
        a = wavfile.read(dst)[1].astype(np.float32) / 32767
    return a
LEAD0 = getattr(cfg, "LEAD0", LEAD)      # первая фраза может звучать сразу — хук в первую секунду
for i, sc in enumerate(SCENES):
    LEAD = LEAD0 if i == 0 else LEAD_N
    spk0 = sc[6] if len(sc) > 6 and sc[6] else getattr(cfg, "SPEAKER", "aidar")   # голос можно задать для каждой сцены
    if sc[1] == "SUB":                                                   # режим субтитров: каждая фраза озвучивается отдельно
        cur, parts = LEAD, []
        if getattr(cfg, "SENTENCES", False):                             # предложение озвучивается целиком (живая интонация), субтитры делятся по слогам
            for grp in sentences(sc[0]):
                a = tts(" ".join(grp), spk0); voice.append((t0 + cur, a))
                nz = np.nonzero(np.abs(a) > 0.02 * np.abs(a).max())[0]; s0, s1 = (nz[0], nz[-1]) if len(nz) else (0, len(a))
                syl = [max(1, sum(ch in "аеёиоуыэюяАЕЁИОУЫЭЮЯ" for ch in g)) for g in grp]; tot = sum(syl); acc = 0
                for g, n in zip(grp, syl):
                    b0 = (s0 + (s1 - s0) * acc / tot) / SR; acc += n; b1 = (s0 + (s1 - s0) * acc / tot) / SR
                    parts.append((cur + b0, cur + b1, clean(g)))
                cur += len(a) / SR + getattr(cfg, "GAP", 0.22)
        else:
          for ph in [p.strip() for p in sc[0].split("|") if p.strip()]:
            spk = spk0
            if ph.startswith("@"): spk, ph = ph[1:].split(":", 1); ph = ph.strip()
            a = tts(ph, spk); voice.append((t0 + cur, a)); parts.append((cur, cur + len(a) / SR, clean(ph))); cur += len(a) / SR + getattr(cfg, "GAP", 0.22)
        PHRASES[i] = parts; dur = cur - 0.22 + TAIL
    else:
        cur = LEAD
        for ph in [p.strip() for p in sc[0].split("|") if p.strip()]:
            a = tts(ph, spk0); voice.append((t0 + cur, a)); cur += len(a) / SR + 0.22
        dur = cur - 0.22 + TAIL
    STARTS.append(t0); DURS.append(dur); t0 += dur
LEAD = LEAD_N
DUR = t0
track = np.zeros(int(DUR * SR) + SR)
for st, a in voice: track[int(st * SR):int(st * SR) + len(a)] += a
wavfile.write(f"{WORK}/voice.wav", SR, (track / np.abs(track).max() * 0.9 * 32767).astype(np.int16))

# ---------- музыка ----------
N = len(track); tt = np.arange(N) / SR; mus = np.zeros(N)
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = getattr(cfg, "PROG", [[50, 57, 62, 65], [46, 53, 58, 62], [43, 55, 58, 62], [45, 52, 57, 61]]); bar = 6.0
for i in range(int(DUR / bar) + 1):
    s0, s1 = int(i * bar * SR), min(int((i + 1) * bar * SR + 2 * SR), N)
    if s0 >= N: break
    seg = tt[s0:s1] - i * bar; env = np.minimum(seg / 2.5, 1) * np.clip((bar + 2 - seg) / 2.5, 0, 1)
    vib = 1 + 0.002 * np.sin(2 * np.pi * 5 * seg)
    for m in prog[i % len(prog)]:
        f = note(m); mus[s0:s1] += env * (0.05 * np.sin(2 * np.pi * f * seg * vib) + 0.02 * np.sin(4 * np.pi * f * seg) + 0.01 * np.sin(6 * np.pi * f * seg))
    mus[s0:s1] += env * 0.06 * np.sin(2 * np.pi * note(prog[i % len(prog)][0] - 12) * seg)
    if getattr(cfg, "DRUM", False):                                      # редкий низкий барабан (для «военной» темы)
        for k in (0, 3):
            a0 = s0 + int(k * SR); a1 = min(a0 + int(0.8 * SR), N)
            if a0 < N: sg = tt[a0:a1] - tt[a0]; mus[a0:a1] += 0.25 * np.exp(-sg * 6) * np.sin(2 * np.pi * (55 + 40 * np.exp(-sg * 20)) * sg)
mus *= np.minimum(np.minimum(tt / 3, 1), np.clip((DUR - tt) / 3, 0, 1))
wavfile.write(f"{WORK}/music.wav", SR, (mus / np.abs(mus).max() * 0.8 * 32767).astype(np.int16))
MUSIC = getattr(cfg, "MUSIC", None)         # MUSIC = ("music/файл.mp3", старт_сек): настоящая запись вместо синтеза (public domain, fetch_music.sh)
if MUSIC:
    mfx = "highpass=f=50,equalizer=f=300:t=q:w=0.8:g=-3,equalizer=f=1500:t=q:w=0.9:g=-6,equalizer=f=3500:t=q:w=1:g=-4,lowpass=f=9000,loudnorm=I=-30:TP=-3"
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(MUSIC[1]), "-i", f"{HERE}/{MUSIC[0]}", "-t", f"{DUR + 1:.2f}",
                    "-af", f"{mfx},afade=t=in:d=2,afade=t=out:st={max(DUR - 3, 0):.2f}:d=3", "-ar", str(SR), f"{WORK}/music.wav"], check=True)

# ---------- картинки ----------
def grade(im):
    im = ImageEnhance.Color(im).enhance(0.82); im = ImageEnhance.Contrast(im).enhance(1.08)
    a = np.asarray(im).astype(np.float32); a[..., 0] *= 1.04; a[..., 2] *= 0.94
    return Image.fromarray(np.clip(a * 0.9, 0, 255).astype(np.uint8))
BIG = (int(W * 1.5), int(H * 1.5))
def prepare(name):
    im = Image.open(f"{HERE}/art/{name}.jpg").convert("RGB")
    if hasattr(cfg, "PREP") and name in cfg.PREP: im = cfg.PREP[name](im)
    if im.width / im.height > 1.0:                                       # горизонтальная картина: размытый фон + полотно в рамке
        bg = im.copy(); s = max(BIG[0] / bg.width, BIG[1] / bg.height)
        bg = bg.resize((int(bg.width * s), int(bg.height * s))).filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg.crop(((bg.width - BIG[0]) // 2, (bg.height - BIG[1]) // 2, (bg.width + BIG[0]) // 2, (bg.height + BIG[1]) // 2))).enhance(0.45)
        fw = int(BIG[0] * 0.92); fg = im.resize((fw, int(im.height * fw / im.width)), Image.LANCZOS); y = int(BIG[1] * 0.36) - fg.height // 2
        sh = Image.new("RGBA", BIG, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle(((BIG[0] - fw) // 2 + 10, y + 20, (BIG[0] + fw) // 2 + 10, y + fg.height + 20), fill=(0, 0, 0, 200))
        bg = bg.convert("RGBA"); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25))); bg = bg.convert("RGB")
        RECT[name] = ((BIG[0] - fw) // 2, y, (BIG[0] + fw) // 2, y + fg.height)
        bg.paste(fg, ((BIG[0] - fw) // 2, y)); ImageDraw.Draw(bg).rectangle(((BIG[0] - fw) // 2 - 3, y - 3, (BIG[0] + fw) // 2 + 2, y + fg.height + 2), outline=GOLD, width=3)
        return grade(bg)
    s = max(BIG[0] / im.width, BIG[1] / im.height); RECT[name] = (0, 0, int(im.width * s), int(im.height * s))
    return grade(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS))
RECT = {}   # картина -> прямоугольник самой картины внутри подложки (пиксели), для эффектов

# ---------- «живые картины»: снег, дождь, рябь воды, свечение (FX = {картина: [(эффект, параметры), ...]}) ----------
def fx_apply(name, im, t):
    fx = getattr(cfg, "FX", {}).get(name)
    if not fx: return im
    x0, y0, x1, y1 = RECT[name]; rw, rh = x1 - x0, y1 - y0
    im = im.copy()
    for kind, o in fx:
        bx = o.get("box", (0, 0, 1, 1)); X0, Y0, X1, Y1 = x0 + bx[0] * rw, y0 + bx[1] * rh, x0 + bx[2] * rw, y0 + bx[3] * rh
        r = np.random.default_rng(o.get("seed", 7))
        if kind in ("snow", "rain"):
            n = o.get("n", 160 if kind == "snow" else 240); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            px, py, sp, sz, ph = r.random(n), r.random(n), r.uniform(0.6, 1.4, n), r.uniform(0.6, 1.6, n), r.random(n) * 6.28
            H_ = Y1 - Y0
            for k in range(n):
                if kind == "snow":
                    y = Y0 + (py[k] * H_ + sp[k] * o.get("speed", 0.09) * H_ * t) % H_
                    x = X0 + (px[k] * (X1 - X0) + math.sin(t * 0.9 * sp[k] + ph[k]) * 14 * sz[k] + o.get("wind", 0.02) * (X1 - X0) * t) % (X1 - X0)
                    rad = o.get("size", 3.2) * sz[k]; al = int(o.get("alpha", 210) * (0.55 + 0.45 * sz[k] / 1.6))
                    d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(250, 250, 255, al))
                else:
                    ang = o.get("angle", 0.28); ln = o.get("len", 70) * sz[k]
                    y = Y0 + (py[k] * H_ + sp[k] * o.get("speed", 1.1) * H_ * t) % H_
                    x = X0 + (px[k] * (X1 - X0) + ang * (y - Y0)) % (X1 - X0)
                    d.line((x, y, x - ang * ln, y - ln), fill=(225, 232, 240, int(o.get("alpha", 95) * sz[k] / 1.6)), width=max(1, int(2 * sz[k])))
            lay = lay.crop((int(X0), int(Y0), int(X1), int(Y1))).filter(ImageFilter.GaussianBlur(o.get("blur", 1.0)))
            base = im.convert("RGBA"); base.alpha_composite(lay, (int(X0), int(Y0))); im = base.convert("RGB")
        elif kind == "shimmer":                                          # рябь: построчный сдвиг по синусоиде
            a = np.asarray(im).copy(); amp, wl, sp_ = o.get("amp", 2.5), o.get("wl", 22), o.get("speed", 2.2)
            for yy_ in range(int(Y0), int(Y1)):
                sh = int(round(amp * math.sin(yy_ / wl * 6.283 + t * sp_) * (0.5 + 0.5 * (yy_ - Y0) / max(Y1 - Y0, 1))))
                if sh: a[yy_, int(X0):int(X1)] = np.roll(a[yy_, int(X0):int(X1)], sh, axis=0)
            im = Image.fromarray(a)
        elif kind == "glow":                                             # пульсирующее свечение (луна, фонарь)
            cx, cy = x0 + o["at"][0] * rw, y0 + o["at"][1] * rh; rad = o.get("r", 0.08) * rw
            k_ = 0.75 + 0.25 * math.sin(t * o.get("speed", 1.3))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for j in range(12, 0, -1):
                rr_ = rad * j / 12 * 2.2; d.ellipse((cx - rr_, cy - rr_, cx + rr_, cy + rr_), fill=o.get("color", (255, 236, 190)) + (int(o.get("alpha", 26) * k_),))
            base = im.convert("RGBA"); base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(rad * 0.4))); im = base.convert("RGB")
    return im

# ---------- видеоклипы вместо картин (CLIPS = {картина: "путь.mp4"}): кадры клипа растягиваются на длину сцены ----------
CLIPF = {}
def clip_frames(path):
    if path not in CLIPF:
        while len(CLIPF) >= 2: del CLIPF[next(iter(CLIPF))]            # в памяти не больше двух клипов (для перехода)
        w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(","))
        raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        CLIPF[path] = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    return CLIPF[path]
def clip_plate(name, lt, D):
    fr = clip_frames(cfg.CLIPS[name]); n = len(fr); k = min(n - 1, max(0, int(lt / D * n)))
    im = Image.fromarray(fr[k]); orig = Image.open(f"{HERE}/art/{name}.jpg")
    if orig.width / orig.height > 1.0:                                   # горизонтальная: как картина в рамке
        if name not in CACHE: plate(name)
        bg = CACHE[name].copy(); x0, y0, x1, y1 = RECT[name]
        bg.paste(grade(im.resize((x1 - x0, y1 - y0), Image.LANCZOS)), (x0, y0)); return bg
    s = max(BIG[0] / im.width, BIG[1] / im.height)
    return grade(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS))
CACHE = {}
def plate(name):
    if name not in CACHE: CACHE[name] = prepare(name)
    return CACHE[name]
def camera(im, z, fx, fy):
    base = min(im.width / W, im.height / H); cw, ch = W * base / z, H * base / z
    cx = min(max(fx * im.width, cw / 2), im.width - cw / 2); cy = min(max(fy * im.height, ch / 2), im.height - ch / 2)
    return im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
TDY = getattr(cfg, "TEXT_DY", 0)
bot = np.clip((yy - 880 - TDY) / 620, 0, 1) ** 1.3 * getattr(cfg, "BOT_ALPHA", 238); top = np.clip((380 - yy) / 380, 0, 1) * getattr(cfg, "TOP_ALPHA", 150)
vig = np.clip(((xx - W / 2) ** 2 / (W * 0.75) ** 2 + (yy - H * 0.45) ** 2 / (H * 0.7) ** 2) - 0.35, 0, 1) * getattr(cfg, "VIG", 170)
OVER = Image.fromarray(np.dstack([np.full((H, W), 8), np.full((H, W), 6), np.full((H, W), 6), np.clip(np.maximum(np.maximum(bot, top), vig), 0, 245)]).astype(np.uint8), "RGBA")
rng = np.random.default_rng(1); GRAIN = [rng.normal(0, getattr(cfg, "GRAIN", 3.5), (H // 2, W // 2)).astype(np.int16) for _ in range(6)]

def spaced(d, xy, text, f, fill, sp=6):
    w = sum(d.textlength(c, font=f) + sp for c in text) - sp; x = xy[0] - w / 2
    for c in text: d.text((x, xy[1]), c, font=f, fill=fill, anchor="lm"); x += d.textlength(c, font=f) + sp
HEAD = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); hd = ImageDraw.Draw(HEAD)
spaced(hd, (W // 2, 150), cfg.HEAD[0], sans("Medium", 26), GOLD + (230,), 7)
hd.line(((W // 2 - 230, 190), (W // 2 + 230, 190)), fill=GOLD + (120,), width=1)
spaced(hd, (W // 2, 222), cfg.HEAD[1], sans("Medium", 22), GREY + (220,), 5)
F_TAG, F_CR = sans("SemiBold", 24), sans("Medium", 22)

def text_layer(i, lt, D):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    text, tag, credit = SCENES[i][1], SCENES[i][2], SCENES[i][4]; out = ease((D - lt - 0.15) / 0.5)
    if text is None:
        word, line2, line3 = cfg.TITLE; a = ease((lt - 0.4) / 1.0) * out
        size = 150
        while size > 80 and d.textlength(word, font=serif("Bold", size)) + 14 * len(word) > 980: size -= 6
        spaced(d, (W // 2, 1240 + TDY), word, serif("Bold", size), WHITE + (int(255 * a),), 14)
        d.line(((W // 2 - 120, 1345 + TDY), (W // 2 + 120, 1345 + TDY)), fill=GOLD + (int(200 * a),), width=2)
        b = ease((lt - 1.4) / 1.0) * out; d.text((W // 2, 1410 + TDY), line2, font=serif("MediumItalic", 58), fill=WHITE + (int(235 * b),), anchor="mm")
        c = ease((lt - 3.0) / 1.0) * out; spaced(d, (W // 2, 1500 + TDY), line3, sans("Medium", 24), GOLD + (int(230 * c),), 4)
    elif text == "SUB":
        a = ease((lt - 0.2) / 0.6) * out
        if tag: spaced(d, (W // 2, 1135 + TDY), tag, F_TAG, GOLD + (int(240 * a),), 6)
        parts = PHRASES[i]; cur = None
        for k, (st, en, ph) in enumerate(parts):
            nxt = parts[k + 1][0] if k + 1 < len(parts) else D
            if st - 0.08 <= lt < max(en + 0.35, nxt - 0.02) or (k == len(parts) - 1 and lt >= st): cur = (st, en, ph)
        if cur:
            st, en, ph = cur; fin = ease((lt - st + 0.08) / 0.18) * out
            SANS = getattr(cfg, "SUB_SANS", None)                          # SUB_SANS = "ExtraBold" — гротеск заглавными (эксперимент)
            words = (ph.upper() if SANS else ph).split(); lines, line = [], ""
            for w_ in words:
                if len(line) + len(w_) + 1 > getattr(cfg, "SUB_CHARS", 26) and line: lines.append(line); line = w_
                else: line = (line + " " + w_).strip()
            lines.append(line)
            mk = (lambda z: sans(SANS, z)) if SANS else (lambda z: serif(getattr(cfg, "SUB_FONT", "MediumItalic"), z))
            size = getattr(cfg, "QUOTE_SIZE", 72); fq = mk(size)
            while size > 40 and max(d.textlength(l, font=fq) for l in lines) > 960: size -= 2; fq = mk(size)
            total = sum(len(w_) + 1 for w_ in words); prog = (lt - st) / max(en - st, 0.1) * total; done = 0
            y0 = 1215 + TDY + int((1 - fin) * 14)
            kara = getattr(cfg, "SUB_STYLE", "") == "karaoke"
            if kara:                                                        # мягкая тёмная подложка под субтитрами
                bw = max(d.textlength(l, font=fq) for l in lines) + 90; bh = len(lines) * int(size * 1.18) + 40
                pad = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(pad).rounded_rectangle((W / 2 - bw / 2, y0 - size * 0.62 - 10, W / 2 + bw / 2, y0 - size * 0.62 + bh), 36, fill=(8, 6, 6, int(130 * fin)))
                lay.alpha_composite(pad.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(lay)
            for k, l in enumerate(lines):                                   # слова подсвечиваются по мере произнесения
                ws = l.split(); lw = d.textlength(l, font=fq); x = W // 2 - lw / 2; y = y0 + k * int(size * 1.18)
                for w_ in ws:
                    a0 = done; spoken = done + len(w_) * 0.5 <= prog; done += len(w_) + 1
                    col = WHITE if spoken else (205, 196, 182); al = int(255 * fin) if spoken else int(150 * fin)
                    if kara and a0 <= prog < done:                          # текущее слово — золотом
                        col, al = GOLD_HI, int(255 * fin)
                    if kara and not spoken and col != GOLD_HI: al = int(95 * fin)
                    d.text((x + 2, y + 3), w_, font=fq, fill=(0, 0, 0, int(110 * fin)), anchor="lm"); d.text((x, y), w_, font=fq, fill=col + (al,), anchor="lm")
                    x += d.textlength(w_ + " ", font=fq)
    else:
        a = ease((lt - 0.2) / 0.6) * out; spaced(d, (W // 2, 1135 + TDY), tag, F_TAG, GOLD + (int(240 * a),), 6)
        lines = text.split("\n"); speak = D - LEAD - TAIL; size = getattr(cfg, "QUOTE_SIZE", 80)
        while size > 56 and max(d.textlength(l, font=serif("MediumItalic", size)) for l in lines) > 960: size -= 2
        fq = serif("MediumItalic", size)
        for k, line in enumerate(lines):
            st = LEAD + speak * (0.12 + 0.62 * k / len(lines)); b = ease((lt - st) / 0.7) * out
            if b <= 0: continue
            y = 1215 + TDY + k * int(size * 1.15) + int((1 - b) * 18)
            d.text((W // 2 + 2, y + 3), line, font=fq, fill=(0, 0, 0, int(120 * b)), anchor="mm")
            d.text((W // 2, y), line, font=fq, fill=WHITE + (int(255 * b),), anchor="mm")
    cr = ease((lt - 1.0) / 0.8) * out; d.text((W // 2, 1640 + min(TDY, 150)), credit, font=F_CR, fill=GREY + (int(200 * cr),), anchor="mm")
    return lay

def hook_layer(lt):
    """Хук: крупная надпись в первые секунды — появляется с «ударом» и лёгкой тряской."""
    txt, t1 = cfg.HOOK; a = ease(lt / 0.18) * ease((t1 - lt) / 0.35)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if a <= 0: return lay
    d = ImageDraw.Draw(lay); f = sans("Black", getattr(cfg, "HOOK_SIZE", 88)); y = getattr(cfg, "HOOK_Y", 360)
    x0, y0, x1, y1 = d.multiline_textbbox((W // 2, y), txt, font=f, anchor="ma", align="center", spacing=16)
    d.rounded_rectangle((x0 - 44, y0 - 34, x1 + 44, y1 + 44), 30, fill=(150, 24, 30, int(236 * a)))
    d.rounded_rectangle((x0 - 44, y0 - 34, x1 + 44, y1 + 44), 30, outline=GOLD + (int(200 * a),), width=3)
    d.multiline_text((W // 2, y), txt, font=f, fill=(255, 250, 240, int(255 * a)), anchor="ma", align="center", spacing=16)
    s = 1.0 + 0.25 * (1 - ease(lt / 0.22)); rot = 2.2 * math.sin(lt * 38) * max(0, 1 - lt / 0.8)
    if s != 1.0 or rot:
        lay = lay.rotate(rot, center=(W // 2, y + 100), resample=Image.BICUBIC)
        big = lay.resize((int(W * s), int(H * s)), Image.BICUBIC); cx, cy = W / 2, y + 100
        lay = big.crop((int(cx * s - cx), int(cy * s - cy), int(cx * s - cx) + W, int(cy * s - cy) + H))
    return lay

def stamp_layer(text, lt, y):
    """Штамп-вердикт («МИФ», «ПРАВДА»): падает с «ударом», чуть повёрнут, держится до конца сцены."""
    a = ease(lt / 0.12); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if a <= 0: return lay
    d = ImageDraw.Draw(lay); f = sans("Black", 150); col = (200, 30, 36) if text != "ПРАВДА" else (40, 150, 70)
    x0, y0, x1, y1 = d.textbbox((W // 2, y), text, font=f, anchor="mm")
    for k in (0, 10): d.rounded_rectangle((x0 - 50 + k, y0 - 40 + k, x1 + 50 - k, y1 + 40 - k), 26, outline=col + (int(235 * a),), width=10 if k == 0 else 4)
    d.text((W // 2, y), text, font=f, fill=col + (int(240 * a),), anchor="mm")
    s = 1.0 + 0.6 * (1 - ease(lt / 0.15)); lay = lay.rotate(-8, center=(W // 2, y), resample=Image.BICUBIC)
    if s != 1.0:
        big = lay.resize((int(W * s), int(H * s)), Image.BICUBIC); lay = big.crop((int(W / 2 * s - W / 2), int(y * s - y), int(W / 2 * s - W / 2) + W, int(y * s - y) + H))
    return lay

def scene_frame(i, lt):
    D = DURS[i]; src = SCENES[i][3]
    if callable(src):                                                    # анимированная сцена: сглаживание краёв + медленный наезд камеры
        im = src(lt, D).filter(ImageFilter.GaussianBlur(getattr(cfg, "AA", 0.8)))
        z = 1.0 + 0.05 * (lt / D); cw, ch = W / z, H / z
        im = im.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) * 0.4, (W + cw) / 2, (H - ch) * 0.4 + ch)).convert("RGBA")
    else:
        z0, z1, (fx0, fy0), (fx1, fy1) = SCENES[i][5]; u = ease(lt / D) * 0.85 + (lt / D) * 0.15
        cuts = getattr(cfg, "CUTS", {}).get(i)                           # быстрый монтаж: внутри сцены картины меняются каждые CUT_LEN с
        if cuts:
            seq = [src] + list(cuts); cl = getattr(cfg, "CUT_LEN", 1.0); k = min(int(lt / cl), len(seq) - 1) if getattr(cfg, "CUT_ONCE", False) else int(lt / cl) % len(seq)
            src = seq[k]; u = ((lt % cl) / cl)
        pl = clip_plate(src, lt, D) if src in getattr(cfg, "CLIPS", {}) else plate(src)
        if src in getattr(cfg, "CLIPS", {}) and src not in RECT: plate(src)
        pl = fx_apply(src, pl, lt)
        im = camera(pl, z0 + (z1 - z0) * u, fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u).convert("RGBA")
    im.alpha_composite(OVER); im.alpha_composite(HEAD, (0, 0)); im.alpha_composite(text_layer(i, lt, D))
    if i == 0 and hasattr(cfg, "HOOK"): im.alpha_composite(hook_layer(lt))
    st = getattr(cfg, "STAMPS", {}).get(i)                                # штамп-вердикт: {сцена: ("МИФ", секунда)}
    if st and lt >= st[1]: im.alpha_composite(stamp_layer(st[0], lt - st[1], getattr(cfg, "STAMP_Y", 760)))
    return im.convert("RGB")

def frame(t, n):
    i = max(k for k in range(len(STARTS)) if STARTS[k] <= t); lt = t - STARTS[i]
    im = scene_frame(i, lt)
    if lt < XF and i > 0: im = Image.blend(scene_frame(i - 1, lt + DURS[i - 1]), im, ease(lt / XF))
    FI = getattr(cfg, "FADE_IN", 0.8)
    if t < FI: im = Image.blend(Image.new("RGB", (W, H)), im, ease(t / FI))
    if DUR - t < 1.0: im = Image.blend(Image.new("RGB", (W, H)), im, ease((DUR - t) / 1.0))
    a = np.asarray(im).astype(np.int16); a += np.repeat(np.repeat(GRAIN[n % len(GRAIN)], 2, 0), 2, 1)[..., None]
    return np.clip(a, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    print("длительность", round(DUR, 1), "с, сцены", [round(d, 1) for d in DURS])
    if len(sys.argv) > 3:
        for k, x in enumerate(map(float, sys.argv[3].split(","))): Image.fromarray(frame(x, k)).resize((360, 640)).save(f"{WORK}/pv_{k}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", "19", "-maxrate", "6M", "-bufsize", "12M", "-profile:v", "high", "-pix_fmt", "yuv420p", f"{WORK}/video.mp4"], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)): p.stdin.write(frame(n / FPS, n).tobytes())
    p.stdin.close(); p.wait()
    vfx = getattr(cfg, "VOICE_FX", "highpass=f=80,equalizer=f=3500:t=q:w=1.5:g=1.5,deesser=i=0.2")   # обработка голоса (VOICE_FX — «студийная»)
    fc = (f"[1:a]{vfx},asplit[v][vk];" +
          (f"[2:a]volume=1[m];[m][vk]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=700[md];" if MUSIC else "[2:a]volume=0.14[m];[m][vk]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=600[md];") +
          "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{WORK}/video.mp4", "-i", f"{WORK}/voice.wav", "-i", f"{WORK}/music.wav",
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.2f}", "-movflags", "+faststart", OUT], check=True)
    # облегчённая копия до ~27 МБ — чтобы отправить в чат; оригинал высокого качества остаётся для загрузки в Instagram
    kbps = int(27 * 8 * 1024 / DUR - 200); light = OUT.replace(".mp4", "_light.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", OUT, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k", "-maxrate", f"{kbps}k", "-bufsize", f"{2 * kbps}k",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", light], check=True)
    print("done", OUT, f"{DUR:.1f} c", "+", light)
