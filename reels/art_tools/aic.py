"""Art Institute of Chicago (общественное достояние, CC0): поиск и загрузка — запасной источник, когда Wikimedia отвечает 429.
  python3 art_tools/aic.py search "запрос" ...      — id | автор | название | дата | размер (только is_public_domain)
  python3 art_tools/aic.py fetch id имя             — art/<имя>.jpg (≤2600 px по короткой стороне) + credits.json"""
import io, json, sys, urllib.parse, urllib.request
from PIL import Image
UA = {"User-Agent": "mysli-vekov/1.0 (avzalbekbozorov506@users.noreply)", "AIC-User-Agent": "mysli-vekov"}
F = "id,title,artist_display,date_display,image_id,is_public_domain,artwork_type_title,thumbnail"
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
if sys.argv[1] == "search":
    for q in sys.argv[2:]:
        r = json.loads(get("https://api.artic.edu/api/v1/artworks/search?" + urllib.parse.urlencode(
            {"q": q, "limit": 25, "fields": F, "query[term][is_public_domain]": "true"})))
        for a in r["data"]:
            if a.get("image_id"):
                t = a.get("thumbnail") or {}
                print(f'{q[:12]:12} {a["id"]} | {a["artwork_type_title"][:10]} | {a["artist_display"].splitlines()[0][:28]} | {a["title"][:55]} | {a["date_display"]} | {t.get("width")}x{t.get("height")}')
else:
    i, name = sys.argv[2], sys.argv[3]
    a = json.loads(get(f"https://api.artic.edu/api/v1/artworks/{i}?fields={F}"))["data"]
    assert a["is_public_domain"], "не public domain"
    im = Image.open(io.BytesIO(get(f'https://www.artic.edu/iiif/2/{a["image_id"]}/full/1686,/0/default.jpg'))).convert("RGB")
    im.save(f"art/{name}.jpg", quality=93); print("saved", name, im.size)
    cr = json.load(open("art/credits.json"))
    cr[name] = f'{a["artist_display"].splitlines()[0]} — {a["title"]}, {a["date_display"]} (Art Institute of Chicago, CC0)'
    json.dump(cr, open("art/credits.json", "w"), ensure_ascii=False, indent=1)
