import json, time, urllib.request, psycopg2

API = "http://127.0.0.1:9000"
conn = psycopg2.connect(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")
cur = conn.cursor()

def submit(task_id, lang, code):
    body = json.dumps({"task_id": task_id, "language": lang, "code": code}).encode()
    req = urllib.request.Request(f"{API}/guest/check", data=body, headers={"Content-Type": "application/json"}, method="POST")
    for attempt in range(6):
        try:
            q = json.loads(urllib.request.urlopen(req, timeout=120).read())
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(8)
                continue
            raise
    jid = q["job_id"]
    for _ in range(180):
        r = json.loads(urllib.request.urlopen(f"{API}/guest/check/{jid}", timeout=120).read())
        if r.get("status") in ("SUCCESS", "FAILED"):
            return r
        time.sleep(0.5)
    return {"status": "TIMEOUT"}

out = {}
for task_id, langs in [(5, ["csharp", "java"]), (77, ["csharp", "java"])]:
    cur.execute("select code_examples from task where id=%s", (task_id,))
    raw = cur.fetchone()[0]
    ce = json.loads(raw) if isinstance(raw, str) else raw
    out[str(task_id)] = {}
    for lang in langs:
        code = ce.get(lang) or ""
        r = submit(task_id, lang, code)
        out[str(task_id)][lang] = {
            "success": r.get("success"),
            "tests": r.get("test_results"),
            "compiler": r.get("compiler_errors"),
            "pattern": r.get("pattern_errors"),
        }
        time.sleep(6)

Path = __import__("pathlib").Path
Path(__file__).resolve().parents[2].joinpath("docs", "_diag_csharp_java.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({k: {l: {"success": v[l]["success"], "tests": v[l]["tests"]} for l in v} for k, v in out.items()}, ensure_ascii=False, indent=2))
