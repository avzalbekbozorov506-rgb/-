"""Генерирует configs/mach_NN.py для серии «Макиавелли · часть 3–22» из series_mach.py (тексты) и series_art.py (картины).
Голос: python3 make_series.py vosk | xtts"""
import sys
from PIL import Image
from series_mach import SERIES
from series_art import ART
VOICE = sys.argv[1] if len(sys.argv) > 1 else "vosk"
V = {"vosk": 'VOSK = dict(speaker=4, rate=1.0, dot=340)   # «студийный» голос Vosk TTS (диктор 4)',
     "xtts": 'XTTS = dict(speaker="Damien Black", tries=6)   # живой голос XTTS-v2, каждое предложение проверено Whisper (xtts_prepare.py)'}[VOICE]
CAM = {(3, "s5"): (1.25, 1.4, (0.5, 0.8), (0.5, 0.74)), (5, "s2"): (1.3, 1.42, (0.6, 0.62), (0.62, 0.55))}   # ручная камера для картин, где главное не в центре
def fn(f): return f"met_{f}" if isinstance(f, int) else f
for s in SERIES:
    n, art = s["n"], ART[s["n"]]; lines = []
    for k, (say, label, key) in enumerate(s["scenes"]):
        f, cap = art[key]; name = fn(f); w, h = Image.open(f"art/{name}.jpg").size
        last = k == len(s["scenes"]) - 1
        if (n, key) in CAM: cam = CAM[(n, key)]
        elif w / h > 1.0: cam = (1.0, 1.15, (0.5, 0.36), (0.5, 0.36))
        elif key == "hook" and last: cam = (1.3, 1.42, (0.45, 0.3), (0.45, 0.28))
        elif key == "hook": cam = (1.08, 1.22, (0.45, 0.34), (0.45, 0.29))
        else: cam = (1.05, 1.2, (0.5, 0.42), (0.5, 0.36))
        lines.append(f"    ({say!r},\n     \"SUB\", {label!r}, {name!r}, {cap!r}, {cam!r}),")
    open(f"configs/mach_{n:02d}.py", "w").write(f'''"""Макиавелли · часть {n}: {s["sub"]}. Сценарий и источники — series_mach.py, картины (The Met, CC0) — series_art.py."""
HEAD = ("МАКИАВЕЛЛИ", "ЧАСТЬ {n}")
TITLE = ("", "", "")
HOOK = ({s["hook"]!r}, 3.0)
HOOK_Y = 900
SPEAKER = "eugene"
{V}
SENTENCES = True   # предложение озвучивается целиком — живая интонация
SUB_STYLE, SUB_FONT, QUOTE_SIZE, SUB_CHARS = "karaoke", "Bold", 64, 30
LEAD0, FADE_IN, GAP, TAIL = 0.05, 0.12, 0.35, 0.75
TEXT_DY, BOT_ALPHA = 120, 236
DRUM = {n in (6, 7, 12, 16, 19)}
SCENES = [
{chr(10).join(lines)}
]
''')
print("ok", len(SERIES))
