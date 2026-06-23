"""Readable curriculum labels for student UI (API-driven, no frontend hardcoding)."""

from __future__ import annotations

from typing import Any

from application.curriculum.core.curriculum_service import CurriculumService
from domain.learning.curriculum.exceptions import CurriculumNotFoundError

LANGUAGE_LABELS: dict[str, str] = {
    "pascal": "Pascal",
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
}

ACTION_LABELS: dict[str, str] = {
    "recognize": "Распознать",
    "assemble": "Собрать",
    "translate": "Перенести",
    "analyze": "Разобрать код",
    "debug": "Исправить",
    "implement": "Написать",
}

ACTION_SKILL_LABELS_RU: dict[str, str] = {
    "recognize": "Распознать конструкцию",
    "assemble": "Собрать из блоков",
    "translate": "Перенести на Pascal",
    "analyze": "Предсказать результат",
    "debug": "Исправить ошибку",
    "implement": "Написать решение",
}

PYTHON_ACTION_SKILL_LABELS_RU: dict[str, str] = {
    "recognize": "Распознать конструкцию",
    "assemble": "Собрать из блоков",
    "translate": "Перенести на Python",
    "analyze": "Предсказать результат",
    "debug": "Исправить ошибку",
    "implement": "Написать решение на Python",
}

ACTION_DESCRIPTIONS_RU: dict[str, str] = {
    "recognize": "Определите, какая конструкция используется в коде или описании.",
    "assemble": "Расставьте блоки, чтобы получить правильную программу.",
    "translate": "Переведите знакомую конструкцию из Python/C++/Java/C# в Pascal.",
    "analyze": "Что выведет программа?",
    "debug": "Найдите и исправьте ошибку в программе.",
    "implement": "Напишите программу на Pascal по условию.",
}

PYTHON_ACTION_DESCRIPTIONS_RU: dict[str, str] = {
    "recognize": "Определите, какая конструкция используется в коде или описании.",
    "assemble": "Расставьте блоки, чтобы получить правильную программу на Python.",
    "translate": "Переведите конструкцию из выбранного языка (Pascal/C++/Java/C#) в Python.",
    "analyze": "Что выведет программа?",
    "debug": "Найдите и исправьте ошибку в Python-коде.",
    "implement": "Напишите программу на Python по условию.",
}

CPP_ACTION_SKILL_LABELS_RU: dict[str, str] = {
    "recognize": "Распознать конструкцию",
    "assemble": "Собрать из блоков",
    "translate": "Перенести на C++",
    "analyze": "Предсказать результат",
    "debug": "Исправить ошибку",
    "implement": "Написать решение на C++",
}

CPP_ACTION_DESCRIPTIONS_RU: dict[str, str] = {
    "recognize": "Определите, какая конструкция C++ используется в коде или описании.",
    "assemble": "Расставьте блоки, чтобы получить правильную программу на C++.",
    "translate": "Переведите знакомую конструкцию (Python/Pascal/Java/C#) в синтаксис C++.",
    "analyze": "Что выведет программа?",
    "debug": "Найдите и исправьте ошибку в C++-коде.",
    "implement": "Напишите программу на C++ по условию.",
}


def get_action_label(action: str) -> str:
    return ACTION_LABELS.get(action, action.replace("_", " ").title() if action else "")


def _normalize_language(language: str | None) -> str:
    return str(language or "pascal").strip().lower()


def get_action_skill_label(action: str, *, language: str | None = None) -> str:
    lang = _normalize_language(language)
    if lang == "python":
        return PYTHON_ACTION_SKILL_LABELS_RU.get(action, get_action_label(action))
    if lang == "cpp":
        return CPP_ACTION_SKILL_LABELS_RU.get(action, get_action_label(action))
    return ACTION_SKILL_LABELS_RU.get(action, get_action_label(action))


def get_action_description_ru(action: str, *, language: str | None = None) -> str:
    lang = _normalize_language(language)
    if lang == "python":
        return PYTHON_ACTION_DESCRIPTIONS_RU.get(action, "")
    if lang == "cpp":
        return CPP_ACTION_DESCRIPTIONS_RU.get(action, "")
    return ACTION_DESCRIPTIONS_RU.get(action, "")


def build_curriculum_display(
    *,
    language: str,
    learning_concept_id: str,
    technical_concept_id: str,
    action: str,
    exercise_pattern_id: str,
) -> dict[str, Any]:
    lang = language.strip().lower()
    try:
        bundle = CurriculumService(lang).get_bundle()
    except CurriculumNotFoundError:
        lang = "pascal"
        bundle = CurriculumService(lang).get_bundle()
    lc = bundle.learning_concept_by_id(learning_concept_id)
    tc = bundle.technical_concept_by_id(technical_concept_id)

    language_label = LANGUAGE_LABELS.get(lang, lang.title())
    theme_name_ru = lc.name_ru if lc else learning_concept_id
    subtopic_name_ru = tc.name_ru if tc else technical_concept_id
    action_label = get_action_label(action)
    action_skill_label = get_action_skill_label(action, language=lang)
    action_description_ru = get_action_description_ru(action, language=lang)

    return {
        "language": lang,
        "language_label": language_label,
        "theme_name_ru": theme_name_ru,
        "subtopic_name_ru": subtopic_name_ru,
        "technical_concept_id": technical_concept_id,
        "action": action,
        "action_label": action_label,
        "action_skill_label": action_skill_label,
        "action_description_ru": action_description_ru,
        "context_line_ru": f"{language_label} · {theme_name_ru} · {subtopic_name_ru}",
        "instruction_ru": action_description_ru,
        "exercise_pattern_id": exercise_pattern_id,
    }


def build_curriculum_display_from_primary_link(primary_link: dict[str, Any]) -> dict[str, Any]:
    return build_curriculum_display(
        language=str(primary_link.get("language") or "pascal"),
        learning_concept_id=str(primary_link["learning_concept_id"]),
        technical_concept_id=str(primary_link["technical_concept_id"]),
        action=str(primary_link.get("action") or ""),
        exercise_pattern_id=str(primary_link["exercise_pattern_id"]),
    )


def attach_curriculum_display_to_task(
    db: Any,
    task_id: int,
    task: dict[str, Any],
    *,
    learning_language: str | None = None,
    source_language: str | None = None,
    task_row: TaskModel | None = None,
) -> dict[str, Any]:
    """Add `curriculum` block to task payload when a primary link exists."""
    from application.curriculum.collections.curriculum_collection_navigation import (
        build_collection_navigation_for_task,
    )
    from application.curriculum.display.showcase_display import (
        enrich_pascal_showcase_hints,
        sanitize_public_task_payload,
    )
    from application.curriculum.mirror.pedagogical_task_store import (
        apply_learning_language_to_payload,
        learning_language_description,
        resolved_showcase,
        sync_assembly_fields_for_language,
    )
    from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService
    from infrastructure.db.models.task import Task as TaskModel

    row = task_row if task_row is not None else (db.get(TaskModel, task_id) if db is not None else None)
    raw_showcase = dict((row.code_examples or {}).get("curriculum_showcase") or {}) if row else {}
    from application.tasks.services.teacher_assembly_preservation import (
        has_teacher_assembly_override,
    )
    from application.tasks.services.teacher_editor_public_payload import (
        apply_teacher_editor_public_payload,
    )

    teacher_override = has_teacher_assembly_override(row.code_examples if row else None)

    effective_learning = str(learning_language or "").strip().lower() or None
    if not effective_learning:
        for source in (
            task.get("target_language"),
            task.get("language"),
            (raw_showcase or {}).get("target_language"),
        ):
            candidate = str(source or "").strip().lower()
            if candidate in {"pascal", "python", "cpp", "csharp", "java"}:
                effective_learning = candidate
                break

    enriched = apply_learning_language_to_payload(
        dict(task),
        effective_learning,
        showcase=raw_showcase or None,
    )
    if effective_learning:
        enriched["requested_target_language"] = effective_learning
        enriched["target_language"] = effective_learning
        enriched["language"] = effective_learning
    enriched = sanitize_public_task_payload(enriched)
    display_lang = (
        str(learning_language or enriched.get("target_language") or enriched.get("language") or "")
        .strip()
        .lower()
    )
    if display_lang:
        enriched = sync_assembly_fields_for_language(enriched, display_lang)
    if db is None:
        return enriched

    link_service = TaskCurriculumLinkService(db)
    has_curriculum_link, primary_link = link_service.primary_link_for_existing_task(
        task_id,
        language=learning_language,
    )
    if not has_curriculum_link or not primary_link:
        if learning_language and raw_showcase and not teacher_override:
            description = learning_language_description(raw_showcase, learning_language)
            if description:
                enriched["description"] = description
        navigation = build_collection_navigation_for_task(
            db,
            task_id,
            learning_language=learning_language,
        )
        if navigation:
            enriched.setdefault("curriculum", {})["navigation"] = navigation
        if display_lang:
            enriched = sync_assembly_fields_for_language(enriched, display_lang)
        enriched = _attach_pedagogical_metadata(enriched, raw_showcase, learning_language=learning_language)
        if row is not None:
            enriched = apply_teacher_editor_public_payload(
                row, enriched, learning_language=learning_language
            )
        from application.curriculum.display.showcase_display import finalize_student_task_payload

        return finalize_student_task_payload(
            enriched,
            source_language=source_language,
            target_language=display_lang or effective_learning,
        )

    display_lang = (
        learning_language or primary_link.get("language") or "pascal"
    ).strip().lower()
    resolved_for_display = (
        resolved_showcase(dict(raw_showcase), learning_language)
        if learning_language
        else dict(raw_showcase)
    )
    curriculum = build_curriculum_display(
        language=display_lang,
        learning_concept_id=str(primary_link["learning_concept_id"]),
        technical_concept_id=str(
            resolved_for_display.get("technical_concept_id")
            or primary_link["technical_concept_id"]
        ),
        action=str(
            (raw_showcase.get("primary_action") if teacher_override else None)
            or resolved_for_display.get("primary_action")
            or primary_link.get("action")
            or ""
        ),
        exercise_pattern_id=str(
            resolved_for_display.get("exercise_pattern_id") or primary_link["exercise_pattern_id"]
        ),
    )
    if row is not None:
        showcase = (
            dict(raw_showcase)
            if teacher_override
            else resolved_showcase(dict(raw_showcase), learning_language)
        )
        if not teacher_override:
            description = learning_language_description(raw_showcase, learning_language)
            if description:
                enriched["description"] = description
        slot_id = showcase.get("slot_id") or raw_showcase.get("slot_id")
        if slot_id:
            curriculum["slot_id"] = str(slot_id)
        pattern_id = (
            showcase.get("slot_pattern_id")
            or showcase.get("exercise_pattern_id")
            or curriculum.get("exercise_pattern_id")
            or primary_link.get("exercise_pattern_id")
        )
        if pattern_id:
            curriculum["slot_pattern_id"] = str(pattern_id)
            curriculum["exercise_pattern_id"] = str(pattern_id)
        from application.curriculum.mirror.pedagogical_task_model import available_language_tracks

        learning_tracks = available_language_tracks(raw_showcase)
        if learning_tracks:
            curriculum["available_language_tracks"] = learning_tracks
        if showcase.get("flowchart_mode"):
            curriculum["flowchart_mode"] = str(showcase["flowchart_mode"])
        if isinstance(showcase, dict) and showcase:
            examples = dict(enriched.get("code_examples") or {})
            examples["curriculum_showcase"] = showcase
            enriched["code_examples"] = examples
            enriched["language"] = str(
                learning_language or showcase.get("target_language") or enriched.get("language") or ""
            ).lower() or enriched.get("language")
            enriched["target_language"] = enriched["language"]
            for key in (
                "expected_concept_ids",
                "pascal_features",
                "cpp_features",
                "slot_id",
                "task_format",
                "primary_action",
                "technical_concept_id",
            ):
                if showcase.get(key) is not None:
                    enriched[key] = showcase[key]
    previous_curriculum = dict(enriched.get("curriculum") or {})
    enriched["curriculum"] = {**previous_curriculum, **curriculum}
    navigation = build_collection_navigation_for_task(
        db,
        task_id,
        learning_language=learning_language,
    )
    if navigation:
        enriched["curriculum"]["navigation"] = navigation
    enriched = sync_assembly_fields_for_language(enriched, display_lang)
    enriched = _attach_pedagogical_metadata(enriched, raw_showcase, learning_language=learning_language)
    if row is not None:
        enriched = apply_teacher_editor_public_payload(
            row, enriched, learning_language=learning_language
        )
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    return finalize_student_task_payload(
        enriched,
        source_language=source_language,
        target_language=display_lang,
    )


def _attach_pedagogical_metadata(
    payload: dict[str, Any],
    raw_showcase: dict[str, Any],
    *,
    learning_language: str | None = None,
) -> dict[str, Any]:
    from application.curriculum.display.showcase_display import enrich_pascal_showcase_hints
    from application.curriculum.mirror.pedagogical_task_model import (
        available_language_tracks,
        concept_id_for_showcase,
    )
    from application.curriculum.mirror.pedagogical_task_store import (
        pedagogical_slot_id_from_showcase,
        resolved_showcase,
    )

    if not raw_showcase:
        return payload
    result = dict(payload)
    ped = pedagogical_slot_id_from_showcase(raw_showcase)
    if ped:
        result["pedagogical_slot_id"] = ped
    tracks = available_language_tracks(raw_showcase)
    if tracks:
        result["available_language_tracks"] = tracks
    resolved = resolved_showcase(raw_showcase, learning_language)
    concept = concept_id_for_showcase(resolved) or concept_id_for_showcase(raw_showcase)
    if concept:
        result["concept_id"] = concept
    if learning_language:
        result["target_language"] = learning_language.strip().lower()
    elif resolved.get("target_language"):
        result["target_language"] = resolved["target_language"]
    if resolved.get("collection_key"):
        result["chapter_key"] = resolved["collection_key"]
    if resolved.get("exercise_pattern_id"):
        result["exercise_pattern_id"] = resolved["exercise_pattern_id"]
    return enrich_pascal_showcase_hints(result)
