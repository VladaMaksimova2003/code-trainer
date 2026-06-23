"""MPLT messages: proactive = краткое предупреждение для пары языков; reactive = разбор с кодом при сдаче."""

from __future__ import annotations

from typing import Final

PairKey = tuple[str, str]

_LANG_RU: dict[str, str] = {
    "pascal": "Pascal",
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
}

_BANNED_FRAGMENTS: Final[frozenset[str]] = frozenset(
    {
        "в этом языке это работает иначе",
        "используется другая идиом",
        "диапазоны задаются иначе",
        "модель ввода отличается",
        "есть особенности реализации",
        "следует использовать другой подход",
        "а не идиома целевого",
        "перенос конструкции",
        "модель ввода перенесена",
    }
)


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _lang_label(language: str) -> str:
    return _LANG_RU.get(_normalize_lang(language), language)


def _pick(messages: dict[PairKey, str], source: str, target: str) -> str | None:
    source = _normalize_lang(source)
    target = _normalize_lang(target)
    for key in ((source, target), (source, "*"), ("*", target), ("*", "*")):
        text = str(messages.get(key) or "").strip()
        if text:
            return text
    return None


def _assert_concrete(text: str, *, pitfall_id: str, kind: str) -> str:
    lowered = text.lower()
    for fragment in _BANNED_FRAGMENTS:
        if fragment in lowered:
            raise ValueError(f"{pitfall_id}/{kind}: banned vague fragment {fragment!r}")
    return text


# --- Proactive (amber banner) — pair-only warnings, no verbatim code ---

# Proactive texts: pitfall_proactive_warnings.py
# --- Reactive (post-submit feedback body, without detector prefix) ---

_FEEDBACK: dict[str, dict[PairKey, str]] = {
    "integer_division": {
        ("python", "pascal"): (
            "Похоже, здесь перенесён оператор / из Python.\n\n"
            "Ваш код:\n"
            "total / n\n\n"
            "В Pascal:\n"
            "total div n\n\n"
            "В Pascal оператор / возвращает вещественное число (real).\n"
            "Если нужен целый результат деления, используйте div."
        ),
        ("pascal", "python"): (
            "Похоже, вы перенесли div из Pascal в Python.\n\n"
            "Ваш код (ошибка):\n"
            "total div n\n\n"
            "В Python:\n"
            "total // n\n\n"
            "Одиночный / в Python даёт float, даже для int."
        ),
        ("cpp", "pascal"): (
            "Похоже, вы использовали / как в C++.\n\n"
            "Ваш код:\n"
            "total / n\n\n"
            "В Pascal для целого частного:\n"
            "total div n\n\n"
            "/ в Pascal даёт real, не целое."
        ),
        ("pascal", "cpp"): (
            "Похоже, вы написали div в C++.\n\n"
            "В C++ целое частное:\n"
            "total / n  (для int)\n\n"
            "Ключевое слово div — синтаксис Pascal."
        ),
        ("java", "pascal"): (
            "Похоже, вы использовали / как в Java.\n\n"
            "Ваш код:\n"
            "total / n\n\n"
            "В Pascal:\n"
            "total div n"
        ),
        ("pascal", "java"): (
            "Похоже, в Java использован div из Pascal.\n\n"
            "В Java целое частное для int:\n"
            "total / n"
        ),
        ("csharp", "pascal"): (
            "Похоже, вы использовали / как в C#.\n\n"
            "Ваш код:\n"
            "total / n\n\n"
            "В Pascal:\n"
            "total div n"
        ),
        ("pascal", "csharp"): (
            "Похоже, в C# использован div.\n\n"
            "В C# целое частное для int:\n"
            "total / n"
        ),
        ("*", "pascal"): (
            "Похоже, в Pascal использован оператор / для целого частного.\n\n"
            "Замените a / b на a div b — / даёт real."
        ),
    },
    "index_1based": {
        ("python", "pascal"): (
            "Похоже, вы обратились к a[0] как в Python.\n\n"
            "В Pascal массив array[1..n]:\n"
            "первый элемент — a[1], не a[0]."
        ),
    },
    "for_range_off_by_one": {
        ("python", "pascal"): (
            "Похоже, здесь перенесена форма цикла из Python.\n\n"
            "Python:\n"
            "for i in range(n):\n"
            "    ...\n\n"
            "Pascal:\n"
            "for i := 1 to n do\n"
            "begin\n"
            "    ...\n"
            "end;\n\n"
            "range(n) выполняется n раз, но начинает счёт с 0.\n"
            "В Pascal диапазон 1..n тоже даёт n итераций, потому что обе границы включены."
        ),
        ("cpp", "pascal"): (
            "Похоже, границы цикла скопированы из C++ (0..n-1).\n\n"
            "C++: for (int i = 0; i < n; i++)\n"
            "Pascal: for i := 1 to n do\n\n"
            "Проверьте, с какого индекса и сколько итераций нужно в задаче."
        ),
    },
    "assignment_vs_compare": {
        ("python", "pascal"): (
            "Похоже, в условии использован один символ = для присваивания.\n\n"
            "Pascal:\n"
            "присваивание — :=\n"
            "сравнение — =\n\n"
            "Пример: if x = 5 then, не if x := 5."
        ),
    },
    "string_index": {
        ("python", "pascal"): (
            "Похоже, позиция символа вычислена как s.find(...) в Python (с нуля).\n\n"
            "Pascal Pos(ch, s) возвращает 1 для первого символа.\n"
            "Не вычитайте 1 без проверки формулировки задачи."
        ),
    },
    "round_semantics": {
        ("python", "pascal"): (
            "Похоже, вы вызвали Round(x) как round(x) из Python.\n\n"
            "Round(2.5) в Pascal и round(2.5) в Python дают разный результат для .5.\n"
            "Подберите функцию округления под тест задачи."
        ),
    },
    "input_line_model": {
        ("python", "pascal"): (
            "Похоже, вы читаете данные по одному числу.\n\n"
            "Ваш код:\n"
            "readln(a);\n"
            "readln(b);\n"
            "readln(c);\n\n"
            "Но тест подаёт данные одной строкой:\n"
            "1 2 3\n\n"
            "Правильный вариант:\n"
            "readln(a, b, c);"
        ),
        ("pascal", "python"): (
            "Похоже, вы перенесли readln(a, b, c) из Pascal.\n\n"
            "Ваш код (ошибка):\n"
            "a, b, c = readln()\n\n"
            "В Python:\n"
            "a, b, c = map(int, input().split())\n\n"
            "input().split() разбирает одну строку «1 2 3»."
        ),
        ("cpp", "pascal"): (
            "Похоже, вы читаете через cin >> по одному числу.\n\n"
            "Ваш код:\n"
            "readln(a);\n"
            "readln(b);\n\n"
            "Если вход — одна строка «1 2 3», в Pascal:\n"
            "readln(a, b, c);"
        ),
        ("pascal", "cpp"): (
            "Похоже, вы перенесли readln(a, b, c) в C++.\n\n"
            "В C++:\n"
            "cin >> a >> b >> c;\n\n"
            "Три отдельных readln в Pascal читают три строки, не одну."
        ),
        ("java", "pascal"): (
            "Похоже, вы читаете через nextInt() по одному.\n\n"
            "Ваш код:\n"
            "readln(a);\n"
            "readln(b);\n\n"
            "Для строки «1 2 3» в Pascal:\n"
            "readln(a, b, c);"
        ),
        ("pascal", "java"): (
            "Похоже, в Java использован readln из Pascal.\n\n"
            "В Java:\n"
            "Scanner sc = new Scanner(System.in);\n"
            "int a = sc.nextInt();\n"
            "int b = sc.nextInt();"
        ),
        ("csharp", "pascal"): (
            "Похоже, вы читаете через ReadLine по одному.\n\n"
            "Ваш код:\n"
            "readln(a);\n"
            "readln(b);\n\n"
            "Для одной строки входа в Pascal:\n"
            "readln(a, b, c);"
        ),
        ("pascal", "csharp"): (
            "Похоже, в C# использован readln из Pascal.\n\n"
            "Ваш код (ошибка):\n"
            "readln(a, b, c);\n\n"
            "В C#:\n"
            "var parts = Console.ReadLine().Split();\n"
            "int a = int.Parse(parts[0]);"
        ),
    },
    "output_space_separated": {
        ("python", "pascal"): (
            "Похоже, три числа выводятся отдельными writeln.\n\n"
            "Ваш код:\n"
            "writeln(a);\n"
            "writeln(b);\n"
            "writeln(c);\n\n"
            "Тест ожидает одну строку:\n"
            "1 2 3\n\n"
            "Правильный вариант:\n"
            "writeln(a, ' ', b, ' ', c);"
        ),
        ("pascal", "python"): (
            "Похоже, вы перенесли writeln(a, b, c) из Pascal.\n\n"
            "В Python для одной строки:\n"
            "print(a, b, c)\n\n"
            "Три отдельных print(a) дают три строки."
        ),
        ("cpp", "pascal"): (
            "Похоже, вывод разбит на несколько writeln.\n\n"
            "Для одной строки «a b c» в Pascal:\n"
            "writeln(a, ' ', b, ' ', c);"
        ),
        ("java", "pascal"): (
            "Похоже, вывод разбит на несколько writeln.\n\n"
            "Для одной строки в Pascal:\n"
            "writeln(a, ' ', b, ' ', c);"
        ),
        ("csharp", "pascal"): (
            "Похоже, вывод разбит на несколько writeln.\n\n"
            "Для одной строки в Pascal:\n"
            "writeln(a, ' ', b, ' ', c);"
        ),
    },
    "float_division_pascal": {
        ("python", "pascal"): (
            "Похоже, вы ожидали целый результат от / в Pascal.\n\n"
            "writeln(a / b)  → вещественное число\n"
            "writeln(a div b)  → целое частное"
        ),
    },
    "mod_negative": {
        ("python", "pascal"): (
            "Похоже, вы использовали % как в Python.\n\n"
            "Pascal: a mod b\n\n"
            "Для отрицательных a или b знак mod может быть другим, чем у % в Python."
        ),
    },
    "chain_comparison": {
        ("python", "pascal"): (
            "Похоже, вы написали цепочку сравнений как в Python:\n"
            "if 0 <= x <= 100 then\n\n"
            "Pascal:\n"
            "if (x >= 0) and (x <= 100) then"
        ),
    },
    "elif_chain": {
        ("python", "pascal"): (
            "Похоже, в коде Pascal остался elif из Python.\n\n"
            "Python:\n"
            "elif t <= 25:\n\n"
            "Pascal:\n"
            "else if t <= 25 then"
        ),
        ("python", "cpp"): (
            "Похоже, в коде C++ остался elif из Python.\n\n"
            "Python:\n"
            "elif t <= 25:\n\n"
            "C++:\n"
            "else if (t <= 25)"
        ),
        ("python", "csharp"): (
            "Похоже, в коде C# остался elif из Python.\n\n"
            "Python:\n"
            "elif t <= 25:\n\n"
            "C#:\n"
            "else if (t <= 25)"
        ),
        ("python", "java"): (
            "Похоже, в коде Java остался elif из Python.\n\n"
            "Python:\n"
            "elif t <= 25:\n\n"
            "Java:\n"
            "else if (t <= 25)"
        ),
    },
    "pascal_case_labels": {
        ("python", "pascal"): (
            "Похоже, сезон по месяцу записан идиомой Python.\n\n"
            "Python:\n"
            "if m in (12, 1, 2): print('winter')\n\n"
            "Pascal:\n"
            "case m of\n  12, 1, 2: writeln('winter');"
        ),
        ("python", "cpp"): (
            "Похоже, сезон записан через in (...) из Python.\n\n"
            "C++:\n"
            "case 12:\ncase 1:\ncase 2:\n  cout << \"winter\"; break;"
        ),
        ("python", "csharp"): (
            "Похоже, сезон записан через in (...) из Python.\n\n"
            "C#:\n"
            "case 12:\ncase 1:\ncase 2:\n  Console.WriteLine(\"winter\"); break;"
        ),
    },
    "leap_year_mod": {
        ("python", "pascal"): (
            "Похоже, правило високосного года или остаток перенесены неверно.\n\n"
            "Python:\n"
            "y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)\n\n"
            "Pascal:\n"
            "(y mod 400 = 0) or ((y mod 4 = 0) and (y mod 100 <> 0))"
        ),
        ("cpp", "pascal"): (
            "Похоже, в Pascal использован % вместо mod.\n\n"
            "Pascal:\n"
            "(y mod 400 = 0) or ((y mod 4 = 0) and (y mod 100 <> 0))"
        ),
    },
    "and_or_keywords": {
        ("python", "cpp"): (
            "Похоже, в условии использованы and/or из Python.\n\n"
            "C++:\n"
            "if (a && b)  — не if (a and b)"
        ),
    },
    "bool_literals": {
        ("python", "pascal"): (
            "Похоже, вы написали True или False как в Python.\n\n"
            "Pascal: true, false (нижний регистр)."
        ),
    },
    "string_immutable": {
        ("python", "java"): (
            "Похоже, вы изменяете символ строки по индексу как в Python.\n\n"
            "Java String неизменяем: используйте StringBuilder или char[]."
        ),
    },
    "list_vs_static_array": {
        ("python", "pascal"): (
            "Похоже, массив заполняется как list.append в Python.\n\n"
            "Pascal array[1..n] фиксированного размера:\n"
            "сначала readln(n), затем for i := 1 to n do readln(a[i])."
        ),
    },
    "exception_model": {
        ("python", "pascal"): (
            "Похоже, вы оставили try/except из Python.\n\n"
            "Pascal: Val(s, x, code); if code <> 0 then …\n"
            "или проверка IOResult после readln."
        ),
    },
    "pass_by_value_ref": {
        ("python", "pascal"): (
            "Похоже, процедура должна изменить параметр снаружи.\n\n"
            "Pascal: procedure P(var x: integer);\n"
            "Без var копия параметра не изменит переменную вызывающего."
        ),
    },
    "file_text_mode": {
        ("python", "pascal"): (
            "Похоже, вы использовали open/readline из Python.\n\n"
            "Pascal:\n"
            "Assign(f, 'f.txt'); Reset(f); Readln(f, line); Close(f);"
        ),
    },
    "switch_fallthrough": {
        ("python", "cpp"): (
            "Похоже, в switch пропущен break.\n\n"
            "C++ без break выполняет следующий case — добавьте break после каждого case."
        ),
    },
    "switch_vs_match": {
        ("python", "csharp"): (
            "Похоже, вы использовали match/case из Python 3.10+.\n\n"
            "C#: switch (x) { case 1: … break; }"
        ),
    },
    "scope_block": {
        ("python", "pascal"): (
            "Похоже, вы написали:\n"
            "return result;\n\n"
            "как в Python.\n\n"
            "В Pascal результат возвращается через имя функции:\n"
            "Power := result;"
        ),
    },
    "null_vs_nil": {
        ("python", "pascal"): (
            "Похоже, в коде есть None из Python.\n\n"
            "Pascal: nil для указателей или другое значение по типу задачи."
        ),
    },
    "overflow_fixed_int": {
        ("python", "pascal"): (
            "Похоже, значение не помещается в integer/longint Pascal.\n\n"
            "Python int не ограничен; проверьте диапазон входных данных."
        ),
    },
}

# ATCC carryover (source token found in target code) — keyed by concept
_ATCC_CARRYOVER: dict[str, dict[PairKey, str]] = {
    "counted_loop": {
        ("python", "pascal"): (
            "В коде Pascal найден range(...) из Python.\n\n"
            "Python: for i in range(n):\n"
            "Pascal: for i := 1 to n do\n\n"
            "range(n) — n шагов с 0; for i := 1 to n do — n шагов с 1."
        ),
    },
    "return_flow": {
        ("python", "pascal"): (
            "В коде Pascal найден return из Python.\n\n"
            "Python: return x;\n"
            "Pascal (функция F): F := x;"
        ),
    },
    "stdout_write": {
        ("python", "pascal"): (
            "В коде Pascal найден print(...) из Python.\n\n"
            "Замените на writeln(...);"
        ),
    },
    "stdin_read": {
        ("python", "pascal"): (
            "В коде Pascal найден input() из Python.\n\n"
            "Замените на readln(x); или Val для строки."
        ),
    },
    "assignment": {
        ("python", "pascal"): (
            "В коде Pascal найден elif из Python.\n\n"
            "Pascal: else if … then"
        ),
    },
}


def proactive_pitfall_message(
    pitfall_id: str | None,
    *,
    source_language: str,
    target_language: str,
) -> str | None:
    from application.curriculum.display.pitfall_proactive_warnings import (
        proactive_warning_for_pair,
    )

    pid = str(pitfall_id or "").strip()
    if not pid:
        return None
    text = proactive_warning_for_pair(
        pid,
        source_language=source_language,
        target_language=target_language,
    )
    return (
        _assert_concrete(text, pitfall_id=pid, kind="proactive")
        if text
        else None
    )


def reactive_pitfall_message(
    pitfall_id: str | None,
    *,
    source_language: str,
    target_language: str,
) -> str | None:
    pid = str(pitfall_id or "").strip()
    if not pid:
        return None
    text = _pick(_FEEDBACK.get(pid, {}), source_language, target_language)
    return _assert_concrete(text, pitfall_id=pid, kind="feedback") if text else None


def atcc_carryover_message(
    concept_id: str,
    *,
    source_language: str,
    target_language: str,
    fragment: str,
) -> str | None:
    text = _pick(_ATCC_CARRYOVER.get(concept_id, {}), source_language, target_language)
    if text:
        return _assert_concrete(text, pitfall_id=f"atcc:{concept_id}", kind="carryover")
    src = _lang_label(source_language)
    tgt = _lang_label(target_language)
    return (
        f"В коде {tgt} найдена конструкция {src}: {fragment}.\n"
        f"Замените её синтаксисом {tgt} для этой задачи."
    )


def contrast_note_message(
    pitfall_id: str | None,
    *,
    source_language: str,
    target_language: str,
) -> str | None:
    """Fallback pedagogy line — same concrete rules as proactive."""
    return proactive_pitfall_message(
        pitfall_id,
        source_language=source_language,
        target_language=target_language,
    )
