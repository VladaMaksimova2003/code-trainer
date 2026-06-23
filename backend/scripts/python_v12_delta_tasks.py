"""Python Course v1.2 delta — new slots on top of v1 baseline."""

from __future__ import annotations

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

V12_DELTA_CORE_COUNT = 33

V12_DELTA_TASKS: list[TaskRow] = []


def _extend(chapter: str, rows: list[tuple]) -> None:
    for row in rows:
        padded = row + ("",) * (10 - len(row))
        V12_DELTA_TASKS.append((padded[0], chapter, *padded[1:9]))  # type: ignore[misc]


# OOP property mirrors (Pascal v3.2)
_extend("oop", [
    ("pyo_19", "Property read-only", "перевод_фрагмента", "translate", "py_pyo_19",
     "Запишите @property только для чтения", "property", "medium"),
    ("pyo_20", "Property write-only", "исправление", "debug", "py_pyo_20",
     "Исправьте setter-only property", "property", "medium"),
    ("pyo_21", "Indexed property", "сборка_фрагмента", "assemble", "py_pyo_21",
     "Соберите __getitem__/__setitem__ или property с индексом", "property", "hard"),
])

# Pitfalls — Python-side slots (pypit_25 mirrors pit_20; 23/24 python-only depth)
_extend("python_pitfalls", [
    ("pypit_23", "Truthiness и ноль", "исправление", "debug", "py_pypit_23",
     "Исправьте условие, которое неверно обрабатывает ноль", "truthiness", "medium"),
    ("pypit_24", "Shared mutable ref", "исправление", "debug", "py_pypit_24",
     "Исправьте присваивание, создающее две переменные на один список", "reference", "medium"),
    ("pypit_25", "Регистр идентификатора", "поиск_ошибки", "debug", "py_pypit_25",
     "Найдите обращение к имени с неверным регистром", "identifier", "easy"),
])

# Comprehensions (+2)
_extend("comprehensions", [
    ("pycmp_10", "Walrus в comprehension", "исправление", "debug", "py_pycmp_10",
     "Используйте := в comprehension для переиспользования выражения", "walrus", "medium"),
    ("pycmp_11", "Generator pipeline", "сборка_фрагмента", "assemble", "py_pycmp_11",
     "Соберите цепочку generator expression и sum/any", "generator", "hard"),
])

# advanced_python (+22)
_extend("advanced_python", [
    ("pyadv_01", "Decorator + wrapper", "сборка_фрагмента", "assemble", "py_pyadv_01",
     "Соберите @decorator и wrapper с сохранением metadata", "decorator", "hard"),
    ("pyadv_02", "Forgot @wraps", "исправление", "debug", "py_pyadv_02",
     "Добавьте functools.wraps в decorator", "decorator", "medium"),
    ("pyadv_03", "Parameterized decorator", "перевод_фрагмента", "translate", "py_pyadv_03",
     "Запишите decorator factory с параметром", "decorator", "hard"),
    ("pyadv_04", "Decorator order", "выбор_фрагмента", "implement", "py_pyadv_04",
     "Выберите корректный порядок stacked decorators", "decorator", "hard"),
    ("pyadv_05", "__enter__/__exit__", "сборка_фрагмента", "assemble", "py_pyadv_05",
     "Соберите context manager class", "context", "hard"),
    ("pyadv_06", "contextlib.suppress", "исправление", "debug", "py_pyadv_06",
     "Исправьте подавление ожидаемого исключения", "context", "medium"),
    ("pyadv_07", "@contextmanager", "сборка_фрагмента", "assemble", "py_pyadv_07",
     "Соберите @contextmanager генератор", "context", "hard"),
    ("pyadv_08", "list[int] annotations", "перевод_фрагмента", "translate", "py_pyadv_08",
     "Запишите аннотации list[int], Optional", "typing", "medium"),
    ("pyadv_09", "Wrong Union", "исправление", "debug", "py_pyadv_09",
     "Исправьте Union/Optional в аннотациях", "typing", "medium"),
    ("pyadv_10", "TypedDict / Literal", "перевод_фрагмента", "translate", "py_pyadv_10",
     "Запишите TypedDict или Literal", "typing", "hard"),
    ("pyadv_11", "Callable annotation", "исправление", "debug", "py_pyadv_11",
     "Исправьте Callable[[int], str] в сигнатуре", "typing", "medium"),
    ("pyadv_12", "Generic class", "сборка_фрагмента", "assemble", "py_pyadv_12",
     "Соберите class Stack[T] с TypeVar", "typing", "hard"),
    ("pyadv_13", "@dataclass fields", "сборка_фрагмента", "assemble", "py_pyadv_13",
     "Соберите @dataclass с полями и defaults", "dataclass", "medium"),
    ("pyadv_14", "dataclass frozen", "исправление", "debug", "py_pyadv_14",
     "Исправьте мутацию frozen dataclass", "dataclass", "medium"),
    ("pyadv_15", "field(default_factory)", "исправление", "debug", "py_pyadv_15",
     "Замените mutable default на default_factory", "dataclass", "medium"),
    ("pyadv_16", "dataclass vs attrs", "выбор_фрагмента", "implement", "py_pyadv_16",
     "Выберите dataclass для DTO без boilerplate", "dataclass", "easy"),
    ("pyadv_17", "yield generator", "исправление", "debug", "py_pyadv_17",
     "Добавьте yield для ленивой последовательности", "generator", "medium"),
    ("pyadv_18", "yield from", "перевод_фрагмента", "translate", "py_pyadv_18",
     "Запишите yield from для делегирования", "generator", "medium"),
    ("pyadv_19", "Generator send/throw", "выбор_фрагмента", "implement", "py_pyadv_19",
     "Выберите корректное использование .send()", "generator", "hard"),
    ("pyadv_20", "Forgot await", "исправление", "debug", "py_pyadv_20",
     "Добавьте await при вызове coroutine", "async", "medium"),
    ("pyadv_21", "async def + await", "сборка_фрагмента", "assemble", "py_pyadv_21",
     "Соберите async def и await asyncio.sleep", "async", "hard"),
    ("pyadv_22", "asyncio.gather", "исправление", "debug", "py_pyadv_22",
     "Исправьте параллельный запуск coroutines через gather", "async", "hard"),
])

# typing_diagnostics (+3)
_extend("typing_diagnostics", [
    ("pytd_01", "Optional vs None default", "исправление", "debug", "py_pytd_01",
     "Исправьте аннотацию Optional без default None", "typing", "medium"),
    ("pytd_02", "list vs List legacy", "исправление", "debug", "py_pytd_02",
     "Приведите аннотации к современному list[int]", "typing", "easy"),
    ("pytd_03", "Incompatible return type", "выбор_фрагмента", "implement", "py_pytd_03",
     "Выберите сигнатуру, согласованную с mypy-style проверкой", "typing", "medium"),
])

V12_CHAPTER_TITLES = {
    "advanced_python": "22. Advanced Python",
    "typing_diagnostics": "23. Typing diagnostics",
}
