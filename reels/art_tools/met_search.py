import json, sys, urllib.request, urllib.parse, concurrent.futures as cf
B = "https://collectionapi.metmuseum.org/public/collection/v1"
def get(u):
    with urllib.request.urlopen(u, timeout=40) as r: return json.load(r)
def obj(i):
    try: return get(f"{B}/objects/{i}")
    except Exception: return None
for q in sys.argv[1:]:
    ids = (get(B.replace("/v1","/v1.1") + "/search?" + urllib.parse.urlencode({"q": q, "hasImages": "true"})) or {}).get("objectIDs") or []
    with cf.ThreadPoolExecutor(10) as ex:
        for o in ex.map(obj, ids[:30]):
            if o and o.get("isPublicDomain") and o.get("primaryImage") and "Painting" in (o.get("classification","")):
                print(f'{q[:12]:12} {o["objectID"]} | {o["culture"][:10]} | {o["artistDisplayName"][:20]} | {o["title"][:55]} | {o["objectDate"]}')
