"""Поиск фото на Wikimedia Commons только с лицензией CC0 / общественное достояние. python3 art_tools/wm_search.py "запрос" [сколько]"""
import json, sys, urllib.request, urllib.parse, time
UA = {"User-Agent": "mysli-vekov/1.0 (avzalbekbozorov506@users.noreply)"}
def get(u):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except Exception as e: time.sleep(15 * (i + 1)); err = e
    raise err
q, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "size|extmetadata", "format": "json"})
for p in json.loads(get(u)).get("query", {}).get("pages", {}).values():
    ii = p["imageinfo"][0]; lic = ii["extmetadata"].get("LicenseShortName", {}).get("value", "")
    if ("CC0" in lic or "Public domain" in lic or lic.startswith("PD")) and min(ii["width"], ii["height"]) >= 1200:
        print(p["title"], ii["width"], ii["height"], "|", lic)
