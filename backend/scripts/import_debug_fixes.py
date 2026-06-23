"""Idempotent importer of reconciled debug-task content into the live DB.

Source of truth for content lives in OVERRIDES below. Each entry is keyed by
curriculum slot pattern_id (NOT the DB primary key). For each task we set:
  - title / description (identity)
  - code_examples[lang]  -> the FIXED reference/source code
  - code_examples[buggy_lang] -> the BUGGY code the student must fix
  - test_cases           -> cleaned, profile-only tests (placeholders/foreign removed)
Format, pattern_id, chapter and other code_examples keys are preserved.

A FIXED reference is kept per task and validated (Python) against test_cases
before anything is written. Run with --apply to write; default is dry-run.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

import psycopg2

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

LANGS = ["pascal", "python", "cpp", "csharp", "java"]

# ----------------------------------------------------------------------------
# task_004 — Count strictly positive operations (filter_positive / AlgorithmDebug).
# Canon: description → v128 tests → curated logic (count init bug).
# ----------------------------------------------------------------------------
T004_TITLE = "Подсчёт положительных операций"
T004_DESC = (
    "Вводится количество операций и затем изменения баланса. "
    "Положительное число означает поступление денег, ноль и отрицательное число "
    "не считаются успешным пополнением. Нужно вывести количество положительных операций."
)
T004_TESTS = [
    {"name": "Тест 1", "inputs": "5\n100\n-20\n0\n50\n-1\n", "output": "2"},
    {"name": "Тест 2", "inputs": "3\n-5\n-1\n0\n", "output": "0"},
    {"name": "Тест 3", "inputs": "4\n1\n2\n3\n4\n", "output": "4"},
    {"name": "Тест 4", "inputs": "2\n0\n0\n", "output": "0"},
]
T004_REF = {
    "python": '''n = int(input())
count = 0
for _ in range(n):
    amount = int(input())
    if amount > 0:
        count += 1
print(count)''',
    "pascal": '''var n, i, amount, count: integer;
begin
  readln(n);
  count := 0;
  for i := 1 to n do
  begin
    readln(amount);
    if amount > 0 then count := count + 1;
  end;
  writeln(count);
end.''',
    "cpp": '''#include <iostream>

int main() {
    int n, amount, count = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> amount;
        if (amount > 0) count++;
    }
    std::cout << count;
    return 0;
}''',
    "csharp": '''using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int count = 0;
        for (int i = 0; i < n; i++) {
            int amount = int.Parse(Console.ReadLine());
            if (amount > 0) count++;
        }
        Console.WriteLine(count);
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int count = 0;
        for (int i = 0; i < n; i++) {
            int amount = sc.nextInt();
            if (amount > 0) count++;
        }
        System.out.println(count);
    }
}''',
}
T004_BUGGY = {
    "python": '''n = int(input())
count = 1
for _ in range(n):
    amount = int(input())
    if amount > 0:
        count += 1
print(count)''',
    "pascal": '''var n, i, amount, count: integer;
begin
  readln(n);
  count := 1;
  for i := 1 to n do
  begin
    readln(amount);
    if amount > 0 then count := count + 1;
  end;
  writeln(count);
end.''',
    "cpp": '''#include <iostream>

int main() {
    int n, amount, count = 1;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> amount;
        if (amount > 0) count++;
    }
    std::cout << count;
    return 0;
}''',
    "csharp": '''using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int count = 1;
        for (int i = 0; i < n; i++) {
            int amount = int.Parse(Console.ReadLine());
            if (amount > 0) count++;
        }
        Console.WriteLine(count);
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int count = 1;
        for (int i = 0; i < n; i++) {
            int amount = sc.nextInt();
            if (amount > 0) count++;
        }
        System.out.println(count);
    }
}''',
}

# ----------------------------------------------------------------------------
# task_007 — Count measurements >= 50 (threshold_count / AlgorithmDebug).
# ----------------------------------------------------------------------------
T007_TITLE = "Измерения не ниже порога"
T007_DESC = (
    "Вводится количество измерений и сами значения. "
    "Нужно посчитать, сколько измерений не меньше 50, и вывести это количество."
)
T007_TESTS = [
    {"name": "Тест 1", "inputs": "5\n40\n50\n60\n10\n70\n", "output": "3"},
    {"name": "Тест 2", "inputs": "3\n1\n2\n3\n", "output": "0"},
    {"name": "Тест 3", "inputs": "4\n50\n50\n49\n51\n", "output": "3"},
    {"name": "Тест 4", "inputs": "4\n50\n50\n50\n50\n", "output": "4"},
]
T007_REF = {
    "python": '''n = int(input())
count = 0
for _ in range(n):
    x = int(input())
    if x >= 50:
        count += 1
print(count)''',
    "pascal": '''var n, i, x, count: integer;
begin
  readln(n);
  count := 0;
  for i := 1 to n do
  begin
    readln(x);
    if x >= 50 then count := count + 1;
  end;
  writeln(count);
end.''',
    "cpp": '''#include <iostream>

int main() {
    int n, x, count = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> x;
        if (x >= 50) count++;
    }
    std::cout << count;
    return 0;
}''',
    "csharp": '''using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int count = 0;
        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x >= 50) count++;
        }
        Console.WriteLine(count);
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int count = 0;
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x >= 50) count++;
        }
        System.out.println(count);
    }
}''',
}
T007_BUGGY = {
    "python": '''n = int(input())
count = 0
for _ in range(n):
    x = int(input())
    if x > 50:
        count += 1
print(count)''',
    "pascal": '''var n, i, x, count: integer;
begin
  readln(n);
  count := 0;
  for i := 1 to n do
  begin
    readln(x);
    if x > 50 then count := count + 1;
  end;
  writeln(count);
end.''',
    "cpp": '''#include <iostream>

int main() {
    int n, x, count = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> x;
        if (x > 50) count++;
    }
    std::cout << count;
    return 0;
}''',
    "csharp": '''using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int count = 0;
        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x > 50) count++;
        }
        Console.WriteLine(count);
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int count = 0;
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x > 50) count++;
        }
        System.out.println(count);
    }
}''',
}

# ----------------------------------------------------------------------------
# task_092 — Undo-stack (LIFO). Canon = tests + curated code; title/desc fixed.
# ----------------------------------------------------------------------------
T092_TITLE = "Откат действий (undo) через стек"
T092_DESC = (
    "Обработайте n команд. Команда «do <действие>» сохраняет действие. "
    "Команда «undo» отменяет последнее сохранённое действие и выводит его. "
    "Если отменять нечего — выведите nothing. (LIFO — стек.)"
)
T092_BUGGY = {
    "pascal": '''var n, i, top: integer;
    line, action: string;
    st: array[1..100] of string;
begin
  n := int(input());
  top = 0;

  for i in range(n) do
  begin
    line := input();

    if line.startsWith('do') then
    begin
      action := line.split(' ')[1];
      st.push(action);
    end
    else if line = 'undo' then
    begin
      if top >= 0 then
        print(st[0])
      else
        writeln('nothing');
    end;
  end;
end.''',
    "python": '''n = int.Parse(Console.ReadLine())
actions = new Stack<string>()

for i := 1 to n do:
    command = input().split()

    if command[0] = 'do':
        actions.Push(command[1])
    elif command[0] == 'undo':
        if actions.Count > 0:
            print(actions[0])
        else:
            Console.WriteLine('nothing')''',
    "cpp": '''#include <iostream>
#include <stack>

int main() {
    int n = int(input());
    Stack<string> actions;

    for i in range(n):
        string command;
        cin >> command;

        if (command = "do") {
            string action;
            cin >> action;
            actions.add(action);
        } else if (command == "undo") {
            if (actions.Count == 0) {
                Console.WriteLine("nothing");
            } else {
                cout << actions.front();
                actions.pop();
            }
        }

    return 0;
}''',
    "csharp": '''using System;

class Program {
    static void Main() {
        int n = int(input());
        Stack<string> actions = [];

        for i in range(n):
            string[] parts = Console.ReadLine().Split();

            if (parts[0] = "do") {
                actions.Add(parts[1]);
            } else if (parts[0] == "undo") {
                if (actions.Length == 0) {
                    print("nothing");
                } else {
                    Console.WriteLine(actions[0]);
                }
            }
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        Stack<String> actions = new Stack<>();

        for i in range(n):
            String command = Scanner.next();

            if (command == "do") {
                actions.add(Scanner.next());
            } else if (command == "undo") {
                if (actions.Count == 0) {
                    Console.WriteLine("nothing");
                } else {
                    System.out.println(actions.get(0));
                }
            }
    }
}''',
}
T092_REF = {
    "pascal": '''var n, i, top: integer;
    line, action: string;
    st: array[1..100] of string;
begin
  readln(n);
  top := 0;

  for i := 1 to n do
  begin
    readln(line);

    if copy(line, 1, 2) = 'do' then
    begin
      action := copy(line, 4, length(line));
      top := top + 1;
      st[top] := action;
    end
    else if line = 'undo' then
    begin
      if top > 0 then
      begin
        writeln(st[top]);
        top := top - 1;
      end
      else
        writeln('nothing');
    end;
  end;
end.''',
    "python": '''n = int(input())
actions = []
for _ in range(n):
    command = input().split()
    if command[0] == 'do':
        actions.append(command[1])
    elif command[0] == 'undo':
        if actions:
            print(actions.pop())
        else:
            print('nothing')''',
    "cpp": '''#include <iostream>
#include <stack>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::stack<std::string> actions;

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "do") {
            std::string action;
            std::cin >> action;
            actions.push(action);
        } else if (command == "undo") {
            if (actions.empty()) {
                std::cout << "nothing\n";
            } else {
                std::cout << actions.top() << '\n';
                actions.pop();
            }
        }
    }

    return 0;
}''',
    "csharp": '''using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Stack<string> actions = new Stack<string>();

        for (int i = 0; i < n; i++) {
            string[] parts = Console.ReadLine().Split();

            if (parts[0] == "do") {
                actions.Push(parts[1]);
            } else if (parts[0] == "undo") {
                if (actions.Count == 0) {
                    Console.WriteLine("nothing");
                } else {
                    Console.WriteLine(actions.Pop());
                }
            }
        }
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Stack<String> actions = new Stack<>();

        for (int i = 0; i < n; i++) {
            String command = sc.next();

            if (command.equals("do")) {
                actions.push(sc.next());
            } else if (command.equals("undo")) {
                if (actions.empty()) {
                    System.out.println("nothing");
                } else {
                    System.out.println(actions.pop());
                }
            }
        }
    }
}''',
}
T092_TESTS = [
    {"name": "Тест 1", "inputs": "2\ndo save\nundo\n", "output": "save"},
    {"name": "Тест 2", "inputs": "1\nundo\n", "output": "nothing"},
    {"name": "Тест 3", "inputs": "3\ndo a\ndo b\nundo\n", "output": "b"},
    {"name": "Тест 4", "inputs": "4\ndo a\ndo b\ndo c\nundo\n", "output": "c"},
    {"name": "Тест 5", "inputs": "4\ndo a\ndo b\nundo\nundo\n", "output": "b\na"},
]

# ----------------------------------------------------------------------------
# task_031 — Merge two sorted arrays. Canon = description + title; rebuilt fresh.
# ----------------------------------------------------------------------------
T031_TITLE = "Слияние отсортированных массивов"
T031_DESC = (
    "Даны два отсортированных по неубыванию массива A (n чисел) и B (m чисел). "
    "Слейте их в один отсортированный массив и выведите его элементы через пробел.\n"
    "Ввод: первая строка — n и m; вторая строка — n чисел; третья строка — m чисел."
)
T031_BUGGY = {
    "python": '''n, m = map(int, input().split())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

i = 0
j = 0
result = []

while i < n and j < m:
    if a[i] < b[j]:
        result.append(a[i])
        i += 1
    else:
        result.append(b[j])
        i += 1

while i <= n:
    result.append(a[i])
    i += 1

print(result)''',
    "pascal": '''var n, m, i, j, k: integer;
    a, b, res: array[1..1000] of integer;
begin
  readln(n, m);
  for i := 1 to n do read(a[i]);
  for j := 1 to m do read(b[j]);

  i := 1;
  j := 1;
  k := 0;

  while (i <= n) and (j <= m) do
  begin
    if a[i] < b[j] then
    begin
      k := k + 1;
      res[k] := a[i];
      i := i + 1;
    end
    else
    begin
      k := k + 1;
      res[k] := b[j];
      i := i + 1;
    end
  end;

  while i <= n do
  begin
    res[k] := a[i];
    i := i + 1;
  end;

  for i := 1 to k do
    write(res[i]);
end.''',
    "cpp": '''#include <iostream>
#include <vector>

int main() {
    int n, m;
    std::cin >> n >> m;

    std::vector<int> a(n), b(m), result;
    for (int i = 0; i < n; i++) std::cin >> a[i];
    for (int j = 0; j < m; j++) std::cin >> b[j];

    int i = 0, j = 0;
    while (i < n && j < m) {
        if (a[i] < b[j]) {
            result.push_back(a[i]);
            i++;
        } else {
            result.push_back(b[j]);
            i++;
        }
    }
    while (i <= n) {
        result.push_back(a[i]);
        i++;
    }

    for (int x : result) std::cout << x;
    return 0;
}''',
    "csharp": '''using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string[] nm = Console.ReadLine().Split();
        int n = int.Parse(nm[0]);
        int m = int.Parse(nm[1]);

        int[] a = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);
        int[] b = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);

        List<int> result = new List<int>();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i] < b[j]) {
                result.Add(a[i]);
                i++;
            } else {
                result.Add(b[j]);
                i++;
            }
        }
        while (i <= n) {
            result.Add(a[i]);
            i++;
        }

        Console.WriteLine(string.Join("", result));
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int[] a = new int[n];
        int[] b = new int[m];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        for (int j = 0; j < m; j++) b[j] = sc.nextInt();

        List<Integer> result = new ArrayList<>();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i] < b[j]) {
                result.add(a[i]);
                i++;
            } else {
                result.add(b[j]);
                i++;
            }
        }
        while (i <= n) {
            result.add(a[i]);
            i++;
        }

        System.out.println(result);
    }
}''',
}
T031_REF = {
    "pascal": '''var n, m, i, j, k: integer;
    a, b, res: array[1..1000] of integer;
begin
  readln(n, m);
  for i := 1 to n do
    read(a[i]);
  for j := 1 to m do
    read(b[j]);

  i := 1;
  j := 1;
  k := 0;

  while (i <= n) and (j <= m) do
  begin
    k := k + 1;
    if a[i] <= b[j] then
    begin
      res[k] := a[i];
      i := i + 1;
    end
    else
    begin
      res[k] := b[j];
      j := j + 1;
    end;
  end;

  while i <= n do
  begin
    k := k + 1;
    res[k] := a[i];
    i := i + 1;
  end;

  while j <= m do
  begin
    k := k + 1;
    res[k] := b[j];
    j := j + 1;
  end;

  for i := 1 to k do
  begin
    if i > 1 then write(' ');
    write(res[i]);
  end;
end.''',
    "python": '''n, m = map(int, input().split())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

i = j = 0
result = []
while i < n and j < m:
    if a[i] <= b[j]:
        result.append(a[i]); i += 1
    else:
        result.append(b[j]); j += 1
while i < n:
    result.append(a[i]); i += 1
while j < m:
    result.append(b[j]); j += 1

print(' '.join(map(str, result)))''',
    "cpp": '''#include <iostream>
#include <vector>

int main() {
    int n, m;
    std::cin >> n >> m;

    std::vector<int> a(n), b(m), result;
    for (int i = 0; i < n; i++) std::cin >> a[i];
    for (int j = 0; j < m; j++) std::cin >> b[j];

    int i = 0, j = 0;
    while (i < n && j < m) {
        if (a[i] <= b[j]) {
            result.push_back(a[i]);
            i++;
        } else {
            result.push_back(b[j]);
            j++;
        }
    }
    while (i < n) result.push_back(a[i++]);
    while (j < m) result.push_back(b[j++]);

    for (int p = 0; p < (int)result.size(); p++) {
        if (p > 0) std::cout << ' ';
        std::cout << result[p];
    }
    return 0;
}''',
    "csharp": '''using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string[] nm = Console.ReadLine().Split();
        int n = int.Parse(nm[0]);
        int m = int.Parse(nm[1]);
        int[] a = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);
        int[] b = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);
        List<int> result = new List<int>();
        int i = 0, j = 0;
        while (i < n && j < m) {
            if (a[i] <= b[j]) result.Add(a[i++]);
            else result.Add(b[j++]);
        }
        while (i < n) result.Add(a[i++]);
        while (j < m) result.Add(b[j++]);
        Console.WriteLine(string.Join(" ", result));
    }
}''',
    "java": '''import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int[] a = new int[n];
        int[] b = new int[m];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        for (int j = 0; j < m; j++) b[j] = sc.nextInt();
        ArrayList<Integer> result = new ArrayList<>();
        int i = 0, j = 0;
        while (i < n && j < m) {
            if (a[i] <= b[j]) result.add(a[i++]);
            else result.add(b[j++]);
        }
        while (i < n) result.add(a[i++]);
        while (j < m) result.add(b[j++]);
        for (int p = 0; p < result.size(); p++) {
            if (p > 0) System.out.print(" ");
            System.out.print(result.get(p));
        }
    }
}''',
}
T031_TESTS = [
    {"name": "Тест 1", "inputs": "3 3\n1 3 5\n2 4 6\n", "output": "1 2 3 4 5 6"},
    {"name": "Тест 2", "inputs": "2 2\n1 2\n3 4\n", "output": "1 2 3 4"},
    {"name": "Тест 3", "inputs": "1 3\n5\n1 2 3\n", "output": "1 2 3 5"},
    {"name": "Тест 4", "inputs": "2 2\n-5 -1\n-3 -2\n", "output": "-5 -3 -2 -1"},
    {"name": "Тест 5", "inputs": "3 1\n1 2 4\n3\n", "output": "1 2 3 4"},
    {"name": "Тест 6", "inputs": "1 1\n7\n7\n", "output": "7 7"},
]

# ----------------------------------------------------------------------------
# task_023 — Frequency histogram 0..9 (fold_aggregate).
# Canon: v128 tests; T1 expected corrected (digit 9 -> freq[9]).
# ----------------------------------------------------------------------------
T023_TITLE = "Гистограмма частот"
T023_DESC = (
    "Даны n и n целых чисел от 0 до 9. "
    "Постройте гистограмму частот и выведите количество каждого значения "
    "(10 чисел для цифр 0..9 через пробел)."
)
T023_TESTS = [
    {"name": "Тест 1", "inputs": "5\n1\n2\n1\n9\n1\n", "output": "0 3 1 0 0 0 0 0 0 1 "},
    {"name": "Тест 2", "inputs": "3\n0\n0\n0\n", "output": "3 0 0 0 0 0 0 0 0 0 "},
    {"name": "Тест 3", "inputs": "4\n9\n8\n7\n6\n", "output": "0 0 0 0 0 0 1 1 1 1 "},
    {"name": "Тест 4", "inputs": "3\n5\n5\n5\n", "output": "0 0 0 0 0 3 0 0 0 0 "},
]
T023_REF = {
    "python": """n = int(input())
freq = [0] * 10
for _ in range(n):
    x = int(input())
    if 0 <= x <= 9:
        freq[x] += 1
print(*freq, end=' ')""",
    "pascal": """var n, i, x: integer;
    freq: array[0..9] of integer;
begin
  readln(n);
  for i := 0 to 9 do
    freq[i] := 0;
  for i := 1 to n do
  begin
    readln(x);
    if (x >= 0) and (x <= 9) then
      freq[x] := freq[x] + 1;
  end;
  for i := 0 to 9 do
    write(freq[i], ' ');
end.""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> freq(10, 0);
    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;
        if (x >= 0 && x <= 9) {
            freq[x]++;
        }
    }
    for (int value : freq) {
        std::cout << value << ' ';
    }
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] freq = new int[10];
        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x >= 0 && x <= 9) {
                freq[x]++;
            }
        }
        for (int i = 0; i < freq.Length; i++) {
            Console.Write(freq[i] + " ");
        }
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] freq = new int[10];
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x >= 0 && x <= 9) {
                freq[x]++;
            }
        }
        for (int value : freq) {
            System.out.print(value + " ");
        }
    }
}""",
}
T023_BUGGY = {
    "python": """n = int(input())
total = 0
for _ in range(n):
    x = int(input())
    if x <= 0:
        total += x
print(total)""",
    "pascal": """var n, i, x, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(x);
    if x <= 0 then
      total := total + x;
  end;
  writeln(total);
end.""",
    "cpp": """#include <iostream>

int main() {
    int n, x, total = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> x;
        if (x <= 0) {
            total += x;
        }
    }
    std::cout << total;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int total = 0;
        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x <= 0) {
                total += x;
            }
        }
        Console.WriteLine(total);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int total = 0;
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x <= 0) {
                total += x;
            }
        }
        System.out.println(total);
    }
}""",
}

# ----------------------------------------------------------------------------
# task_028 — Insert at 1-based position (index_1based / AlgorithmDebug).
# pos and x are on separate input lines (matches v128 tests).
# ----------------------------------------------------------------------------
T028_TITLE = "Вставка элемента по позиции"
T028_DESC = (
    "Даны n, массив из n чисел, позиция pos (1-based) и значение x. "
    "Вставьте x на позицию pos и выведите массив из n+1 элементов через пробел."
)
T028_TESTS = [
    {"name": "Тест 1", "inputs": "3\n1\n2\n3\n2\n9\n", "output": "1 9 2 3"},
    {"name": "Тест 2", "inputs": "2\n10\n20\n1\n5\n", "output": "5 10 20"},
    {"name": "Тест 3", "inputs": "1\n7\n1\n3\n", "output": "3 7"},
    {"name": "Тест 4", "inputs": "4\n1\n2\n3\n4\n3\n0\n", "output": "1 2 0 3 4"},
]
T028_REF = {
    "python": """n = int(input())
a = [int(input()) for _ in range(n)]
pos = int(input())
x = int(input())
a.insert(pos - 1, x)
print(' '.join(str(v) for v in a))""",
    "pascal": """var n, i, pos, x: integer;
    a: array[1..100] of integer;
begin
  readln(n);
  for i := 1 to n do
    readln(a[i]);
  readln(pos);
  readln(x);
  for i := n downto pos do
    a[i + 1] := a[i];
  a[pos] := x;
  for i := 1 to n + 1 do
    write(a[i], ' ');
end.""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }
    int pos, x;
    std::cin >> pos >> x;
    a.insert(a.begin() + (pos - 1), x);
    for (int i = 0; i < (int)a.size(); i++) {
        if (i > 0) std::cout << ' ';
        std::cout << a[i];
    }
    return 0;
}""",
    "csharp": """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        var a = new List<int>();
        for (int i = 0; i < n; i++) {
            a.Add(int.Parse(Console.ReadLine()));
        }
        int pos = int.Parse(Console.ReadLine());
        int x = int.Parse(Console.ReadLine());
        a.Insert(pos - 1, x);
        Console.WriteLine(string.Join(" ", a));
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ArrayList<Integer> a = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            a.add(sc.nextInt());
        }
        int pos = sc.nextInt();
        int x = sc.nextInt();
        a.add(pos - 1, x);
        for (int i = 0; i < a.size(); i++) {
            if (i > 0) System.out.print(" ");
            System.out.print(a.get(i));
        }
    }
}""",
}
T028_BUGGY = {
    "python": """n = int(input())
a = [int(input()) for _ in range(n)]
pos = int(input())
x = int(input())
a.insert(pos, x)
print(' '.join(str(v) for v in a))""",
    "pascal": """var n, i, pos, x: integer;
    a: array[1..100] of integer;
begin
  readln(n);
  for i := 1 to n do
    readln(a[i]);
  readln(pos);
  readln(x);
  for i := n downto pos + 1 do
    a[i + 1] := a[i];
  a[pos + 1] := x;
  for i := 1 to n + 1 do
    write(a[i], ' ');
end.""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }
    int pos, x;
    std::cin >> pos >> x;
    a.insert(a.begin() + pos, x);
    for (int i = 0; i < (int)a.size(); i++) {
        if (i > 0) std::cout << ' ';
        std::cout << a[i];
    }
    return 0;
}""",
    "csharp": """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        var a = new List<int>();
        for (int i = 0; i < n; i++) {
            a.Add(int.Parse(Console.ReadLine()));
        }
        int pos = int.Parse(Console.ReadLine());
        int x = int.Parse(Console.ReadLine());
        a.Insert(pos, x);
        Console.WriteLine(string.Join(" ", a));
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ArrayList<Integer> a = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            a.add(sc.nextInt());
        }
        int pos = sc.nextInt();
        int x = sc.nextInt();
        a.add(pos, x);
        for (int i = 0; i < a.size(); i++) {
            if (i > 0) System.out.print(" ");
            System.out.print(a.get(i));
        }
    }
}""",
}

# ----------------------------------------------------------------------------
# task_036 — First substring occurrence, 1-based index or 0 (string_index).
# ----------------------------------------------------------------------------
T036_TITLE = "Первое вхождение подстроки"
T036_DESC = (
    "Даны строка s и подстрока p. "
    "Найдите первое вхождение p в s и выведите индекс (1-based) или 0, если p не найдена."
)
T036_TESTS = [
    {"name": "Тест 1", "inputs": "hello\nll\n", "output": "3"},
    {"name": "Тест 2", "inputs": "abc\nz\n", "output": "0"},
    {"name": "Тест 3", "inputs": "ababab\nab\n", "output": "1"},
    {"name": "Тест 4", "inputs": "test\nt\n", "output": "1"},
]
T036_REF = {
    "python": """s = input()
p = input()
idx = s.find(p)
print(idx + 1 if idx >= 0 else 0)""",
    "pascal": """var s, p: string;
    i, pos: integer;
begin
  readln(s);
  readln(p);
  pos := 0;
  if length(p) > 0 then
    for i := 1 to length(s) - length(p) + 1 do
      if (pos = 0) and (copy(s, i, length(p)) = p) then
        pos := i;
  writeln(pos);
end.""",
    "cpp": """#include <iostream>
#include <string>

int main() {
    std::string s, p;
    std::getline(std::cin, s);
    std::getline(std::cin, p);
    size_t idx = s.find(p);
    int pos = (idx == std::string::npos) ? 0 : (int)idx + 1;
    std::cout << pos;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        string p = Console.ReadLine();
        int idx = s.IndexOf(p);
        Console.WriteLine(idx >= 0 ? idx + 1 : 0);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        String p = sc.nextLine();
        int idx = s.indexOf(p);
        System.out.println(idx >= 0 ? idx + 1 : 0);
    }
}""",
}
T036_BUGGY = {
    "python": """s = input()
p = input()
print(s.find(p))""",
    "pascal": """var s, p: string;
    i, pos: integer;
begin
  readln(s);
  readln(p);
  pos := 0;
  if length(p) > 0 then
    for i := 1 to length(s) - length(p) + 1 do
      if (pos = 0) and (copy(s, i, length(p)) = p) then
        pos := i - 1;
  writeln(pos);
end.""",
    "cpp": """#include <iostream>
#include <string>

int main() {
    std::string s, p;
    std::getline(std::cin, s);
    std::getline(std::cin, p);
    size_t idx = s.find(p);
    std::cout << (idx == std::string::npos ? -1 : (int)idx);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        string p = Console.ReadLine();
        Console.WriteLine(s.IndexOf(p));
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        String p = sc.nextLine();
        System.out.println(s.indexOf(p));
    }
}""",
}

# ----------------------------------------------------------------------------
# task_039 — RLE compression (string_sequence).
# Buggy: count starts at 0 and last group is not flushed.
# ----------------------------------------------------------------------------
T039_TITLE = "RLE-сжатие строки"
T039_DESC = (
    "Дана строка s. Выполните RLE-сжатие: "
    "каждую группу одинаковых символов замените символом и длиной группы (например, aaabb -> a3b2)."
)
T039_TESTS = [
    {"name": "Тест 1", "inputs": "aaabb\n", "output": "a3b2"},
    {"name": "Тест 2", "inputs": "abba\n", "output": "a1b2a1"},
    {"name": "Тест 3", "inputs": "abc\n", "output": "a1b1c1"},
    {"name": "Тест 4", "inputs": "a\n", "output": "a1"},
]
T039_REF = {
    "python": """s = input()
if s == '':
    print('')
else:
    result = ''
    count = 1
    for i in range(1, len(s) + 1):
        if i < len(s) and s[i] == s[i - 1]:
            count += 1
        else:
            result += s[i - 1] + str(count)
            count = 1
    print(result)""",
    "pascal": """var s, res: string;
    i, count: integer;
begin
  readln(s);
  if s = '' then
    writeln('')
  else
  begin
    res := '';
    count := 1;
    for i := 2 to length(s) + 1 do
    begin
      if (i <= length(s)) and (s[i] = s[i - 1]) then
        count := count + 1
      else
      begin
        res := res + s[i - 1] + IntToStr(count);
        count := 1;
      end;
    end;
    writeln(res);
  end;
end.""",
    "cpp": """#include <iostream>
#include <string>

int main() {
    std::string s;
    std::getline(std::cin, s);
    if (s.empty()) {
        std::cout << "";
    } else {
        std::string result;
        int count = 1;
        for (int i = 1; i <= (int)s.size(); i++) {
            if (i < (int)s.size() && s[i] == s[i - 1]) {
                count++;
            } else {
                result += s[i - 1];
                result += std::to_string(count);
                count = 1;
            }
        }
        std::cout << result;
    }
    return 0;
}""",
    "csharp": """using System;
using System.Text;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        if (s == "") {
            Console.WriteLine("");
        } else {
            StringBuilder result = new StringBuilder();
            int count = 1;
            for (int i = 1; i <= s.Length; i++) {
                if (i < s.Length && s[i] == s[i - 1]) {
                    count++;
                } else {
                    result.Append(s[i - 1]);
                    result.Append(count);
                    count = 1;
                }
            }
            Console.WriteLine(result.ToString());
        }
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        if (s.equals("")) {
            System.out.println("");
        } else {
            StringBuilder result = new StringBuilder();
            int count = 1;
            for (int i = 1; i <= s.length(); i++) {
                if (i < s.length() && s.charAt(i) == s.charAt(i - 1)) {
                    count++;
                } else {
                    result.append(s.charAt(i - 1));
                    result.append(count);
                    count = 1;
                }
            }
            System.out.println(result.toString());
        }
    }
}""",
}
T039_BUGGY = {
    "python": """s = input()
result = ''
count = 0
for i in range(len(s)):
    if i > 0 and s[i] == s[i - 1]:
        count += 1
    else:
        if i > 0:
            result += s[i - 1] + str(count)
        count = 1
print(result)""",
    "pascal": """var s, res: string;
    i, count: integer;
begin
  readln(s);
  res := '';
  count := 0;
  for i := 2 to length(s) do
  begin
    if s[i] = s[i - 1] then
      count := count + 1
    else
    begin
      res := res + s[i - 1] + IntToStr(count);
      count := 1;
    end;
  end;
  writeln(res);
end.""",
    "cpp": """#include <iostream>
#include <string>

int main() {
    std::string s;
    std::getline(std::cin, s);
    std::string result;
    int count = 0;
    for (int i = 0; i < (int)s.size(); i++) {
        if (i > 0 && s[i] == s[i - 1]) {
            count++;
        } else {
            if (i > 0) {
                result += s[i - 1];
                result += std::to_string(count);
            }
            count = 1;
        }
    }
    std::cout << result;
    return 0;
}""",
    "csharp": """using System;
using System.Text;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        StringBuilder result = new StringBuilder();
        int count = 0;
        for (int i = 0; i < s.Length; i++) {
            if (i > 0 && s[i] == s[i - 1]) {
                count++;
            } else {
                if (i > 0) {
                    result.Append(s[i - 1]);
                    result.Append(count);
                }
                count = 1;
            }
        }
        Console.WriteLine(result.ToString());
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        StringBuilder result = new StringBuilder();
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            if (i > 0 && s.charAt(i) == s.charAt(i - 1)) {
                count++;
            } else {
                if (i > 0) {
                    result.append(s.charAt(i - 1));
                    result.append(count);
                }
                count = 1;
            }
        }
        System.out.println(result.toString());
    }
}""",
}


# ----------------------------------------------------------------------------
# Batch 3 — task_044 power, task_047 min/max (canon confirmed; not applied to DB)
# ----------------------------------------------------------------------------
import sys
from pathlib import Path as _Path

_SCRIPTS_DIR = _Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from debug_batch3_t044_t047 import (  # noqa: E402
    T044_BUGGY,
    T044_DESC,
    T044_HINTS,
    T044_POST,
    T044_REF,
    T044_TESTS,
    T044_TITLE,
    T047_BUGGY,
    T047_DESC,
    T047_HINTS,
    T047_POST,
    T047_REF,
    T047_TESTS,
    T047_TITLE,
)
from debug_batch4_t012_t020 import (  # noqa: E402
    T012_BUGGY,
    T012_DESC,
    T012_HINTS,
    T012_POST,
    T012_REF,
    T012_TESTS,
    T012_TITLE,
    T020_BUGGY,
    T020_DESC,
    T020_HINTS,
    T020_POST,
    T020_REF,
    T020_TESTS,
    T020_TITLE,
)
from debug_batch5_t068_t076 import BATCH5_OVERRIDES  # noqa: E402
from debug_batch6_t015_t079 import BATCH6_OVERRIDES  # noqa: E402

# ----------------------------------------------------------------------------
# Batch 3 — task_055 Quicksort, task_060 Bubble sort (draft; not applied to DB)
# ----------------------------------------------------------------------------
T055_TITLE = "Quicksort"
T055_DESC = (
    "Отсортируйте массив алгоритмом quicksort и выведите элементы через пробел."
)
T055_REF = {
    "pascal": """procedure QuickSort(var a: array of integer; left, right: integer);
var i, j, pivot, temp: integer;
begin
  i := left;
  j := right;
  pivot := a[(left + right) div 2];

  while i <= j do
  begin
    while a[i] < pivot do i := i + 1;
    while a[j] > pivot do j := j - 1;

    if i <= j then
    begin
      temp := a[i];
      a[i] := a[j];
      a[j] := temp;

      i := i + 1;
      j := j - 1;
    end;
  end;

  if left < j then QuickSort(a, left, j);
  if i < right then QuickSort(a, i, right);
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  QuickSort(a, 0, n - 1);

  for i := 0 to n - 1 do
    write(a[i], ' ');
end.""",
    "python": """def quicksort(a):
    if len(a) <= 1:
        return a

    pivot = a[len(a) // 2]

    left = []
    middle = []
    right = []

    for x in a:
        if x < pivot:
            left.append(x)
        elif x > pivot:
            right.append(x)
        else:
            middle.append(x)

    return quicksort(left) + middle + quicksort(right)


n = int(input())
a = [int(input()) for _ in range(n)]

print(*quicksort(a))""",
    "cpp": """#include <iostream>
#include <vector>
#include <algorithm>

void quickSort(std::vector<int>& a, int left, int right) {
    int i = left;
    int j = right;
    int pivot = a[(left + right) / 2];

    while (i <= j) {
        while (a[i] < pivot) i++;
        while (a[j] > pivot) j--;

        if (i <= j) {
            std::swap(a[i], a[j]);
            i++;
            j--;
        }
    }

    if (left < j) quickSort(a, left, j);
    if (i < right) quickSort(a, i, right);
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    quickSort(a, 0, n - 1);

    for (int x : a) {
        std::cout << x << ' ';
    }

    return 0;
}""",
    "csharp": """using System;

class Program {
    static void QuickSort(int[] a, int left, int right) {
        int i = left;
        int j = right;
        int pivot = a[(left + right) / 2];

        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;

            if (i <= j) {
                int temp = a[i];
                a[i] = a[j];
                a[j] = temp;

                i++;
                j--;
            }
        }

        if (left < j) QuickSort(a, left, j);
        if (i < right) QuickSort(a, i, right);
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        QuickSort(a, 0, n - 1);

        foreach (int x in a) {
            Console.Write(x + " ");
        }
    }
}""",
    "java": """import java.util.*;

class Main {
    static void quickSort(int[] a, int left, int right) {
        int i = left;
        int j = right;
        int pivot = a[(left + right) / 2];

        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;

            if (i <= j) {
                int temp = a[i];
                a[i] = a[j];
                a[j] = temp;

                i++;
                j--;
            }
        }

        if (left < j) quickSort(a, left, j);
        if (i < right) quickSort(a, i, right);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        quickSort(a, 0, n - 1);

        for (int x : a) {
            System.out.print(x + " ");
        }
    }
}""",
}
T055_BUGGY = {
    "pascal": """procedure QuickSort(var a: array of integer; left, right: integer);
var i, j, pivot, temp: integer;
begin
  pivot := a[left];

  while left <= right do
  begin
    while a[left] <= pivot do left := left + 1;
    while a[right] > pivot do right := right - 1;

    if left <= right then
    begin
      temp := a[left];
      a[left] := a[right];
      a[right] := temp;
    end;
  end;

  QuickSort(a, left, right);
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  QuickSort(a, 0, n);

  for i := 0 to n - 1 do
    writeln(a[i]);
end.""",
    "python": """def quicksort(int[] a):
    if len(a) < 1:
        return []

    pivot := a[0]
    left = []
    right = []

    for x in a:
        if x <= pivot:
            left.append(x)
        else:
            right.append(x)

    return quicksort(left) + pivot + quicksort(right)


n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

Console.WriteLine(quicksort(a))""",
    "cpp": """#include <iostream>
#include <vector>

void quickSort(vector<int> a, int left, int right) {
    int pivot := a[left];

    while left <= right {
        while (a[left] <= pivot) left++;
        while (a[right] > pivot) right--;

        if (left <= right) {
            a[left], a[right] = a[right], a[left];
        }
    }

    quickSort(a, left, right);
}

int main() {
    int n = int(input());
    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    quickSort(a, 0, n);

    Console.WriteLine(a);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void QuickSort(int[] a, int left, int right) {
        int pivot := a[left];

        while left <= right {
            while (a[left] <= pivot) left++;
            while (a[right] > pivot) right--;

            if (left <= right) {
                a[left], a[right] = a[right], a[left];
            }
        }

        QuickSort(a, left, right);
    }

    static void Main() {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        QuickSort(a, 0, n);

        print(a);
    }
}""",
    "java": """import java.util.*;

class Main {
    static void quickSort(int[] a, int left, int right) {
        int pivot := a[left];

        while left <= right {
            while (a[left] <= pivot) left++;
            while (a[right] > pivot) right--;

            if (left <= right) {
                a[left], a[right] = a[right], a[left];
            }
        }

        quickSort(a, left, right);
    }

    public static void main(String[] args) {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        quickSort(a, 0, n);

        Console.WriteLine(a);
    }
}""",
}
T055_TESTS = [
    {"name": "Тест 1", "inputs": "5\n5\n2\n9\n1\n7\n", "output": "1 2 5 7 9"},
    {"name": "Тест 2", "inputs": "1\n10\n", "output": "10"},
    {"name": "Тест 3", "inputs": "3\n3\n2\n1\n", "output": "1 2 3"},
    {"name": "Тест 4", "inputs": "3\n-1\n-3\n-2\n", "output": "-3 -2 -1"},
]

T060_TITLE = "Сортировка пузырьком"
T060_DESC = (
    "Отсортируйте массив по возрастанию алгоритмом bubble sort "
    "и выведите элементы через пробел."
)
T060_REF = {
    "pascal": """var n, i, j, temp: integer;
    a: array[0..99] of integer;
begin
  readln(n);

  for i := 0 to n - 1 do
    readln(a[i]);

  for i := 0 to n - 1 do
    for j := 0 to n - i - 2 do
      if a[j] > a[j + 1] then
      begin
        temp := a[j];
        a[j] := a[j + 1];
        a[j + 1] := temp;
      end;

  for i := 0 to n - 1 do
    write(a[i], ' ');
end.""",
    "python": """n = int(input())
a = [int(input()) for _ in range(n)]

for i in range(n):
    for j in range(0, n - i - 1):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]

print(*a)""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (a[j] > a[j + 1]) {
                std::swap(a[j], a[j + 1]);
            }
        }
    }

    for (int x : a) {
        std::cout << x << ' ';
    }

    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (a[j] > a[j + 1]) {
                    int temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;
                }
            }
        }

        foreach (int x in a) {
            Console.Write(x + " ");
        }
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (a[j] > a[j + 1]) {
                    int temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;
                }
            }
        }

        for (int x : a) {
            System.out.print(x + " ");
        }
    }
}""",
}
T060_BUGGY = {
    "pascal": """var n, i, j, temp: integer;
    a: array[0..99] of integer;
begin
  n = int(input());

  for i in range(n) do
    a[i] := int(input());

  for i := 0 to n do
    for j := 0 to n - i do
      if a[j] > a[j + 1] then
      begin
        swap(a[j], a[j + 1]);
      end;

  print(*a);
end.""",
    "python": """n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

for i in range(n):
    for j in range(0, n - i):
        if a[j] > a[j + 1]:
            swap(a[j], a[j + 1])

Console.WriteLine(a)""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n = int(input());
    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    for (int i = 0; i <= n; i++) {
        for (int j = 0; j < n - i; j++) {
            if (a[j] > a[j + 1]) {
                a[j], a[j + 1] = a[j + 1], a[j];
            }
        }
    }

    Console.WriteLine(a);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        for (int i = 0; i <= n; i++) {
            for (int j = 0; j < n - i; j++) {
                if (a[j] > a[j + 1]) {
                    a[j], a[j + 1] = a[j + 1], a[j];
                }
            }
        }

        print(a);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        for (int i = 0; i <= n; i++) {
            for (int j = 0; j < n - i; j++) {
                if (a[j] > a[j + 1]) {
                    a[j], a[j + 1] = a[j + 1], a[j];
                }
            }
        }

        Console.WriteLine(a);
    }
}""",
}
T060_TESTS = [
    {"name": "Тест 1", "inputs": "5\n5\n2\n9\n1\n7\n", "output": "1 2 5 7 9"},
    {"name": "Тест 2", "inputs": "1\n10\n", "output": "10"},
    {"name": "Тест 3", "inputs": "3\n3\n2\n1\n", "output": "1 2 3"},
    {"name": "Тест 4", "inputs": "3\n5\n5\n5\n", "output": "5 5 5"},
]

OVERRIDES = {
    "task_004": {
        "title": T004_TITLE,
        "description": T004_DESC,
        "buggy": T004_BUGGY,
        "ref": T004_REF,
        "tests": T004_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "counted_loop",
            "simple_branch",
            "filter_select",
            "arithmetic_ops",
        ],
        "hints": [
            "Считайте только положительные значения; ноль и отрицательные не подходят.",
            "Счётчик успешных операций нужно начинать с нуля.",
            "Проверяйте условие amount > 0 внутри цикла для каждого значения.",
        ],
        "post_solve": (
            "Положительная операция — только amount > 0. "
            "Счётчик должен стартовать с 0; инициализация count := 1 даёт лишнюю единицу даже "
            "когда положительных операций нет."
        ),
    },
    "task_007": {
        "title": T007_TITLE,
        "description": T007_DESC,
        "buggy": T007_BUGGY,
        "ref": T007_REF,
        "tests": T007_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "counted_loop",
            "simple_branch",
            "filter_select",
        ],
        "hints": [
            "Сравнивайте каждое значение с порогом (>= 50), а не только последнее.",
            "Значение ровно 50 должно учитываться в ответе.",
            "Условие в теле цикла должно включать границу порога.",
        ],
        "post_solve": (
            "Нужно считать измерения с x >= 50. "
            "Условие x > 50 теряет значения, равные порогу, и занижает ответ."
        ),
    },
    "task_012": {
        "title": T012_TITLE,
        "description": T012_DESC,
        "buggy": T012_BUGGY,
        "ref": T012_REF,
        "tests": T012_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "stdin_read",
            "stdout_write",
            "simple_branch",
            "branch_logic",
        ],
        "hints": T012_HINTS,
        "post_solve": T012_POST,
    },
    "task_020": {
        "title": T020_TITLE,
        "description": T020_DESC,
        "buggy": T020_BUGGY,
        "ref": T020_REF,
        "tests": T020_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "pre_condition_loop",
        ],
        "hints": T020_HINTS,
        "post_solve": T020_POST,
    },
    "task_068": {
        k: v
        for k, v in BATCH5_OVERRIDES["task_068"].items()
        if k not in ("canon_notes", "failing_test_fix", "conflicts")
    },
    "task_076": {
        k: v
        for k, v in BATCH5_OVERRIDES["task_076"].items()
        if k not in ("canon_notes", "failing_test_fix", "conflicts")
    },
    "task_015": {
        k: v
        for k, v in BATCH6_OVERRIDES["task_015"].items()
        if k not in ("canon_notes", "db_replacements", "legacy_untouched", "risks")
    },
    "task_079": {
        k: v
        for k, v in BATCH6_OVERRIDES["task_079"].items()
        if k not in ("canon_notes", "db_replacements", "legacy_untouched", "risks")
    },
    "task_092": {
        "title": T092_TITLE,
        "description": T092_DESC,
        "buggy": T092_BUGGY,
        "ref": T092_REF,
        "tests": T092_TESTS,
        "concepts": ["tc_linear_structures", "tc_loops", "tc_conditionals", "tc_strings", "tc_console_io"],
        "hints": [
            "Стек хранит последние действия: do добавляет действие на вершину, undo снимает именно последнее.",
            "Проверяйте пустой стек перед pop/top: при пустом стеке нужно вывести nothing.",
            "В Pascal стек можно реализовать массивом и переменной top.",
        ],
        "post_solve": (
            "Undo работает по LIFO: последнее сохранённое действие отменяется первым. "
            "Главная ошибка переноса — заменить стек очередью или читать первый элемент вместо вершины."
        ),
    },
    "task_031": {
        "title": T031_TITLE,
        "description": T031_DESC,
        "buggy": T031_BUGGY,
        "ref": T031_REF,
        "tests": T031_TESTS,
        "concepts": ["tc_arrays", "tc_collection_traversal", "tc_loops", "tc_conditionals", "tc_console_io"],
        "hints": [
            "Держите два указателя: i для A и j для B.",
            "После выбора элемента из B должен двигаться j, а не i.",
            "После основного цикла нужно дописать остаток обоих массивов.",
        ],
        "post_solve": (
            "Слияние отсортированных массивов — классический two pointers: сравниваем текущие элементы, "
            "кладём меньший в результат и двигаем указатель того массива, откуда взяли элемент."
        ),
    },
    "task_023": {
        "title": T023_TITLE,
        "description": T023_DESC,
        "buggy": T023_BUGGY,
        "ref": T023_REF,
        "tests": T023_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "counted_loop",
            "arithmetic_ops",
            "fold_aggregate",
        ],
        "hints": [
            "Используйте массив из 10 счётчиков для цифр 0..9.",
            "Увеличивайте freq[x] только если 0 <= x <= 9.",
            "Выводите все 10 частот через пробел, включая нули.",
        ],
        "post_solve": (
            "Нужна гистограмма частот по цифрам 0..9, а не сумма отрицательных. "
            "Каждое значение увеличивает свой счётчик freq[x]."
        ),
    },
    "task_028": {
        "title": T028_TITLE,
        "description": T028_DESC,
        "buggy": T028_BUGGY,
        "ref": T028_REF,
        "tests": T028_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "indexed_sequence",
            "counted_loop",
        ],
        "hints": [
            "Позиция pos в условии задаётся с 1.",
            "Сдвиг элементов делайте с конца массива к pos.",
            "После вставки элементов должно стать n+1.",
        ],
        "post_solve": (
            "В Pascal массив 1-based: pos=2 означает второй элемент. "
            "Ошибка insert(pos) в Python-стиле или сдвига не с той позиции вставляет не туда."
        ),
    },
    "task_036": {
        "title": T036_TITLE,
        "description": T036_DESC,
        "buggy": T036_BUGGY,
        "ref": T036_REF,
        "tests": T036_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "counted_loop",
            "search_find",
        ],
        "hints": [
            "find возвращает 0-based индекс или -1.",
            "В ответе нужен 1-based индекс первого вхождения.",
            "Если подстрока не найдена, выведите 0.",
        ],
        "post_solve": (
            "Python str.find даёт 0 для первого символа и -1 при отсутствии. "
            "По условию нужно 1 и 0 соответственно."
        ),
    },

    "task_044": {
        "title": T044_TITLE,
        "description": T044_DESC,
        "buggy": T044_BUGGY,
        "ref": T044_REF,
        "tests": T044_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "function_definition",
            "function_invocation",
        ],
        "hints": T044_HINTS,
        "post_solve": T044_POST,
    },
    "task_047": {
        "title": T047_TITLE,
        "description": T047_DESC,
        "buggy": T047_BUGGY,
        "ref": T047_REF,
        "tests": T047_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "function_definition",
            "function_invocation",
        ],
        "hints": T047_HINTS,
        "post_solve": T047_POST,
    },
    "task_055": {
        "title": T055_TITLE,
        "description": T055_DESC,
        "buggy": T055_BUGGY,
        "ref": T055_REF,
        "tests": T055_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "function_definition",
            "function_invocation",
            "recursion",
        ],
        "hints": [
            "Выберите опорный элемент и разделите массив на части меньше и больше pivot.",
            "Рекурсивно сортируйте левую и правую части только если в них больше одного элемента.",
            "После partition индексы i и j должны двигаться навстреч друг другу.",
        ],
        "post_solve": (
            "Классический quicksort: pivot обычно берут из середины, после обменов "
            "рекурсия идёт на [left..j] и [i..right]. Ошибки — pivot только слева, "
            "бесконечная рекурсия без сужения диапазона, граница right=n вместо n-1."
        ),
    },
    "task_060": {
        "title": T060_TITLE,
        "description": T060_DESC,
        "buggy": T060_BUGGY,
        "ref": T060_REF,
        "tests": T060_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "indexed_sequence",
            "counted_loop",
            "sort_order",
        ],
        "hints": [
            "Сравнивайте соседние элементы a[j] и a[j+1].",
            "Меняйте местами только если левый элемент больше правого.",
            "Внешний цикл уменьшает число неотсортированных хвостовых элементов.",
        ],
        "post_solve": (
            "Bubble sort по возрастанию: условие обмена a[j] > a[j+1]. "
            "Внутренний цикл — до n-i-1, внешний — n-1 проходов. "
            "Ошибки границ (i<=n, j<=n-i) и обратное сравнение дают неверный порядок."
        ),
    },
    "task_039": {
        "title": T039_TITLE,
        "description": T039_DESC,
        "buggy": T039_BUGGY,
        "ref": T039_REF,
        "tests": T039_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "string_sequence",
        ],
        "hints": [
            "Счётчик группы начинайте с 1 для первого символа.",
            "При смене символа допишите предыдущий символ и длину в результат.",
            "Не забудьте закрыть последнюю группу после цикла.",
        ],
        "post_solve": (
            "RLE идёт по группам: пока символ повторяется — увеличиваем count, "
            "при смене — пишем char+count и сбрасываем. count=0 и пропуск последней группы ломают ответ."
        ),
    },
}


def run_python(code: str, inp: str) -> str:
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    open(sf, "w", encoding="utf-8").write(code)
    r = subprocess.run([sys.executable, sf], input=inp, capture_output=True,
                       text=True, timeout=8, cwd=wd)
    return r.stdout


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def validate(pid: str, spec: dict) -> bool:
    ref = spec["ref"].get("python")
    if not ref:
        print(f"  [validate] {pid}: no python ref, skipped")
        return True
    ok = True
    for tc in spec["tests"]:
        got = run_python(ref, tc["inputs"])
        if norm(got) != norm(tc["output"]):
            ok = False
            print(f"  [validate] {pid} FAIL in={tc['inputs']!r} exp={tc['output']!r} got={got!r}")
    # buggy must fail at least one test (otherwise nothing to fix)
    bug = spec["buggy"].get("python")
    if bug:
        fails = 0
        for tc in spec["tests"]:
            try:
                got = run_python(bug, tc["inputs"])
            except Exception:
                got = "ERR"
            if norm(got) != norm(tc["output"]):
                fails += 1
        if fails == 0:
            print(f"  [validate] {pid} WARNING: buggy python passes all tests (no bug to fix)")
        else:
            print(f"  [validate] {pid}: buggy fails {fails}/{len(spec['tests'])} tests (good)")
    if ok:
        print(f"  [validate] {pid}: reference passes all {len(spec['tests'])} tests OK")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes to DB")
    ap.add_argument("--only", nargs="*", help="restrict to given pattern_ids")
    args = ap.parse_args()

    targets = OVERRIDES
    if args.only:
        targets = {k: v for k, v in OVERRIDES.items() if k in args.only}

    print("== VALIDATION ==")
    all_ok = True
    for pid, spec in targets.items():
        if not validate(pid, spec):
            all_ok = False
    if not all_ok:
        print("\nValidation failed; aborting (nothing written).")
        sys.exit(1)

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    print("\n== %s ==" % ("APPLY" if args.apply else "DRY-RUN"))
    for pid, spec in targets.items():
        cur.execute("""select id, title, code_examples, test_cases from task
                       where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""", (pid,))
        row = cur.fetchone()
        if not row:
            print(f"  {pid}: NOT FOUND in DB"); continue
        did, old_title, ce, tc = row
        if isinstance(ce, str):
            ce = json.loads(ce)
        new_ce = dict(ce)
        showcase = dict(new_ce.get("curriculum_showcase") or {})
        concepts = list(spec.get("concepts") or [])
        concepts_by_lang = {lang: list(concepts) for lang in LANGS}

        # Teacher-edited debug contract:
        #   code_examples[lang]       -> fixed/reference code
        #   code_examples[buggy_lang] -> buggy starter shown in the editor
        for lang in LANGS:
            fixed = str((spec.get("ref") or {}).get(lang) or "").strip()
            buggy = str((spec.get("buggy") or {}).get(lang) or "").strip()
            if fixed:
                new_ce[lang] = fixed
            if buggy:
                new_ce[f"buggy_{lang}"] = buggy

        if concepts:
            new_ce["patterns"] = list(concepts)
            new_ce["expected_concepts"] = concepts_by_lang
            showcase["expected_concept_ids"] = list(concepts)
            showcase["expected_concepts"] = concepts_by_lang
        if spec.get("hints"):
            new_ce["hints"] = list(spec["hints"])
            showcase["hints"] = list(spec["hints"])
        if spec.get("post_solve"):
            new_ce["post_solve_explanation"] = str(spec["post_solve"])
            showcase["post_solve_explanation"] = str(spec["post_solve"])

        showcase["primary_action"] = "debug"
        showcase["task_format"] = "исправление"
        for key in ("template", "blocks", "correct_order", "original_code"):
            new_ce.pop(key, None)
            showcase.pop(key, None)

        new_ce["teacher_assembly_override"] = True
        new_ce["curriculum_showcase"] = showcase
        print(f"  {pid} (DB id {did})")
        print(f"    title : {old_title!r}")
        print(f"        -> {spec['title']!r}")
        print(f"    fixed langs updated: {[lang for lang in LANGS if (spec.get('ref') or {}).get(lang)]}")
        print(f"    buggy langs updated: {[lang for lang in LANGS if (spec.get('buggy') or {}).get(lang)]}")
        print(f"    expected concepts: {concepts}")
        print(f"    tests: {len(tc) if tc else 0} -> {len(spec['tests'])}")
        if args.apply:
            cur.execute(
                """update task set title=%s, description=%s,
                          code_examples=%s, test_cases=%s, task_type=%s, updated_at=now()
                   where id=%s""",
                (
                    spec["title"],
                    spec["description"],
                    json.dumps(new_ce, ensure_ascii=False),
                    json.dumps(spec["tests"], ensure_ascii=False),
                    "algorithm",
                    did,
                ),
            )
    if args.apply:
        conn.commit()
        print("\nCommitted.")
    else:
        print("\nDry-run only. Re-run with --apply to write.")
    cur.close(); conn.close()


if __name__ == "__main__":
    main()
