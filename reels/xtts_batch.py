"""XTTS-v2 (живой голос) с автопроверкой: каждое предложение синтезируется, Whisper сверяет слова, при расхождении — новая попытка
с другим seed (до N раз), лучший вариант кладётся в кэш work/tts/<md5>.wav (48 кГц). Запуск в окружении /opt/xtts:
/opt/xtts/bin/python xtts_batch.py <speaker> <файл со строками-предложениями> [попыток]"""
import difflib, hashlib, os, re, sys
os.environ["COQUI_TOS_AGREED"] = "1"
import numpy as np, torch, scipy.signal as ss
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = f"{HERE}/work/tts"; os.makedirs(CACHE, exist_ok=True)
spk, src = sys.argv[1], sys.argv[2]; tries = int(sys.argv[3]) if len(sys.argv) > 3 else 5
lines = [l.strip() for l in open(src, encoding="utf-8") if l.strip()]
def key(t): return hashlib.md5(f"xtts|{spk}|{t}".encode()).hexdigest()
todo = [l for l in lines if not os.path.exists(f"{CACHE}/{key(l)}.wav")]
if not todo: print("всё в кэше"); sys.exit()
from TTS.api import TTS
from transformers import pipeline
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small")
NUM = {"0": "ноль"}
NUMW = re.compile(r"^(ноль|один|одна|два|две|три|четыр|пят|шест|сем|восем|девят|десят|двадцат|тридцат|сорок|сто|двест|трист|тысяч|миллион|перв|втор|трет|четв)")
def norm(t, drop_nums=False):
    w = re.sub(r"[^а-яa-z0-9 ]", " ", t.lower().replace("ё", "е")).split()
    return [x for x in w if not (x.isdigit() or (drop_nums and NUMW.match(x)))]
for t in todo:
    say = re.sub(r"[«»“”\"]", "", t.replace("+", ""))
    best = None
    for k in range(tries):
        torch.manual_seed(1000 + k)
        a = np.asarray(tts.tts(text=say, speaker=spk, language="ru"), np.float32)
        hyp = asr({"raw": ss.resample_poly(a, 16000, 24000).astype(np.float32), "sampling_rate": 16000}, generate_kwargs={"language": "ru"})["text"]
        h = norm(hyp); r = norm(say, drop_nums=any(c.isdigit() for c in hyp))         # числа: Whisper пишет цифрами — сравниваем без них
        score = difflib.SequenceMatcher(None, r, h).ratio() - 0.15 * max(0, len(h) - len(r))
        if best is None or score > best[0]: best = (score, a, hyp)
        if score >= 0.97: break
    score, a, hyp = best
    print(f"{score:.2f} | {say} => {hyp.strip()}", flush=True)
    a = ss.resample_poly(a, 2, 1).astype(np.float32)                    # 24 → 48 кГц
    wavfile.write(f"{CACHE}/{key(t)}.wav", 48000, (a / max(np.abs(a).max(), 1e-6) * 0.9 * 32767).astype(np.int16))
