"""Формат «Объясняем» — 2D-анимация в стиле тёмной научной презентации (HUD, голубые линии, жёлтые цифры, слова-субтитры).
Ролик: «Tesla Roadster едет по потолку» (показ 15.10.2026). Сборка: python3 reels/explainer/build.py [out.mp4] [t1,t2,...]  (превью кадров по секундам)."""
import os, sys, math, re, hashlib, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile
import scipy.signal as ss
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "cubes"))
from subs_sync import sync
sys.path.insert(0, HERE)
W, H, FPS, SR = 1080, 1920, 24, 48000
TMP = "/tmp/expl"; os.makedirs(TMP, exist_ok=True)
FD = "/usr/share/fonts/opentype/inter/"
def F(sz, w="Bold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", sz)
VOICE = dict(speaker=4, rate=.9)
GAP, LEAD, TAIL = .45, .25, .45

BG, CY, CY2, YEL, RED, GRN, WHITE = (6, 10, 22), (60, 200, 255), (30, 110, 160), (255, 176, 40), (255, 80, 80), (60, 230, 150), (240, 244, 250)

# ---------- сценарий: (имя сцены, озвучка с ударениями «+») ----------
SCRIPT = [
 ("hook",   "Эта машина едет по потолку. И не падает."),
 ("parts",  "Давай разберём её. Внутри вентиляторы, баллоны и сопла."),
 ("event",  "Пятнадцатого октября Т+эсла показала новый Р+оудстер. Он въехал вверх колёсами по рампе, перевернулся в воздухе и сел на асфальт. Как это возможно?"),
 ("ceil",   "Начнём с потолка. Его не присасывает. Его прижимает воздух."),
 ("tons",   "На каждый квадратный метр давит около десяти тонн воздуха."),
 ("zero",   "Мы не замечаем, потому что давит одинаково со всех сторон."),
 ("gap1",   "Под кузовом стоят вентиляторы. Они откачивают воздух из зазора, и там давление падает."),
 ("gap2",   "Снизу давление прежнее, и оно прижимает машину. Маск говорит: до двух джи."),
 ("nofuel", "Теперь полёт. Ракетного топлива здесь нет."),
 ("tanks",  "В машине два баллона: шестьсот литров сжатого воздуха, это около двухсот пятидесяти килограммов. И десять с+опел."),
 ("flip",   "Воздух вылетает в одну сторону, машину толкает в другую."),
 ("sat",    "Так же поворачивают космические аппараты."),
 ("end",    "Выпуск обещают в две тысячи двадцать восьмом году. Сел бы в такую? Пиши в комментариях. И отправь тому, кто любит машины."),
]

_SYN = None
def tts(text):
    f = f"{TMP}/t_{hashlib.md5((text+str(VOICE)).encode()).hexdigest()}.wav"
    if os.path.exists(f): return wavfile.read(f)[1].astype(np.float32) / 32768
    global _SYN
    if _SYN is None:
        from vosk_tts import Model, Synth
        _SYN = Synth(Model(model_name="vosk-model-tts-ru-0.9-multi"))
    parts = [p for p in re.split(r"(?<=[.:!?])\s+", text) if p.strip()]; segs = []
    for k, p in enumerate(parts):
        a = np.asarray(_SYN.synth_audio(p, speaker_id=VOICE["speaker"], speech_rate=VOICE["rate"]), np.float32) / 32768
        segs.append(ss.resample_poly(a, SR, 22050).astype(np.float32))
        if k < len(parts) - 1: segs.append(np.zeros(int(SR * .5), np.float32))
    a = np.concatenate(segs); wavfile.write(f, SR, (a * 32767).astype(np.int16)); return a

def timeline():
    t0 = 0.0; sc = []
    for name, text in SCRIPT:
        a = tts(text); dur = LEAD + len(a) / SR + TAIL
        subs = [(t0 + LEAD + c0, t0 + LEAD + c1, ct) for c0, c1, ct in sync(text.replace("+", ""), a, SR)]
        nf = int(round(dur * FPS)); sc.append(dict(name=name, a=a, t0=t0, dur=nf / FPS, subs=subs, nf=nf)); t0 += nf / FPS
    return sc, t0

from scenes_x import *
Y0, Y1 = 250, 1400
from PIL import ImageFilter

# ---------- кадр ----------
_BG = None
def background():
    global _BG
    if _BG is None:
        y = np.linspace(0, 1, H)[:, None, None]; base = np.array(BG, np.float32)[None, None, :]
        img = np.broadcast_to(base * (1 + .8 * y), (H, W, 3)).copy()
        _BG = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return _BG.copy()

def frame(i, SC, DUR):
    t = i / FPS; sc = next(s for s in SC if s["t0"] <= t < s["t0"] + s["dur"] + 1e-6) if t < DUR else SC[-1]
    lt = t - sc["t0"]
    img = background()
    lay = Image.new("RGBA", (W * K, (Y1 + 120) * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    SCENES[sc["name"]](d, lt, sc["dur"])
    lay = lay.resize((W, Y1 + 120), Image.LANCZOS)
    from PIL import ImageChops
    rgb = Image.new("RGB", lay.size, (0, 0, 0)); rgb.paste(lay, (0, 0), lay)
    glow = rgb.filter(ImageFilter.GaussianBlur(14))
    img.paste(lay, (0, 0), lay)
    reg = img.crop((0, 0) + lay.size); reg = ImageChops.screen(reg, glow.point(lambda v: int(v * .8))); img.paste(reg, (0, 0))
    d = ImageDraw.Draw(img)
    # шапка: HUD
    d.text((54, 70), "ФИЗИКА · ПРЕЗЕНТАЦИЯ 15.10.2026", font=F(22, "Medium"), fill=(110, 140, 170))
    d.rectangle([54, 130, W - 54, 134], fill=(20, 40, 64)); d.rectangle([54, 130, 54 + (W - 108) * min(1, t / DUR), 134], fill=CY)
    # субтитры (мягкие, пословные фразы)
    cur = next((s for s in sc["subs"] if s[0] <= t <= s[1]), None)
    if cur:
        f = F(46, "Bold"); words = cur[2]; ws = words.split(); lines = [words]
        if d.textlength(words, font=f) > W - 120:
            k = len(ws) // 2; lines = [" ".join(ws[:k]), " ".join(ws[k:])]
        for li, ln in enumerate(lines):
            x = (W - d.textlength(ln, font=f)) / 2; yy = 1480 + li * 62
            d.text((x + 3, yy + 3), ln, font=f, fill=(0, 0, 0)); d.text((x, yy), ln, font=f, fill=WHITE)
    return img

def _job(args): i, SC, DUR = args; return i, frame(i, SC, DUR)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/expl/out.mp4"; prev = sys.argv[2] if len(sys.argv) > 2 else ""
    SC, DUR = timeline(); NF = int(round(DUR * FPS)); print("длина", round(DUR, 1), "с, кадров", NF, [round(s["dur"], 1) for s in SC], flush=True)
    if prev:
        for t in prev.split(","): frame(int(float(t) * FPS), SC, DUR).save(f"{TMP}/pv_{t}.png"); print("pv", t)
        sys.exit()
    # звук
    track = np.zeros(int(DUR * SR) + SR, np.float32)
    for s in SC: i0 = int((s["t0"] + LEAD) * SR); track[i0:i0 + len(s["a"])] += s["a"]
    track = track / max(np.abs(track).max(), 1e-6) * .85
    mp = os.path.join(HERE, "..", "music", "suk_meditation.mp3")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", "4", "-t", str(DUR + 1), "-i", mp, "-ar", str(SR), "-ac", "1", f"{TMP}/_m.wav"], check=True)
    m = wavfile.read(f"{TMP}/_m.wav")[1].astype(np.float32) / 32768; m = np.pad(m, (0, max(0, len(track) - len(m))))[:len(track)]
    fade = np.minimum(1, np.minimum(np.arange(len(track)) / (SR * 1.5), (len(track) - np.arange(len(track))) / (SR * 2.5)))
    track = track + m / max(np.abs(m).max(), 1e-6) * .2 * fade
    wavfile.write(f"{TMP}/_a.wav", SR, (np.clip(track / np.abs(track).max(), -1, 1) * .9 * 32767).astype(np.int16))
    # кадры
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{TMP}/_a.wav",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for n, (i, im) in enumerate(pool.imap(_job, [(i, SC, DUR) for i in range(NF)], chunksize=4)):
            p.stdin.write(im.convert("RGB").tobytes())
            if n % 120 == 0: print("кадр", n, "/", NF, flush=True)
    p.stdin.close(); p.wait(); print("готово", out)
