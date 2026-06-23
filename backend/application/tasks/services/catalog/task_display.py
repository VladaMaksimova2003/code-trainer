"""Human-readable task titles for teacher lists and analytics."""

from __future__ import annotations

from typing import Any

from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.mirror.curriculum_slot_mirror import canonical_title_for_slot
from application.curriculum.mirror.pedagogical_task_store import pedagogical_slot_id_from_showcase


def _showcase_dict(code_examples: dict[str, Any] | None) -> dict[str, Any]:
    raw = (code_examples or {}).get("curriculum_showcase")
    return dict(raw) if isinstance(raw, dict) else {}


def display_title_for_task(
    title: str,
    code_examples: dict[str, Any] | None = None,
) -> str:
    """Canonical curriculum title or seed-prefix-stripped fallback."""
    examples = dict(code_examples or {})
    if examples.get("teacher_assembly_override"):
        return strip_showcase_title_prefix(str(title or ""))
    showcase = _showcase_dict(code_examples)
    if showcase:
        ped = pedagogical_slot_id_from_showcase(showcase)
        slot = ped or showcase.get("slot_id") or showcase.get("slug")
        canonical = canonical_title_for_slot(str(slot) if slot else None)
        if canonical:
            return canonical
    return strip_showcase_title_prefix(str(title or ""))


def display_title_for_task_model(task: Any) -> str:
    return display_title_for_task(
        str(getattr(task, "title", "") or ""),
        getattr(task, "code_examples", None),
    )
