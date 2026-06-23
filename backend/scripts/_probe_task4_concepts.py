import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg2

from application.curriculum.display.showcase_display import finalize_student_task_payload
from application.curriculum.validation.expected_concept_checker import (
    build_display_expected_concept_cards,
)

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="code_trainer",
    user="code_trainer",
    password="change_me",
)
cur = conn.cursor()
cur.execute(
    "select id, title, description, test_cases, code_examples, task_type from task where id=4"
)
row = cur.fetchone()
ce = row[4]
payload = {
    "id": 4,
    "title": row[1],
    "description": row[2],
    "test_cases": row[3],
    "type": "block_reorder",
    "task_type": "block_reorder",
    "code_examples": ce,
    "curriculum": {
        "slot_pattern_id": "task_006",
        "slot_id": "pas_004",
        "action": "assemble",
    },
}
final = finalize_student_task_payload(
    payload,
    source_language="python",
    target_language="java",
)
names = [c.get("name_ru") for c in final.get("expected_concepts", [])]
ids = [c.get("id") for c in final.get("expected_concepts", [])]
print("FINAL count", len(names))
for name, cid in zip(names, ids):
    print(f"  {cid}: {name}")

java_ids = (ce.get("expected_concepts") or {}).get("java") or []
print("\nDB java ids", java_ids)
cards = build_display_expected_concept_cards(java_ids)
print("build_display cards", len(cards), [c["id"] for c in cards])
conn.close()
