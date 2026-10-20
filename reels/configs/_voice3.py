"""Голос недели Берна (21.10.2026, просьба пользователя: студийный, мягкий, выразительный): Vosk диктор 4, темп 0.88, паузы длиннее,
после вопроса пауза в 1,5 раза длиннее; мягкая студийная обработка (тепло снизу, срезаны «гул» и резкость, лёгкая комната)."""
from _voice2 import *
VOSK = dict(speaker=4, rate=0.88, dot=560, qmul=1.5, stress=True)
VOICE_FX = "highpass=f=70,equalizer=f=120:t=q:w=1:g=2.5,equalizer=f=280:t=q:w=1.2:g=-2,equalizer=f=2800:t=q:w=1.5:g=-1,equalizer=f=7000:t=h:w=1:g=-3,deesser=i=0.35,acompressor=threshold=0.09:ratio=3:attack=15:release=250:makeup=2,aecho=0.85:0.8:22|44:0.07|0.04,alimiter=limit=0.9"
