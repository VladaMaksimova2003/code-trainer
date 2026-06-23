"""Load chapter-11 (files_modules) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "files_modules"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_COMMON_DESC = (
    "Программа читает или записывает файл и отделяет обработку данных от основного сценария."
)

# 81,84,85 assemble; 82,83 translation; 86,87,88 debug
_KIND_BY_PATTERN = {
    "task_081": "assemble",
    "task_082": "translation",
    "task_083": "translation",
    "task_084": "assemble",
    "task_085": "assemble",
    "task_086": "debug",
    "task_087": "debug",
    "task_088": "debug",
}

_FORMAT_BY_PATTERN = {
    "task_081": "сборка_программы",
    "task_082": "перевод_программы",
    "task_083": "перевод_программы",
    "task_084": "сборка_программы",
    "task_085": "сборка_программы",
    "task_086": "исправление",
    "task_087": "исправление",
    "task_088": "исправление",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_081": {
        "title": "Чтение чисел из файла",
        "short_goal": "Чтение чисел из файла.",
        "detailed_description": _COMMON_DESC,
    },
    "task_082": {
        "title": "Подсчёт строк файла",
        "short_goal": "Подсчёт строк файла.",
        "detailed_description": _COMMON_DESC,
    },
    "task_083": {
        "title": "Анализ CSV",
        "short_goal": "Анализ CSV.",
        "detailed_description": (
            "Файл input.csv содержит строки формата name,amount. Нужно вывести сумму amount."
        ),
    },
    "task_084": {
        "title": "Запись отчёта",
        "short_goal": "Запись отчёта.",
        "detailed_description": (
            "Прочитать числа из input.txt, посчитать сумму и записать её в report.txt."
        ),
    },
    "task_085": {
        "title": "Логирование событий",
        "short_goal": "Логирование событий.",
        "detailed_description": (
            "Вводится строка события. Нужно дописать её в файл log.txt и вывести logged."
        ),
    },
    "task_086": {
        "title": "Модуль сортировок",
        "short_goal": "Модуль сортировок.",
        "detailed_description": (
            "Прочитать числа из input.txt, отсортировать их и вывести по возрастанию. "
            "Логика сортировки вынесена в отдельную функцию."
        ),
    },
    "task_087": {
        "title": "Конфликт имён в модулях",
        "short_goal": "Конфликт имён в модулях.",
        "detailed_description": (
            "Есть своя функция countLines/count_lines, чтобы не путать её с библиотечными "
            "методами чтения файла. Нужно вывести количество строк в input.txt."
        ),
    },
    "task_088": {
        "title": "Итоговая: обработчик логов",
        "short_goal": "Итоговая: обработчик логов.",
        "detailed_description": (
            "Файл log.txt содержит строки формата level message, где level — INFO, WARN или ERROR. "
            "Нужно вывести количество ошибок и предупреждений: errors warnings."
        ),
    },
}


def _tests_from_course(pattern_id: str) -> list[dict[str, str]]:
    rows = json.loads(_COURSE_JSON.read_text(encoding="utf-8"))
    row = next(r for r in rows if r.get("pattern_id") == pattern_id)
    return [
        {"inputs": str(case.get("inputs", "")), "output": str(case.get("output", ""))}
        for case in row.get("test_cases") or []
    ]


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_085":
        return [
            {"inputs": "login\n", "output": "logged"},
            {"inputs": "error\n", "output": "logged"},
            {"inputs": "user action\n", "output": "logged"},
        ]
    return _tests_from_course(pattern_id)


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch11_user_codes.task_{task_num:03d}")


def _codes_from_module(mod, kind: str) -> dict[str, Any]:
    if kind == "debug":
        fixed = {
            "pascal": mod.FIXED_PASCAL,
            "python": mod.FIXED_PYTHON,
            "cpp": mod.FIXED_CPP,
            "csharp": mod.FIXED_CSHARP,
            "java": mod.FIXED_JAVA,
        }
        buggy = {
            "pascal": mod.BUGGY_PASCAL,
            "python": mod.BUGGY_PYTHON,
            "cpp": mod.BUGGY_CPP,
            "csharp": mod.BUGGY_CSHARP,
            "java": mod.BUGGY_JAVA,
        }
        return {"fixed": fixed, "buggy": buggy}
    codes = {
        "pascal": mod.PASCAL,
        "python": mod.PYTHON,
        "cpp": mod.CPP,
        "csharp": mod.CSHARP,
        "java": mod.JAVA,
    }
    return {"codes": codes}


def _difficulty_from_course(pattern_id: str) -> str:
    rows = json.loads(_COURSE_JSON.read_text(encoding="utf-8"))
    row = next(r for r in rows if r.get("pattern_id") == pattern_id)
    raw = str(row.get("difficulty") or "medium").strip().lower()
    if raw in {"easy", "medium", "hard"}:
        return raw
    mapping = {"легкий": "easy", "средний": "medium", "сложный": "hard"}
    return mapping.get(raw, "medium")


def build_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for task_num in range(81, 89):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        meta = dict(_USER_META[pattern_id])
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": _FORMAT_BY_PATTERN[pattern_id],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _tests_for_pattern(pattern_id),
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
