#!/usr/bin/env bash
# Готовит новую облачную сессию к сборке Reels: Python-пакеты, голосовая модель Silero v5, Whisper для проверки озвучки.
# Запуск: bash reels/setup.sh   (из корня репозитория; повторный запуск безопасен)
set -e
cd "$(dirname "$0")"
pip install -q --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
pip install -q --break-system-packages scipy numpy pillow transformers
[ -s v5_ru.pt ] || curl -sSL -o v5_ru.pt https://models.silero.ai/models/tts/ru/v5_ru.pt
pip install -q --break-system-packages vosk-tts
bash ./fetch_music.sh >/dev/null 2>&1 || echo "музыка не скачалась — повторите: bash reels/fetch_music.sh"
command -v ffmpeg >/dev/null || { echo "Нужен ffmpeg"; exit 1; }
python3 -c "import torch, scipy, transformers, PIL; print('setup ok, torch', torch.__version__)"
