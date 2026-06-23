#!/usr/bin/env python3
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.content.algo_syntax_task_extra import (
    resolve_slot_pattern_key,
    algo_expected_concepts,
)
from application.curriculum.display.showcase_display import (
    strip_showcase_title_prefix,
    sanitize_public_task_payload,
)
from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled

print("catalog_sync", is_catalog_sync_enabled())
print("pattern", resolve_slot_pattern_key("pas_005"))
print("java concepts", algo_expected_concepts("pas_005", "java"))
title = "[1. Базовый синтаксис через простые алгоритмы] Подсчёт положительных операций"
print("strip", strip_showcase_title_prefix(title))

payload = sanitize_public_task_payload(
    {
        "id": 5,
        "title": title,
        "code_examples": {
            "cpp": "int main(){}",
            "java": "class Main{}",
            "curriculum_showcase": {
                "slot_id": "pas_005",
                "target_language": "java",
                "technical_concept_id": "tc_console_io",
                "known_language_variants": {
                    "cpp": {"source_code": "#include <iostream>"},
                    "java": {"source_code": "class Main{}"},
                },
            },
        },
        "curriculum": {"slot_id": "pas_005", "target_language": "java"},
    }
)
print("title out", payload.get("title"))
concepts = (payload.get("curriculum") or {}).get("expected_concepts") or payload.get("expected_concepts") or []
print("n concepts", len(concepts))
print("ids", [c.get("id") for c in concepts])
print("display", [c.get("display_id") for c in concepts])
print("names", [c.get("name_ru") for c in concepts])
transfer = payload.get("transfer") or (payload.get("curriculum") or {}).get("transfer")
print("transfer keys", sorted((transfer or {}).keys()))
print("warning", (transfer or {}).get("reference_warning_ru"))
