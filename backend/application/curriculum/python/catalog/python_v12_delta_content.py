"""Seed payloads for Python v1.2 delta slots."""

from __future__ import annotations

V12_REFERENCE: dict[str, str] = {
    "pyo_19": (
        "class Box:\n"
        "    def __init__(self, name: str):\n"
        "        self._name = name\n"
        "    @property\n"
        "    def name(self) -> str:\n"
        "        return self._name"
    ),
    "pyo_20": (
        "class Box:\n"
        "    def __init__(self):\n"
        "        self._v = 0\n"
        "    @property\n"
        "    def value(self) -> None:\n"
        "        pass\n"
        "    @value.setter\n"
        "    def value(self, v: int) -> None:\n"
        "        self._v = v"
    ),
    "pyo_21": (
        "class Items:\n"
        "    def __init__(self):\n"
        "        self._data: list[int] = []\n"
        "    def __getitem__(self, i: int) -> int:\n"
        "        return self._data[i]\n"
        "    def __setitem__(self, i: int, v: int) -> None:\n"
        "        self._data[i] = v"
    ),
    "pypit_23": "if v != 0:\n    print('yes')\nelse:\n    print('no')",
    "pypit_24": "a = [0, 0, 0]\nb = [0, 0, 0]\na[0] = 1\nprint(b[0])",
    "pypit_25": "count = 1\nprint(Count)",
    "pydg_14": "items = [1, 2, 3]\nprint(items[3])",
    "pydg_15": "def f():\n    x = 1\n print(x)",
    "pyx_05": (
        "class EMy(Exception):\n"
        "    pass\n\n"
        "raise EMy('custom')"
    ),
    "pyx_12": (
        "try:\n"
        "    open('missing.txt')\n"
        "except FileNotFoundError:\n"
        "    print('no file')"
    ),
    "pycmp_10": "vals = [x * 2 for x in range(5) if (n := x % 2) == 0]",
    "pycmp_11": "total = sum(x * x for x in range(10) if x % 2 == 0)",
}

V12_DEBUG_STARTER: dict[str, str] = {
    "pyo_20": (
        "class Box:\n"
        "    @property\n"
        "    def value(self):\n"
        "        return self._v\n"
    ),
    "pypit_23": "v = 0\nif v:\n    print('yes')\nelse:\n    print('no')",
    "pypit_24": "a = []\nb = a\na.append(1)\nprint(b[0])",
    "pypit_25": "count = 1\nprint(Count)",
    "pydg_14": "items = [1, 2, 3]\nprint(items[3])",
    "pydg_15": "def f():\n    x = 1\n print(x)",
    "pyx_12": (
        "path = 'missing.txt'\nf = open(path)\nprint('ok')"
    ),
    "pycmp_10": "vals = [x * 2 for x in range(5) if x % 2 == 0]",
    "pyadv_02": (
        "def deco(fn):\n"
        "    def wrapper(*a, **k):\n"
        "        return fn(*a, **k)\n"
        "    return wrapper"
    ),
    "pyadv_06": (
        "from contextlib import suppress\n"
        "with suppress(ValueError):\n"
        "    int('x')\n"
        "    raise RuntimeError('lost')"
    ),
    "pyadv_09": "def f(x: int | str) -> int:\n    return x",
    "pyadv_14": (
        "from dataclasses import dataclass\n"
        "@dataclass(frozen=True)\n"
        "class P:\n"
        "    x: int\n"
        "p = P(1)\n"
        "p.x = 2"
    ),
    "pyadv_15": (
        "from dataclasses import dataclass, field\n"
        "@dataclass\n"
        "class P:\n"
        "    items: list = []"
    ),
    "pyadv_17": "def gen():\n    for i in range(3):\n        return i",
    "pyadv_20": (
        "import asyncio\n"
        "async def main():\n"
        "    asyncio.sleep(1)\n"
        "asyncio.run(main())"
    ),
    "pyadv_22": (
        "import asyncio\n"
        "async def work():\n"
        "    await asyncio.sleep(0)\n"
        "    return 1\n"
        "async def main():\n"
        "    await work()\n"
        "    await work()"
    ),
    "pytd_01": "def f(x: int | None) -> int:\n    return x or 0",
    "pytd_02": "from typing import List\ndef f(a: List[int]) -> List[int]:\n    return a",
}

V12_TEST_CASES: dict[str, list[dict[str, str]]] = {
    "pyo_19": [],
    "pyo_20": [],
    "pyo_21": [],
    "pypit_23": [{"inputs": "", "output": "no"}],
    "pypit_24": [{"inputs": "", "output": "0"}],
    "pypit_25": [{"inputs": "", "output": "1"}],
    "pydg_14": [{"inputs": "", "output": "3"}],
    "pydg_15": [{"inputs": "", "output": "1"}],
    "pyx_05": [],
    "pyx_12": [{"inputs": "", "output": "no file"}],
    "pycmp_10": [{"inputs": "", "output": "[0, 4, 8]"}],
    "pycmp_11": [{"inputs": "", "output": "120"}],
    "pyadv_01": [],
    "pyadv_05": [],
    "pyadv_07": [],
    "pyadv_13": [],
    "pyadv_21": [],
    "pytd_01": [{"inputs": "", "output": "0"}],
    "pytd_02": [{"inputs": "", "output": "[]"}],
}

V12_ASSEMBLY: dict[str, tuple[str, str, list[str], list[int], list[dict[str, str]]]] = {
    "pyo_21": (
        "class Items:\n    def __getitem__(self, i): return self._data[i]",
        "___",
        ["class Items:", "    def __getitem__(self, i): return self._data[i]"],
        [0, 1],
        [],
    ),
    "pyadv_01": (
        "def deco(fn):\n    @wraps(fn)\n    def wrapper(*a, **k):\n        return fn(*a, **k)\n    return wrapper",
        "___",
        ["def deco(fn):", "    @wraps(fn)", "    def wrapper(*a, **k):", "        return fn(*a, **k)", "    return wrapper"],
        [0, 1, 2, 3, 4],
        [],
    ),
    "pyadv_05": (
        "class CM:\n    def __enter__(self): return self\n    def __exit__(self, *a): return False",
        "___",
        ["class CM:", "    def __enter__(self): return self", "    def __exit__(self, *a): return False"],
        [0, 1, 2],
        [],
    ),
    "pyadv_07": (
        "from contextlib import contextmanager\n@contextmanager\ndef cm():\n    yield resource",
        "___",
        ["from contextlib import contextmanager", "@contextmanager", "def cm():", "    yield resource"],
        [0, 1, 2, 3],
        [],
    ),
    "pyadv_12": (
        "from typing import TypeVar, Generic\nT = TypeVar('T')\nclass Stack(Generic[T]):\n    def push(self, x: T) -> None: ...",
        "___",
        ["from typing import TypeVar, Generic", "T = TypeVar('T')", "class Stack(Generic[T]):", "    def push(self, x: T) -> None: ..."],
        [0, 1, 2, 3],
        [],
    ),
    "pyadv_13": (
        "from dataclasses import dataclass\n@dataclass\nclass User:\n    name: str\n    age: int = 0",
        "___",
        ["from dataclasses import dataclass", "@dataclass", "class User:", "    name: str", "    age: int = 0"],
        [0, 1, 2, 3, 4],
        [],
    ),
    "pyadv_21": (
        "import asyncio\nasync def main():\n    await asyncio.sleep(0.1)\nasyncio.run(main())",
        "___",
        ["import asyncio", "async def main():", "    await asyncio.sleep(0.1)", "asyncio.run(main())"],
        [0, 1, 2, 3],
        [],
    ),
    "pycmp_11": (
        "total = sum(x * x for x in range(10) if x % 2 == 0)",
        "___",
        ["total = sum(", "x * x for x in range(10) if x % 2 == 0", ")"],
        [0, 1, 2],
        [{"inputs": "", "output": "120"}],
    ),
}

V12_KNOWN_CODE: dict[str, tuple[str, str, str, str]] = {
    "pyo_19": (
        "property Name: string read FName;",
        "string getName() const { return _name; }",
        "String getName(){ return _name; }",
        "string Name => _name;",
    ),
    "pyo_20": (
        "property Value write F;",
        "void setValue(int v){ _v=v; }",
        "void setValue(int v){ _v=v; }",
        "void set Value(int v){ _v=v; }",
    ),
    "pyo_21": (
        "property Items[Index: integer]: integer read GetItem write SetItem;",
        "int& operator[](int i);",
        "int get(int i);",
        "int this[int i] => _items[i];",
    ),
}

V12_EXPECTED_CONCEPT_OVERRIDES: dict[str, list[str]] = {
    "pyo_19": ["class_type"],
    "pyo_20": ["class_type"],
    "pyo_21": ["class_type"],
    "pypit_23": ["assignment"],
    "pypit_24": ["dynamic_array"],
    "pypit_25": ["assignment"],
    "pydg_14": ["indexed_sequence"],
    "pydg_15": ["typed_declaration"],
    "pyadv_01": ["function_definition"],
    "pyadv_05": ["function_definition"],
    "pyadv_08": ["typed_declaration"],
    "pyadv_13": ["class_type"],
    "pyadv_17": ["function_definition"],
    "pyadv_20": ["function_definition"],
    "pytd_01": ["typed_declaration"],
    "pytd_02": ["typed_declaration"],
    "pytd_03": ["typed_declaration"],
    "pycmp_10": ["indexed_sequence"],
    "pycmp_11": ["indexed_sequence"],
}
