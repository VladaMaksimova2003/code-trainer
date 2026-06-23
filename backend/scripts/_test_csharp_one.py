import json, time, urllib.request, psycopg2

API = "http://127.0.0.1:9000"
conn = psycopg2.connect(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")
cur = conn.cursor()
cur.execute("select code_examples from task where id=%s", (5,))
raw = cur.fetchone()[0]
ce = raw if isinstance(raw, dict) else json.loads(raw)
code = ce["csharp"]
body = json.dumps({"task_id": 5, "language": "csharp", "code": code}).encode()
for attempt in range(10):
    try:
        q = json.loads(urllib.request.urlopen(urllib.request.Request(f"{API}/guest/check", data=body, headers={"Content-Type": "application/json"}, method="POST"), timeout=120).read())
        break
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(10)
            continue
        raise
for _ in range(240):
    r = json.loads(urllib.request.urlopen(f"{API}/guest/check/{q['job_id']}", timeout=120).read())
    if r.get("status") in ("SUCCESS", "FAILED"):
        print(json.dumps({"success": r.get("success"), "tests": r.get("test_results"), "compiler": r.get("compiler_errors")}, ensure_ascii=False, indent=2))
        break
    time.sleep(0.5)
