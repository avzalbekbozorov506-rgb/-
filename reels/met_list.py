"""Список картин отдела европейской живописи The Met (public domain) по запросам: id | автор | название | дата."""
import json, sys, urllib.request, urllib.parse, concurrent.futures as cf
B = "https://collectionapi.metmuseum.org/public/collection/v1"
def get(u):
    with urllib.request.urlopen(u, timeout=40) as r: return json.load(r)
def obj(i):
    try: return get(f"{B}/objects/{i}")
    except Exception: return None
seen = set()
for q in sys.argv[1:]:
    ids = (get(B.replace("/v1", "/v1.1") + "/search?" + urllib.parse.urlencode({"q": q, "hasImages": "true", "departmentId": 11})) or {}).get("objectIDs") or []
    with cf.ThreadPoolExecutor(10) as ex:
        for o in ex.map(obj, [i for i in ids[:14] if i not in seen]):
            if o and o.get("isPublicDomain") and o.get("primaryImage"):
                seen.add(o["objectID"]); print(f'{q[:14]:14} {o["objectID"]} | {o["artistDisplayName"][:22]} | {o["title"][:55]} | {o["objectDate"]}')
