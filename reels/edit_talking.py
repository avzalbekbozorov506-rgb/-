"""Монтаж «говорящей головы» для Reels: 1080×1920, цветокоррекция, резкие наезды камеры на ключевых словах,
всплывающие слова с эмодзи, плашка-тема в начале, полоса прогресса, призыв подписаться в конце, чистый звук + тихая музыка.
Использование: python3 edit_talking.py <папка с src.mp4 и audio_fixed.mp4> <out.mp4>  (сценарий — словарь PLAN ниже)."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from scipy.io import wavfile
D, OUT = sys.argv[1], sys.argv[2]; W, H, FPS = 1080, 1920, 30
SRC, AUD = f"{D}/src.mp4", f"{D}/audio_fixed.mp4"
w0, h0 = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout.strip().split(","))
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)
# ---------- сценарий монтажа: (начало, конец, текст, эмодзи, цвет плашки) ----------
POPS = [(0.75, 1.75, "AMERIKA", "🇺🇸", (40, 70, 160)), (1.7, 2.95, "PREZIDENT", "🏛", (150, 30, 40)),
        (4.7, 7.0, "SUN'IY\nINTELLEKT", "🤖", (90, 40, 170))]
PUNCH = [0.75, 1.7, 4.7, 8.6]                                   # резкие наезды камеры
TOPIC = ("AMERIKA VA\nSUN'IY INTELLEKT", 0.0, 2.2)
CTA = (8.4, "OBUNA BO'LING!", "✌️")
def font(w, s): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
F_POP, F_TOP, F_CTA = font("Black", 92), font("Black", 78), font("Black", 80)
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def emoji(ch, size):
    im = Image.new("RGBA", (150, 150), (0, 0, 0, 0)); ImageDraw.Draw(im).text((75, 75), ch, font=EMO, embedded_color=True, anchor="mm")
    return im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)
EMOS = {e: emoji(e, 150) for e in {p[3] for p in POPS} | {CTA[2]}}
def pill(d, box, col, a): d.rounded_rectangle(box, 34, fill=col + (a,))
def pop_layer(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for t0, t1, txt, em, col in POPS:
        if not (t0 <= t < t1): continue
        k = t - t0; a = ease(k / 0.12) * ease((t1 - t) / 0.18); s = 1 + 0.35 * (1 - ease(k / 0.18)) - 0.04 * ease((k - 0.2) / 0.6)
        tile = Image.new("RGBA", (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(tile)
        x0, y0, x1, y1 = d.multiline_textbbox((W // 2, 300), txt, font=F_POP, anchor="ma", align="center", spacing=6)
        sh = Image.new("RGBA", tile.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 - 46, y0 - 30 + 16, x1 + 46, y1 + 40 + 16), 36, fill=(0, 0, 0, 150))
        tile.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(tile)
        pill(d, (x0 - 46, y0 - 30, x1 + 46, y1 + 40), col, 240); d.rounded_rectangle((x0 - 46, y0 - 30, x1 + 46, y1 + 40), 36, outline=(255, 214, 120, 255), width=4)
        d.multiline_text((W // 2, 300), txt, font=F_POP, fill=(255, 255, 255), anchor="ma", align="center", spacing=6)
        e = EMOS[em]; tile.alpha_composite(e, (W // 2 - 75, int(y0 - 30 - 130 + 12 * math.sin(t * 8))))
        tile = tile.resize((int(W * s), int(560 * s)), Image.BICUBIC); tile.putalpha(tile.getchannel("A").point(lambda v: int(v * a)))
        rot = 3 * math.sin(k * 30) * max(0, 1 - k / 0.3)
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=False)
        lay.alpha_composite(tile, (int(W / 2 - tile.width / 2), int(1440 - tile.height / 2)))
    return lay
def topic_layer(t):
    txt, t0, t1 = TOPIC; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not (t0 <= t < t1): return lay
    a = ease((t - t0) / 0.2) * ease((t1 - t) / 0.3); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = d.multiline_textbbox((W // 2, 300), txt, font=F_TOP, anchor="ma", align="center", spacing=10)
    pill(d, (x0 - 40, y0 - 26, x1 + 40, y1 + 34), (196, 24, 36), int(235 * a))
    d.multiline_text((W // 2, 300), txt, font=F_TOP, fill=(255, 255, 255, int(255 * a)), anchor="ma", align="center", spacing=10)
    return lay
def cta_layer(t):
    t0, txt, em = CTA; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < t0: return lay
    k = t - t0; a = ease(k / 0.2); s = 1 + 0.3 * (1 - ease(k / 0.25)) + 0.03 * math.sin(k * 6)
    tile = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(tile)
    x0, y0, x1, y1 = d.textbbox((W // 2 + 60, 200), txt, font=F_CTA, anchor="mm")
    pill(d, (x0 - 150, y0 - 34, x1 + 44, y1 + 34), (232, 30, 70), 245); d.text((W // 2 + 60, 200), txt, font=F_CTA, fill=(255, 255, 255), anchor="mm")
    tile.alpha_composite(EMOS[em].resize((110, 110)), (int(x0 - 130), 145))
    tile = tile.resize((int(W * s), int(400 * s)), Image.BICUBIC); tile.putalpha(tile.getchannel("A").point(lambda v: int(v * a)))
    lay.alpha_composite(tile, (int(W / 2 - tile.width / 2), int(1500 - tile.height / 2))); return lay
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = Image.fromarray(np.dstack([np.zeros((H, W)), np.zeros((H, W)), np.zeros((H, W)),
      np.clip(((xx - W / 2) ** 2 / (W * 0.72) ** 2 + (yy - H * 0.45) ** 2 / (H * 0.62) ** 2 - 0.45) * 190, 0, 150)]).astype(np.uint8), "RGBA")
def zoom_at(t):
    z = 1.04 + 0.015 * math.sin(t * 0.7)
    for p in PUNCH:
        k = t - p
        if 0 <= k < 0.9: z += 0.11 * (1 - ease(k / 0.9)) * ease(k / 0.06)
    return z
def frame(img, t):
    im = img.resize((W, H), Image.LANCZOS)
    z = zoom_at(t); cw, ch = W / z, H / z; cy = H * 0.42
    im = im.resize((W, H), Image.BICUBIC, box=(W / 2 - cw / 2, cy - ch * 0.42, W / 2 + cw / 2, cy - ch * 0.42 + ch))
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.12)).enhance(1.08)
    a = np.asarray(im).astype(np.float32); a[..., 0] *= 1.03; a[..., 2] *= 0.96; im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    im.alpha_composite(VIG); im.alpha_composite(topic_layer(t)); im.alpha_composite(pop_layer(t)); im.alpha_composite(cta_layer(t))
    d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 12), fill=(0, 0, 0, 120)); d.rectangle((0, 0, int(W * t / DUR), 12), fill=(255, 210, 90))   # прогресс
    return im.convert("RGB")
# ---------- музыка: мягкий бит, глушится голосом ----------
SR = 48000; N = int(DUR * SR) + SR; tt = np.arange(N) / SR; mus = np.zeros(N)
def note(m): return 440 * 2 ** ((m - 69) / 12)
bpm = 96; beat = 60 / bpm
for i, ch in enumerate([[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]] * 4):
    s0 = int(i * 4 * beat * SR); s1 = min(int((i + 1) * 4 * beat * SR), N)
    if s0 >= N: break
    seg = tt[s0:s1] - tt[s0]; env = np.minimum(seg / 0.3, 1) * np.clip((4 * beat - seg) / 0.4, 0, 1)
    for m in ch: mus[s0:s1] += 0.05 * env * np.sin(2 * np.pi * note(m) * seg)
for b in range(int(DUR / beat) + 1):
    a0 = int(b * beat * SR); a1 = min(a0 + int(0.25 * SR), N)
    if a0 < N: sg = tt[a0:a1] - tt[a0]; mus[a0:a1] += 0.35 * np.exp(-sg * 18) * np.sin(2 * np.pi * (52 + 70 * np.exp(-sg * 30)) * sg)
    h0_ = a0 + int(beat / 2 * SR); h1_ = min(h0_ + int(0.05 * SR), N)
    if h0_ < N: mus[h0_:h1_] += 0.04 * np.random.default_rng(b).normal(0, 1, h1_ - h0_) * np.exp(-np.arange(h1_ - h0_) / SR * 60)
mus *= np.minimum(tt / 0.5, 1) * np.clip((DUR - tt) / 0.8, 0, 1)
os.makedirs(f"{D}/tmp", exist_ok=True); wavfile.write(f"{D}/tmp/music.wav", SR, (mus / np.abs(mus).max() * 0.8 * 32767).astype(np.int16))
# ---------- рендер ----------
dec = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", SRC, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", f"{D}/tmp/video.mp4"], stdin=subprocess.PIPE)
n = 0; fs = w0 * h0 * 3
while True:
    raw = dec.stdout.read(fs)
    if len(raw) < fs: break
    enc.stdin.write(frame(Image.frombytes("RGB", (w0, h0), raw), n / FPS).tobytes()); n += 1
enc.stdin.close(); enc.wait()
fc = "[1:a]asplit[v][vk];[2:a]volume=0.22[m];[m][vk]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=300[md];[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]"
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{D}/tmp/video.mp4", "-i", AUD, "-i", f"{D}/tmp/music.wav", "-filter_complex", fc,
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.2f}", "-movflags", "+faststart", OUT], check=True)
print("готово", OUT, n, "кадров")
