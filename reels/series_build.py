"""Сборка серии: для каждой части — рендер, finalize (громкость, HQ), Whisper по всему ролику, лист кадров. Пропускает готовые."""
import os, subprocess, sys
from PIL import Image
QA = "/tmp/claude-0/-home-user--/7984ad60-5f4e-55ab-ae11-65543a494bda/scratchpad/qa_asr.py"
for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else range(3, 23)):
    name = f"mach_{n:02d}"; W = f"work/{name}"; os.makedirs(W, exist_ok=True)
    if os.path.exists(f"hq/{name}_hq.mp4") and os.path.exists(f"{W}/qa.txt"): continue
    for f in (f"{W}/_src.mp4",):
        if os.path.exists(f): os.remove(f)
    r = subprocess.run(["python3", "cinema_engine.py", f"configs/{name}.py", f"{name}.mp4"], capture_output=True, text=True)
    if r.returncode: print(name, "ОШИБКА рендера", r.stderr[-400:], flush=True); continue
    dur = [l for l in r.stdout.splitlines() if "длительность" in l]
    fin = subprocess.run(["python3", "finalize.py", name], capture_output=True, text=True).stdout.strip().replace("\n", " | ")
    asr = subprocess.run(["python3", QA, f"{name}.mp4"], capture_output=True, text=True).stdout
    open(f"{W}/qa.txt", "w").write(asr)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{name}.mp4"], capture_output=True, text=True).stdout)
    tiles = []
    for k in range(8):
        t = 0.6 + (d - 1.5) * k / 7
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", f"{name}.mp4", "-frames:v", "1", "-vf", "scale=240:-1", f"{W}/q{k}.png"])
        tiles.append(Image.open(f"{W}/q{k}.png"))
    S = Image.new("RGB", (240 * 8, tiles[0].height))
    for k, t in enumerate(tiles): S.paste(t, (k * 240, 0))
    S.save(f"{W}/qa.jpg", quality=80)
    print(name, dur[0] if dur else "", "|", fin, flush=True)
