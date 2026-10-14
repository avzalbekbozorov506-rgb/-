"""Пересведение звука готового рендера без повторного рендера видео: берёт work/<имя>/{video.mp4,voice.wav,music.wav} и собирает <имя>.mp4 по схеме движка.
Использование: python3 remix.py <имя>   (затем python3 finalize.py <имя>)"""
import importlib.util, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); N = sys.argv[1]; W = f"work/{N}"
spec = importlib.util.spec_from_file_location("cfg", f"configs/{N}.py"); cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{W}/video.mp4"], capture_output=True, text=True).stdout)
vfx = getattr(cfg, "VOICE_FX", "highpass=f=80,equalizer=f=3500:t=q:w=1.5:g=1.5,deesser=i=0.2")
mus = ("[2:a]volume=1[m];[m][vk]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=700[md];" if getattr(cfg, "MUSIC", None)
       else "[2:a]volume=0.14[m];[m][vk]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=600[md];")
fc = f"[1:a]{vfx},asplit[v][vk];" + mus + "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]"
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{W}/video.mp4", "-i", f"{W}/voice.wav", "-i", f"{W}/music.wav", "-filter_complex", fc,
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.2f}", "-movflags", "+faststart", f"{N}.mp4"], check=True)
print("пересведено", N, f"{dur:.1f} с")
