"""MPLT manual verification helper: GET payload + guest submit for 5 demo tasks."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("MPLT_API", "http://127.0.0.1:9000")

CASES = {
    "TCC": {
        "pattern": "task_001",
        "db_id": 2,
        "expect_transfer_type": "TCC",
        "expect_proactive": False,
        "expect_algorithm_hint": False,
        "submit_lang": "pascal",
        "submit_code": """var n, i, x, best: integer;
begin
  readln(n);
  best := -999999;
  for i := 1 to n do
  begin
    readln(x);
    if x > best then best := x;
  end;
  writeln(best + 1);
end.""",
        "expect_pattern_types": set(),
    },
    "FCC": {
        "pattern": "task_006",
        "db_id": 4,
        "expect_transfer_type": "FCC",
        "expect_proactive": True,
        "expect_algorithm_hint": False,
        "submit_lang": "pascal",
        "submit_code": """var total, n: integer;
begin
  readln(n);
  total := 10;
  writeln(total / n);
end.""",
        "expect_pattern_types": {"TRANSFER_PITFALL"},
        "expect_transfer_subtype": "FCC",
    },
    "ATCC": {
        "pattern": "task_020",
        "db_id": 28,
        "expect_transfer_type": "ATCC",
        "expect_proactive": True,
        "expect_algorithm_hint": False,
        "submit_lang": "pascal",
        "submit_code": """var n, i, x, total: integer;
begin
  readln(n);
  total := 0;
  for i := 0 to n do
  begin
    readln(x);
    if x >= 0 then total := total + x;
  end;
  writeln(total);
end.""",
        "expect_pattern_types": {"TRANSFER_PITFALL"},
        "expect_transfer_subtype": "ATCC",
    },
    "AFCC": {
        "pattern": "task_003",
        "db_id": 7,
        "expect_transfer_type": "AFCC",
        "expect_proactive": True,
        "expect_algorithm_hint": False,
        "submit_lang": "pascal",
        "submit_code": """var a, b, c: integer;
begin
  readln(a);
  readln(b);
  readln(c);
  writeln(a + b + c);
end.""",
        "expect_pattern_types": {"TRANSFER_PITFALL"},
        "expect_transfer_subtype": "AFCC",
    },
    "AlgorithmDebug": {
        "pattern": "task_004",
        "db_id": 5,
        "expect_transfer_type": "TCC",
        "expect_proactive": False,
        "expect_algorithm_hint": True,
        "submit_lang": "pascal",
        "submit_code": """var n, i, amount, count: integer;
begin
  readln(n);
  count := 1;
  for i := 1 to n do
  begin
    readln(amount);
    if amount > 0 then count := count + 1;
  end;
  writeln(count);
end.""",
        "expect_pattern_types": {"ALGORITHM"},
    },
}


def http_json(method: str, url: str, body: dict | None = None, timeout: int = 120):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"detail": raw[:500]}
        return e.code, payload


def poll_guest(job_id: str, attempts: int = 120, interval: float = 0.5):
    for _ in range(attempts):
        status, payload = http_json("GET", f"{API}/guest/check/{job_id}")
        if status != 200:
            return status, payload
        st = str(payload.get("status") or "")
        if st in {"SUCCESS", "FAILED"}:
            return status, payload
        time.sleep(interval)
    return 408, {"status": "TIMEOUT"}


def analyze_get(category: str, spec: dict, payload: dict) -> dict:
    transfer = payload.get("transfer") or (payload.get("curriculum") or {}).get("transfer") or {}
    proactive_text = ((transfer.get("proactive") or {}).get("text") or "").strip()
    algo_hint = (transfer.get("algorithm_proactive") or {}).get("text") or transfer.get("debug_meta", {}).get("hint_ru") or ""
    algo_hint = str(algo_hint).strip()
    concepts = (payload.get("curriculum") or {}).get("expected_concepts") or payload.get("expected_concepts") or []
    return {
        "transfer_type": transfer.get("transfer_type"),
        "proactive_present": bool(proactive_text),
        "proactive_snippet": proactive_text[:120],
        "algorithm_hint_present": bool(algo_hint),
        "algorithm_hint_snippet": algo_hint[:120],
        "debug_id": transfer.get("debug_id"),
        "concepts_count": len(concepts) if isinstance(concepts, list) else 0,
        "concepts_sample": [c.get("id") if isinstance(c, dict) else c for c in (concepts[:5] if isinstance(concepts, list) else [])],
        "checks": {
            "transfer_type_ok": str(transfer.get("transfer_type") or "").upper() == spec["expect_transfer_type"],
            "proactive_ok": bool(proactive_text) == spec["expect_proactive"],
            "algo_hint_ok": bool(algo_hint) == spec["expect_algorithm_hint"],
        },
    }


def analyze_submit(spec: dict, result: dict) -> dict:
    pattern_errors = result.get("pattern_errors") or []
    types = {str(e.get("type") or "").upper() for e in pattern_errors}
    transfer_rows = [e for e in pattern_errors if str(e.get("type")).upper() == "TRANSFER_PITFALL"]
    algo_rows = [e for e in pattern_errors if str(e.get("type")).upper() == "ALGORITHM"]
    tests = result.get("test_results") or []
    failed = sum(1 for t in tests if str(t.get("status")).upper() != "PASSED")
    subtype = transfer_rows[0].get("transfer_type") if transfer_rows else None
    return {
        "success_flag": result.get("success"),
        "tests_failed": failed,
        "tests_total": len(tests),
        "pattern_error_types": sorted(types),
        "transfer_feedback": transfer_rows[:2],
        "algorithm_feedback": algo_rows[:2],
        "checks": {
            "tests_failed_ok": failed > 0 or not tests,
            "pattern_types_ok": spec["expect_pattern_types"].issubset(types),
            "no_unexpected_transfer": ("TRANSFER_PITFALL" not in types) == (not spec["expect_pattern_types"] or spec["expect_pattern_types"] == {"ALGORITHM"} or "TRANSFER_PITFALL" not in spec["expect_pattern_types"]),
            "transfer_subtype_ok": (not spec.get("expect_transfer_subtype")) or subtype == spec.get("expect_transfer_subtype"),
            "algorithm_ok": ("ALGORITHM" in types) == ("ALGORITHM" in spec["expect_pattern_types"]),
        },
    }


def main():
    report = []
    for category, spec in CASES.items():
        row = {"category": category, "task_id": spec["pattern"], "db_id": spec["db_id"]}
        st, payload = http_json("GET", f"{API}/tasks/{spec['db_id']}?learning_language=pascal")
        row["get_status"] = st
        if st != 200:
            row["status"] = "FAIL GET"
            row["get_error"] = payload
            report.append(row)
            continue
        before = analyze_get(category, spec, payload)
        row["before_submit"] = before
        row["transfer_payload_snippet"] = {
            k: (payload.get("transfer") or {}).get(k)
            for k in ["transfer_type", "pitfall_id", "debug_id", "proactive", "algorithm_proactive", "debug_meta"]
            if (payload.get("transfer") or {}).get(k) is not None
        }
        st2, queued = http_json(
            "POST",
            f"{API}/guest/check",
            {"task_id": spec["db_id"], "language": spec["submit_lang"], "code": spec["submit_code"]},
        )
        row["submit_queue_status"] = st2
        if st2 != 200 or not queued.get("job_id"):
            row["status"] = "FAIL SUBMIT QUEUE"
            row["submit_error"] = queued
            report.append(row)
            continue
        _, result = poll_guest(str(queued["job_id"]))
        submit = analyze_submit(spec, result)
        row["after_submit"] = submit
        row["api_feedback_snippet"] = {
            "pattern_errors": (result.get("pattern_errors") or [])[:3],
            "test_stats": {
                "total": len(result.get("test_results") or []),
                "failed": submit["tests_failed"],
            },
        }
        before_ok = all(before["checks"].values())
        submit_ok = all(submit["checks"].values())
        row["status"] = "PASS" if before_ok and submit_ok else "FAIL"
        report.append(row)

    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "MPLT_runtime_manual_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\nWROTE", out_path)


if __name__ == "__main__":
    main()
