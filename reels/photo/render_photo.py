"""Ролик из готовых картинок: озвучка (explainer/build.py, EXPL=scenes_two), движение камеры (Ken Burns), подписи по слову, музыка.
Запуск: EXPL=scenes_two python3 reels/photo/render_photo.py reels/hq/two_shifts_photo_hq.mp4 [превью-секунды]"""
import os, sys, re, math, subprocess, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "explainer"))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile
from multiprocessing import Pool
import build
M = importlib.import_module(os.environ.get("EXPL", "scenes_two"))
W, H, FPS = 1080, 1920, 24
IMG = {}
CHUNKS = []
def load(n):
    if n not in IMG: IMG[n] = Image.open(os.path.join(HERE, "img_two_shifts", f"{n:02d}.jpg")).convert("RGB")
    return IMG[n]
def F(sz, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", sz)
VOW = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
def plan():
    SC, DUR = build.timeline(); segs = []
    for s in SC:
        shots = M.SHOTS[s["name"]]; n = len(shots); d = s["dur"] / n
        for k, (img, a, b) in enumerate(shots): segs.append(dict(img=img, a=a, b=b, t0=s["t0"] + k * d, t1=s["t0"] + (k + 1) * d, name=s["name"], first=(k == 0)))
    words = []
    for s in SC:
        for (c0, c1, txt) in s["subs"]:
            ws = txt.split(); wt = [max(1, sum(ch in VOW for ch in w)) for w in ws]; tot = sum(wt); acc = 0
            for w, x in zip(ws, wt): words.append((c0 + (c1 - c0) * acc / tot, c0 + (c1 - c0) * (acc + x) / tot, w)); acc += x
    return SC, DUR, segs, words
def kb(seg, t):
    im = load(seg["img"]); sw, sh = im.size; u = (t - seg["t0"]) / max(1e-6, seg["t1"] - seg["t0"]); u = max(0, min(1, u)); e = u * u * (3 - 2 * u)
    z = 1.0 + .10 * e; ch = sh / z; cw = ch * W / H
    if cw > sw: cw = sw; ch = cw * H / W
    cx = cw / 2 + (sw - cw) * (seg["a"] + (seg["b"] - seg["a"]) * e); cy = ch / 2 + (sh - ch) * .5
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return im.resize((W, H), Image.LANCZOS, box=box)
def frame(i, segs, words, DUR):
    t = i / FPS; seg = next((s for s in segs if s["t0"] <= t < s["t1"]), segs[-1]); fr = kb(seg, t)
    k = seg["t1"] - t; kin = t - seg["t0"]
    if kin < .35 and seg is not segs[0]:                                    # плавный переход из предыдущей
        prev = segs[segs.index(seg) - 1]; fr = Image.blend(kb(prev, t), fr, kin / .35)
    a = np.asarray(fr, np.float32); yy, xx = np.mgrid[0:H, 0:W]; v = 1 - .35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.0
    a = a * v[..., None] + np.random.RandomState(i).randn(H, W, 1) * 3; fr = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(fr, "RGBA")
    d.text((W - 54, 96), "@mysli.vekov", font=F(26, "SemiBold"), fill=(255, 255, 255, 150), anchor="ra")
    ph = next((c for c in CHUNKS if c[0] <= t < c[1] + .1), None)
    if ph:
        c0, c1, txt = ph; al = max(0, min(1, (t - c0) / .22, (c1 + .1 - t) / .18))
        f = F(52, "Bold"); ws = txt.split(); lines = [[]]
        for w_ in ws:
            tr = " ".join(lines[-1] + [w_])
            if lines[-1] and d.textlength(tr, font=f) > 900: lines.append([w_])
            else: lines[-1].append(w_)
        lh = 72; y0 = 1580 - (len(lines) - 1) * lh // 2 + int((1 - al) * 18)
        wmax = max(d.textlength(" ".join(l), font=f) for l in lines)
        d.rounded_rectangle(((W - wmax) / 2 - 40, y0 - 24, (W + wmax) / 2 + 40, y0 + len(lines) * lh - 4), 36, fill=(10, 6, 4, int(150 * al)))
        for li, l in enumerate(lines):
            x = (W - d.textlength(" ".join(l), font=f)) / 2
            for w_ in l:
                key = re.sub(r"[^\w]", "", w_).lower() in M.KEY
                col = (255, 196, 90, int(255 * al)) if key else (255, 255, 255, int(255 * al))
                d.text((x, y0 + li * lh), w_, font=f, fill=col); x += d.textlength(w_ + " ", font=f)
    chip = M.CHIPS.get(seg["name"])
    if chip and kin > .2:
        ca = int(255 * min(1, (kin - .2) / .3)); ft = F(34, "Bold"); tw_ = d.textlength(chip, font=ft)
        d.rounded_rectangle((54, 150, 54 + tw_ + 50, 214), 32, fill=(10, 6, 4, int(180 * ca / 255)), outline=(255, 196, 90, ca), width=2)
        d.text((79, 160), chip, font=ft, fill=(255, 210, 130, ca))
    if t < 2.2: 
        al = int(255 * min(1, t / .3) * min(1, (2.2 - t) / .4)); d.rounded_rectangle((300, 200, 780, 290), 45, fill=(255, 184, 48, al))
        d.text((540, 245), "▶ ПОДПИШИСЬ", font=F(46, "Black"), fill=(26, 16, 0, al), anchor="mm")
    return fr
def job(args):
    i, segs, words, DUR = args; return i, frame(i, segs, words, DUR)
if __name__ == "__main__":
    out = sys.argv[1]; prev = sys.argv[2] if len(sys.argv) > 2 else ""
    SC, DUR, segs, words = plan(); CHUNKS.extend(c for s_ in SC for c in s_["subs"]); NF = int(round(DUR * FPS)); print("длина", round(DUR, 1), "с")
    if prev:
        ts = [float(x) for x in prev.split(",")]; ims = [frame(int(t * FPS), segs, words, DUR).resize((360, 640)) for t in ts]
        sh = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): sh.paste(im, (k * 360, 0))
        sh.save("/tmp/photo_prev.png"); sys.exit()
    SR = build.SR; track = np.zeros(int(DUR * SR) + SR, np.float32)
    for s in SC: i0 = int((s["t0"] + build.LEAD) * SR); track[i0:i0 + len(s["a"])] += s["a"]
    track = track / max(np.abs(track).max(), 1e-6) * .85
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", "2", "-t", str(DUR + 1), "-i", os.path.join(HERE, "..", "music", "beethoven_adagio.mp3"), "-ar", str(SR), "-ac", "1", "/tmp/_pm.wav"], check=True)
    m = wavfile.read("/tmp/_pm.wav")[1].astype(np.float32) / 32768; m = np.pad(m, (0, max(0, len(track) - len(m))))[:len(track)]
    fade = np.minimum(1, np.minimum(np.arange(len(track)) / (SR * 1.5), (len(track) - np.arange(len(track))) / (SR * 2.5))); track = track + m / max(np.abs(m).max(), 1e-6) * .22 * fade
    wavfile.write("/tmp/_pv.wav", SR, (np.clip(track / np.abs(track).max(), -1, 1) * .9 * 32767).astype(np.int16))
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "/tmp/_pv.wav",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for n, (i, im) in enumerate(pool.imap(job, [(i, segs, words, DUR) for i in range(NF)], chunksize=4)):
            p.stdin.write(im.tobytes())
            if n % 120 == 0: print("кадр", n, "/", NF, flush=True)
    p.stdin.close(); p.wait(); print("готово", out)
