#!/usr/bin/env python3
from application.tasks.services.catalog.task_query import TaskQueryService
from infrastructure.db.session import SessionLocal

db = SessionLocal()
svc = TaskQueryService()
payload = svc.get_task(db, 4, None, learning_language="python", source_language="cpp")
transfer = payload.get("transfer") or {}
print("PROACTIVE:", (transfer.get("proactive") or {}).get("text", ""))
print("HINTS:")
for i, h in enumerate(payload.get("hints") or []):
    print(f"  [{i}] {h}")
db.close()
