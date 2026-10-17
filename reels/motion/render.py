"""Моушен-рендер: озвучка из explainer/build.py (EXPL=scenes_scam), кадры — Chromium (stage.html), сборка — ffmpeg.
Запуск: EXPL=scenes_scam python3 reels/motion/render.py reels/hq/<имя>_hq.mp4 [превью-секунды через запятую]"""
import os, sys, json, subprocess, shutil
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "explainer")); sys.argv_backup = sys.argv[:]
import numpy as np
from scipy.io import wavfile
import build
FPS = 24; CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"; TMPF = "/tmp/motion_frames"
def setup():
    SC, DUR = build.timeline()
    subs = [[a, b, t] for s in SC for (a, b, t) in s["subs"]]
    return SC, DUR, dict(dur=DUR, scenes=[dict(name=s["name"], t0=s["t0"], dur=s["dur"]) for s in SC], subs=subs)
def worker(args):
    ids, tl = args
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.add_init_script("window.TL=" + json.dumps(tl)); pg.goto("file://" + os.path.join(HERE, "stage.html")); pg.wait_for_timeout(400)
        for i in ids:
            pg.evaluate(f"seek({i / FPS})"); pg.screenshot(path=f"{TMPF}/f_{i:05d}.jpg", type="jpeg", quality=93); out.append(i)
        b.close()
    return len(out)
if __name__ == "__main__":
    out = sys.argv[1]; prev = sys.argv[2] if len(sys.argv) > 2 else ""
    SC, DUR, tl = setup(); NF = int(round(DUR * FPS)); shutil.rmtree(TMPF, ignore_errors=True); os.makedirs(TMPF)
    if prev:
        ids = [int(float(t) * FPS) for t in prev.split(",")]; worker((ids, tl))
        from PIL import Image
        ims = [Image.open(f"{TMPF}/f_{i:05d}.jpg").resize((360, 640)) for i in ids]; sh = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): sh.paste(im, (k * 360, 0))
        sh.save("/tmp/motion_prev.png"); print("превью /tmp/motion_prev.png", [(s["name"], round(s["t0"], 1)) for s in SC]); sys.exit()
    # звук
    SR = build.SR; track = np.zeros(int(DUR * SR) + SR, np.float32)
    for s in SC: i0 = int((s["t0"] + build.LEAD) * SR); track[i0:i0 + len(s["a"])] += s["a"]
    track = track / max(np.abs(track).max(), 1e-6) * .85
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", "4", "-t", str(DUR + 1), "-i", os.path.join(HERE, "..", "music", "suk_meditation.mp3"), "-ar", str(SR), "-ac", "1", "/tmp/_mm.wav"], check=True)
    m = wavfile.read("/tmp/_mm.wav")[1].astype(np.float32) / 32768; m = np.pad(m, (0, max(0, len(track) - len(m))))[:len(track)]
    fade = np.minimum(1, np.minimum(np.arange(len(track)) / (SR * 1.5), (len(track) - np.arange(len(track))) / (SR * 2.5))); track = track + m / max(np.abs(m).max(), 1e-6) * .2 * fade
    wavfile.write("/tmp/_mv.wav", SR, (np.clip(track / np.abs(track).max(), -1, 1) * .9 * 32767).astype(np.int16))
    N = 4; chunks = [list(range(k, NF, N)) for k in range(N)]
    with Pool(N) as pool: print("кадров", sum(pool.map(worker, [(c, tl) for c in chunks])), flush=True)
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", f"{TMPF}/f_%05d.jpg", "-i", "/tmp/_mv.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("готово", out)
