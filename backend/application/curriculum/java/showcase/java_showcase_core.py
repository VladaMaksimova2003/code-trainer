"""Seed / attach Java language tracks to Universal Core tasks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.java.catalog.java_v311_content import attach_java_code_examples
from application.curriculum.java.showcase.java_v311_registry import (
    v311_collection_by_key,
    v311_showcase_group,
)
from application.curriculum.java.showcase.java_v311_showcase_all_specs import (
    all_java_v311_showcase_specs,
)
from application.curriculum.mirror.pedagogical_task_store import (
    attach_unified_showcase_meta,
    find_showcase_task_by_track_slug,
    resolve_unified_task_for_mirror_attach,
    track_slug,
)
from application.curriculum.showcase.showcase_collection_tasks import (
    list_showcase_tasks_for_tracked_language,
)
from infrastructure.db.models.task.task import Task as TaskModel

LANGUAGE = "java"


@dataclass
class JavaSeedReport:
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
        "concept_patterns": [str(rec["technical_concept_id"])] if rec["technical_concept_id"] else ["assign"],
        "primary_action": rec.get("primary_action"),
        "task_format": extra.get("task_format"),
        "java_features": extra.get("java_features"),
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


def _attach_track(session: Session, row: TaskModel, rec: dict[str, Any], report: JavaSeedReport) -> None:
    slug = str(rec["slug"])
    attach_unified_showcase_meta(row, _showcase_meta(rec), LANGUAGE)
    examples = attach_java_code_examples(dict(row.code_examples or {}), slug, rec.get("extra") or {})
    row.code_examples = examples
    flag_modified(row, "code_examples")
    report.attached.append(slug)


def seed_java_collection(
    session: Session,
    collection_key: str,
    specs: tuple[dict[str, Any], ...],
    *,
    teacher_id: int | None = None,
) -> JavaSeedReport:
    report = JavaSeedReport(collection_key=collection_key)

    for rec in specs:
        slug = str(rec.get("slug") or "")
        pascal_mirror = str(rec.get("pascal_mirror") or "").strip()

        if pascal_mirror:
            row = resolve_unified_task_for_mirror_attach(
                session,
                mirror_slug=pascal_mirror,
                target_slug=slug,
            )
            if row is None:
                report.errors.append(f"{slug}: unified task missing for {pascal_mirror}")
                continue
            existing_slug = track_slug(
                dict((row.code_examples or {}).get("curriculum_showcase") or {}), LANGUAGE
            )
            if existing_slug == slug:
                report.skipped.append(f"attached:{slug}")
                continue
            _attach_track(session, row, rec, report)
        else:
            existing = find_showcase_task_by_track_slug(session, slug, language=LANGUAGE)
            if existing is not None:
                _attach_track(session, existing, rec, report)
                report.skipped.append(f"refresh:{slug}")
                continue
            report.errors.append(f"{slug}: no pascal_mirror and no existing task")

    session.flush()
    return report


_JAVA_COLLECTION_CACHE: dict[str, list[dict[str, Any]]] | None = None


def list_java_tasks_for_collection(session: Session, collection_key: str) -> list[dict[str, Any]]:
    global _JAVA_COLLECTION_CACHE
    if _JAVA_COLLECTION_CACHE is None:
        _JAVA_COLLECTION_CACHE = {}
    if collection_key not in _JAVA_COLLECTION_CACHE:
        specs = all_java_v311_showcase_specs().get(collection_key, ())
        _JAVA_COLLECTION_CACHE[collection_key] = list_showcase_tasks_for_tracked_language(
            session,
            LANGUAGE,
            collection_key,
            curriculum_version="1.0",
            showcase_group=v311_showcase_group,
            catalog_specs=specs,
        )
    return list(_JAVA_COLLECTION_CACHE[collection_key])
