"""Общие настройки «голоса №2» (Vosk диктор 4 + студийная обработка) и оформления — импортируются конфигами."""
SPEAKER = "eugene"
VOSK = dict(speaker=4, rate=1.0, dot=380, stress=True)
SENTENCES = True
VOICE_FX = ("highpass=f=70,equalizer=f=160:t=q:w=1:g=2.5,equalizer=f=320:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.5:g=2,"
            "deesser=i=0.3,acompressor=threshold=0.08:ratio=3:attack=8:release=180:makeup=2,aecho=0.8:0.5:28|46:0.18|0.12")
SUB_STYLE, SUB_FONT, QUOTE_SIZE, SUB_CHARS = "karaoke", "Bold", 64, 30
LEAD0, FADE_IN, GAP, TAIL = 0.05, 0.12, 0.38, 0.7
TEXT_DY, BOT_ALPHA = 120, 236
