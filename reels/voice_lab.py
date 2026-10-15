"""Лаборатория голоса: один текст — несколько вариантов озвучки (чистая обработка, без эха) + проверка Whisper + микс с музыкой.
Использование: python3 voice_lab.py            → work/voicelab/{A,B,C}.wav и проверка"""
import os, re, subprocess, sys, numpy as np, scipy.io.wavfile as wf, scipy.signal as ss
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/work/voicelab"; os.makedirs(OUT, exist_ok=True)
SR = 48000
TEXT = ["Император Рима начал главную книгу своей жизни совсем не с мудрости.", "Он начал её с благодарности.",
        "Первая книга «Размышлений» — список людей, которым он благодарен.", "От деда он взял добрый нрав.",
        "От матери он взял щедрость и чистые мысли.", "Кого бы ты хотел поблагодарить?", "Отправь это ему сейчас."]
def save(name, a, sr):
    a = np.asarray(a, np.float32); a = ss.resample_poly(a, SR, sr).astype(np.float32) if sr != SR else a
    wf.write(f"{OUT}/{name}.wav", SR, (a / max(np.abs(a).max(), 1e-6) * 0.9 * 32767).astype(np.int16))
def pause(sec): return np.zeros(int(SR * sec), np.float32)
which = sys.argv[1:] or ["A", "B", "C"]
if "A" in which or "C" in which:
    from vosk_tts import Model, Synth
    syn = Synth(Model(model_name="vosk-model-tts-ru-0.9-multi"))
    def vk(t, rate, spk=4): return ss.resample_poly(np.asarray(syn.synth_audio(re.sub(r"[«»]", "", t), speaker_id=spk, speech_rate=rate), np.float32) / 32768, SR, 22050).astype(np.float32)
if "A" in which:      # Vosk диктор 4, как сейчас, но ровные паузы и без эха
    out = []
    for t in TEXT: out += [vk(t, 0.95), pause(0.38)]
    save("A", np.concatenate(out), SR)
if "C" in which:      # Vosk, спокойнее, паузы по знакам препинания (после вопроса и в конце мысли — длиннее)
    out = []
    for t in TEXT:
        out += [vk(t, 0.9), pause(0.62 if t.endswith("?") else 0.5)]
    save("C", np.concatenate(out), SR)
if "B" in which:      # Silero v5 (48 кГц), диктор eugene
    import torch
    m = torch.package.PackageImporter(f"{HERE}/v5_ru.pt").load_pickle("tts_models", "model"); m.to("cpu")
    out = []
    for t in TEXT:
        out += [m.apply_tts(text=t, speaker="eugene", sample_rate=SR, put_accent=True, put_yo=True).numpy().astype(np.float32), pause(0.45)]
    save("B", np.concatenate(out), SR)
print("готово", which)
