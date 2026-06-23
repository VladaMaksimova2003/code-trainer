"""Pascal Course v3.2 delta — new slots on top of v3.1.1 baseline."""

from __future__ import annotations

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

V32_DELTA_CORE_COUNT = 27

V32_DELTA_TASKS: list[TaskRow] = []


def _extend(chapter: str, rows: list[tuple]) -> None:
    for row in rows:
        padded = row + ("",) * (10 - len(row))
        V32_DELTA_TASKS.append((padded[0], chapter, *padded[1:9]))  # type: ignore[misc]


# 19. error_handling (+8)
_extend("error_handling", [
    ("exc_01", "try/except — перевод", "перевод_фрагмента", "translate", "tr_try_except",
     "Записать блок try/except для перехвата ошибок", "try; except", "easy"),
    ("exc_02", "Неверный тип в except", "исправление", "debug", "dbg_except_type",
     "Исправить тип исключения в except", "except", "easy"),
    ("exc_03", "try/finally — сборка", "сборка_фрагмента", "assemble", "asm_try_finally",
     "Собрать try/finally с освобождением ресурса", "try; finally", "medium"),
    ("exc_04", "raise и повторный raise", "исправление", "debug", "dbg_raise_reraise",
     "Исправить raise после перехвата исключения", "raise", "medium"),
    ("exc_05", "Пустой except — исправление", "исправление", "debug", "dbg_except_pass",
     "Заменить пустой except на осмысленную обработку", "except", "medium"),
    ("exc_06", "Своё исключение", "перевод_фрагмента", "translate", "tr_custom_exception",
     "Объявить и вызвать пользовательское исключение", "exception", "medium"),
    ("exc_07", "Файл не найден", "исправление", "debug", "dbg_file_not_found",
     "Добавить обработку ошибки открытия файла", "try; file", "medium"),
    ("exc_08", "Блок-схема → try/except", "код_по_блок-схеме", "implement", "flow_except_to_code",
     "Построить try/except по блок-схеме", "try; except", "medium"),
])

# expressions (+3)
_extend("expressions", [
    ("exp_09", "Приоритет операторов", "исправление", "debug", "dbg_precedence",
     "Исправить выражение с неверным приоритетом операторов", "precedence", "easy"),
    ("exp_10", "real → integer", "перевод_фрагмента", "translate", "tr_float_to_int",
     "Записать приведение real к integer через trunc/round", "trunc; real", "medium"),
    ("exp_11", "Сравнение вещественных", "исправление", "debug", "dbg_float_compare",
     "Исправить сравнение вещественных чисел", "real; compare", "medium"),
])

# pitfalls (+3)
_extend("pascal_pitfalls", [
    ("pit_05", "Условие и ноль", "исправление", "debug", "dbg_pit_truthiness",
     "Исправить условие, которое неверно обрабатывает ноль", "if; zero", "medium"),
    ("pit_06", "Общая ссылка на массив", "исправление", "debug", "dbg_pit_shared_ref",
     "Исправить присваивание, создающее две переменные на один dynamic array", "dynamic array", "medium"),
    ("pit_20", "Регистр идентификатора", "поиск_ошибки", "debug", "dbg_pit_identifier_case",
     "Найти обращение к идентификатору с неверным регистром", "identifier", "easy"),
])

# diagnostics (+2)
_extend("compiler_diagnostics", [
    ("cdg_08", "Неверный индекс массива", "исправление", "debug", "cdg_array_index",
     "Исправить индекс массива по сообщению компилятора", "array", "medium"),
    ("cdg_10", "Ожидался идентификатор", "исправление", "debug", "cdg_syntax_identifier",
     "Исправить синтаксическую ошибку «identifier expected»", "syntax", "easy"),
])

# Group C — Pascal-only (+12)
_extend("loops", [
    ("lop_16", "begin/end в теле цикла", "сборка_фрагмента", "assemble", "asm_loop_begin_end",
     "Собрать тело цикла с begin/end для нескольких операторов", "begin; end; for", "easy"),
])
_extend("functions", [
    ("fn_13", "begin/end в function", "сборка_фрагмента", "assemble", "asm_fn_begin_end",
     "Собрать function с begin/end в теле", "begin; end; function", "medium"),
])
_extend("dynamic_arrays", [
    ("dyn_12", "SetLength off-by-one", "исправление", "debug", "dbg_setlength_offbyone",
     "Исправить SetLength с неверной длиной массива", "setlength", "hard"),
])
_extend("units", [
    ("unt_14", "Циклические uses", "поиск_ошибки", "debug", "dbg_unit_circular_uses",
     "Найти циклическую зависимость unit", "uses", "hard"),
    ("unt_15", "Экспорт из interface", "сборка_фрагмента", "assemble", "asm_unit_export",
     "Собрать interface с экспортом процедуры", "interface; uses", "medium"),
])
_extend("procedures", [
    ("prc_14", "Forward procedure", "сборка_фрагмента", "assemble", "asm_forward_procedure",
     "Собрать forward и реализацию procedure", "forward", "hard"),
])
_extend("oop", [
    ("oop_19", "Property read-only", "перевод_фрагмента", "translate", "tr_property_readonly",
     "Записать property только для чтения", "property", "medium"),
    ("oop_20", "Property write-only", "исправление", "debug", "dbg_property_writeonly",
     "Исправить property только для записи", "property", "medium"),
    ("oop_21", "Property с индексом", "сборка_фрагмента", "assemble", "asm_property_indexed",
     "Собрать indexed property", "property", "hard"),
])
_extend("records", [
    ("rec_12", "Variant record — debug", "исправление", "debug", "dbg_variant_record",
     "Исправить доступ к variant record", "variant", "hard"),
])
_extend("files", [
    ("fil_09", "Eof и пустой файл", "исправление", "debug", "dbg_eof_edge",
     "Исправить чтение файла при Eof", "eof; file", "medium"),
])

V32_CHAPTER_TITLES = {
    "error_handling": "19. Обработка ошибок",
}
