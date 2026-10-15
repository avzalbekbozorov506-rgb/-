"""Публикация Reels в Instagram через официальный API (Instagram API со входом через Instagram).
Ключ: переменная окружения IG_TOKEN (права instagram_business_basic, instagram_business_content_publish, instagram_business_manage_insights).
  python3 ig_publish.py me                         — проверить ключ: аккаунт и подписчики
  python3 ig_publish.py stats [N]                  — статистика последних N публикаций (просмотры, лайки, комментарии, сохранения)
  python3 ig_publish.py post <video.mp4> <caption.txt> [кадр_обложки_мс]  — опубликовать Reels (загрузка файла напрямую)
  python3 ig_publish.py refresh                    — продлить ключ ещё на 60 дней (печатает новый)
Обложка: API принимает только ссылку на картинку в интернете, поэтому обложка задаётся кадром видео (thumb_offset)."""
import json, os, sys, time, urllib.parse, urllib.request
API = "https://graph.instagram.com/v21.0"
TOKEN = os.environ.get("IG_TOKEN") or sys.exit("нет IG_TOKEN в окружении")
def call(method, path, params=None, data=None, headers=None, url=None):
    params = dict(params or {}, access_token=TOKEN) if not url else (params or {})
    u = (url or f"{API}/{path}") + ("?" + urllib.parse.urlencode(params) if params and method == "GET" else "")
    body = data if data is not None else (urllib.parse.urlencode(params).encode() if method == "POST" and not url else None)
    req = urllib.request.Request(u, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r: return json.load(r)
    except urllib.error.HTTPError as e: sys.exit(f"Ошибка API {e.code}: {e.read().decode()[:500]}")
def me(): return call("GET", "me", {"fields": "user_id,username,account_type,followers_count,media_count"})
cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
if cmd == "me": print(json.dumps(me(), ensure_ascii=False, indent=1))
elif cmd == "refresh": print(call("GET", "", url="https://graph.instagram.com/refresh_access_token", params={"grant_type": "ig_refresh_token", "access_token": TOKEN}))
elif cmd == "stats":
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10; uid = me()["user_id"]
    for m in call("GET", f"{uid}/media", {"fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink", "limit": n}).get("data", []):
        ins = call("GET", f"{m['id']}/insights", {"metric": "views,reach,saved,shares,total_interactions"}) if m.get("media_type") == "VIDEO" else {"data": []}
        v = {x["name"]: x["values"][0]["value"] for x in ins.get("data", [])}
        print(m["timestamp"][:10], (m.get("caption") or "")[:40].replace("\n", " "), "| лайки", m.get("like_count"), "| комм.", m.get("comments_count"), "|", v)
elif cmd == "post":
    video, cap = sys.argv[2], open(sys.argv[3], encoding="utf-8").read().strip(); thumb = sys.argv[4] if len(sys.argv) > 4 else "1500"
    uid = me()["user_id"]; size = os.path.getsize(video)
    c = call("POST", f"{uid}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": cap, "share_to_feed": "true", "thumb_offset": thumb})
    print("контейнер", c["id"]); up = call("POST", "", url=c["uri"], data=open(video, "rb").read(),
        headers={"Authorization": f"OAuth {TOKEN}", "offset": "0", "file_size": str(size)}); print("загрузка:", up)
    for _ in range(60):
        st = call("GET", c["id"], {"fields": "status_code,status"}); print("статус:", st.get("status_code"))
        if st.get("status_code") == "FINISHED": break
        if st.get("status_code") == "ERROR": sys.exit(f"Instagram не принял видео: {st}")
        time.sleep(10)
    print("опубликовано:", call("POST", f"{uid}/media_publish", {"creation_id": c["id"]}))
