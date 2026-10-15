"""Подбор картин из The Met (только isPublicDomain): для каждой сцены — первый подходящий результат по запросам, без повторов.
python3 art_pick.py <spec.json> <out.json> — spec: {"6": {"hook": ["запрос", ...], "s1": [...]}, ...}; лист превью work/series/sheet_<n>.jpg"""
import json, os, sys, urllib.request, urllib.parse, io, concurrent.futures as cf
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
B = "https://collectionapi.metmuseum.org/public/collection/v1"
def get(u):
    with urllib.request.urlopen(u, timeout=40) as r: return json.load(r)
spec = json.load(open(sys.argv[1])); outp = sys.argv[2]
res = json.load(open(outp)) if os.path.exists(outp) else {}
used = {v["id"] for r in res.values() for v in r.values()}
used |= {int(x) for x in json.load(open(f"{HERE}/work/series/used_ids.json"))} if os.path.exists(f"{HERE}/work/series/used_ids.json") else set()
def obj(i):
    try: return get(f"{B}/objects/{i}")
    except Exception: return None
for n, scenes in spec.items():
    res.setdefault(n, {})
    for key, qs in scenes.items():
        if key in res[n]: continue
        pick = None
        for q in qs:
            for medium in ("Paintings", None):
                p = {"q": q, "hasImages": "true"}
                if medium: p["medium"] = medium
                try: ids = (get(B.replace("/v1", "/v1.1") + "/search?" + urllib.parse.urlencode(p)) or {}).get("objectIDs") or []
                except Exception: ids = []
                with cf.ThreadPoolExecutor(8) as ex:
                    for o in ex.map(obj, [i for i in ids[:16] if i not in used]):
                        if o and o.get("isPublicDomain") and o.get("primaryImage") and o["objectID"] not in used \
                           and any(k in (o.get("classification", "") + o.get("objectName", "")) for k in ("Painting", "painting")):
                            pick = o; break
                if pick: break
            if pick: break
        if pick:
            used.add(pick["objectID"])
            res[n][key] = dict(id=pick["objectID"], a=pick["artistDisplayName"], t=pick["title"], d=pick["objectDate"], img=pick["primaryImage"], small=pick["primaryImageSmall"], q=q)
        print(n, key, "→", (pick or {}).get("title", "НЕТ")[:60], flush=True)
    json.dump(res, open(outp, "w"), ensure_ascii=False, indent=1)
    tiles = []
    for key, v in res[n].items():
        try:
            im = Image.open(io.BytesIO(urllib.request.urlopen(v["small"], timeout=40).read())).convert("RGB"); im.thumbnail((260, 260))
        except Exception: im = Image.new("RGB", (260, 260), "gray")
        t = Image.new("RGB", (260, 285), "white"); t.paste(im, ((260 - im.width) // 2, 0)); ImageDraw.Draw(t).text((3, 265), f"{key}: {v['t'][:34]}", fill="black"); tiles.append(t)
    S = Image.new("RGB", (260 * len(tiles), 285), "white")
    for k, t in enumerate(tiles): S.paste(t, (260 * k, 0))
    S.save(f"{HERE}/work/series/sheet_{n}.jpg", quality=80)
