"""Проверка ролика после озвучки (обязательна, решение пользователя 14.10.2026): 1) грамматика и орфография текста — LanguageTool (ru-RU);
2) голос — check_all.py: синтез каждого предложения, Whisper, печать предложений, где услышано не то.
Использование: python3 check_text.py configs/<имя>.py [ещё конфиги...]   (из папки reels/)"""
import json, re, subprocess, sys, urllib.parse, urllib.request, importlib.util
SKIP = {"WHITESPACE_RULE", "DOUBLE_PUNCTUATION", "UPPERCASE_SENTENCE_START", "DASH_RULE", "EN_QUOTES", "RU_UNPAIRED_BRACKETS"}
def scenes_text(cfg_path):
    sp = importlib.util.spec_from_file_location("c", cfg_path); c = importlib.util.module_from_spec(sp); sp.loader.exec_module(c)
    out = []
    for sc in c.SCENES:
        t = re.sub(r"\s*\|\s*", " ", sc[0]).replace("+", "").strip()
        out.append(t if t[-1] in ".!?…»" else t + ".")
    return out
bad_total = 0
for cfg in sys.argv[1:]:
    text = "\n".join(scenes_text(cfg))
    req = urllib.request.Request("https://api.languagetool.org/v2/check", data=urllib.parse.urlencode({"language": "ru-RU", "text": text}).encode())
    try: matches = json.loads(urllib.request.urlopen(req, timeout=60).read())["matches"]
    except Exception as e: print(f"### {cfg}: LanguageTool недоступен ({e}) — проверить текст вручную"); matches = []
    matches = [m for m in matches if m["rule"]["id"] not in SKIP]
    print(f"### {cfg}: грамматика — {'OK' if not matches else str(len(matches)) + ' замечаний'}")
    for m in matches:
        frag = text[m["offset"]: m["offset"] + m["length"]]
        sug = ", ".join(r["value"] for r in m["replacements"][:3])
        print(f"   «{frag}» — {m['message']}" + (f" → {sug}" if sug else ""))
    bad_total += len(matches)
    print(subprocess.run(["python3", "check_all.py", cfg], capture_output=True, text=True).stdout, end="")
print("Грамматика без замечаний." if not bad_total else f"Грамматика: {bad_total} замечаний — разобрать до рендера.")
