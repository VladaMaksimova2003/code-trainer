"""MPLT submit profile — pattern bindings + mirror context for post-submit feedback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from application.curriculum.content.algo_syntax_task_extra import algo_implementation
from application.curriculum.display.mplt_pattern_bindings import get_mplt_pattern_binding
from application.curriculum.display.pitfall_catalog import PitfallSpec, get_pitfall
from application.tasks.services.catalog.task_catalog_orchestrator import (
    get_task_mirror_context,
    get_task_pattern_key,
)
from application.tasks.use_cases.debug_code_keys import buggy_code_key


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _load_buggy_code_from_task(
    db: Session,
    task_id: int,
    *,
    target_language: str,
) -> str:
    from infrastructure.db.models.task import Task as TaskModel

    row = db.get(TaskModel, task_id)
    if row is None:
        return ""
    raw_examples = row.code_examples
    if not isinstance(raw_examples, dict):
        return ""
    key = buggy_code_key(_normalize_lang(target_language))
    return str(raw_examples.get(key) or raw_examples.get("buggy_code") or "").strip()


@dataclass(frozen=True)
class MpltSubmitProfile:
    pattern_key: str
    dominant_pitfall_id: str | None
    pitfall_ids: tuple[str, ...]
    debug_id: str | None
    transfer_category: str
    pitfall: PitfallSpec | None
    source_language: str
    target_language: str
    buggy_code: str

    @property
    def pitfall_transfer_type(self) -> str:
        if not self.pitfall:
            return ""
        return str(self.pitfall.get("transfer_type") or "").upper()

    @property
    def pitfall_concept_ids(self) -> list[str]:
        from application.curriculum.display.pitfall_catalog import get_pitfall

        concept_ids: list[str] = []
        for pid in self.pitfall_ids:
            spec = get_pitfall(str(pid))
            if not spec:
                continue
            for item in spec.get("concept_ids") or []:
                cid = str(item).strip()
                if cid and cid not in concept_ids:
                    concept_ids.append(cid)
        return concept_ids


def resolve_mplt_submit_profile(
    db: Session,
    task_id: int,
    *,
    submission_language: str,
) -> MpltSubmitProfile | None:
    pattern_key = get_task_pattern_key(db, task_id) or ""
    if not pattern_key:
        return None

    from application.curriculum.display.chapter1_algo_basics_pitfalls import (
        is_chapter1_pattern,
        resolve_chapter1_pitfall_ids,
    )
    from application.curriculum.display.chapter2_branches_pitfalls import (
        is_chapter2_pattern,
        resolve_chapter2_pitfall_ids,
    )
    from application.curriculum.display.chapter3_loops_pitfalls import (
        is_chapter3_pattern,
        resolve_chapter3_pitfall_ids,
    )
    from application.curriculum.display.chapter4_arrays_pitfalls import (
        is_chapter4_pattern,
        resolve_chapter4_pitfall_ids,
    )
    from application.curriculum.display.chapter5_strings_pitfalls import (
        is_chapter5_pattern,
        resolve_chapter5_pitfall_ids,
    )

    binding = get_mplt_pattern_binding(pattern_key) or {}
    dominant = binding.get("dominant_pitfall_id")
    debug_id = binding.get("debug_id")
    transfer_category = str(binding.get("transfer_category") or "TCC").upper()

    ctx = get_task_mirror_context(db, task_id, submission_language=submission_language) or {}
    target = _normalize_lang(str(ctx.get("target_language") or submission_language or "pascal"))
    source = _normalize_lang(str(ctx.get("source_language") or "python"))

    pitfall_id_list: list[str] = []
    if is_chapter1_pattern(pattern_key) and source != target:
        pitfall_id_list = resolve_chapter1_pitfall_ids(
            pattern_key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter2_pattern(pattern_key) and source != target:
        pitfall_id_list = resolve_chapter2_pitfall_ids(
            pattern_key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter3_pattern(pattern_key) and source != target:
        pitfall_id_list = resolve_chapter3_pitfall_ids(
            pattern_key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter4_pattern(pattern_key) and source != target:
        pitfall_id_list = resolve_chapter4_pitfall_ids(
            pattern_key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter5_pattern(pattern_key) and source != target:
        pitfall_id_list = resolve_chapter5_pitfall_ids(
            pattern_key,
            source_language=source,
            target_language=target,
        )
    elif dominant:
        pitfall_id_list = [str(dominant).strip()]

    primary = pitfall_id_list[0] if pitfall_id_list else None
    pitfall: PitfallSpec | None = get_pitfall(str(primary)) if primary else None

    impl = algo_implementation("", target, slot_pattern_id=pattern_key)
    db_buggy = _load_buggy_code_from_task(db, task_id, target_language=target)
    catalog_buggy = str(impl.get("buggy_code") or "").strip()
    buggy_code = db_buggy or catalog_buggy

    return MpltSubmitProfile(
        pattern_key=pattern_key,
        dominant_pitfall_id=str(primary).strip() if primary else None,
        pitfall_ids=tuple(pitfall_id_list),
        debug_id=str(debug_id).strip() if debug_id else None,
        transfer_category=transfer_category,
        pitfall=pitfall,
        source_language=source,
        target_language=target,
        buggy_code=buggy_code,
    )


def profile_to_dict(profile: MpltSubmitProfile | None) -> dict[str, Any]:
    if not profile:
        return {}
    return {
        "pattern_key": profile.pattern_key,
        "dominant_pitfall_id": profile.dominant_pitfall_id,
        "pitfall_ids": list(profile.pitfall_ids),
        "debug_id": profile.debug_id,
        "transfer_category": profile.transfer_category,
        "pitfall_transfer_type": profile.pitfall_transfer_type,
        "source_language": profile.source_language,
        "target_language": profile.target_language,
    }
