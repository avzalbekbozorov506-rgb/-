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
def serif(style, size): return ImageFont.truetype(f"{HERE}/fonts/CormorantGaramond-{style}.ttf", size)
def sans(style, size): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{style}.otf", size)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
SCENES = cfg.SCENES          # (озвучка, текст или None для титула, метка, картина|функция(lt, D), подпись, камера)
LEAD, TAIL, XF = 0.6, 1.0, 0.7

# ---------- озвучка ----------
model = torch.package.PackageImporter(SILERO).load_pickle("tts_models", "model"); model.to("cpu")
SR = 48000; voice, STARTS, DURS, t0 = [], [], [], 0.0
PHRASES = {}   # сцена -> [(начало, конец, текст)] — для субтитров, точно совпадающих с голосом
def clean(t): return t.replace("+", "")
def tts(text, spk): return model.apply_tts(text=text, speaker=spk, sample_rate=SR, put_accent=True, put_yo=True).numpy()
for i, sc in enumerate(SCENES):
    spk0 = sc[6] if len(sc) > 6 and sc[6] else getattr(cfg, "SPEAKER", "aidar")   # голос можно задать для каждой сцены
    if sc[1] == "SUB":                                                   # режим субтитров: каждая фраза озвучивается отдельно
        cur, parts = LEAD, []
        for ph in [p.strip() for p in sc[0].split("|") if p.strip()]:
            spk = spk0
            if ph.startswith("@"): spk, ph = ph[1:].split(":", 1); ph = ph.strip()
            a = tts(ph, spk); voice.append((t0 + cur, a)); parts.append((cur, cur + len(a) / SR, clean(ph))); cur += len(a) / SR + 0.22
        PHRASES[i] = parts; dur = cur - 0.22 + TAIL
    else:
        a = tts(sc[0], spk0); voice.append((t0 + LEAD, a)); dur = LEAD + len(a) / SR + TAIL
    STARTS.append(t0); DURS.append(dur); t0 += dur
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
        bg.paste(fg, ((BIG[0] - fw) // 2, y)); ImageDraw.Draw(bg).rectangle(((BIG[0] - fw) // 2 - 3, y - 3, (BIG[0] + fw) // 2 + 2, y + fg.height + 2), outline=GOLD, width=3)
        return grade(bg)
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
            words = ph.split(); lines, line = [], ""
            for w_ in words:
                if len(line) + len(w_) + 1 > getattr(cfg, "SUB_CHARS", 26) and line: lines.append(line); line = w_
                else: line = (line + " " + w_).strip()
            lines.append(line)
            size = getattr(cfg, "QUOTE_SIZE", 72); fq = serif("MediumItalic", size)
            while size > 50 and max(d.textlength(l, font=fq) for l in lines) > 960: size -= 2; fq = serif("MediumItalic", size)
            total = sum(len(w_) + 1 for w_ in words); prog = (lt - st) / max(en - st, 0.1) * total; done = 0
            y0 = 1215 + TDY + int((1 - fin) * 14)
            for k, l in enumerate(lines):                                   # слова подсвечиваются по мере произнесения
                ws = l.split(); lw = d.textlength(l, font=fq); x = W // 2 - lw / 2; y = y0 + k * int(size * 1.18)
                for w_ in ws:
                    spoken = done + len(w_) * 0.5 <= prog; done += len(w_) + 1
                    col = WHITE if spoken else (205, 196, 182); al = int(255 * fin) if spoken else int(150 * fin)
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

def scene_frame(i, lt):
    D = DURS[i]; src = SCENES[i][3]
    if callable(src):                                                    # анимированная сцена: сглаживание краёв + медленный наезд камеры
        im = src(lt, D).filter(ImageFilter.GaussianBlur(getattr(cfg, "AA", 0.8)))
        z = 1.0 + 0.05 * (lt / D); cw, ch = W / z, H / z
        im = im.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) * 0.4, (W + cw) / 2, (H - ch) * 0.4 + ch)).convert("RGBA")
    else:
        z0, z1, (fx0, fy0), (fx1, fy1) = SCENES[i][5]; u = ease(lt / D) * 0.85 + (lt / D) * 0.15
        im = camera(plate(src), z0 + (z1 - z0) * u, fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u).convert("RGBA")
    im.alpha_composite(OVER); im.alpha_composite(HEAD, (0, 0)); im.alpha_composite(text_layer(i, lt, D))
    return im.convert("RGB")

def frame(t, n):
    i = max(k for k in range(len(STARTS)) if STARTS[k] <= t); lt = t - STARTS[i]
    im = scene_frame(i, lt)
    if lt < XF and i > 0: im = Image.blend(scene_frame(i - 1, lt + DURS[i - 1]), im, ease(lt / XF))
    if t < 0.8: im = Image.blend(Image.new("RGB", (W, H)), im, ease(t / 0.8))
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
    fc = ("[1:a]highpass=f=80,equalizer=f=3500:t=q:w=1.5:g=1.5,deesser=i=0.2,asplit[v][vk];"
          "[2:a]volume=0.14[m];[m][vk]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=600[md];"
          "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{WORK}/video.mp4", "-i", f"{WORK}/voice.wav", "-i", f"{WORK}/music.wav",
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.2f}", "-movflags", "+faststart", OUT], check=True)
    # облегчённая копия до ~27 МБ — чтобы отправить в чат; оригинал высокого качества остаётся для загрузки в Instagram
    kbps = int(27 * 8 * 1024 / DUR - 200); light = OUT.replace(".mp4", "_light.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", OUT, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k", "-maxrate", f"{kbps}k", "-bufsize", f"{2 * kbps}k",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", light], check=True)
    print("done", OUT, f"{DUR:.1f} c", "+", light)
