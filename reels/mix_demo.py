"""Микс-образец: голос (wav) + музыка (файл из music/) по той же схеме, что в движке. python3 mix_demo.py голос.wav музыка.mp3 старт_сек выход.mp3"""
import subprocess, sys
voice, music, start, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
VOICE_FX = "highpass=f=75,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3000:t=q:w=1.5:g=1.5,deesser=i=0.3,acompressor=threshold=0.1:ratio=2.5:attack=10:release=200:makeup=1.5"
MUSIC_FX = "highpass=f=50,equalizer=f=300:t=q:w=0.8:g=-3,equalizer=f=1500:t=q:w=0.9:g=-6,equalizer=f=3500:t=q:w=1:g=-4,lowpass=f=9000,loudnorm=I=-30:TP=-3"
fc = (f"[0:a]{VOICE_FX},asplit[v][vk];[1:a]{MUSIC_FX},afade=t=in:d=2,afade=t=out:st=17:d=4[m];"
      "[m][vk]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=700[md];[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", voice, "-ss", start, "-i", music, "-filter_complex", fc, "-map", "[a]", "-t", "22", "-b:a", "192k", out], check=True)
print("ok", out)
