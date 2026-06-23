"""Reference / starter C# code for C# Course v1."""
from __future__ import annotations

from typing import Any

from application.curriculum.csharp.catalog.csharp_known_language import (
    build_known_language_variants,
    code_examples_from_variants,
)

_FALLBACK = "Console.WriteLine(\"demo\");"


def reference_solution_for_slot(slot_id: str, *, slot_pattern_id: str | None = None) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_reference_code,
        is_algo_syntax_slot,
        resolve_slot_pattern_key,
    )

    if is_algo_syntax_slot(slot_id):
        ref = algo_reference_code(slot_id, "csharp", slot_pattern_id=slot_pattern_id)
        if ref:
            return ref
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code

        pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
        code = get_reference_code(slot_id, "csharp", pattern_key=pattern)
        if code:
            return code
    except ImportError:
        pass
    return _FALLBACK


def debug_starter_for_slot(slot_id: str) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_starter,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        starter = algo_debug_starter(slot_id, "csharp")
        if starter:
            return starter
    return reference_solution_for_slot(slot_id)


def build_task_extra(row: tuple) -> dict[str, Any]:
    slot_id, _chapter, _title, fmt, _action, pattern, goal, features, _diff, _legacy = row
    _cs = reference_solution_for_slot(slot_id)
    _py = "print('demo')"
    _pas = "writeln('demo');"
    _java = "System.out.println(\"demo\");"
    _cpp = "std::cout << \"demo\" << std::endl;"
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code
        _py = get_reference_code(slot_id, "python") or _py
        _pas = get_reference_code(slot_id, "pascal") or _pas
        _java = get_reference_code(slot_id, "java") or _java
        _cpp = get_reference_code(slot_id, "cpp") or _cpp
    except ImportError:
        pass
    variants = build_known_language_variants(python=_py, pascal=_pas, java=_java, cpp=_cpp)
    extra: dict[str, Any] = {
        "slot_pattern_id": pattern,
        "task_format": fmt,
        "csharp_features": features,
        "educational_goal": goal,
        "expected_concept_ids": [],
        "known_language_variants": variants,
    }
    from application.curriculum.content.algo_syntax_showcase_meta import (
        attach_expected_concepts_to_extra,
    )
    from application.curriculum.content.algo_syntax_task_extra import is_algo_syntax_slot
    if is_algo_syntax_slot(slot_id):
        extra = attach_expected_concepts_to_extra(
            extra,
            slot_id=slot_id,
            slot_pattern_id=pattern,
        )
    if fmt in {"исправление", "поиск_ошибки"}:
        extra["starter_csharp"] = debug_starter_for_slot(slot_id)
        extra["reference_csharp"] = _cs
    elif fmt.startswith("перевод"):
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_translation_starter,
            is_algo_syntax_slot,
        )

        extra["source_language"] = "python"
        extra["source_code"] = variants["python"]["source_code"]
        extra["reference_csharp"] = _cs
        extra["starter_csharp"] = (
            algo_translation_starter(slot_id, "csharp")
            if is_algo_syntax_slot(slot_id)
            else _cs
        )
    elif fmt.startswith("сборка"):
        from application.curriculum.content.v4_assembly_extra import apply_v4_assembly_extra

        apply_v4_assembly_extra(
            extra,
            slot_id=slot_id,
            language="csharp",
            task_format=fmt,
            reference_code=_cs,
        )
    extra["concept_patterns"] = ["assign"]
    return extra


def attach_csharp_code_examples(
    examples: dict[str, Any], slot_id: str, extra: dict[str, Any]
) -> dict[str, Any]:
    merged = dict(examples or {})
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        merged.update(code_examples_from_variants(variants))
    starter = str(extra.get("starter_csharp") or "").strip()
    ref = str(extra.get("reference_csharp") or reference_solution_for_slot(slot_id)).strip()
    if starter:
        merged["csharp"] = starter
    elif ref:
        merged["csharp"] = ref
    return merged
