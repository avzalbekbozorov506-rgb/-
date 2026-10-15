import json, sys, urllib.request, io, concurrent.futures as cf
from PIL import Image, ImageDraw
B = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
def get(i):
    o = json.load(urllib.request.urlopen(B + str(i), timeout=40))
    im = Image.open(io.BytesIO(urllib.request.urlopen(o["primaryImageSmall"], timeout=60).read())).convert("RGB")
    return i, o, im
ids = [int(x) for x in sys.argv[2:]]
with cf.ThreadPoolExecutor(8) as ex: res = list(ex.map(get, ids))
T = 300; sheet = Image.new("RGB", (T * 5, (T + 30) * ((len(res) + 4) // 5)), (20, 20, 20)); d = ImageDraw.Draw(sheet)
for k, (i, o, im) in enumerate(res):
    im.thumbnail((T, T)); x, y = (k % 5) * T, (k // 5) * (T + 30); sheet.paste(im, (x + (T - im.width) // 2, y))
    d.text((x + 4, y + T + 4), f"{i} {o['artistDisplayName'][:18]}", fill=(255, 255, 255))
    print(i, o["isPublicDomain"], o["artistDisplayName"], "|", o["title"][:60], "|", o["objectDate"])
sheet.save(sys.argv[1])
