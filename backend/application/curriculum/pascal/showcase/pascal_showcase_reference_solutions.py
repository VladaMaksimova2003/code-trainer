"""Reference solutions for unified Pascal showcase collections."""

from __future__ import annotations

from application.curriculum.pascal.legacy.conditions.conditions_showcase_reference_solutions import (
    BLOCK_REORDER_SOLUTIONS as LEGACY_CONDITIONS_BLOCK_REORDER_SOLUTIONS,
)
from application.curriculum.pascal.legacy.conditions.conditions_showcase_reference_solutions import (
    REFERENCE_SOLUTIONS as LEGACY_CONDITIONS_REFERENCE_SOLUTIONS,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_reference_solutions import (
    BLOCK_REORDER_SOLUTIONS as LEGACY_LOOPS_BLOCK_REORDER_SOLUTIONS,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_reference_solutions import (
    REFERENCE_SOLUTIONS as LEGACY_LOOPS_REFERENCE_SOLUTIONS,
)
from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs


def _extract_reference_solutions() -> tuple[dict[str, str], dict[str, dict]]:
    reference_solutions: dict[str, str] = {}
    block_reorder_solutions: dict[str, dict] = {}

    for specs in all_pascal_showcase_specs().values():
        for spec in specs:
            extra = spec.extra or {}
            if spec.builder_key == "block_reorder_pascal":
                order = extra.get("correct_order")
                if isinstance(order, list):
                    payload: dict[str, object] = {"order": list(order)}
                    assembled_code = extra.get("original_code")
                    if isinstance(assembled_code, str) and assembled_code.strip():
                        payload["assembled_code"] = assembled_code
                    block_reorder_solutions[spec.slug] = payload
                continue

            # E2E-validated tasks (translation/io/debug) should have a reference Pascal solution.
            solution = extra.get("reference_solution_pascal")
            if isinstance(solution, str) and solution.strip():
                reference_solutions[spec.slug] = solution
                continue

            # Legacy analyze-style tasks may store solution directly in code_examples_pascal.
            fallback = extra.get("code_examples_pascal")
            if isinstance(fallback, str) and fallback.strip():
                reference_solutions[spec.slug] = fallback

    # Ensure full E2E coverage for legacy seeded collections.
    reference_solutions = {
        **LEGACY_LOOPS_REFERENCE_SOLUTIONS,
        **LEGACY_CONDITIONS_REFERENCE_SOLUTIONS,
        **reference_solutions,
    }
    block_reorder_solutions = {
        **LEGACY_LOOPS_BLOCK_REORDER_SOLUTIONS,
        **LEGACY_CONDITIONS_BLOCK_REORDER_SOLUTIONS,
        **block_reorder_solutions,
    }

    return reference_solutions, block_reorder_solutions


REFERENCE_SOLUTIONS, BLOCK_REORDER_SOLUTIONS = _extract_reference_solutions()


