"""Проверка озвучки: синтезирует каждую фразу конфига, распознаёт её Whisper и показывает расхождения с текстом.
Использование: python3 check_voice.py configs/<имя>.py"""
import importlib.util, os, re, sys, difflib
import numpy as np, scipy.signal as ss, torch
from transformers import pipeline
spec = importlib.util.spec_from_file_location("cfg", sys.argv[1]); cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
m = torch.package.PackageImporter(os.environ.get("SILERO_MODEL", "v5_ru.pt")).load_pickle("tts_models", "model")
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small")
def norm(t): return re.sub(r"[^а-яё ]", " ", t.lower().replace("+", "").replace("ё", "е")).split()
bad = 0
for sc in cfg.SCENES:
    spk0 = sc[6] if len(sc) > 6 and sc[6] else getattr(cfg, "SPEAKER", "aidar")
    for ph in [p.strip() for p in sc[0].split("|") if p.strip()]:
        spk = spk0
        if ph.startswith("@"): spk, ph = ph[1:].split(":", 1); ph = ph.strip()
        a = m.apply_tts(text=ph, speaker=spk, sample_rate=48000, put_accent=True, put_yo=True).numpy()
        hyp = asr({"raw": ss.resample_poly(a, 1, 3).astype(np.float32), "sampling_rate": 16000}, generate_kwargs={"language": "ru"})["text"].strip()
        r = difflib.SequenceMatcher(None, norm(ph), norm(hyp)).ratio(); flag = "  " if r >= 0.85 else "!!"; bad += r < 0.85
        print(f"{flag} {r:.2f} [{spk}] {ph}  =>  {hyp}")
print(f"итого подозрительных фраз: {bad}")
