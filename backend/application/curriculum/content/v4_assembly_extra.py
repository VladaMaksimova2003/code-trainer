"""Shared assembly extras for language content modules."""

from __future__ import annotations

from typing import Any


def apply_v4_assembly_extra(
    extra: dict[str, Any],
    *,
    slot_id: str,
    language: str,
    task_format: str,
    reference_code: str,
) -> dict[str, Any]:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_assembly_payload,
        algo_expected_concepts,
        algo_multilingual_assembly,
        algo_test_cases,
        is_algo_syntax_slot,
    )
    from application.curriculum.content.v4_assembly_builder import (
        build_multilingual_assembly_variants,
        primary_assembly_extra,
    )

    fmt = str(task_format or "")
    lang = str(language or "python").lower()

    if is_algo_syntax_slot(slot_id):
        asm_orig, asm_tpl, asm_blocks, asm_order = algo_assembly_payload(
            slot_id,
            lang,
            task_format=fmt,
        )
        extra["original_code"] = asm_orig
        extra["template"] = asm_tpl
        extra["blocks"] = asm_blocks
        extra["correct_order"] = asm_order
        extra["language"] = lang
        cases = algo_test_cases(slot_id)
        if cases:
            extra["test_cases"] = cases
        concepts = algo_expected_concepts(slot_id, lang)
        if concepts:
            extra["expected_concept_ids"] = concepts
        extra["language_variants"] = algo_multilingual_assembly(slot_id, task_format=fmt)
        return extra

    asm = primary_assembly_extra(
        slot_id,
        lang,
        task_format=fmt,
        reference_code=reference_code,
    )
    extra.update(asm)
    extra["language"] = lang
    variants = build_multilingual_assembly_variants(slot_id, task_format=fmt)
    if variants:
        extra["language_variants"] = variants
    return extra
