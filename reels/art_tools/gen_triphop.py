"""Своя музыка для эксперимента (не для плана): медленный эмбиент/трип-хоп — бочка, суб-бас, пэд, арпеджио с эхом.
  python3 art_tools/gen_triphop.py секунд music/gen_triphop.mp3 [секунда_брейка]"""
import sys, subprocess, numpy as np, scipy.signal as ss, scipy.io.wavfile as wf
SR = 44100; DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 90; OUT = sys.argv[2] if len(sys.argv) > 2 else "music/gen_triphop.mp3"
BRK = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
BPM = 84; B = 60 / BPM; N = int(SR * DUR); rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    L[i:j] += sig[:j - i] * g * (1 - max(pan, 0)); R[i:j] += sig[:j - i] * g * (1 + min(pan, 0))
def lp(x, fc, o=2): return ss.lfilter(*ss.butter(o, fc / (SR / 2)), x)
def hp(x, fc, o=2): return ss.lfilter(*ss.butter(o, fc / (SR / 2), "high"), x)
def note(m): return 440 * 2 ** ((m - 69) / 12)
t1 = np.arange(int(SR * 0.6)) / SR
kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-t1 * 28)) / SR) * np.exp(-t1 * 6.5); kick = np.tanh(kick * 2.2) * 0.9
tn = np.arange(int(SR * 0.35)) / SR
snare = hp(lp(rng.normal(0, 1, len(tn)), 5000), 700) * np.exp(-tn * 14) * 0.35 + np.sin(2 * np.pi * 190 * tn) * np.exp(-tn * 30) * 0.2
th = np.arange(int(SR * 0.06)) / SR; hat = hp(rng.normal(0, 1, len(th)), 7000, 4) * np.exp(-th * 70) * 0.12
CH = [[57, 60, 64, 67], [53, 57, 60, 64], [50, 53, 57, 60], [52, 55, 59, 62]]   # Am7 — Fmaj7 — Dm7 — Em7
bar = 4 * B; nb = int(DUR / bar) + 1
for b in range(nb):
    t0 = b * bar; ch = CH[b % 4]
    drums = t0 >= 4 * B * 1 and not (BRK <= t0 < BRK + 2 * bar) and t0 < DUR - bar
    # пэд: 3 расстроенные пилы на ноту, мягкий фильтр, длинная атака
    tt = np.arange(int(SR * bar * 1.1)) / SR; env = np.minimum(1, tt / 1.2) * np.minimum(1, (bar * 1.1 - tt) / 0.6)
    pad = np.zeros(len(tt))
    for m in ch:
        for d in (-0.08, 0.0, 0.07):
            f = note(m + d); pad += (2 * ((tt * f) % 1) - 1)
    pad = lp(pad, 900 + 300 * np.sin(b), 2) * env * 0.035
    add(pad, t0, -0.3); add(pad, t0 + 0.013, 0.3)
    # суб-бас: корень аккорда октавой ниже
    tb = np.arange(int(SR * bar)) / SR; f = note(ch[0] - 24)
    bass = np.tanh(1.6 * np.sin(2 * np.pi * f * tb)) * np.minimum(1, tb / 0.05) * np.exp(-tb * 0.35) * 0.32
    add(bass, t0)
    # арпеджио-«звёзды» с эхом
    for k in range(8):
        m = ch[[0, 2, 1, 3, 2, 1, 3, 0][k]] + 12; tp = np.arange(int(SR * 0.9)) / SR
        pl = np.sin(2 * np.pi * note(m) * tp) * np.exp(-tp * 5) * 0.05
        for e, g in ((0, 1), (B * 0.75, 0.45), (B * 1.5, 0.22)): add(pl, t0 + k * B / 2 + e, 0.5 if k % 2 else -0.5, g)
    if drums:
        for kb in (0, 2.5): add(kick, t0 + kb * B, 0, 1.0)
        for sb in (1, 3): add(snare, t0 + sb * B, 0.1, 1.0)
        for hb in range(8): add(hat, t0 + hb * B / 2 + (0.02 if hb % 2 else 0), 0.35, 0.6 if hb % 2 else 1.0)
# реверберация: шумовой хвост 2.8 с
ir_t = np.arange(int(SR * 2.8)) / SR; ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 2.2); ir = lp(ir, 6000); ir /= np.abs(ir).sum() ** 0.5 * 18
L = L + ss.fftconvolve(L, ir)[:N] * 0.8; R = R + ss.fftconvolve(R, ir[::-1].copy())[:N] * 0.8
fade = np.minimum(1, np.arange(N) / (SR * 2.0)) * np.minimum(1, (N - np.arange(N)) / (SR * 3.0))
st = np.stack([L * fade, R * fade], 1); st = st / np.abs(st).max() * 0.89
wf.write("/tmp/_triphop.wav", SR, (st * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", "/tmp/_triphop.wav", "-b:a", "192k", OUT], check=True); print("saved", OUT, DUR, "c")
