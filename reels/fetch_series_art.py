"""Скачивает картины серии из The Met в art/met_<id>.jpg (≤2600 px по короткой стороне), пишет credits, печатает данные музея для сверки."""
import json, io, os, urllib.request, concurrent.futures as cf
from PIL import Image
from series_art import ART
B = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
cr = json.load(open("art/credits.json"))
ids = sorted({v[0] for d in ART.values() for v in d.values() if isinstance(v[0], int)})
def job(i):
    p = f"art/met_{i}.jpg"; o = json.load(urllib.request.urlopen(B + str(i), timeout=60))
    if not o.get("isPublicDomain"): return i, None, "НЕ PD"
    if not os.path.exists(p):
        im = Image.open(io.BytesIO(urllib.request.urlopen(o["primaryImage"], timeout=120).read())).convert("RGB")
        s = min(1, 2600 / min(im.size)); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS) if s < 1 else im
        im.save(p, quality=92)
    w, h = Image.open(p).size
    return i, o, f"{w}x{h}"
with cf.ThreadPoolExecutor(6) as ex:
    for i, o, info in ex.map(job, ids):
        if o: cr[f"met_{i}"] = f"{o['artistDisplayName'] or 'Unknown'} — {o['title']}{', ' + o['objectDate'] if o['objectDate'] else ''} (The Met, CC0)"
        print(i, info, "|", (o or {}).get("artistDisplayName", "")[:25], "|", (o or {}).get("title", "")[:50], "|", (o or {}).get("objectDate", ""), flush=True)
json.dump(cr, open("art/credits.json", "w"), ensure_ascii=False, indent=1)
