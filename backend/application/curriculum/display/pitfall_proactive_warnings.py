"""Proactive MPLT warnings — one language pair, no verbatim code (see expected concepts for syntax)."""

from __future__ import annotations

PairKey = tuple[str, str]

_LANG_RU: dict[str, str] = {
    "pascal": "Pascal",
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
}


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _lang_label(language: str) -> str:
    return _LANG_RU.get(_normalize_lang(language), language)

_COURSE_LANGS: tuple[str, ...] = ("python", "pascal", "cpp", "csharp", "java")
_ZERO_BASED: frozenset[str] = frozenset({"python", "cpp", "csharp", "java"})
_C_LIKE: frozenset[str] = frozenset({"cpp", "csharp", "java"})


def _warn(source: str, target: str, body: str) -> str:
    return (
        f"При переносе из {_lang_label(source)} в {_lang_label(target)}: "
        f"{body.strip()}"
    )


def _all_pairs() -> list[PairKey]:
    return [(s, t) for s in _COURSE_LANGS for t in _COURSE_LANGS if s != t]


def _for_range_off_by_one() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in _ZERO_BASED:
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "цикл по n элементам обычно начинается с нуля; "
            "в Pascal для n повторений счётчик идёт от 1 до n включительно. "
            "Не копируйте границы дословно — проверьте число итераций и начальный индекс "
            "(подсказка в ожидаемых конструкциях).",
        )
    for tgt in _ZERO_BASED:
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "цикл от 1 до n включает обе границы; "
            f"в {_lang_label(tgt)} проход по n элементам обычно начинается с нуля. "
            "Учтите сдвиг индекса или счётчика при переносе.",
        )
    for src in _C_LIKE:
        for tgt in _C_LIKE:
            if src != tgt:
                out[(src, tgt)] = _warn(
                    src,
                    tgt,
                    "границы цикла по n элементам совпадают по идее (с нуля), "
                    "но синтаксис заголовка цикла разный — не переносите конструкцию буквально.",
                )
    return out


def _integer_division() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in _ZERO_BASED:
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "в исходном языке целое частное записывается иначе, чем в Pascal; "
            "оператор / в Pascal даёт вещественный результат — для целой части нужен div.",
        )
    for tgt in _ZERO_BASED:
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "в Pascal целая часть — через div; "
            f"в {_lang_label(tgt)} правило деления для целых другое. "
            "Не переносите оператор деления буквально.",
        )
    for src in _C_LIKE:
        for tgt in _C_LIKE:
            if src != tgt:
                out[(src, tgt)] = _warn(
                    src,
                    tgt,
                    "для целых чисел деление в обоих языках даёт целую часть, "
                    "но не переносите комментарии и лишние скобки из другого синтаксиса.",
                )
    out[("python", "cpp")] = _warn(
        "python",
        "cpp",
        "в Python целое частное — отдельный оператор; "
        "в C++ двойной слэш — это комментарий, не деление.",
    )
    out[("python", "java")] = _warn(
        "python",
        "java",
        "в Python целое частное — отдельный оператор; "
        "в Java двойной слэш — это комментарий, не деление.",
    )
    out[("python", "csharp")] = _warn(
        "python",
        "csharp",
        "в Python целое частное — отдельный оператор; "
        "в C# двойной слэш — это комментарий, не деление.",
    )
    return out


def _index_1based() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in _ZERO_BASED:
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "первый элемент в исходном языке имеет индекс 0; "
            "в Pascal статический массив array[1..n] начинается с 1. "
            "Не вычитайте и не прибавляйте единицу без проверки условия задачи.",
        )
    for tgt in _ZERO_BASED:
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "в Pascal первый элемент массива — с индекса 1; "
            f"в {_lang_label(tgt)} — с нуля. Учтите сдвиг при переносе обращений к элементам.",
        )
    return out


def _elif_chain() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for tgt in _COURSE_LANGS:
        if tgt == "python":
            continue
        if tgt == "pascal":
            body = (
                "цепочка взаимоисключающих веток в Python оформляется иначе, "
                "чем в Pascal — не переносите ключевые слова буквально; "
                "пример цепочки веток смотрите в «Условия и ветвление»."
            )
        elif tgt in _C_LIKE:
            body = (
                "цепочка взаимоисключающих веток в Python оформляется иначе "
                "в C-family — не оставляйте синтаксис исходного языка; "
                "см. «Условия и ветвление»."
            )
        else:
            body = (
                "цепочка взаимоисключающих веток оформляется идиомой целевого языка — "
                "см. «Условия и ветвление»."
            )
        out[("python", tgt)] = _warn("python", tgt, body)

    for src in _C_LIKE:
        if src == "pascal":
            continue
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "заголовок следующей ветки в C-family записывается иначе, чем в Pascal — "
            "не переносите скобки и служебные слова буквально; "
            "пример в «Условия и ветвление».",
        )
    return out


def _pascal_case_labels() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for tgt in _COURSE_LANGS:
        if tgt == "python":
            continue
        if tgt == "pascal":
            body = (
                "несколько значений одной ветки в Pascal объединяют в одном case; "
                "в Python для того же смысла используют проверку принадлежности множеству. "
                "Пример сезона по месяцу — в «Выбор по значению»."
            )
        elif tgt in _C_LIKE:
            body = (
                "несколько месяцев одного сезона в C-family оформляют несколькими метками "
                "подряд с выходом из switch; в Python — через проверку нескольких значений. "
                "Смотрите пример в «Выбор по значению»."
            )
        else:
            body = (
                "выбор по нескольким значениям одной ветки записывается идиомой целевого языка — "
                "см. «Выбор по значению»."
            )
        out[("python", tgt)] = _warn("python", tgt, body)
    return out


def _leap_year_mod() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in _ZERO_BASED:
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "правило високосного года (400 / 4 / 100) и оператор остатка в Pascal "
            "отличаются от исходного языка — не переносите формулу буквально; "
            "пример в «Арифметика и выражения».",
        )
    for tgt in _ZERO_BASED:
        if tgt == "pascal":
            continue
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "в Pascal остаток записывается своим оператором; при переносе в целевой язык "
            "замените его и проверьте правило 400/4/100 для февраля — "
            "см. «Арифметика и выражения».",
        )
    for src in _C_LIKE:
        for tgt in _C_LIKE:
            if src != tgt:
                out[(src, tgt)] = _warn(
                    src,
                    tgt,
                    "формула високосного года та же по смыслу, но синтаксис остатка и скобок "
                    "разный — сверьте с примером в «Арифметика и выражения».",
                )
    return out


def _assignment_vs_compare() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in ("python", "cpp", "csharp", "java"):
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "в исходном языке один символ = часто означает присваивание; "
            "в Pascal присваивание и сравнение записываются разными операторами. "
            "Проверьте условия и присваивания — пример в «Условия и ветвление».",
        )
    out[("pascal", "python")] = _warn(
        "pascal",
        "python",
        "в Pascal = в условии — сравнение, а присваивание — отдельный оператор; "
        "в Python = — присваивание, сравнение — другой оператор (см. «Условия и ветвление»).",
    )
    for tgt in _C_LIKE:
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "в Pascal присваивание и сравнение на равенство записываются разными операторами; "
            f"в {_lang_label(tgt)} правило другое — см. «Условия и ветвление».",
        )
    return out


def _input_line_model() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in _ZERO_BASED:
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "модель ввода может отличаться: несколько чисел в одной строке "
            "читаются иначе, чем по одному числу на строку. "
            "Сверьте формат входа с примером в «Ввод и вывод (консоль)».",
        )
    for tgt in _ZERO_BASED:
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "в Pascal readln с несколькими переменными читает из одной строки; "
            f"в {_lang_label(tgt)} для той же строки входа нужна своя идиома разбора. "
            "Не переносите количество вызовов чтения буквально.",
        )
    for src in _C_LIKE:
        for tgt in _C_LIKE:
            if src != tgt:
                out[(src, tgt)] = _warn(
                    src,
                    tgt,
                    "способ чтения нескольких чисел из одной строки входа различается — "
                    "проверьте формат тестовых данных.",
                )
    return out


def _output_space_separated() -> dict[PairKey, str]:
    out: dict[PairKey, str] = {}
    for src in _ZERO_BASED:
        out[(src, "pascal")] = _warn(
            src,
            "pascal",
            "несколько значений в одной строке вывода оформляются иначе, "
            "чем отдельный вывод каждого на своей строке. "
            "Проверьте, ждёт ли задача одну строку с пробелами.",
        )
    for tgt in _ZERO_BASED:
        out[("pascal", tgt)] = _warn(
            "pascal",
            tgt,
            "в Pascal несколько аргументов writeln попадают в одну строку; "
            f"в {_lang_label(tgt)} для того же эффекта нужен свой способ форматирования вывода.",
        )
    for src in _C_LIKE:
        for tgt in _C_LIKE:
            if src != tgt:
                out[(src, tgt)] = _warn(
                    src,
                    tgt,
                    "вывод нескольких значений в одной строке с пробелами "
                    "оформляется по-разному — не дублируйте отдельный вывод на каждую строку.",
                )
    return out


def _single_pair_pitfalls() -> dict[str, dict[PairKey, str]]:
    """Pitfalls with mostly python↔pascal relevance."""
    return {
        "string_index": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "позиция первого символа в строке в Python отсчитывается с нуля, "
                "в Pascal функция поиска — с единицы. Не сдвигайте результат без проверки задачи.",
            ),
        },
        "round_semantics": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "правила округления .5 в Python и Pascal могут различаться — "
                "подберите функцию под ожидаемый ответ теста.",
            ),
        },
        "float_division_pascal": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "даже для целых переменных / в Pascal даёт вещественный результат; "
                "для целой части используйте div.",
            ),
        },
        "mod_negative": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "остаток от деления в Pascal (mod) может вести себя иначе, "
                "чем % в Python, для отрицательных операндов.",
            ),
        },
        "switch_fallthrough": {
            ("python", "cpp"): _warn(
                "python",
                "cpp",
                "в C++ switch без явного выхода проваливается в следующую ветку — "
                "после каждой ветки нужен выход; пример в «Выбор по значению».",
            ),
            ("python", "csharp"): _warn(
                "python",
                "csharp",
                "в C# switch без явного выхода проваливается в следующую ветку — "
                "после каждой ветки нужен выход; пример в «Выбор по значению».",
            ),
            ("pascal", "cpp"): _warn(
                "pascal",
                "cpp",
                "в Pascal case of не требует явного выхода; в C++ switch без него "
                "выполнение идёт дальше — см. «Выбор по значению».",
            ),
            ("pascal", "csharp"): _warn(
                "pascal",
                "csharp",
                "в Pascal case of не требует явного выхода; в C# switch без него "
                "выполнение идёт дальше — см. «Выбор по значению».",
            ),
        },
        "chain_comparison": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "цепочка сравнений в одном условии в Python не переносится в Pascal напрямую — "
                "разбейте на два сравнения, соединённые and (см. «Условия и ветвление»).",
            ),
            ("python", "cpp"): _warn(
                "python",
                "cpp",
                "цепочка сравнений в Python записывается иначе, чем в C++ — "
                "используйте два сравнения с && (см. «Условия и ветвление»).",
            ),
            ("python", "csharp"): _warn(
                "python",
                "csharp",
                "цепочка сравнений в Python записывается иначе, чем в C# — "
                "используйте два сравнения с && (см. «Условия и ветвление»).",
            ),
            ("python", "java"): _warn(
                "python",
                "java",
                "цепочка сравнений в Python записывается иначе, чем в Java — "
                "используйте два сравнения с && (см. «Условия и ветвление»).",
            ),
        },
        "and_or_keywords": {
            ("python", "cpp"): _warn(
                "python",
                "cpp",
                "логические and/or — синтаксис Python; в C++ используются операторы && и ||.",
            ),
            ("python", "csharp"): _warn(
                "python",
                "csharp",
                "логические and/or — синтаксис Python; в C# — && и ||.",
            ),
            ("python", "java"): _warn(
                "python",
                "java",
                "логические and/or — синтаксис Python; в Java — && и ||.",
            ),
        },
        "bool_literals": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "литералы True/False в Python не совпадают с true/false в Pascal — "
                "обратите внимание на регистр.",
            ),
        },
        "string_immutable": {
            ("python", "java"): _warn(
                "python",
                "java",
                "строка в Java неизменяема так же, как список символов в Python — "
                "для правок нужен другой тип.",
            ),
        },
        "list_vs_static_array": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "список Python может расти динамически; "
                "в Pascal массив фиксированного размера — сначала узнайте n, затем заполняйте по индексу.",
            ),
        },
        "scope_block": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "выход из процедуры/функции и возврат значения оформляются иначе, "
                "чем return в Python — в Pascal результат задают через имя функции.",
            ),
        },
        "while_sentinel": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "числа читаются до стоп-значения — цикл с условием на входе, "
                "а не for по заранее известному n; см. «Циклы с условием».",
            ),
            ("python", "cpp"): _warn(
                "python",
                "cpp",
                "количество чисел не задано: используйте цикл while до стоп-сигнала, "
                "не фиксированный for по n — см. «Циклы с условием».",
            ),
        },
        "search_first_guard": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "первое вхождение: сохраняйте позицию только пока ответ ещё не найден — "
                "не перезаписывайте её на каждом совпадении.",
            ),
        },
        "search_last_overwrite": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "последнее вхождение: обновляйте позицию при каждом совпадении — "
                "guard «только если ещё ноль» здесь лишний.",
            ),
        },
        "yes_no_output": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "ответ — строки yes или no в нижнем регистре, "
                "не булевы литералы и не другие слова из постановки.",
            ),
        },
        "mod_sqrt_loop": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "проверка делителей до корня из n; оператор остатка mod/% "
                "записывается идиомой целевого языка — см. «Арифметика и выражения».",
            ),
        },
        "filter_non_negative": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "в сумму попадают только неотрицательные; стоп-ноль завершает ввод, "
                "но не добавляется к сумме.",
            ),
        },
        "loop_upper_bound_n": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "верхняя граница счётного цикла — входное n, не фиксированная константа; "
                "см. «Счётный цикл».",
            ),
        },
        "frequency_bucket": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "для каждой цифры 0..9 свой счётчик — значение x увеличивает bucket с индексом x, "
                "а не один общий итог.",
            ),
        },
        "array_reverse_order": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "элементы выводятся в обратном порядке — обходите массив с последнего к первому, "
                "см. «Массивы и коллекции».",
            ),
            ("python", "cpp"): _warn(
                "python",
                "cpp",
                "разворот массива: выводите элементы от последнего к первому — "
                "см. «Массивы и коллекции».",
            ),
        },
        "cyclic_shift_mod_k": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "циклический сдвиг вправо: сначала приведите k по остатку от деления на n, "
                "затем последние k элементов переносятся в начало — см. «Массивы и коллекции».",
            ),
        },
        "array_delete_shift": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "удаление на позиции pos сдвигает хвост массива влево — pos в условии считается с единицы.",
            ),
        },
        "array_insert_shift": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "вставка на позиции pos раздвигает элементы вправо — pos в условии 1-based, "
                "см. «Массивы и коллекции».",
            ),
        },
        "dual_array_concat": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "два массива подряд: размер и элементы первого, затем второго — "
                "не перепутайте порядок чтения.",
            ),
        },
        "duplicate_pair_loop": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "дубликаты ищите попарным сравнением при j > i — ответ yes или no, "
                "не другие слова.",
            ),
        },
        "merge_sorted_two_ptr": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "два отсортированных массива сливаются двумя указателями без повторной сортировки — "
                "см. «Массивы и коллекции».",
            ),
        },
        "sorted_insert_pos": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "в отсортированном массиве найдите 1-based позицию вставки x — "
                "куда встанет x, сохраняя порядок.",
            ),
        },
        "string_length_builtin": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "длина строки — все символы включая пробелы; "
                "используйте встроенную функцию длины целевого языка — см. «Строки».",
            ),
        },
        "string_reverse_chars": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "разворот строки — символы в обратном порядке; "
                "см. «Строки» в ожидаемых конструкциях.",
            ),
        },
        "palindrome_symmetry": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "палиндром читается одинаково с обеих сторон — "
                "ответ yes или no в нижнем регистре.",
            ),
        },
        "substring_first_1based": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "первое вхождение подстроки: индекс с единицы, "
                "не переносите 0-based find без сдвига — см. «Строки».",
            ),
        },
        "word_split_spaces": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "слова разделены пробелами — считайте непробельные группы; "
                "пустая строка даёт 0 слов.",
            ),
        },
        "anagram_letter_freq": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "анаграммы — одинаковый набор букв; сравните отсортированные символы, "
                "не только длину строк.",
            ),
        },
        "rle_run_encoding": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "RLE: символ и длина каждой группы одинаковых символов подряд — "
                "см. «Строки».",
            ),
        },
        "text_stats_vowels": {
            ("python", "pascal"): _warn(
                "python",
                "pascal",
                "три числа: длина, слова и гласные aeiou — пробелы в длине, но не в словах.",
            ),
        },
    }


def build_proactive_warnings() -> dict[str, dict[PairKey, str]]:
    merged: dict[str, dict[PairKey, str]] = {
        "for_range_off_by_one": _for_range_off_by_one(),
        "integer_division": _integer_division(),
        "index_1based": _index_1based(),
        "assignment_vs_compare": _assignment_vs_compare(),
        "input_line_model": _input_line_model(),
        "output_space_separated": _output_space_separated(),
        "elif_chain": _elif_chain(),
        "pascal_case_labels": _pascal_case_labels(),
        "leap_year_mod": _leap_year_mod(),
    }
    for pid, pairs in _single_pair_pitfalls().items():
        merged[pid] = pairs
    return merged


PROACTIVE_FALLBACK: dict[str, str] = {
    "for_range_off_by_one": (
        "проверьте границы цикла и число итераций — подробности в ожидаемых конструкциях."
    ),
    "integer_division": (
        "целое деление в целевом языке записывается иначе — не переносите оператор буквально."
    ),
    "index_1based": (
        "нумерация элементов массива может начинаться с другого индекса — учтите сдвиг."
    ),
    "assignment_vs_compare": (
        "присваивание и сравнение в целевом языке различаются иначе — проверьте условия."
    ),
    "input_line_model": (
        "формат ввода (одна строка или несколько) влияет на способ чтения — сверьте с тестом."
    ),
    "output_space_separated": (
        "несколько чисел в одной строке вывода оформляются иначе — проверьте формат ответа."
    ),
    "elif_chain": (
        "цепочка взаимоисключающих веток оформляется идиомой целевого языка — "
        "см. «Условия и ветвление»."
    ),
    "pascal_case_labels": (
        "несколько значений одной ветки оформляются идиомой целевого языка — "
        "см. «Выбор по значению»."
    ),
    "leap_year_mod": (
        "правило високосного года и оператор остатка различаются — "
        "см. «Арифметика и выражения»."
    ),
    "switch_fallthrough": (
        "в C-family switch без явного выхода проваливается в следующую ветку — "
        "см. «Выбор по значению»."
    ),
    "while_sentinel": (
        "ввод до стоп-значения оформляется циклом с условием — см. «Циклы с условием»."
    ),
    "search_first_guard": (
        "первое вхождение: не перезаписывайте найденную позицию на каждом совпадении."
    ),
    "search_last_overwrite": (
        "последнее вхождение: обновляйте позицию при каждом совпадении, без guard на ноль."
    ),
    "yes_no_output": (
        "ответ — yes или no в нижнем регистре, не булевы литералы и не другие слова."
    ),
    "mod_sqrt_loop": (
        "делители до корня из n; оператор остатка — идиома целевого языка."
    ),
    "filter_non_negative": (
        "суммируйте только неотрицательные; ноль — стоп-сигнал, не слагаемое."
    ),
    "loop_upper_bound_n": (
        "граница цикла берётся из n на входе — см. «Счётный цикл»."
    ),
    "frequency_bucket": (
        "частота цифры d — в ячейке с индексом d, не в одном общем счётчике."
    ),
    "array_reverse_order": (
        "разворот массива — обход с последнего элемента к первому; см. «Массивы и коллекции»."
    ),
    "cyclic_shift_mod_k": (
        "сдвиг на k: сначала остаток от деления k на n, затем циклическая перестановка вправо."
    ),
    "array_delete_shift": (
        "удаление на pos сдвигает хвост — pos считается с единицы."
    ),
    "array_insert_shift": (
        "вставка на pos раздвигает элементы — pos 1-based; см. «Массивы и коллекции»."
    ),
    "dual_array_concat": (
        "два массива: n элементов, затем m элементов — порядок чтения важен."
    ),
    "duplicate_pair_loop": (
        "дубликаты — попарное сравнение при j > i; ответ yes или no."
    ),
    "merge_sorted_two_ptr": (
        "слияние отсортированных массивов двумя указателями — без повторной сортировки."
    ),
    "sorted_insert_pos": (
        "1-based позиция вставки x в отсортированный массив."
    ),
    "string_length_builtin": (
        "длина строки — все символы; встроенная функция длины целевого языка."
    ),
    "string_reverse_chars": (
        "разворот строки — символы в обратном порядке; см. «Строки»."
    ),
    "palindrome_symmetry": (
        "палиндром — симметрия слева направо; ответ yes или no."
    ),
    "substring_first_1based": (
        "первое вхождение подстроки — индекс с единицы, не 0-based find."
    ),
    "word_split_spaces": (
        "слова — группы между пробелами; пустая строка → 0 слов."
    ),
    "anagram_letter_freq": (
        "анаграмма — одинаковый набор букв, не только равная длина."
    ),
    "rle_run_encoding": (
        "RLE: символ и длина каждой группы подряд одинаковых символов."
    ),
    "text_stats_vowels": (
        "длина, слова и гласные aeiou — три числа в одной строке."
    ),
}


def proactive_warning_for_pair(
    pitfall_id: str,
    *,
    source_language: str,
    target_language: str,
) -> str | None:
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if source == target:
        return None
    catalog = build_proactive_warnings()
    text = str((catalog.get(pitfall_id) or {}).get((source, target)) or "").strip()
    if text:
        return text
    fallback = PROACTIVE_FALLBACK.get(pitfall_id)
    if fallback:
        return _warn(source, target, fallback)
    return None
