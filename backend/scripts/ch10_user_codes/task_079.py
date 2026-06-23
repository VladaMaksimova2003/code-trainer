FIXED_PASCAL = """var n, m, i, j, count, value: integer;
    key: string;
    keys: array[1..200] of string;
    values: array[1..200] of integer;
    found: boolean;
begin
  count := 0;

  readln(n);

  for i := 1 to n do
  begin
    readln(key, value);
    count := count + 1;
    keys[count] := key;
    values[count] := value;
  end;

  readln(m);

  for i := 1 to m do
  begin
    readln(key, value);
    found := false;

    for j := 1 to count do
      if keys[j] = key then
      begin
        values[j] := values[j] + value;
        found := true;
      end;

    if not found then
    begin
      count := count + 1;
      keys[count] := key;
      values[count] := value;
    end;
  end;

  for i := 1 to count do
    for j := i + 1 to count do
      if keys[j] < keys[i] then
      begin
        key := keys[i];
        keys[i] := keys[j];
        keys[j] := key;
        value := values[i];
        values[i] := values[j];
        values[j] := value;
      end;

  for i := 1 to count do
    writeln(keys[i], ' ', values[i]);
end."""

BUGGY_PASCAL = """var n, m, i, j, count, value: integer;
    key: string;
    keys: array[1..200] of string;
    values: array[1..200] of integer;
begin
  readln(n);

  for i := 1 to n do
  begin
    readln(key, value);
    keys[i] := key;
    values[i] := value;
  end;

  readln(m);

  for i := 1 to m do
  begin
    readln(key, value);

    for j := 1 to n do
      if keys[j] = key then
        values[j] := value;
  end;

  for i := 1 to n do
    writeln(keys[i], values[i]);
end."""

FIXED_PYTHON = """n = int(input())
result = {}

for _ in range(n):
    key, value = input().split()
    result[key] = result.get(key, 0) + int(value)

m = int(input())

for _ in range(m):
    key, value = input().split()
    result[key] = result.get(key, 0) + int(value)

for key in sorted(result):
    print(key, result[key])"""

BUGGY_PYTHON = """n = int(input())
result = {}

for _ in range(n):
    key, value = input().split()
    result[key] = int(value)

m = int(input())

for _ in range(m):
    key, value = input().split()

    if key in result:
        result[key] = int(value)
    else:
        result[key] = value

for key, value in result:
    print(key, value)"""

FIXED_CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> result;

    int n;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        std::string key;
        int value;

        std::cin >> key >> value;
        result[key] += value;
    }

    int m;
    std::cin >> m;

    for (int i = 0; i < m; i++) {
        std::string key;
        int value;

        std::cin >> key >> value;
        result[key] += value;
    }

    for (auto item : result) {
        std::cout << item.first << ' ' << item.second << '\\n';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    std::unordered_map<std::string, int> result;

    int n;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        std::string key;
        int value;

        std::cin >> key >> value;
        result.insert({key, value});
    }

    int m;
    std::cin >> m;

    for (int i = 0; i < m; i++) {
        std::string key;
        int value;

        std::cin >> key >> value;
        result.insert({key, value});
    }

    for (auto item : result) {
        std::cout << item.first << ' ' << item.second << '\\n';
    }

    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void AddValue(SortedDictionary<string, int> dict, string key, int value) {
        if (!dict.ContainsKey(key)) dict[key] = 0;
        dict[key] += value;
    }

    static void Main() {
        SortedDictionary<string, int> result = new SortedDictionary<string, int>();

        int n = int.Parse(Console.ReadLine());

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();
            AddValue(result, p[0], int.Parse(p[1]));
        }

        int m = int.Parse(Console.ReadLine());

        for (int i = 0; i < m; i++) {
            string[] p = Console.ReadLine().Split();
            AddValue(result, p[0], int.Parse(p[1]));
        }

        foreach (var item in result) {
            Console.WriteLine($"{item.Key} {item.Value}");
        }
    }
}"""

BUGGY_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        Dictionary<string, int> result = new Dictionary<string, int>();

        int n = int.Parse(Console.ReadLine());

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();
            result.Add(p[0], int.Parse(p[1]));
        }

        int m = int.Parse(Console.ReadLine());

        for (int i = 0; i < m; i++) {
            string[] p = Console.ReadLine().Split();
            result.Add(p[0], int.Parse(p[1]));
        }

        foreach (var item in result) {
            Console.WriteLine(item);
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static void addValue(TreeMap<String, Integer> map, String key, int value) {
        map.put(key, map.getOrDefault(key, 0) + value);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        TreeMap<String, Integer> result = new TreeMap<>();

        int n = sc.nextInt();

        for (int i = 0; i < n; i++) {
            String key = sc.next();
            int value = sc.nextInt();
            addValue(result, key, value);
        }

        int m = sc.nextInt();

        for (int i = 0; i < m; i++) {
            String key = sc.next();
            int value = sc.nextInt();
            addValue(result, key, value);
        }

        for (String key : result.keySet()) {
            System.out.println(key + " " + result.get(key));
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        HashMap<String, Integer> result = new HashMap<>();
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        for (int i = 0; i < n; i++) {
            String key = sc.next();
            int value = sc.nextInt();
            result.put(key, value);
        }

        int m = sc.nextInt();

        for (int i = 0; i < m; i++) {
            String key = sc.next();
            int value = sc.nextInt();
            result.put(key, value);
        }

        for (String key : result.keySet()) {
            System.out.println(key + " " + result.get(key));
        }
    }
}"""
