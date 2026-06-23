"""Pascal task catalog v4 — 270 tasks, 21 chapters."""
from __future__ import annotations

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

V4_CORE_TASK_COUNT = 270

V4_TASKS: list[TaskRow] = []


def _extend(chapter: str, rows: list[tuple]) -> None:
    for row in rows:
        padded = row + ("",) * (10 - len(row))
        V4_TASKS.append((padded[0], chapter, *padded[1:9]))  # type: ignore[misc]


# 1. Базовая программа (12)
_extend("program_skeleton", [
    ("pas_001", "Вывести приветствие", "сборка_программы", "assemble", "task_001", "Вывести строку Hello.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_002", "Сохранить возраст", "исправление", "debug", "task_002", "Создать переменную age со значением 18 и вывести ее.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_003", "Посчитать сумму двух чисел", "перевод_программы", "implement", "task_003", "Задать два числа и вывести их сумму.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "hard"),
    ("pas_004", "Посчитать площадь прямоугольника", "сборка_программы", "assemble", "task_004", "Задать ширину и высоту, вывести площадь.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_005", "Посчитать периметр прямоугольника", "исправление", "debug", "task_005", "Задать стороны, вывести периметр.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_006", "Поменять две переменные местами", "перевод_программы", "implement", "task_006", "Обменять значения через временную переменную.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "hard"),
    ("pas_007", "Найти среднее двух чисел", "сборка_программы", "assemble", "task_007", "Задать два числа и вывести среднее с дробной частью.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_008", "Вывести последнюю цифру числа", "исправление", "debug", "task_008", "Для заданного числа вывести последнюю цифру.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_009", "Найти сумму цифр двузначного числа", "перевод_программы", "implement", "task_009", "Задать двузначное число и вывести сумму его цифр.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "hard"),
    ("pas_010", "Перевести минуты в часы и минуты", "сборка_программы", "assemble", "task_010", "Задано количество минут; вывести полные часы и остаток минут.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_011", "Рассчитать стоимость покупки", "исправление", "debug", "task_011", "Заданы цена и количество; вывести итоговую стоимость.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_012", "Проверочная: чек с налогом и скидкой", "перевод_программы", "implement", "task_012", "Рассчитать итоговую сумму заказа с налогом и скидкой.", "program_entry; typed_declaration; assignment; arithmetic_ops; stdout_write", "hard"),
])

# 2. Ввод и вывод (12)
_extend("io", [
    ("pas_013", "Прочитать число и вывести квадрат", "сборка_программы", "assemble", "task_013", "Пользователь вводит число; программа выводит квадрат.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_014", "Прочитать имя и вывести приветствие", "исправление", "debug", "task_014", "Пользователь вводит имя; программа выводит приветствие.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_015", "Прочитать два числа и вывести сумму", "перевод_программы", "implement", "task_015", "Ввести два числа и вывести их сумму.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "hard"),
    ("pas_016", "Прочитать стороны прямоугольника", "сборка_программы", "assemble", "task_016", "Ввести стороны и вывести площадь.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_017", "Прочитать минуты", "исправление", "debug", "task_017", "Ввести минуты и вывести часы и остаток минут.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_018", "Прочитать цену и количество", "перевод_программы", "implement", "task_018", "Ввести цену и количество, вывести стоимость покупки.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "hard"),
    ("pas_019", "Прочитать число и вывести последнюю цифру", "сборка_программы", "assemble", "task_019", "Использовать целочисленные операции.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_020", "Прочитать двузначное число", "исправление", "debug", "task_020", "Вывести сумму цифр.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_021", "Прочитать температуру Celsius", "перевод_программы", "implement", "task_021", "Вывести Fahrenheit.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "hard"),
    ("pas_022", "Прочитать строку с числом", "сборка_программы", "assemble", "task_022", "Преобразовать строку в число и увеличить на 1.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "easy"),
    ("pas_023", "Прочитать три числа", "исправление", "debug", "task_023", "Вывести среднее значение.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "medium"),
    ("pas_024", "Проверочная: стоимость доставки", "перевод_программы", "implement", "task_024", "Ввести цену товара, вес и тариф; вывести итоговую стоимость.", "typed_declaration; stdin_read; assignment; arithmetic_ops; stdout_write", "hard"),
])

# 3. Простое ветвление (14)
_extend("conditions", [
    ("pas_025", "Проверить знак числа", "сборка_программы", "assemble", "task_025", "Вывести, положительное число или нет.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_026", "Проверить четность", "исправление", "debug", "task_026", "Вывести even или odd.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_027", "Вывести большее из двух чисел", "перевод_программы", "implement", "task_027", "Сравнить два числа и вывести максимум.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_028", "Найти модуль числа", "сборка_программы", "assemble", "task_028", "Если число отрицательное, изменить знак.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_029", "Проверить диапазон", "исправление", "debug", "task_029", "Определить, входит ли число в диапазон 10..20.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_030", "Проверить совершеннолетие", "перевод_программы", "implement", "task_030", "По возрасту вывести разрешение или отказ.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_031", "Проверить пароль", "сборка_программы", "assemble", "task_031", "Сравнить введенную строку с правильным паролем.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_032", "Проверить скидку", "исправление", "debug", "task_032", "Если сумма больше лимита, применить скидку.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_033", "Проверить деление", "перевод_программы", "implement", "task_033", "Если делитель не равен нулю, вывести частное.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_034", "Выбрать текст по условию", "сборка_программы", "assemble", "task_034", "Сохранить строку статуса в переменную и вывести ее.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_035", "Проверить корректность оценки", "исправление", "debug", "task_035", "Оценка должна быть от 1 до 5.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_036", "Проверить доступ по возрасту и билету", "перевод_программы", "implement", "task_036", "Доступ есть только при двух условиях.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_037", "Проверить знак произведения", "сборка_программы", "assemble", "task_037", "Определить знак произведения без умножения.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_038", "Проверочная: допуск к экзамену", "исправление", "debug", "task_038", "Учитывать баллы, посещаемость и задолженности.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
])

# 4. Множественное ветвление (12)
_extend("conditions_multi", [
    ("pas_039", "Оценка по баллам", "перевод_программы", "implement", "task_039", "Вывести 5, 4, 3 или 2 по диапазонам.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_040", "День недели", "сборка_программы", "assemble", "task_040", "Вывести название дня по номеру.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_041", "Сезон по месяцу", "исправление", "debug", "task_041", "Определить сезон.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_042", "Тариф по категории", "перевод_программы", "implement", "task_042", "Выбрать цену тарифа по коду.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_043", "Размер скидки", "сборка_программы", "assemble", "task_043", "Выбрать процент скидки по сумме заказа.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_044", "Мини-калькулятор", "исправление", "debug", "task_044", "Выполнить операцию по символу +, -, *, /.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_045", "Статус заказа", "перевод_программы", "implement", "task_045", "Вывести текст статуса по коду.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_046", "Категория возраста", "сборка_программы", "assemble", "task_046", "Определить: ребенок, подросток, взрослый.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_047", "Рейтинг игрока", "исправление", "debug", "task_047", "Определить уровень по очкам.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
    ("pas_048", "Тип треугольника", "перевод_программы", "implement", "task_048", "Определить: равносторонний, равнобедренный или обычный.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "hard"),
    ("pas_049", "Категория товара", "сборка_программы", "assemble", "task_049", "По коду вывести категорию.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "easy"),
    ("pas_050", "Проверочная: меню банкомата", "исправление", "debug", "task_050", "Выбрать действие по пункту меню.", "typed_declaration; stdin_read; simple_branch; assignment; stdout_write", "medium"),
])

# 5. Циклы: база (16)
_extend("loops", [
    ("pas_051", "Вывести числа от 1 до N", "перевод_программы", "implement", "task_051", "Пользователь вводит N, вывести последовательность.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "hard"),
    ("pas_052", "Вывести числа от N до 1", "сборка_программы", "assemble", "task_052", "Сделать обратный счет.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "easy"),
    ("pas_053", "Сумма чисел от 1 до N", "исправление", "debug", "task_053", "Накопить сумму.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "medium"),
    ("pas_054", "Произведение чисел", "перевод_программы", "implement", "task_054", "Вычислить факториальный тип произведения.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "hard"),
    ("pas_055", "Посчитать четные числа", "сборка_программы", "assemble", "task_055", "Среди 1..N посчитать четные.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "easy"),
    ("pas_056", "Таблица умножения", "исправление", "debug", "task_056", "Вывести строку таблицы для одного числа.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "medium"),
    ("pas_057", "Сумма квадратов", "перевод_программы", "implement", "task_057", "Накопить сумму квадратов от 1 до N.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "hard"),
    ("pas_058", "Максимум из вводимых чисел", "сборка_программы", "assemble", "task_058", "Ввести N чисел и найти максимум.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "easy"),
    ("pas_059", "Минимум из вводимых чисел", "исправление", "debug", "task_059", "Ввести N чисел и найти минимум.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "medium"),
    ("pas_060", "Количество положительных", "перевод_программы", "implement", "task_060", "Среди N чисел посчитать положительные.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "hard"),
    ("pas_061", "Сумма покупок", "сборка_программы", "assemble", "task_061", "Вводить цены и накопить итог.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "easy"),
    ("pas_062", "Средний балл", "исправление", "debug", "task_062", "Ввести N оценок и вывести среднее.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "medium"),
    ("pas_063", "Ввод до нуля", "перевод_программы", "implement", "task_063", "Читать числа, пока не введен 0.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "hard"),
    ("pas_064", "Повтор пароля", "сборка_программы", "assemble", "task_064", "Спрашивать пароль до правильного ввода.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "easy"),
    ("pas_065", "Накопление бонусов", "исправление", "debug", "task_065", "Начислять бонусы за несколько покупок.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "medium"),
    ("pas_066", "Проверочная: анализ экзамена", "перевод_программы", "implement", "task_066", "Найти средний балл, максимум и количество сдавших.", "typed_declaration; stdin_read; counted_loop; pre_condition_loop; assignment; stdout_write", "hard"),
])

# 6. Вложенные циклы и управление (12)
_extend("loops_adv", [
    ("pas_067", "Квадрат из символов", "сборка_программы", "assemble", "task_067", "Вывести квадрат N x N.", "nested_iteration; loop_control; counted_loop; stdout_write", "easy"),
    ("pas_068", "Прямоугольник из символов", "исправление", "debug", "task_068", "Вывести прямоугольник заданного размера.", "nested_iteration; loop_control; counted_loop; stdout_write", "medium"),
    ("pas_069", "Треугольник из символов", "перевод_программы", "implement", "task_069", "Вывести лестницу из звездочек.", "nested_iteration; loop_control; counted_loop; stdout_write", "hard"),
    ("pas_070", "Полная таблица умножения", "сборка_программы", "assemble", "task_070", "Вывести таблицу 1..9.", "nested_iteration; loop_control; counted_loop; stdout_write", "easy"),
    ("pas_071", "Шахматная доска", "исправление", "debug", "task_071", "Вывести клетки двумя символами.", "nested_iteration; loop_control; counted_loop; stdout_write", "medium"),
    ("pas_072", "Координатная сетка", "перевод_программы", "implement", "task_072", "Вывести пары координат.", "nested_iteration; loop_control; counted_loop; stdout_write", "hard"),
    ("pas_073", "Поиск первой подходящей пары", "сборка_программы", "assemble", "task_073", "Найти пару чисел с нужной суммой.", "nested_iteration; loop_control; counted_loop; stdout_write", "easy"),
    ("pas_074", "Пропуск запрещенных значений", "исправление", "debug", "task_074", "Использовать пропуск итерации.", "nested_iteration; loop_control; counted_loop; stdout_write", "medium"),
    ("pas_075", "Досрочный выход из поиска", "перевод_программы", "implement", "task_075", "Остановить цикл после нахождения.", "nested_iteration; loop_control; counted_loop; stdout_write", "hard"),
    ("pas_076", "Подсчет мест в зале", "сборка_программы", "assemble", "task_076", "Пройти по рядам и местам.", "nested_iteration; loop_control; counted_loop; stdout_write", "easy"),
    ("pas_077", "Матрица расстояний", "исправление", "debug", "task_077", "Вывести таблицу расстояний между точками.", "nested_iteration; loop_control; counted_loop; stdout_write", "medium"),
    ("pas_078", "Проверочная: схема рассадки", "перевод_программы", "implement", "task_078", "Распределить студентов по рядам с ограничениями.", "nested_iteration; loop_control; counted_loop; stdout_write", "hard"),
])

# 7. Массивы (16)
_extend("static_arrays", [
    ("pas_079", "Заполнить массив числами", "сборка_программы", "assemble", "task_079", "Ввести N элементов и вывести их.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "easy"),
    ("pas_080", "Сумма массива", "исправление", "debug", "task_080", "Найти сумму элементов.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "medium"),
    ("pas_081", "Максимум массива", "перевод_программы", "implement", "task_081", "Найти наибольший элемент.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "hard"),
    ("pas_082", "Минимум массива", "сборка_программы", "assemble", "task_082", "Найти наименьший элемент.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "easy"),
    ("pas_083", "Индекс максимума", "исправление", "debug", "task_083", "Вывести позицию максимального элемента.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "medium"),
    ("pas_084", "Количество четных элементов", "перевод_программы", "implement", "task_084", "Пройти массив и посчитать четные.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "hard"),
    ("pas_085", "Сумма положительных элементов", "сборка_программы", "assemble", "task_085", "Накопить только положительные.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "easy"),
    ("pas_086", "Замена отрицательных на ноль", "исправление", "debug", "task_086", "Изменить элементы массива.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "medium"),
    ("pas_087", "Проверить наличие числа", "перевод_программы", "implement", "task_087", "Определить, есть ли число в массиве.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "hard"),
    ("pas_088", "Найти первое вхождение", "сборка_программы", "assemble", "task_088", "Вывести индекс первого совпадения.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "easy"),
    ("pas_089", "Скопировать массив", "исправление", "debug", "task_089", "Создать копию элементов.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "medium"),
    ("pas_090", "Развернуть массив", "перевод_программы", "implement", "task_090", "Вывести элементы в обратном порядке.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "hard"),
    ("pas_091", "Сдвиг массива вправо", "сборка_программы", "assemble", "task_091", "Циклически сдвинуть элементы.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "easy"),
    ("pas_092", "Сравнить два массива", "исправление", "debug", "task_092", "Проверить одинаковую длину и элементы.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "medium"),
    ("pas_093", "Объединить два массива", "перевод_программы", "implement", "task_093", "Создать общий список элементов.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "hard"),
    ("pas_094", "Проверочная: статистика продаж", "сборка_программы", "assemble", "task_094", "По массиву продаж найти сумму, максимум и количество успешных дней.", "indexed_sequence; collection_iteration; counted_loop; stdout_write", "easy"),
])

# 8. Динамические массивы и списки (14)
_extend("dynamic_arrays", [
    ("pas_095", "Добавить элементы в список", "исправление", "debug", "task_095", "Вводить значения и добавлять в динамическую коллекцию.", "dynamic_array; collection_iteration; stdout_write", "medium"),
    ("pas_096", "Удалить последнее значение", "перевод_программы", "implement", "task_096", "Убрать последний элемент, если список не пуст.", "dynamic_array; collection_iteration; stdout_write", "hard"),
    ("pas_097", "Добавить только положительные", "сборка_программы", "assemble", "task_097", "Фильтровать ввод при добавлении.", "dynamic_array; collection_iteration; stdout_write", "easy"),
    ("pas_098", "Список покупок", "исправление", "debug", "task_098", "Добавлять товары и вывести весь список.", "dynamic_array; collection_iteration; stdout_write", "medium"),
    ("pas_099", "Список оценок", "перевод_программы", "implement", "task_099", "Добавить оценки и найти среднюю.", "dynamic_array; collection_iteration; stdout_write", "hard"),
    ("pas_100", "Найти элемент в списке", "сборка_программы", "assemble", "task_100", "Проверить наличие значения.", "dynamic_array; collection_iteration; stdout_write", "easy"),
    ("pas_101", "Удалить все нули", "исправление", "debug", "task_101", "Оставить только ненулевые элементы.", "dynamic_array; collection_iteration; stdout_write", "medium"),
    ("pas_102", "Разделить список", "перевод_программы", "implement", "task_102", "Положительные в один список, отрицательные в другой.", "dynamic_array; collection_iteration; stdout_write", "hard"),
    ("pas_103", "Список уникальных значений", "сборка_программы", "assemble", "task_103", "Добавить элемент только если его еще нет.", "dynamic_array; collection_iteration; stdout_write", "easy"),
    ("pas_104", "Ограничить размер списка", "исправление", "debug", "task_104", "Хранить только последние K значений.", "dynamic_array; collection_iteration; stdout_write", "medium"),
    ("pas_105", "Перенести элементы между списками", "перевод_программы", "implement", "task_105", "Переместить подходящие элементы.", "dynamic_array; collection_iteration; stdout_write", "hard"),
    ("pas_106", "Очередь заявок на списке", "сборка_программы", "assemble", "task_106", "Добавлять заявки и обрабатывать первую.", "dynamic_array; collection_iteration; stdout_write", "easy"),
    ("pas_107", "История действий", "исправление", "debug", "task_107", "Хранить последние действия пользователя.", "dynamic_array; collection_iteration; stdout_write", "medium"),
    ("pas_108", "Проверочная: корзина покупателя", "перевод_программы", "implement", "task_108", "Добавлять, удалять и считать сумму товаров.", "dynamic_array; collection_iteration; stdout_write", "hard"),
])

# 9. Строки (14)
_extend("strings", [
    ("pas_109", "Длина строки", "сборка_программы", "assemble", "task_109", "Ввести строку и вывести длину.", "string_sequence; collection_iteration; simple_branch; stdout_write", "easy"),
    ("pas_110", "Первый и последний символ", "исправление", "debug", "task_110", "Вывести крайние символы строки.", "string_sequence; collection_iteration; simple_branch; stdout_write", "medium"),
    ("pas_111", "Подсчет символа", "перевод_программы", "implement", "task_111", "Посчитать, сколько раз символ встречается в строке.", "string_sequence; collection_iteration; simple_branch; stdout_write", "hard"),
    ("pas_112", "Проверить наличие символа", "сборка_программы", "assemble", "task_112", "Определить, есть ли символ.", "string_sequence; collection_iteration; simple_branch; stdout_write", "easy"),
    ("pas_113", "Подсчитать цифры в строке", "исправление", "debug", "task_113", "Пройти строку и посчитать цифры.", "string_sequence; collection_iteration; simple_branch; stdout_write", "medium"),
    ("pas_114", "Удалить пробелы", "перевод_программы", "implement", "task_114", "Собрать строку без пробелов.", "string_sequence; collection_iteration; simple_branch; stdout_write", "hard"),
    ("pas_115", "Развернуть строку", "сборка_программы", "assemble", "task_115", "Вывести строку наоборот.", "string_sequence; collection_iteration; simple_branch; stdout_write", "easy"),
    ("pas_116", "Проверить палиндром", "исправление", "debug", "task_116", "Строка читается одинаково слева и справа.", "string_sequence; collection_iteration; simple_branch; stdout_write", "medium"),
    ("pas_117", "Проверить пароль", "перевод_программы", "implement", "task_117", "Пароль должен иметь длину и цифру.", "string_sequence; collection_iteration; simple_branch; stdout_write", "hard"),
    ("pas_118", "Разбить строку на слова", "сборка_программы", "assemble", "task_118", "Вывести слова по одному.", "string_sequence; collection_iteration; simple_branch; stdout_write", "easy"),
    ("pas_119", "Найти самое длинное слово", "исправление", "debug", "task_119", "Среди слов найти максимальное по длине.", "string_sequence; collection_iteration; simple_branch; stdout_write", "medium"),
    ("pas_120", "Заменить символы", "перевод_программы", "implement", "task_120", "Заменить один символ на другой.", "string_sequence; collection_iteration; simple_branch; stdout_write", "hard"),
    ("pas_121", "Сформировать логин", "сборка_программы", "assemble", "task_121", "Из имени и фамилии собрать логин.", "string_sequence; collection_iteration; simple_branch; stdout_write", "easy"),
    ("pas_122", "Проверочная: валидация анкеты", "исправление", "debug", "task_122", "Проверить имя, возраст и пароль.", "string_sequence; collection_iteration; simple_branch; stdout_write", "medium"),
])

# 10. Функции и процедуры (18)
_extend("functions", [
    ("pas_123", "Функция суммы", "перевод_программы", "implement", "task_123", "Оформить сумму двух чисел функцией.", "function_definition; function_invocation; return_flow", "hard"),
    ("pas_124", "Функция максимума", "сборка_программы", "assemble", "task_124", "Вернуть большее из двух чисел.", "function_definition; function_invocation; return_flow", "easy"),
    ("pas_125", "Функция четности", "исправление", "debug", "task_125", "Вернуть истину, если число четное.", "function_definition; function_invocation; return_flow", "medium"),
    ("pas_126", "Функция скидки", "перевод_программы", "implement", "task_126", "Вернуть цену с учетом скидки.", "function_definition; function_invocation; return_flow", "hard"),
    ("pas_127", "Процедура вывода сообщения", "сборка_программы", "assemble", "task_127", "Вынести повторяющийся вывод в процедуру.", "function_definition; function_invocation; return_flow", "easy"),
    ("pas_128", "Процедура обмена значений", "исправление", "debug", "task_128", "Поменять два значения местами.", "function_definition; function_invocation; return_flow", "medium"),
    ("pas_129", "Функция площади", "перевод_программы", "implement", "task_129", "Вернуть площадь прямоугольника.", "function_definition; function_invocation; return_flow", "hard"),
    ("pas_130", "Функция перевода температуры", "сборка_программы", "assemble", "task_130", "Celsius -> Fahrenheit.", "function_definition; function_invocation; return_flow", "easy"),
    ("pas_131", "Функция налога", "исправление", "debug", "task_131", "Вернуть сумму налога.", "function_definition; function_invocation; return_flow", "medium"),
    ("pas_132", "Функция среднего массива", "перевод_программы", "implement", "task_132", "Вычислить среднее значение.", "function_definition; function_invocation; return_flow", "hard"),
    ("pas_133", "Функция поиска элемента", "сборка_программы", "assemble", "task_133", "Вернуть, найден ли элемент.", "function_definition; function_invocation; return_flow", "easy"),
    ("pas_134", "Функция индекса элемента", "исправление", "debug", "task_134", "Вернуть индекс или специальное значение.", "function_definition; function_invocation; return_flow", "medium"),
    ("pas_135", "Функция подсчета подходящих", "перевод_программы", "implement", "task_135", "Посчитать элементы по условию.", "function_definition; function_invocation; return_flow", "hard"),
    ("pas_136", "Функция проверки пароля", "сборка_программы", "assemble", "task_136", "Вынести правила пароля в функцию.", "function_definition; function_invocation; return_flow", "easy"),
    ("pas_137", "Функция форматирования имени", "исправление", "debug", "task_137", "Собрать строку из имени и фамилии.", "function_definition; function_invocation; return_flow", "medium"),
    ("pas_138", "Функция категории оценки", "перевод_программы", "implement", "task_138", "Вернуть текстовую категорию.", "function_definition; function_invocation; return_flow", "hard"),
    ("pas_139", "Функция расчета зарплаты", "сборка_программы", "assemble", "task_139", "Учесть часы, ставку и премию.", "function_definition; function_invocation; return_flow", "easy"),
    ("pas_140", "Проверочная: калькулятор функций", "исправление", "debug", "task_140", "Меню вызывает разные функции расчета.", "function_definition; function_invocation; return_flow", "medium"),
])

# 11. Рекурсия (8)
_extend("recursion", [
    ("pas_141", "Рекурсивный факториал", "перевод_программы", "implement", "task_141", "Вычислить факториал через рекурсию.", "function_definition; recursion; simple_branch; return_flow", "hard"),
    ("pas_142", "Рекурсивная сумма чисел", "сборка_программы", "assemble", "task_142", "Найти сумму от 1 до N.", "function_definition; recursion; simple_branch; return_flow", "easy"),
    ("pas_143", "Рекурсивный Fibonacci", "исправление", "debug", "task_143", "Найти N-е число.", "function_definition; recursion; simple_branch; return_flow", "medium"),
    ("pas_144", "Рекурсивный обратный вывод", "перевод_программы", "implement", "task_144", "Вывести числа от N до 1.", "function_definition; recursion; simple_branch; return_flow", "hard"),
    ("pas_145", "Рекурсивная сумма цифр", "сборка_программы", "assemble", "task_145", "Вычислить сумму цифр числа.", "function_definition; recursion; simple_branch; return_flow", "easy"),
    ("pas_146", "Рекурсивный поиск в массиве", "исправление", "debug", "task_146", "Проверить наличие элемента.", "function_definition; recursion; simple_branch; return_flow", "medium"),
    ("pas_147", "Рекурсивная проверка палиндрома", "перевод_программы", "implement", "task_147", "Проверить строку.", "function_definition; recursion; simple_branch; return_flow", "hard"),
    ("pas_148", "Проверочная: дерево папок", "сборка_программы", "assemble", "task_148", "Посчитать вложенные элементы рекурсивно.", "function_definition; recursion; simple_branch; return_flow", "easy"),
])

# 12. Поиск, фильтрация, свертка (18)
_extend("algorithms", [
    ("pas_149", "Линейный поиск товара", "исправление", "debug", "task_149", "Найти товар по названию.", "search_find; filter_select; fold_aggregate; collection_iteration", "medium"),
    ("pas_150", "Поиск первого дорогого товара", "перевод_программы", "implement", "task_150", "Найти первый товар дороже лимита.", "search_find; filter_select; fold_aggregate; collection_iteration", "hard"),
    ("pas_151", "Фильтрация положительных чисел", "сборка_программы", "assemble", "task_151", "Оставить только положительные.", "search_find; filter_select; fold_aggregate; collection_iteration", "easy"),
    ("pas_152", "Фильтрация строк по длине", "исправление", "debug", "task_152", "Оставить строки длиннее K.", "search_find; filter_select; fold_aggregate; collection_iteration", "medium"),
    ("pas_153", "Сумма подходящих элементов", "перевод_программы", "implement", "task_153", "Сложить элементы, прошедшие условие.", "search_find; filter_select; fold_aggregate; collection_iteration", "hard"),
    ("pas_154", "Количество подходящих элементов", "сборка_программы", "assemble", "task_154", "Посчитать элементы по фильтру.", "search_find; filter_select; fold_aggregate; collection_iteration", "easy"),
    ("pas_155", "Проверка хотя бы одного элемента", "исправление", "debug", "task_155", "Определить, есть ли подходящий элемент.", "search_find; filter_select; fold_aggregate; collection_iteration", "medium"),
    ("pas_156", "Проверка всех элементов", "перевод_программы", "implement", "task_156", "Все ли значения положительные.", "search_find; filter_select; fold_aggregate; collection_iteration", "hard"),
    ("pas_157", "Преобразование цен", "сборка_программы", "assemble", "task_157", "Применить скидку ко всем ценам.", "search_find; filter_select; fold_aggregate; collection_iteration", "easy"),
    ("pas_158", "Преобразование строк", "исправление", "debug", "task_158", "Привести список имен к единому виду.", "search_find; filter_select; fold_aggregate; collection_iteration", "medium"),
    ("pas_159", "Сумма заказов клиента", "перевод_программы", "implement", "task_159", "Сложить заказы выбранного клиента.", "search_find; filter_select; fold_aggregate; collection_iteration", "hard"),
    ("pas_160", "Средний рейтинг", "сборка_программы", "assemble", "task_160", "Посчитать среднее только по активным отзывам.", "search_find; filter_select; fold_aggregate; collection_iteration", "easy"),
    ("pas_161", "Отбор студентов", "исправление", "debug", "task_161", "Выбрать студентов с проходным баллом.", "search_find; filter_select; fold_aggregate; collection_iteration", "medium"),
    ("pas_162", "Отбор файлов по расширению", "перевод_программы", "implement", "task_162", "Оставить только файлы нужного типа.", "search_find; filter_select; fold_aggregate; collection_iteration", "hard"),
    ("pas_163", "Преобразование температур", "сборка_программы", "assemble", "task_163", "Список Celsius перевести в Fahrenheit.", "search_find; filter_select; fold_aggregate; collection_iteration", "easy"),
    ("pas_164", "Группировка результатов вручную", "исправление", "debug", "task_164", "Распределить значения по категориям.", "search_find; filter_select; fold_aggregate; collection_iteration", "medium"),
    ("pas_165", "Поиск лучшего предложения", "перевод_программы", "implement", "task_165", "Выбрать товар с лучшей ценой.", "search_find; filter_select; fold_aggregate; collection_iteration", "hard"),
    ("pas_166", "Проверочная: отчет магазина", "сборка_программы", "assemble", "task_166", "Отфильтровать заказы, посчитать сумму и найти максимум.", "search_find; filter_select; fold_aggregate; collection_iteration", "easy"),
])

# 13. Сортировка (10)
_extend("sorting", [
    ("pas_167", "Сортировка чисел по возрастанию", "исправление", "debug", "task_167", "Упорядочить список чисел.", "sort_order; collection_iteration", "medium"),
    ("pas_168", "Сортировка чисел по убыванию", "перевод_программы", "implement", "task_168", "Вывести список в обратном порядке сортировки.", "sort_order; collection_iteration", "hard"),
    ("pas_169", "Сортировка строк", "сборка_программы", "assemble", "task_169", "Упорядочить имена по алфавиту.", "sort_order; collection_iteration", "easy"),
    ("pas_170", "Сортировка товаров по цене", "исправление", "debug", "task_170", "Упорядочить товары по числовому полю.", "sort_order; collection_iteration", "medium"),
    ("pas_171", "Сортировка студентов по баллу", "перевод_программы", "implement", "task_171", "Вывести рейтинг.", "sort_order; collection_iteration", "hard"),
    ("pas_172", "Ручная сортировка пузырьком", "сборка_программы", "assemble", "task_172", "Реализовать обмен соседних элементов.", "sort_order; collection_iteration", "easy"),
    ("pas_173", "Сортировка с условием", "исправление", "debug", "task_173", "Сначала отфильтровать, потом отсортировать.", "sort_order; collection_iteration", "medium"),
    ("pas_174", "Найти топ-3 значения", "перевод_программы", "implement", "task_174", "Отсортировать и вывести три лучших.", "sort_order; collection_iteration", "hard"),
    ("pas_175", "Сортировка по длине строки", "сборка_программы", "assemble", "task_175", "Упорядочить слова по длине.", "sort_order; collection_iteration", "easy"),
    ("pas_176", "Проверочная: таблица лидеров", "исправление", "debug", "task_176", "Отсортировать игроков по очкам и вывести топ.", "sort_order; collection_iteration", "medium"),
])

# 14. Ключ-значение и записи (12)
_extend("records", [
    ("pas_177", "Хранить цену по коду товара", "перевод_программы", "implement", "task_177", "По коду вывести цену.", "key_value_map; search_find; indexed_sequence", "hard"),
    ("pas_178", "Телефонная книга", "сборка_программы", "assemble", "task_178", "По имени найти номер.", "key_value_map; search_find; indexed_sequence", "easy"),
    ("pas_179", "Словарь оценок", "исправление", "debug", "task_179", "По имени студента вывести оценку.", "key_value_map; search_find; indexed_sequence", "medium"),
    ("pas_180", "Подсчет повторов слов", "перевод_программы", "implement", "task_180", "Посчитать частоту каждого слова.", "key_value_map; search_find; indexed_sequence", "hard"),
    ("pas_181", "Запись товара", "сборка_программы", "assemble", "task_181", "Хранить название, цену и количество.", "key_value_map; search_find; indexed_sequence", "easy"),
    ("pas_182", "Массив записей товаров", "исправление", "debug", "task_182", "Найти самый дорогой товар.", "key_value_map; search_find; indexed_sequence", "medium"),
    ("pas_183", "Массив записей студентов", "перевод_программы", "implement", "task_183", "Найти студента с лучшим баллом.", "key_value_map; search_find; indexed_sequence", "hard"),
    ("pas_184", "Поиск записи по id", "сборка_программы", "assemble", "task_184", "Найти объект по идентификатору.", "key_value_map; search_find; indexed_sequence", "easy"),
    ("pas_185", "Обновление значения по ключу", "исправление", "debug", "task_185", "Изменить количество товара на складе.", "key_value_map; search_find; indexed_sequence", "medium"),
    ("pas_186", "Проверка существования ключа", "перевод_программы", "implement", "task_186", "Вывести значение или сообщение об ошибке.", "key_value_map; search_find; indexed_sequence", "hard"),
    ("pas_187", "Сводка по категориям", "сборка_программы", "assemble", "task_187", "Накопить суммы по категориям.", "key_value_map; search_find; indexed_sequence", "easy"),
    ("pas_188", "Проверочная: склад товаров", "исправление", "debug", "task_188", "Хранить товары, искать по коду и обновлять остаток.", "key_value_map; search_find; indexed_sequence", "medium"),
])

# 15. Файлы (10)
_extend("files", [
    ("pas_189", "Прочитать файл строк", "перевод_программы", "implement", "task_189", "Вывести все строки файла.", "file_read; file_write; collection_iteration", "hard"),
    ("pas_190", "Посчитать строки файла", "сборка_программы", "assemble", "task_190", "Вывести количество строк.", "file_read; file_write; collection_iteration", "easy"),
    ("pas_191", "Найти строку в файле", "исправление", "debug", "task_191", "Определить наличие текста.", "file_read; file_write; collection_iteration", "medium"),
    ("pas_192", "Посчитать числа из файла", "перевод_программы", "implement", "task_192", "Прочитать числа и вывести сумму.", "file_read; file_write; collection_iteration", "hard"),
    ("pas_193", "Записать результат в файл", "сборка_программы", "assemble", "task_193", "Сохранить вычисленный ответ.", "file_read; file_write; collection_iteration", "easy"),
    ("pas_194", "Скопировать файл", "исправление", "debug", "task_194", "Прочитать один файл и записать в другой.", "file_read; file_write; collection_iteration", "medium"),
    ("pas_195", "Фильтровать файл", "перевод_программы", "implement", "task_195", "Записать только подходящие строки.", "file_read; file_write; collection_iteration", "hard"),
    ("pas_196", "Обработать журнал событий", "сборка_программы", "assemble", "task_196", "Посчитать события нужного типа.", "file_read; file_write; collection_iteration", "easy"),
    ("pas_197", "Таблица оценок из файла", "исправление", "debug", "task_197", "Прочитать оценки и найти среднюю.", "file_read; file_write; collection_iteration", "medium"),
    ("pas_198", "Проверочная: отчет по логам", "перевод_программы", "implement", "task_198", "Прочитать лог, отфильтровать ошибки и записать отчет.", "file_read; file_write; collection_iteration", "hard"),
])

# 16. Модули (8)
_extend("units", [
    ("pas_199", "Подключить математический модуль", "сборка_программы", "assemble", "task_199", "Использовать функцию из подключаемого модуля.", "import_dependency; module_namespace; symbol_visibility", "easy"),
    ("pas_200", "Вынести функцию в модуль", "исправление", "debug", "task_200", "Основная программа вызывает внешнюю функцию.", "import_dependency; module_namespace; symbol_visibility", "medium"),
    ("pas_201", "Разделить код на два файла", "перевод_программы", "implement", "task_201", "Логика находится отдельно от запуска.", "import_dependency; module_namespace; symbol_visibility", "hard"),
    ("pas_202", "Скрыть вспомогательную функцию", "сборка_программы", "assemble", "task_202", "Публичной оставить только основную функцию.", "import_dependency; module_namespace; symbol_visibility", "easy"),
    ("pas_203", "Модуль работы со строками", "исправление", "debug", "task_203", "Вынести проверку строки в отдельный модуль.", "import_dependency; module_namespace; symbol_visibility", "medium"),
    ("pas_204", "Модуль расчета скидок", "перевод_программы", "implement", "task_204", "Основная программа вызывает расчет из модуля.", "import_dependency; module_namespace; symbol_visibility", "hard"),
    ("pas_205", "Модуль статистики массива", "сборка_программы", "assemble", "task_205", "Использовать функции суммы и максимума.", "import_dependency; module_namespace; symbol_visibility", "easy"),
    ("pas_206", "Проверочная: мини-библиотека функций", "исправление", "debug", "task_206", "Собрать несколько функций в модуль и вызвать их из программы.", "import_dependency; module_namespace; symbol_visibility", "medium"),
])

# 17. Структуры данных (15)
_extend("data_structures", [
    ("pas_207", "Стек действий", "перевод_программы", "implement", "task_207", "Добавлять действия и отменять последнее.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "hard"),
    ("pas_208", "Очередь клиентов", "сборка_программы", "assemble", "task_208", "Добавить клиента и обработать первого.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "easy"),
    ("pas_209", "Проверка скобок стеком", "исправление", "debug", "task_209", "Определить корректность скобочной строки.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "medium"),
    ("pas_210", "Очередь печати", "перевод_программы", "implement", "task_210", "Обрабатывать задания по порядку.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "hard"),
    ("pas_211", "Связный список: добавление", "сборка_программы", "assemble", "task_211", "Добавить узел в начало списка.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "easy"),
    ("pas_212", "Связный список: поиск", "исправление", "debug", "task_212", "Найти значение в цепочке узлов.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "medium"),
    ("pas_213", "Связный список: удаление", "перевод_программы", "implement", "task_213", "Удалить первый подходящий узел.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "hard"),
    ("pas_214", "Дерево: создать узел", "сборка_программы", "assemble", "task_214", "Хранить значение и ссылки на потомков.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "easy"),
    ("pas_215", "Дерево: подсчет узлов", "исправление", "debug", "task_215", "Рекурсивно посчитать узлы.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "medium"),
    ("pas_216", "Дерево: поиск значения", "перевод_программы", "implement", "task_216", "Найти значение обходом дерева.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "hard"),
    ("pas_217", "Граф матрицей смежности", "сборка_программы", "assemble", "task_217", "Сохранить связи между вершинами.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "easy"),
    ("pas_218", "Граф списком ребер", "исправление", "debug", "task_218", "Хранить пары вершин.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "medium"),
    ("pas_219", "Подсчитать степень вершины", "перевод_программы", "implement", "task_219", "Определить количество связей.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "hard"),
    ("pas_220", "Найти соседей вершины", "сборка_программы", "assemble", "task_220", "Вывести все связанные вершины.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "easy"),
    ("pas_221", "Проверочная: маршрут по карте", "исправление", "debug", "task_221", "Хранить граф городов и проверить наличие дороги.", "stack_queue; linked_node; tree_hierarchy; graph_edges", "medium"),
])

# 18. Идиоматичная обработка данных (15)
_extend("functional", [
    ("pas_222", "Пронумеровать список студентов", "перевод_программы", "implement", "task_222", "Вывести номер и имя каждого студента.", "filter_select; fold_aggregate", "hard"),
    ("pas_223", "Сумма положительных элементов", "сборка_программы", "assemble", "task_223", "Найти сумму положительных значений идиоматичным способом.", "filter_select; fold_aggregate", "easy"),
    ("pas_224", "Все четные элементы", "исправление", "debug", "task_224", "Получить список четных элементов.", "filter_select; fold_aggregate", "medium"),
    ("pas_225", "Преобразовать температуры", "перевод_программы", "implement", "task_225", "Преобразовать список температур.", "filter_select; fold_aggregate", "hard"),
    ("pas_226", "Отфильтровать совершеннолетних", "сборка_программы", "assemble", "task_226", "Оставить пользователей старше 18.", "filter_select; fold_aggregate", "easy"),
    ("pas_227", "Получить список имен", "исправление", "debug", "task_227", "Из списка студентов получить только имена.", "filter_select; fold_aggregate", "medium"),
    ("pas_228", "Найти максимальную цену", "перевод_программы", "implement", "task_228", "Найти максимальное поле цены.", "filter_select; fold_aggregate", "hard"),
    ("pas_229", "Подсчитать уникальные слова", "сборка_программы", "assemble", "task_229", "Получить количество разных слов.", "filter_select; fold_aggregate", "easy"),
    ("pas_230", "Построить рейтинг игроков", "исправление", "debug", "task_230", "Отсортировать и пронумеровать игроков.", "filter_select; fold_aggregate", "medium"),
    ("pas_231", "Отсортировать товары по цене", "перевод_программы", "implement", "task_231", "Использовать язык-специфичный способ сортировки.", "filter_select; fold_aggregate", "hard"),
    ("pas_232", "Найти популярный товар", "сборка_программы", "assemble", "task_232", "Посчитать частоты и выбрать максимум.", "filter_select; fold_aggregate", "easy"),
    ("pas_233", "Средний балл группы", "исправление", "debug", "task_233", "Посчитать среднее идиоматичным способом.", "filter_select; fold_aggregate", "medium"),
    ("pas_234", "Сгруппировать студентов по оценке", "перевод_программы", "implement", "task_234", "Разложить студентов по категориям.", "filter_select; fold_aggregate", "hard"),
    ("pas_235", "Сформировать отчет по заказам", "сборка_программы", "assemble", "task_235", "Отфильтровать, преобразовать и просуммировать заказы.", "filter_select; fold_aggregate", "easy"),
    ("pas_236", "Проверочная: аналитика магазина", "исправление", "debug", "task_236", "Собрать краткий отчет по заказам.", "filter_select; fold_aggregate", "medium"),
])

# 19. ООП: классы и объекты (14)
_extend("oop", [
    ("pas_237", "Класс товара", "перевод_программы", "implement", "task_237", "Создать тип с названием и ценой.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_238", "Создать объект товара", "сборка_программы", "assemble", "task_238", "Создать экземпляр и вывести поля.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_239", "Метод расчета цены", "исправление", "debug", "task_239", "Объект сам считает цену со скидкой.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_240", "Класс студента", "перевод_программы", "implement", "task_240", "Хранить имя и балл, метод возвращает статус.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_241", "Класс банковского счета", "сборка_программы", "assemble", "task_241", "Хранить баланс и выводить его.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_242", "Конструктор товара", "исправление", "debug", "task_242", "Инициализировать объект через конструктор.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_243", "Метод изменения состояния", "перевод_программы", "implement", "task_243", "Изменить поле объекта методом.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_244", "Несколько объектов", "сборка_программы", "assemble", "task_244", "Создать несколько объектов и сравнить их.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_245", "Класс прямоугольника", "исправление", "debug", "task_245", "Метод возвращает площадь.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_246", "Класс таймера", "перевод_программы", "implement", "task_246", "Хранить минуты и переводить в часы.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_247", "Класс заказа", "сборка_программы", "assemble", "task_247", "Хранить цену, количество и итог.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_248", "Класс пользователя", "исправление", "debug", "task_248", "Проверять доступ пользователя.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_249", "Класс книги", "перевод_программы", "implement", "task_249", "Хранить автора и название.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_250", "Проверочная: карточка товара", "сборка_программы", "assemble", "task_250", "Создать товар с методами вывода и расчета.", "class_type; object_instance; method_dispatch", "easy"),
])

# 20. ООП: состояние и коллекции объектов (10)
_extend("oop_state", [
    ("pas_251", "Список студентов", "исправление", "debug", "task_251", "Хранить несколько объектов студентов.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_252", "Найти лучшего студента", "перевод_программы", "implement", "task_252", "Найти объект с максимальным баллом.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_253", "Отсортировать товары", "сборка_программы", "assemble", "task_253", "Упорядочить объекты товаров по цене.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_254", "Фильтр активных пользователей", "исправление", "debug", "task_254", "Оставить только активных объектов.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_255", "Корзина объектов", "перевод_программы", "implement", "task_255", "Хранить товары и считать сумму.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_256", "Банковский счет: пополнение", "сборка_программы", "assemble", "task_256", "Метод увеличивает баланс.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_257", "Банковский счет: снятие", "исправление", "debug", "task_257", "Метод проверяет и уменьшает баланс.", "class_type; object_instance; method_dispatch", "medium"),
    ("pas_258", "Журнал заказов", "перевод_программы", "implement", "task_258", "Хранить список заказов и искать дорогие.", "class_type; object_instance; method_dispatch", "hard"),
    ("pas_259", "Каталог книг", "сборка_программы", "assemble", "task_259", "Искать книгу по названию.", "class_type; object_instance; method_dispatch", "easy"),
    ("pas_260", "Проверочная: мини-магазин", "исправление", "debug", "task_260", "Коллекция товаров с поиском, сортировкой и суммой.", "class_type; object_instance; method_dispatch", "medium"),
])

# 21. ООП: наследование, полиморфизм и итог (10)
_extend("oop_inherit", [
    ("pas_261", "Сотрудник и менеджер", "перевод_программы", "implement", "task_261", "Менеджер наследует сотрудника и имеет бонус.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "hard"),
    ("pas_262", "Транспорт и автомобиль", "сборка_программы", "assemble", "task_262", "Автомобиль расширяет общий транспорт.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "easy"),
    ("pas_263", "Животное и собака", "исправление", "debug", "task_263", "Переопределить метод звука.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "medium"),
    ("pas_264", "Фигура и прямоугольник", "перевод_программы", "implement", "task_264", "Общий метод площади реализован в потомке.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "hard"),
    ("pas_265", "Платеж и оплата картой", "сборка_программы", "assemble", "task_265", "Разные способы оплаты имеют общий интерфейс.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "easy"),
    ("pas_266", "Доставка разными способами", "исправление", "debug", "task_266", "Рассчитать стоимость доставки полиморфно.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "medium"),
    ("pas_267", "Список базового типа", "перевод_программы", "implement", "task_267", "Хранить разные объекты в одной коллекции.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "hard"),
    ("pas_268", "Переопределение вывода", "сборка_программы", "assemble", "task_268", "Каждый объект сам формирует описание.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "easy"),
    ("pas_269", "Интерфейс проверки", "исправление", "debug", "task_269", "Разные классы реализуют общий метод проверки.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "medium"),
    ("pas_270", "Проверочная: мини-система магазина", "перевод_программы", "implement", "task_270", "Товары, пользователи, заказы и разные способы доставки.", "class_type; object_instance; method_dispatch; inheritance_hierarchy", "hard"),
])

assert len(V4_TASKS) == V4_CORE_TASK_COUNT, f"Expected 270, got {len(V4_TASKS)}"
