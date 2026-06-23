"""Drop legacy mirror duplicate rows from collection task lists."""

from __future__ import annotations

from typing import Any

from application.curriculum.mirror.pedagogical_task_store import (
    pedagogical_slot_id_from_showcase,
    unified_pedagogical_slot_key,
)
from infrastructure.db.models.task.task import Task as TaskModel

_SLOT_PREFIXES_BY_LANG: dict[str, tuple[str, ...]] = {
    "pascal": ("pas_", "psk_", "plh_"),
    "python": ("py_", "pyk_"),
    "cpp": ("cpp_", "cpk_"),
    "csharp": ("cs_", "csk_"),
    "java": ("java_", "javk_"),
}

# Legacy mirror seed created standalone per-language rows above this id.
_LEGACY_MIRROR_MAX_CANONICAL_TASK_ID = 128


def showcase_row_dedupe_key(showcase: dict[str, Any], *, task_id: int) -> str:
    unified = unified_pedagogical_slot_key(showcase)
    if unified:
        return f"ped:{unified}"
    ped = pedagogical_slot_id_from_showcase(showcase)
    if ped:
        return f"ped:{ped}"
    return f"row:{task_id}"


def _slug_affinity(slug: str, language: str) -> int:
    normalized = str(slug or "").strip().lower()
    if not normalized:
        return 80
    for prefix in _SLOT_PREFIXES_BY_LANG.get(language, ()):
        if normalized.startswith(prefix):
            return 0
    return 80


def _track_count(showcase: dict[str, Any]) -> int:
    tracks = showcase.get("language_tracks")
    return len(tracks) if isinstance(tracks, dict) else 0


def _canonical_row_priority(showcase: dict[str, Any], task_id: int) -> int:
    """Unified multi-language rows beat legacy single-language mirror copies."""
    if task_id <= _LEGACY_MIRROR_MAX_CANONICAL_TASK_ID and _track_count(showcase) >= 3:
        return 0
    if task_id > _LEGACY_MIRROR_MAX_CANONICAL_TASK_ID:
        return 2
    return 1


def _showcase_language_affinity(showcase: dict[str, Any], language: str, task_id: int) -> tuple[int, int]:
    lang = str(language or "").strip().lower()
    target = str(showcase.get("target_language") or "").strip().lower()
    slot = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    tracks = showcase.get("language_tracks")
    score = 70
    if target == lang:
        score = 0
    elif isinstance(tracks, dict) and lang in tracks:
        score = 20
    else:
        score = _slug_affinity(slot, lang)
    return (score, int(task_id))


def _showcase_row_rank(showcase: dict[str, Any], language: str, task_id: int) -> tuple[int, tuple[int, int]]:
    return (_canonical_row_priority(showcase, task_id), _showcase_language_affinity(showcase, language, task_id))


def _payload_language_affinity(payload: dict[str, Any], language: str) -> tuple[int, int]:
    lang = str(language or "").strip().lower()
    task_id = int(payload.get("task_id") or 0)
    slug = str(payload.get("slug") or "")
    row_lang = str(payload.get("language") or "").strip().lower()
    score = _slug_affinity(slug, lang)
    if row_lang == lang and score > 0:
        score = min(score, 15)
    return (score, task_id)


def _payload_row_rank(payload: dict[str, Any], language: str) -> tuple[int, tuple[int, int]]:
    task_id = int(payload.get("task_id") or 0)
    legacy = 2 if task_id > _LEGACY_MIRROR_MAX_CANONICAL_TASK_ID else 0
    return (legacy, _payload_language_affinity(payload, language))


def dedupe_showcase_task_rows(
    matched: list[tuple[TaskModel, dict[str, Any]]],
    *,
    language: str,
) -> list[tuple[TaskModel, dict[str, Any]]]:
    """Keep one DB row per pedagogical slot for the requested language track."""
    best: dict[str, tuple[tuple[int, tuple[int, int]], TaskModel, dict[str, Any]]] = {}
    order: list[str] = []
    for row, showcase in matched:
        key = showcase_row_dedupe_key(showcase, task_id=int(row.id))
        rank = _showcase_row_rank(showcase, language, int(row.id))
        prev = best.get(key)
        if prev is None:
            order.append(key)
            best[key] = (rank, row, showcase)
            continue
        if rank < prev[0]:
            best[key] = (rank, row, showcase)
    return [best[key][1:] for key in order if key in best]


def dedupe_collection_task_payloads(
    rows: list[dict[str, Any]],
    *,
    language: str,
) -> list[dict[str, Any]]:
    """Drop mirror duplicates from serialized collection rows."""
    best: dict[str, tuple[tuple[int, tuple[int, int]], dict[str, Any]]] = {}
    order: list[str] = []
    for row in rows:
        task_id = int(row.get("task_id") or 0)
        slug = str(row.get("slug") or "")
        unified = unified_pedagogical_slot_key({"slug": slug, "slot_id": slug})
        key = f"ped:{unified}" if unified else f"row:{task_id}"
        rank = _payload_row_rank(row, language)
        prev = best.get(key)
        if prev is None:
            order.append(key)
            best[key] = (rank, row)
            continue
        if rank < prev[0]:
            best[key] = (rank, row)
    return [best[key][1] for key in order if key in best]
