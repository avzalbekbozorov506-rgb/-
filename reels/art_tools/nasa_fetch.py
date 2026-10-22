"""NASA Image and Video Library (images.nasa.gov): поиск и загрузка. Материалы NASA — общественное достояние (не использовать логотип NASA как
одобрение). Запуск: python3 art_tools/nasa_fetch.py search "запрос" [N]  |  python3 art_tools/nasa_fetch.py get NASA_ID имя  -> art/nasa_<имя>.jpg"""
import sys, json, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def jget(u): return json.load(urllib.request.urlopen(u, timeout=60))
def search(q, n=20):
    d = jget("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "image"}))
    out = []
    for x in d["collection"]["items"][:n]:
        m = x["data"][0]; th = next((l["href"] for l in x.get("links", []) if l.get("rel") == "preview"), None)
        out.append((m["nasa_id"], m.get("title", ""), m.get("center", ""), th))
    return out
def get(nid, name):
    files = jget(f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nid)}")["collection"]["items"]
    hrefs = [f["href"] for f in files if f["href"].lower().endswith((".jpg", ".jpeg", ".png", ".tif"))]
    best = next((h for h in hrefs if "~orig" in h), None) or next((h for h in hrefs if "~large" in h), hrefs[0])
    dst = f"{HERE}/art/nasa_{name}.jpg"; urllib.request.urlretrieve(best.replace("http://", "https://"), dst)
    cr = f"{HERE}/art/credits.json"; c = json.load(open(cr)) if os.path.exists(cr) else {}
    c[f"nasa_{name}"] = {"source": "NASA Image and Video Library", "nasa_id": nid, "license": "Public domain (NASA)"}; json.dump(c, open(cr, "w"), ensure_ascii=False, indent=1)
    return dst
if __name__ == "__main__":
    if sys.argv[1] == "search":
        for r in search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20): print(*r[:3], sep=" | ")
    else: print(get(sys.argv[2], sys.argv[3]))
