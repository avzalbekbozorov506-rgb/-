"""Озвучка «Создай машину времени»: Vosk диктор 4, rate 0.88, паузы 560 мс между предложениями, студийная обработка _voice3. Пишет work/ai_time_1/v_NN.wav и durations.json.
Запуск: python3 cartoon/ai_time_voice.py [--check]"""
import os, re, sys, json, subprocess
import numpy as np, scipy.signal as ss
from scipy.io import wavfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT); WK = "work/ai_time_1"; os.makedirs(WK, exist_ok=True); SR = 44100
sys.path.insert(0, "configs")
PH = ["Создай машину времени.", "Нейросеть не спорит. Она проверяет физику.", "Назад — способа никто не нашёл.", "Вперёд — всё проверено.",
      "В тысяча девятьсот семьдесят первом атомные часы облетели Землю на обычных самолётах. И вернулись с другим временем.",
      "Сергей Крикал+ёв провёл на орбите восемьсот три дня. И улетел в будущее примерно на две сотых доли секунды.",
      "Спутники навигации делают это каждые сутки. Их часы уходят вперёд на тридцать восемь миллионных долей секунды. Без поправки навигатор ошибался бы на километры.",
      "Нейросеть делает вывод.", "Готово. Машина времени уже работает.", "Она едет вперёд. Одна секунда за секунду.", "Пассажир — ты. Остановки нет.",
      "Вернуться нельзя. Зато можно успеть.", "Отправь тому, кто мечтает вернуться в прошлое. Подпишись."]
if __name__ == "__main__":
    from vosk_tts import Model, Synth
    from _voice3 import VOICE_FX
    S = Synth(Model(model_name="vosk-model-tts-ru-0.9-multi")); dur = {}
    for i, ph in enumerate(PH, 1):
        if len(sys.argv) > 2 and str(i) not in sys.argv[2:]: continue
        parts = [p for p in re.split(r"(?<=[.:!?])\s+", ph) if p.strip()]; out = []
        for k, p in enumerate(parts):
            a = ss.resample_poly(np.asarray(S.synth_audio(p, speaker_id=4, speech_rate=0.88), np.float32) / 32768.0, SR, 22050).astype(np.float32); out.append(a)
            if k < len(parts) - 1: out.append(np.zeros(int(SR * 0.56), np.float32))
        a = np.concatenate(out); raw = f"{WK}/_r.wav"; wavfile.write(raw, SR, (a * 32767).astype(np.int16)); fn = f"{WK}/v_{i:02d}.wav"
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", raw, "-af", VOICE_FX, fn], check=True)
        dur[i] = len(a) / SR; print(i, round(dur[i], 2), flush=True)
    old = json.load(open(f"{WK}/durations.json")) if os.path.exists(f"{WK}/durations.json") else {}; old.update({str(k): v for k, v in dur.items()}); json.dump(old, open(f"{WK}/durations.json", "w"))
