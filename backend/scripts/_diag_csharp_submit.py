#!/usr/bin/env python3
"""Quick C# guest submit diagnostic for task_004."""
import json
import sys
import time
import urllib.request

API = "http://127.0.0.1:9000"
TASK_ID = 5

# Minimal fixed filter_positive in C# from import_debug_fixes
FIXED = """
using System;
class Program {
  static int CountPositive(int[] amounts) {
    int count = 0;
    foreach (var amount in amounts) {
      if (amount > 0) count++;
    }
    return count;
  }
  static void Main() {
    var line = Console.ReadLine();
    if (line == null) return;
    var parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
    var amounts = Array.ConvertAll(parts, int.Parse);
    Console.WriteLine(CountPositive(amounts));
  }
}
"""

body = json.dumps({"task_id": TASK_ID, "language": "csharp", "code": FIXED}).encode()
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

tests = result.get("test_results") or []
passed = sum(1 for t in tests if str(t.get("status")).upper() == "PASSED")
print(f"status={result.get('status')} tests={passed}/{len(tests)}")
for t in tests:
    print(" ", t.get("status"), (t.get("stderr") or t.get("output") or "")[:200])
if result.get("execution_error"):
    print("exec_error:", result["execution_error"][:500])
if result.get("compile_output"):
    print("compile:", str(result["compile_output"])[:500])
