"""Reels 9:16: «5 ошибок при покупке студии». Кадры — Pillow, музыка — numpy, сборка — ffmpeg."""
import math, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 20.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "reel.mp4"
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BG1, BG2 = (14, 20, 48), (40, 18, 70)
ACCENT, RED, WHITE, MUTED = (255, 196, 0), (255, 70, 85), (255, 255, 255), (190, 196, 225)

SLIDES = [  # (start, end, kind, emoji, title, subtitle)
    (0, 2, "hook", "⚠️", "Не покупай\nстудию, пока\nне посмотришь это", ""),
    (2, 5, "err", "📉", "Смотреть только на цену,\nа не на цену за м²", "Дешёвая студия может оказаться\nсамой дорогой за метр"),
    (5, 8, "err", "📄", "Не проверить застройщика\nи документы", "Проектная декларация,\nДДУ, эскроу-счёт"),
    (8, 11, "err", "💳", "Не спросить\nпро рассрочку без %", "Многие застройщики её дают —\nпросто спросите"),
    (11, 14, "err", "🚇", "Забыть про дорогу\nдо метро / МЦД", "Проверьте путь в час пик,\nа не только по карте"),
    (14, 17, "err", "🤝", "Не торговаться", "2% от 6 млн ₽ —\nэто 120 000 ₽"),
    (17, 20, "cta", "📌", "Сохрани,\nчтобы не забыть", "И отправь тому, кто ищет квартиру"),
]

def font(w, s): return ImageFont.truetype(INTER.format(w), s)
F_TITLE, F_HOOK, F_SUB, F_LABEL, F_NUM = font("ExtraBold", 84), font("Black", 96), font("Medium", 50), font("Bold", 44), font("Black", 300)
EMO = ImageFont.truetype(EMOJI, 109)
_emoji_cache = {}

def emoji(ch, size):
    key = (ch, size)
    if key not in _emoji_cache:
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((80, 80), ch, font=EMO, embedded_color=True, anchor="mm")
        im = im.crop(im.getbbox())
        _emoji_cache[key] = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    return _emoji_cache[key]

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

# фон: диагональный градиент + мягкие пятна света
yy, xx = np.mgrid[0:H, 0:W]
t = ((xx / W) * 0.4 + (yy / H) * 0.6)[..., None]
BASE = (np.array(BG1) * (1 - t) + np.array(BG2) * t).astype(np.float32)

def background(time):
    img = BASE.copy()
    for cx, cy, r, col, ph in [(0.2, 0.25, 520, (90, 60, 200), 0), (0.85, 0.75, 600, (200, 60, 120), 2)]:
        cx = cx * W + 60 * math.sin(time * 0.6 + ph); cy = cy * H + 80 * math.cos(time * 0.5 + ph)
        d = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None]
        img += d * np.array(col) * 0.35
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")

BG_CACHE = [background(i / 6) for i in range(int(DUR * 6) + 1)]  # 6 вариантов фона в секунду, дешевле

def fit(d, text, weight, size, maxw=900, spacing=18):
    while size > 30:
        f = font(weight, size)
        if d.multiline_textbbox((0, 0), text, font=f, spacing=spacing)[2] <= maxw: return f
        size -= 4
    return font(weight, size)

def centered(d, y, text, f, fill, spacing=18, shadow=True):
    if shadow:
        d.multiline_text((W // 2 + 4, y + 5), text, font=f, fill=(0, 0, 0, 120), anchor="ma", align="center", spacing=spacing)
    d.multiline_text((W // 2, y), text, font=f, fill=fill, anchor="ma", align="center", spacing=spacing)

def frame(time):
    base = BG_CACHE[min(int(time * 6), len(BG_CACHE) - 1)].convert("RGBA")
    s = next(s for s in SLIDES if s[0] <= time < s[1] or s is SLIDES[-1])
    start, end, kind, emo, title, sub = s
    lt = time - start
    a_in, a_out = ease(lt / 0.35), ease((end - time) / 0.25) if s is not SLIDES[-1] else 1
    alpha = min(a_in, a_out)
    dy = int((1 - a_in) * 120)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if kind == "hook":
        shake = int(10 * math.sin(lt * 55) * max(0, 1 - lt / 1.2))
        layer.alpha_composite(emoji(emo, 220), (W // 2 - 110 + shake, 560 + dy))
        f = fit(d, title, "Black", 96, 860, 22)
        x0, y0, x1, y1 = d.multiline_textbbox((W // 2, 880 + dy), title, font=f, anchor="ma", align="center", spacing=22)
        d.rounded_rectangle((x0 - 50, y0 - 50, x1 + 50, y1 + 60), 40, fill=RED + (235,))
        centered(d, 880 + dy, title, f, WHITE, spacing=22)
        layer = layer.rotate(math.sin(lt * 40) * 2.2 * max(0, 1 - lt / 1.2), center=(W // 2, 900))
    elif kind == "err":
        n = SLIDES.index(s)
        num_im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(num_im).text((W - 70, 330), str(n), font=F_NUM, fill=ACCENT + (40,), anchor="ra")
        layer.alpha_composite(num_im)
        d.rounded_rectangle((W // 2 - 190, 420 + dy, W // 2 + 190, 500 + dy), 40, fill=ACCENT)
        d.text((W // 2, 460 + dy), f"ОШИБКА №{n}", font=F_LABEL, fill=BG1, anchor="mm")
        layer.alpha_composite(emoji(emo, 200), (W // 2 - 100, 560 + dy))
        centered(d, 830 + dy, title, fit(d, title, "ExtraBold", 84, 920), WHITE)
        sa = ease((lt - 0.4) / 0.4)
        if sa > 0:
            d.line((W // 2 - 80, 1080 + dy, W // 2 + 80, 1080 + dy), fill=ACCENT, width=6)
            centered(d, 1120 + dy, sub, fit(d, sub, "Medium", 50, 920, 14), MUTED + (int(255 * sa),), spacing=14, shadow=False)
    else:  # cta
        pulse = 1 + 0.06 * math.sin(lt * 6)
        e = emoji(emo, int(220 * pulse))
        layer.alpha_composite(e, (W // 2 - e.width // 2, 620 - e.height // 2 + 110 + dy))
        centered(d, 900 + dy, title, F_HOOK, ACCENT, spacing=22)
        centered(d, 1160 + dy, sub, fit(d, sub, "Medium", 50, 920), MUTED, shadow=False)

    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(layer, (0, 130))

    # прогресс-бар сверху (в безопасной зоне Reels)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((90, 230, W - 90, 242), 6, fill=(255, 255, 255, 50))
    d.rounded_rectangle((90, 230, 90 + int((W - 180) * min(time / DUR, 1)), 242), 6, fill=ACCENT)
    return base.convert("RGB")

# ---------- музыка: 120 BPM, Am–F–C–G, бочка, хэт, бас, пэд ----------
SR = 44100
N = int(SR * DUR)
tt = np.arange(N) / SR
beat = 0.5
mus = np.zeros(N)
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [67, 71, 74])]  # бас, аккорд
bar = beat * 4
for i in range(int(DUR / bar) + 1):
    b, ch = prog[i % 4]
    s0, s1 = int(i * bar * SR), min(int((i + 1) * bar * SR), N)
    if s0 >= N: break
    seg = tt[s0:s1] - i * bar
    env = np.minimum(seg / 0.3, 1) * np.minimum((bar - seg) / 0.3, 1)
    pad = sum(np.sin(2 * np.pi * note(m) * seg) + 0.3 * np.sin(2 * np.pi * note(m) * 2.003 * seg) for m in ch)
    mus[s0:s1] += 0.06 * env * pad
    for k in range(8):  # бас восьмыми
        a0 = s0 + int(k * beat / 2 * SR); a1 = min(a0 + int(beat / 2 * SR), N)
        if a0 >= N: break
        sg = tt[a0:a1] - tt[a0]
        mus[a0:a1] += 0.18 * np.exp(-sg * 6) * np.tanh(2 * np.sin(2 * np.pi * note(b - 12) * sg))
rng = np.random.default_rng(1)
for k in range(int(DUR / beat)):
    a0 = int(k * beat * SR); L = int(0.35 * SR); a1 = min(a0 + L, N)
    sg = tt[a0:a1] - tt[a0]
    mus[a0:a1] += 0.55 * np.exp(-sg * 9) * np.sin(2 * np.pi * (45 + 90 * np.exp(-sg * 30)) * sg)  # бочка
    h0 = a0 + int(beat / 2 * SR); h1 = min(h0 + int(0.06 * SR), N)
    if h0 < N:
        hs = tt[h0:h1] - tt[h0]
        mus[h0:h1] += 0.06 * np.exp(-hs * 60) * rng.standard_normal(h1 - h0)  # хэт
# «вжух» на смене слайдов
for s in SLIDES[1:]:
    a0 = int((s[0] - 0.25) * SR); a1 = int(s[0] * SR)
    sg = np.linspace(0, 1, a1 - a0)
    mus[a0:a1] += 0.05 * sg ** 2 * rng.standard_normal(a1 - a0)
fade = np.minimum(np.minimum(tt / 0.3, 1), np.minimum((DUR - tt) / 1.5, 1))
mus *= fade
mus = mus / np.max(np.abs(mus)) * 0.85
pcm = (np.repeat(mus[:, None], 2, 1) * 32767).astype(np.int16)
with wave.open("music.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())

# ---------- сборка ----------
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", "music.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
                      "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait()
print("done", OUT)
