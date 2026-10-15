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
model.speaking_rate = 1.0
model.noise_scale = 0.45            # меньше «дребезга» в голосе (по умолчанию 0.667)
model.noise_scale_duration = 0.6    # ровнее ритм речи
TRIES = 4
from transformers import pipeline
import scipy.signal as ss, difflib
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small")
CYR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюяўқғҳ", ["a","b","v","g","d","e","yo","j","z","i","y","k","l","m","n","o","p","r","s","t","u","f","x","ts","ch","sh","sh","","i","","e","yu","ya","o","q","g","h"]))
def lat(t): return "".join(CYR.get(c, c) for c in t.lower())
def norm(t): return "".join(c for c in lat(t) if c.isalpha())
def score(wav, text):
    a = ss.resample_poly(wav, 16000, SR) if SR != 16000 else wav
    hyp = asr({"raw": a.astype(np.float32), "sampling_rate": 16000}, generate_kwargs={"language": "uz", "task": "transcribe"})["text"]
    return difflib.SequenceMatcher(None, norm(hyp), norm(text)).ratio()
SR = model.config.sampling_rate
LEAD = 0.25  # голос начинается чуть позже смены слайда

parts = []
for i, (a, b, text) in enumerate(LINES):
    best = None
    for seed in range(TRIES):
        torch.manual_seed(seed)
        with torch.no_grad():
            cand = model(**tok(text, return_tensors="pt")).waveform[0].numpy()
        if len(cand) / SR > (b - a - LEAD - 0.15) * 1.3: continue
        sc = score(cand, text)
        if best is None or sc > best[0]: best = (sc, seed, cand)
    if best is None: sys.exit(f"строка {i}: ни один вариант не влез в слот")
    sc, seed, wav = best
    print(f"{i}: лучший вариант seed={seed}, совпадение с текстом {sc:.0%}")
    raw = f"voice/raw_{i}.wav"
    wavfile.write(raw, SR, (wav / np.abs(wav).max() * 0.9 * 32767).astype(np.int16))
    dur, slot = len(wav) / SR, b - a - LEAD - 0.15
    tempo = max(1.0, dur / slot)
    if tempo > 1.35:
        sys.exit(f"строка {i} слишком длинная: {dur:.1f} с при слоте {slot:.1f} с")
    out = f"voice/v_{i}.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", raw, "-af", f"aresample=44100,atempo={tempo:.3f},highpass=f=90,"
                    "equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1.2:g=3,equalizer=f=6500:t=q:w=2:g=-2,"
                    "deesser=i=0.4,acompressor=threshold=-22dB:ratio=3:attack=4:release=90:makeup=3,"
                    "aecho=0.85:0.5:28|47:0.12|0.08,"
                    f"adelay={int((a + LEAD) * 1000)}:all=1", "-ar", "44100", "-ac", "2", out], check=True)
    parts.append(out)
    print(f"{i}: {dur:.2f} с, слот {slot:.2f} с, темп ×{tempo:.2f}")

# голос поверх музыки: музыка приглушается, пока звучит голос (sidechain), всё нормализуется под Instagram
inputs = sum((["-i", p] for p in parts), [])
n = len(parts)
fc = (f"{''.join(f'[{k + 1}:a]' for k in range(n))}amix=inputs={n}:normalize=0,highpass=f=70,"
      f"alimiter=limit=0.9,volume=1.4[v];"
      f"[v]asplit[vk][vm];[0:a]volume=0.35,lowpass=f=9000[m];[m][vk]sidechaincompress=threshold=0.02:ratio=12:attack=15:release=500[md];"
      f"[md][vm]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", VIDEO_IN, *inputs, "-filter_complex", fc,
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "60", "-movflags", "+faststart", VIDEO_OUT], check=True)
print("done", VIDEO_OUT)
