"""Скачивает файл Wikimedia Commons, печатает автора/лицензию, пишет credits. Ширина превью — стандартная 1280 (нестандартные размеры Wikimedia режет 429).
Если API отвечает 429 — превью напрямую: upload.wikimedia.org/wikipedia/commons/thumb/<md5[0]>/<md5[:2]>/<файл>/960px-<файл>."""
import json, sys, urllib.request, urllib.parse, io
from PIL import Image
UA = {"User-Agent": "mysli-vekov/1.0 (avzalbekbozorov506@users.noreply)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
title, name = sys.argv[1], sys.argv[2]
q = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1280, "format": "json"})
p = next(iter(json.loads(get(q))["query"]["pages"].values())); ii = p["imageinfo"][0]; md = ii["extmetadata"]
lic = md.get("LicenseShortName", {}).get("value", ""); art = md.get("Artist", {}).get("value", ""); date = md.get("DateTimeOriginal", {}).get("value", "")
print(title, ii["width"], ii["height"], "|", lic, "|", art[:80], "|", date[:40])
assert "Public domain" in lic or "PD" in lic or "CC0" in lic, "не public domain"
im = Image.open(io.BytesIO(get(ii.get("thumburl") or ii["url"]))).convert("RGB")
s = min(1, 2600 / min(im.size)); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS) if s < 1 else im
im.save(f"art/{name}.jpg", quality=92); print("saved", name, im.size)
cr = json.load(open("art/credits.json")); cr[name] = sys.argv[3] + " (Wikimedia Commons, public domain)"; json.dump(cr, open("art/credits.json", "w"), ensure_ascii=False, indent=1)
