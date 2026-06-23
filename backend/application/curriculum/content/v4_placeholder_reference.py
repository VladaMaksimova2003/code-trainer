"""Reference code and assembly metadata for placeholder capstone tasks (plh_*)."""

from __future__ import annotations

from typing import Any

try:
    from scripts.placeholder_capstone_tasks import PLACEHOLDER_CAPSTONE_META
except ImportError:
    PLACEHOLDER_CAPSTONE_META: dict[str, dict[str, Any]] = {}


def is_placeholder_slot(slot_id: str | None) -> bool:
    return bool(slot_id and str(slot_id).strip().startswith("plh_"))


def placeholder_meta(slot_id: str) -> dict[str, Any] | None:
    raw = PLACEHOLDER_CAPSTONE_META.get(str(slot_id).strip())
    if not raw:
        return None
    return _enriched_meta(raw)


def _enriched_meta(raw: dict[str, Any]) -> dict[str, Any]:
    from application.curriculum.content.plh_reference_synthesis import enrich_reference_codes

    meta = dict(raw)
    meta["reference_codes"] = enrich_reference_codes(meta)
    return meta


_AFTER_TASK_TO_CHAPTER: dict[int, str] | None = None


def _build_after_task_map() -> dict[int, str]:
    from application.curriculum.python.showcase.python_v311_registry import (
        V311_CHAPTER_ORDER,
        V311_COLLECTION_TARGETS,
    )

    mapping: dict[int, str] = {}
    total = 0
    for chapter in V311_CHAPTER_ORDER:
        core_count = max(0, V311_COLLECTION_TARGETS[chapter] - 3)
        total += core_count
        mapping[total] = chapter
    return mapping


def chapter_for_placeholder(slot_id: str) -> str:
    global _AFTER_TASK_TO_CHAPTER
    if _AFTER_TASK_TO_CHAPTER is None:
        _AFTER_TASK_TO_CHAPTER = _build_after_task_map()
    meta = placeholder_meta(slot_id) or {}
    after = int(meta.get("after_task") or 0)
    return _AFTER_TASK_TO_CHAPTER.get(after, "program_skeleton")


def placeholder_title(slot_id: str) -> str:
    meta = placeholder_meta(slot_id) or {}
    return str(meta.get("title") or meta.get("short_goal") or slot_id).strip()


def placeholder_description(slot_id: str) -> str:
    meta = placeholder_meta(slot_id) or {}
    return str(meta.get("detailed_description") or meta.get("goal") or "").strip()


def placeholder_test_cases(slot_id: str) -> list[dict[str, str]]:
    meta = placeholder_meta(slot_id) or {}
    raw = meta.get("test_cases") or []
    return [dict(item) for item in raw if isinstance(item, dict)]


def placeholder_expected_concepts(slot_id: str) -> list[str]:
    meta = placeholder_meta(slot_id) or {}
    raw = meta.get("expected_concepts") or []
    return [str(item) for item in raw if str(item).strip()]


def get_placeholder_reference(slot_id: str, language: str) -> str:
    meta = placeholder_meta(slot_id)
    if not meta:
        return ""
    codes = meta.get("reference_codes") or {}
    return str(codes.get(str(language).lower()) or "").strip()


def _template_from_underscore_gaps(code: str, blocks: list[str]) -> tuple[str, list[str], list[int]]:
    parts = str(code or "").split("___")
    gap_count = max(0, len(parts) - 1)
    template = parts[0]
    for idx in range(gap_count):
        template += "{" + str(idx) + "}" + parts[idx + 1]
    pool = [str(item) for item in blocks if str(item).strip()]
    if not pool:
        pool = [":=", ">=", "then"]
    correct_order = list(range(min(gap_count, len(pool))))
    while len(pool) < gap_count:
        pool.append(f"gap{len(pool)}")
    return template, pool, correct_order


def placeholder_assembly_payload(
    slot_id: str,
    language: str,
    *,
    task_format: str = "сборка_фрагмента",
) -> tuple[str, str, list[str], list[int]]:
    from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format
    from application.curriculum.content.v4_code_format import format_reference_code

    lang = str(language or "python").lower()
    meta = placeholder_meta(slot_id) or {}
    ref = format_reference_code(get_placeholder_reference(slot_id, lang), lang)

    codes = meta.get("placeholder_codes") or {}
    blocks_map = meta.get("placeholder_blocks") or {}
    placeholder_code = str(codes.get(lang) or "").strip()
    blocks = list(blocks_map.get(lang) or [])

    if placeholder_code and "___" in placeholder_code:
        template, block_pool, order = _template_from_underscore_gaps(placeholder_code, blocks)
        display = format_reference_code(placeholder_code.replace("___", " ___ "), lang)
        return display or placeholder_code, template, block_pool, order

    if placeholder_code and blocks:
        template, block_pool, order = _template_from_underscore_gaps(placeholder_code, blocks)
        return placeholder_code, template, block_pool, order

    return assembly_payload_for_format(task_format, lang, ref)
