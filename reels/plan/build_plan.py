"""Собирает reels/plan/index.html из plan30_data.py (контент-план на 30 дней со сценариями)."""
import json, pathlib
here = pathlib.Path(__file__).parent
ns = {}; exec((here / "plan30_data.py").read_text(), ns)
data = json.dumps(ns["DAYS"], ensure_ascii=False)
html = (here / "page_template.html").read_text().replace("/*__DATA__*/[]", data)
(here / "index.html").write_text(html)
print("ok", len(html))
