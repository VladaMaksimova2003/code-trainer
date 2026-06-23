import urllib.request
urls = [
    "http://127.0.0.1:5173/",
    "http://127.0.0.1:9000/docs",
    "http://127.0.0.1:9000/openapi.json",
    "http://127.0.0.1:9000/api/tasks/2",
    "http://127.0.0.1:9000/guest/check",
]
for u in urls:
    try:
        req = urllib.request.Request(u, method="GET")
        r = urllib.request.urlopen(req, timeout=10)
        print(u, r.status, len(r.read()))
    except Exception as e:
        print(u, type(e).__name__, str(e)[:120])
