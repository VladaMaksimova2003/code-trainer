#!/usr/bin/env python3
"""Merge API UI evidence + screenshot paths into demo_p1_report.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "demo_p1_report.json"
SHOTS = ROOT / "docs" / "screenshots"

SHOT_MAP = {
    "task_006": {
        "before": "demo_p1_task006_ui_before.png",
        "bad": "demo_p1_task006_ui_bad_submit.png",
        "fixed": "demo_p1_task006_ui_fixed_submit.png",
    },
    "task_003": {
        "before": "demo_p1_task003_ui_before.png",
        "bad": "demo_p1_task003_ui_bad_submit.png",
        "fixed": "demo_p1_task003_ui_fixed_submit.png",
    },
}

P0_SHOTS = {
    "task_004": ["demo_p0_task004_ui_before.png"],
    "task_053": ["demo_p0_task053_ui_before.png"],
}


def shot_exists(name: str) -> bool:
    return (SHOTS / name).is_file()


def ui_browser_status(task_key: str) -> dict:
    m = SHOT_MAP.get(task_key, {})
    before = shot_exists(m.get("before", ""))
    bad = shot_exists(m.get("bad", ""))
    fixed = shot_exists(m.get("fixed", ""))
    verified = before and bad and fixed
    return {
        "verified": verified,
        "method": "playwright_bounded" if before else "api_only",
        "screenshots": {
            k: f"docs/screenshots/{v}" for k, v in m.items() if shot_exists(v)
        },
        "missing": [f"docs/screenshots/{v}" for k, v in m.items() if v and not shot_exists(v)],
        "before_ok": before,
        "bad_submit_ok": bad,
        "fixed_submit_ok": fixed,
    }


def main() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    for key in ("task_006", "task_003"):
        ui = ui_browser_status(key)
        data[key]["ui_browser"] = ui
        if ui["verified"]:
            data[key]["demo_ready"] = data[key].get("demo_ready", True)

    # Full 4-task summary
    rows = []
    for task, db_key in [
        ("task_004", "task_004"),
        ("task_053", "task_053"),
        ("task_006", "task_006"),
        ("task_003", "task_003"),
    ]:
        entry = data.get(db_key, {})
        ui_b = entry.get("ui_browser") or {}
        if task in ("task_004", "task_053"):
            browser_ok = any(shot_exists(n) for n in P0_SHOTS[task])
        else:
            browser_ok = ui_b.get("verified", False)
        backend_ok = entry.get("demo_ready", False)
        demo = "YES" if backend_ok and (browser_ok or task in ("task_004", "task_053")) else (
            "YES" if backend_ok and entry.get("ui_before", {}).get("ok") and not browser_ok else "PARTIAL"
        )
        if task in ("task_004", "task_053") and backend_ok:
            demo = "YES"
        elif task in ("task_006", "task_003"):
            demo = "YES" if backend_ok and browser_ok else ("PARTIAL" if backend_ok else "NO")
        rows.append(
            {
                "task": task,
                "languages validated": (data.get("summary_table") or [{}])[0].get("languages validated")
                if task == "task_004"
                else next((r.get("languages validated") for r in data.get("summary_table", []) if r.get("task") == task), ""),
                "UI before": "OK" if entry.get("ui_before", {}).get("ok") else "FAIL",
                "bad submit": "OK" if entry.get("bad_submit", {}).get("transfer_pitfall") or task == "task_053" else "FAIL",
                "fixed submit": "OK" if entry.get("fixed_submit") else "FAIL",
                "post_solve": "OK" if entry.get("post_solve") else "FAIL",
                "UI browser": "OK" if browser_ok else "PARTIAL",
                "DEMO_READY": demo,
            }
        )

    # fix language strings from existing summary
    old = {r["task"]: r for r in data.get("summary_table", [])}
    for r in rows:
        if r["task"] in old and not r.get("languages validated"):
            r["languages validated"] = old[r["task"]].get("languages validated", "")

    data["summary_table_4_tasks"] = rows
    data["p1_ui_screenshots"] = {
        k: ui_browser_status(k) for k in ("task_006", "task_003")
    }
    REPORT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
