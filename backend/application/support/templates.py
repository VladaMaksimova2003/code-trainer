"""Static reply templates for support ticket creation (frontend chips)."""

from __future__ import annotations

from typing import Any

_CATEGORY_LABELS: dict[str, str] = {
    "task_content": "Ошибка в задании",
    "autograder": "Проблема с автопроверкой",
    "technical": "Техническая проблема",
    "account": "Аккаунт и доступ",
    "other": "Другое",
}

_TASK_STUDENT_TEMPLATES: list[dict[str, str]] = [
    {"id": "task_typo", "label": "Ошибка в условии", "draft": "В условии задания: "},
    {"id": "wrong_test", "label": "Неверный тест", "draft": "Тест №…: ожидается …, но …"},
    {"id": "unclear", "label": "Неясное условие", "draft": "Не понятно, что требуется: "},
    {"id": "other_task", "label": "Другое", "draft": ""},
]

_AUTOGRADER_STUDENT_TEMPLATES: list[dict[str, str]] = [
    {
        "id": "wrong_verdict",
        "label": "Верное решение не принято",
        "draft": "Моё решение должно быть верным, но автопроверка выдаёт: ",
    },
    {"id": "runtime_fail", "label": "Ошибка выполнения", "draft": "Код не выполняется: "},
    {"id": "other_auto", "label": "Другое", "draft": ""},
]

_TECHNICAL_TEMPLATES: list[dict[str, str]] = [
    {"id": "page_load", "label": "Не грузится страница", "draft": "Страница не загружается: "},
    {"id": "editor", "label": "Проблема с редактором", "draft": "Редактор кода: "},
    {"id": "submit_fail", "label": "Не отправляется решение", "draft": "Не удаётся отправить решение: "},
    {"id": "group_join", "label": "Не могу войти в группу", "draft": "Проблема с группой: "},
    {"id": "other_tech", "label": "Другое", "draft": ""},
]

_ACCOUNT_TEMPLATES: list[dict[str, str]] = [
    {"id": "login", "label": "Не могу войти", "draft": "Не получается войти в аккаунт: "},
    {"id": "blocked", "label": "Аккаунт заблокирован", "draft": "Мой аккаунт заблокирован: "},
    {"id": "progress", "label": "Пропал прогресс", "draft": "Пропал прогресс или данные: "},
    {"id": "other_account", "label": "Другое", "draft": ""},
]

_TEACHER_TECH_TEMPLATES: list[dict[str, str]] = [
    {"id": "task_save", "label": "Не сохраняется задание", "draft": "Не сохраняется или не публикуется задание: "},
    {"id": "analytics", "label": "Не грузится аналитика", "draft": "Проблема с аналитикой: "},
    {"id": "runner", "label": "Runner падает", "draft": "Runner падает на коде: "},
    {"id": "other_teacher", "label": "Другое", "draft": ""},
]

_CATEGORIES_BY_CONTEXT: dict[str, list[str]] = {
    "task": ["task_content", "autograder", "technical"],
    "general": ["technical", "account", "other"],
}

_CATEGORIES_STUDENT: list[str] = [
    "task_content",
    "autograder",
    "technical",
    "account",
    "other",
]

_CATEGORIES_TEACHER: list[str] = [
    "technical",
    "account",
    "other",
]


def _category_meta(category: str) -> dict[str, Any]:
    templates: list[dict[str, str]]
    if category == "task_content":
        templates = _TASK_STUDENT_TEMPLATES
    elif category == "autograder":
        templates = _AUTOGRADER_STUDENT_TEMPLATES
    elif category == "technical":
        templates = _TECHNICAL_TEMPLATES
    elif category == "account":
        templates = _ACCOUNT_TEMPLATES
    else:
        templates = [{"id": "free", "label": "Свободный текст", "draft": ""}]
    return {
        "id": category,
        "label": _CATEGORY_LABELS.get(category, category),
        "templates": templates,
    }


def get_support_templates(*, role: str, context: str = "general") -> dict[str, Any]:
    role_norm = (role or "student").strip().lower()
    context_norm = (context or "general").strip().lower()

    if role_norm == "teacher":
        categories = list(_CATEGORIES_TEACHER)
        if context_norm == "task":
            categories = ["task_content", "autograder", *categories]
    else:
        if context_norm == "task":
            categories = list(_CATEGORIES_BY_CONTEXT["task"])
        else:
            categories = list(_CATEGORIES_STUDENT)

    items = [_category_meta(cat) for cat in categories]
    if role_norm == "teacher":
        for item in items:
            if item["id"] == "technical":
                item["templates"] = _TEACHER_TECH_TEMPLATES

    return {"context": context_norm, "role": role_norm, "categories": items}
