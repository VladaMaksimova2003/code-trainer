"""Batch 5 (Phase 2) overrides: task_068 count equal x, task_076 lookup by id."""

T068_TITLE = "Подсчёт элементов, равных x"
T068_DESC = (
    "В первой строке вводятся n и x. Затем вводятся n чисел по одному в строке. "
    "Подсчитайте количество элементов, равных x, и выведите результат."
)
# Curated from v128 corrections: fix n/x/data so outputs match count-equal-x (not search-index).
T068_TESTS = [
    {"name": "Тест 1", "inputs": "5 3\n1\n3\n5\n3\n7\n", "output": "2"},
    {"name": "Тест 2", "inputs": "4 7\n1\n2\n3\n4\n", "output": "0"},
    {"name": "Тест 3", "inputs": "3 0\n0\n0\n0\n", "output": "3"},
    {"name": "Тест 4", "inputs": "4 2\n2\n2\n1\n3\n", "output": "2"},
]

T068_REF = {
    "pascal": """var n, i, x, v, count: integer;
begin
  readln(n, x);
  count := 0;

  for i := 1 to n do
  begin
    readln(v);
    if v = x then
      count := count + 1;
  end;

  writeln(count);
end.""",
    "python": """n, x = map(int, input().split())
count = 0

for _ in range(n):
    v = int(input())
    if v == x:
        count += 1

print(count)""",
    "cpp": """#include <iostream>

int main() {
    int n, x, v, count = 0;
    std::cin >> n >> x;

    for (int i = 0; i < n; i++) {
        std::cin >> v;
        if (v == x) {
            count++;
        }
    }

    std::cout << count;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();
        int n = int.Parse(first[0]);
        int x = int.Parse(first[1]);
        int count = 0;

        for (int i = 0; i < n; i++) {
            int v = int.Parse(Console.ReadLine());
            if (v == x) {
                count++;
            }
        }

        Console.WriteLine(count);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int x = sc.nextInt();
        int count = 0;

        for (int i = 0; i < n; i++) {
            int v = sc.nextInt();
            if (v == x) {
                count++;
            }
        }

        System.out.println(count);
    }
}""",
}

T068_BUGGY = {
    "pascal": """var n, i, x, v, count: integer;
begin
  readln(n, x);
  count := 1;

  for i := 1 to n do
  begin
    readln(v);
    if v = x then
      count := count + 1;
  end;

  writeln(count);
end.""",
    "python": """n, x = map(int, input().split())
count = 1

for _ in range(n):
    v = int(input())
    if v == x:
        count += 1

print(count)""",
    "cpp": """#include <iostream>

int main() {
    int n, x, v, count = 1;
    std::cin >> n >> x;

    for (int i = 0; i < n; i++) {
        std::cin >> v;
        if (v == x) {
            count++;
        }
    }

    std::cout << count;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();
        int n = int.Parse(first[0]);
        int x = int.Parse(first[1]);
        int count = 1;

        for (int i = 0; i < n; i++) {
            int v = int.Parse(Console.ReadLine());
            if (v == x) {
                count++;
            }
        }

        Console.WriteLine(count);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int x = sc.nextInt();
        int count = 1;

        for (int i = 0; i < n; i++) {
            int v = sc.nextInt();
            if (v == x) {
                count++;
            }
        }

        System.out.println(count);
    }
}""",
}

T068_HINTS = [
    "Сначала прочитайте n и x из первой строки.",
    "Пройдите по n числам и увеличивайте счётчик при совпадении с x.",
    "Выведите только итоговое количество.",
]
T068_POST = (
    "Нужно прочитать n и x, затем n чисел и посчитать, сколько из них равны x. "
    "Типичные ошибки: счётчик не обнуляется (начинают с 1), сравнивают с другим значением "
    "или путают задачу с поиском индекса."
)

T076_TITLE = "Поиск value по id"
T076_DESC = (
    "Вводится n, затем n строк формата id name grade, затем id для поиска. "
    "Если id найден — выведите name и grade через пробел, иначе выведите not found."
)
T076_TESTS = [
    {"name": "Тест 1", "inputs": "2\ns1 Ivan 5\ns2 Olya 4\ns1\n", "output": "Ivan 5"},
    {"name": "Тест 2", "inputs": "1\nx Ann 10\nx\n", "output": "Ann 10"},
    {"name": "Тест 3", "inputs": "1\nx Ann 10\ny\n", "output": "not found"},
    {"name": "Тест 4", "inputs": "1\nid1 Bob 7\nid1\n", "output": "Bob 7"},
]

T076_REF = {
    "pascal": """var n, i: integer;
    id, query: string;
    ids, names: array[1..100] of string;
    grades: array[1..100] of integer;
    found: boolean;
begin
  readln(n);

  for i := 1 to n do
    readln(ids[i], names[i], grades[i]);

  readln(query);
  found := false;

  for i := 1 to n do
    if ids[i] = query then
    begin
      writeln(names[i], ' ', grades[i]);
      found := true;
      break;
    end;

  if not found then
    writeln('not found');
end.""",
    "python": """n = int(input())
students = {}

for _ in range(n):
    student_id, name, grade = input().split()
    students[student_id] = (name, grade)

query = input()

if query in students:
    name, grade = students[query]
    print(name, grade)
else:
    print('not found')""",
    "cpp": """#include <iostream>
#include <map>
#include <string>

struct Student {
    std::string name;
    int grade;
};

int main() {
    int n;
    std::cin >> n;

    std::map<std::string, Student> students;

    for (int i = 0; i < n; i++) {
        std::string id;
        Student st;

        std::cin >> id >> st.name >> st.grade;
        students[id] = st;
    }

    std::string query;
    std::cin >> query;

    if (students.count(query)) {
        std::cout << students[query].name << ' ' << students[query].grade;
    } else {
        std::cout << "not found";
    }

    return 0;
}""",
    "csharp": """using System;
using System.Collections.Generic;

class Student {
    public string Name;
    public int Grade;
}

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Dictionary<string, Student> students = new Dictionary<string, Student>();

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            students[p[0]] = new Student {
                Name = p[1],
                Grade = int.Parse(p[2])
            };
        }

        string query = Console.ReadLine();

        if (students.ContainsKey(query)) {
            Console.WriteLine($"{students[query].Name} {students[query].Grade}");
        } else {
            Console.WriteLine("not found");
        }
    }
}""",
    "java": """import java.util.*;

class Student {
    String name;
    int grade;

    Student(String name, int grade) {
        this.name = name;
        this.grade = grade;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        HashMap<String, Student> students = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String id = sc.next();
            String name = sc.next();
            int grade = sc.nextInt();

            students.put(id, new Student(name, grade));
        }

        String query = sc.next();

        if (students.containsKey(query)) {
            Student st = students.get(query);
            System.out.println(st.name + " " + st.grade);
        } else {
            System.out.println("not found");
        }
    }
}""",
}

T076_BUGGY = {
    "pascal": """var n, i: integer;
    id, query, name: string;
    grade: integer;
    found: boolean;
begin
  readln(n);

  for i := 1 to n do
    readln(id, name, grade);

  readln(query);
  found := false;

  for i := 1 to n do
    if name = query then
    begin
      writeln(name, ' ', grade);
      found := true;
    end;

  if not found then
    writeln('not found');
end.""",
    "python": """n = int(input())
students = {}

for _ in range(n):
    student_id, name, grade = input().split()
    students[student_id] = (name, grade)

query = input()

for sid, (name, grade) in students.items():
    if name == query:
        print(name, grade)
        break
else:
    print('not found')""",
    "cpp": """#include <iostream>
#include <map>
#include <string>

struct Student {
    std::string name;
    int grade;
};

int main() {
    int n;
    std::cin >> n;

    std::map<std::string, Student> students;

    for (int i = 0; i < n; i++) {
        std::string id;
        Student st;

        std::cin >> id >> st.name >> st.grade;
        students[id] = st;
    }

    std::string query;
    std::cin >> query;

    for (const auto& pair : students) {
        if (pair.second.name == query) {
            std::cout << pair.second.name << ' ' << pair.second.grade;
            return 0;
        }
    }

    std::cout << "not found";
    return 0;
}""",
    "csharp": """using System;
using System.Collections.Generic;

class Student {
    public string Name;
    public int Grade;
}

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Dictionary<string, Student> students = new Dictionary<string, Student>();

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            students[p[0]] = new Student {
                Name = p[1],
                Grade = int.Parse(p[2])
            };
        }

        string query = Console.ReadLine();

        foreach (var pair in students) {
            if (pair.Value.Name == query) {
                Console.WriteLine($"{pair.Value.Name} {pair.Value.Grade}");
                return;
            }
        }

        Console.WriteLine("not found");
    }
}""",
    "java": """import java.util.*;

class Student {
    String name;
    int grade;

    Student(String name, int grade) {
        this.name = name;
        this.grade = grade;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        HashMap<String, Student> students = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String id = sc.next();
            String name = sc.next();
            int grade = sc.nextInt();

            students.put(id, new Student(name, grade));
        }

        String query = sc.next();

        for (Student st : students.values()) {
            if (st.name.equals(query)) {
                System.out.println(st.name + " " + st.grade);
                return;
            }
        }

        System.out.println("not found");
    }
}""",
}

T076_HINTS = [
    "Сначала сохраните все пары id → (name, grade).",
    "Ищите по id из последней строки, а не по имени.",
    "Если id не найден — выведите not found.",
]
T076_POST = (
    "Нужно построить индекс по id и выполнить поиск по ключу. "
    "Типичная ошибка — сравнивать запрос с name вместо id (map_key_missing / wrong lookup key)."
)

BATCH5_OVERRIDES = {
    "task_068": {
        "title": T068_TITLE,
        "description": T068_DESC,
        "ref": T068_REF,
        "buggy": T068_BUGGY,
        "tests": T068_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "counted_loop",
            "filter_select",
        ],
        "hints": T068_HINTS,
        "post_solve": T068_POST,
        "canon_notes": (
            "I/O: первая строка «n x», далее n чисел. Тесты v128 corrections переписаны: "
            "старые expected outputs соответствовали поиску индекса (task_002), не count-equal-x. "
            "Buggy: count := 1 / off-by-one init."
        ),
        "failing_test_fix": (
            "DB T1–T4: несовместимы с count-логикой (T1 n=5 при 6 числах; T2 x=3 встречается в массиве; "
            "T3 count(0)≠3 при 1,2,3; T4 expected 3 при двух двойках). Canon заменяет на 4 согласованных теста."
        ),
        "conflicts": [
            "meta/raw_title «Фильтр заказов по статусу» vs catalog «Подсчёт элементов, равных x»",
            "ch9_user_codes/task_068.py — код фильтра paid-заказов (v128_test_suites_data)",
            "v128_test_suites_corrections outputs — артефакт linear-search, не count",
            "DB python — код фильтра положительных (postive filter), 0/4",
        ],
    },
    "task_076": {
        "title": T076_TITLE,
        "description": T076_DESC,
        "ref": T076_REF,
        "buggy": T076_BUGGY,
        "tests": T076_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "key_value_map",
        ],
        "hints": T076_HINTS,
        "post_solve": T076_POST,
        "canon_notes": (
            "Формат id name grade (не abstract id/value). Убрать placeholder T5 (3\\n1\\n2\\n3\\n→6). "
            "Buggy: lookup по name вместо id. Pitfall: map_key_missing."
        ),
        "failing_test_fix": (
            "T1–T4 v128 совпадают с maps_ch10_user_payload. T5 placeholder удаляется. "
            "DB python — word-frequency код, 0/5."
        ),
        "conflicts": [
            "catalog goal «value по id» vs тесты «id name grade» (согласовано в canon description)",
            "meta/raw_title «Индекс студентов по ID» vs catalog title «Поиск value по id»",
            "DB description краткое «id и value» без формата строк",
        ],
    },
}
