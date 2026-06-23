"""List showcase tasks for a language/collection (index, DB scan, catalog mirror fallback)."""

from __future__ import annotations

from typing import Any, Callable

from application.curriculum.display.chapter_task_display_order import effective_display_order
from application.curriculum.mirror.pedagogical_task_store import (
    iter_showcase_tasks,
    resolve_unified_task_for_mirror_attach,
    resolved_showcase,
    showcase_matches_collection,
    track_slug,
)
from application.curriculum.showcase.showcase_task_index import get_showcase_task_index
from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService


def resolve_showcase_row_metadata(
    *,
    showcase: dict[str, Any],
    language: str,
    primary: dict[str, Any] | None,
) -> dict[str, Any]:
    resolved = resolved_showcase(showcase, language)

    def _pick(field: str) -> Any:
        if primary and primary.get(field) is not None:
            return primary.get(field)
        return resolved.get(field) or showcase.get(field)

    action = (
        showcase.get("primary_action")
        or resolved.get("primary_action")
        or (primary.get("action") if primary else None)
    )
    return {
        "learning_concept_id": _pick("learning_concept_id"),
        "technical_concept_id": _pick("technical_concept_id"),
        "exercise_pattern_id": _pick("exercise_pattern_id"),
        "action": action,
    }


def build_showcase_collection_task_row(
    *,
    row: Any,
    showcase: dict[str, Any],
    language: str,
    collection_key: str,
    primary: dict[str, Any] | None,
) -> dict[str, Any]:
    meta = resolve_showcase_row_metadata(showcase=showcase, language=language, primary=primary)
    resolved = resolved_showcase(showcase, language)
    slug = track_slug(showcase, language) or str(resolved.get("slug") or showcase.get("slug") or "")
    return {
        "task_id": row.id,
        "title": row.title,
        "task_type": row.task_type,
        "difficulty": row.difficulty,
        "slug": slug,
        "collection_key": showcase.get("collection_key") or collection_key,
        "has_primary_link": primary is not None,
        "language": language,
        "display_order": effective_display_order(showcase),
        **meta,
    }


def _rows_from_showcase_scan(
    session,
    *,
    language: str,
    collection_key: str,
    group: str,
) -> list[dict[str, Any]]:
    matched: list[tuple[Any, dict[str, Any]]] = []
    for row, showcase in iter_showcase_tasks(session):
        if showcase_matches_collection(
            showcase,
            language=language,
            collection_key=collection_key,
            group=group,
        ):
            matched.append((row, showcase))

    from application.curriculum.showcase.showcase_row_dedupe import dedupe_showcase_task_rows
    from application.curriculum.course_scope import filter_showcase_matches_in_scope

    matched = filter_showcase_matches_in_scope(matched)
    matched = dedupe_showcase_task_rows(matched, language=language)

    link_service = TaskCurriculumLinkService(session)
    primary_by_task = link_service.get_primary_links_by_task_ids(
        [row.id for row, _ in matched],
        language=language,
    )

    rows: list[dict[str, Any]] = []
    for row, showcase in matched:
        primary = primary_by_task.get(row.id)
        payload = build_showcase_collection_task_row(
            row=row,
            showcase=showcase,
            language=language,
            collection_key=collection_key,
            primary=primary,
        )
        payload["title"] = str(row.title or "")
        rows.append(payload)
    return rows


def _rows_from_catalog_specs(
    session,
    *,
    language: str,
    collection_key: str,
    specs: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[int] = set()
    for rec in specs:
        slug = str(rec.get("slug") or rec.get("slot_id") or "").strip()
        mirror = str(rec.get("pascal_mirror") or "").strip()
        row = None
        if mirror:
            row = resolve_unified_task_for_mirror_attach(
                session,
                mirror_slug=mirror,
                target_slug=slug,
            )
        if row is None and slug:
            from application.curriculum.mirror.pedagogical_task_store import find_showcase_task_by_track_slug

            row = find_showcase_task_by_track_slug(session, slug, language=language)
        if row is None or row.id in seen:
            continue
        seen.add(row.id)
        rows.append(
            {
                "task_id": row.id,
                "slug": slug,
                "title": str(rec.get("title") or row.title or ""),
                "task_type": row.task_type,
                "difficulty": str(rec.get("difficulty") or row.difficulty or "easy"),
                "collection_key": collection_key,
                "learning_concept_id": None,
                "technical_concept_id": rec.get("technical_concept_id"),
                "action": rec.get("primary_action"),
                "exercise_pattern_id": rec.get("exercise_pattern_id"),
                "has_primary_link": False,
                "language": language,
            }
        )
    return rows


def align_rows_to_catalog_specs(
    rows: list[dict[str, Any]],
    catalog_specs: tuple[dict[str, Any], ...] | None,
) -> list[dict[str, Any]]:
    """Keep only catalog slugs in catalog order (drops stale mirror/expansion duplicates)."""
    if not catalog_specs:
        return rows
    by_slug: dict[str, dict[str, Any]] = {}
    for row in rows:
        slug = str(row.get("slug") or row.get("slot_id") or "").strip()
        if slug:
            by_slug.setdefault(slug, row)
    aligned: list[dict[str, Any]] = []
    for spec in catalog_specs:
        slug = str(spec.get("slug") or spec.get("slot_id") or "").strip()
        if slug in by_slug:
            aligned.append(by_slug[slug])
    return aligned if aligned else rows


def list_showcase_tasks_for_tracked_language(
    session,
    language: str,
    collection_key: str,
    *,
    curriculum_version: str = "1.0",
    showcase_group: Callable[[str], str],
    catalog_specs: tuple[dict[str, Any], ...] | None = None,
) -> list[dict[str, Any]]:
    lang = str(language or "").strip().lower()
    version = str(curriculum_version)

    if catalog_specs:
        group = showcase_group(collection_key)
        rows = align_rows_to_catalog_specs(
            _rows_from_showcase_scan(
                session,
                language=lang,
                collection_key=collection_key,
                group=group,
            ),
            catalog_specs,
        )
        if rows:
            return rows

    index = get_showcase_task_index()
    if index is not None:
        cached = index.list_for_collection(lang, collection_key, curriculum_version=version)
        if cached:
            rows = align_rows_to_catalog_specs(list(cached), catalog_specs)
            if rows:
                return rows

    group = showcase_group(collection_key)
    rows = _rows_from_showcase_scan(
        session,
        language=lang,
        collection_key=collection_key,
        group=group,
    )
    rows = align_rows_to_catalog_specs(rows, catalog_specs)
    if rows:
        return rows

    if catalog_specs:
        return _rows_from_catalog_specs(
            session,
            language=lang,
            collection_key=collection_key,
            specs=catalog_specs,
        )
    return []
