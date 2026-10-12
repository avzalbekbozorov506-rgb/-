"""Узбекская озвучка для reel_migrantlar_uz_60s.mp4 (Meta MMS-TTS, офлайн) и сведение с музыкой."""
import subprocess, sys
import numpy as np, scipy.io.wavfile as wavfile, torch
from transformers import VitsModel, AutoTokenizer

VIDEO_IN, VIDEO_OUT = sys.argv[1], sys.argv[2]
# (начало слайда, конец слайда, текст) — кириллицей: модель обучена на узбекской кириллице, цифры — словами
LINES = [
    (0, 3, "Россияга ишга келяпсизми?"),
    (3, 6, "Мигрантлар учун бешта муҳим қоида."),
    (6, 15, "Биринчи қоида. Рўйхатдан ўтиш. Келгандан кейин етти иш куни ичида. Муддат ўтса, жарима."),
    (15, 24, "Иккинчи қоида. Тиббий кўрик. Келгандан кейин ўттиз кун ичида. Бармоқ изи ва сурат топширилади."),
    (24, 33, "Учинчи қоида. Патент. Ҳужжатларни ўттиз кун ичида топширинг. Патент фақат берилган вилоятда амал қилади."),
    (33, 42, "Тўртинчи қоида. Патент тўлови. Ҳар ой ўз вақтида тўланг. Бир кун кечикса ҳам, патент бекор бўлади."),
    (42, 51, "Бешинчи қоида. Москвада Амина иловаси мажбурий. Геолокация доим ёниқ бўлсин."),
    (51, 56, "Фирибгарлардан эҳтиёт бўлинг! Фақат расмий марказга боринг."),
    (56, 60, "Сақлаб қўйинг ва дўстларингизга юборинг!"),
]
MODEL = "facebook/mms-tts-uzb-script_cyrillic"
tok, model = AutoTokenizer.from_pretrained(MODEL), VitsModel.from_pretrained(MODEL)
torch.manual_seed(7)
model.speaking_rate = 1.08
SR = model.config.sampling_rate
LEAD = 0.25  # голос начинается чуть позже смены слайда

parts = []
for i, (a, b, text) in enumerate(LINES):
    with torch.no_grad():
        wav = model(**tok(text, return_tensors="pt")).waveform[0].numpy()
    raw = f"voice/raw_{i}.wav"
    wavfile.write(raw, SR, (wav / np.abs(wav).max() * 0.9 * 32767).astype(np.int16))
    dur, slot = len(wav) / SR, b - a - LEAD - 0.15
    tempo = max(1.0, dur / slot)
    if tempo > 1.35:
        sys.exit(f"строка {i} слишком длинная: {dur:.1f} с при слоте {slot:.1f} с")
    out = f"voice/v_{i}.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", f"atempo={tempo:.3f},adelay={int((a + LEAD) * 1000)}:all=1", "-ar", "44100", "-ac", "2", out], check=True)
    parts.append(out)
    print(f"{i}: {dur:.2f} с, слот {slot:.2f} с, темп ×{tempo:.2f}")

# голос поверх музыки: музыка приглушается, пока звучит голос (sidechain), всё нормализуется под Instagram
inputs = sum((["-i", p] for p in parts), [])
n = len(parts)
fc = (f"{''.join(f'[{k + 1}:a]' for k in range(n))}amix=inputs={n}:normalize=0,highpass=f=70,"
      f"acompressor=threshold=-20dB:ratio=3:attack=5:release=120,volume=1.6[v];"
      f"[v]asplit[vk][vm];[0:a]volume=0.55[m];[m][vk]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
      f"[md][vm]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", VIDEO_IN, *inputs, "-filter_complex", fc,
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "60", "-movflags", "+faststart", VIDEO_OUT], check=True)
print("done", VIDEO_OUT)
