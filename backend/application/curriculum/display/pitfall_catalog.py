"""Catalog of MPLT transfer pitfalls (FCC / AFCC) for mirror tasks."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

TransferType = Literal["TCC", "ATCC", "FCC", "AFCC"]
DetectorKind = Literal["matches_buggy", "code_pattern", "contrast_test"]


class PitfallSpec(TypedDict, total=False):
    id: str
    transfer_type: TransferType
    concept_ids: list[str]
    source_langs: list[str]
    target_langs: list[str]
    detector: DetectorKind
    hint_ru: str
    contrast_note_ru: str
    feedback_ru: str
    pedagogy_note_ru: str
    buggy_snippets: dict[str, str]
    code_patterns: dict[str, str]
    contrast_test_indices: list[int]


_ALL_LANGS = ["python", "cpp", "pascal", "csharp", "java"]


PITFALLS: dict[str, PitfallSpec] = {
    "integer_division": {
        "id": "integer_division",
        "transfer_type": "FCC",
        "concept_ids": ["arithmetic_ops"],
        "source_langs": _ALL_LANGS,
        "target_langs": _ALL_LANGS,
        "detector": "code_pattern",
        "hint_ru": "В Pascal для целого частного используйте div; оператор / даёт вещественный результат.",
        "contrast_note_ru": "В Python целое деление — //; в Pascal — div; в C++ / для int даёт целое частное.",
        "feedback_ru": (
            "Ложный перенос (FCC): оператор / в Pascal даёт вещественный результат, "
            "для целого частного нужен div."
        ),
        "code_patterns": {"pascal": r"\b\w+\s*/\s*\w+"},
        "buggy_snippets": {"pascal": "/"},
    },
    "index_1based": {
        "id": "index_1based",
        "transfer_type": "FCC",
        "concept_ids": ["indexed_sequence", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "code_pattern",
        "hint_ru": "В Pascal первый элемент массива имеет индекс 1 — пишите a[1], не a[0].",
        "contrast_note_ru": "Python индексирует с нуля; Pascal — с единицы.",
        "feedback_ru": (
            "Ложный перенос (FCC): индексация с нуля перенесена из Python в Pascal."
        ),
        "buggy_snippets": {"pascal": "[0]"},
        "code_patterns": {"pascal": r"\[\s*0\s*\]"},
    },
    "for_range_off_by_one": {
        "id": "for_range_off_by_one",
        "transfer_type": "ATCC",
        "concept_ids": ["counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Python range(n) даёт n шагов с 0; "
            "в Pascal ту же идею часто записывают диапазоном 1..n."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): границы цикла перенесены как range(n), а не идиома целевого языка."
        ),
    },
    "output_space_separated": {
        "id": "output_space_separated",
        "transfer_type": "AFCC",
        "concept_ids": ["stdout_write"],
        "source_langs": _ALL_LANGS,
        "target_langs": _ALL_LANGS,
        "detector": "matches_buggy",
        "hint_ru": (
            "Три числа в одной строке вывода: Pascal writeln(a, ' ', b, ' ', c) "
            "или writeln(a, b, c); Python print(a, b, c) или print(f'{a} {b} {c}')."
        ),
        "contrast_note_ru": (
            "Один writeln с несколькими аргументами vs три отдельных print — "
            "пробелы между числами должны совпасть с тестом."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): формат вывода нескольких чисел в одной строке "
            "перенесён из другого языка неверно."
        ),
    },
    "assignment_vs_compare": {
        "id": "assignment_vs_compare",
        "transfer_type": "FCC",
        "concept_ids": ["assignment", "simple_branch"],
        "source_langs": ["python", "cpp", "csharp", "java"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "code_pattern",
        "hint_ru": "В Pascal присваивание — :=, сравнение — =.",
        "feedback_ru": "Ложный перенос (FCC): перепутаны присваивание и сравнение в Pascal.",
        "code_patterns": {"pascal": r"(?<![:<>=!])=(?!=)"},
    },
    "string_index": {
        "id": "string_index",
        "transfer_type": "FCC",
        "concept_ids": ["string_sequence", "search_find"],
        "source_langs": ["python"],
        "target_langs": ["pascal"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Pos(ch, s) в Pascal возвращает 1 для первого символа; "
            "s.find(ch) в Python — 0."
        ),
        "feedback_ru": "Ложный перенос (FCC): индекс подстроки вычислен как в Python.",
    },
    "round_semantics": {
        "id": "round_semantics",
        "transfer_type": "AFCC",
        "concept_ids": ["arithmetic_ops"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Функции round() в Python и Round() в Pascal по-разному округляют числа вида x.5 — "
            "не переносите вызов round() буквально."
        ),
        "contrast_note_ru": (
            "При округлении .5 выберите функцию целевого языка явно — "
            "Python round() и Pascal Round() следуют разным правилам."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): семантика округления перенесена из Python неверно."
        ),
        "contrast_test_indices": [1],
    },
    "input_line_model": {
        "id": "input_line_model",
        "transfer_type": "AFCC",
        "concept_ids": ["stdin_read"],
        "source_langs": _ALL_LANGS,
        "target_langs": _ALL_LANGS,
        "detector": "contrast_test",
        "hint_ru": (
            "В Python несколько чисел часто разбирают через input().split(); "
            "в Pascal их можно читать через readln(a, b, c) или разобрать строку вручную."
        ),
        "contrast_note_ru": (
            "Одна строка входа: Python split(), Java Scanner, Pascal readln/Val — "
            "разберите формат входа задачи перед переносом."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): модель ввода перенесена из Python некорректно."
        ),
        "contrast_test_indices": [0],
    },
    "float_division_pascal": {
        "id": "float_division_pascal",
        "transfer_type": "AFCC",
        "concept_ids": ["arithmetic_ops"],
        "source_langs": ["python", "cpp", "csharp", "java"],
        "target_langs": ["pascal", "cpp"],
        "detector": "code_pattern",
        "hint_ru": "Для целого результата в Pascal используйте div, не вещественное деление.",
        "contrast_note_ru": "Writeln(a / b) в Pascal даёт real; для целого — div.",
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): в Pascal / всегда вещественное деление; "
            "для целой части нужен div."
        ),
        "code_patterns": {"pascal": r"\bwriteln\s*\([^)]*/[^)]*\)"},
    },
    "mod_negative": {
        "id": "mod_negative",
        "transfer_type": "AFCC",
        "concept_ids": ["arithmetic_ops"],
        "source_langs": ["python", "cpp", "csharp", "java"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "code_pattern",
        "hint_ru": "В Pascal остаток — mod, не %; знак результата может отличаться от Python.",
        "contrast_note_ru": "Оператор % из Python переносят как mod, но семантика для отрицательных чисел другая.",
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): оператор остатка перенесён из Python без учёта mod в Pascal."
        ),
        "buggy_snippets": {"pascal": "%"},
        "code_patterns": {"pascal": r"%"},
    },
    "chain_comparison": {
        "id": "chain_comparison",
        "transfer_type": "FCC",
        "concept_ids": ["simple_branch", "multi_branch"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "cpp", "csharp", "java"],
        "detector": "code_pattern",
        "hint_ru": (
            "Запись 0 <= x <= 100 из Python в Pascal/C++/Java: "
            "два сравнения, соединённых and/&&."
        ),
        "contrast_note_ru": "В Python допустимо 0 <= x <= 100; в Pascal нужно (x >= 0) and (x <= 100).",
        "feedback_ru": (
            "Ложный перенос (FCC): цепочка сравнений перенесена из Python в Pascal/C++."
        ),
        "code_patterns": {
            "pascal": r"(?<![<>=!])<=?\s*\w+\s*<=?",
            "cpp": r"(?<![<>=!])<=?\s*\w+\s*<=?",
        },
    },
    "and_or_keywords": {
        "id": "and_or_keywords",
        "transfer_type": "FCC",
        "concept_ids": ["simple_branch"],
        "source_langs": ["python"],
        "target_langs": ["cpp", "csharp", "java"],
        "detector": "code_pattern",
        "hint_ru": "В C/C++ логика — && и ||, не and/or.",
        "feedback_ru": "Ложный перенос (FCC): ключевые слова and/or перенесены из Python в C-family.",
        "code_patterns": {"cpp": r"\b(and|or)\b", "csharp": r"\b(and|or)\b", "java": r"\b(and|or)\b"},
    },
    "bool_literals": {
        "id": "bool_literals",
        "transfer_type": "FCC",
        "concept_ids": ["simple_branch"],
        "source_langs": ["python"],
        "target_langs": ["pascal"],
        "detector": "code_pattern",
        "hint_ru": "В Pascal логические литералы — true/false (нижний регистр), не True/False.",
        "feedback_ru": "Ложный перенос (FCC): булевы литералы Python перенесены в Pascal.",
        "code_patterns": {"pascal": r"\b(True|False)\b"},
    },
    "string_immutable": {
        "id": "string_immutable",
        "transfer_type": "AFCC",
        "concept_ids": ["string_sequence"],
        "source_langs": ["python"],
        "target_langs": ["java", "csharp"],
        "detector": "matches_buggy",
        "hint_ru": "Строка в Java/C# неизменяема — символ нельзя присвоить по индексу.",
        "contrast_note_ru": "В Python s[i] = 'x' допустимо для list-like моделей; String в Java — immutable.",
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): попытка изменить символ immutable-строки."
        ),
    },
    "list_vs_static_array": {
        "id": "list_vs_static_array",
        "transfer_type": "AFCC",
        "concept_ids": ["indexed_sequence", "dynamic_array"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "cpp"],
        "detector": "contrast_test",
        "hint_ru": (
            "Python list.append добавляет элемент; массив Pascal array[1..n] фиксирован — "
            "размер n задайте до заполнения."
        ),
        "contrast_note_ru": (
            "Динамический list в Python vs static array в Pascal: "
            "размер массива Pascal задаётся при объявлении."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): динамический list перенесён как static array."
        ),
        "contrast_test_indices": [0],
    },
    "exception_model": {
        "id": "exception_model",
        "transfer_type": "ATCC",
        "concept_ids": ["exception_handling"],
        "source_langs": ["python", "cpp", "csharp", "java"],
        "target_langs": ["pascal", "java", "csharp"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Python try/except в Pascal замените проверкой IOResult или Val(..., code) "
            "с проверкой code <> 0."
        ),
        "contrast_note_ru": (
            "Python try/except → Pascal: IOResult, Val с кодом ошибки или явная проверка условия."
        ),
        "feedback_ru": "Абстрактный перенос (ATCC): выберите идиому обработки ошибок целевого языка.",
    },
    "pass_by_value_ref": {
        "id": "pass_by_value_ref",
        "transfer_type": "ATCC",
        "concept_ids": ["parameter_passing"],
        "source_langs": ["python"],
        "target_langs": ["pascal"],
        "detector": "matches_buggy",
        "hint_ru": "Чтобы изменить параметр в Pascal, используйте var в заголовке процедуры.",
        "contrast_note_ru": "Python передаёт ссылки на объекты; Pascal — value, var для in-out.",
        "feedback_ru": "Абстрактный перенос (ATCC): параметр без var не изменит переменную вызывающего.",
    },
    "file_text_mode": {
        "id": "file_text_mode",
        "transfer_type": "ATCC",
        "concept_ids": ["file_read", "file_write"],
        "source_langs": ["python"],
        "target_langs": ["pascal"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Python: with open('f.txt') as f: Readln. "
            "Pascal: Assign(f,'f.txt'); Reset(f); Readln(f,line); Close(f)."
        ),
        "contrast_note_ru": (
            "Python with open(...) → Pascal Assign/Reset/Readln/Close для текстового файла."
        ),
        "feedback_ru": "Абстрактный перенос (ATCC): API файлов перенесён буквально из Python.",
    },
    "switch_fallthrough": {
        "id": "switch_fallthrough",
        "transfer_type": "FCC",
        "concept_ids": ["switch_selection"],
        "source_langs": ["python"],
        "target_langs": ["cpp", "csharp"],
        "detector": "matches_buggy",
        "hint_ru": "В C/C++ switch без break проваливается в следующий case (см. «Выбор по значению»).",
        "feedback_ru": "Ложный перенос (FCC): отсутствует break в switch — fallthrough в C-family.",
    },
    "switch_vs_match": {
        "id": "switch_vs_match",
        "transfer_type": "ATCC",
        "concept_ids": ["switch_selection"],
        "source_langs": ["python"],
        "target_langs": ["python", "csharp"],
        "detector": "matches_buggy",
        "hint_ru": "match/case (Python 3.10+) и switch (C#) — разные идиомы ветвления.",
        "feedback_ru": "Абстрактный перенос (ATCC): используйте switch/case целевого языка.",
    },
    "scope_block": {
        "id": "scope_block",
        "transfer_type": "ATCC",
        "concept_ids": ["return_flow", "function_definition"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": "В Python — return x; в Pascal присвойте имя функции: MyFunc := x.",
        "contrast_note_ru": "Pascal: MyFunc := x; Python: return x",
        "feedback_ru": "Абстрактный перенос (ATCC): возврат значения из функции записан не той идиомой.",
    },
    "null_vs_nil": {
        "id": "null_vs_nil",
        "transfer_type": "FCC",
        "concept_ids": ["object_instance"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "java", "csharp"],
        "detector": "code_pattern",
        "hint_ru": "None/null/nil — разные литералы; не переносите None в Pascal.",
        "feedback_ru": "Ложный перенос (FCC): None из Python перенесён в другой язык без замены.",
        "code_patterns": {"pascal": r"\bNone\b", "java": r"\bNone\b", "csharp": r"\bNone\b"},
    },
    "overflow_fixed_int": {
        "id": "overflow_fixed_int",
        "transfer_type": "AFCC",
        "concept_ids": ["arithmetic_ops", "indexed_sequence"],
        "source_langs": ["python"],
        "target_langs": ["pascal"],
        "detector": "contrast_test",
        "hint_ru": "Фиксированный тип/массив в Pascal может переполниться там, где Python int не ограничен.",
        "contrast_note_ru": "Python int произвольной точности; Pascal integer и static array имеют предел.",
        "feedback_ru": "Абстрактно-ложный перенос (AFCC): переполнение fixed-size типа.",
        "contrast_test_indices": [0],
    },
    "elif_chain": {
        "id": "elif_chain",
        "transfer_type": "ATCC",
        "concept_ids": ["multi_branch"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Цепочка elif — идиома Python; в целевом языке используйте else if "
            "(см. ожидаемую конструкцию «Условия и ветвление»)."
        ),
        "contrast_note_ru": (
            "Python elif не переносится как отдельное ключевое слово Pascal; "
            "нужна цепочка else if с полным покрытием веток."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): цепочка ветвлений перенесена идиомой elif, "
            "а не конструкцией целевого языка."
        ),
    },
    "pascal_case_labels": {
        "id": "pascal_case_labels",
        "transfer_type": "ATCC",
        "concept_ids": ["switch_selection"],
        "source_langs": ["python"],
        "target_langs": ["pascal", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Несколько значений одной ветки оформляются идиомой целевого языка "
            "(см. «Выбор по значению»)."
        ),
        "contrast_note_ru": (
            "Сезон по месяцу: в Pascal метки case перечисляют через запятую; "
            "в Python — in (...), в C-family — несколько case подряд с break."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): выбор сезона записан идиомой Python, "
            "а не case/switch целевого языка."
        ),
    },
    "leap_year_mod": {
        "id": "leap_year_mod",
        "transfer_type": "AFCC",
        "concept_ids": ["simple_branch", "arithmetic_ops"],
        "source_langs": ["python", "cpp", "csharp", "java"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Високосный год: правило 400 / 4 / 100 и оператор остатка в целевом языке "
            "(см. «Арифметика и выражения»)."
        ),
        "contrast_note_ru": (
            "Проверка 29 февраля требует правила 400/4/100; "
            "одного «делится на 4» недостаточно (1900, 2100)."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): правило високосного года или mod "
            "перенесены из другого языка неверно."
        ),
        "contrast_test_indices": [0],
    },
    "while_sentinel": {
        "id": "while_sentinel",
        "transfer_type": "ATCC",
        "concept_ids": ["pre_condition_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Чтение до стоп-значения оформляется циклом с условием на входе, "
            "а не счётчиком по заранее известному n — см. «Циклы с условием»."
        ),
        "contrast_note_ru": (
            "Стоп-сигнал (0) не входит в результат; количество чисел заранее не задано."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): вместо цикла «пока не стоп» перенесён цикл for по n."
        ),
    },
    "search_first_guard": {
        "id": "search_first_guard",
        "transfer_type": "FCC",
        "concept_ids": ["search_find", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Первое вхождение: сохраняйте позицию только пока ответ ещё не найден — "
            "не обновляйте её на каждом совпадении."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): алгоритм последнего вхождения перенесён на поиск первого."
        ),
    },
    "search_last_overwrite": {
        "id": "search_last_overwrite",
        "transfer_type": "FCC",
        "concept_ids": ["search_find", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Последнее вхождение: при каждом совпадении обновляйте позицию — "
            "не останавливайтесь на первом и не блокируйте перезапись guard-условием."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): оставлен алгоритм первого вхождения вместо последнего."
        ),
    },
    "yes_no_output": {
        "id": "yes_no_output",
        "transfer_type": "AFCC",
        "concept_ids": ["stdout_write"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Ответ задачи — строки yes или no в нижнем регистре, "
            "не булевы литералы и не слова prime/composite."
        ),
        "contrast_note_ru": (
            "Формат вывода задан условием: одно слово yes или no без пояснений."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): выведен формат ответа из другой постановки."
        ),
        "contrast_test_indices": [0],
    },
    "mod_sqrt_loop": {
        "id": "mod_sqrt_loop",
        "transfer_type": "AFCC",
        "concept_ids": ["pre_condition_loop", "arithmetic_ops"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Проверка простоты: делители до корня из n; оператор остатка в целевом языке "
            "может отличаться — см. «Арифметика и выражения»."
        ),
        "contrast_note_ru": (
            "Достаточно перебора i, пока i×i ≤ n; полный перебор до n-1 избыточен, "
            "но главное — корректный mod/div."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): проверка делителей или остаток перенесены неверно."
        ),
    },
    "filter_non_negative": {
        "id": "filter_non_negative",
        "transfer_type": "FCC",
        "concept_ids": ["pre_condition_loop", "simple_branch"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "В сумму попадают только неотрицательные значения; отрицательные пропускаются, "
            "но чтение продолжается до стоп-нуля."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): условие фильтрации знака или стоп-сигнал обработаны неверно."
        ),
    },
    "loop_upper_bound_n": {
        "id": "loop_upper_bound_n",
        "transfer_type": "ATCC",
        "concept_ids": ["counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Верхняя граница цикла берётся из входного n, а не из фиксированной константы — "
            "см. «Счётный цикл»."
        ),
        "contrast_note_ru": (
            "Таблица умножения строится для множителей 1..n, где n задано на входе."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): граница цикла не привязана к n из условия."
        ),
    },
    "frequency_bucket": {
        "id": "frequency_bucket",
        "transfer_type": "AFCC",
        "concept_ids": ["fold_aggregate", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Частота цифры d хранится в ячейке с индексом d (0..9), "
            "а не суммируется в один общий счётчик."
        ),
        "contrast_note_ru": (
            "Гистограмма — десять независимых счётчиков; значение x увеличивает bucket[x]."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): вместо массива частот накоплен один агрегат."
        ),
    },
    "array_reverse_order": {
        "id": "array_reverse_order",
        "transfer_type": "ATCC",
        "concept_ids": ["indexed_sequence", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Разворот массива: обходите элементы с последнего к первому — "
            "порядок вывода обратный исходному."
        ),
        "contrast_note_ru": (
            "В Pascal удобен цикл downto; в Python — reversed или индекс от n−1 к 0."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): элементы выведены в прямом порядке вместо обратного."
        ),
        "contrast_test_indices": [0],
    },
    "cyclic_shift_mod_k": {
        "id": "cyclic_shift_mod_k",
        "transfer_type": "AFCC",
        "concept_ids": ["indexed_sequence", "arithmetic_ops"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Циклический сдвиг вправо на k: сначала k := k mod n, "
            "затем последние k элементов переносятся в начало."
        ),
        "contrast_note_ru": (
            "k и n приходят в одной строке; сдвиг на k, кратное n, не меняет массив."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): сдвиг выполнен без k mod n или в неверную сторону."
        ),
        "contrast_test_indices": [0],
    },
    "array_delete_shift": {
        "id": "array_delete_shift",
        "transfer_type": "FCC",
        "concept_ids": ["indexed_sequence", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Удаление на позиции pos (1-based) сдвигает элементы pos+1..n влево — "
            "не оставляйте «дыру» в массиве."
        ),
        "contrast_note_ru": (
            "pos вне 1..n — invalid; единственный элемент после удаления даёт пустой вывод."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): удаление выполнено с 0-based индексом или без сдвига хвоста."
        ),
    },
    "array_insert_shift": {
        "id": "array_insert_shift",
        "transfer_type": "FCC",
        "concept_ids": ["indexed_sequence", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Вставка на позицию pos раздвигает элементы с pos до n вправo — "
            "pos в условии 1-based, допустим 1..n+1."
        ),
        "contrast_note_ru": (
            "pos и значение x часто в одной строке; pos вне диапазона — invalid."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): вставка на pos без сдвига или со смещением на 0-based индекс."
        ),
    },
    "dual_array_concat": {
        "id": "dual_array_concat",
        "transfer_type": "AFCC",
        "concept_ids": ["indexed_sequence", "stdin_read"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Два массива: сначала n и n чисел, затем m и m чисел — "
            "результат: все элементы первого, потом второго."
        ),
        "contrast_note_ru": (
            "Порядок чтения строк важен; при m = 0 второй массив пуст."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): перепутан порядок чтения или объединения массивов."
        ),
        "contrast_test_indices": [0],
    },
    "duplicate_pair_loop": {
        "id": "duplicate_pair_loop",
        "transfer_type": "FCC",
        "concept_ids": ["counted_loop", "simple_branch"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Дубликаты ищите попарным сравнением при j > i — "
            "достаточно одного совпадения для yes."
        ),
        "contrast_note_ru": (
            "Не сравнивайте элемент только с соседом — нужны все пары с разными индексами."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): проверены не все пары или пропущены не соседние дубликаты."
        ),
    },
    "merge_sorted_two_ptr": {
        "id": "merge_sorted_two_ptr",
        "transfer_type": "AFCC",
        "concept_ids": ["indexed_sequence", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Два отсортированных массива сливаются двумя указателями — "
            "на каждом шаге берите меньший из текущих элементов."
        ),
        "contrast_note_ru": (
            "При равенстве сначала элемент из A; допишите хвост неслитого массива."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): результат пересортирован или слияние выполнено неверно."
        ),
        "contrast_test_indices": [0],
    },
    "sorted_insert_pos": {
        "id": "sorted_insert_pos",
        "transfer_type": "FCC",
        "concept_ids": ["search_find", "indexed_sequence"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "В отсортированном массиве найдите 1-based позицию вставки x — "
            "куда встанет x, сохраняя порядок."
        ),
        "contrast_note_ru": (
            "x меньше всех элементов → позиция 1; равные элементы — вставка после них."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): позиция вставки вычислена как 0-based или без учёта порядка."
        ),
    },
    "string_length_builtin": {
        "id": "string_length_builtin",
        "transfer_type": "ATCC",
        "concept_ids": ["string_sequence", "stdin_read"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Длина строки — число всех символов, включая пробелы; "
            "в целевом языке есть встроенная функция длины."
        ),
        "contrast_note_ru": (
            "Python len(s), Pascal length(s), C++ s.size() — не путайте с числом слов."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): длина строки посчитана вручную неверно или перепутана с словами."
        ),
        "contrast_test_indices": [0],
    },
    "string_reverse_chars": {
        "id": "string_reverse_chars",
        "transfer_type": "ATCC",
        "concept_ids": ["string_sequence"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Разворот строки — символы в обратном порядке; "
            "используйте идиому целевого языка, не копируйте срез Python буквально."
        ),
        "contrast_note_ru": (
            "Ответ — одна строка без пробелов между символами."
        ),
        "feedback_ru": (
            "Абстрактный перенос (ATCC): строка выведена не в обратном порядке символов."
        ),
        "contrast_test_indices": [0],
    },
    "palindrome_symmetry": {
        "id": "palindrome_symmetry",
        "transfer_type": "AFCC",
        "concept_ids": ["string_sequence", "search_find"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Палиндром читается одинаково слева направо и справа налево — "
            "сравните симметричные позиции или строку с её разворотом."
        ),
        "contrast_note_ru": (
            "Регистр символов учитывается; ответ — yes или no."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): проверка палиндрома выполнена неверно."
        ),
        "contrast_test_indices": [0],
    },
    "substring_first_1based": {
        "id": "substring_first_1based",
        "transfer_type": "FCC",
        "concept_ids": ["string_sequence", "search_find"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Первое вхождение подстроки: индекс в условии 1-based; "
            "в Python find даёт 0-based, в Pascal Pos — 1-based."
        ),
        "contrast_note_ru": (
            "Если подстрока не найдена — выведите 0, не отрицательный индекс."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): индекс подстроки перенесён как 0-based или без сдвига."
        ),
    },
    "word_split_spaces": {
        "id": "word_split_spaces",
        "transfer_type": "AFCC",
        "concept_ids": ["string_sequence", "stdin_read"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "Слова разделены пробелами — считайте группы непробельных символов; "
            "пустая строка даёт 0 слов."
        ),
        "contrast_note_ru": (
            "Подряд идущие пробелы не создают пустых слов."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): слова посчитаны по символам или с пустыми токенами."
        ),
        "contrast_test_indices": [0],
    },
    "anagram_letter_freq": {
        "id": "anagram_letter_freq",
        "transfer_type": "FCC",
        "concept_ids": ["string_sequence"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Анаграммы — одинаковый набор букв; сравните отсортированные символы "
            "или частоты, а не только равенство длины."
        ),
        "contrast_note_ru": (
            "Разная длина строк сразу означает no."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): анаграмма проверена сравнением строк без учёта перестановки букв."
        ),
    },
    "rle_run_encoding": {
        "id": "rle_run_encoding",
        "transfer_type": "AFCC",
        "concept_ids": ["string_sequence", "counted_loop"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "contrast_test",
        "hint_ru": (
            "RLE: каждая группа одинаковых символов → символ и длина группы подряд, "
            "без разделителей между парами."
        ),
        "contrast_note_ru": (
            "aaabb → a3b2; одиночный символ даёт суффикс 1."
        ),
        "feedback_ru": (
            "Абстрактно-ложный перенос (AFCC): сжатие RLE собрано неверно или группы разорваны."
        ),
        "contrast_test_indices": [0],
    },
    "text_stats_vowels": {
        "id": "text_stats_vowels",
        "transfer_type": "FCC",
        "concept_ids": ["string_sequence", "fold_aggregate"],
        "source_langs": ["python", "cpp", "csharp", "java", "pascal"],
        "target_langs": ["pascal", "python", "cpp", "csharp", "java"],
        "detector": "matches_buggy",
        "hint_ru": (
            "Три числа: длина строки, число слов и гласных aeiou — "
            "пробелы входят в длину, но не в слова."
        ),
        "contrast_note_ru": (
            "Гласные считаются по латинским a, e, i, o, u без учёта регистра."
        ),
        "feedback_ru": (
            "Ложный перенос (FCC): перепутаны длина, слова и гласные или неверно посчитаны гласные."
        ),
    },
}


def get_pitfall(pitfall_id: str | None) -> PitfallSpec | None:
    if not pitfall_id:
        return None
    spec = PITFALLS.get(str(pitfall_id).strip())
    return dict(spec) if spec else None


def build_pitfall_payload(pitfall_id: str | None) -> dict[str, Any]:
    spec = get_pitfall(pitfall_id)
    if not spec:
        return {}
    return _build_pitfall_payload_from_spec(spec, pitfall_id)


def _normalize_pitfall_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def pitfall_applies_to_language_pair(
    spec: PitfallSpec | dict[str, Any],
    *,
    source_language: str,
    target_language: str,
) -> bool:
    source = _normalize_pitfall_lang(source_language)
    target = _normalize_pitfall_lang(target_language)
    if source == target:
        return False
    source_langs = [_normalize_pitfall_lang(item) for item in (spec.get("source_langs") or [])]
    target_langs = [_normalize_pitfall_lang(item) for item in (spec.get("target_langs") or [])]
    if source_langs and source not in source_langs:
        return False
    if target_langs and target not in target_langs:
        return False
    return True


def build_pitfall_payload_for_languages(
    pitfall_id: str | None,
    *,
    source_language: str,
    target_language: str,
) -> dict[str, Any]:
    """Proactive MPLT payload for a concrete mirror pair (source → target)."""
    spec = get_pitfall(pitfall_id)
    if not spec or not pitfall_applies_to_language_pair(
        spec,
        source_language=source_language,
        target_language=target_language,
    ):
        return {}

    payload = _build_pitfall_payload_from_spec(
        spec,
        pitfall_id,
        source_language=source_language,
        target_language=target_language,
    )
    proactive = _proactive_warning_for_pair(spec, source_language, target_language)
    if proactive:
        payload["reference_warning_ru"] = proactive
        if not payload.get("pedagogy_note_ru"):
            payload["hint_ru"] = proactive
    return payload


def _proactive_warning_for_pair(
    spec: PitfallSpec | dict[str, Any],
    source_language: str,
    target_language: str,
) -> str:
    source = _normalize_pitfall_lang(source_language)
    target = _normalize_pitfall_lang(target_language)
    from application.curriculum.display.pitfall_pair_hints import proactive_pitfall_hint
    from application.curriculum.display.pitfall_messages import contrast_note_message

    pid = str(spec.get("id") or "").strip()
    pair_hint = proactive_pitfall_hint(pid, source_language=source, target_language=target)
    if pair_hint:
        return pair_hint

    from application.curriculum.display.atcc_idiom_engine import idiom_hint_for_concept

    for concept_id in spec.get("concept_ids") or []:
        hint = idiom_hint_for_concept(source, target, str(concept_id))
        if hint:
            return hint

    tt = str(spec.get("transfer_type") or "").upper()
    if tt == "AFCC":
        return str(
            proactive_pitfall_hint(pid, source_language=source, target_language=target)
            or contrast_note_message(pid, source_language=source, target_language=target)
            or spec.get("contrast_note_ru")
            or spec.get("hint_ru")
            or ""
        ).strip()
    if tt == "FCC":
        return str(
            proactive_pitfall_hint(pid, source_language=source, target_language=target)
            or spec.get("hint_ru")
            or spec.get("contrast_note_ru")
            or ""
        ).strip()
    return str(
        proactive_pitfall_hint(pid, source_language=source, target_language=target)
        or spec.get("hint_ru")
        or spec.get("pedagogy_note_ru")
        or ""
    ).strip()


def _build_pitfall_payload_from_spec(
    spec: PitfallSpec | dict[str, Any],
    pitfall_id: str | None,
    *,
    source_language: str = "python",
    target_language: str = "pascal",
) -> dict[str, Any]:
    from application.curriculum.display.pitfall_messages import (
        contrast_note_message,
        proactive_pitfall_message,
        reactive_pitfall_message,
    )

    pid = str(spec.get("id") or pitfall_id or "").strip()
    hint = proactive_pitfall_message(
        pid, source_language=source_language, target_language=target_language,
    ) or str(spec.get("hint_ru") or "").strip()
    feedback = reactive_pitfall_message(
        pid, source_language=source_language, target_language=target_language,
    ) or str(spec.get("feedback_ru") or "").strip()
    contrast = contrast_note_message(
        pid, source_language=source_language, target_language=target_language,
    ) or str(spec.get("contrast_note_ru") or "").strip()
    reference_warning = (
        spec.get("reference_warning_ru")
        or contrast
        or hint
        or spec.get("pedagogy_note_ru")
    )
    return {
        "pitfall_id": spec.get("id") or pitfall_id,
        "transfer_type": spec.get("transfer_type"),
        "hint_ru": hint or None,
        "contrast_note_ru": contrast or None,
        "reference_warning_ru": reference_warning,
        "feedback_ru": feedback or None,
        "pedagogy_note_ru": spec.get("pedagogy_note_ru"),
        "detector": spec.get("detector"),
        "contrast_test_indices": list(spec.get("contrast_test_indices") or []),
    }


def list_pitfall_ids() -> list[str]:
    return sorted(PITFALLS.keys())


def pitfall_ids_for_transfer_type(transfer_type: str) -> list[str]:
    tt = str(transfer_type or "").strip().upper()
    return sorted(
        key
        for key, spec in PITFALLS.items()
        if str(spec.get("transfer_type") or "").upper() == tt
    )


def validate_pitfall_id(pitfall_id: str | None) -> bool:
    if not pitfall_id:
        return False
    return str(pitfall_id).strip() in PITFALLS
