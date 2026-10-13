"""Проверка озвучки нескольких конфигов: печатает только предложения, где Whisper услышал не то (без учёта пунктуации, ё/е и чисел)."""
import re, subprocess, sys, difflib
NUMW = re.compile(r"^(ноль|один|одна|два|две|три|четыр|пят|шест|сем|восем|девят|десят|двадцат|тридцат|сорок|сто|двест|трист|тысяч|перв|втор|трет|четв)")
def norm(t, dn=False):
    w = re.sub(r"[^а-яa-z0-9 ]", " ", t.lower().replace("ё", "е").replace("-", " ")).split()
    return [x for x in w if not (x.isdigit() or (dn and NUMW.match(x)))]
for c in sys.argv[1:]:
    out = subprocess.run(["python3", "check_voice.py", c], capture_output=True, text=True).stdout.splitlines()
    pairs = [(out[i], out[i + 1].replace("   => ", "")) for i in range(0, len(out) - 1) if out[i + 1].startswith("   => ")]
    bad = [(r, h) for r, h in pairs if norm(r.replace("+", ""), any(ch.isdigit() for ch in h)) != norm(h)]
    print(f"### {c}: {len(pairs) - len(bad)}/{len(pairs)} OK", flush=True)
    for r, h in bad: print(f"   {r}\n   => {h}", flush=True)
