#!/usr/bin/env bash
# Скачивает фоновую музыку (общественное достояние, Musopen, archive.org) в reels/music/. Повторный запуск безопасен.
cd "$(dirname "$0")"; mkdir -p music; cd music
B="https://archive.org/download/musopen-dvd/Musopen-DVD.zip/Musopen%20DVD"
dl(){ [ -s "$1" ] || curl -sSL -m 300 --retry 2 -o "$1" "$B/$2"; }
dl goldberg_aria.mp3 "Goldberg%20Variations/Goldberg%20Variations%2C%20BWV%20988%20-%20Aria.mp3"
dl borodin_nocturne.mp3 "String%20Quartets/Borodin%20String%20Quartet%20No%202/String%20Quartet%20No.%202%20in%20D%20Major%20-%20III.%20Nocturne%20Andante.mp3"
dl grieg_aase.mp3 "Grieg%20-%20Peer%20Gynt/Peer%20Gynt%20Suite%20No.%201%2C%20Op.%2046%20-%20II.%20Aase%27s%20Death.mp3"
dl schubert_d959_andantino.mp3 "Schubert%20-%20The%20Piano%20Sonatas/Sonata%20in%20A%20Minor%2C%20D.%20959%20-%20II.%20Andantino.mp3"
dl beethoven_adagio.mp3 "String%20Quartets/Beethoven%20String%20Quartet%20in%20B%20flat%20Major%20Op%2018/String%20Quartet%20No.%206%20in%20B%20Flat%20Major%2C%20Op.%2018%2C%20No.%206%20-%20II.%20Adagio%20ma%20non%20troppo.mp3"
dl haydn_adagio.mp3 "String%20Quartets/Haydn%20Quartet%20in%20D%20Major%20Op.64/String%20Quartet%20In%20D%2C%20Op.%20645%2C%20H%20363%2C%20Lark%20-%20II.%20Adagio%2C%20Cantabile.mp3"
dl suk_meditation.mp3 "String%20Quartets/Suk%20-Meditation/Meditation.mp3"
# CC0 1.0 (проверено 21.10.2026 по метаданным archive.org): Бах, Гольдберг-вариации, Ария — Kimiko Ishizaka, The Open Goldberg Variations. Основная музыка недели «Весы».
[ -s ogv_aria.mp3 ] || curl -sSL -m 300 --retry 2 -o ogv_aria.mp3 "https://archive.org/download/The_Open_Goldberg_Variations-11823/Kimiko_Ishizaka_-_01_-_Aria.mp3"
ls -la
