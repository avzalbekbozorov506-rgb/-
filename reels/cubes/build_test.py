"""Тест стиля: сцена 1 «Клод, а что было бы тысячу лет назад?» — комната, диалог мальчика и Клода (~10 с).
python3 build_test.py [выход.mp4]"""
import sys, os, re, subprocess, numpy as np
from multiprocessing import Pool
from scipy.io import wavfile
import scipy.signal as ss
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cuberender as R, scene_room as S

OUT = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/test_scene1.mp4"
W, H, FPS, SR = 1080, 1920, 24, 48000
PLATE = "Я ПРОСТО СПРОСИЛ,\nЧТО БЫЛО БЫ 1000 ЛЕТ НАЗАД"
LINES = [("boy", "Клод, а что было бы, если бы ты появился тысячи лет назад?"),
         ("claude", "Я бы остался без работы. Там уже всё было.")]
SPEAK = {"boy": dict(speaker=2, rate=0.98, pitch=1.14), "claude": dict(speaker=4, rate=0.9, pitch=1.0)}
GAP = 0.45

def tts_lines():
    from vosk_tts import Model, Synth
    syn = Synth(Model(model_name="vosk-model-tts-ru-0.9-multi")); out = []
    for who, text in LINES:
        v = SPEAK[who]; parts = [p for p in re.split(r"(?<=[.:!?])\s+", text) if p.strip()]; segs = []
        for k, p in enumerate(parts):
            a = np.asarray(syn.synth_audio(p, speaker_id=v["speaker"], speech_rate=v["rate"]), np.float32) / 32768
            segs.append(ss.resample_poly(a, SR, 22050).astype(np.float32))
            if k < len(parts) - 1: segs.append(np.zeros(int(SR * .5), np.float32))
        a = np.concatenate(segs)
        if v["pitch"] != 1.0:                                           # выше тон без смены темпа (мальчик)
            wavfile.write("/tmp/claude-0/_p.wav", SR, (a * 32767).astype(np.int16))
            subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", "/tmp/claude-0/_p.wav", "-af",
                            f"asetrate={int(SR * v['pitch'])},aresample={SR},atempo={1 / v['pitch']:.4f}", "/tmp/claude-0/_q.wav"], check=True)
            a = wavfile.read("/tmp/claude-0/_q.wav")[1].astype(np.float32) / 32768
        out.append((who, text, a))
    return out

voices = tts_lines()
t = 0.4; TL = []                                                         # (кто, текст, старт, длина, звук)
for who, text, a in voices:
    TL.append((who, text, t, len(a) / SR, a)); t += len(a) / SR + GAP
DUR = t + .5; NF = int(DUR * FPS)
track = np.zeros(int(DUR * SR) + SR, np.float32)
for who, text, st, d, a in TL: track[int(st * SR):int(st * SR) + len(a)] += a
track = track / np.abs(track).max() * .85
wavfile.write("/tmp/claude-0/_voice.wav", SR, (track * 32767).astype(np.int16))

def envelope(who):                                                       # огибающая речи -> открытие рта на кадр
    env = np.zeros(NF)
    for w, text, st, d, a in TL:
        if w != who: continue
        hop = SR // FPS
        for i in range(int(d * FPS) + 1):
            seg = a[i * hop:(i + 1) * hop]
            if len(seg): env[min(NF - 1, int(st * FPS) + i)] = np.sqrt((seg ** 2).mean())
    ref = np.percentile(env[env > 0], 90) if (env > 0).any() else 1
    return np.clip(env / ref, 0, 1) ** .8

ENV = {w: envelope(w) for w in ("boy", "claude")}
def blink(f, off):                                                       # моргание раз в ~3 с
    ph = (f / FPS + off) % 3.1
    return max(0.0, 1 - abs(ph - .1) / .1) if ph < .2 else 0.0

SHOT = R.Shot(S.build_static(), S.camera(), lights=S.lights(), dof=(3.3, 1.5))

def q(v, lv): return min(lv, key=lambda x: abs(x - v))
def state(f):
    t = f / FPS
    ta = lambda e: q(float(e[f]), (0, .35, .7, 1.0))
    br = .004 * np.sin(t * 2.6)
    return (ta(ENV["boy"]), ta(ENV["claude"]), q(blink(f, .0), (0, .5, 1)), q(blink(f, 1.4), (0, .5, 1)), round(br, 3))

def render_state(key):
    bt, ct, bb, cb, br = key
    return SHOT.render(S.build_dyn(dict(boy_talk=bt, claude_talk=ct, boy_blink=bb, claude_blink=cb, boy_bob=br + .012 * bt, claude_bob=-br + .012 * ct)))

def font(sz, bold="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{bold}.otf", sz)

def overlay(f):
    """Плашка сверху (весь ролик) и субтитры внизу."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    ft = font(58); lines = PLATE.split("\n"); ws = [d.textlength(l, font=ft) for l in lines]
    bw, bh = int(max(ws) + 90), 70 * len(lines) + 50
    pl = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((0, 0, bw - 1, bh - 1), 28, fill=(18, 18, 20, 235))
    for i, l in enumerate(lines): pd.text(((bw - ws[i]) / 2, 22 + 70 * i), l, font=ft, fill=(255, 255, 255, 255))
    pl = pl.rotate(1.5, resample=Image.BICUBIC, expand=True); ov.alpha_composite(pl, ((W - pl.width) // 2, 215))
    sec = f / FPS
    for who, text, st, dd, a in TL:
        if st - .05 <= sec <= st + dd + .35:
            words = text.split(); fs = font(60, "ExtraBold"); rows, cur = [], ""
            for w_ in words:
                if d.textlength((cur + " " + w_).strip(), font=fs) > 900: rows.append(cur); cur = w_
                else: cur = (cur + " " + w_).strip()
            rows.append(cur)
            y = 1500
            for r in rows:
                x = (W - d.textlength(r, font=fs)) / 2
                d.text((x, y), r, font=fs, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(20, 20, 24, 255)); y += 82
    return ov

if __name__ == "__main__":
    print("кадров", NF, "длина", round(DUR, 1), flush=True)
    ff = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", "/tmp/claude-0/_voice.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
    keys = [state(f) for f in range(NF)]; uniq = sorted(set(keys)); print("уникальных кадров", len(uniq), flush=True)
    with Pool(4) as pool:
        cache = dict(zip(uniq, pool.imap(render_state, uniq, chunksize=1)))
    print("кадры посчитаны", flush=True)
    for f in range(NF):
        im = cache[keys[f]]
        z = 1 + .04 * f / NF                                          # мягкий наезд
        pil = Image.fromarray(im).resize((int(W * z), int(H * z)), Image.LANCZOS)
        x0, y0 = (pil.width - W) // 2, (pil.height - H) // 2
        fr = pil.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA"); fr.alpha_composite(overlay(f))
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait(); print("готово", OUT)
