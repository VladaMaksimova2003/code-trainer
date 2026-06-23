"""Stage 3 expansion task payloads task_145–task_192 (chapters 5–16, P2)."""

from __future__ import annotations

from typing import Any

from algo_v192_plan import V128_CHAPTER_KEYS, expansion_task_nums_for_chapter
from v128_test_matrix import tc

_IMPLEMENT_SLOTS: frozenset[int] = frozenset(
    {148, 152, 156, 160, 164, 168, 172, 176, 180, 184, 188, 192}
)

_CHAPTER_BY_NUM: dict[int, str] = {
    n: key
    for key in V128_CHAPTER_KEYS
    for n in expansion_task_nums_for_chapter(key)
}

_ACTION_BY_NUM: dict[int, str] = {
    145: "assemble",
    146: "assemble",
    147: "debug",
    148: "implement",
    149: "assemble",
    150: "assemble",
    151: "debug",
    152: "implement",
    153: "assemble",
    154: "assemble",
    155: "debug",
    156: "implement",
    157: "assemble",
    158: "assemble",
    159: "debug",
    160: "implement",
    161: "assemble",
    162: "assemble",
    163: "debug",
    164: "implement",
    165: "assemble",
    166: "assemble",
    167: "debug",
    168: "implement",
    169: "assemble",
    170: "assemble",
    171: "debug",
    172: "implement",
    173: "assemble",
    174: "assemble",
    175: "debug",
    176: "implement",
    177: "assemble",
    178: "assemble",
    179: "debug",
    180: "implement",
    181: "assemble",
    182: "assemble",
    183: "debug",
    184: "implement",
    185: "assemble",
    186: "assemble",
    187: "debug",
    188: "implement",
    189: "assemble",
    190: "assemble",
    191: "debug",
    192: "implement",
}

_PITFALL_BY_NUM: dict[int, str] = {
    147: "index_1based",
    151: "scope_block",
    155: "for_range_off_by_one",
    159: "index_1based",
    163: "round_semantics",
    171: "file_text_mode",
    183: "index_1based",
    187: "exception_model",
}

_TITLES: dict[int, str] = {
    145: "Подсчёт гласных",
    146: "Шифр Caesar (+k)",
    147: "Первое вхождение символа",
    148: "Самое длинное слово",
    149: "Функция is_even",
    150: "Функция lcm через gcd",
    151: "Факториал (return)",
    152: "Массив отсортирован?",
    153: "x^n рекурсивно",
    154: "Сумма 1..n рекурсией",
    155: "Факториал (базовый случай)",
    156: "Башни Ханоя — число ходов",
    157: "Сортировка подсчётом (0..9)",
    158: "Бинарный поиск — последнее вхождение",
    159: "Bubble sort (индекс)",
    160: "Слияние двух отсортированных массивов",
    161: "Мода массива",
    162: "Произведение элементов",
    163: "Среднее с округлением",
    164: "Элементы выше среднего",
    165: "Two sum (индексы пары)",
    166: "Первый неповторяющийся символ",
    167: "Частота id (ключ)",
    168: "Группировка анаграмм",
    169: "Максимум чисел из файла",
    170: "Подсчёт слов в файле",
    171: "CSV: чтение файла",
    172: "Фильтр чётных в output.txt",
    173: "Вычисление RPN",
    174: "Очередь: симуляция кассы",
    175: "Проверка скобок (пустой стек)",
    176: "BFS: кратчайший путь",
    177: "Длина односвязного списка",
    178: "Вставка в начало списка",
    179: "Удаление по значению",
    180: "Сортировка списка вставками",
    181: "Число вершин дерева",
    182: "Inorder обход (фрагмент)",
    183: "DFS: индексация вершин",
    184: "Компоненты связности",
    185: "Класс Counter",
    186: "Класс Stack на массиве",
    187: "BankAccount: withdraw",
    188: "Student: лучший средний балл",
    189: "Shape → Circle/Rectangle",
    190: "Employee → Manager",
    191: "Полиморфизм speak (virtual)",
    192: "Итог: система доставки",
}

_GOALS: dict[int, str] = {
    145: "Дана строка s. Выведите количество гласных (aeiouAEIOU).",
    146: "Даны строка s и целое k. Выведите Caesar-шифр (+k) для латинских букв.",
    147: "Даны строка s и символ c. Выведите 0-based индекс первого вхождения или -1.",
    148: "Дана строка из слов. Выведите самое длинное слово (при равенстве — первое).",
    149: "Дано n. Выведите yes, если n чётное, иначе no.",
    150: "Даны a и b. Выведите НОК(a, b).",
    151: "Дано n. Выведите n! с помощью рекурсивной функции.",
    152: "Дано n и n чисел. Выведите yes, если массив неубывающий, иначе no.",
    153: "Даны x и n. Рекурсивно выведите x^n.",
    154: "Дано n. Рекурсивно выведите сумму 1 + 2 + … + n.",
    155: "Дано n. Рекурсивно выведите n!.",
    156: "Дано n. Выведите минимальное число ходов для Башен Ханоя (2^n − 1).",
    157: "Дано n и n чисел 0..9. Выведите их в отсортированном порядке (сортировка подсчётом).",
    158: "Даны n, отсортированный массив и x. Выведите индекс последнего вхождения x или -1.",
    159: "Дано n и n чисел. Отсортируйте bubble sort и выведите элементы.",
    160: "Даны n, массив A, m, массив B (оба отсортированы). Выведите слияние.",
    161: "Дано n и n чисел. Выведите моду (самое частое; при равенстве — минимальное).",
    162: "Дано n и n чисел. Выведите произведение всех элементов.",
    163: "Дано n и n чисел. Выведите round(среднее).",
    164: "Дано n и n чисел. Выведите элементы строго больше среднего через пробел.",
    165: "Даны n, target и n чисел. Выведите два 0-based индекса пары с суммой target.",
    166: "Дана строка s. Выведите первый символ, встречающийся один раз, или _.",
    167: "Дано n id и запрос id. Выведите частоту id (0, если не встречался).",
    168: "Дано n слов. Выведите число групп анаграмм.",
    169: "Даны числа (по одному в строке до EOF). Выведите максимум.",
    170: "Дан текст (строки до EOF). Выведите число слов.",
    171: "Даны строки CSV name,value. Выведите сумму value.",
    172: "Дано n и n чисел. Выведите чётные через пробел.",
    173: "Дана строка RPN (числа и + - * /). Выведите результат.",
    174: "Дано n и n времен обслуживания. Выведите суммарное время ожидания в очереди.",
    175: "Дана строка скобок ()[]{}. Выведите yes, если корректна, иначе no.",
    176: "Даны n, m и m рёбер неориентированного графа. Выведите кратчайший путь 0→n−1 или -1.",
    177: "Дано n и n чисел списка. Выведите длину списка.",
    178: "Дано n, n чисел и x. Выведите список после вставки x в начало.",
    179: "Дано n, n чисел и v. Выведите список после удаления первого вхождения v.",
    180: "Дано n и n чисел. Отсортируйте insertion sort и выведите элементы.",
    181: "Дано n и n−1 рёбер дерева. Выведите число вершин.",
    182: "Дано n и n значений (0 — пусто) в куче. Выведите inorder обход.",
    183: "Даны n, m и m рёбер. DFS из 0: выведите порядок посещения вершин (0-based).",
    184: "Даны n, m и m рёбер. Выведите число компонент связности.",
    185: "Даны команды Counter: inc/dec/get. Выведите ответы get.",
    186: "Даны команды push/pop/top. Выведите ответы top (empty если пуст).",
    187: "Даны deposit и withdraw. Выведите баланс (не ниже 0).",
    188: "Дано n студентов (имя и 3 оценки). Выведите имя с лучшим средним.",
    189: "Даны фигуры circle r / rect w h. Выведите площади.",
    190: "Даны employee salary и manager bonus. Выведите итоговые зарплаты.",
    191: "Даны Dog/Cat speak. Выведите звуки через полиморфный вызов.",
    192: "Даны заказы (id weight). Выведите суммарный вес доставленных (weight≤10).",
}

_TESTS: dict[int, list[dict[str, str]]] = {
    145: [
        tc("typical", "hello\n", "2", input_kind="string"),
        tc("single", "a\n", "1", input_kind="string"),
        tc("zero_empty", "xyz\n", "0", input_kind="string"),
        tc("boundary", "7\n", "0", input_kind="scalar"),
    ],
    146: [
        tc("typical", "abc 3\n", "def", input_kind="string"),
        tc("boundary", "xyz 0\n", "xyz", input_kind="string"),
        tc("typical", "AbZ 1\n", "BcA", input_kind="string"),
        tc("single", "a 25\n", "z", input_kind="scalar"),
    ],
    147: [
        tc("typical", "hello\nl\n", "2", input_kind="string"),
        tc("not_found", "abc\nz\n", "-1", input_kind="string"),
        tc("single", "a\na\n", "0", input_kind="string"),
        tc("boundary", "ab\nb\n", "1", input_kind="scalar"),
    ],
    148: [
        tc("typical", "one two three\n", "three", input_kind="string"),
        tc("single", "word\n", "word", input_kind="string"),
        tc("duplicate", "aa aaa aa\n", "aaa", input_kind="scalar"),
        tc("typical", "hi there friend\n", "friend", input_kind="string"),
        tc("boundary", "a bb ccc bb\n", "ccc", input_kind="string"),
    ],
    149: [
        tc("typical", "4\n", "yes", input_kind="scalar"),
        tc("typical", "7\n", "no", input_kind="scalar"),
        tc("zero_empty", "0\n", "yes", input_kind="scalar"),
        tc("boundary", "1\n8\n", "no", input_kind="array"),
    ],
    150: [
        tc("typical", "12 8\n", "24", input_kind="scalar"),
        tc("single", "7 7\n", "7", input_kind="scalar"),
        tc("typical", "4 6\n", "12", input_kind="scalar"),
        tc("boundary", "1 1\n", "1", input_kind="pairs"),
    ],
    151: [
        tc("typical", "5\n", "120", input_kind="scalar"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "0\n", "1", input_kind="scalar"),
        tc("boundary", "1\n5\n", "1", input_kind="array"),
    ],
    152: [
        tc("typical", "4\n1\n2\n3\n4\n", "yes", input_kind="array"),
        tc("typical", "3\n1\n3\n2\n", "no", input_kind="array"),
        tc("single", "1\n5\n", "yes", input_kind="array"),
        tc("all_equal", "3\n2\n2\n2\n", "yes", input_kind="array"),
        tc("boundary", "2\n1\n2\n", "yes", input_kind="pairs"),
    ],
    153: [
        tc("typical", "2 10\n", "1024", input_kind="scalar"),
        tc("single", "5 0\n", "1", input_kind="scalar"),
        tc("boundary", "3 1\n", "3", input_kind="scalar"),
        tc("typical", "2 3\n", "8", input_kind="pairs"),
    ],
    154: [
        tc("typical", "5\n", "15", input_kind="scalar"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "0\n", "0", input_kind="scalar"),
        tc("boundary", "1\n10\n", "1", input_kind="array"),
    ],
    155: [
        tc("typical", "5\n", "120", input_kind="scalar"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "0\n", "1", input_kind="scalar"),
        tc("boundary", "1\n5\n", "1", input_kind="array"),
    ],
    156: [
        tc("typical", "3\n", "7", input_kind="scalar"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "0\n", "0", input_kind="scalar"),
        tc("boundary", "1\n5\n", "1", input_kind="array"),
        tc("typical", "10\n", "1023", input_kind="scalar"),
    ],
    157: [
        tc("typical", "5\n2\n0\n2\n1\n0\n", "0 0 1 2 2", input_kind="array"),
        tc("single", "1\n9\n", "9", input_kind="array"),
        tc("all_equal", "3\n1\n1\n1\n", "1 1 1", input_kind="array"),
        tc("zero_empty", "0\n", "", input_kind="scalar"),
    ],
    158: [
        tc("typical", "6\n1\n2\n2\n2\n3\n4\n2\n", "3", input_kind="array"),
        tc("not_found", "3\n1\n2\n3\n5\n", "-1", input_kind="array"),
        tc("single", "1\n5\n5\n", "0", input_kind="array"),
        tc("duplicate", "4\n2\n2\n2\n2\n2\n", "3", input_kind="scalar"),
    ],
    159: [
        tc("typical", "4\n3\n1\n4\n2\n", "1 2 3 4", input_kind="array"),
        tc("single", "1\n7\n", "7", input_kind="array"),
        tc("all_equal", "3\n5\n5\n5\n", "5 5 5", input_kind="array"),
        tc("negative", "3\n-1\n-3\n-2\n", "-3 -2 -1", input_kind="scalar"),
    ],
    160: [
        tc("typical", "2\n1\n3\n3\n2\n4\n5\n", "1 2 3 4 5", input_kind="array"),
        tc("zero_empty", "0\n3\n1\n2\n3\n", "1 2 3", input_kind="array"),
        tc("single", "1\n1\n0\n", "1", input_kind="array"),
        tc("typical", "1\n5\n1\n10\n", "5 10", input_kind="scalar"),
        tc("duplicate", "3\n1\n1\n1\n3\n2\n2\n2\n", "1 1 1 2 2 2", input_kind="array"),
    ],
    161: [
        tc("typical", "5\n1\n2\n2\n3\n2\n", "2", input_kind="array"),
        tc("single", "1\n7\n", "7", input_kind="array"),
        tc("duplicate", "4\n1\n1\n2\n2\n", "1", input_kind="array"),
        tc("negative", "3\n-1\n-1\n2\n", "-1", input_kind="scalar"),
    ],
    162: [
        tc("typical", "3\n2\n3\n4\n", "24", input_kind="array"),
        tc("single", "1\n5\n", "5", input_kind="array"),
        tc("zero_empty", "3\n1\n0\n5\n", "0", input_kind="array"),
        tc("negative", "2\n-2\n3\n", "-6", input_kind="scalar"),
    ],
    163: [
        tc("typical", "3\n1\n2\n2\n", "2", input_kind="array"),
        tc("single", "1\n5\n", "5", input_kind="array"),
        tc("boundary", "2\n1\n2\n", "2", input_kind="array"),
        tc("negative", "3\n-1\n0\n1\n", "0", input_kind="scalar"),
    ],
    164: [
        tc("typical", "4\n1\n2\n3\n4\n", "3 4", input_kind="array"),
        tc("single", "1\n5\n", "", input_kind="array"),
        tc("all_equal", "3\n2\n2\n2\n", "", input_kind="array"),
        tc("negative", "3\n-5\n0\n5\n", "5", input_kind="array"),
        tc("zero_empty", "3\n0\n0\n0\n", "", input_kind="scalar"),
    ],
    165: [
        tc("typical", "4 9\n2\n7\n11\n15\n", "0 1", input_kind="array"),
        tc("single", "2 3\n1\n2\n", "0 1", input_kind="array"),
        tc("typical", "3 6\n3\n3\n4\n", "0 1", input_kind="pairs"),
        tc("not_found", "2 100\n1\n2\n", "0 0", input_kind="pairs"),
    ],
    166: [
        tc("typical", "swiss\n", "w", input_kind="string"),
        tc("not_found", "aabb\n", "_", input_kind="string"),
        tc("single", "z\n", "z", input_kind="string"),
        tc("boundary", "z\n", "z", input_kind="scalar"),
    ],
    167: [
        tc("typical", "3\na\nb\na\na\n", "2", input_kind="string"),
        tc("not_found", "2\nx\ny\nz\n", "0", input_kind="string"),
        tc("single", "1\nk\nk\n", "1", input_kind="string"),
        tc("zero_empty", "0\nq\n", "0", input_kind="array"),
    ],
    168: [
        tc("typical", "3\neat\ntea\nate\n", "1", input_kind="array"),
        tc("typical", "4\nbat\ntab\nabt\nxyz\n", "2", input_kind="array"),
        tc("single", "1\na\n", "1", input_kind="array"),
        tc("duplicate", "2\nab\nba\n", "1", input_kind="array"),
        tc("zero_empty", "0\n", "0", input_kind="scalar"),
    ],
    169: [
        tc("typical", "1\n5\n2\n", "5", input_kind="array"),
        tc("single", "10\n", "10", input_kind="scalar"),
        tc("negative", "-1\n-5\n-2\n", "-1", input_kind="array"),
        tc("typical", "1\n2\n3\n", "3", input_kind="file_sim"),
    ],
    170: [
        tc("typical", "one two three\n", "3", input_kind="string"),
        tc("single", "word\n", "1", input_kind="string"),
        tc("zero_empty", "\n", "0", input_kind="string"),
        tc("typical", "hello world\n", "2", input_kind="file_sim"),
    ],
    171: [
        tc("typical", "a,10\nb,20\n", "30", input_kind="string"),
        tc("single", "x,7\n", "7", input_kind="string"),
        tc("zero_empty", "z,0\n", "0", input_kind="string"),
        tc("typical", "p,3\nq,4\n", "7", input_kind="file_sim"),
    ],
    172: [
        tc("typical", "4\n1\n2\n3\n4\n", "2 4", input_kind="array"),
        tc("single", "1\n3\n", "", input_kind="array"),
        tc("zero_empty", "2\n0\n0\n", "0 0", input_kind="array"),
        tc("negative", "3\n-2\n1\n3\n", "-2", input_kind="scalar"),
        tc("all_equal", "3\n2\n2\n2\n", "2 2 2", input_kind="array"),
    ],
    173: [
        tc("typical", "2 3 + 5 *\n", "25", input_kind="string"),
        tc("single", "7\n", "7", input_kind="string"),
        tc("typical", "4 13 5 /\n", "2", input_kind="commands"),
        tc("boundary", "6 2 /\n", "3", input_kind="commands"),
    ],
    174: [
        tc("typical", "3\n3\n2\n4\n", "8", input_kind="array"),
        tc("single", "1\n5\n", "0", input_kind="array"),
        tc("zero_empty", "2\n1\n1\n", "1", input_kind="array"),
        tc("typical", "4\n1\n2\n3\n4\n", "10", input_kind="commands"),
    ],
    175: [
        tc("typical", "([])\n", "yes", input_kind="string"),
        tc("invalid", "([)]\n", "no", input_kind="string"),
        tc("zero_empty", "\n", "yes", input_kind="string"),
        tc("single", "()\n", "yes", input_kind="commands"),
    ],
    176: [
        tc("typical", "4 4\n0 1\n1 2\n0 3\n3 2\n", "1", input_kind="graph"),
        tc("not_found", "4 1\n0 1\n2 3\n", "-1", input_kind="graph"),
        tc("single", "1 0\n", "0", input_kind="graph"),
        tc("boundary", "2 1\n0 1\n", "1", input_kind="graph"),
        tc("typical", "5 4\n0 1\n1 2\n2 3\n3 4\n", "4", input_kind="scalar"),
    ],
    177: [
        tc("typical", "4\n1\n2\n3\n4\n", "4", input_kind="array"),
        tc("single", "1\n7\n", "1", input_kind="array"),
        tc("zero_empty", "0\n", "0", input_kind="array"),
        tc("typical", "3\n5\n5\n5\n", "3", input_kind="commands"),
    ],
    178: [
        tc("typical", "3\n1\n2\n3\n0\n", "0 1 2 3", input_kind="array"),
        tc("single", "1\n5\n9\n", "9 5", input_kind="array"),
        tc("zero_empty", "0\n7\n", "7", input_kind="array"),
        tc("typical", "2\n4\n8\n1\n", "1 4 8", input_kind="commands"),
    ],
    179: [
        tc("typical", "3\n1\n2\n3\n2\n", "1 3", input_kind="array"),
        tc("single", "1\n5\n5\n", "", input_kind="array"),
        tc("not_found", "3\n1\n2\n3\n9\n", "1 2 3", input_kind="array"),
        tc("typical", "3\n2\n2\n2\n2\n", "2 2", input_kind="commands"),
    ],
    180: [
        tc("typical", "4\n3\n1\n4\n2\n", "1 2 3 4", input_kind="array"),
        tc("single", "1\n7\n", "7", input_kind="array"),
        tc("all_equal", "3\n2\n2\n2\n", "2 2 2", input_kind="array"),
        tc("negative", "3\n-1\n-3\n-2\n", "-3 -2 -1", input_kind="array"),
        tc("zero_empty", "1\n0\n", "0", input_kind="scalar"),
    ],
    181: [
        tc("typical", "4\n0 1\n0 2\n1 3\n", "4", input_kind="graph"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "2\n0 1\n", "2", input_kind="graph"),
        tc("typical", "5\n0 1\n0 2\n0 3\n1 4\n", "5", input_kind="commands"),
    ],
    182: [
        tc("typical", "5\n1\n2\n3\n0\n0\n", "2 1 3", input_kind="array"),
        tc("single", "1\n5\n", "5", input_kind="array"),
        tc("zero_empty", "3\n0\n0\n0\n", "", input_kind="array"),
        tc("typical", "7\n4\n2\n6\n0\n0\n0\n0\n", "2 4 6", input_kind="commands"),
    ],
    183: [
        tc("typical", "4 3\n0 1\n0 2\n1 3\n", "0 1 3 2", input_kind="graph"),
        tc("single", "1 0\n", "0", input_kind="graph"),
        tc("typical", "3 2\n0 1\n0 2\n", "0 1 2", input_kind="graph"),
        tc("boundary", "2 1\n1 0\n", "0 1", input_kind="commands"),
    ],
    184: [
        tc("typical", "4 2\n0 1\n2 3\n", "2", input_kind="graph"),
        tc("single", "1 0\n", "1", input_kind="graph"),
        tc("zero_empty", "3 0\n", "3", input_kind="graph"),
        tc("typical", "5 3\n0 1\n1 2\n3 4\n", "2", input_kind="graph"),
        tc("zero_empty", "6 0\n", "6", input_kind="scalar"),
    ],
    185: [
        tc("typical", "3\ninc\nget\ninc\n", "1", input_kind="commands"),
        tc("single", "1\nget\n", "0", input_kind="commands"),
        tc("typical", "4\ndec\nget\ninc\nget\n", "0 1", input_kind="commands"),
        tc("zero_empty", "2\ninc\nget\n", "1", input_kind="scalar"),
    ],
    186: [
        tc("typical", "3\npush 1\npush 2\ntop\n", "2", input_kind="commands"),
        tc("single", "2\npush 5\npop\n", "5", input_kind="commands"),
        tc("zero_empty", "1\ntop\n", "empty", input_kind="commands"),
        tc("typical", "4\npush 3\npush 4\npop\ntop\n", "4 3", input_kind="scalar"),
    ],
    187: [
        tc("typical", "100 30\n", "70", input_kind="scalar"),
        tc("boundary", "50 50\n", "0", input_kind="scalar"),
        tc("invalid", "10 20\n", "0", input_kind="scalar"),
        tc("typical", "200 50 30\n", "120", input_kind="commands"),
    ],
    188: [
        tc("typical", "2\nAnn 5 5 5\nBob 4 4 4\n", "Ann", input_kind="array"),
        tc("single", "1\nZed 3 3 3\n", "Zed", input_kind="array"),
        tc("duplicate", "2\nA 2 2 5\nB 3 3 3\n", "A", input_kind="array"),
        tc("typical", "3\nX 1 1 1\nY 2 2 2\nZ 3 3 3\n", "Z", input_kind="pairs"),
        tc("negative", "2\nM -1 5 5\nN 0 0 0\n", "M", input_kind="pairs"),
    ],
    189: [
        tc("typical", "2\ncircle 3\nrect 4 5\n", "28.27 20.00", input_kind="commands"),
        tc("single", "1\ncircle 1\n", "3.14", input_kind="commands"),
        tc("zero_empty", "1\nrect 0 10\n", "0.00", input_kind="commands"),
        tc("typical", "1\nrect 2 2\n", "4.00", input_kind="scalar"),
    ],
    190: [
        tc("typical", "2\nemployee 1000\nmanager 1000 500\n", "1000 1500", input_kind="commands"),
        tc("single", "1\nemployee 800\n", "800", input_kind="commands"),
        tc("zero_empty", "1\nmanager 1000 0\n", "1000", input_kind="commands"),
        tc("typical", "2\nemployee 500\nemployee 700\n", "500 700", input_kind="scalar"),
    ],
    191: [
        tc("typical", "2\nDog\nCat\n", "woof meow", input_kind="commands"),
        tc("single", "1\nDog\n", "woof", input_kind="commands"),
        tc("zero_empty", "0\n", "", input_kind="commands"),
        tc("typical", "3\nCat\nDog\nCat\n", "meow woof meow", input_kind="string"),
    ],
    192: [
        tc("typical", "3\n1 5\n2 12\n3 8\n", "13", input_kind="pairs"),
        tc("single", "1\n1 3\n", "3", input_kind="pairs"),
        tc("zero_empty", "0\n", "0", input_kind="scalar"),
        tc("boundary", "2\n1 10\n2 10\n", "20", input_kind="pairs"),
        tc("invalid", "2\n1 11\n2 5\n", "5", input_kind="pairs"),
    ],
}

_PYTHON_REF: dict[int, str] = {
    145: (
        "s = input().strip()\n"
        "vowels = 'aeiouAEIOU'\n"
        "print(sum(1 for c in s if c in vowels))"
    ),
    146: (
        "s, k = input().split()\n"
        "k = int(k) % 26\n"
        "out = []\n"
        "for c in s:\n"
        "    if 'a' <= c <= 'z':\n"
        "        out.append(chr((ord(c) - ord('a') + k) % 26 + ord('a')))\n"
        "    elif 'A' <= c <= 'Z':\n"
        "        out.append(chr((ord(c) - ord('A') + k) % 26 + ord('A')))\n"
        "    else:\n"
        "        out.append(c)\n"
        "print(''.join(out))"
    ),
    147: "s = input().strip()\nc = input().strip()\nprint(s.find(c))",
    148: "words = input().split()\nprint(max(words, key=len))",
    149: (
        "def is_even(n):\n    return n % 2 == 0\n"
        "n = int(input())\nprint('yes' if is_even(n) else 'no')"
    ),
    150: (
        "def gcd(a, b):\n    while b:\n        a, b = b, a % b\n    return a\n"
        "a, b = map(int, input().split())\nprint(a * b // gcd(a, b))"
    ),
    151: (
        "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n"
        "print(fact(int(input())))"
    ),
    152: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "ok = all(a[i] <= a[i + 1] for i in range(n - 1)) if n > 1 else True\n"
        "print('yes' if ok else 'no')"
    ),
    153: (
        "def powr(x, n):\n    if n == 0:\n        return 1\n    return x * powr(x, n - 1)\n"
        "x, n = map(int, input().split())\nprint(powr(x, n))"
    ),
    154: (
        "def ssum(n):\n    if n <= 0:\n        return 0\n    return n + ssum(n - 1)\n"
        "print(ssum(int(input())))"
    ),
    155: (
        "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n"
        "print(fact(int(input())))"
    ),
    156: "n = int(input())\nprint((1 << n) - 1 if n > 0 else 0)",
    157: (
        "n = int(input())\n"
        "cnt = [0] * 10\n"
        "for _ in range(n):\n    cnt[int(input())] += 1\n"
        "out = []\n"
        "for d in range(10):\n    out.extend([d] * cnt[d])\n"
        "print(' '.join(map(str, out)))"
    ),
    158: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "x = int(input())\n"
        "lo, hi, ans = 0, n - 1, -1\n"
        "while lo <= hi:\n"
        "    mid = (lo + hi) // 2\n"
        "    if a[mid] == x:\n"
        "        ans = mid\n"
        "        lo = mid + 1\n"
        "    elif a[mid] < x:\n"
        "        lo = mid + 1\n"
        "    else:\n"
        "        hi = mid - 1\n"
        "print(ans)"
    ),
    159: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(n):\n"
        "    for j in range(n - 1 - i):\n"
        "        if a[j] > a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(map(str, a)))"
    ),
    160: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "m = int(input())\n"
        "b = [int(input()) for _ in range(m)]\n"
        "i = j = 0\n"
        "out = []\n"
        "while i < n and j < m:\n"
        "    if a[i] <= b[j]:\n"
        "        out.append(a[i])\n        i += 1\n"
        "    else:\n"
        "        out.append(b[j])\n        j += 1\n"
        "out.extend(a[i:])\nout.extend(b[j:])\n"
        "print(' '.join(map(str, out)))"
    ),
    161: (
        "from collections import Counter\n"
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "c = Counter(a)\n"
        "best = max(c.values())\n"
        "print(min(k for k, v in c.items() if v == best))"
    ),
    162: (
        "n = int(input())\n"
        "p = 1\n"
        "for _ in range(n):\n    p *= int(input())\n"
        "print(p)"
    ),
    163: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "print(round(sum(a) / n))"
    ),
    164: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "avg = sum(a) / n\n"
        "above = [str(x) for x in a if x > avg]\n"
        "print(' '.join(above))"
    ),
    165: (
        "n, target = map(int, input().split())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "seen = {}\n"
        "for i, v in enumerate(a):\n"
        "    need = target - v\n"
        "    if need in seen:\n"
        "        print(seen[need], i)\n        break\n"
        "    seen[v] = i\n"
        "else:\n    print(0, 0)"
    ),
    166: (
        "from collections import Counter\n"
        "s = input().strip()\n"
        "c = Counter(s)\n"
        "for ch in s:\n"
        "    if c[ch] == 1:\n"
        "        print(ch)\n        break\n"
        "else:\n    print('_')"
    ),
    167: (
        "n = int(input())\n"
        "freq = {}\n"
        "for _ in range(n):\n    key = input().strip()\n    freq[key] = freq.get(key, 0) + 1\n"
        "q = input().strip()\n"
        "print(freq.get(q, 0))"
    ),
    168: (
        "from collections import defaultdict\n"
        "n = int(input())\n"
        "groups = defaultdict(list)\n"
        "for _ in range(n):\n    w = input().strip()\n    groups[''.join(sorted(w))].append(w)\n"
        "print(len(groups))"
    ),
    169: (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "nums = list(map(int, data))\n"
        "print(max(nums))"
    ),
    170: (
        "import sys\n"
        "text = sys.stdin.read()\n"
        "print(len(text.split()))"
    ),
    171: (
        "import sys\n"
        "total = 0\n"
        "for line in sys.stdin:\n"
        "    line = line.strip()\n"
        "    if not line:\n        continue\n"
        "    _, val = line.split(',')\n"
        "    total += int(val)\n"
        "print(total)"
    ),
    172: (
        "n = int(input())\n"
        "evens = []\n"
        "for _ in range(n):\n"
        "    x = int(input())\n"
        "    if x % 2 == 0:\n"
        "        evens.append(str(x))\n"
        "print(' '.join(evens))"
    ),
    173: (
        "def eval_rpn(tokens):\n"
        "    st = []\n"
        "    ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b,\n"
        "           '*': lambda a, b: a * b, '/': lambda a, b: int(a / b)}\n"
        "    for t in tokens:\n"
        "        if t in ops:\n"
        "            b, a = st.pop(), st.pop()\n"
        "            st.append(ops[t](a, b))\n"
        "        else:\n"
        "            st.append(int(t))\n"
        "    return st[-1]\n"
        "print(eval_rpn(input().split()))"
    ),
    174: (
        "n = int(input())\n"
        "times = [int(input()) for _ in range(n)]\n"
        "wait = total = 0\n"
        "for t in times:\n    total += wait\n    wait += t\n"
        "print(total)"
    ),
    175: (
        "s = input().strip()\n"
        "pairs = {')': '(', ']': '[', '}': '{'}\n"
        "st = []\n"
        "for ch in s:\n"
        "    if ch in '([{':\n"
        "        st.append(ch)\n"
        "    elif not st or st.pop() != pairs[ch]:\n"
        "        print('no')\n        break\n"
        "else:\n    print('yes' if not st else 'no')"
    ),
    176: (
        "from collections import deque\n"
        "n, m = map(int, input().split())\n"
        "g = [[] for _ in range(n)]\n"
        "for _ in range(m):\n    u, v = map(int, input().split())\n    g[u].append(v)\n    g[v].append(u)\n"
        "dist = [-1] * n\n"
        "dist[0] = 0\n"
        "q = deque([0])\n"
        "while q:\n"
        "    u = q.popleft()\n"
        "    for v in g[u]:\n"
        "        if dist[v] == -1:\n"
        "            dist[v] = dist[u] + 1\n"
        "            q.append(v)\n"
        "print(dist[n - 1])"
    ),
    177: "n = int(input())\nprint(n)",
    178: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "x = int(input())\n"
        "print(' '.join(str(v) for v in [x] + a))"
    ),
    179: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "v = int(input())\n"
        "if v in a:\n    a.remove(v)\n"
        "print(' '.join(map(str, a)))"
    ),
    180: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(1, n):\n"
        "    key = a[i]\n"
        "    j = i - 1\n"
        "    while j >= 0 and a[j] > key:\n"
        "        a[j + 1] = a[j]\n        j -= 1\n"
        "    a[j + 1] = key\n"
        "print(' '.join(map(str, a)))"
    ),
    181: (
        "n = int(input())\n"
        "for _ in range(n - 1):\n    input()\n"
        "print(n)"
    ),
    182: (
        "def inorder(vals, i):\n"
        "    if i >= len(vals) or vals[i] == 0:\n        return []\n"
        "    return inorder(vals, 2 * i + 1) + [vals[i]] + inorder(vals, 2 * i + 2)\n"
        "n = int(input())\n"
        "vals = [int(input()) for _ in range(n)]\n"
        "print(' '.join(map(str, inorder(vals, 0))))"
    ),
    183: (
        "n, m = map(int, input().split())\n"
        "g = [[] for _ in range(n)]\n"
        "for _ in range(m):\n    u, v = map(int, input().split())\n    g[u].append(v)\n    g[v].append(u)\n"
        "seen = [False] * n\n"
        "order = []\n"
        "def dfs(u):\n"
        "    seen[u] = True\n"
        "    order.append(u)\n"
        "    for v in g[u]:\n"
        "        if not seen[v]:\n            dfs(v)\n"
        "dfs(0)\n"
        "print(' '.join(map(str, order)))"
    ),
    184: (
        "n, m = map(int, input().split())\n"
        "parent = list(range(n))\n"
        "def find(x):\n"
        "    while parent[x] != x:\n        x = parent[x]\n"
        "    return x\n"
        "def union(a, b):\n"
        "    ra, rb = find(a), find(b)\n"
        "    if ra != rb:\n        parent[rb] = ra\n"
        "for _ in range(m):\n    u, v = map(int, input().split())\n    union(u, v)\n"
        "print(len({find(i) for i in range(n)}))"
    ),
    185: (
        "class Counter:\n"
        "    def __init__(self):\n        self.v = 0\n"
        "    def inc(self):\n        self.v += 1\n"
        "    def dec(self):\n        self.v = max(0, self.v - 1)\n"
        "    def get(self):\n        return self.v\n"
        "c = Counter()\n"
        "k = int(input())\n"
        "out = []\n"
        "for _ in range(k):\n"
        "    cmd = input().strip()\n"
        "    if cmd == 'inc':\n        c.inc()\n"
        "    elif cmd == 'dec':\n        c.dec()\n"
        "    elif cmd == 'get':\n        out.append(str(c.get()))\n"
        "print(' '.join(out))"
    ),
    186: (
        "class Stack:\n"
        "    def __init__(self):\n        self.a = []\n"
        "    def push(self, x):\n        self.a.append(x)\n"
        "    def pop(self):\n        return self.a.pop()\n"
        "    def top(self):\n        return self.a[-1] if self.a else 'empty'\n"
        "st = Stack()\n"
        "k = int(input())\n"
        "out = []\n"
        "for _ in range(k):\n"
        "  parts = input().split()\n"
        "  if parts[0] == 'push':\n    st.push(int(parts[1]))\n"
        "  elif parts[0] == 'pop':\n    out.append(str(st.pop()))\n"
        "  elif parts[0] == 'top':\n    out.append(str(st.top()))\n"
        "print(' '.join(out))"
    ),
    187: (
        "class BankAccount:\n"
        "    def __init__(self, balance=0):\n        self.balance = balance\n"
        "    def deposit(self, x):\n        self.balance += x\n"
        "    def withdraw(self, x):\n        self.balance = max(0, self.balance - x)\n"
        "parts = input().split()\n"
        "bal = int(parts[0])\n"
        "acc = BankAccount(bal)\n"
        "for x in map(int, parts[1:]):\n    acc.withdraw(x)\n"
        "print(acc.balance)"
    ),
    188: (
        "n = int(input())\n"
        "best_name = ''\n"
        "best_avg = -1\n"
        "for _ in range(n):\n"
        "    parts = input().split()\n"
        "    name = parts[0]\n"
        "    grades = list(map(int, parts[1:]))\n"
        "    avg = sum(grades) / len(grades)\n"
        "    if avg > best_avg:\n        best_avg = avg\n        best_name = name\n"
        "print(best_name)"
    ),
    189: (
        "import math\n"
        "k = int(input())\n"
        "out = []\n"
        "for _ in range(k):\n"
        "    parts = input().split()\n"
        "    if parts[0] == 'circle':\n"
        "        r = float(parts[1])\n        out.append(f'{math.pi * r * r:.2f}')\n"
        "    else:\n"
        "        w, h = map(float, parts[1:])\n        out.append(f'{w * h:.2f}')\n"
        "print(' '.join(out))"
    ),
    190: (
        "class Employee:\n"
        "    def __init__(self, salary):\n        self.salary = salary\n"
        "    def pay(self):\n        return self.salary\n"
        "class Manager(Employee):\n"
        "    def __init__(self, salary, bonus):\n        super().__init__(salary)\n        self.bonus = bonus\n"
        "    def pay(self):\n        return self.salary + self.bonus\n"
        "k = int(input())\n"
        "out = []\n"
        "for _ in range(k):\n"
        "    parts = input().split()\n"
        "    if parts[0] == 'employee':\n        out.append(str(Employee(int(parts[1])).pay()))\n"
        "    else:\n        out.append(str(Manager(int(parts[1]), int(parts[2])).pay()))\n"
        "print(' '.join(out))"
    ),
    191: (
        "class Animal:\n"
        "    def speak(self):\n        return ''\n"
        "class Dog(Animal):\n"
        "    def speak(self):\n        return 'woof'\n"
        "class Cat(Animal):\n"
        "    def speak(self):\n        return 'meow'\n"
        "n = int(input())\n"
        "out = []\n"
        "for _ in range(n):\n"
        "    kind = input().strip()\n"
        "    obj = Dog() if kind == 'Dog' else Cat()\n"
        "    out.append(obj.speak())\n"
        "print(' '.join(out))"
    ),
    192: (
        "n = int(input())\n"
        "total = 0\n"
        "for _ in range(n):\n"
        "    _, w = map(int, input().split())\n"
        "    if w <= 10:\n        total += w\n"
        "print(total)"
    ),
}

_DEBUG_PAIR: dict[int, tuple[str, str]] = {
    147: (
        "s = input().strip()\nc = input().strip()\nidx = s.find(c)\nprint(idx + 1 if idx >= 0 else -1)",
        "s = input().strip()\nc = input().strip()\nprint(s.find(c))",
    ),
    151: (
        "def fact(n):\n    if n <= 1:\n        result = 1\n    else:\n        result = n * fact(n - 1)\n"
        "print(fact(int(input())))",
        "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n"
        "print(fact(int(input())))",
    ),
    155: (
        "def fact(n):\n    if n == 1:\n        return 1\n    return n * fact(n - 1)\nprint(fact(int(input())))",
        "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\nprint(fact(int(input())))",
    ),
    159: (
        "n = int(input())\n"
        "a = [0] + [int(input()) for _ in range(n)]\n"
        "for i in range(1, n):\n"
        "    for j in range(1, n - i + 1):\n"
        "        if a[j] > a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(str(a[i]) for i in range(1, n + 1)))",
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(n):\n"
        "    for j in range(n - 1 - i):\n"
        "        if a[j] > a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(map(str, a)))",
    ),
    163: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "print(int(sum(a) / n))",
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "print(round(sum(a) / n))",
    ),
    167: (
        "n = int(input())\n"
        "freq = {}\n"
        "for _ in range(n):\n    key = input().strip()\n    freq[key] = freq.get(key, 0) + 1\n"
        "q = input().strip()\n"
        "print(freq.get(q, -1))",
        "n = int(input())\n"
        "freq = {}\n"
        "for _ in range(n):\n    key = input().strip()\n    freq[key] = freq.get(key, 0) + 1\n"
        "q = input().strip()\n"
        "print(freq.get(q, 0))",
    ),
    171: (
        "import sys\n"
        "total = 0\n"
        "for line in sys.stdin.buffer:\n"
        "    _, val = line.decode().strip().split(',')\n"
        "    total += int(val)\n"
        "print(total)",
        "import sys\n"
        "total = 0\n"
        "for line in sys.stdin:\n"
        "    line = line.strip()\n"
        "    if not line:\n        continue\n"
        "    _, val = line.split(',')\n"
        "    total += int(val)\n"
        "print(total)",
    ),
    175: (
        "s = input().strip()\n"
        "pairs = {')': '(', ']': '[', '}': '{'}\n"
        "st = []\n"
        "for ch in s:\n"
        "    if ch in '([{':\n"
        "        st.append(ch)\n"
        "    else:\n"
        "        if st.pop() != pairs[ch]:\n"
        "            print('no')\n            break\n"
        "else:\n    print('yes' if not st else 'no')",
        "s = input().strip()\n"
        "pairs = {')': '(', ']': '[', '}': '{'}\n"
        "st = []\n"
        "for ch in s:\n"
        "    if ch in '([{':\n"
        "        st.append(ch)\n"
        "    elif not st or st.pop() != pairs[ch]:\n"
        "        print('no')\n        break\n"
        "else:\n    print('yes' if not st else 'no')",
    ),
    179: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "v = int(input())\n"
        "for i in range(1, n):\n"
        "    if a[i] == v:\n"
        "        del a[i]\n        break\n"
        "print(' '.join(map(str, a)))",
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "v = int(input())\n"
        "if v in a:\n    a.remove(v)\n"
        "print(' '.join(map(str, a)))",
    ),
    183: (
        "n, m = map(int, input().split())\n"
        "g = [[] for _ in range(n + 1)]\n"
        "for _ in range(m):\n    u, v = map(int, input().split())\n    g[u].append(v)\n    g[v].append(u)\n"
        "seen = [False] * (n + 1)\n"
        "order = []\n"
        "def dfs(u):\n"
        "    seen[u] = True\n"
        "    order.append(u)\n"
        "    for v in g[u]:\n"
        "        if not seen[v]:\n            dfs(v)\n"
        "dfs(1)\n"
        "print(' '.join(str(u - 1) for u in order))",
        "n, m = map(int, input().split())\n"
        "g = [[] for _ in range(n)]\n"
        "for _ in range(m):\n    u, v = map(int, input().split())\n    g[u].append(v)\n    g[v].append(u)\n"
        "seen = [False] * n\n"
        "order = []\n"
        "def dfs(u):\n"
        "    seen[u] = True\n"
        "    order.append(u)\n"
        "    for v in g[u]:\n"
        "        if not seen[v]:\n            dfs(v)\n"
        "dfs(0)\n"
        "print(' '.join(map(str, order)))",
    ),
    187: (
        "class BankAccount:\n"
        "    def __init__(self, balance=0):\n        self.balance = balance\n"
        "    def withdraw(self, x):\n        self.balance -= x\n"
        "parts = input().split()\n"
        "acc = BankAccount(int(parts[0]))\n"
        "for x in map(int, parts[1:]):\n    acc.withdraw(x)\n"
        "print(acc.balance)",
        "class BankAccount:\n"
        "    def __init__(self, balance=0):\n        self.balance = balance\n"
        "    def deposit(self, x):\n        self.balance += x\n"
        "    def withdraw(self, x):\n        self.balance = max(0, self.balance - x)\n"
        "parts = input().split()\n"
        "bal = int(parts[0])\n"
        "acc = BankAccount(bal)\n"
        "for x in map(int, parts[1:]):\n    acc.withdraw(x)\n"
        "print(acc.balance)",
    ),
    191: (
        "class Animal:\n"
        "    def speak(self):\n        return '?'\n"
        "class Dog(Animal):\n"
        "    def speak(self):\n        return 'woof'\n"
        "class Cat(Animal):\n"
        "    def speak(self):\n        return 'meow'\n"
        "n = int(input())\n"
        "out = []\n"
        "for _ in range(n):\n"
        "    kind = input().strip()\n"
        "    obj = Animal()\n"
        "    if kind == 'Dog':\n        obj = Dog()\n"
        "    out.append(obj.speak())\n"
        "print(' '.join(out))",
        "class Animal:\n"
        "    def speak(self):\n        return ''\n"
        "class Dog(Animal):\n"
        "    def speak(self):\n        return 'woof'\n"
        "class Cat(Animal):\n"
        "    def speak(self):\n        return 'meow'\n"
        "n = int(input())\n"
        "out = []\n"
        "for _ in range(n):\n"
        "    kind = input().strip()\n"
        "    obj = Dog() if kind == 'Dog' else Cat()\n"
        "    out.append(obj.speak())\n"
        "print(' '.join(out))",
    ),
}


def _build_row(task_num: int) -> dict[str, Any]:
    action = _ACTION_BY_NUM[task_num]
    row: dict[str, Any] = {
        "title": _TITLES[task_num],
        "goal": _GOALS[task_num],
        "action": action,
        "chapter_key": _CHAPTER_BY_NUM[task_num],
        "tests": [dict(t) for t in _TESTS[task_num]],
        "python": _PYTHON_REF[task_num],
    }
    pitfall = _PITFALL_BY_NUM.get(task_num)
    if pitfall:
        row["pitfall_id"] = pitfall
    if action == "debug" and task_num in _DEBUG_PAIR:
        buggy, fixed = _DEBUG_PAIR[task_num]
        row["debug_buggy"] = buggy
        row["debug_fixed"] = fixed
    return row


EXPANSION_TASKS_145_192: dict[int, dict[str, Any]] = {
    n: _build_row(n) for n in range(145, 193)
}
