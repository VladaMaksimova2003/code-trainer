"""v3.1 → v3.1.1 task swap log (same slot_ids, new content)."""
from __future__ import annotations

# slot_id -> {old_title, old_format, old_goal, problem, new_title, new_format, new_goal, new_pattern, new_features}
V311_SWAPS: dict[str, dict] = {
    "dyn_03": {
        "problem": "Дублирует dyn_06 — оба про выделение dynamic array через перевод",
        "old": ("Динамическая коллекция элементов", "перевод_фрагмента", "Перенести динамическую коллекцию"),
        "new": ("SetLength(n) vs SetLength(n+1)", "выбор_фрагмента", "Выбрать корректный SetLength для добавления", "mcq_setlength_append", "setlength"),
    },
    "dyn_06": {
        "problem": "Дублирует dyn_03; только перевод",
        "old": ("Выделение массива заданного размера", "перевод_фрагмента", "Записать SetLength для нового массива"),
        "new": ("Сборка начального SetLength", "сборка_фрагмента", "Собрать SetLength(a, 0) для пустого массива", "asm_setlength_init", "setlength"),
    },
    "dyn_10": {
        "problem": "Дублирует dyn_04 (append); оба — сборка append",
        "old": ("Соберите добавление в dynamic array", "сборка_фрагмента", "Собрать SetLength и запись в новый элемент"),
        "new": ("Индекс после SetLength(+1)", "исправление", "Исправить off-by-one при записи в новый элемент", "dbg_setlength_index", "setlength"),
    },
    "fn_07": {
        "problem": "Дублирует fn_02 (Result через перевод)",
        "old": ("Возврат значения из функции", "перевод_фрагмента", "Перенести return в Result"),
        "new": ("Сборка forward declaration", "сборка_фрагмента", "Собрать forward и заголовок function", "asm_forward_decl", "forward"),
    },
    "fn_11": {
        "problem": "Обобщённый перевод; слабое покрытие forward diagnostics",
        "old": ("Статическая функция", "перевод_фрагмента", "Перенести объявление функции верхнего уровня"),
        "new": ("Куда поместить forward", "выбор_фрагмента", "Выбрать корректное место forward-объявления", "mcq_forward_placement", "forward"),
    },
    "str_09": {
        "problem": "Дублирует str_01 (индекс строки через перевод)",
        "old": ("Доступ к символу по индексу", "перевод_фрагмента", "Записать s[i] для символа строки"),
        "new": ("Сборка цикла 1..Length(s)", "сборка_фрагмента", "Собрать for i := 1 to Length(s) do", "asm_string_loop", "string; length"),
    },
    "str_07": {
        "problem": "4 перевода подряд в разделе strings",
        "old": ("Цикл по символам строки", "перевод_фрагмента", "Записать for i := 1 to Length(s)"),
        "new": ("Copy и конкатенация — сборка", "сборка_фрагмента", "Собрать Copy(s,i,n) и Concat", "asm_string_copy_concat", "copy; concat"),
    },
    "rec_04": {
        "problem": "Дублирует rec_01 (record через перевод)",
        "old": ("Структура с именованными полями", "перевод_фрагмента", "Перенести struct-подобный тип в record"),
        "new": ("Разыменование p^ — ошибка", "исправление", "Исправить доступ через указатель p^", "dbg_ptr_deref", "^; pointer"),
    },
    "rec_06": {
        "problem": "Единственная задача на указатели — только перевод",
        "old": ("Указатель ^ на record", "перевод_фрагмента", "Использовать New/Dispose для record"),
        "new": ("Сборка New/Dispose", "сборка_фрагмента", "Собрать New(p), p^ и Dispose", "asm_new_dispose", "new; dispose; ^"),
    },
    "oop_03": {
        "problem": "destructor — только перевод, нет inherited Destroy",
        "old": ("destructor Destroy", "перевод_фрагмента", "Записать destructor Destroy"),
        "new": ("Сборка destructor Destroy", "сборка_фрагмента", "Собрать destructor с inherited Destroy", "asm_destructor", "destructor; inherited"),
    },
    "oop_06": {
        "problem": "abstract — перевод; нужна active virtual/override",
        "old": ("abstract class", "перевод_фрагмента", "Объявить abstract class"),
        "new": ("Сборка virtual и override", "сборка_фрагмента", "Собрать virtual метод и override в потомке", "asm_virtual_override", "virtual; override"),
    },
    "oop_08": {
        "problem": "Self — перевод в блоке из 4 переводов подряд",
        "old": ("Ссылка на текущий объект (Self)", "перевод_фрагмента", "Записать Self в методе"),
        "new": ("Property: read/write поле", "исправление", "Исправить property и backing field", "dbg_property_field", "property"),
    },
    "oop_15": {
        "problem": "Наследование — перевод без inherited",
        "old": ("Наследование class(TBase)", "перевод_фрагмента", "Записать наследование class(TBase)"),
        "new": ("inherited в override", "исправление", "Добавить inherited в переопределённый метод", "dbg_inherited_override", "inherited; override"),
    },
    "oop_05": {
        "problem": "virtual/override — перевод при наличии oop_06 assemble",
        "old": ("virtual / override", "перевод_фрагмента", "Записать virtual и override"),
        "new": ("override без virtual — исправление", "исправление", "Добавить virtual перед override", "dbg_virtual_before_override", "virtual; override"),
    },
    "oop_11": {
        "problem": "Дублирует pit_14 и oop_05",
        "old": ("override без virtual", "поиск_ошибки", "Найти override без virtual"),
        "new": ("Incompatible types (class)", "поиск_ошибки", "Найти несовместимость типов class при присваивании", "dbg_class_type_mismatch", "class"),
    },
    "exp_04": {
        "problem": "set of/in — единственная задача, только перевод",
        "old": ("Проверка in для множества", "перевод_фрагмента", "Использовать set of и in"),
        "new": ("Сборка set of и in", "сборка_фрагмента", "Собрать set of char и проверку ch in S", "asm_set_of_in", "set of; in"),
    },
    "exp_05": {
        "problem": "4 перевода подряд в expressions",
        "old": ("Логические операторы and/or", "перевод_фрагмента", "Записать составное логическое условие"),
        "new": ("Short-circuit and/or", "выбор_фрагмента", "Выбрать корректное поведение and/or в Pascal", "mcq_short_circuit", "and; or"),
    },
    "fil_02": {
        "problem": "Запись TextFile — только перевод",
        "old": ("Запись TextFile", "перевод_фрагмента", "Записать Rewrite/WriteLn"),
        "new": ("Сборка записи TextFile", "сборка_фрагмента", "Собрать Assign/Rewrite/WriteLn/CloseFile", "asm_textfile_write", "textfile; rewrite"),
    },
    "unt_05": {
        "problem": "initialization — только перевод",
        "old": ("initialization/finalization", "перевод_фрагмента", "Записать initialization/finalization"),
        "new": ("initialization/finalization — порядок", "исправление", "Исправить порядок initialization и finalization", "dbg_unit_init_order", "initialization; finalization"),
    },
    "unt_07": {
        "problem": "Модуль — перевод без interface/implementation",
        "old": ("Пространство имён / модуль", "перевод_фрагмента", "Перенести модуль в unit"),
        "new": ("interface vs implementation", "выбор_фрагмента", "Выбрать секцию unit для объявления и реализации", "mcq_interface_impl", "interface; implementation"),
    },
    "lop_03": {
        "problem": "downto — только перевод",
        "old": ("Цикл for … downto … do", "перевод_фрагмента", "Записать обратный for downto"),
        "new": ("Сборка for … downto … do", "сборка_фрагмента", "Собрать заголовок и тело for downto", "asm_for_downto", "for downto"),
    },
    "rcu_01": {
        "problem": "Рекурсия — перевод program",
        "old": ("Рекурсивная function", "перевод_программы", "Перенести рекурсивную function"),
        "new": ("Сборка рекурсивной function", "сборка_программы", "Собрать program с рекурсивной function", "asm_recursive_program", "function; recursion"),
    },
    "cdg_10": {
        "problem": "Дублирует cnd_13 и pit_01 (; перед else)",
        "old": ("';' expected before ELSE", "исправление", "Убрать ; перед else"),
        "new": ("Forward declaration not solved", "выбор_фрагмента", "Выбрать исправление для unresolved forward", "cdg_forward_unsolved", "forward"),
    },
    "cdg_09": {
        "problem": "String/Integer — близко к cdg_02; заменить на class diagnostic",
        "old": ("Incompatible types String/Integer", "исправление", "Исправить смешение string и integer"),
        "new": ("Incompatible types (class)", "исправление", "Исправить присваивание несовместимых class-типов", "cdg_class_incompatible", "class"),
    },
    "cdg_12": {
        "problem": "Overloaded procedure — слабая связь с Pascal transfer; нужен override diagnostic",
        "old": ("Overloaded procedure mismatch", "поиск_ошибки", "Найти несовпадение перегруженной procedure"),
        "new": ("Virtual method must be marked override", "поиск_ошибки", "Найти override без virtual или неверную сигнатуру", "cdg_virtual_override", "virtual; override"),
    },
    "pit_02": {
        "problem": "Дублирует typ_02 (:= vs =)",
        "old": ("Присваивание := vs =", "исправление", "Заменить = на :="),
        "new": ("nil перед разыменованием", "исправление", "Исправить разыменование nil-указателя", "dbg_pit_nil_ptr", "nil; ^"),
    },
    "pit_14": {
        "problem": "Дублирует oop_05/oop_11 (override без virtual)",
        "old": ("override без virtual", "исправление", "Добавить virtual перед override"),
        "new": ("Dispose без New", "поиск_ошибки", "Найти Dispose без предшествующего New", "dbg_pit_dispose_new", "new; dispose"),
    },
    "pit_11": {
        "problem": "Monotony: 4× исправление подряд в pascal_pitfalls",
        "old": ("end vs end.", "исправление", "Добавить точку после end программы"),
        "new": ("end vs end. — выбор", "выбор_фрагмента", "Выбрать корректное завершение program", "mcq_pit_end_dot", "end."),
    },
    "pit_12": {
        "problem": "Monotony: 4× исправление подряд в pascal_pitfalls",
        "old": ("begin/end в одной ветке if", "исправление", "Добавить begin/end в ветку if"),
        "new": ("begin/end в ветке if — сборка", "сборка_фрагмента", "Собрать if then begin … end", "asm_pit_if_begin", "begin/end"),
    },
    "cdg_11": {
        "problem": "Result undeclared — оставить без изменений",
        "old": None,
        "new": None,
    },
    "dyn_08": {
        "problem": "Copy dynamic — перевод, слабая активность",
        "old": ("Copy для dynamic array", "перевод_фрагмента", "Скопировать dynamic array"),
        "new": ("Сборка Copy dynamic array", "сборка_фрагмента", "Собрать b := Copy(a, i, count)", "asm_dyn_copy", "copy"),
    },
    "rcu_06": {
        "problem": "forward mutual — перевод",
        "old": ("Взаимная рекурсия (forward)", "перевод_фрагмента", "Записать взаимные forward-объявления"),
        "new": ("Forward: ошибка компиляции", "поиск_ошибки", "Найти forward без implementation", "dbg_forward_unimplemented", "forward"),
    },
    "cdg_16": {
        "problem": "Generic type mismatch MCQ — заменить на Property not found",
        "old": ("Выбор исправления: Type mismatch", "выбор_фрагмента", "Выбрать исправление по диагностике"),
        "new": ("Property not found", "выбор_фрагмента", "Выбрать исправление для Property not found", "cdg_property_not_found", "property"),
    },
    "oop_16": {
        "problem": "Метод Self — перевод в oop блоке",
        "old": ("Метод с Self", "перевод_фрагмента", "Перенести метод экземпляра"),
        "new": ("Сборка метода с Self", "сборка_фрагмента", "Собрать method с Self и полем класса", "asm_method_self", "self; class"),
    },
    "oop_07": {
        "problem": "Property — перевод при наличии oop_18 assemble",
        "old": ("Свойство объекта", "перевод_фрагмента", "Записать property read/write"),
        "new": ("Property read/write — типичная ошибка", "поиск_ошибки", "Найти property без корректного read/write", "dbg_property_read_write", "property"),
    },
}

# Remove entries with no swap
V311_SWAPS = {k: v for k, v in V311_SWAPS.items() if v.get("old") is not None}
