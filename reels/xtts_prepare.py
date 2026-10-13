"""Готовит озвучку XTTS для конфига: собирает предложения (как движок в режиме SENTENCES) и запускает xtts_batch.py
в окружении /opt/xtts (синтез + проверка Whisper + повтор). Использование: python3 xtts_prepare.py configs/<имя>.py [...]"""
import importlib.util, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for c in sys.argv[1:]:
    spec = importlib.util.spec_from_file_location("cfg", c); cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
    src = open(f"{HERE}/cinema_engine.py").read(); ns = {}
    exec(src[src.index("def sentences("):src.index("_VOSK = None")], ns)
    lines = [" ".join(g) for sc in cfg.SCENES for g in ns["sentences"](sc[0])]
    lst = f"{HERE}/work/tts/_{os.path.basename(c)}.txt"; os.makedirs(f"{HERE}/work/tts", exist_ok=True)
    open(lst, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt", REQUESTS_CA_BUNDLE="/root/.ccr/ca-bundle.crt")
    subprocess.run(["/opt/xtts/bin/python", f"{HERE}/xtts_batch.py", cfg.XTTS["speaker"], lst, str(cfg.XTTS.get("tries", 6))], env=env, check=True)
