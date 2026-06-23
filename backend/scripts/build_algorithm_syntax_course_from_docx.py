#!/usr/bin/env python3
"""Parse algorithm-syntax course docx (128 tasks, 16 chapters) and emit catalog artifacts."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DEFAULT = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

LANGS = ["Pascal", "Python", "C++", "C#", "Java"]
LANG_KEYS = ["pascal", "python", "cpp", "csharp", "java"]
LANG_MAP = {
    "Pascal": "pascal",
    "Python": "python",
    "C++": "cpp",
    "C#": "csharp",
    "Java": "java",
}

CHAPTER_KEYS = [
    "algo_basics",
    "branches",
    "loops",
    "arrays_collections",
    "strings",
    "functions",
    "recursion",
    "search_sort",
    "aggregation",
    "maps",
    "files_modules",
    "stack_queue",
    "linked_lists",
    "trees_graphs",
    "oop",
    "inheritance_capstone",
]

FORMAT_MAP = {
    "Сборка по блокам полностью": ("сборка_программы", "assemble"),
    "Сборка по блокам": ("сборка_программы", "assemble"),
    "Сборка с плейсхолдерами": ("сборка_фрагмента", "assemble"),
    "Код с плейсхолдерами и допустимыми словами": ("сборка_фрагмента", "assemble"),
    "Перевод кода": ("перевод_программы", "implement"),
    "Перевод программы": ("перевод_программы", "implement"),
    "Исправление ошибок": ("исправление", "debug"),
    "Исправление ошибки": ("исправление", "debug"),
}

DIFFICULTY_MAP = {
    "легкий": "easy",
    "легкий.": "easy",
    "средний": "medium",
    "средний.": "medium",
    "сложный": "hard",
    "сложный.": "hard",
}

TASK_HEADER = re.compile(r"^Задача\s+(\d+)\.\s*(.+)$")
CHAPTER_HEADER = re.compile(r"^Глава\s+(\d+)\.\s*(.+)$")
NUMBERED_BLOCK = re.compile(r"^\[\d+\]\s*(.+)$")
LANG_COLON = re.compile(r"^(Pascal|Python|C\+\+|C#|Java):\s*$")
CODE_HINT = re.compile(
    r"\b(begin|program|var\b|def\b|#include|using\b|import\b|class\b|int main|public static)\b",
    re.I,
)

TC_HEADER = {"№", "Вход / данные", "Ожидаемый вывод / результат"}
CONCEPTS_HEADER = {"Язык", "expected_concept_ids"}
GAP_TABLE_HEADER = {
    "id",
    "Что пропущено",
    "Правильный ответ",
    "Варианты ответа",
    "answer",
    "options",
}
ERROR_TABLE_HEADER = {"№", "Ошибка"}
BLOCKS_TABLE_HEADER = {"№", "Блок"}


def paras(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    out: list[str] = []
    for para in root.iter(f"{W}p"):
        text = "".join(node.text or "" for node in para.iter(f"{W}t")).strip()
        if text:
            out.append(text)
    return out


def _is_lang(line: str) -> bool:
    return line in LANGS


def _lang_from_line(line: str) -> str | None:
    if line in LANG_MAP:
        return LANG_MAP[line]
    match = LANG_COLON.match(line)
    if match:
        return LANG_MAP.get(match.group(1))
    return None


def _is_lang_line(line: str) -> bool:
    return _lang_from_line(line) is not None


def _is_impl_boundary(line: str) -> bool:
    text = str(line or "").strip()
    return text.startswith("Реализация") or text.startswith("Материал")


def _looks_like_code(line: str) -> bool:
    text = str(line or "").strip()
    if not text:
        return False
    if text in GAP_TABLE_HEADER or text.startswith("Правильн") or text.startswith("Код с"):
        return False
    return bool(CODE_HINT.search(text)) or ":=" in text or "___" in text or "print(" in text


def _is_task_boundary(line: str) -> bool:
    return TASK_HEADER.match(line) is not None or CHAPTER_HEADER.match(line) is not None


def _parse_test_cases(lines: list[str], start: int) -> tuple[list[dict[str, str]], int]:
    cases: list[dict[str, str]] = []
    i = start
    while i < len(lines) and lines[i] in TC_HEADER:
        i += 1
    while i < len(lines):
        line = lines[i]
        if (
            line.startswith("Expected Concepts")
            or _is_impl_boundary(line)
            or _is_lang_line(line)
            or _is_task_boundary(line)
        ):
            break
        if line.isdigit():
            i += 1
            if i >= len(lines):
                break
            inputs = lines[i]
            i += 1
            if i >= len(lines):
                break
            output = lines[i]
            cases.append({"inputs": inputs, "output": output})
        i += 1
    return cases, i


def _parse_expected_concepts(lines: list[str], start: int) -> tuple[dict[str, list[str]], int]:
    concepts: dict[str, list[str]] = {}
    i = start
    while i < len(lines) and lines[i] in CONCEPTS_HEADER:
        i += 1
    while i < len(lines):
        line = lines[i]
        if _is_impl_boundary(line) or _is_task_boundary(line):
            break
        if _is_lang_line(line) and line.endswith(":"):
            break
        if line in LANG_MAP:
            lang = LANG_MAP[line]
            i += 1
            if i < len(lines) and lines[i] not in LANGS and not _is_impl_boundary(lines[i]):
                concepts[lang] = [c.strip() for c in lines[i].split(",") if c.strip()]
        i += 1
    return concepts, i


def _parse_numbered_blocks(lines: list[str], start: int) -> tuple[list[str], int]:
    blocks: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if _is_lang_line(line) or _is_task_boundary(line):
            break
        match = NUMBERED_BLOCK.match(line)
        if match:
            blocks.append(match.group(1).strip())
            i += 1
            continue
        if blocks:
            break
        if line.startswith("Блоки для сборки") or line in BLOCKS_TABLE_HEADER:
            i += 1
            continue
        if not blocks and not line.startswith("["):
            i += 1
            continue
        break
    return blocks, i


def _skip_table_header(lines: list[str], i: int, header: set[str]) -> int:
    while i < len(lines) and lines[i] in header:
        i += 1
    return i


def _parse_assembly_blocks(lines: list[str], start: int) -> tuple[list[str], int]:
    blocks: list[str] = []
    i = start
    if i < len(lines) and lines[i].startswith("Блоки для сборки"):
        i += 1
    i = _skip_table_header(lines, i, BLOCKS_TABLE_HEADER)
    while i < len(lines):
        line = lines[i]
        if _is_lang_line(line) or _is_task_boundary(line):
            break
        if line.isdigit():
            i += 1
            if i < len(lines):
                blocks.append(lines[i])
                i += 1
        else:
            i += 1
    return blocks, i


def _parse_gap_table(lines: list[str], start: int) -> tuple[list[dict], int]:
    gaps: list[dict] = []
    i = _skip_table_header(lines, start, GAP_TABLE_HEADER)
    while i < len(lines):
        line = lines[i]
        if _is_lang_line(line) or _is_task_boundary(line):
            break
        if re.match(r"^p\d+$", line):
            gap_id = line
            i += 1
            label = lines[i] if i < len(lines) else ""
            i += 1
            answer = lines[i] if i < len(lines) else ""
            i += 1
            variants_raw = lines[i] if i < len(lines) else ""
            i += 1
            variants = [v.strip() for v in re.split(r"[;,]", variants_raw) if v.strip()]
            gaps.append(
                {
                    "id": gap_id,
                    "label": label,
                    "correct": answer,
                    "answer": answer,
                    "variants": variants,
                }
            )
        else:
            i += 1
    return gaps, i


_GLUE_KEYWORDS = ("print", "writeln", "write", "readln", "input", "int", "return", "elif", "else")


def _next_bare_placeholder_pos(text: str, start: int = 0) -> int:
    i = start
    while i <= len(text) - 3:
        if text[i : i + 3] != "___":
            i += 1
            continue
        if i > 0 and text[i - 1].isalnum():
            i += 1
            continue
        if i + 3 < len(text) and text[i + 3].isalnum():
            rest = text[i + 3 :].lower()
            if any(rest.startswith(kw) for kw in _GLUE_KEYWORDS):
                if i == 0 or text[i - 1] in " \t=:(":
                    return i
            i += 1
            continue
        return i
        i += 1
    return -1


def _normalize_placeholder_markers(code: str, gaps: list[dict]) -> str:
    out = str(code or "")
    gap_idx = 0
    search_from = 0
    while gap_idx < len(gaps):
        pos = _next_bare_placeholder_pos(out, search_from)
        if pos < 0:
            break
        gid = str(gaps[gap_idx].get("id") or f"p{gap_idx + 1}")
        token = f"___{gid}___"
        out = out[:pos] + token + out[pos + 3 :]
        search_from = pos + len(token)
        gap_idx += 1
    return out


def _parse_placeholder_section(lines: list[str], start: int) -> tuple[str, list[dict], int]:
    code = ""
    gaps: list[dict] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if _is_lang_line(line) or _is_task_boundary(line):
            return "", [], i
        if line == "Код с плейсхолдерами:":
            i += 1
            if i < len(lines):
                code = lines[i]
                i += 1
            break
        if "___" in line and _looks_like_code(line):
            code = line
            i += 1
            break
        i += 1
    while i < len(lines):
        line = lines[i]
        if line.startswith("Правильн") or line.startswith("Какие блоки"):
            i += 1
            gaps, i = _parse_gap_table(lines, i)
            break
        if re.match(r"^p\d+$", line):
            gaps, i = _parse_gap_table(lines, i)
            break
        if _is_lang_line(line) or _is_task_boundary(line):
            break
        i += 1
    if code and gaps:
        code = _normalize_placeholder_markers(code, gaps)
    return code, gaps, i


def _parse_translation_code(lines: list[str], start: int) -> tuple[str, int]:
    i = start
    while i < len(lines):
        line = lines[i]
        if _is_lang_line(line) or _is_task_boundary(line):
            break
        if (
            line.startswith("Исходный язык")
            or line.startswith("Реализация")
            or line.startswith("Материал")
        ):
            i += 1
            continue
        if _looks_like_code(line):
            return line, i + 1
        i += 1
    return "", i


def _parse_debug_codes(lines: list[str], start: int) -> tuple[str, str, list[str], int]:
    buggy = ""
    fixed = ""
    errors: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if _is_lang_line(line) or _is_task_boundary(line):
            break
        if line == "Код с ошибками:":
            i += 1
            if i < len(lines):
                buggy = lines[i]
                i += 1
            continue
        if line == "Правильный вариант:":
            i += 1
            if i < len(lines):
                fixed = lines[i]
                i += 1
            continue
        if line.startswith("Список ошибок"):
            i += 1
            i = _skip_table_header(lines, i, ERROR_TABLE_HEADER)
            while i < len(lines):
                inner = lines[i]
                if _is_lang_line(inner) or _is_task_boundary(inner):
                    break
                if inner.isdigit():
                    i += 1
                    if i < len(lines):
                        errors.append(lines[i])
                        i += 1
                else:
                    i += 1
            continue
        if line.startswith("Ошибк"):
            errors.append(line.split(":", 1)[-1].strip() or line)
            i += 1
            continue
        if not buggy and _looks_like_code(line):
            buggy = line
            i += 1
            continue
        i += 1
    return buggy, fixed, errors, i


def _fill_placeholders(code: str, gaps: list[dict]) -> str:
    out = code
    for gap in gaps:
        gid = str(gap.get("id") or "")
        correct = str(gap.get("correct") or gap.get("answer") or "")
        if not gid or not correct:
            continue
        out = out.replace(f"___{gid}___", correct)
    out = re.sub(r"(\S)(print\s*\()", r"\1\n\2", out, flags=re.I)
    out = re.sub(r"(\S)(writeln\b)", r"\1\n\2", out, flags=re.I)
    return out


def _reference_for_lang(impl: dict, lang: str) -> str:
    if impl.get("fixed_code"):
        return impl["fixed_code"]
    if impl.get("translation_code"):
        return impl["translation_code"]
    if impl.get("assembly_blocks"):
        from application.curriculum.content.v4_assembly_builder import canonical_assembly_blocks

        blocks = canonical_assembly_blocks(impl["assembly_blocks"], lang)
        return "\n".join(blocks)
    if impl.get("placeholder_code"):
        return _fill_placeholders(impl["placeholder_code"], impl.get("gaps") or [])
    return ""


def _parse_language_impl(lines: list[str], start: int, format_type: str) -> tuple[dict, int]:
    impl: dict = {
        "assembly_blocks": [],
        "placeholder_code": "",
        "gaps": [],
        "translation_code": "",
        "buggy_code": "",
        "fixed_code": "",
        "error_descriptions": [],
    }
    i = start
    if format_type == "assemble_full":
        blocks, i = _parse_numbered_blocks(lines, i)
        if not blocks:
            blocks, i = _parse_assembly_blocks(lines, i)
        impl["assembly_blocks"] = blocks
    elif format_type == "assemble_placeholder":
        code, gaps, i = _parse_placeholder_section(lines, i)
        impl["placeholder_code"] = code
        impl["gaps"] = gaps
    elif format_type == "translation":
        code, i = _parse_translation_code(lines, i)
        impl["translation_code"] = code
    elif format_type == "debug":
        buggy, fixed, errors, i = _parse_debug_codes(lines, i)
        impl["buggy_code"] = buggy
        impl["fixed_code"] = fixed
        impl["error_descriptions"] = errors
    return impl, i


def _format_type_key(fmt_ru: str) -> str:
    fmt = str(fmt_ru or "").strip()
    norm, action = FORMAT_MAP.get(fmt, ("", ""))
    if action == "assemble":
        if "фрагмента" in norm or "плейсхолдер" in fmt.lower():
            return "assemble_placeholder"
        return "assemble_full"
    if action == "implement":
        return "translation"
    if action == "debug":
        return "debug"
    if fmt == "Сборка по блокам полностью":
        return "assemble_full"
    if fmt == "Сборка с плейсхолдерами":
        return "assemble_placeholder"
    if fmt == "Перевод кода":
        return "translation"
    if fmt == "Исправление ошибок":
        return "debug"
    return "unknown"


def parse_course(lines: list[str]) -> tuple[list[dict], dict[str, str], list[str]]:
    chapters: dict[int, str] = {}
    chapter_titles: dict[str, str] = {}
    tasks: list[dict] = []
    failures: list[str] = []

    i = 0
    current_chapter_key: str | None = None
    while i < len(lines):
        ch_match = CHAPTER_HEADER.match(lines[i])
        if ch_match:
            ch_num = int(ch_match.group(1))
            ch_title = ch_match.group(2).strip()
            if 1 <= ch_num <= len(CHAPTER_KEYS):
                current_chapter_key = CHAPTER_KEYS[ch_num - 1]
                chapters[ch_num] = current_chapter_key
                chapter_titles[current_chapter_key] = ch_title
            else:
                failures.append(f"Unexpected chapter number {ch_num}: {ch_title}")
            i += 1
            continue

        task_match = TASK_HEADER.match(lines[i])
        if not task_match:
            i += 1
            continue

        task_num = int(task_match.group(1))
        raw_title = task_match.group(2).strip()
        title = raw_title
        i += 1

        short_goal = ""
        detailed = ""
        fmt_ru = ""
        difficulty_ru = ""
        test_cases: list[dict[str, str]] = []
        expected_concepts: dict[str, list[str]] = {}
        implementations: dict[str, dict] = {k: {} for k in LANG_KEYS}

        while i < len(lines):
            if TASK_HEADER.match(lines[i]) or CHAPTER_HEADER.match(lines[i]):
                break

            line = lines[i]
            if line.startswith("Краткое условие:"):
                short_goal = line.split(":", 1)[1].strip()
            elif line.startswith("Подробное условие:"):
                detailed = line.split(":", 1)[1].strip()
            elif line.startswith("Тип реализации:"):
                fmt_ru = line.split(":", 1)[1].strip()
            elif line.startswith("Сложность:"):
                difficulty_ru = line.split(":", 1)[1].strip().rstrip(".")
            elif line == "Тест-кейсы:":
                test_cases, i = _parse_test_cases(lines, i + 1)
                continue
            elif line.startswith("Expected Concepts"):
                expected_concepts, i = _parse_expected_concepts(lines, i + 1)
                continue
            elif _is_impl_boundary(line):
                i += 1
                continue
            elif (lang := _lang_from_line(line)) is not None:
                fmt_key = _format_type_key(fmt_ru)
                impl, i = _parse_language_impl(lines, i + 1, fmt_key)
                implementations[lang] = impl
                continue
            i += 1

        if not current_chapter_key:
            ch_idx = (task_num - 1) // 8
            if ch_idx < len(CHAPTER_KEYS):
                current_chapter_key = CHAPTER_KEYS[ch_idx]

        fmt_ru_norm, action = FORMAT_MAP.get(fmt_ru.strip(), ("", ""))
        difficulty = DIFFICULTY_MAP.get(
            difficulty_ru.strip().rstrip("."),
            difficulty_ru.strip().rstrip(".") or "medium",
        )
        pattern_id = f"task_{task_num:03d}"

        fmt_key = _format_type_key(fmt_ru)
        if fmt_key == "assemble_full":
            from application.curriculum.content.v4_assembly_builder import canonical_assembly_blocks

            for lang in LANG_KEYS:
                impl = implementations[lang]
                blocks = impl.get("assembly_blocks") or []
                if blocks:
                    impl["assembly_blocks"] = canonical_assembly_blocks(blocks, lang)

        reference_codes = {lang: _reference_for_lang(implementations[lang], lang) for lang in LANG_KEYS}

        from application.curriculum.content.v4_code_format import format_reference_code
        from application.curriculum.validation.expected_concept_checker import (
            prune_expected_concepts_for_code,
        )

        for lang in LANG_KEYS:
            raw_ref = reference_codes.get(lang) or ""
            if raw_ref and "\n" in raw_ref and fmt_key == "assemble_full":
                formatted_ref = raw_ref
            else:
                formatted_ref = format_reference_code(raw_ref, lang) if raw_ref else ""
            reference_codes[lang] = formatted_ref or raw_ref
            expected_concepts[lang] = prune_expected_concepts_for_code(
                expected_concepts.get(lang) or [],
                reference_codes[lang],
                lang,
            )

        task_issues: list[str] = []
        if not fmt_ru_norm:
            task_issues.append(f"missing/unknown format '{fmt_ru}'")
        if not test_cases:
            task_issues.append("no test cases")
        if not any(expected_concepts.get(lang) for lang in LANG_KEYS):
            task_issues.append("no expected concepts")
        for lang in LANG_KEYS:
            impl = implementations[lang]
            fmt_key = _format_type_key(fmt_ru)
            if fmt_key == "assemble_full" and not impl.get("assembly_blocks"):
                task_issues.append(f"{lang}: no assembly blocks")
            elif fmt_key == "assemble_placeholder" and not impl.get("placeholder_code"):
                task_issues.append(f"{lang}: no placeholder code")
            elif fmt_key == "translation" and not impl.get("translation_code"):
                task_issues.append(f"{lang}: no translation code")
            elif fmt_key == "debug" and not impl.get("fixed_code"):
                task_issues.append(f"{lang}: no fixed code")
        if task_issues:
            failures.append(f"task {task_num}: {', '.join(task_issues)}")

        primary_concepts = expected_concepts.get("pascal") or next(
            (expected_concepts[l] for l in LANG_KEYS if expected_concepts.get(l)),
            [],
        )

        from application.curriculum.content.v4_test_cases_io import normalize_test_cases_list

        ref_for_tc = reference_codes.get("python") or reference_codes.get("pascal") or ""
        test_cases = normalize_test_cases_list(
            test_cases,
            reference_code=ref_for_tc,
            language="python",
        )

        tasks.append(
            {
                "task_num": task_num,
                "pattern_id": pattern_id,
                "chapter_key": current_chapter_key or CHAPTER_KEYS[0],
                "title": title,
                "raw_title": raw_title,
                "short_goal": short_goal,
                "detailed_description": detailed or short_goal or title,
                "format_ru": fmt_ru_norm,
                "format_raw": fmt_ru,
                "action": action,
                "difficulty": difficulty,
                "difficulty_ru": difficulty_ru,
                "test_cases": test_cases,
                "expected_concepts": expected_concepts,
                "expected_concepts_primary": primary_concepts,
                "implementations": implementations,
                "reference_codes": reference_codes,
            }
        )

    return tasks, chapter_titles, failures


_PLACEHOLDER_GAP_PLACEHOLDER = frozenset({"условие", "condition", ""})


def _infer_primary_gap_answer(reference_code: str) -> str | None:
    ref = str(reference_code or "")
    for pattern in (
        r"if\s+([^:\n]+?)\s+then",
        r"if\s*\(([^)]+)\)",
        r"if\s+([^:\n]+?):",
        r"if\s+([^<\n]+?<[^:\n]+)",
    ):
        match = re.search(pattern, ref, flags=re.I)
        if match:
            candidate = match.group(1).strip()
            if candidate and candidate not in _PLACEHOLDER_GAP_PLACEHOLDER:
                return candidate
    return None


def _repair_broken_placeholder_gaps(tasks: list[dict]) -> None:
    """Fix docx placeholder tables that use generic gap labels instead of real tokens."""
    gap_marker = re.compile(r"___p\d+___")

    for task in tasks:
        fmt_key = _format_type_key(str(task.get("format_raw") or task.get("format_ru") or ""))
        if fmt_key != "assemble_placeholder":
            continue

        implementations = task.get("implementations") or {}
        reference_codes = task.get("reference_codes") or {}

        for lang in LANG_KEYS:
            impl = dict(implementations.get(lang) or {})
            gaps = [dict(g) for g in (impl.get("gaps") or []) if isinstance(g, dict)]
            if not gaps:
                continue

            ref = str(reference_codes.get(lang) or _reference_for_lang(impl, lang) or "")
            placeholder = str(impl.get("placeholder_code") or "")

            for idx, gap in enumerate(gaps):
                answer = str(gap.get("answer") or gap.get("correct") or "").strip()
                if answer not in _PLACEHOLDER_GAP_PLACEHOLDER:
                    continue
                inferred = _infer_primary_gap_answer(ref)
                if inferred:
                    gap["answer"] = gap["correct"] = inferred
                    gap["variants"] = [
                        inferred,
                        inferred.replace("<", ">").replace(">=", "<"),
                        "n",
                        "target",
                    ]

            if placeholder and not gap_marker.search(placeholder) and ref:
                updated = ref
                for gap in gaps:
                    answer = str(gap.get("answer") or gap.get("correct") or "").strip()
                    gid = str(gap.get("id") or "")
                    if not answer or not gid or answer not in updated:
                        continue
                    updated = updated.replace(answer, f"___{gid}___", 1)
                if gap_marker.search(updated):
                    placeholder = updated

            impl["gaps"] = gaps
            impl["placeholder_code"] = placeholder
            implementations[lang] = impl

        task["implementations"] = implementations
        reference_codes.update(
            {lang: _reference_for_lang(implementations.get(lang) or {}, lang) for lang in LANG_KEYS}
        )
        task["reference_codes"] = reference_codes


def _repair_duplicate_task_metadata(tasks: list[dict]) -> None:
    """When docx repeats chapter-level text, prefix with task title instead of dropping detail."""
    from collections import defaultdict

    by_detail: dict[str, list[dict]] = defaultdict(list)
    by_short: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        detail = str(task.get("detailed_description") or "").strip()
        short = str(task.get("short_goal") or "").strip()
        if detail:
            by_detail[detail].append(task)
        if short:
            by_short[short].append(task)

    for task in tasks:
        title = str(task.get("title") or task.get("raw_title") or "").strip()
        if not title:
            continue
        detail = str(task.get("detailed_description") or "").strip()
        short = str(task.get("short_goal") or "").strip().rstrip(".")
        if detail and len(by_detail.get(detail, [])) > 1:
            if not detail.startswith(title):
                task["detailed_description"] = f"{title}. {detail}"
        if short and len(by_short.get(short, [])) > 1:
            if short.lower() == title.lower() or len(short) < 8:
                task["short_goal"] = f"{title}."
            elif not short.startswith(title):
                task["short_goal"] = f"{title}: {short}."


def _escape_py(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def emit_algo_v128_catalog(
    tasks: list[dict],
    chapter_titles: dict[str, str],
    out_path: Path,
) -> None:
    titles = {key: chapter_titles.get(key, key) for key in CHAPTER_KEYS}
    lines = [
        '"""Algorithm-syntax course catalog — 128 tasks, 16 chapters (generated from docx)."""',
        "from __future__ import annotations",
        "",
        "TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]",
        "",
        "V128_CORE_TASK_COUNT = 128",
        "",
        "V128_CHAPTER_KEYS: tuple[str, ...] = (",
    ]
    for key in CHAPTER_KEYS:
        lines.append(f'    "{key}",')
    lines.append(")")
    lines.append("")
    lines.append("V128_CHAPTER_ORDER: tuple[str, ...] = V128_CHAPTER_KEYS")
    lines.append("")
    lines.append("V128_CHAPTER_TITLES: dict[str, str] = {")
    for key in CHAPTER_KEYS:
        title = titles[key].replace('"', "'")
        lines.append(f'    "{key}": "{title}",')
    lines.append("}")
    lines.append("")
    lines.append("_TASK_INDEX: list[dict] = [")
    for task in sorted(tasks, key=lambda t: t["task_num"]):
        lines.append(
            f"    {{"
            f'"task_num": {task["task_num"]}, '
            f'"chapter_key": "{task["chapter_key"]}", '
            f'"title": {_escape_py(task["title"])}, '
            f'"format_ru": {_escape_py(task["format_ru"])}, '
            f'"action": {_escape_py(task["action"])}, '
            f'"difficulty": {_escape_py(task["difficulty"])}, '
            f'"pattern_id": {_escape_py(task["pattern_id"])}, '
            f'"goal": {_escape_py(task["detailed_description"])}, '
            f'"features": {_escape_py("; ".join(task["expected_concepts_primary"]))}'
            f"}},"
        )
    lines.append("]")
    lines.append("")
    lines.append("")
    lines.append("def build_task_rows(prefix: str) -> list[TaskRow]:")
    lines.append('    """Build language-specific catalog rows (slot_id uses given prefix)."""')
    lines.append("    rows: list[TaskRow] = []")
    lines.append("    for item in _TASK_INDEX:")
    lines.append("        n = int(item['task_num'])")
    lines.append("        slot = f\"{prefix}_{n:03d}\"")
    lines.append("        mirror = f\"pas_{n:03d}\" if prefix in {\"cs\", \"java\"} else \"\"")
    lines.append("        rows.append(")
    lines.append("            (")
    lines.append("                slot,")
    lines.append("                item['chapter_key'],")
    lines.append("                item['title'],")
    lines.append("                item['format_ru'],")
    lines.append("                item['action'],")
    lines.append("                item['pattern_id'],")
    lines.append("                item['goal'],")
    lines.append("                item['features'],")
    lines.append("                item['difficulty'],")
    lines.append("                mirror,")
    lines.append("            )")
    lines.append("        )")
    lines.append("    return rows")
    lines.append("")
    lines.append("ALGO_SYNTAX_META: dict[str, dict] = {")
    for task in sorted(tasks, key=lambda t: t["task_num"]):
        n = task["task_num"]
        meta_key = f"task_{n:03d}"
        meta = {
            "task_num": n,
            "chapter_key": task["chapter_key"],
            "raw_title": task.get("raw_title"),
            "title": task.get("title"),
            "short_goal": task.get("short_goal"),
            "detailed_description": task.get("detailed_description"),
            "format_ru": task.get("format_ru"),
            "format_raw": task.get("format_raw"),
            "action": task.get("action"),
            "difficulty": task.get("difficulty"),
            "difficulty_ru": task.get("difficulty_ru"),
            "test_cases": task.get("test_cases") or [],
            "expected_concepts": task.get("expected_concepts") or {},
            "implementations": task.get("implementations") or {},
            "reference_codes": task.get("reference_codes") or {},
        }
        lines.append(f'    "{meta_key}": {json.dumps(meta, ensure_ascii=False)},')
    lines.append("}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def emit_reference_code(tasks: list[dict], out_path: Path) -> None:
    from application.curriculum.content.v4_code_format import format_reference_code

    lines = [
        '"""Reference code for v4 tasks — all 5 languages per task."""',
        "from __future__ import annotations",
        "",
        "_TASK_REFERENCE_CODE: dict[str, dict[str, str]] = {",
    ]
    for task in sorted(tasks, key=lambda t: t["task_num"]):
        safe_title = re.sub(r"\s+", " ", task["title"]).strip()[:100]
        lines.append(f'    # Task {task["task_num"]}: {safe_title}')
        lines.append(f'    "{task["pattern_id"]}": {{')
        for lang in LANG_KEYS:
            raw = str(task["reference_codes"].get(lang, "") or "")
            formatted = format_reference_code(raw, lang) if raw else ""
            code = _escape_py(formatted)
            lines.append(f'        "{lang}": {code},')
        lines.append("    },")
    lines.extend(
        [
            "}",
            "",
            "",
            "def get_reference_code(slot_id: str, language: str) -> str:",
            '    """Get reference code for a slot and language."""',
            "    import re",
            "",
            "    from application.curriculum.content.v4_code_format import format_reference_code",
            "    from application.curriculum.content.v4_placeholder_reference import (",
            "        get_placeholder_reference,",
            "        is_placeholder_slot,",
            "    )",
            "",
            "    if is_placeholder_slot(slot_id):",
            "        raw = get_placeholder_reference(slot_id, language)",
            "        return format_reference_code(raw, language)",
            "",
            "    pat = slot_id",
            '    m = re.match(r"^(?:pas|py|cpp|cs|java)_(\\d+)$", slot_id)',
            "    if m:",
            '        pat = f"task_{int(m.group(1)):03d}"',
            '    raw = _TASK_REFERENCE_CODE.get(pat, {}).get(language, "")',
            "    if not raw:",
            '        m2 = re.match(r"^task_(\\d+)$", slot_id)',
            "        if m2:",
            '            pat = f"task_{int(m2.group(1)):03d}"',
            '            raw = _TASK_REFERENCE_CODE.get(pat, {}).get(language, "")',
            "    return format_reference_code(raw, language)",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def emit_test_cases(tasks: list[dict], out_path: Path) -> None:
    lines = [
        '"""Test cases for v4 tasks (shared across all language tracks)."""',
        "from __future__ import annotations",
        "",
        "# _SLOT_TEST_CASES[slot_id] = [(input, expected_output), ...]",
        "# slot_id prefix \"task_NNN\" is language-neutral.",
        "# Per-language slots (pas_NNN, py_NNN, cpp_NNN) resolve to the same pattern.",
        "",
        "_TASK_TEST_CASES: dict[str, list[tuple[str, str]]] = {",
    ]
    for task in sorted(tasks, key=lambda t: t["task_num"]):
        safe_title = re.sub(r"\s+", " ", task["title"]).strip()[:100]
        lines.append(f'    # Task {task["task_num"]}: {safe_title}')
        lines.append(f'    "{task["pattern_id"]}": [')
        for case in task.get("test_cases") or []:
            inp = _escape_py(case.get("inputs", ""))
            out = _escape_py(case.get("output", ""))
            lines.append(f"        ({inp}, {out}),")
        lines.append("    ],")
    lines.extend(
        [
            "}",
            "",
            "",
            "def get_test_cases(slot_id: str) -> list[tuple[str, str]]:",
            '    """Resolve test cases for any slot_id."""',
            "    if slot_id in _TASK_TEST_CASES:",
            "        return _TASK_TEST_CASES[slot_id]",
            "    import re",
            "",
            '    m = re.match(r"^(?:pas|py|cpp|cs|java)_(\\d+)$", slot_id)',
            "    if m:",
            '        pat = f"task_{int(m.group(1)):03d}"',
            "        return _TASK_TEST_CASES.get(pat, [])",
            '    m2 = re.match(r"^task_(\\d+)$", slot_id)',
            "    if m2:",
            '        pat = f"task_{int(m2.group(1)):03d}"',
            "        return _TASK_TEST_CASES.get(pat, [])",
            "    return []",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build algorithm-syntax course artifacts from docx.")
    parser.add_argument("--docx", type=Path, default=SRC_DEFAULT)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=BACKEND_ROOT / "algo_syntax_course.json",
    )
    parser.add_argument(
        "--out-catalog",
        type=Path,
        default=Path(__file__).resolve().parent / "algo_v128_catalog.py",
    )
    parser.add_argument(
        "--out-reference",
        type=Path,
        default=BACKEND_ROOT / "application" / "curriculum" / "content" / "v4_reference_code.py",
    )
    parser.add_argument(
        "--out-test-cases",
        type=Path,
        default=BACKEND_ROOT / "application" / "curriculum" / "content" / "v4_test_cases.py",
    )
    args = parser.parse_args()

    if not args.docx.is_file():
        print(f"ERROR: docx not found: {args.docx}")
        return 1

    lines = paras(args.docx)
    tasks, chapter_titles, failures = parse_course(lines)
    _repair_duplicate_task_metadata(tasks)
    for task in tasks:
        from algo_task_descriptions import enrich_detailed_description

        enrich_detailed_description(task)
    _repair_broken_placeholder_gaps(tasks)
    from application.curriculum.content.v4_placeholder_gap_repair import repair_task_placeholders

    for task in tasks:
        repair_task_placeholders(task)

    from application.curriculum.content.v4_code_format import format_reference_code

    for task in tasks:
        reference_codes: dict[str, str] = {}
        for lang in LANG_KEYS:
            impl = (task.get("implementations") or {}).get(lang) or {}
            gaps = [g for g in (impl.get("gaps") or []) if isinstance(g, dict)]
            raw_ref = _reference_for_lang(impl, lang)
            if gaps:
                from application.curriculum.content.v4_placeholder_gap_repair import (
                    scrub_pedagogical_labels,
                )

                raw_ref = scrub_pedagogical_labels(raw_ref, gaps, language=lang)
            reference_codes[lang] = (
                format_reference_code(raw_ref, lang) if raw_ref else ""
            )
        task["reference_codes"] = reference_codes

    tasks = sorted(tasks, key=lambda t: t["task_num"])

    args.out_json.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    emit_algo_v128_catalog(tasks, chapter_titles, args.out_catalog)
    emit_reference_code(tasks, args.out_reference)
    emit_test_cases(tasks, args.out_test_cases)

    print(f"parsed {len(tasks)} tasks from {args.docx}")
    print(f"  chapters: {len(chapter_titles)}")
    print(f"  json: {args.out_json}")
    print(f"  catalog: {args.out_catalog}")
    print(f"  reference: {args.out_reference}")
    print(f"  test_cases: {args.out_test_cases}")

    if tasks:
        sample = tasks[0]
        print(f"  sample task 1: {sample['title']} | {sample['format_ru']} | {sample['difficulty']}")
        print(f"  sample concepts (pascal): {len(sample['expected_concepts'].get('pascal', []))}")
        print(f"  sample TC count: {len(sample['test_cases'])}")

    by_chapter: dict[str, int] = {}
    for task in tasks:
        by_chapter[task["chapter_key"]] = by_chapter.get(task["chapter_key"], 0) + 1
    print("  tasks per chapter:", dict(sorted(by_chapter.items(), key=lambda x: CHAPTER_KEYS.index(x[0]))))

    if failures:
        print(f"parse warnings ({len(failures)}):")
        for msg in failures[:30]:
            print(f"  - {msg}")
        if len(failures) > 30:
            print(f"  ... and {len(failures) - 30} more")
    else:
        print("  parse warnings: none")

    _report_docx_duplicates(tasks)

    return 0 if len(tasks) == 128 else 1


def _report_docx_duplicates(tasks: list[dict]) -> None:
    """Warn when docx copy-pasted the same description/TC/blocks across tasks."""
    from collections import defaultdict

    by_desc: dict[str, list[int]] = defaultdict(list)
    by_tc: dict[str, list[int]] = defaultdict(list)
    by_blocks: dict[str, list[int]] = defaultdict(list)
    for task in tasks:
        n = int(task["task_num"])
        desc = str(task.get("detailed_description") or "").strip()
        if desc:
            by_desc[desc].append(n)
        tc_key = json.dumps(task.get("test_cases") or [], ensure_ascii=False, sort_keys=True)
        if tc_key != "[]":
            by_tc[tc_key].append(n)
        pas_blocks = task.get("implementations", {}).get("pascal", {}).get("assembly_blocks") or []
        if pas_blocks:
            by_blocks["\n".join(pas_blocks)].append(n)

    dup_desc = {k: v for k, v in by_desc.items() if len(v) > 1}
    dup_tc = {k: v for k, v in by_tc.items() if len(v) > 1}
    dup_blocks = {k: v for k, v in by_blocks.items() if len(v) > 1}
    if dup_desc or dup_tc or dup_blocks:
        print("  docx duplicate audit:")
        if dup_desc:
            largest = max(dup_desc.values(), key=len)
            print(f"    shared descriptions: {len(dup_desc)} groups (max {len(largest)} tasks, e.g. {largest[:8]})")
        if dup_tc:
            largest = max(dup_tc.values(), key=len)
            print(f"    shared test cases: {len(dup_tc)} groups (max {len(largest)} tasks, e.g. {largest[:8]})")
        if dup_blocks:
            largest = max(dup_blocks.values(), key=len)
            print(f"    shared Pascal blocks: {len(dup_blocks)} groups (max {len(largest)} tasks, e.g. {largest[:8]})")


if __name__ == "__main__":
    raise SystemExit(main())
