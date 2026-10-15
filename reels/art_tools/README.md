# Инструменты подбора картин (запускать из reels/)
- `python3 art_tools/met_search.py "запрос" ...` — картины The Met (только public domain, живопись): id | автор | название.
- `python3 art_tools/met_sheet.py лист.jpg id id ...` — контактный лист превью (смотреть глазами перед выбором).
- `python3 art_tools/met_fetch.py id id ...` — скачать в `art/met_<id>.jpg` (≤2600 px) + credits.json.
- `python3 art_tools/wikimedia_fetch.py "File:Название.jpg" имя "Автор — название, год"` — картина с Wikimedia Commons (только public domain);
  Wikimedia часто отвечает 429 — повторять с паузой 30–60 с, не чаще 1 файла в 20 с.
- `python3 art_tools/aic.py search "запрос"` / `aic.py fetch id имя` — Art Institute of Chicago (CC0), когда Wikimedia отвечает 429. Много античных сюжетов, шпалер, гравюр.
- `python3 art_tools/used_art.py configs/<имя>.py` — **обязательно перед рендером**: картины, уже бывшие в роликах и обложках (просьба пользователя 15.10 — не повторять). Без аргумента — список всех.
