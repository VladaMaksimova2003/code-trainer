#!/usr/bin/env python3
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_debug_fixes import T004_REF  # noqa: E402

API = "http://127.0.0.1:9000"
code = T004_REF["csharp"]
body = json.dumps({"task_id": 5, "language": "csharp", "code": code}).encode()
req = urllib.request.Request(
    f"{API}/guest/check",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as resp:
    queued = json.loads(resp.read().decode())
job_id = queued["job_id"]
for _ in range(120):
    with urllib.request.urlopen(f"{API}/guest/check/{job_id}", timeout=120) as resp:
        result = json.loads(resp.read().decode())
    if result.get("status") in ("SUCCESS", "FAILED"):
        break
    time.sleep(0.5)

print(json.dumps(result, ensure_ascii=False, indent=2))
