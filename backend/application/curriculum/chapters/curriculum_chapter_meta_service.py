"""CRUD and resolution for teacher-managed curriculum chapter metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.collections.curriculum_collections_registry import (
    list_curriculum_collections,
)
from infrastructure.db.models.learning.curriculum_chapter_meta import CurriculumChapterMeta

_CHAPTER_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{1,126}$")
_GLOBAL_LANGUAGE = ""
COLLECTION_META_CHAPTER_KEY = "__collection__"
PLATFORM_COURSE_META_CHAPTER_KEY = "__platform_course__"
PLATFORM_COURSE_DEFAULT_TITLE = "Базовый синтаксис через алгоритмы"
PLATFORM_COURSE_DEFAULT_DESCRIPTION = (
    "Единый алгоритмический курс: 16 глав и 128 задач. "
    "Один сюжет — параллельные реализации на Python, Pascal, C++, C# и Java."
)


@dataclass(frozen=True)
class ChapterMetaRecord:
    language: str
    chapter_key: str
    title: str
    description: str
    sort_order: int
    is_custom: bool
    task_count: int = 0
    registry_title: str | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class ChapterMetaContext:
    rows_by_key: dict[tuple[str, str], CurriculumChapterMeta]
    registry: dict[tuple[str, str], tuple[str, str, int]]
    task_counts_by_chapter: dict[str, int]


def _registry_chapters(language: str | None = None) -> dict[tuple[str, str], tuple[str, str, int]]:
    """(language, chapter_key) → (title, description, default_order)."""
    result: dict[tuple[str, str], tuple[str, str, int]] = {}
    for index, definition in enumerate(list_curriculum_collections(language)):
        key = (str(definition.language), str(definition.chapter_key))
        if key in result:
            continue
        result[key] = (
            str(definition.title_ru),
            str(definition.description_ru or ""),
            index * 10,
        )
    return result


def _slugify_chapter_key(title: str) -> str:
    translit = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    lowered = title.strip().lower()
    chars: list[str] = []
    for ch in lowered:
        if ch in translit:
            chars.append(translit[ch])
        elif ch.isalnum():
            chars.append(ch)
        elif ch in {" ", "-", "_"}:
            chars.append("_")
    slug = re.sub(r"_+", "_", "".join(chars)).strip("_")
    if not slug or not _CHAPTER_KEY_RE.match(slug):
        slug = "chapter"
    return slug[:64]


def _unique_chapter_key(session: Session, language: str, base: str) -> str:
    candidate = base
    suffix = 2
    while _chapter_row(session, language, candidate) is not None or _registry_has_key(language, candidate):
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def _registry_has_key(language: str, chapter_key: str) -> bool:
    return (language, chapter_key) in _registry_chapters(language)


def _chapter_row(session: Session, language: str, chapter_key: str) -> CurriculumChapterMeta | None:
    return session.execute(
        select(CurriculumChapterMeta).where(
            CurriculumChapterMeta.language == language,
            CurriculumChapterMeta.chapter_key == chapter_key,
        )
    ).scalar_one_or_none()


def count_tasks_by_chapter_key(session: Session) -> dict[str, int]:
    from application.curriculum.showcase.showcase_task_index import get_showcase_task_index

    index = get_showcase_task_index()
    if index is not None:
        return index.chapter_task_counts()

    from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

    try:
        counts: dict[str, int] = {}
        for _row, showcase in iter_showcase_tasks(session):
            chapter_key = str(showcase.get("collection_key") or "").strip()
            if chapter_key:
                counts[chapter_key] = counts.get(chapter_key, 0) + 1
        return counts
    except Exception:
        return {}


def count_tasks_for_chapter(session: Session, chapter_key: str) -> int:
    return count_tasks_by_chapter_key(session).get(str(chapter_key or "").strip(), 0)


def load_chapter_meta_context(
    session: Session,
    *,
    language: str | None = None,
    task_counts_by_chapter: dict[str, int] | None = None,
) -> ChapterMetaContext:
    db_rows = session.execute(select(CurriculumChapterMeta)).scalars().all()
    rows_by_key = {(str(row.language), str(row.chapter_key)): row for row in db_rows}
    counts = (
        task_counts_by_chapter
        if task_counts_by_chapter is not None
        else count_tasks_by_chapter_key(session)
    )
    return ChapterMetaContext(
        rows_by_key=rows_by_key,
        registry=_registry_chapters(language),
        task_counts_by_chapter=counts,
    )


def _lookup_chapter_row(
    session: Session,
    language: str,
    chapter_key: str,
    *,
    meta_ctx: ChapterMetaContext | None = None,
) -> CurriculumChapterMeta | None:
    lang = str(language or "").strip().lower()
    key = str(chapter_key or "").strip()
    if meta_ctx is not None:
        row = meta_ctx.rows_by_key.get((lang, key))
        if row is not None:
            return row
        return meta_ctx.rows_by_key.get((_GLOBAL_LANGUAGE, key))
    return _chapter_row(session, lang, key)


def list_chapters(
    session: Session,
    *,
    language: str | None = None,
    meta_ctx: ChapterMetaContext | None = None,
) -> list[ChapterMetaRecord]:
    lang_filter = str(language or "").strip().lower() or None
    ctx = meta_ctx or load_chapter_meta_context(session, language=lang_filter)
    registry = ctx.registry

    keys: set[tuple[str, str]] = set(registry)
    for (row_lang, chapter_key) in ctx.rows_by_key:
        if lang_filter is not None and row_lang != lang_filter:
            continue
        keys.add((row_lang, chapter_key))

    records: list[ChapterMetaRecord] = []
    for row_lang, chapter_key in keys:
        reg = registry.get((row_lang, chapter_key))
        db_row = ctx.rows_by_key.get((row_lang, chapter_key))
        global_row = ctx.rows_by_key.get((_GLOBAL_LANGUAGE, chapter_key)) if row_lang else None
        registry_title = reg[0] if reg else None
        default_order = reg[2] if reg else 9000

        if db_row is not None:
            title = str(db_row.title)
            description = str(db_row.description or "")
            sort_order = int(db_row.sort_order or default_order)
            is_custom = bool(db_row.is_custom)
            updated_at = db_row.updated_at
        elif global_row is not None and reg is not None:
            title = str(global_row.title)
            description = str(global_row.description or "")
            sort_order = int(global_row.sort_order or default_order)
            is_custom = False
            updated_at = global_row.updated_at
        elif reg is not None:
            title, description, sort_order = reg[0], reg[1], default_order
            is_custom = False
            updated_at = None
        else:
            continue

        records.append(
            ChapterMetaRecord(
                language=row_lang,
                chapter_key=chapter_key,
                title=title,
                description=description,
                sort_order=sort_order,
                is_custom=is_custom,
                task_count=ctx.task_counts_by_chapter.get(chapter_key, 0),
                registry_title=registry_title,
                updated_at=updated_at,
            )
        )
    records.sort(key=lambda item: (item.sort_order, item.title.lower()))
    return [item for item in records if item.chapter_key != COLLECTION_META_CHAPTER_KEY]


def get_chapter_title_map(session: Session) -> dict[str, str]:
    titles: dict[str, str] = {}
    for item in list_chapters(session):
        titles[item.chapter_key] = item.title
    return titles


def resolve_chapter_display(
    session: Session,
    language: str,
    chapter_key: str,
    *,
    default_title: str | None = None,
    default_description: str | None = None,
    meta_ctx: ChapterMetaContext | None = None,
) -> tuple[str, str]:
    lang = str(language or "").strip().lower()
    key = str(chapter_key or "").strip()
    if not key:
        return default_title or "", default_description or ""

    row = _lookup_chapter_row(session, lang, key, meta_ctx=meta_ctx)
    if row is None:
        row = _lookup_chapter_row(session, _GLOBAL_LANGUAGE, key, meta_ctx=meta_ctx)
    if row is not None:
        return str(row.title), str(row.description or "")

    registry = (meta_ctx.registry if meta_ctx is not None else _registry_chapters(lang)).get(
        (lang, key)
    )
    if registry is not None:
        return registry[0], registry[1]
    return default_title or key, default_description or ""


def create_chapter(
    session: Session,
    *,
    teacher_id: int,
    language: str,
    title: str,
    description: str = "",
    chapter_key: str | None = None,
) -> CurriculumChapterMeta:
    lang = str(language or "").strip().lower()
    if not lang:
        raise ValueError("language is required")
    clean_title = str(title or "").strip()
    if not clean_title:
        raise ValueError("title is required")

    base_key = str(chapter_key or "").strip().lower() or _slugify_chapter_key(clean_title)
    if not _CHAPTER_KEY_RE.match(base_key):
        raise ValueError("chapter_key must match [a-z][a-z0-9_]{1,126}")

    final_key = base_key
    if _registry_has_key(lang, final_key) or _chapter_row(session, lang, final_key) is not None:
        if chapter_key:
            raise ValueError(f"chapter_key already exists: {final_key}")
        final_key = _unique_chapter_key(session, lang, base_key)

    existing_orders = [
        int(row.sort_order or 0)
        for row in session.execute(
            select(CurriculumChapterMeta.sort_order).where(CurriculumChapterMeta.language == lang)
        ).scalars().all()
    ]
    registry_orders = [
        value[2] for (row_lang, key), value in _registry_chapters(lang).items() if row_lang == lang
    ]
    max_order = max([*existing_orders, *registry_orders, 0])
    row = CurriculumChapterMeta(
        language=lang,
        chapter_key=final_key,
        title=clean_title,
        description=str(description or "").strip(),
        sort_order=max_order + 10,
        is_custom=True,
        teacher_id=teacher_id,
    )
    session.add(row)
    session.flush()
    _invalidate_caches()
    return row


def upsert_chapter(
    session: Session,
    *,
    teacher_id: int,
    language: str,
    chapter_key: str,
    title: str,
    description: str = "",
) -> CurriculumChapterMeta:
    lang = str(language or _GLOBAL_LANGUAGE).strip().lower()
    key = str(chapter_key or "").strip()
    clean_title = str(title or "").strip()
    if not key:
        raise ValueError("chapter_key is required")
    if not clean_title:
        raise ValueError("title is required")

    row = _chapter_row(session, lang, key)
    if row is None and lang:
        registry = _registry_chapters(lang).get((lang, key))
        if registry is not None:
            lang = _GLOBAL_LANGUAGE
            row = _chapter_row(session, lang, key)

    if row is None:
        registry = _registry_chapters(lang if lang else None).get((lang, key))
        if registry is None and lang:
            registry = _registry_chapters(lang).get((lang, key))
        sort_order = registry[2] if registry else 9000
        row = CurriculumChapterMeta(
            language=lang,
            chapter_key=key,
            title=clean_title,
            description=str(description or "").strip(),
            sort_order=sort_order,
            is_custom=registry is None,
            teacher_id=teacher_id,
        )
        session.add(row)
    else:
        row.title = clean_title
        row.description = str(description or "").strip()
        row.teacher_id = teacher_id
        row.updated_at = datetime.now(timezone.utc)

    session.flush()
    _invalidate_caches()
    return row


def resolve_collection_display(session: Session, language: str) -> tuple[str, str]:
    from application.curriculum.collections.curriculum_language_catalog import LANGUAGE_LABELS

    lang = str(language or "").strip().lower()
    default_title = LANGUAGE_LABELS.get(lang, lang.title() or lang)
    row = _chapter_row(session, lang, COLLECTION_META_CHAPTER_KEY)
    if row is not None:
        return str(row.title), str(row.description or "")
    return default_title, ""


def list_collection_meta(session: Session) -> list[dict[str, Any]]:
    from application.curriculum.collections.curriculum_language_catalog import (
        LANGUAGE_LABELS,
        list_home_languages,
    )

    rows: list[dict[str, Any]] = []
    for lang_def in list_home_languages():
        lang = lang_def.language
        title, description = resolve_collection_display(session, lang)
        row = _chapter_row(session, lang, COLLECTION_META_CHAPTER_KEY)
        rows.append(
            {
                "language": lang,
                "title": title,
                "description": description,
                "registry_title": LANGUAGE_LABELS.get(lang, lang_def.language_label),
                "updated_at": row.updated_at if row is not None else None,
            }
        )
    return rows


def resolve_platform_course_display(session: Session) -> tuple[str, str]:
    row = _chapter_row(session, _GLOBAL_LANGUAGE, PLATFORM_COURSE_META_CHAPTER_KEY)
    if row is not None:
        return str(row.title), str(row.description or "")
    return PLATFORM_COURSE_DEFAULT_TITLE, PLATFORM_COURSE_DEFAULT_DESCRIPTION


def resolve_platform_course_author(session: Session) -> tuple[int | None, str | None]:
    row = _chapter_row(session, _GLOBAL_LANGUAGE, PLATFORM_COURSE_META_CHAPTER_KEY)
    if row is None:
        return None, None
    from infrastructure.db.models.user.user import User

    user = session.get(User, row.teacher_id)
    if user is None:
        return row.teacher_id, None
    return user.id, user.name


def get_platform_course_meta(session: Session) -> dict[str, Any]:
    title, description = resolve_platform_course_display(session)
    row = _chapter_row(session, _GLOBAL_LANGUAGE, PLATFORM_COURSE_META_CHAPTER_KEY)
    author_user_id, author_name = resolve_platform_course_author(session)
    return {
        "title": title,
        "description": description,
        "registry_title": PLATFORM_COURSE_DEFAULT_TITLE,
        "updated_at": row.updated_at if row is not None else None,
        "author_user_id": author_user_id,
        "author_name": author_name,
    }


def upsert_platform_course_meta(
    session: Session,
    *,
    teacher_id: int,
    title: str,
    description: str = "",
) -> CurriculumChapterMeta:
    return upsert_chapter(
        session,
        teacher_id=teacher_id,
        language=_GLOBAL_LANGUAGE,
        chapter_key=PLATFORM_COURSE_META_CHAPTER_KEY,
        title=title,
        description=description,
    )


def upsert_collection_meta(
    session: Session,
    *,
    teacher_id: int,
    language: str,
    title: str,
    description: str = "",
) -> CurriculumChapterMeta:
    from application.curriculum.collections.curriculum_language_catalog import list_home_languages

    lang = str(language or "").strip().lower()
    allowed = {item.language for item in list_home_languages()}
    if lang not in allowed:
        raise ValueError(f"unsupported language: {lang}")
    return upsert_chapter(
        session,
        teacher_id=teacher_id,
        language=lang,
        chapter_key=COLLECTION_META_CHAPTER_KEY,
        title=title,
        description=description,
    )


def chapter_record_to_dict(record: ChapterMetaRecord) -> dict[str, Any]:
    return {
        "language": record.language,
        "chapter_key": record.chapter_key,
        "title": record.title,
        "description": record.description,
        "sort_order": record.sort_order,
        "is_custom": record.is_custom,
        "task_count": record.task_count,
        "registry_title": record.registry_title,
        "updated_at": record.updated_at,
    }


def list_custom_chapters_for_language(session: Session, language: str) -> list[ChapterMetaRecord]:
    lang = str(language or "").strip().lower()
    return [item for item in list_chapters(session, language=lang) if item.is_custom]


def chapter_key_for_route_suffix(
    session: Session,
    language: str,
    route_suffix: str,
    *,
    registry_lookup: Callable[[str], str | None],
) -> str | None:
    key = registry_lookup(route_suffix)
    if key is not None:
        return key
    suffix = str(route_suffix or "").strip()
    if not suffix:
        return None
    for chapter in list_custom_chapters_for_language(session, language):
        if chapter.chapter_key == suffix:
            return suffix
    return None


def custom_showcase_collection(session: Session, language: str, chapter_key: str):
    from types import SimpleNamespace

    title, description = resolve_chapter_display(session, language, chapter_key)
    return SimpleNamespace(
        chapter_key=chapter_key,
        title_ru=title,
        description_ru=description,
        yaml_chapter_id=chapter_key,
        study_order_tc=(),
        title_prefix="",
    )


def _invalidate_caches() -> None:
    try:
        from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache

        invalidate_showcase_task_index_cache()
    except Exception:
        pass


def delete_custom_chapter(
    session: Session,
    *,
    chapter_key: str,
    language: str | None = None,
) -> None:
    """Remove a teacher-created chapter row when it has no tasks."""
    key = str(chapter_key or "").strip()
    if not key:
        raise ValueError("chapter_key is required")

    lang = str(language or "").strip().lower()
    row = _chapter_row(session, lang, key) if lang else None
    if row is None:
        row = session.execute(
            select(CurriculumChapterMeta)
            .where(CurriculumChapterMeta.chapter_key == key)
            .order_by(CurriculumChapterMeta.language)
        ).scalars().first()

    if row is None:
        raise ValueError("chapter not found")
    if not row.is_custom:
        raise ValueError("cannot delete registry chapter")
    if count_tasks_for_chapter(session, key) > 0:
        raise ValueError("chapter has tasks")

    session.delete(row)
    session.flush()
    _invalidate_caches()


def persist_chapter_sort_orders(
    session: Session,
    *,
    teacher_id: int,
    rank_by_key: dict[str, int],
) -> None:
    """Sync curriculum_chapter_meta.sort_order after teacher reorders chapters."""
    if not rank_by_key:
        return

    registry = _registry_chapters(None)
    for chapter_key, sort_order in rank_by_key.items():
        key = str(chapter_key).strip()
        if not key:
            continue
        row = session.execute(
            select(CurriculumChapterMeta)
            .where(CurriculumChapterMeta.chapter_key == key)
            .order_by(CurriculumChapterMeta.language)
        ).scalars().first()
        if row is not None:
            row.sort_order = int(sort_order)
            continue

        reg_lang = _GLOBAL_LANGUAGE
        reg: tuple[str, str, int] | None = None
        for (lang, reg_key), value in registry.items():
            if reg_key == key:
                reg = value
                reg_lang = lang
                break
        if reg is None:
            continue
        title, description, _default_order = reg
        session.add(
            CurriculumChapterMeta(
                language=reg_lang,
                chapter_key=key,
                title=title,
                description=description,
                sort_order=int(sort_order),
                is_custom=False,
                teacher_id=teacher_id,
            )
        )
    session.flush()
    _invalidate_caches()
