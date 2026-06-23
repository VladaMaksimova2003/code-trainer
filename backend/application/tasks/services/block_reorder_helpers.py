"""Block-reorder pure helpers (no DB, no side effects)."""
from __future__ import annotations

import random
from typing import Any

from shared.enums import AssignmentType, Difficulty, TaskType
from domain.entities.tasks.block_reorder_task import BlockReorderTask as BlockReorderTaskEntity


def is_build_from_blocks_task_type(raw: str) -> bool:
    try:
        return AssignmentType.parse(raw) == AssignmentType.TASK_BUILD_FROM_BLOCKS
    except ValueError:
        return raw in {"block_reorder", "code_assembly"}


_is_build_from_blocks_task_type = is_build_from_blocks_task_type


def parse_difficulty(raw: str) -> Difficulty:
    normalized = str(raw or "easy").strip().lower()
    try:
        return Difficulty(normalized)
    except ValueError:
        return Difficulty.EASY


def _decode_newlines(text: str | None) -> str:
    value = str(text or "")
    return value.replace("\r\n", "\n").replace("\\n", "\n").replace("`n", "\n")


def normalize_code_blocks(original_code: str) -> list[str]:
    lines = [line.rstrip("\n") for line in _decode_newlines(original_code).splitlines()]
    return [line for line in lines if line.strip()]


def build_shuffled_blocks(original_code: str) -> tuple[list[str], list[int]]:
    ordered_blocks = normalize_code_blocks(original_code)
    indexed_blocks = list(enumerate(ordered_blocks))
    random.shuffle(indexed_blocks)
    blocks = [line for _, line in indexed_blocks]
    correct_order = [original_idx for original_idx, _ in indexed_blocks]
    return blocks, correct_order


def autogenerate_test_cases(*, language: str, canonical_code: str) -> list[dict[str, str]]:
    """Placeholder — probe execution runs via async job at task publish time."""
    _ = language, canonical_code
    return [{"name": "Case 1", "inputs": "", "output": ""}]


def build_entity_from_db(task, relation) -> BlockReorderTaskEntity:
    """Map Task + block_reorder_task ORM rows to domain entity."""
    difficulty = parse_difficulty(str(getattr(task, "difficulty", None) or "easy"))
    raw_type = str(getattr(task, "task_type", None) or TaskType.BLOCK_REORDER.value)
    try:
        task_type = TaskType(raw_type)
    except ValueError:
        task_type = TaskType.BLOCK_REORDER

    return BlockReorderTaskEntity(
        id=getattr(task, "id", None),
        teacher_id=int(getattr(task, "teacher_id", None) or 0),
        title=str(getattr(task, "title", None) or ""),
        description=str(getattr(task, "description", None) or ""),
        difficulty=difficulty,
        task_type=task_type,
        original_code=str(getattr(relation, "original_code", None) or ""),
        template=getattr(relation, "template", None),
        blocks=list(getattr(relation, "blocks", None) or []),
        correct_order=list(getattr(relation, "correct_order", None) or []),
        language=str(getattr(relation, "language", None) or ""),
        language_variants=dict(getattr(relation, "language_variants", None) or {}),
        constructions=[],
    )


def build_canonical_code(
    entity: BlockReorderTaskEntity,
    *,
    language: str | None = None,
) -> str:
    """Reference solution text for probes / test-case generation."""
    requested = str(language or entity.language or "").lower()
    primary = str(entity.language or "").lower()
    original = _decode_newlines(entity.original_code or "").strip()
    if original and (not requested or requested == primary):
        return original
    variant = entity._get_variant(language)
    order = list(variant.get("correct_order") or [])
    if not order:
        return ""
    return entity.build_code(order, language)


def infer_indents_from_original(entity: BlockReorderTaskEntity, *, language: str | None) -> list[int]:
    variant = entity._get_variant(language)
    template = variant.get("template") or entity.template
    correct_order = list(variant.get("correct_order") or [])
    if template or not correct_order:
        return [0] * len(correct_order)
    original_lines = [
        line for line in _decode_newlines(entity.original_code or "").splitlines() if line.strip()
    ]
    indent_by_line: dict[str, list[int]] = {}
    for line in original_lines:
        stripped = line.lstrip(" \t")
        if not stripped:
            continue
        leading = line[: len(line) - len(stripped)]
        indent_by_line.setdefault(stripped, []).append(len(leading))

    indents: list[int] = []
    for block_index in correct_order:
        block = entity.blocks[block_index] if block_index < len(entity.blocks) else ""
        stripped = block.lstrip(" \t")
        candidates = indent_by_line.get(stripped, [0])
        indents.append(candidates[0] if candidates else 0)
    return indents
