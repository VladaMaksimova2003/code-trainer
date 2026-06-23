"""Seed payloads for Python Course v1 tasks."""

from __future__ import annotations

import re
from typing import Any

from application.curriculum.pascal.catalog.pascal_flowchart_diagrams import (
    diagram_if_n_pos,
    empty_diagram,
)
from application.curriculum.python.catalog.python_known_language import (
    build_known_language_variants,
    code_examples_from_variants,
)
from application.curriculum.python.catalog.python_v311_capstone_catalog import (
    capstone_reference_python,
    capstone_starter_python,
)
from application.curriculum.python.catalog.python_v311_known_code import fallback_known_code, resolve_known_codes
from application.curriculum.python.catalog.python_v311_test_case_resolver import derive_test_cases
from application.curriculum.python.catalog.python_v12_delta_content import (
    V12_ASSEMBLY,
    V12_DEBUG_STARTER,
    V12_REFERENCE,
    V12_TEST_CASES,
)

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

_PYTHON_PROGRAM = (
    "def main():\n"
    "    x = 1\n"
    "    y = x + 1\n"
    "    print(y)\n\n"
    "if __name__ == '__main__':\n"
    "    main()\n"
)

_PYTHON_SNIPPET = "x = 1\ny = x + 1\nprint(y)"

_ASSEMBLE_BLOCKS = ["x = 1", "y = x + 1", "print(y)"]
_ASSEMBLE_TEMPLATE = "def main():\n    ___\n\nif __name__ == '__main__':\n    main()"

_SLOT_REFERENCE: dict[str, str] = {
    "pyk_01": "print('Hello, World!')",
    "pyk_02": "if True:\nprint('ok')",
    "pyk_04": "if __name__ == '__main__':\n    print('start')",
    "pyt_02": "x == 1",
    "pyt_03": "x = 3.14\ny = 2.71",
    "pyt_04": "flag = True\nif flag:\n    print('yes')",
    "pyt_07": "x = 5\nassert 1 <= x <= 10",
    "pyt_08": "MAX = 100\nPI = 3.14",
    "pyt_10": "x = 7.9\nn = int(x)\nm = round(x)",
    "pyt_11": "x = 42",
    "pye_01": "result = 5 / 2",
    "pyc_01": "x = int(input())\nif x > 0:\n    print('positive')\nelse:\n    print('non-positive')",
    "pyl_01": "n = int(input())\nfor i in range(1, n + 1):\n    print(i)",
    "pyf_01": "def add(a, b):\n    return a + b",
    "pya_01": "items = [1, 2, 3]\nprint(items[0])",
    "pycmp_01": "squares = [x * x for x in range(5)]\nprint(squares[1])",
}
_SLOT_REFERENCE.update(V12_REFERENCE)
_SLOT_REFERENCE.update(capstone_reference_python())

_SLOT_DEBUG_STARTER: dict[str, str] = {
    "pyk_02": "if True:\nprint('ok')",
    "pyt_02": "x == 1\nprint(x)",
    "pyt_10": "x = 7.9\nn = x\nm = round(x)",
    "pye_01": "result = 5 / 2\nprint(result)",
    "pyl_07": "for i in range(1, n):\n    print(i)",
    "pyf_03": "def double(n):\n    n * 2",
    "pypit_04": "def add(x=[]):\n    x.append(1)\n    return x",
}
_SLOT_DEBUG_STARTER.update(V12_DEBUG_STARTER)
_SLOT_DEBUG_STARTER.update(capstone_starter_python())

_SLOT_ASSEMBLY: dict[str, tuple[str, str, list[str], list[int], list[dict[str, str]]]] = {
    "pyk_03": (
        "if __name__ == '__main__':\n    print('done')",
        "___",
        ["if __name__ == '__main__':", "    print('done')"],
        [0, 1],
        [{"inputs": "", "output": "done"}],
    ),
    "pyc_02": (
        "x = int(input())\nif x > 0:\n    print('positive')\nelse:\n    print('non-positive')",
        "___",
        [
            "x = int(input())",
            "if x > 0:",
            "    print('positive')",
            "else:",
            "    print('non-positive')",
        ],
        [0, 1, 2, 3, 4],
        [{"inputs": "5\n", "output": "positive"}],
    ),
    "pyl_01": (
        "n = int(input())\nfor i in range(1, n + 1):\n    print(i)",
        "___",
        ["n = int(input())", "for i in range(1, n + 1):", "    print(i)"],
        [0, 1, 2],
        [{"inputs": "3\n", "output": "1\n2\n3"}],
    ),
    "pyf_08": (
        "def add(a, b):\n    return a + b",
        "___",
        ["def add(a, b):", "    return a + b"],
        [0, 1],
        [],
    ),
    "pycmp_01": (
        "squares = [x * x for x in range(5)]",
        "___",
        ["squares = [", "x * x for x in range(5)", "]"],
        [0, 1, 2],
        [],
    ),
}
_SLOT_ASSEMBLY.update(V12_ASSEMBLY)


def reference_solution_for_slot(slot_id: str, *, slot_pattern_id: str | None = None) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_reference_code,
        is_algo_syntax_slot,
        resolve_slot_pattern_key,
    )

    if is_algo_syntax_slot(slot_id):
        ref = algo_reference_code(slot_id, "python", slot_pattern_id=slot_pattern_id)
        if ref:
            return ref
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code

        pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
        code = get_reference_code(slot_id, "python", pattern_key=pattern)
        if code:
            return code
    except ImportError:
        pass
    return _PYTHON_SNIPPET


def _v4_python_reference(slot_id: str) -> str:
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code

        return str(get_reference_code(slot_id, "python") or "").strip()
    except ImportError:
        return ""


def _make_variants(slot_id: str) -> dict[str, Any]:
    pascal, cpp, java, csharp = resolve_known_codes(slot_id)
    variants = build_known_language_variants(pascal=pascal, cpp=cpp, java=java, csharp=csharp)
    py_snippet = reference_solution_for_slot(slot_id)
    if py_snippet.strip():
        variants["python"] = {
            "source_code": py_snippet.strip(),
            "explanation": "Фрагмент на Python — сравните с целевым решением.",
        }
    return variants


def _known_language_extra(slot_id: str, **fields: Any) -> dict[str, Any]:
    variants = _make_variants(slot_id)
    payload: dict[str, Any] = {
        "known_language_variants": variants,
        "assemble_context": code_examples_from_variants(variants),
    }
    payload.update(fields)
    return payload


def _attach_expected_concepts(
    extra: dict[str, Any],
    *,
    slot_id: str,
    chapter_key: str,
    python_features: str,
    task_format: str,
    slot_pattern_id: str | None = None,
) -> dict[str, Any]:
    from application.curriculum.content.algo_syntax_showcase_meta import (
        attach_expected_concepts_to_extra,
    )
    from application.curriculum.content.algo_syntax_task_extra import is_algo_syntax_slot
    from application.curriculum.python.catalog.python_v311_expected_concepts import (
        expected_concept_ids_for_row,
    )

    pattern = slot_pattern_id or str(extra.get("slot_pattern_id") or "").strip() or None
    if is_algo_syntax_slot(slot_id):
        enriched = attach_expected_concepts_to_extra(
            extra,
            slot_id=slot_id,
            slot_pattern_id=pattern,
        )
        if enriched.get("expected_concepts"):
            return enriched

    extra["expected_concept_ids"] = expected_concept_ids_for_row(
        slot_id=slot_id,
        chapter_key=chapter_key,
        python_features=python_features,
        task_format=task_format,
    )
    return extra


def _reference_solution(slot_id: str, features: str) -> str:
    del features
    return reference_solution_for_slot(slot_id)


def _debug_starter(slot_id: str) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_starter,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        starter = algo_debug_starter(slot_id, "python")
        if starter:
            return starter
    if slot_id in _SLOT_DEBUG_STARTER:
        return _SLOT_DEBUG_STARTER[slot_id]
    from application.curriculum.python.catalog.python_catalog_runtime import (
        debug_starter_for_slot,
        is_v4_python_slot,
    )
    from application.curriculum.python.catalog.python_mirror_content import python_debug_starter_from_mirror

    if is_v4_python_slot(slot_id):
        ref = _v4_python_reference(slot_id)
        if ref:
            return debug_starter_for_slot(slot_id, ref)
    mirrored = python_debug_starter_from_mirror(slot_id)
    if mirrored:
        return mirrored
    return (
        "x = 1\n"
        "print(x)\n"
    )


def _debug_solution(slot_id: str) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_solution,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        fixed = algo_debug_solution(slot_id, "python")
        if fixed:
            return fixed
    return _reference_solution(slot_id, "")


def _mcq_options(slot_id: str, features: str) -> tuple[list[str], int, str]:
    del slot_id, features
    correct = "print('ok')"
    distractors = [
        "print ok",
        "if x = 1:",
        "def f(): pass;",
    ]
    return [correct, *distractors], 0, "Корректный фрагмент использует синтаксис Python."


def _task_test_cases(slot_id: str, task_format: str, row: TaskRow | None = None) -> list[dict[str, str]]:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_test_cases,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        cases = algo_test_cases(slot_id)
        if cases:
            return cases

    from application.curriculum.python.catalog.python_mirror_content import python_test_cases_from_mirror

    if slot_id in V12_TEST_CASES and V12_TEST_CASES[slot_id]:
        return V12_TEST_CASES[slot_id]
    try:
        from application.curriculum.content.v4_test_cases import get_test_cases
        v4 = get_test_cases(slot_id)
        if v4:
            return [{"inputs": inp, "output": out} for inp, out in v4]
    except ImportError:
        pass
    mirrored = python_test_cases_from_mirror(slot_id)
    if mirrored:
        return mirrored
    if row is None:
        row = (slot_id, "", "", task_format, "", "", "", "", "", "")
    return derive_test_cases(row)


def build_task_extra(row: TaskRow) -> dict[str, Any]:
    slot_id, chapter, title, task_format, _action, pattern, goal, features, _diff, _legacy = row

    ref = _reference_solution(slot_id, features)
    test_cases = _task_test_cases(slot_id, task_format, row)

    def _finalize(extra: dict[str, Any]) -> dict[str, Any]:
        return _attach_expected_concepts(
            extra,
            slot_id=slot_id,
            chapter_key=chapter,
            python_features=features,
            task_format=task_format,
            slot_pattern_id=pattern,
        )

    if task_format in {"перевод_программы", "перевод_фрагмента"}:
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_translation_starter,
            is_algo_syntax_slot,
        )

        snippet = task_format == "перевод_фрагмента"
        starter = capstone_starter_python().get(slot_id, "")
        if is_algo_syntax_slot(slot_id):
            starter = algo_translation_starter(slot_id, "python")
        translate_extra: dict[str, Any] = dict(
            reference_solution_python=ref if snippet or "def " in ref or "print" in ref else _PYTHON_PROGRAM,
            test_cases=test_cases,
            slot_pattern_id=pattern,
            educational_goal=goal,
            python_features=features,
        )
        if starter:
            translate_extra["starter_python"] = starter
        return _finalize(_known_language_extra(slot_id, **translate_extra))

    if task_format in {"исправление", "поиск_ошибки"}:
        mode = "find" if task_format == "поиск_ошибки" else "fix"
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_debug_assembly_payload,
            algo_multilingual_debug_assembly,
            is_algo_syntax_slot,
        )

        if is_algo_syntax_slot(slot_id):
            debug_asm = algo_debug_assembly_payload(slot_id, "python")
            if debug_asm:
                extra = _known_language_extra(
                    slot_id,
                    language="python",
                    original_code=debug_asm["original_code"],
                    template=debug_asm["template"],
                    blocks=debug_asm["blocks"],
                    correct_order=debug_asm["correct_order"],
                    reference_solution_python=debug_asm["reference_solution"],
                    test_cases=test_cases,
                    debug_mode=mode,
                    slot_pattern_id=pattern,
                    educational_goal=goal,
                    python_features=features,
                )
                extra["language_variants"] = algo_multilingual_debug_assembly(slot_id)
                return _finalize(extra)

        return _finalize(
            _known_language_extra(
                slot_id,
                starter_python=_debug_starter(slot_id),
                reference_solution_python=_debug_solution(slot_id),
                test_cases=test_cases,
                debug_mode=mode,
                slot_pattern_id=pattern,
                educational_goal=goal,
                python_features=features,
            )
        )

    if task_format in {"сборка_программы", "сборка_фрагмента"}:
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_assembly_payload,
            algo_multilingual_assembly,
            is_algo_syntax_slot,
        )
        from application.curriculum.content.v4_assembly_builder import build_multilingual_assembly_variants
        from application.curriculum.python.catalog.python_catalog_runtime import (
            assembly_payload_for_slot,
            is_v4_python_slot,
        )

        if is_algo_syntax_slot(slot_id):
            asm_orig, asm_tpl, asm_blocks, asm_order = algo_assembly_payload(
                slot_id,
                "python",
                task_format=task_format,
            )
            effective_tc = test_cases
            language_variants = algo_multilingual_assembly(slot_id, task_format=task_format)
        elif slot_id in _SLOT_ASSEMBLY:
            asm_orig, asm_tpl, asm_blocks, asm_order, asm_tc = _SLOT_ASSEMBLY[slot_id]
            effective_tc = test_cases or asm_tc
            language_variants = None
        elif is_v4_python_slot(slot_id):
            v4_ref = _v4_python_reference(slot_id)
            asm_orig, asm_tpl, asm_blocks, asm_order = assembly_payload_for_slot(
                slot_id,
                v4_ref or ref,
            )
            effective_tc = test_cases
            language_variants = build_multilingual_assembly_variants(slot_id, task_format=task_format) or None
        else:
            asm_orig = _PYTHON_PROGRAM if task_format == "сборка_программы" else _PYTHON_SNIPPET
            asm_tpl = _ASSEMBLE_TEMPLATE
            asm_blocks = list(_ASSEMBLE_BLOCKS)
            asm_order = list(range(len(_ASSEMBLE_BLOCKS)))
            effective_tc = test_cases
            language_variants = None

        extra = _known_language_extra(
            slot_id,
            language="python",
            original_code=asm_orig,
            template=asm_tpl,
            blocks=asm_blocks,
            correct_order=asm_order,
            reference_solution_python=ref,
            test_cases=effective_tc,
            slot_pattern_id=pattern,
            educational_goal=goal,
            python_features=features,
        )
        if language_variants:
            extra["language_variants"] = language_variants
        return _finalize(extra)

    if task_format == "выбор_фрагмента":
        options, correct_index, explanation = _mcq_options(slot_id, features)
        return _finalize(
            _known_language_extra(
                slot_id,
                mcq_prompt=goal,
                mcq_options=options,
                correct_index=correct_index,
                explanation=explanation,
                reference_solution_python=options[correct_index],
                test_cases=test_cases,
                slot_pattern_id=pattern,
                educational_goal=goal,
                python_features=features,
            )
        )

    if task_format == "код_по_блок-схеме":
        return _finalize(
            _known_language_extra(
                slot_id,
                diagram=diagram_if_n_pos(),
                reference_code_python=ref,
                expose_reference_code=False,
                flowchart_mode="flowchart_to_code",
                test_cases=test_cases,
                slot_pattern_id=pattern,
                educational_goal=goal,
                python_features=features,
            )
        )

    if task_format == "блок-схема_по_коду":
        return _finalize(
            _known_language_extra(
                slot_id,
                diagram=empty_diagram(),
                reference_code_python=ref,
                expose_reference_code=True,
                flowchart_mode="code_to_flowchart",
                flow_spec={"nodes": [], "edges": []},
                test_cases=test_cases,
                slot_pattern_id=pattern,
                educational_goal=goal,
                python_features=features,
            )
        )

    raise ValueError(f"Unsupported task_format for {slot_id}: {task_format}")
