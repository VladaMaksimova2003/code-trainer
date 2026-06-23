"""Runtime/catalog helpers for Python v4 showcase tasks."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

_V4_SLOT = re.compile(r"^py_(\d{3})$")

_SLOT_TO_ROW: dict[str, tuple] | None = None


def is_v4_python_slot(slot_id: str | None) -> bool:
    return bool(slot_id and _V4_SLOT.match(str(slot_id).strip()))


def _catalog_row_for_slot(slot_id: str) -> tuple | None:
    global _SLOT_TO_ROW
    if _SLOT_TO_ROW is None:
        from scripts.python_v31_tasks import V31_TASKS

        _SLOT_TO_ROW = {row[0]: row for row in V31_TASKS}
    return _SLOT_TO_ROW.get(str(slot_id).strip())


@lru_cache(maxsize=512)
def catalog_extra_for_slot(slot_id: str) -> dict[str, Any] | None:
    row = _catalog_row_for_slot(slot_id)
    if row is None:
        return None
    from application.curriculum.python.catalog.python_v311_content import build_task_extra

    return build_task_extra(row)


def educational_goal_for_slot(slot_id: str) -> str:
    extra = catalog_extra_for_slot(slot_id)
    if not extra:
        return ""
    return str(extra.get("educational_goal") or "")


def expected_concepts_for_slot(slot_id: str) -> list[str]:
    extra = catalog_extra_for_slot(slot_id)
    if not extra:
        return []
    raw = extra.get("expected_concept_ids")
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()]


def sync_v4_expected_concepts(showcase_fields: dict[str, Any]) -> None:
    """Always align v4 Python expected concepts with the in-code catalog."""
    raw = showcase_fields.get("expected_concepts")
    if isinstance(raw, dict) and any(isinstance(v, list) and v for v in raw.values()):
        return
    slot_id = str(showcase_fields.get("slot_id") or showcase_fields.get("slug") or "").strip()
    if not is_v4_python_slot(slot_id):
        return
    concepts = expected_concepts_for_slot(slot_id)
    if concepts:
        showcase_fields["expected_concept_ids"] = concepts


def debug_starter_for_slot(slot_id: str, reference_python: str) -> str:
    ref = reference_python.strip()
    if not ref:
        return "x = 1\nprint(x)"
    lines = [ln.strip() for ln in ref.splitlines() if ln.strip()]
    if not lines:
        return ref

    m = _V4_SLOT.match(slot_id)
    task_num = int(m.group(1)) if m else 0

    # Perimeter / doubled formula tasks: drop *2 factor.
    for idx, line in enumerate(lines):
        if "* 2" in line or "*2" in line:
            lines[idx] = line.replace("* 2", "", 1).replace("*2", "", 1)
            return "\n".join(lines)

    # Modulo / last digit: use division instead of mod.
    for idx, line in enumerate(lines):
        if " % " in line and task_num % 3 == 0:
            lines[idx] = line.replace(" % ", " // ", 1)
            return "\n".join(lines)

    # Assignment vs comparison confusion.
    if task_num % 2 == 0:
        for idx, line in enumerate(lines):
            if " = " in line and "==" not in line and not line.strip().startswith("print"):
                lines[idx] = line.replace(" = ", " == ", 1)
                return "\n".join(lines)

    # Broken print / typo in output line.
    if lines[-1].startswith("print("):
        lines[-1] = lines[-1].replace("print(", "prnt(", 1)
        return "\n".join(lines)

    lines[-1] = lines[-1] + "  # исправьте ошибку"
    return "\n".join(lines)


def assembly_payload_for_slot(slot_id: str, reference_python: str) -> tuple[str, str, list[str], list[int]]:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_assembly_payload,
        is_algo_syntax_slot,
    )
    from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format

    if is_algo_syntax_slot(slot_id):
        return algo_assembly_payload(slot_id, "python", task_format="сборка_программы")
    return assembly_payload_for_format("сборка_программы", "python", reference_python)


def apply_catalog_fields_to_showcase(showcase_fields: dict[str, Any]) -> dict[str, Any]:
    slot_id = str(showcase_fields.get("slot_id") or showcase_fields.get("slug") or "").strip()
    if not is_v4_python_slot(slot_id):
        return showcase_fields

    extra = catalog_extra_for_slot(slot_id)
    if not extra:
        return showcase_fields

    refreshed = dict(showcase_fields)
    teacher_concepts = showcase_fields.get("expected_concepts")
    has_teacher = isinstance(teacher_concepts, dict) and any(
        isinstance(v, list) and v for v in teacher_concepts.values()
    )
    for key in (
        "expected_concept_ids",
        "known_language_variants",
        "assemble_context",
        "test_cases",
        "python_features",
        "task_format",
        "educational_goal",
        "slot_pattern_id",
    ):
        if has_teacher and key == "expected_concept_ids":
            continue
        if key in extra and extra[key] is not None:
            merged[key] = extra[key]

    if extra.get("educational_goal"):
        merged["short_instruction"] = str(extra["educational_goal"])

    return merged


def apply_catalog_fields_to_task_payload(payload: dict[str, Any], showcase_fields: dict[str, Any]) -> dict[str, Any]:
    slot_id = str(showcase_fields.get("slot_id") or showcase_fields.get("slug") or "").strip()
    if not is_v4_python_slot(slot_id):
        return payload

    extra = catalog_extra_for_slot(slot_id)
    if not extra:
        return payload

    result = dict(payload)
    if extra.get("educational_goal"):
        result["description"] = str(extra["educational_goal"])

    test_cases = extra.get("test_cases")
    if isinstance(test_cases, list) and test_cases:
        result["test_cases"] = test_cases

    if extra.get("expected_concept_ids"):
        result["expected_concept_ids"] = list(extra["expected_concept_ids"])

    task_type = str(result.get("type") or result.get("task_type") or "")
    fmt = str(extra.get("task_format") or "")

    if fmt in {"исправление", "поиск_ошибки"} or task_type in {"debug", "translation"}:
        starter = extra.get("starter_python")
        if starter:
            examples = dict(result.get("code_examples") or {})
            examples["python"] = str(starter)
            result["code_examples"] = examples
            if task_type in {"debug", "translation"}:
                result["source_code"] = str(starter)
                result["source_language"] = "python"

    if fmt.startswith("сборка") or task_type == "blocks":
        blocks = extra.get("blocks")
        template = extra.get("template")
        if isinstance(blocks, list) and blocks:
            result["blocks"] = blocks
        if template is not None:
            result["template"] = template

    return result
