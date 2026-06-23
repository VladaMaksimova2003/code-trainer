import json
import urllib.request

for tid in (4, 7):
    url = f"http://127.0.0.1:9000/tasks/{tid}?learning_language=pascal&source_language=python"
    r = json.loads(urllib.request.urlopen(url).read())
    print("=== task", tid, "===")
    print("transfer keys:", list((r.get("transfer") or {}).keys()))
    t = r.get("transfer") or {}
    for k, v in t.items():
        if "proactive" in k.lower() or k in ("pitfall_id", "transfer_type"):
            print(k, ":", str(v)[:200])
