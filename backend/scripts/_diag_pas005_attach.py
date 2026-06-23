#!/usr/bin/env python3
"""Simulate DB attach path for pas_005 (chapter 1, task 5)."""

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.display.showcase_display import finalize_student_task_payload
from application.tasks.services.teacher_editor_public_payload import (
    apply_teacher_editor_public_payload,
)


class _Row:
    title = "[1. Базовый синтаксис через простые алгоритмы] Подсчёт положительных операций"
    description = "debug task"
    difficulty = "easy"
    task_type = "debug_code"
    test_cases = [{"inputs": "5\n100\n-20\n0\n50\n-1\n", "output": "2"}]
    code_examples = {
        "java": "class Main {}",
        "cpp": "#include <iostream>",
        "curriculum_showcase": {
            "slot_id": "pas_005",
            "target_language": "java",
            "technical_concept_id": "tc_console_io",
            "expected_concept_ids": ["tc_console_io"],
            "primary_action": "debug",
            "task_format": "исправление",
            "known_language_variants": {
                "cpp": {"source_code": "#include <iostream>\nint main(){}"},
                "java": {"source_code": "class Main {}"},
            },
        },
    }


payload = {
    "id": 5,
    "title": _Row.title,
    "code_examples": dict(_Row.code_examples),
    "curriculum": {"slot_id": "pas_005", "target_language": "java"},
    "teacher_assembly_override": True,
}

payload = apply_teacher_editor_public_payload(_Row(), payload, learning_language="java")
payload = finalize_student_task_payload(payload)

print("title:", payload.get("title"))
concepts = (payload.get("curriculum") or {}).get("expected_concepts") or []
print("concepts:", len(concepts), [c.get("id") for c in concepts])
transfer = payload.get("transfer") or (payload.get("curriculum") or {}).get("transfer") or {}
print("warning:", transfer.get("reference_warning_ru"))
