"""Reference / starter Java code for Java Course v1."""
from __future__ import annotations

from typing import Any

from application.curriculum.java.catalog.java_known_language import (
    build_known_language_variants,
    code_examples_from_variants,
)

_FALLBACK = "System.out.println(\"demo\");"


def reference_solution_for_slot(slot_id: str, *, slot_pattern_id: str | None = None) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_reference_code,
        is_algo_syntax_slot,
        resolve_slot_pattern_key,
    )

    if is_algo_syntax_slot(slot_id):
        ref = algo_reference_code(slot_id, "java", slot_pattern_id=slot_pattern_id)
        if ref:
            return ref
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code

        pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
        code = get_reference_code(slot_id, "java", pattern_key=pattern)
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
        starter = algo_debug_starter(slot_id, "java")
        if starter:
            return starter
    return reference_solution_for_slot(slot_id)


def build_task_extra(row: tuple) -> dict[str, Any]:
    slot_id, _chapter, _title, fmt, _action, pattern, goal, features, _diff, _legacy = row
    _java = reference_solution_for_slot(slot_id)
    _py = "print('demo')"
    _pas = "writeln('demo');"
    _cs = "Console.WriteLine(\"demo\");"
    _cpp = "std::cout << \"demo\" << std::endl;"
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code
        _py = get_reference_code(slot_id, "python") or _py
        _pas = get_reference_code(slot_id, "pascal") or _pas
        _cs = get_reference_code(slot_id, "csharp") or _cs
        _cpp = get_reference_code(slot_id, "cpp") or _cpp
    except ImportError:
        pass
    variants = build_known_language_variants(python=_py, pascal=_pas, csharp=_cs, cpp=_cpp)
    extra: dict[str, Any] = {
        "slot_pattern_id": pattern,
        "task_format": fmt,
        "java_features": features,
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
        extra["starter_java"] = debug_starter_for_slot(slot_id)
        extra["reference_java"] = _java
    elif fmt.startswith("перевод"):
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_translation_starter,
            is_algo_syntax_slot,
        )

        extra["source_language"] = "python"
        extra["source_code"] = variants["python"]["source_code"]
        extra["reference_java"] = _java
        extra["starter_java"] = (
            algo_translation_starter(slot_id, "java")
            if is_algo_syntax_slot(slot_id)
            else _java
        )
    elif fmt.startswith("сборка"):
        from application.curriculum.content.v4_assembly_extra import apply_v4_assembly_extra

        apply_v4_assembly_extra(
            extra,
            slot_id=slot_id,
            language="java",
            task_format=fmt,
            reference_code=_java,
        )
    extra["concept_patterns"] = ["assign"]
    return extra


def attach_java_code_examples(
    examples: dict[str, Any], slot_id: str, extra: dict[str, Any]
) -> dict[str, Any]:
    merged = dict(examples or {})
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        merged.update(code_examples_from_variants(variants))
    starter = str(extra.get("starter_java") or "").strip()
    ref = str(extra.get("reference_java") or reference_solution_for_slot(slot_id)).strip()
    if starter:
        merged["java"] = starter
    elif ref:
        merged["java"] = ref
    return merged
