"""Mirror mapping between Pascal v3.1.1 and Python v1 curriculum slot ids."""

from __future__ import annotations

import re
from typing import Literal

CurriculumLanguage = Literal["pascal", "python"]
ALL_CURRICULUM_LANGUAGES = ("python", "pascal", "cpp", "csharp", "java")
ALGO_V4_SLOT_RE = re.compile(r"^(pas_|py_|cpp_|cs_|java_)(\d+)$", re.I)
ALGO_V4_PREFIX_BY_LANG = {
    "pascal": "pas_",
    "python": "py_",
    "cpp": "cpp_",
    "csharp": "cs_",
    "java": "java_",
}

PASCAL_TO_PY_PREFIX: dict[str, str] = {
    "psk": "pyk",
    "typ": "pyt",
    "io": "pyi",
    "exp": "pye",
    "cnd": "pyc",
    "lop": "pyl",
    "fn": "pyf",
    "prc": "pypr",
    "arr": "pya",
    "dyn": "pyd",
    "str": "pys",
    "rec": "pyr",
    "fil": "pyfl",
    "unt": "pym",
    "rcu": "pyrc",
    "oop": "pyo",
    "exc": "pyx",
    "pit": "pypit",
    "cdg": "pydg",
}

PY_TO_PASCAL_PREFIX: dict[str, str] = {value: key for key, value in PASCAL_TO_PY_PREFIX.items()}

# Chapters mirrored across languages despite python-only curriculum bucket.
_CROSS_LANGUAGE_CHAPTER_MIRROR: frozenset[tuple[str, str]] = frozenset({
    ("error_handling", "exceptions"),
})

# Chapters without a 1:1 mirror (python-only or pascal-only).
PYTHON_ONLY_CHAPTERS = frozenset({"comprehensions", "exceptions", "pro_python", "advanced_python", "typing_diagnostics", "capstones"})
PASCAL_ONLY_CHAPTERS = frozenset()

CHAPTER_MIRROR: dict[str, str] = {
    "program_skeleton": "program_entry",
    "program_entry": "program_skeleton",
    "typed_variables": "typed_variables",
    "io": "io",
    "expressions": "expressions",
    "conditions": "conditions",
    "loops": "loops",
    "functions": "functions",
    "procedures": "parameters",
    "parameters": "procedures",
    "static_arrays": "lists",
    "lists": "static_arrays",
    "dynamic_arrays": "dynamic_lists",
    "dynamic_lists": "dynamic_arrays",
    "strings": "strings",
    "records": "mappings",
    "mappings": "records",
    "files": "files",
    "units": "modules",
    "modules": "units",
    "recursion": "recursion",
    "oop": "oop",
    "error_handling": "exceptions",
    "exceptions": "error_handling",
    "pascal_pitfalls": "python_pitfalls",
    "python_pitfalls": "pascal_pitfalls",
    "compiler_diagnostics": "python_diagnostics",
    "python_diagnostics": "compiler_diagnostics",
}

PYTHON_ONLY_SLOTS = frozenset()  # see curriculum_slot_mirror_map.PYTHON_ONLY_SLOTS


def _python_only_slots() -> frozenset[str]:
    from application.curriculum.mirror.curriculum_slot_mirror_map import PYTHON_ONLY_SLOTS as _SLOTS

    return _SLOTS


def _slot_prefix(slot_id: str) -> str:
    if "_cap" in slot_id:
        return slot_id.rsplit("_cap", 1)[0].split("_")[0]
    return slot_id.split("_")[0]


def slot_language(slot_id: str) -> CurriculumLanguage | None:
    prefix = _slot_prefix(slot_id)
    if prefix in PASCAL_TO_PY_PREFIX:
        return "pascal"
    if prefix in PY_TO_PASCAL_PREFIX or prefix.startswith("py"):
        return "python"
    return None


def mirror_slot_id(slot_id: str, *, target: CurriculumLanguage) -> str | None:
    if not slot_id:
        return None
    python_only = _python_only_slots()
    if slot_id in python_only:
        return None
    from application.curriculum.mirror.curriculum_slot_mirror_map import (
        pascal_to_python_slot,
        python_to_pascal_slot,
    )

    source = slot_language(slot_id)
    if source is None or source == target:
        return None
    if source == "pascal" and target == "python":
        mapped = pascal_to_python_slot(slot_id)
        if mapped and mapped not in python_only:
            return mapped
        return None
    if source == "python" and target == "pascal":
        mapped = python_to_pascal_slot(slot_id)
        if mapped:
            return mapped
        return None
    return None


def is_algo_v4_slot(slot_id: str) -> bool:
    return bool(ALGO_V4_SLOT_RE.match(str(slot_id or "").strip()))


def mirror_slot_to_language(slot_id: str, target: str) -> str | None:
    match = ALGO_V4_SLOT_RE.match(str(slot_id or "").strip())
    lang = str(target or "").strip().lower()
    if not match or lang not in ALGO_V4_PREFIX_BY_LANG:
        return None
    prefix = ALGO_V4_PREFIX_BY_LANG[lang]
    return f"{prefix}{match.group(2)}"


def mirror_languages_for_slot(slot_id: str) -> list[str]:
    if is_algo_v4_slot(slot_id):
        return list(ALL_CURRICULUM_LANGUAGES)
    langs: list[str] = []
    source = slot_language(slot_id)
    if source:
        langs.append(source)
    if mirror_slot_id(slot_id, target="pascal"):
        if "pascal" not in langs:
            langs.append("pascal")
    if mirror_slot_id(slot_id, target="python"):
        if "python" not in langs:
            langs.append("python")
    return langs


def mirror_chapter_key(chapter_key: str, *, target: CurriculumLanguage) -> str | None:
    if target == "python" and chapter_key in PASCAL_ONLY_CHAPTERS:
        return None
    if target == "pascal" and chapter_key in PYTHON_ONLY_CHAPTERS:
        if (chapter_key, "error_handling") not in _CROSS_LANGUAGE_CHAPTER_MIRROR and (
            "error_handling",
            chapter_key,
        ) not in _CROSS_LANGUAGE_CHAPTER_MIRROR:
            return None
    mirrored = CHAPTER_MIRROR.get(chapter_key)
    if not mirrored:
        return None
    if target == "python" and mirrored in PYTHON_ONLY_CHAPTERS:
        if (chapter_key, mirrored) not in _CROSS_LANGUAGE_CHAPTER_MIRROR:
            return None
    if target == "pascal" and mirrored in PASCAL_ONLY_CHAPTERS:
        return None
    return mirrored


def neutralize_title(title: str) -> str:
    """Language-neutral display title for mirrored tasks."""
    result = str(title or "").strip()
    if "program … begin … end" in result:
        return "Каркас программы"
    replacements = [
        ("Pascal", ""),
        ("Python", ""),
        ("program/begin/end", "каркас программы"),
        ("Readln", "ввод"),
        ("Writeln", "вывод"),
    ]
    for old, new in replacements:
        result = result.replace(old, new)
    return " ".join(result.split())


def build_canonical_titles() -> dict[str, str]:
    """slot_id → shared neutral title (from Pascal catalog metadata)."""
    from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
        all_v311_task_records as all_pascal_records,
    )
    from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
        all_v311_task_records as all_python_records,
    )

    titles: dict[str, str] = {}
    for rec in all_pascal_records():
        canonical = neutralize_title(rec.title)
        titles[rec.slot_id] = canonical
        py_id = mirror_slot_id(rec.slot_id, target="python")
        if py_id:
            titles[py_id] = canonical
    for rec in all_python_records():
        if rec.slot_id not in titles:
            titles[rec.slot_id] = neutralize_title(rec.title)
    return titles


_CANONICAL_TITLES: dict[str, str] | None = None


def canonical_title_for_slot(slot_id: str | None) -> str | None:
    global _CANONICAL_TITLES
    if not slot_id:
        return None
    if _CANONICAL_TITLES is None:
        try:
            _CANONICAL_TITLES = build_canonical_titles()
        except Exception:
            _CANONICAL_TITLES = {}
    return _CANONICAL_TITLES.get(str(slot_id))
