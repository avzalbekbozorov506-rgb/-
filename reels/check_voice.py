"""Проверка озвучки: синтезирует каждую фразу конфига ТЕМ ЖЕ способом, что и движок (голос, темп, паузы),
распознаёт её Whisper и печатает, что услышано. Ищите проглоченные окончания и неверные ударения.
Использование: python3 check_voice.py configs/<имя>.py            — все фразы конфига
               printf 'фраза 1\nфраза 2\n' | python3 check_voice.py configs/<имя>.py -   — свои варианты из stdin"""
import sys, numpy as np, scipy.signal as ss
CFG, MODE = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
sys.argv = ["x", CFG, "/tmp/_check_voice.mp4"]
exec(compile(open("cinema_engine.py").read().split("for i, sc in enumerate(SCENES)")[0], "cinema_engine", "exec"))
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small")
phrases = [l for l in sys.stdin.read().split("\n") if l.strip()] if MODE == "-" else ([" ".join(g) for sc in SCENES for g in sentences(sc[0])] if getattr(cfg, "SENTENCES", False) else [p.strip() for sc in SCENES for p in sc[0].split("|") if p.strip()])
for ph in phrases:
    spk = getattr(cfg, "SPEAKER", "aidar")
    if ph.startswith("@"): spk, ph = ph[1:].split(":", 1); ph = ph.strip()
    a = tts(ph, spk)
    hyp = asr({"raw": ss.resample_poly(a, 1, 3).astype(np.float32), "sampling_rate": 16000}, generate_kwargs={"language": "ru"})["text"].strip()
    print(f"{clean(ph)}\n   => {hyp}")
