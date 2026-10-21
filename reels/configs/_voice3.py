"""Голос А «тёплый» (утверждён пользователем 21.10.2026). Прежнее описание: голос недели Берна (21.10.2026, просьба пользователя: студийный, мягкий, выразительный): Vosk диктор 4, темп 0.88, паузы длиннее,
после вопроса пауза в 1,5 раза длиннее; мягкая студийная обработка (тепло снизу, срезаны «гул» и резкость, лёгкая комната)."""
from _voice2 import *
VOSK = dict(speaker=4, rate=0.86, dot=600, qmul=1.5, stress=True)
VOICE_FX = "highpass=f=70,equalizer=f=110:t=q:w=1:g=3.5,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3000:t=q:w=1.5:g=-1.5,equalizer=f=6500:t=h:w=1:g=-4,lowpass=f=9500,deesser=i=0.4,acompressor=threshold=0.08:ratio=3:attack=20:release=300:makeup=3,aecho=0.85:0.85:30|55:0.06|0.03,alimiter=limit=0.9"
