import json, io, os, sys, urllib.request, concurrent.futures as cf
from PIL import Image
B = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
cr = json.load(open("art/credits.json")); ids = [int(x) for x in sys.argv[1:]]
def job(i):
    p = f"art/met_{i}.jpg"; o = json.load(urllib.request.urlopen(B + str(i), timeout=60))
    if not o.get("isPublicDomain"): return i, None, "НЕ PD"
    if not os.path.exists(p):
        im = Image.open(io.BytesIO(urllib.request.urlopen(o["primaryImage"], timeout=180).read())).convert("RGB")
        s = min(1, 2600 / min(im.size)); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS) if s < 1 else im
        im.save(p, quality=92)
    return i, o, "%dx%d" % Image.open(p).size
with cf.ThreadPoolExecutor(6) as ex:
    for i, o, info in ex.map(job, ids):
        if o: cr[f"met_{i}"] = f"{o['artistDisplayName'] or 'Unknown'} — {o['title']}{', ' + o['objectDate'] if o['objectDate'] else ''} (The Met, CC0)"
        print(i, info, flush=True)
json.dump(cr, open("art/credits.json", "w"), ensure_ascii=False, indent=1)
