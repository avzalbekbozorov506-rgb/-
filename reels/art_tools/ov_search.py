"""Поиск фото в Openverse, только CC0 / общественное достояние. Лист-превью: python3 art_tools/ov_search.py "запрос" лист.jpg [сколько]
Скачать: python3 art_tools/ov_search.py --get <id> <имя>   (пишет art/<имя>.jpg и credits.json)"""
import json, sys, urllib.request, urllib.parse, io
from PIL import Image, ImageDraw
UA = {"User-Agent": "mysli-vekov/1.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
API = "https://api.openverse.org/v1/images/"
if sys.argv[1] == "--get":
    o = json.loads(get(API + sys.argv[2] + "/")); im = Image.open(io.BytesIO(get(o["url"]))).convert("RGB")
    im.save(f"art/{sys.argv[3]}.jpg", quality=92); print("saved", sys.argv[3], im.size, o["license"], o.get("creator"))
    cr = json.load(open("art/credits.json")); cr[sys.argv[3]] = f"{o['title']} — {o.get('creator')} ({o['provider']}, {o['license'].upper()}) {o['foreign_landing_url']}"
    json.dump(cr, open("art/credits.json", "w"), ensure_ascii=False, indent=1); sys.exit()
q, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10
r = json.loads(get(API + "?" + urllib.parse.urlencode({"q": q, "license": "cc0,pdm", "aspect_ratio": "tall", "size": "large", "page_size": n, "mature": "false", "source": "stocksnap"})))["results"]
T = 270; sh = Image.new("RGB", (T * 5, (T + 20) * ((len(r) + 4) // 5)), (20, 20, 20)); d = ImageDraw.Draw(sh)
for k, o in enumerate(r):
    try: im = Image.open(io.BytesIO(get(o.get("thumbnail") or o["url"]))).convert("RGB"); im.thumbnail((T, T)); sh.paste(im, ((k % 5) * T, (k // 5) * (T + 20)))
    except Exception as e: pass
    d.text(((k % 5) * T + 4, (k // 5) * (T + 20) + T + 4), o["id"][:8], fill=(255, 255, 0)); print(k, o["id"], o["provider"], o["title"][:50], o.get("width"), o.get("height"))
sh.save(out)
