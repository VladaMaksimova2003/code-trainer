import json, urllib.request, time

API = "http://127.0.0.1:9000"
code = """var total, n: integer;
begin
  readln(n);
  total := 10;
  writeln(total / n);
end."""
body = json.dumps({"task_id": 4, "language": "pascal", "code": code}).encode()
req = urllib.request.Request(f"{API}/guest/check", data=body, headers={"Content-Type":"application/json"}, method="POST")
job = json.loads(urllib.request.urlopen(req, timeout=30).read())
print("job", job)
for i in range(60):
    r = json.loads(urllib.request.urlopen(f"{API}/guest/check/{job['job_id']}", timeout=30).read())
    if r.get("status") in ("SUCCESS","FAILED"):
        print(json.dumps(r, ensure_ascii=False, indent=2))
        break
    time.sleep(0.5)
