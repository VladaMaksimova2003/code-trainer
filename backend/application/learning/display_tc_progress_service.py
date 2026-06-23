"""Progress by display TC cards (tc_display_registry.json), not raw task counts."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from application.curriculum.validation.canonical_technical_ids import canonical_technical_id
from application.curriculum.validation.technical_concept_detector import rollup_to_display_tc
from application.curriculum.validation.technical_concept_registry import list_display_tc_cards
from application.learning.skill_progress_service import (
    CURRICULUM_LANGUAGE_ORDER,
    curriculum_languages_for_task,
    normalize_curriculum_language,
)
from domain.learning.tc_skill_groups import TC_SKILL_GROUPS, display_tc_group_id
from application.tasks.services.authoring_expected_concepts import (
    resolve_authoring_expected_concept_ids,
    resolve_authoring_expected_concepts_by_language,
)


def _dedupe_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = str(item or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(key)
    return ordered


def _normalize_showcase_fields(showcase: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(showcase)
    if not str(normalized.get("slot_id") or "").strip():
        slug = str(normalized.get("slug") or "").strip()
        if slug:
            normalized["slot_id"] = slug
    if not str(normalized.get("chapter_key") or "").strip():
        chapter_key = str(normalized.get("collection_key") or "").strip()
        if chapter_key:
            normalized["chapter_key"] = chapter_key
    if not str(normalized.get("target_language") or "").strip():
        language = str(normalized.get("language") or "").strip().lower()
        if language:
            normalized["target_language"] = language
    return normalized


def _showcase_tc42_ids(showcase: dict[str, Any]) -> list[str]:
    showcase = _normalize_showcase_fields(showcase)
    explicit = showcase.get("expected_concept_ids")
    if isinstance(explicit, list) and explicit:
        raw_ids = _dedupe_preserve([str(item).strip() for item in explicit if str(item).strip()])
        if raw_ids:
            return raw_ids

    technical = str(showcase.get("technical_concept_id") or "").strip()
    if technical:
        return [technical]

    tracks = showcase.get("language_tracks")
    if isinstance(tracks, dict):
        merged: list[str] = []
        for track in tracks.values():
            if not isinstance(track, dict):
                continue
            track_ids = track.get("expected_concept_ids")
            if isinstance(track_ids, list):
                merged.extend(str(item).strip() for item in track_ids if str(item).strip())
            track_tc = str(track.get("technical_concept_id") or "").strip()
            if track_tc:
                merged.append(track_tc)
        merged = _dedupe_preserve(merged)
        if merged:
            return merged

    return _catalog_tc42_ids_from_showcase(showcase)


def _catalog_tc42_ids_from_showcase(showcase: dict[str, Any]) -> list[str]:
    showcase = _normalize_showcase_fields(showcase)
    slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    if not slot_id:
        chapter_only = str(
            showcase.get("chapter_key") or showcase.get("collection_key") or ""
        ).strip()
        if chapter_only:
            from application.curriculum.shared.algo_v128_showcase import CHAPTER_STUDY_TC

            study = CHAPTER_STUDY_TC.get(chapter_only)
            if study:
                return list(study)
        return []

    from application.curriculum.content.algo_syntax_task_extra import (
        algo_expected_concepts,
        is_algo_syntax_slot,
    )

    target_lang = str(
        showcase.get("target_language") or showcase.get("language") or ""
    ).strip().lower()

    if is_algo_syntax_slot(slot_id):
        for lang in [target_lang, "pascal", "python", "cpp", "csharp", "java"]:
            if not lang:
                continue
            concepts = algo_expected_concepts(
                slot_id,
                lang,
                slot_pattern_id=str(showcase.get("slot_pattern_id") or "") or None,
            )
            if concepts:
                return concepts

    from application.curriculum.python.catalog.python_catalog_runtime import expected_concepts_for_slot

    ids = expected_concepts_for_slot(slot_id)
    if ids:
        return list(ids)

    from application.curriculum.pascal.catalog.pascal_v311_expected_concepts import (
        expected_concepts_by_slot,
    )

    cached = expected_concepts_by_slot().get(slot_id)
    if cached:
        return list(cached)

    chapter_key = str(showcase.get("chapter_key") or showcase.get("collection_key") or "").strip()
    features = str(showcase.get("pascal_features") or showcase.get("python_features") or "").strip()
    task_format = str(showcase.get("task_format") or "")

    for resolver, kwargs in _catalog_resolvers(slot_id, chapter_key, features, task_format):
        resolved = resolver(**kwargs)
        if resolved:
            return list(resolved)

    if chapter_key:
        from application.curriculum.shared.algo_v128_showcase import CHAPTER_STUDY_TC

        study = CHAPTER_STUDY_TC.get(chapter_key)
        if study:
            return list(study)
    return []


def _catalog_resolvers(
    slot_id: str,
    chapter_key: str,
    features: str,
    task_format: str,
) -> list[tuple[Any, dict[str, Any]]]:
    from application.curriculum.cpp.catalog.cpp_v311_expected_concepts import (
        expected_concept_ids_for_row as cpp_expected,
    )
    from application.curriculum.csharp.catalog.csharp_v311_expected_concepts import (
        expected_concept_ids_for_row as csharp_expected,
    )
    from application.curriculum.java.catalog.java_v311_expected_concepts import (
        expected_concept_ids_for_row as java_expected,
    )
    from application.curriculum.pascal.catalog.pascal_v311_expected_concepts import (
        expected_concept_ids_for_row as pascal_expected,
    )
    from application.curriculum.python.catalog.python_v311_expected_concepts import (
        expected_concept_ids_for_row as python_expected,
    )

    return [
        (
            pascal_expected,
            {
                "slot_id": slot_id,
                "chapter_key": chapter_key,
                "pascal_features": features,
                "task_format": task_format,
            },
        ),
        (
            python_expected,
            {
                "slot_id": slot_id,
                "chapter_key": chapter_key,
                "python_features": features,
                "task_format": task_format,
            },
        ),
        (cpp_expected, {"slot_id": slot_id, "chapter_key": chapter_key}),
        (csharp_expected, {"slot_id": slot_id, "chapter_key": chapter_key}),
        (java_expected, {"slot_id": slot_id, "chapter_key": chapter_key}),
    ]


def resolve_tc42_ids_for_task(code_examples: dict[str, Any] | None) -> list[str]:
    """All TC42 / curriculum concept ids attached to a task (union across language tracks)."""
    examples = dict(code_examples or {})
    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        explicit = showcase.get("expected_concept_ids")
        if isinstance(explicit, list) and explicit:
            raw_ids = _dedupe_preserve(
                [str(item).strip() for item in explicit if str(item).strip()]
            )
            if raw_ids:
                return raw_ids

    by_lang = resolve_authoring_expected_concepts_by_language(examples)
    if by_lang:
        merged: list[str] = []
        for ids in by_lang.values():
            merged.extend(ids)
        return _dedupe_preserve(merged)

    stored = resolve_authoring_expected_concept_ids(examples)
    if stored:
        return list(stored)

    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        catalog_ids = _showcase_tc42_ids(showcase)
        if catalog_ids:
            return catalog_ids
    return []


def _display_tc_ids_from_concept_ids(concept_ids: Iterable[str]) -> frozenset[str]:
    display_ids: set[str] = set()
    technical: set[str] = set()
    for item in concept_ids:
        key = str(item or "").strip()
        if not key:
            continue
        if key.startswith("tc_"):
            display_ids.add(key)
            continue
        technical.add(canonical_technical_id(key))
    display_ids.update(rollup_to_display_tc(technical))
    return frozenset(display_ids)


def resolve_display_tc_ids_for_task(code_examples: dict[str, Any] | None) -> frozenset[str]:
    tc42_ids = resolve_tc42_ids_for_task(code_examples)
    if not tc42_ids:
        return frozenset()
    return _display_tc_ids_from_concept_ids(tc42_ids)


def resolve_tc42_ids_for_task_for_language(
    code_examples: dict[str, Any] | None,
    language: str,
) -> list[str]:
    """Curriculum concept ids for one language track (not union across mirrors)."""
    lang = normalize_curriculum_language(language)
    if not lang:
        return []

    examples = enrich_code_examples_for_tc_progress(code_examples)
    by_lang = resolve_authoring_expected_concepts_by_language(examples)
    if by_lang.get(lang):
        return list(by_lang[lang])

    tracks = curriculum_languages_for_task(examples)
    if tracks and lang not in tracks:
        return []

    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        explicit = showcase.get("expected_concept_ids")
        if isinstance(explicit, list) and explicit:
            primary = normalize_curriculum_language(
                str(showcase.get("target_language") or "")
            )
            if not tracks or primary == lang:
                raw_ids = _dedupe_preserve(
                    [str(item).strip() for item in explicit if str(item).strip()]
                )
                if raw_ids:
                    return raw_ids

        scoped = dict(showcase)
        scoped["target_language"] = lang
        catalog_ids = _showcase_tc42_ids(scoped)
        if catalog_ids:
            return catalog_ids

    return []


def resolve_display_tc_ids_for_task_for_language(
    code_examples: dict[str, Any] | None,
    language: str,
) -> frozenset[str]:
    tc42_ids = resolve_tc42_ids_for_task_for_language(code_examples, language)
    if not tc42_ids:
        return frozenset()
    return _display_tc_ids_from_concept_ids(tc42_ids)


def _pedagogical_progress_key(task_id: int, code_examples: dict[str, Any] | None) -> str:
    """One curriculum slot → one progress unit (mirrors task list dedupe)."""
    from application.curriculum.mirror.pedagogical_task_store import unified_pedagogical_slot_key

    showcase = (code_examples or {}).get("curriculum_showcase")
    if isinstance(showcase, dict):
        unified = unified_pedagogical_slot_key(showcase)
        if unified:
            return f"ped:{unified}"
    return f"row:{int(task_id)}"


def enrich_code_examples_for_tc_progress(
    code_examples: dict[str, Any] | None,
) -> dict[str, Any]:
    """Ensure curriculum showcase can resolve TC ids (catalog / algo v128 fallbacks)."""
    examples = dict(code_examples or {})
    if resolve_tc42_ids_for_task(examples):
        return examples

    showcase = examples.get("curriculum_showcase")
    if not isinstance(showcase, dict):
        showcase = {}
        examples["curriculum_showcase"] = showcase

    showcase.update(_normalize_showcase_fields(showcase))

    if not str(showcase.get("slot_id") or showcase.get("slug") or "").strip():
        pedagogical = str(showcase.get("pedagogical_slot_id") or "").strip()
        if pedagogical:
            showcase["slot_id"] = pedagogical

    catalog_ids = _showcase_tc42_ids(showcase)
    if catalog_ids:
        showcase.setdefault("expected_concept_ids", catalog_ids)
    return examples


def _collect_progress_slots(
    *,
    accessible_task_ids: Iterable[int],
    solved_task_ids: set[int],
    get_code_examples: Callable[[int], dict[str, Any] | None],
    language: str | None = None,
    solved_task_ids_by_language: dict[str, set[int]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Pedagogical slot → display TC ids + solved flag (deduped per language track)."""
    lang_key = normalize_curriculum_language(language) if language else None
    slots: dict[str, dict[str, Any]] = {}

    for task_id in accessible_task_ids:
        code_examples = enrich_code_examples_for_tc_progress(get_code_examples(task_id))
        if lang_key:
            display_ids = resolve_display_tc_ids_for_task_for_language(code_examples, lang_key)
            if not display_ids:
                continue
            tracks = curriculum_languages_for_task(code_examples)
            if tracks and lang_key not in tracks:
                continue
            solved_for_lang = (solved_task_ids_by_language or {}).get(lang_key, set())
            is_solved = int(task_id) in solved_for_lang
            slot_key = f"{lang_key}:{_pedagogical_progress_key(int(task_id), code_examples)}"
        else:
            display_ids = resolve_display_tc_ids_for_task(code_examples)
            if not display_ids:
                continue
            is_solved = int(task_id) in solved_task_ids
            slot_key = _pedagogical_progress_key(int(task_id), code_examples)

        bucket = slots.get(slot_key)
        if bucket is None:
            slots[slot_key] = {
                "display_ids": set(display_ids),
                "solved": is_solved,
            }
            continue
        bucket["display_ids"].update(display_ids)
        bucket["solved"] = bool(bucket["solved"]) or is_solved

    return slots


def _rollup_slots_to_group_rows(slots: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate slot progress into ~8 pedagogical skill groups."""
    stats: dict[str, dict[str, int]] = {
        group.id: {"total": 0, "solved": 0} for group in TC_SKILL_GROUPS
    }
    seen: dict[str, set[str]] = {group.id: set() for group in TC_SKILL_GROUPS}

    for slot_key, bucket in slots.items():
        is_solved = bool(bucket["solved"])
        group_ids: set[str] = set()
        for tc_id in bucket["display_ids"]:
            gid = display_tc_group_id(str(tc_id))
            if gid:
                group_ids.add(gid)
        for gid in group_ids:
            if slot_key in seen[gid]:
                continue
            seen[gid].add(slot_key)
            stats[gid]["total"] += 1
            if is_solved:
                stats[gid]["solved"] += 1

    rows: list[dict[str, Any]] = []
    for group in TC_SKILL_GROUPS:
        total = stats[group.id]["total"]
        solved = stats[group.id]["solved"]
        rows.append(
            {
                "id": group.id,
                "label": group.label,
                "description": group.hint,
                "total": total,
                "solved": solved,
                "percent": round(100.0 * solved / total, 1) if total else 0.0,
            }
        )
    return rows


def _rollup_slots_to_detail_rows(slots: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    stats: dict[str, dict[str, int]] = {
        tc_id: {"total": 0, "solved": 0} for tc_id in list_display_tc_cards()
    }

    for bucket in slots.values():
        is_solved = bool(bucket["solved"])
        for tc_id in bucket["display_ids"]:
            if tc_id not in stats:
                continue
            stats[tc_id]["total"] += 1
            if is_solved:
                stats[tc_id]["solved"] += 1

    rows: list[dict[str, Any]] = []
    for tc_id, card in list_display_tc_cards().items():
        total = stats[tc_id]["total"]
        solved = stats[tc_id]["solved"]
        rows.append(
            {
                "id": tc_id,
                "label": str(card.get("name_ru") or tc_id),
                "description": str(card.get("description_ru") or ""),
                "total": total,
                "solved": solved,
                "percent": round(100.0 * solved / total, 1) if total else 0.0,
            }
        )
    return rows


def build_display_tc_group_progress(
    *,
    accessible_task_ids: Iterable[int],
    solved_task_ids: set[int],
    get_code_examples: Callable[[int], dict[str, Any] | None],
    language: str | None = None,
    solved_task_ids_by_language: dict[str, set[int]] | None = None,
) -> list[dict[str, Any]]:
    """Progress by upleveled TC skill groups (8 rows instead of ~29 display cards)."""
    slots = _collect_progress_slots(
        accessible_task_ids=accessible_task_ids,
        solved_task_ids=solved_task_ids,
        get_code_examples=get_code_examples,
        language=language,
        solved_task_ids_by_language=solved_task_ids_by_language,
    )
    return _rollup_slots_to_group_rows(slots)


def build_display_tc_group_progress_by_language(
    *,
    languages: Iterable[str] | None = None,
    accessible_task_ids: Iterable[int],
    solved_task_ids_by_language: dict[str, set[int]],
    task_languages: Callable[[int], list[str]],
    get_code_examples: Callable[[int], dict[str, Any] | None],
) -> dict[str, list[dict[str, Any]]]:
    langs = list(languages or CURRICULUM_LANGUAGE_ORDER)
    accessible_set = set(accessible_task_ids)
    result: dict[str, list[dict[str, Any]]] = {}

    for lang in langs:
        lang_key = normalize_curriculum_language(lang) or str(lang).strip().lower()
        if not lang_key:
            continue
        lang_tasks = {
            task_id
            for task_id in accessible_set
            if not task_languages(task_id) or lang_key in task_languages(task_id)
        }
        result[lang_key] = build_display_tc_group_progress(
            accessible_task_ids=lang_tasks,
            solved_task_ids=set(),
            get_code_examples=get_code_examples,
            language=lang_key,
            solved_task_ids_by_language=solved_task_ids_by_language,
        )
    return result


def build_display_tc_progress(
    *,
    accessible_task_ids: Iterable[int],
    solved_task_ids: set[int],
    get_code_examples: Callable[[int], dict[str, Any] | None],
    language: str | None = None,
    solved_task_ids_by_language: dict[str, set[int]] | None = None,
) -> list[dict[str, Any]]:
    """
    For each display TC card:
    progress = solved slots containing TC / total curriculum slots containing TC.

    Tasks are deduped by pedagogical slot so mirror rows (Pascal/Python on the
    same slot) count once per language track — aligned with the 128-task course.

    When ``language`` is set, only tasks and solves for that track are counted.
    """
    slots = _collect_progress_slots(
        accessible_task_ids=accessible_task_ids,
        solved_task_ids=solved_task_ids,
        get_code_examples=get_code_examples,
        language=language,
        solved_task_ids_by_language=solved_task_ids_by_language,
    )
    return _rollup_slots_to_detail_rows(slots)


def build_display_tc_progress_by_language(
    *,
    languages: Iterable[str] | None = None,
    accessible_task_ids: Iterable[int],
    solved_task_ids_by_language: dict[str, set[int]],
    task_languages: Callable[[int], list[str]],
    get_code_examples: Callable[[int], dict[str, Any] | None],
) -> dict[str, list[dict[str, Any]]]:
    """Display TC progress per curriculum language track."""
    langs = list(languages or CURRICULUM_LANGUAGE_ORDER)
    accessible_set = set(accessible_task_ids)
    result: dict[str, list[dict[str, Any]]] = {}

    for lang in langs:
        lang_key = normalize_curriculum_language(lang) or str(lang).strip().lower()
        if not lang_key:
            continue
        lang_tasks = {
            task_id
            for task_id in accessible_set
            if not task_languages(task_id) or lang_key in task_languages(task_id)
        }
        result[lang_key] = build_display_tc_progress(
            accessible_task_ids=lang_tasks,
            solved_task_ids=set(),
            get_code_examples=get_code_examples,
            language=lang_key,
            solved_task_ids_by_language=solved_task_ids_by_language,
        )
    return result


def pick_default_tc_skills_language(
    tc_skills_by_language: dict[str, list[dict[str, Any]]],
    solved_task_ids_by_language: dict[str, set[int]],
) -> str:
    """Prefer the track with the most successful solves that has catalog coverage."""
    best_lang = ""
    best_score = -1
    for lang in CURRICULUM_LANGUAGE_ORDER:
        rows = tc_skills_by_language.get(lang) or []
        if not any(int(row.get("total") or 0) > 0 for row in rows):
            continue
        score = len(solved_task_ids_by_language.get(lang, set()))
        if score > best_score:
            best_score = score
            best_lang = lang
    if best_lang:
        return best_lang
    for lang in CURRICULUM_LANGUAGE_ORDER:
        rows = tc_skills_by_language.get(lang) or []
        if any(int(row.get("total") or 0) > 0 for row in rows):
            return lang
    return CURRICULUM_LANGUAGE_ORDER[0] if CURRICULUM_LANGUAGE_ORDER else "pascal"
