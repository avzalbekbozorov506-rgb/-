"""Финальная обработка ролика: громкость −14 LUFS (лимитер + подбор усиления, true peak ≤ −1 dB), облегчённая копия с тем же звуком,
HQ-копия ≈28,5 МиБ для чата (двухпроходный x264). Использование: python3 finalize.py <имя>   (работает с <имя>.mp4 в папке reels)"""
import json, os, re, subprocess, sys
N = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); W = f"work/{N}"; os.makedirs(W, exist_ok=True); os.makedirs("hq", exist_ok=True)
def run(*a): return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *a], capture_output=True, text=True)
def loud(f):
    e = run("-i", f, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
src = f"{W}/_src.mp4"
if not os.path.exists(src): os.replace(f"{N}.mp4", src)                 # исходник рендера сохраняем, чтобы можно было перезапустить
best = None
for lim, gain in ((0.5, 5.0), (0.4, 6.6), (0.35, 7.6), (0.3, 9.2), (0.25, 10.8), (0.2, 12.8), (0.16, 14.8)):
    out = f"{W}/_ln.mp4"
    run("-y", "-i", src, "-af", f"aresample=192000,alimiter=limit={lim}:attack=3:release=80:level=false:asc=1,volume={gain}dB,aresample=48000",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out)
    i, p = loud(out); best = (lim, gain, i, p)
    if i >= -14.6: break
lim, gain, i, p = best; adj = min(-14.0 - i, -1.0 - p)                 # к −14 LUFS, но пик не выше −1 dB
run("-y", "-i", src, "-af", f"aresample=192000,alimiter=limit={lim}:attack=3:release=80:level=false:asc=1,volume={gain + adj:.2f}dB,aresample=48000",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{N}.mp4")
i, p = loud(f"{N}.mp4"); print(f"громкость {i} LUFS, пик {p} dB")
if os.path.exists(f"{N}_light.mp4"):
    run("-y", "-i", f"{N}_light.mp4", "-i", f"{N}.mp4", "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", f"{W}/_l.mp4"); os.replace(f"{W}/_l.mp4", f"{N}_light.mp4")
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{N}.mp4"], capture_output=True, text=True).stdout)
k = int(28.5 * 8 * 1024 * 1024 / 1000 / d - 192)
for ps in (1, 2):
    a = ["-y", "-i", f"{N}.mp4", "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-b:v", f"{k}k", "-pass", str(ps), "-passlogfile", f"{W}/x264", "-pix_fmt", "yuv420p"]
    run(*(a + (["-an", "-f", "mp4", "/dev/null"] if ps == 1 else ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"hq/{N}_hq.mp4"])))
print(f"длительность {d:.1f} c, HQ {os.path.getsize(f'hq/{N}_hq.mp4') / 1048576:.1f} МиБ")
