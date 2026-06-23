"""Runtime/catalog helpers for Pascal showcase tasks (pas_* and legacy slugs)."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

_PAS_SLOT = re.compile(r"^pas_(\d{3})$")
_LEGACY_SLOT = re.compile(r"^[a-z]{2,4}_\d{2,3}$")

_LEGACY_ROWS: dict[str, tuple] = {
    "str_07": (
        "str_07",
        "strings",
        "Copy и конкатенация — сборка",
        "сборка_фрагмента",
        "assemble",
        "asm_string_copy_concat",
        "",
        "copy; concat",
        "medium",
        "",
    ),
}

_SLOT_TO_ROW: dict[str, tuple] | None = None


def is_pascal_catalog_slot(slot_id: str | None) -> bool:
    if not slot_id:
        return False
    sid = str(slot_id).strip()
    return bool(_PAS_SLOT.match(sid) or _LEGACY_SLOT.match(sid))


def _catalog_row_for_slot(slot_id: str) -> tuple | None:
    global _SLOT_TO_ROW
    if _SLOT_TO_ROW is None:
        from scripts.pascal_v31_tasks import V31_TASKS

        _SLOT_TO_ROW = {row[0]: row for row in V31_TASKS}
        _SLOT_TO_ROW.update(_LEGACY_ROWS)
    return _SLOT_TO_ROW.get(str(slot_id).strip())


@lru_cache(maxsize=512)
def catalog_extra_for_slot(slot_id: str) -> dict[str, Any] | None:
    row = _catalog_row_for_slot(slot_id)
    if row is None:
        return None
    from application.curriculum.pascal.catalog.pascal_v311_content import build_task_extra

    extra = dict(build_task_extra(row))
    extra.setdefault("slot_id", slot_id)
    extra.setdefault("slug", slot_id)
    return extra


def _has_assembly_blocks(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def apply_catalog_fields_to_showcase(showcase_fields: dict[str, Any]) -> dict[str, Any]:
    slot_id = str(showcase_fields.get("slot_id") or showcase_fields.get("slug") or "").strip()
    extra = catalog_extra_for_slot(slot_id)
    if not extra:
        return showcase_fields

    refreshed = dict(showcase_fields)
    teacher_concepts = showcase_fields.get("expected_concepts")
    has_teacher = isinstance(teacher_concepts, dict) and any(
        isinstance(v, list) and v for v in teacher_concepts.values()
    )
    for key in (
        "test_cases",
        "educational_goal",
        "expected_concept_ids",
        "pascal_features",
        "task_format",
        "reference_solution_pascal",
        "language_variants",
    ):
        if has_teacher and key == "expected_concept_ids":
            continue
        if key in extra and extra[key] is not None:
            refreshed[key] = extra[key]

    catalog_blocks = extra.get("blocks")
    existing_blocks = showcase_fields.get("blocks")
    if _has_assembly_blocks(catalog_blocks) and (
        not _has_assembly_blocks(existing_blocks) or slot_id in _LEGACY_ROWS
    ):
        refreshed["blocks"] = catalog_blocks
        for key in ("original_code", "template", "correct_order"):
            if key in extra and extra[key] is not None:
                refreshed[key] = extra[key]
    elif not _has_assembly_blocks(existing_blocks):
        for key in ("original_code", "template", "blocks", "correct_order"):
            if key in extra and extra[key] is not None:
                refreshed[key] = extra[key]

    description = extra.get("educational_goal")
    if description:
        refreshed["description"] = description
        refreshed["short_instruction"] = description

    return refreshed
