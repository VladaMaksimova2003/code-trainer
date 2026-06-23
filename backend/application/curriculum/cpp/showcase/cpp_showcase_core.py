"""Seed / attach C++ language tracks to Universal Core tasks."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.cpp.catalog.cpp_v311_content import (
    attach_cpp_code_examples,
    build_task_extra,
    reference_solution_for_slot,
)
from application.curriculum.cpp.showcase.cpp_v311_registry import v311_collection_by_key, v311_showcase_group
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from application.curriculum.mirror.pedagogical_task_store import (
    attach_unified_showcase_meta,
    find_showcase_task_by_track_slug,
    iter_showcase_tasks,
    resolve_unified_task_for_mirror_attach,
    resolved_showcase,
    showcase_matches_collection,
    track_slug,
)
from application.curriculum.task_curriculum_link_service import (
    TaskCurriculumLinkService,
    validate_task_curriculum_link_metadata,
)
from application.tasks.services.task_id_allocator import allocate_next_task_id
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask as TranslationTaskModel

LANGUAGE = "cpp"
_LINK_LANGUAGES: tuple[str, ...] = ("cpp", "pascal", "python")


def _resolve_cpp_link_pattern(
    technical_concept_id: str,
    primary_action: str,
    preferred: str,
) -> str:
    if preferred:
        for lang in _LINK_LANGUAGES:
            try:
                validate_task_curriculum_link_metadata(lang, technical_concept_id, preferred)
                return preferred
            except Exception:
                continue
    action = (primary_action or "implement").strip().lower()
    for lang in _LINK_LANGUAGES:
        try:
            bundle = CurriculumService(lang).get_bundle()
        except Exception:
            continue
        mask = bundle.action_masks.get(technical_concept_id)
        if mask is None:
            continue
        allowed = set(mask.patterns_for_action(action))
        if allowed:
            return sorted(allowed)[0]
        for fallback in ("implement", "debug", "translate", "assemble"):
            if fallback == action:
                continue
            allowed = set(mask.patterns_for_action(fallback))
            if allowed:
                return sorted(allowed)[0]
    return preferred


def _prepare_rec_for_seed(rec: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(rec)
    pattern = _resolve_cpp_link_pattern(
        str(rec["technical_concept_id"]),
        str(rec.get("primary_action") or ""),
        str(rec.get("exercise_pattern_id") or ""),
    )
    prepared["exercise_pattern_id"] = pattern
    extra = dict(prepared.get("extra") or {})
    extra["exercise_pattern_id"] = pattern
    prepared["extra"] = extra
    return prepared


@dataclass
class CppSeedReport:
    collection_key: str
    attached: list[str] = field(default_factory=list)
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "collection_key": self.collection_key,
            "attached": self.attached,
            "created": self.created,
            "skipped": self.skipped,
            "errors": self.errors,
            "totals": {
                "attached": len(self.attached),
                "created": len(self.created),
                "skipped": len(self.skipped),
                "errors": len(self.errors),
            },
        }


def _concept_patterns(technical_concept_id: str) -> list[str]:
    return [technical_concept_id] if technical_concept_id else ["assign"]


def _showcase_meta(rec: dict[str, Any]) -> dict[str, Any]:
    extra = rec.get("extra") or {}
    col = v311_collection_by_key(str(rec["collection_key"]))
    meta: dict[str, Any] = {
        "group": v311_showcase_group(str(rec["collection_key"])),
        "collection_key": rec["collection_key"],
        "slug": rec["slug"],
        "slot_id": rec["slot_id"],
        "technical_concept_id": rec["technical_concept_id"],
        "exercise_pattern_id": rec["exercise_pattern_id"],
        "curriculum_version": "1.0",
        "target_language": LANGUAGE,
        "language": LANGUAGE,
        "concept_patterns": _concept_patterns(str(rec["technical_concept_id"])),
        "primary_action": rec.get("primary_action"),
        "task_format": extra.get("task_format"),
        "cpp_features": extra.get("cpp_features"),
        "expected_concept_ids": extra.get("expected_concept_ids") or [],
        "educational_goal": extra.get("educational_goal") or rec.get("description"),
        "short_instruction": extra.get("educational_goal") or rec.get("description"),
        "title": rec.get("title"),
        "display_title": rec.get("title"),
    }
    if col is not None:
        meta["collection_id"] = col.collection_id
    slot_pattern = extra.get("slot_pattern_id")
    if slot_pattern:
        meta["slot_pattern_id"] = slot_pattern
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        meta["known_language_variants"] = variants
    return meta


def _attach_cpp_track(session: Session, row: TaskModel, rec: dict[str, Any], report: CppSeedReport) -> None:
    slug = str(rec["slug"])
    track = _showcase_meta(rec)
    attach_unified_showcase_meta(row, track, LANGUAGE)
    examples = attach_cpp_code_examples(dict(row.code_examples or {}), slug, rec.get("extra") or {})
    row.code_examples = examples
    flag_modified(row, "code_examples")
    report.attached.append(slug)


def _create_cpp_only_task(
    session: Session,
    rec: dict[str, Any],
    *,
    teacher_id: int | None,
    report: CppSeedReport,
) -> None:
    slug = str(rec["slug"])
    extra = rec.get("extra") or {}
    starter = str(extra.get("starter_cpp") or reference_solution_for_slot(slug)).strip()
    task_id = allocate_next_task_id(session)
    session.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=teacher_id,
            title=str(rec["title"]),
            description=str(rec.get("description") or ""),
            difficulty=str(rec.get("difficulty") or "easy"),
            task_type=str(rec.get("assignment_type") or "task_translate_full_program"),
            test_cases=[],
            code_examples={"cpp": starter},
            flow_spec={"target_language": LANGUAGE},
        )
    )
    session.execute(
        sa.insert(TranslationTaskModel.__table__).values(
            task_id=task_id,
            source_code=str(extra.get("source_code") or ""),
            source_language=str(extra.get("source_language") or "python"),
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        report.errors.append(f"{slug}: create failed")
        return
    attach_unified_showcase_meta(row, _showcase_meta(rec), LANGUAGE)
    row.code_examples = attach_cpp_code_examples(dict(row.code_examples or {}), slug, extra)
    flag_modified(row, "code_examples")
    report.created.append(slug)


def seed_cpp_collection(
    session: Session,
    collection_key: str,
    specs: tuple[dict[str, Any], ...],
    *,
    teacher_id: int | None = None,
) -> CppSeedReport:
    report = CppSeedReport(collection_key=collection_key)
    link_service = TaskCurriculumLinkService(session)

    for raw_rec in specs:
        rec = _prepare_rec_for_seed(raw_rec)
        slug = str(rec.get("slug") or "")
        pascal_mirror = str(rec.get("pascal_mirror") or "").strip()
        try:
            link_service.validate_task_curriculum_link(
                LANGUAGE,
                str(rec["technical_concept_id"]),
                str(rec["exercise_pattern_id"]),
            )
        except Exception:
            try:
                link_service.validate_task_curriculum_link(
                    "pascal",
                    str(rec["technical_concept_id"]),
                    str(rec["exercise_pattern_id"]),
                )
            except Exception as exc:
                report.errors.append(f"{slug}: link validation: {exc}")
                continue

        if pascal_mirror:
            row = resolve_unified_task_for_mirror_attach(
                session,
                mirror_slug=pascal_mirror,
                target_slug=slug,
            )
            if row is None:
                report.errors.append(f"{slug}: unified task missing for {pascal_mirror}")
                continue
            tracks = available_language_tracks(
                dict((row.code_examples or {}).get("curriculum_showcase") or {})
            )
            if "cpp" in tracks and track_slug(
                dict((row.code_examples or {}).get("curriculum_showcase") or {}), "cpp"
            ) == slug:
                report.skipped.append(f"attached:{slug}")
                continue
            _attach_cpp_track(session, row, rec, report)
        else:
            existing = find_showcase_task_by_track_slug(session, slug, language=LANGUAGE)
            if existing is not None:
                _attach_cpp_track(session, existing, rec, report)
                report.skipped.append(f"refresh:{slug}")
                continue
            _create_cpp_only_task(session, rec, teacher_id=teacher_id, report=report)

        row = find_showcase_task_by_track_slug(session, slug, language=LANGUAGE) or (
            resolve_unified_task_for_mirror_attach(
                session,
                mirror_slug=pascal_mirror,
                target_slug=slug,
            )
            if pascal_mirror
            else None
        )
        if row is not None:
            try:
                link_service.link_task_to_curriculum(
                    row.id,
                    LANGUAGE,
                    str(rec["technical_concept_id"]),
                    str(rec["exercise_pattern_id"]),
                    is_primary=True,
                )
            except Exception:
                pass

    session.flush()
    return report


def list_cpp_tasks_for_collection(session: Session, collection_key: str) -> list[dict[str, Any]]:
    col = v311_collection_by_key(collection_key)
    if col is None:
        return []

    from application.curriculum.showcase.showcase_task_index import get_showcase_task_index

    index = get_showcase_task_index()
    if index is not None:
        cached = index.list_for_collection(LANGUAGE, collection_key, curriculum_version="1.0")
        if cached is not None:
            return cached

    group = v311_showcase_group(collection_key)
    rows: list[dict[str, Any]] = []
    for row, showcase in iter_showcase_tasks(session):
        if not showcase_matches_collection(
            showcase,
            language=LANGUAGE,
            collection_key=collection_key,
            group=group,
        ):
            continue
        resolved = resolved_showcase(showcase, LANGUAGE)
        slug = track_slug(showcase, LANGUAGE) or str(resolved.get("slug") or "")
        title = str(resolved.get("title") or row.title or "")
        rows.append(
            {
                "task_id": row.id,
                "slug": slug,
                "title": title,
                "task_type": row.task_type,
                "difficulty": row.difficulty,
                "collection_key": collection_key,
                "technical_concept_id": resolved.get("technical_concept_id"),
                "action": resolved.get("primary_action"),
                "language": LANGUAGE,
            }
        )
    return rows
