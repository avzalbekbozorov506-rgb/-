"""Финальная обработка ролика: громкость −14 LUFS (лимитер + подбор усиления, true peak ≤ −1 dB), облегчённая копия с тем же звуком,
HQ-копия ≈28,5 МиБ для чата (двухпроходный x264). Использование: python3 finalize.py <имя> [--cover файл.jpg | --no-cover]   (работает с <имя>.mp4 в папке reels)
Обложка вшивается в HQ первыми 3 кадрами (~0,1 с): Instagram берёт первый кадр как обложку, если её не задать (ShapelessAI, vidIQ).
По умолчанию берётся covers/*<имя>*click.jpg, затем covers/*<имя>*.jpg; если обложки нет — HQ без неё."""
import glob, json, os, re, subprocess, sys
N = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); W = f"work/{N}"; os.makedirs(W, exist_ok=True); os.makedirs("hq", exist_ok=True)
def run(*a): return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *a], capture_output=True, text=True)
def loud(f):
    e = run("-i", f, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
src = f"{W}/_src.mp4"
if not os.path.exists(src) or os.path.getmtime(f"{N}.mp4") > os.path.getmtime(src): os.replace(f"{N}.mp4", src)   # свежий рендер всегда становится исходником                 # исходник рендера сохраняем, чтобы можно было перезапустить
i0, _ = loud(src); g = -14.0 - i0                                       # усиление к −14 LUFS, пики режет лимитер (−2 dB), 3 подхода
for _ in range(4):
    run("-y", "-i", src, "-af", f"aresample=192000,volume={g:.2f}dB,alimiter=limit=0.79:attack=2:release=60:level=false:asc=1,aresample=48000",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{N}.mp4")
    i, p = loud(f"{N}.mp4")
    if abs(i + 14.0) <= 0.4: break
    g += -14.0 - i
i, p = loud(f"{N}.mp4"); print(f"громкость {i} LUFS, пик {p} dB")
if os.path.exists(f"{N}_light.mp4"):
    run("-y", "-i", f"{N}_light.mp4", "-i", f"{N}.mp4", "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", f"{W}/_l.mp4"); os.replace(f"{W}/_l.mp4", f"{N}_light.mp4")
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{N}.mp4"], capture_output=True, text=True).stdout)
cv = None if "--no-cover" in sys.argv else sys.argv[sys.argv.index("--cover") + 1] if "--cover" in sys.argv else \
    next(iter(sorted(glob.glob(f"covers/*{N}*click.jpg")) + sorted(glob.glob(f"covers/*{N}*.jpg"))), None)
inp, flt = ["-i", f"{N}.mp4"], []
if cv:                                                                   # обложка = первые 3 кадра, звук сдвигается на столько же
    vw, vh, fr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "csv=p=0",
                                 f"{N}.mp4"], capture_output=True, text=True).stdout.strip().split(",")[:3]
    a_, b_ = map(int, fr.split("/")); cd = 3 * b_ / a_; d += cd
    inp += ["-loop", "1", "-framerate", fr, "-t", f"{cd + 0.5:.3f}", "-i", cv]
    flt = ["-filter_complex", f"[1:v]scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
           f"trim=end_frame=3,setpts=PTS-STARTPTS[c];[0:v]setsar=1,format=yuv420p[m];[c][m]concat=n=2:v=1:a=0[v];"
           f"[0:a]adelay={round(cd * 1000)}:all=1[a]", "-map", "[v]", "-map", "[a]"]
    print(f"обложка {cv} вшита первыми 3 кадрами")
k = int(28.5 * 8 * 1024 * 1024 / 1000 / d - 192)
for ps in (1, 2):
    a = ["-y", *inp, *flt, "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-b:v", f"{k}k", "-pass", str(ps), "-passlogfile", f"{W}/x264", "-pix_fmt", "yuv420p"]
    run(*(a + (["-an", "-f", "mp4", "/dev/null"] if ps == 1 else ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"hq/{N}_hq.mp4"])))
print(f"длительность {d:.1f} c, HQ {os.path.getsize(f'hq/{N}_hq.mp4') / 1048576:.1f} МиБ")
