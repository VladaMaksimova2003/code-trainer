"""One DB task row per pedagogical curriculum slot; language tracks hold per-language metadata."""

from __future__ import annotations

from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.mirror.curriculum_slot_mirror_map import (
    PYTHON_ONLY_SLOTS,
    strict_python_to_pascal_slot,
)
from application.curriculum.mirror.curriculum_slot_mirror_cpp import (
    CPP_ONLY_SLOTS,
    cpp_to_pascal_slot,
    is_cpp_only_slot,
)
from infrastructure.db.models.task.task import Task as TaskModel

_showcase_tasks_cache: list[tuple[TaskModel, dict[str, Any]]] | None = None
_showcase_tasks_cached_fingerprint: tuple[int, int, bytes] | None = None

CurriculumLanguage = Literal["pascal", "python", "cpp"]

_TRACK_FIELD_KEYS = (
    "group",
    "collection_key",
    "slug",
    "concept_id",
    "technical_concept_id",
    "exercise_pattern_id",
    "curriculum_version",
    "target_language",
    "language",
    "concept_patterns",
    "slot_id",
    "slot_pattern_id",
    "task_format",
    "pascal_features",
    "python_features",
    "cpp_features",
    "expected_concept_ids",
    "educational_goal",
    "is_preview",
    "collection_id",
    "primary_action",
    "secondary_actions",
    "short_instruction",
    "flowchart_mode",
    "known_language_variants",
    "assemble_context",
    "expected_output",
    "reference_solution",
    "starter_code",
    "display_order",
    "collection_chapter_rank",
)


def canonical_pedagogical_slot_id(
    *,
    slot_id: str | None = None,
    slug: str | None = None,
    language: str,
) -> str:
    candidate = str(slot_id or slug or "").strip()
    if not candidate:
        return ""
    lang = language.strip().lower()
    if lang == "pascal":
        return candidate
    if candidate in PYTHON_ONLY_SLOTS or candidate in CPP_ONLY_SLOTS:
        return candidate
    if lang == "cpp" and is_cpp_only_slot(candidate):
        return candidate
    if lang == "cpp":
        mapped = cpp_to_pascal_slot(candidate)
        if mapped:
            return mapped
    mapped = strict_python_to_pascal_slot(candidate)
    return mapped or candidate


def _language_from_group(group: Any) -> str | None:
    g = str(group or "")
    if g.startswith("python_curriculum"):
        return "python"
    if g.startswith("pascal_curriculum"):
        return "pascal"
    if g.startswith("cpp_curriculum"):
        return "cpp"
    return None


def pedagogical_slot_id_from_showcase(showcase: dict[str, Any]) -> str | None:
    ped = str(showcase.get("pedagogical_slot_id") or "").strip()
    if ped:
        return ped
    slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    if not slot_id:
        return None
    lang = str(
        showcase.get("target_language") or _language_from_group(showcase.get("group")) or "pascal"
    )
    canonical = canonical_pedagogical_slot_id(slot_id=slot_id, slug=slot_id, language=lang)
    return canonical or None


def unified_pedagogical_slot_key(showcase: dict[str, Any]) -> str | None:
    """One curriculum exercise across language rows (pas_001 + py_001 → same key)."""
    from application.curriculum.mirror.curriculum_slot_mirror import ALGO_V4_SLOT_RE, is_algo_v4_slot

    slot = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    if slot and is_algo_v4_slot(slot):
        match = ALGO_V4_SLOT_RE.match(slot)
        if match:
            return f"algo_v4:{match.group(2)}"
    return pedagogical_slot_id_from_showcase(showcase)


def language_track(showcase: dict[str, Any], language: str) -> dict[str, Any]:
    lang = language.strip().lower()
    tracks = showcase.get("language_tracks")
    if isinstance(tracks, dict):
        track = tracks.get(lang)
        if isinstance(track, dict):
            return dict(track)
    target = str(
        showcase.get("target_language") or _language_from_group(showcase.get("group")) or ""
    ).lower()
    if target == lang:
        return {key: showcase[key] for key in _TRACK_FIELD_KEYS if key in showcase}

    from application.curriculum.mirror.curriculum_slot_mirror import (
        is_algo_v4_slot,
        mirror_slot_to_language,
    )

    seed_slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
    if not seed_slug and isinstance(tracks, dict):
        for track in tracks.values():
            if isinstance(track, dict):
                seed_slug = str(track.get("slug") or track.get("slot_id") or "").strip()
                if seed_slug:
                    break
    if seed_slug and is_algo_v4_slot(seed_slug):
        mirrored = mirror_slot_to_language(seed_slug, lang)
        if mirrored:
            synthesized = {
                "slug": mirrored,
                "slot_id": mirrored,
                "target_language": lang,
            }
            if isinstance(tracks, dict):
                sibling = tracks.get("python") or tracks.get("pascal") or next(iter(tracks.values()), None)
                if isinstance(sibling, dict) and sibling.get("collection_key"):
                    synthesized["collection_key"] = sibling["collection_key"]
            return synthesized
    return {}


def track_slug(showcase: dict[str, Any], language: str) -> str | None:
    track = language_track(showcase, language)
    slug = str(track.get("slug") or "").strip()
    if slug:
        return slug
    target = str(showcase.get("target_language") or "").lower()
    if target == language.strip().lower():
        legacy = str(showcase.get("slug") or "").strip()
        return legacy or None
    return None


def _collection_group_suffix(collection_key: str) -> str:
    return f"_{collection_key}"


def _collection_groups_compatible(
    *,
    expected_group: str | None,
    showcase_group: str | None,
    collection_key: str,
) -> bool:
    if not expected_group:
        return True
    expected = str(expected_group)
    actual = str(showcase_group or "")
    if actual == expected:
        return True
    suffix = _collection_group_suffix(collection_key)
    return expected.endswith(suffix) and actual.endswith(suffix)


def showcase_matches_collection(
    showcase: dict[str, Any],
    *,
    language: str,
    collection_key: str,
    group: str | None = None,
) -> bool:
    lang = language.strip().lower()
    track = language_track(showcase, lang)
    if track and str(track.get("collection_key") or "") == collection_key:
        track_group = str(track.get("group") or "")
        if group is None or track_group == group:
            return True
        if not track_group:
            sibling_group = ""
            tracks = showcase.get("language_tracks")
            if isinstance(tracks, dict):
                for sibling in tracks.values():
                    if isinstance(sibling, dict) and sibling.get("group"):
                        sibling_group = str(sibling.get("group"))
                        break
            if _collection_groups_compatible(
                expected_group=group,
                showcase_group=str(showcase.get("group") or sibling_group),
                collection_key=collection_key,
            ):
                return True

    tracks = showcase.get("language_tracks")
    root_collection = str(showcase.get("collection_key") or "")
    if (
        isinstance(tracks, dict)
        and lang in tracks
        and root_collection == collection_key
        and _collection_groups_compatible(
            expected_group=group,
            showcase_group=str(showcase.get("group") or ""),
            collection_key=collection_key,
        )
    ):
        return True

    if group and str(showcase.get("group") or "") != group:
        return False
    if root_collection != collection_key:
        return False
    track_lang = str(
        showcase.get("target_language") or _language_from_group(showcase.get("group")) or ""
    ).lower()
    return track_lang == lang


def merge_language_track(
    showcase: dict[str, Any],
    track: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    lang = language.strip().lower()
    merged = dict(showcase)
    ped_id = canonical_pedagogical_slot_id(
        slot_id=str(track.get("slot_id") or track.get("slug") or ""),
        slug=str(track.get("slug") or ""),
        language=lang,
    )
    if ped_id:
        existing = str(merged.get("pedagogical_slot_id") or "").strip()
        if not existing or lang == "pascal":
            merged["pedagogical_slot_id"] = ped_id
    tracks = dict(merged.get("language_tracks") or {})
    tracks[lang] = dict(track)
    merged["language_tracks"] = tracks
    return merged


def resolved_showcase(showcase: dict[str, Any], learning_language: str | None) -> dict[str, Any]:
    if not learning_language:
        return dict(showcase)
    lang = learning_language.strip().lower()
    if lang not in {"pascal", "python", "cpp", "csharp", "java"}:
        return dict(showcase)
    track = language_track(showcase, lang)
    if not track:
        return dict(showcase)
    resolved = dict(showcase)
    for key, value in track.items():
        resolved[key] = value
    resolved["target_language"] = lang
    return resolved


def learning_language_description(
    showcase: dict[str, Any],
    learning_language: str | None,
) -> str | None:
    if not learning_language:
        return None
    lang = learning_language.strip().lower()
    if lang not in {"pascal", "python", "cpp", "csharp", "java"}:
        return None
    resolved = resolved_showcase(showcase, lang)
    for key in ("educational_goal", "short_instruction"):
        text = str(resolved.get(key) or "").strip()
        if text:
            return text
    track = language_track(showcase, lang)
    for key in ("educational_goal", "short_instruction"):
        text = str(track.get(key) or "").strip()
        if text:
            return text
    return None


def learning_language_title(
    showcase: dict[str, Any],
    learning_language: str | None,
    *,
    fallback: str = "",
) -> str:
    if not learning_language:
        return fallback
    lang = learning_language.strip().lower()
    if lang not in {"pascal", "python", "cpp", "csharp", "java"}:
        return fallback
    resolved = resolved_showcase(showcase, lang)
    for key in ("display_title", "title"):
        text = str(resolved.get(key) or "").strip()
        if text:
            return text
    from application.curriculum.mirror.pedagogical_task_model import neutral_title_for_showcase

    neutral = neutral_title_for_showcase(resolved)
    if neutral:
        return neutral
    slug = track_slug(showcase, lang) or str(resolved.get("slug") or resolved.get("slot_id") or "")
    if lang == "cpp" and slug:
        from application.curriculum.cpp.catalog.cpp_curriculum_v3_catalog import catalog_title_for_slot

        catalog_title = catalog_title_for_slot(slug, with_prefix=True)
        if catalog_title:
            return catalog_title
    if lang == "csharp" and slug:
        from application.curriculum.csharp.catalog.csharp_curriculum_v3_catalog import catalog_title_for_slot

        catalog_title = catalog_title_for_slot(slug, with_prefix=True)
        if catalog_title:
            return catalog_title
    if lang == "java" and slug:
        from application.curriculum.java.catalog.java_curriculum_v3_catalog import catalog_title_for_slot

        catalog_title = catalog_title_for_slot(slug, with_prefix=True)
        if catalog_title:
            return catalog_title
    return fallback


def _apply_cpp_learning_materials(
    payload: dict[str, Any],
    showcase: dict[str, Any],
    resolved: dict[str, Any],
) -> dict[str, Any]:
    result = dict(payload)
    slot = track_slug(showcase, "cpp") or str(resolved.get("slug") or resolved.get("slot_id") or "")
    task_fmt = str(resolved.get("task_format") or "")
    track = language_track(showcase, "cpp") or {}
    variants = resolved.get("known_language_variants")
    if not isinstance(variants, dict):
        variants = track.get("known_language_variants")
    if isinstance(variants, dict):
        from application.curriculum.cpp.catalog.cpp_known_language import code_examples_from_variants

        examples = dict(result.get("code_examples") or {})
        for lang_key, code in code_examples_from_variants(variants).items():
            if not str(examples.get(lang_key) or "").strip():
                examples[lang_key] = code
        result["code_examples"] = examples
        py_variant = variants.get("python")
        if isinstance(py_variant, dict):
            src = str(py_variant.get("source_code") or "").strip()
            if src:
                result["source_code"] = src
                result["source_language"] = "python"
    if slot:
        from application.curriculum.cpp.catalog.cpp_v311_content import (
            debug_starter_for_slot,
            reference_solution_for_slot,
        )

        if task_fmt.startswith("перевод"):
            ref = reference_solution_for_slot(slot)
            examples = dict(result.get("code_examples") or {})
            examples.setdefault("cpp", ref)
            result["code_examples"] = examples
        elif task_fmt in {"исправление", "поиск_ошибки"}:
            starter = debug_starter_for_slot(slot)
            if starter:
                result["source_code"] = starter
                result["source_language"] = "cpp"
    if resolved.get("cpp_features"):
        result["cpp_features"] = resolved["cpp_features"]
    if resolved.get("exercise_pattern_id"):
        result["exercise_pattern_id"] = resolved["exercise_pattern_id"]
    if resolved.get("expected_concept_ids"):
        result["expected_concept_ids"] = resolved["expected_concept_ids"]
    return result


def sync_assembly_fields_for_language(
    payload: dict[str, Any],
    language: str | None = None,
) -> dict[str, Any]:
    """Expose the active learning-language assembly on payload root (template/blocks/order)."""
    lang = str(
        language
        or payload.get("target_language")
        or payload.get("language")
        or ""
    ).strip().lower()
    if lang not in {"pascal", "python", "cpp", "csharp", "java"}:
        return payload

    variants = payload.get("language_variants")
    if not isinstance(variants, dict):
        return payload
    variant = variants.get(lang)
    if not isinstance(variant, dict):
        for key, raw in variants.items():
            if str(key).lower() == lang and isinstance(raw, dict):
                variant = raw
                break
    if not isinstance(variant, dict):
        return payload

    result = dict(payload)
    if variant.get("template") is not None:
        result["template"] = variant["template"]
    if variant.get("blocks") is not None:
        result["blocks"] = list(variant["blocks"])
    if variant.get("correct_order") is not None:
        result["correct_order"] = list(variant["correct_order"])
    result["language"] = lang
    return result


def apply_learning_language_to_payload(
    payload: dict[str, Any],
    learning_language: str | None,
    *,
    showcase: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not learning_language:
        return payload
    lang = learning_language.strip().lower()
    if lang not in {"pascal", "python", "cpp", "csharp", "java"}:
        return payload
    if showcase is None:
        examples = payload.get("code_examples")
        if not isinstance(examples, dict):
            return payload
        showcase = examples.get("curriculum_showcase")
    if not isinstance(showcase, dict):
        return payload
    examples = payload.get("code_examples")
    if not isinstance(examples, dict):
        examples = {}
    from application.tasks.services.teacher_assembly_preservation import (
        has_teacher_assembly_override,
    )

    if has_teacher_assembly_override(examples):
        result = dict(payload)
        lang = learning_language.strip().lower()
        result["language"] = lang
        result["target_language"] = lang
        return sync_assembly_fields_for_language(result, lang)

    resolved = resolved_showcase(showcase, lang)
    track = language_track(showcase, lang)
    result = dict(payload)
    merged_examples = dict(examples)
    merged_examples["curriculum_showcase"] = resolved
    result["code_examples"] = merged_examples
    result["language"] = lang
    result["target_language"] = lang
    description = learning_language_description(showcase, lang)
    if description:
        result["description"] = description
    if lang == "cpp":
        result = _apply_cpp_learning_materials(result, showcase, resolved)
    title = learning_language_title(showcase, lang, fallback=str(result.get("title") or ""))
    if title:
        result["title"] = title
    result = apply_mirror_sibling_code_examples(result, showcase, lang)
    return sync_assembly_fields_for_language(result, lang)


def _slot_id_for_learning_track(showcase: dict[str, Any], learning_language: str) -> str:
    current = language_track(showcase, learning_language)
    slot_id = str(current.get("slug") or current.get("slot_id") or "").strip()
    if slot_id:
        return slot_id
    return str(showcase.get("slot_id") or showcase.get("slug") or "").strip()


def populate_algo_v4_reference_examples(
    payload: dict[str, Any],
    showcase: dict[str, Any],
    learning_language: str,
) -> dict[str, Any]:
    """Fill code_examples with v4 reference snippets for every curriculum language."""
    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled

    if not is_catalog_sync_enabled():
        return payload

    from application.curriculum.content.algo_syntax_task_extra import (
        is_algo_syntax_slot,
        resolve_slot_pattern_key,
    )
    from application.curriculum.content.v4_reference_code import get_reference_code
    from application.tasks.services.teacher_assembly_preservation import (
        has_teacher_assembly_override,
    )

    examples = payload.get("code_examples")
    if isinstance(examples, dict) and has_teacher_assembly_override(examples):
        return payload

    slot_id = _slot_id_for_learning_track(showcase, learning_language)
    if not slot_id or not is_algo_syntax_slot(slot_id):
        return payload

    track = language_track(showcase, learning_language) or {}
    pattern_key = resolve_slot_pattern_key(
        slot_id,
        slot_pattern_id=str(
            showcase.get("slot_pattern_id") or track.get("slot_pattern_id") or ""
        ).strip()
        or None,
    )
    result = dict(payload)
    examples = dict(result.get("code_examples") or {})
    for lang in ("pascal", "python", "cpp", "csharp", "java"):
        fresh = str(get_reference_code(slot_id, lang, pattern_key=pattern_key) or "")
        if fresh.strip() and not str(examples.get(lang) or "").strip():
            examples[lang] = fresh
    result["code_examples"] = examples
    return result


def apply_mirror_sibling_code_examples(
    payload: dict[str, Any],
    showcase: dict[str, Any],
    learning_language: str | None,
) -> dict[str, Any]:
    """Expose mirror track fragment (Pascal↔Python) in code_examples for «Я знаю»."""
    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled

    if not is_catalog_sync_enabled():
        return payload
    if not learning_language:
        return payload
    learning = learning_language.strip().lower()
    if learning not in {"pascal", "python", "cpp", "csharp", "java"}:
        return payload

    payload = populate_algo_v4_reference_examples(payload, showcase, learning)
    if learning in {"cpp", "csharp", "java"}:
        return payload
    sibling_lang = "pascal" if learning == "python" else "python"
    from application.curriculum.mirror.curriculum_slot_mirror import mirror_slot_id

    sibling_track = language_track(showcase, sibling_lang)
    sibling_slot = str(sibling_track.get("slug") or sibling_track.get("slot_id") or "").strip()
    if not sibling_slot:
        current = language_track(showcase, learning)
        current_slot = str(current.get("slug") or current.get("slot_id") or "").strip()
        sibling_slot = mirror_slot_id(current_slot, target=sibling_lang) or ""
    if not sibling_slot:
        return payload

    if sibling_lang == "pascal":
        from application.curriculum.pascal.catalog.pascal_v311_content import reference_solution_for_slot

        pattern_id = str(
            sibling_track.get("slot_pattern_id")
            or showcase.get("slot_pattern_id")
            or ""
        ).strip() or None
        code = reference_solution_for_slot(sibling_slot, slot_pattern_id=pattern_id)
    else:
        from application.curriculum.python.catalog.python_v311_content import reference_solution_for_slot

        pattern_id = str(
            sibling_track.get("slot_pattern_id")
            or showcase.get("slot_pattern_id")
            or ""
        ).strip() or None
        code = reference_solution_for_slot(sibling_slot, slot_pattern_id=pattern_id)
    code = str(code or "").strip()
    if not code:
        return payload

    result = dict(payload)
    examples = dict(result.get("code_examples") or {})
    if not str(examples.get(sibling_lang) or "").strip():
        examples[sibling_lang] = code
    result["code_examples"] = examples
    return result


def _showcase_title_prefixes() -> tuple[str, ...]:
    from application.curriculum.pascal.showcase.pascal_v311_registry import PASCAL_V311_SHOWCASE_COLLECTIONS

    prefixes = {col.title_prefix for col in PASCAL_V311_SHOWCASE_COLLECTIONS}
    prefixes.update(
        {
            "[Pascal v3.1.1:",
            "[Python v1:",
            "[C++ v1:",
            "[C# v1:",
            "[Java v1:",
            "[Pascal Loops Showcase]",
            "[Pascal Conditions Showcase]",
            "[Pascal Showcase]",
        }
    )
    return tuple(sorted(prefixes, key=len, reverse=True))


def _is_curriculum_showcase_task(row: TaskModel) -> bool:
    title = str(row.title or "")
    if title.startswith("["):
        for prefix in _showcase_title_prefixes():
            if title.startswith(prefix):
                return True
    showcase = (row.code_examples or {}).get("curriculum_showcase")
    if not isinstance(showcase, dict) or not showcase:
        return False
    if showcase.get("pedagogical_slot_id") or showcase.get("language_tracks"):
        return True
    if showcase.get("collection_key") and showcase.get("slug"):
        return True
    return False


_pedagogical_slot_index: dict[str, int] | None = None
_pedagogical_slot_index_fingerprint: tuple[int, int] | None = None


def _pedagogical_slot_task_id(session: Session, pedagogical_slot_id: str) -> int | None:
    global _pedagogical_slot_index, _pedagogical_slot_index_fingerprint

    from application.curriculum.showcase.showcase_task_index import _showcase_index_fingerprint

    fingerprint = _showcase_index_fingerprint(session)
    if _pedagogical_slot_index is None or _pedagogical_slot_index_fingerprint != fingerprint:
        index: dict[str, int] = {}
        for row, showcase in iter_showcase_tasks(session):
            ped = str(showcase.get("pedagogical_slot_id") or "").strip()
            if ped:
                index.setdefault(ped, row.id)
            derived = pedagogical_slot_id_from_showcase(showcase)
            if derived:
                index.setdefault(str(derived), row.id)
        _pedagogical_slot_index = index
        _pedagogical_slot_index_fingerprint = fingerprint
    return _pedagogical_slot_index.get(pedagogical_slot_id)


def invalidate_pedagogical_slot_index_cache() -> None:
    global _pedagogical_slot_index, _pedagogical_slot_index_fingerprint
    _pedagogical_slot_index = None
    _pedagogical_slot_index_fingerprint = None


def find_task_by_pedagogical_slot(session: Session, pedagogical_slot_id: str) -> TaskModel | None:
    target = str(pedagogical_slot_id or "").strip()
    if not target:
        return None
    cached_id = _pedagogical_slot_task_id(session, target)
    if cached_id is not None:
        row = session.get(TaskModel, cached_id)
        if row is not None and not row.is_delete:
            return row
    for row, showcase in iter_showcase_tasks(session):
        if str(showcase.get("pedagogical_slot_id") or "") == target:
            return row
        if pedagogical_slot_id_from_showcase(showcase) == target:
            return row
    return None


def resolve_unified_task_for_mirror_attach(
    session: Session,
    *,
    mirror_slug: str,
    target_slug: str = "",
) -> TaskModel | None:
    """Find Universal Core row for mirror attach (v4 py_* or legacy pas_* / psk_*)."""
    from application.curriculum.mirror.curriculum_slot_mirror import mirror_slot_to_language

    candidates: list[str] = []
    mirror = str(mirror_slug or "").strip()
    if mirror:
        candidates.append(mirror)
        pas_from_py = mirror_slot_to_language(mirror, "pascal")
        if pas_from_py:
            candidates.append(pas_from_py)
        if mirror.startswith("pas_"):
            candidates.append(f"py_{mirror[4:]}")

    target = str(target_slug or "").strip()
    if target:
        candidates.append(target)
        for prefix in ("cpp_", "cs_", "java_", "py_", "pas_"):
            if target.startswith(prefix):
                suffix = target[len(prefix) :]
                if suffix:
                    candidates.append(f"py_{suffix}")
                break

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        row = find_task_by_pedagogical_slot(session, candidate)
        if row is not None:
            return row

    for candidate in candidates:
        if candidate.startswith("py_"):
            row = find_showcase_task_by_track_slug(session, candidate, language="python")
            if row is not None:
                return row
    return None


def attach_unified_showcase_meta(
    row: TaskModel,
    track_meta: dict[str, Any],
    language: CurriculumLanguage,
) -> None:
    from application.curriculum.mirror.pedagogical_task_model import normalize_unified_showcase

    examples = dict(row.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    merged = merge_language_track(showcase, track_meta, language)
    merged = normalize_unified_showcase(merged)
    if language == "pascal" or not merged.get("slug"):
        for key in _TRACK_FIELD_KEYS:
            if key in track_meta:
                merged[key] = track_meta[key]
    examples["curriculum_showcase"] = merged
    row.code_examples = examples


def find_showcase_task_by_track_slug(
    session: Session,
    slug: str,
    *,
    language: str,
    collection_key: str | None = None,
    group: str | None = None,
) -> TaskModel | None:
    for row, showcase in iter_showcase_tasks(session):
        if track_slug(showcase, language) != slug:
            continue
        if collection_key and not showcase_matches_collection(
            showcase,
            language=language,
            collection_key=collection_key,
            group=group,
        ):
            continue
        return row
    return None


def invalidate_showcase_tasks_cache() -> None:
    """Drop cached showcase task rows after seed/migration."""
    global _showcase_tasks_cache, _showcase_tasks_cached_fingerprint
    _showcase_tasks_cache = None
    _showcase_tasks_cached_fingerprint = None


def _compute_showcase_tasks_fingerprint(session: Session) -> tuple[int, int, bytes]:
    import hashlib

    from sqlalchemy import func, select

    count, max_id, max_updated = session.execute(
        select(
            func.count(TaskModel.id),
            func.max(TaskModel.id),
            func.max(TaskModel.updated_at),
        ).where(TaskModel.is_delete.is_(False))
    ).one()
    payload = f"showcase-tasks|{int(count or 0)}|{int(max_id or 0)}|{max_updated}\n"
    return int(count or 0), int(max_id or 0), hashlib.sha256(payload.encode("utf-8")).digest()


def iter_showcase_tasks(session: Session) -> list[tuple[TaskModel, dict[str, Any]]]:
    global _showcase_tasks_cache, _showcase_tasks_cached_fingerprint

    fingerprint = _compute_showcase_tasks_fingerprint(session)
    if _showcase_tasks_cache is not None and _showcase_tasks_cached_fingerprint == fingerprint:
        return _showcase_tasks_cache

    from sqlalchemy.orm import load_only

    stmt = (
        select(TaskModel)
        .where(TaskModel.is_delete.is_(False))
        .options(
            load_only(
                TaskModel.id,
                TaskModel.title,
                TaskModel.task_type,
                TaskModel.difficulty,
                TaskModel.code_examples,
            )
        )
        .order_by(TaskModel.id.asc())
    )
    try:
        if session.get_bind().dialect.name == "postgresql":
            stmt = stmt.where(TaskModel.code_examples.has_key("curriculum_showcase"))
    except Exception:
        pass

    rows = session.scalars(stmt).all()
    matched: list[tuple[TaskModel, dict[str, Any]]] = []
    for row in rows:
        if not _is_curriculum_showcase_task(row):
            continue
        showcase = dict((row.code_examples or {}).get("curriculum_showcase") or {})
        if showcase:
            matched.append((row, showcase))
    _showcase_tasks_cache = matched
    _showcase_tasks_cached_fingerprint = fingerprint
    return matched

