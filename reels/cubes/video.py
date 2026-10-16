"""Сборка ролика «Клод, а что было бы тысячу лет назад?»: озвучка по ролям → кадры 3D-сцен → плашка/субтитры → музыка → mp4.
python3 video.py [выход.mp4] [сцены через запятую, напр. room1,egypt]"""
import sys, os, re, io, hashlib, subprocess, numpy as np
from multiprocessing import Pool
from scipy.io import wavfile
import scipy.signal as ss
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cuberender as R, importlib
MODNAME = os.environ.get('SCENES', 'scenes'); S = importlib.import_module(MODNAME)

OUT = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/claude_1000_years.mp4"
ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
TMP = "/tmp/claude-0/c1000" if MODNAME == "scenes" else f"/tmp/claude-0/{MODNAME}"; os.makedirs(TMP, exist_ok=True)
W, H, FPS, SR = 1080, 1920, 24, 48000
PLATE = getattr(S, "PLATE", "Я ПРОСТО СПРОСИЛ,\nЧТО БЫЛО БЫ 1000 ЛЕТ НАЗАД")
GAP, LEAD, TAIL = .36, .30, .55
MUSIC = (f"{HERE}/../music/goldberg_aria.mp3", 2.0)

# ---------- озвучка ----------
_SYN = None
def tts_line(who, text):
    if who == "_t": return np.zeros(int(float(text) * SR), np.float32)          # молчаливая пауза (таймер), text = секунды
    if text.startswith("@audio:"):                                              # готовое аудио пользователя «как есть» (без обработки голоса)
        src, _, lim = text[7:].partition("|"); wv = f"{TMP}/aud_{hashlib.md5(text.encode()).hexdigest()}.wav"       # "|T" — обрезать тишину в конце до T секунд
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", src] + (["-t", lim] if lim else []) + ["-ar", str(SR), "-ac", "1", wv], check=True)
        return wavfile.read(wv)[1].astype(np.float32) / 32768
    key = hashlib.md5(f"{who}|{text}|{S.LINE[who]}".encode()).hexdigest(); f = f"{TMP}/tts_{key}.wav"
    if os.path.exists(f): return wavfile.read(f)[1].astype(np.float32) / 32768
    global _SYN
    if _SYN is None:
        from vosk_tts import Model, Synth
        _SYN = Synth(Model(model_name="vosk-model-tts-ru-0.9-multi"))
    v = S.LINE[who]; parts = [p for p in re.split(r"(?<=[.:!?…])\s+", text) if p.strip()]; segs = []
    for k, p in enumerate(parts):
        a = np.asarray(_SYN.synth_audio(p.replace("…", ".").replace("«", "").replace("»", ""), speaker_id=v["speaker"], speech_rate=v["rate"]), np.float32) / 32768
        segs.append(ss.resample_poly(a, SR, 22050).astype(np.float32))
        if k < len(parts) - 1: segs.append(np.zeros(int(SR * .5), np.float32))
    a = np.concatenate(segs)
    if v["pitch"] != 1.0:
        wavfile.write(f"{TMP}/_p.wav", SR, (a * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{TMP}/_p.wav", "-af",
                        f"asetrate={int(SR * v['pitch'])},aresample={SR},atempo={1 / v['pitch']:.4f}", f"{TMP}/_q.wav"], check=True)
        a = wavfile.read(f"{TMP}/_q.wav")[1].astype(np.float32) / 32768
    wavfile.write(f, SR, (a * 32767).astype(np.int16)); return a

SC = [s for s in S.SCENES if not ONLY or s["name"] in ONLY]
t0 = 0.0
for sc in SC:
    cur = LEAD; sc["tl"] = []
    for ln in sc["lines"]:
        who, text = ln[0], ln[1]; a = tts_line(who, ln[2] if len(ln) > 2 else text); sc["tl"].append((who, text, cur, len(a) / SR, a)); cur += len(a) / SR + GAP
    from subs_sync import sync as _sync
    sc["subs"] = [[(st + c0, st + c1, ct) for c0, c1, ct in (sc["lines"][k][3] if len(sc["lines"][k]) > 3 else _sync(text.replace("+", ""), a, SR))] if who != "_t" else []
                  for k, (who, text, st, d, a) in enumerate(sc["tl"])]
    sc["dur"] = cur - GAP + TAIL; sc["t0"] = t0; sc["nf"] = int(round(sc["dur"] * FPS)); t0 += sc["nf"] / FPS
DUR = t0; NF_ALL = sum(s["nf"] for s in SC)
print("длина ролика", round(DUR, 1), "с, кадров", NF_ALL, flush=True)

track = np.zeros(int(DUR * SR) + SR, np.float32)
for sc in SC:
    for who, text, st, d, a in sc["tl"]: i0 = int((sc["t0"] + st) * SR); track[i0:i0 + len(a)] += a
track = track / max(np.abs(track).max(), 1e-6) * .85
# музыка: тихо под голосом, плавно входит и уходит
try:
    if getattr(S, "NO_MUSIC", False): raise RuntimeError("NO_MUSIC")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(MUSIC[1]), "-t", str(DUR + 1), "-i", MUSIC[0], "-ar", str(SR), "-ac", "1", f"{TMP}/_m.wav"], check=True)
    m = wavfile.read(f"{TMP}/_m.wav")[1].astype(np.float32) / 32768; m = np.pad(m, (0, max(0, len(track) - len(m))))[:len(track)]
    fade = np.minimum(1, np.minimum(np.arange(len(track)) / (SR * 1.5), (len(track) - np.arange(len(track))) / (SR * 2.5)))
    track = track + m / max(np.abs(m).max(), 1e-6) * .20 * fade
except Exception as e: print("музыка не добавлена:", e)
wavfile.write(f"{TMP}/_voice.wav", SR, (np.clip(track / max(np.abs(track).max(), 1e-6), -1, 1) * .9 * 32767).astype(np.int16))

# ---------- состояния персонажей ----------
def q(v, lv): return min(lv, key=lambda x: abs(x - v))
def envelope(sc, who):
    n = sc["nf"]; env = np.zeros(n); hop = SR // FPS
    for w, text, st, d, a in sc["tl"]:
        if w != who: continue
        for i in range(int(d * FPS) + 1):
            seg = a[i * hop:(i + 1) * hop]
            if len(seg) and 0 <= int(st * FPS) + i < n: env[int(st * FPS) + i] = np.sqrt((seg ** 2).mean())
    if sc.get("gate", {}).get(who):
        m = np.zeros(n, bool)
        for g0, g1 in sc["gate"][who]: m[int(g0 * FPS):int(g1 * FPS) + 1] = True
        env = env * m
    ref = np.percentile(env[env > 0], 90) if (env > 0).any() else 1
    return np.clip(env / ref, 0, 1) ** .8
def blink(f, off):
    ph = (f / FPS + off) % 3.1
    return max(0.0, 1 - abs(ph - .1) / .1) if ph < .2 else 0.0
WHOS = list(S.LINE.keys()) + ["onfim"]
PHASE = {w: i * .7 for i, w in enumerate(WHOS)}

def state_key(sc, f, env):
    t = f / FPS; tk = []; bl = []
    for w in WHOS:
        tk.append(q(float(env[w][f]), (0, .35, .7, 1.0)) if w in env else 0); bl.append(q(blink(f, PHASE[w]), (0, .5, 1)))
    br = round(.004 * np.sin(t * 2.6), 3)
    arm_roman = .9 if any(w in ("roman", "legion") and st - .2 <= t <= st + d + .3 for w, _, st, d, _ in sc["tl"]) else 0.0
    onf = q(.5 + .3 * np.sin(t * 5), (.2, .5, .8)) if sc["name"] == "onfim" else 0
    boy_arm = .0; book = 0
    if sc["name"] == "room2":
        l1 = sc["tl"][0]; boy_arm = .8 if t < l1[2] + l1[3] + .2 else .0; book = 1 if t >= l1[2] + l1[3] + .15 else 0
    return (tuple(tk), tuple(bl), br, arm_roman, onf, boy_arm, book)
def key_to_st(key):
    tk, bl, br, ar, onf, ba, book = key
    st = dict(talk=dict(zip(WHOS, tk)), blink=dict(zip(WHOS, bl)), bob={}, arm={"roman": ar, "legion": ar, "jellinek": ar, "adman": ar, "worker": ar, "onfim": onf, "boy": ba}, book=book)
    st["bob"] = {w: br * (1 if i % 2 == 0 else -1) + .012 * tk[i] for i, w in enumerate(WHOS)}
    return st

SHOT = None; CUR = None
def render_state(args):
    i, key = args
    im = SHOT.render(CUR["dyn"](key_to_st(key)))
    Image.fromarray(im).save(f"{TMP}/{CUR['name']}_{i}.jpg", quality=96, subsampling=0)
    return i

# ---------- оформление ----------
def font(sz, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)
def plate_layer(tag):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if not PLATE.strip():                                              # без верхней плашки (PLATE = ""): только жёлтая метка места
        if tag:
            fc = font(40, "ExtraBold"); tw = d.textlength(tag, font=fc); cw, ch = int(tw + 70), 80
            chip = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); cd = ImageDraw.Draw(chip)
            cd.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=(255, 214, 80, 245)); cd.text((35, 16), tag, font=fc, fill=(30, 24, 20, 255))
            ov.alpha_composite(chip, ((W - cw) // 2, 230))
        return ov
    lines = PLATE.split("\n"); sz = 58
    while sz > 36 and max(d.textlength(l, font=font(sz)) for l in lines) > 860: sz -= 2
    ft = font(sz); ws = [d.textlength(l, font=ft) for l in lines]
    bw, bh = int(max(ws) + 90), 70 * len(lines) + 50
    pl = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((0, 0, bw - 1, bh - 1), 28, fill=(18, 18, 20, 235))
    for i, l in enumerate(lines): pd.text(((bw - ws[i]) / 2, 22 + 70 * i), l, font=ft, fill=(255, 255, 255, 255))
    pl = pl.rotate(1.5, resample=Image.BICUBIC, expand=True); ov.alpha_composite(pl, ((W - pl.width) // 2, 215))
    if tag:
        fc = font(40, "ExtraBold"); tw = d.textlength(tag, font=fc); cw, ch = int(tw + 70), 80
        chip = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); cd = ImageDraw.Draw(chip)
        cd.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=(255, 214, 80, 245)); cd.text((35, 16), tag, font=fc, fill=(30, 24, 20, 255))
        ov.alpha_composite(chip, ((W - cw) // 2, 205 + bh + 48))
    return ov
_SUBS = {}
def sub_layer(text, cta=False):
    k = (text, cta)
    if k in _SUBS: return _SUBS[k]
    if not os.environ.get("SUBS_OLD"):                                  # мягкие субтитры (по умолчанию); SUBS_OLD=1 — прежние жирные
        from subs_soft import soft_sub_layer
        _SUBS[k] = soft_sub_layer(text, cta, W, H); return _SUBS[k]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); fs = font(60, "ExtraBold"); rows, cur = [], ""
    for w_ in text.split():
        if d.textlength((cur + " " + w_).strip(), font=fs) > 900: rows.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    rows.append(cur); y = 1500 - (82 if cta and len(rows) > 2 else 0)
    for r in rows:
        x = (W - d.textlength(r, font=fs)) / 2
        d.text((x, y), r, font=fs, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(20, 20, 24, 255)); y += 82
    if cta:
        fc = font(46, "Black"); t = "ПОДПИШИСЬ  ·  @MYSLI.VEKOV"; tw = d.textlength(t, font=fc)
        d.rounded_rectangle(((W - tw) / 2 - 40, 1700, (W + tw) / 2 + 40, 1790), 45, fill=(255, 214, 80, 250)); d.text(((W - tw) / 2, 1716), t, font=fc, fill=(30, 24, 20, 255))
    _SUBS[k] = ov; return ov

if __name__ == "__main__":
    ENV = {}
    for sc in SC:
        names = []
        env = {w: envelope(sc, w) for w in {x[0] for x in sc["tl"]}}
        sc["keys"] = [state_key(sc, f, env) for f in range(sc["nf"])]
        uniq = sorted(set(sc["keys"])); sc["uniq"] = {k: i for i, k in enumerate(uniq)}
        print(sc["name"], "кадров", sc["nf"], "уникальных", len(uniq), flush=True)
        kf = f"{TMP}/{sc['name']}_keys.txt"; sig = repr(uniq)
        if sc["name"] in os.environ.get("TRUST", "").split(",") and all(os.path.exists(f"{TMP}/{sc['name']}_{i}.jpg") for i in range(len(uniq))): print(sc["name"], "оставлена", flush=True); continue
        if os.path.exists(kf) and open(kf).read() == sig and all(os.path.exists(f"{TMP}/{sc['name']}_{i}.jpg") for i in range(len(uniq))): print(sc["name"], "без изменений", flush=True); continue
        CUR = sc; SHOT = R.Shot(sc["static"](), sc["camera"](), lights=sc["lights"](), region=sc["region"], dof=sc["dof"])
        with Pool(4) as pool: list(pool.imap(render_state, [(i, k) for k, i in sc["uniq"].items()], chunksize=1))
        open(kf, "w").write(sig); print(sc["name"], "готово", flush=True)
    ff = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", f"{TMP}/_voice.wav", "-af", "loudnorm=I=-14:TP=-1:LRA=9", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", OUT], stdin=subprocess.PIPE)
    for sc in SC:
        base = plate_layer(sc["tag"]); last = len(sc["tl"]) - 1
        for f in range(sc["nf"]):
            im = Image.open(f"{TMP}/{sc['name']}_{sc['uniq'][sc['keys'][f]]}.jpg").convert("RGB")
            z = 1 + .04 * f / sc["nf"]; im = im.resize((int(W * z), int(H * z)), Image.LANCZOS)
            x0, y0 = (im.width - W) // 2, (im.height - H) // 2
            fr = im.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA"); fr.alpha_composite(base)
            t = f / FPS
            for j, (who, text, st, d, a) in enumerate(sc["tl"]):
                for c0, c1, ct in sc["subs"][j]:
                    if c0 - .03 <= t < c1:
                        fr.alpha_composite(sub_layer(ct, cta=((sc["name"] == "room2" or sc.get("final")) and j == last))); break
            if hasattr(S, "overlay"): S.overlay(sc, t, fr)
            ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait(); print("готово", OUT)
