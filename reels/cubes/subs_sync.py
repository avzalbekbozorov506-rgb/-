"""Синхронизация субтитров с озвучкой: границы предложений берутся из реальных пауз в аудио (синтезатор ставит 0,5 с между предложениями),
внутри предложения фразы-субтитры делятся по числу слогов (гласных) — время каждого слова пропорционально слогам, как в речи диктора."""
import re
import numpy as np

VOW = set("аеёиоуыэюяaeiouyАЕЁИОУЫЭЮЯ")
def _w(word):
    v = sum(ch in VOW for ch in word) or 1
    return v + (.9 if word[-1:] in ",:;—–-" else 0) + (.4 if re.search(r"\d", word) else 0)

def split_sentences(text): return [s for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s]

def split_chunks(sentence, soft=22, hard=44):
    words = sentence.split(); chunks, cur = [], []
    for i, w in enumerate(words):
        trial = " ".join(cur + [w])
        if cur and len(trial) > hard: chunks.append(cur); cur = []
        cur.append(w)
        if len(" ".join(cur)) >= soft and w[-1:] in ",:;—–?!" and i < len(words) - 1: chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    if len(chunks) > 1 and len(chunks[-1]) == 1 and len(" ".join(chunks[-2] + chunks[-1])) <= hard: chunks[-2] += chunks.pop()
    return chunks

def voiced_sections(a, SR, gap=.36):
    hop = SR // 100; n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1)); thr = max(.003, .03 * np.percentile(rms, 95))
    v = rms > thr; secs = []; i = 0
    while i < n:
        if v[i]:
            j = i; last = i
            while j < n and (j - last) * .01 < gap:
                if v[j]: last = j
                j += 1
            secs.append((i * .01, (last + 1) * .01)); i = last + 1
        else: i += 1
    return secs

def sync(text, a, SR, tail=.3):
    """-> [(t0, t1, текст)] относительно начала реплики."""
    sents = split_sentences(text); secs = voiced_sections(a, SR); dur = len(a) / SR
    if not secs: secs = [(0, dur)]
    sw = [sum(_w(w) for w in s.split()) for s in sents]
    if len(secs) == len(sents): rngs = secs
    else:                                                    # запасной вариант: делим весь голос по весу предложений
        s0, s1 = secs[0][0], secs[-1][1]; tot = sum(sw) + 2.2 * (len(sents) - 1); cur = s0; rngs = []
        for k, w in enumerate(sw):
            span = (s1 - s0) * w / tot; rngs.append((cur, cur + span)); cur += span + (s1 - s0) * 2.2 / tot
    out = []
    for s, (a0, a1) in zip(sents, rngs):
        chs = split_chunks(s); ws = [sum(_w(w) for w in c) for c in chs]; tot = sum(ws); cur = a0
        for c, w in zip(chs, ws):
            span = (a1 - a0) * w / tot; out.append([cur, cur + span, " ".join(c)]); cur += span
        out[-1][1] = a1 + .12                                 # конец предложения
    for i in range(len(out) - 1):                             # внутри предложения удерживаем фразу до начала следующей
        if out[i + 1][0] - out[i][1] < .3: out[i][1] = out[i + 1][0]
    out[-1][1] = min(dur, out[-1][1]) + tail
    return [tuple(x) for x in out]
