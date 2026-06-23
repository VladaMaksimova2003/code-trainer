"""Target course volume v192-B: 16 chapters × 12 tasks (128 base + 64 expansion).

Stage 0 locks the roadmap in code. Expansion slots task_129…task_192 are planned here;
content is filled in stage 3 (not in v128 catalog yet).
"""

from __future__ import annotations

from typing import Any

# --- Stage 0: fixed target volume (192-B) ---

COURSE_VARIANT = "192-B"
V128_CORE_TASK_COUNT = 128

V128_CHAPTER_KEYS: tuple[str, ...] = (
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
)

V128_CHAPTER_TITLES: dict[str, str] = {
    "algo_basics": "Базовый синтаксис через простые алгоритмы",
    "branches": "Ветвления",
    "loops": "Циклы",
    "arrays_collections": "Массивы и коллекции",
    "strings": "Строки",
    "functions": "Функции",
    "recursion": "Рекурсия",
    "search_sort": "Поиск и сортировки",
    "aggregation": "Агрегация и фильтрация данных",
    "maps": "Словари и key-value структуры",
    "files_modules": "Файлы и модули",
    "stack_queue": "Стек и очередь",
    "linked_lists": "Связные списки",
    "trees_graphs": "Деревья и графы",
    "oop": "ООП",
    "inheritance_capstone": "Наследование и итоговый проект",
}

V192_CHAPTER_COUNT = len(V128_CHAPTER_KEYS)
V192_CHAPTER_TASK_COUNT = 12
V192_EXPANSION_TASK_COUNT = 64
V192_TARGET_TASK_COUNT = V128_CORE_TASK_COUNT + V192_EXPANSION_TASK_COUNT
V192_EXPANSION_TASK_FIRST = V128_CORE_TASK_COUNT + 1  # 129
V192_EXPANSION_TASK_LAST = V192_TARGET_TASK_COUNT  # 192

# Per expansion block (+4 at end of each chapter): 2 assemble + 1 debug + 1 implement
V192_EXPANSION_ACTIONS: tuple[str, ...] = ("assemble", "assemble", "debug", "implement")

V192_COLLECTION_TARGETS: dict[str, int] = {
    key: V192_CHAPTER_TASK_COUNT for key in V128_CHAPTER_KEYS
}


def expansion_task_nums_for_chapter(chapter_key: str) -> tuple[int, ...]:
    """Return global task numbers 129-192 for the +4 block of a chapter."""
    try:
        idx = V128_CHAPTER_KEYS.index(chapter_key)
    except ValueError:
        return ()
    base = V192_EXPANSION_TASK_FIRST + idx * 4
    return tuple(range(base, base + 4))


def pattern_id(task_num: int) -> str:
    return f"task_{task_num:03d}"


# Planned +64 algorithm tasks (titles only; full meta in stage 3).
_V192_EXPANSION_BY_CHAPTER: dict[str, list[dict[str, str]]] = {
    "algo_basics": [
        {"title": "Сумма цифр числа", "action": "assemble"},
        {"title": "Количество чётных чисел", "action": "assemble"},
        {"title": "Среднее температур (целое)", "action": "debug", "pitfall_id": "integer_division"},
        {"title": "Минимум из n чисел", "action": "implement"},
    ],
    "branches": [
        {"title": "Високосный год", "action": "assemble"},
        {"title": "Категория BMI", "action": "assemble"},
        {"title": "Попадание x в отрезок [a,b]", "action": "debug", "pitfall_id": "chain_comparison"},
        {"title": "Количество корней квадратного уравнения", "action": "implement"},
    ],
    "loops": [
        {"title": "Сумма 1+2+…+n", "action": "assemble"},
        {"title": "НОД (алгоритм Еuclid)", "action": "assemble"},
        {"title": "Сумма до нуля (off-by-one)", "action": "debug", "pitfall_id": "for_range_off_by_one"},
        {"title": "Длина последовательности Collatz", "action": "implement"},
    ],
    "arrays_collections": [
        {"title": "Второй максимум массива", "action": "assemble"},
        {"title": "Сдвиг нулей в конец", "action": "assemble"},
        {"title": "Разворот массива (индекс)", "action": "debug", "pitfall_id": "index_1based"},
        {"title": "Префиксные суммы", "action": "implement"},
    ],
    "strings": [
        {"title": "Подсчёт гласных", "action": "assemble"},
        {"title": "Шифр Caesar (+k)", "action": "assemble"},
        {"title": "Первое вхождение символа", "action": "debug", "pitfall_id": "index_1based"},
        {"title": "Самое длинное слово", "action": "implement"},
    ],
    "functions": [
        {"title": "Функция is_even", "action": "assemble"},
        {"title": "Функция lcm через gcd", "action": "assemble"},
        {"title": "Факториал (return)", "action": "debug", "pitfall_id": "scope_block"},
        {"title": "Массив отсортирован?", "action": "implement"},
    ],
    "recursion": [
        {"title": "x^n рекурсивно", "action": "assemble"},
        {"title": "Сумма 1..n рекурсией", "action": "assemble"},
        {"title": "Факториал (базовый случай)", "action": "debug", "pitfall_id": "for_range_off_by_one"},
        {"title": "Башни Ханоя — число ходов", "action": "implement"},
    ],
    "search_sort": [
        {"title": "Сортировка подсчётом (0..9)", "action": "assemble"},
        {"title": "Бинарный поиск — последнее вхождение", "action": "assemble"},
        {"title": "Bubble sort (индекс)", "action": "debug", "pitfall_id": "index_1based"},
        {"title": "Слияние двух отсортированных массивов", "action": "implement"},
    ],
    "aggregation": [
        {"title": "Мода массива", "action": "assemble"},
        {"title": "Произведение элементов", "action": "assemble"},
        {"title": "Среднее с округлением", "action": "debug", "pitfall_id": "round_semantics"},
        {"title": "Элементы выше среднего", "action": "implement"},
    ],
    "maps": [
        {"title": "Two sum (индексы пары)", "action": "assemble"},
        {"title": "Первый неповторяющийся символ", "action": "assemble"},
        {"title": "Частота id (ключ)", "action": "debug"},
        {"title": "Группировка анаграмм", "action": "implement"},
    ],
    "files_modules": [
        {"title": "Максимум чисел из файла", "action": "assemble"},
        {"title": "Подсчёт слов в файле", "action": "assemble"},
        {"title": "CSV: чтение файла", "action": "debug", "pitfall_id": "file_text_mode"},
        {"title": "Фильтр чётных в output.txt", "action": "implement"},
    ],
    "stack_queue": [
        {"title": "Вычисление RPN", "action": "assemble"},
        {"title": "Очередь: симуляция кассы", "action": "assemble"},
        {"title": "Проверка скобок (пустой стек)", "action": "debug"},
        {"title": "BFS: кратчайший путь", "action": "implement"},
    ],
    "linked_lists": [
        {"title": "Длина односвязного списка", "action": "assemble"},
        {"title": "Вставка в начало списка", "action": "assemble"},
        {"title": "Удаление по значению", "action": "debug"},
        {"title": "Сортировка списка вставками", "action": "implement"},
    ],
    "trees_graphs": [
        {"title": "Число вершин дерева", "action": "assemble"},
        {"title": "Inorder обход (фрагмент)", "action": "assemble"},
        {"title": "DFS: индексация вершин", "action": "debug", "pitfall_id": "index_1based"},
        {"title": "Компоненты связности", "action": "implement"},
    ],
    "oop": [
        {"title": "Класс Counter", "action": "assemble"},
        {"title": "Класс Stack на массиве", "action": "assemble"},
        {"title": "BankAccount: withdraw", "action": "debug", "pitfall_id": "exception_model"},
        {"title": "Student: лучший средний балл", "action": "implement"},
    ],
    "inheritance_capstone": [
        {"title": "Shape → Circle/Rectangle", "action": "assemble"},
        {"title": "Employee → Manager", "action": "assemble"},
        {"title": "Полиморфизм speak (virtual)", "action": "debug"},
        {"title": "Итог: система доставки", "action": "implement"},
    ],
}


def build_v192_expansion_index() -> list[dict[str, Any]]:
    """Planned rows for task_129…task_192 (not seeded until stage 3)."""
    rows: list[dict[str, Any]] = []
    for chapter_key in V128_CHAPTER_KEYS:
        specs = _V192_EXPANSION_BY_CHAPTER[chapter_key]
        nums = expansion_task_nums_for_chapter(chapter_key)
        for task_num, spec in zip(nums, specs, strict=True):
            rows.append(
                {
                    "task_num": task_num,
                    "chapter_key": chapter_key,
                    "chapter_title": V128_CHAPTER_TITLES[chapter_key],
                    "pattern_id": pattern_id(task_num),
                    "title": spec["title"],
                    "action": spec["action"],
                    "pitfall_id": spec.get("pitfall_id"),
                    "status": "planned",
                }
            )
    return rows


V192_EXPANSION_INDEX: list[dict[str, Any]] = build_v192_expansion_index()
