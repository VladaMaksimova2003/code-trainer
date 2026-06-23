"""Generate docs/python_course_v1_task_list.md — mirror of Pascal v3.1.1 catalog."""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pascal_v31_tasks import V31_CHAPTER_TITLES, V31_TASKS  # noqa: E402
from shared.super_user import SUPER_USER_EMAIL  # noqa: E402
from application.curriculum.pascal.catalog.pascal_v311_capstone_catalog import (  # noqa: E402
    capstone_task_rows,
)

PASCAL_TO_PY_PREFIX = {
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
    "pit": "pypit",
    "cdg": "pydg",
}

PYTHON_CHAPTER_TITLES = {
    "program_skeleton": "1. Точка входа и структура программы",
    "typed_variables": "2. Переменные и динамическая типизация",
    "io": "3. Ввод-вывод",
    "expressions": "4. Выражения и операторы",
    "conditions": "5. Условия",
    "loops": "6. Циклы",
    "functions": "7. Функции",
    "procedures": "8. Параметры и вызовы",
    "static_arrays": "9. Списки и индексация",
    "dynamic_arrays": "10. Динамические списки",
    "strings": "11. Строки",
    "records": "12. Словари, кортежи, dataclass",
    "files": "13. Файлы",
    "units": "14. Модули и пакеты",
    "recursion": "15. Рекурсия",
    "oop": "16. Классы и ООП",
    "pascal_pitfalls": "17. Типичные ошибки Python",
    "compiler_diagnostics": "18. Диагностика интерпретатора",
}

FORMAT_HINT = {
    "перевод_программы": "Перенести программу из эталона в Python",
    "перевод_фрагмента": "Перенести фрагмент в идиоматичный Python",
    "исправление": "Исправить код Python (SyntaxError, TypeError, IndentationError)",
    "поиск_ошибки": "Найти типичную ошибку Python и исправить",
    "сборка_программы": "Собрать программу из блоков (отступы = структура)",
    "сборка_фрагмента": "Собрать фрагмент из блоков",
    "выбор_фрагмента": "Выбрать корректный вариант Python (MCQ)",
    "код_по_блок-схеме": "Построить Python-код по блок-схеме",
    "блок-схема_по_коду": "Построить блок-схему по Python-коду",
}

PYTHON_TITLE_OVERRIDE: dict[str, str] = {
    "psk_09": "Комментарии # и \"\"\"",
    "psk_01": "Каркас: скрипт и if __name__",
    "pit_13": "Тело def не там (уровень модуля)",
    "pit_03": "Индекс строки s[1] — ошибка",
    "pit_07": "Имя модуля ≠ имя файла",
    "unt_02": "Модуль .py: def на уровне файла",
    "rec_02": "Доступ к полям dict/dataclass",
    "arr_03": "Индекс списка: 0 vs 1",
}

PYTHON_FOCUS: dict[str, str] = {
    "psk_01": "program/begin/end → скрипт или if __name__ == '__main__'",
    "psk_09": "# и \"\"\" вместо { } и (* *) — комментарии Python",
    "psk_02": "отсутствие ; в конце строки",
    "psk_10": "pass вместо пустого begin/end",
    "psk_11": "нет секций var/const/type — порядок import/def/main",
    "typ_02": "оператор = вместо :=",
    "typ_01": "нет секции var — присваивание сразу",
    "typ_04": "True/False с заглавной буквы",
    "typ_08": "UPPER_CASE для констант вместо const",
    "io_01": "input() и int(input()) вместо Readln",
    "io_02": "print(a, b) — несколько аргументов через запятую",
    "io_04": "f-string или format() вместо Format",
    "exp_02": "// и % вместо div/mod",
    "exp_04": "in для membership вместо set of / in",
    "cnd_01": "if/elif/else с двоеточием и отступами",
    "cnd_03": "elif вместо else if",
    "cnd_05": "match/case (3.10+) или цепочка elif вместо case of",
    "cnd_06": "тернарный x if c else y",
    "cnd_13": "IndentationError / пропущенное : после if",
    "lop_01": "for i in range(...) вместо for i := 1 to n",
    "lop_03": "range(n, 0, -1) вместо downto",
    "lop_05": "while True + break вместо repeat until",
    "lop_14": "for i in range(10) — не присваивать i в теле",
    "fn_01": "def вместо function",
    "fn_02": "return вместо Result",
    "fn_08": "вложенный def допустим (в отличие от Pascal)",
    "prc_01": "def без return vs function",
    "prc_02": "изменяемые объекты (list) вместо var-параметра",
    "arr_01": "list, индекс с 0",
    "arr_03": "индекс 0 — первый элемент (зеркало Pascal arr_03)",
    "dyn_01": "list + append вместо SetLength",
    "dyn_09": "list[] без фиксированных границ",
    "str_01": "len(s), s[i], индекс с 0",
    "str_03": "s[-1] или s[len(s)-1] — последний символ",
    "rec_01": "dict или @dataclass вместо record",
    "rec_02": "r['field'] / r.field — без with",
    "rec_04": "ссылки и GC — нет явного ^ (python-only адаптация)",
    "fil_01": "with open(...) as f вместо Assign/Reset",
    "fil_03": "with автоматически закрывает файл",
    "unt_01": "import / from … import вместо uses",
    "unt_02": "файл .py как модуль — def на уровне модуля",
    "unt_06": "циклический import — debug",
    "oop_02": "__init__ вместо constructor Create",
    "oop_04": "super() вместо inherited",
    "oop_06": "@property вместо property read/write",
    "oop_14": "Protocol / ABC — вместо interface type (адаптация)",
    "pit_03": "s[1] ошибочно — нужен s[0] (зеркало Pascal pit_03)",
    "pit_13": "def на уровне модуля — не путать объявление и тело",
    "pit_16": "a, b = b, a вместо Swap с var",
    "pit_17": "return x вместо exit(x) в function",
    "pit_22": "list[] вместо array[1..10] + SetLength",
    "pit_24": "@property без поля — добавить self._x",
    "cdg_04": "пропущенное : после if/def/for",
    "cdg_06": "IndentationError / пропущенный :",
}

PYTHON_ONLY_EXTRAS = [
    ("pyk_13", "program_skeleton", "Сборка if __name__ == '__main__'", "Нет program/begin/end"),
    ("pyt_11", "typed_variables", "Множественное присваивание a, b = 1, 2", "Unpacking"),
    ("pyt_12", "typed_variables", "None vs null/nil", "Отсутствие значения"),
    ("pyi_11", "io", "f-string f'{x:.2f}'", "Форматирование строк"),
    ("pye_11", "expressions", "Truthiness: if []", "Пустой список — falsy"),
    ("pye_12", "expressions", "Цепочка 1 < x < 10", "Chained comparisons"),
    ("pyl_17", "loops", "else у цикла for", "Python-only"),
    ("pyl_18", "loops", "enumerate в for", "Идиома обхода"),
    ("pyf_13", "functions", "lambda one-liner", "Анонимные функции"),
    ("pyf_14", "functions", "Ловушка def f(a=[])", "Mutable default"),
    ("pya_11", "static_arrays", "List comprehension", "Идиома вместо for"),
    ("pya_12", "static_arrays", "Срез a[1:4]", "Slice semantics"),
    ("pyd_11", "records", "set literal {1,2,3}", "Множества Python"),
    ("pys_11", "strings", "split / join", "Методы строк"),
    ("pym_11", "units", "pip / venv (MCQ)", "Экосистема"),
    ("pyexc_01", "exceptions", "try/except ValueError", "Новая глава: исключения"),
    ("pyexc_02", "exceptions", "EAFP: int(input())", "Стиль Python"),
    ("pypro_01", "pro_python", "generator yield", "Продвинутый Python"),
    ("pypro_02", "pro_python", "decorator @timer", "Продвинутый Python"),
]

CAP_IDS = {r[0] for r in capstone_task_rows()}


def mirror_id(pascal_id: str) -> str:
    if "_cap" in pascal_id:
        base, cap = pascal_id.rsplit("_cap", 1)
        prefix = base.split("_")[0]
        return f"{PASCAL_TO_PY_PREFIX.get(prefix, 'py')}_cap{cap}"
    prefix = pascal_id.split("_")[0]
    suffix = pascal_id[len(prefix) :]
    return f"{PASCAL_TO_PY_PREFIX.get(prefix, 'py')}{suffix}"


def mirror_type(slot_id: str, chapter: str) -> str:
    if slot_id in CAP_IDS:
        return "capstone"
    if slot_id in {"pit_03", "fn_08", "rec_04"}:
        return "python-only"
    if chapter in {"pascal_pitfalls", "compiler_diagnostics"}:
        return "adapted"
    return "direct"


def python_title(title: str) -> str:
    replacements = [
        ("Pascal", "Python"),
        ("program … begin … end.", "скрипт / main"),
        ("program/begin/end", "main / отступы"),
        ("Readln", "input()"),
        ("Writeln", "print()"),
        (":=", "="),
        ("div/mod", "// и %"),
        ("case of", "match / elif"),
        ("for … to … do", "for … in range()"),
        ("procedure", "def"),
        ("function", "def + return"),
        ("record", "dict / dataclass"),
        ("unit", "модуль .py"),
        ("uses", "import"),
        ("SetLength", "append / list()"),
        ("TextFile", "open()"),
        ("interface/implementation", "модуль и def"),
        ("dynamic array", "list"),
        ("array[1..N]", "list"),
    ]
    result = title
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def python_goal(row: tuple) -> str:
    slot_id = row[0]
    fmt = row[3]
    goal = row[6]
    focus = PYTHON_FOCUS.get(slot_id)
    if focus:
        return focus if not goal else f"{focus}. {goal}"
    hint = FORMAT_HINT.get(fmt, "")
    if hint and goal:
        return f"{hint}. {goal}"
    return goal or hint or ""


def generate() -> str:
    lines: list[str] = []
    lines += [
        "# Python Course v1 — зеркальный каталог заданий",
        "",
        "Зеркало **Pascal Course v3.1.1**: 252 задачи (180 core + 72 capstone).",
        "",
        "**Целевой язык изучения:** Python 3.10+  ",
        "**Эталоны «Я знаю»:** Pascal, C/C++, Java, C#",
        "",
        "## Принцип зеркалирования",
        "",
        "| Тип | Метка | Смысл |",
        "|-----|-------|-------|",
        "| direct | 🔄 | Та же педагогическая цель, синтаксис Python |",
        "| adapted | 🔀 | Та же идея, типичная ошибка/конструкция Python |",
        "| python-only | 🐍 | Уникально для Python или зеркало «наоборот» |",
        "| capstone | 🏁 | Итоговая задача главы (4 на главу) |",
        "",
        "## Форматы",
        "",
        "| Формат | Действие |",
        "|--------|----------|",
        "| перевод_программы / перевод_фрагмента | translate |",
        "| исправление / поиск_ошибки | debug |",
        "| сборка_программы / сборка_фрагмента | assemble |",
        "| выбор_фрагмента | implement (MCQ) |",
        "| код_по_блок-схеме / блок-схема_по_коду | implement |",
        "",
        "---",
        "",
    ]

    by_ch: dict[str, list[tuple]] = defaultdict(list)
    for row in V31_TASKS:
        by_ch[row[1]].append(row)

    total = 0
    emoji_map = {
        "direct": "🔄",
        "adapted": "🔀",
        "python-only": "🐍",
        "capstone": "🏁",
    }

    for ch_key in V31_CHAPTER_TITLES:
        rows = by_ch[ch_key]
        py_ch_title = PYTHON_CHAPTER_TITLES.get(ch_key, ch_key)
        lines += [
            f"## {py_ch_title}",
            "",
            f"**Ключ:** `{ch_key}` · **Задач:** {len(rows)} · "
            f"**Зеркало Pascal:** {V31_CHAPTER_TITLES[ch_key]}",
            "",
            "| ID | Pascal | Тип | Название | Формат | Сложность | Цель / Python-фокус |",
            "|----|--------|-----|----------|--------|-----------|---------------------|",
        ]
        for row in rows:
            slot_id, _chapter, title, fmt, _action, _pattern, _goal, _feat, diff, _legacy = row[:10]
            py_id = mirror_id(slot_id)
            mtype = mirror_type(slot_id, ch_key)
            emoji = emoji_map[mtype]
            py_t = PYTHON_TITLE_OVERRIDE.get(slot_id) or python_title(title)
            py_g = python_goal(row).replace("|", "\\|").replace("\n", " ")
            if len(py_g) > 180:
                py_g = py_g[:177] + "…"
            lines.append(
                f"| `{py_id}` | `{slot_id}` | {emoji} | {py_t} | {fmt} | {diff} | {py_g} |"
            )
            total += 1
        lines += ["", "---", ""]

    lines += [
        "## Сводка",
        "",
        f"| Показатель | Значение |",
        f"|------------|----------|",
        f"| Зеркальных задач (из Pascal) | {total} |",
        f"| Глав | 18 |",
        f"| Core | 180 |",
        f"| Capstone | 72 |",
        "",
        "## Дополнительные Python-only задачи (рекомендуется)",
        "",
        "Не зеркалят Pascal напрямую, но логичны для Python-трека:",
        "",
        "| ID | Глава | Название | Зачем |",
        "|----|-------|----------|-------|",
    ]
    for extra in PYTHON_ONLY_EXTRAS:
        lines.append(f"| `{extra[0]}` | {extra[1]} | {extra[2]} | {extra[3]} |")

    lines += [
        "",
        f"| **Итого с дополнениями** | **~{total + len(PYTHON_ONLY_EXTRAS)}** | | |",
        "",
        "## Автор задач и ручное редактирование",
        "",
        "Все задачи курса (Pascal и будущий Python) при сидировании привязываются к "
        f"**`{SUPER_USER_EMAIL}`** (`teacher_id` в БД).",
        "",
        "- Сид: `poetry run python scripts/seed_pascal_course_v311.py` "
        "(флаг `--teacher-email` переопределяет автора)",
        "- Уже созданные задачи без автора: `poetry run python scripts/assign_tasks_to_teacher.py`",
        "- Редактирование: войти как admin → раздел преподавателя → «Мои задачи» / редактор задания",
        "",
        "## Следующий шаг реализации",
        "",
        "1. `backend/scripts/python_v31_tasks.py` — строки каталога",
        "2. `python_v311_known_code.py` — эталоны Pascal/C#/Java",
        "3. `python_v311_content.py` — starter code, tests, debug starters",
        "4. `seed_python_course_v311.py` + `/learn/python` в UI",
        "5. Переключатель языка изучения (Pascal ↔ Python) в профиле/настройках",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    # In Docker repo root is /app; locally it's the project root.
    if not (repo_root / "docs").is_dir() and Path("/app/docs").is_dir():
        repo_root = Path("/app")
    out = repo_root / "docs" / "python_course_v1_task_list.md"
    out.write_text(generate(), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
