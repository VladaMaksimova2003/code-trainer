FIXED_PASCAL = """var n, i, j, count, tmpTotal: integer;
    category: string;
    amount: integer;
    names: array[1..100] of string;
    totals: array[1..100] of integer;
    found: boolean;
    tmpName: string;
begin
  readln(n);
  count := 0;

  for i := 1 to n do
  begin
    readln(category, amount);
    found := false;

    for j := 1 to count do
      if names[j] = category then
      begin
        totals[j] := totals[j] + amount;
        found := true;
      end;

    if not found then
    begin
      count := count + 1;
      names[count] := category;
      totals[count] := amount;
    end;
  end;

  for i := 1 to count do
    for j := i + 1 to count do
      if names[j] < names[i] then
      begin
        tmpName := names[i];
        names[i] := names[j];
        names[j] := tmpName;
        tmpTotal := totals[i];
        totals[i] := totals[j];
        totals[j] := tmpTotal;
      end;

  for i := 1 to count do
    writeln(names[i], ' ', totals[i]);
end."""

BUGGY_PASCAL = """var n, i: integer;
    groups: Dictionary<string, integer>;
    category: string;
    amount: integer;
begin
  n = int(input());

  for i in range(n) do
  begin
    category, amount = input().split();
    groups[category] += amount;
  end;

  for key in sorted(groups) do
    print(key, groups[key]);
end."""

FIXED_PYTHON = """n = int(input())
groups = {}

for _ in range(n):
    category, amount = input().split()
    amount = int(amount)

    groups[category] = groups.get(category, 0) + amount

for category in sorted(groups):
    print(category, groups[category])"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
groups = new Dictionary<string, int>()

for i := 1 to n do:
    category, amount = input().split()
    groups[category] += amount

for category in groups.Keys:
    Console.WriteLine(category + " " + groups[category])"""

FIXED_CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::map<std::string, int> groups;

    for (int i = 0; i < n; i++) {
        std::string category;
        int amount;

        std::cin >> category >> amount;
        groups[category] += amount;
    }

    for (auto& item : groups) {
        std::cout << item.first << ' ' << item.second << '\\n';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <map>

int main() {
    int n = int(input());
    Dictionary<string, int> groups;

    for i in range(n):
        string category;
        int amount;
        Console.ReadLine(category, amount);

        groups[category] = groups.get(category, 0) + amount;

    for key in sorted(groups):
        print(key, groups[key]);

    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        SortedDictionary<string, int> groups = new SortedDictionary<string, int>();

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            string category = p[0];
            int amount = int.Parse(p[1]);

            if (!groups.ContainsKey(category)) {
                groups[category] = 0;
            }

            groups[category] += amount;
        }

        foreach (var item in groups) {
            Console.WriteLine($"{item.Key} {item.Value}");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int(input());
        var groups = {};

        for i in range(n):
            category, amount = Console.ReadLine().Split();
            groups[category] += amount;

        for key in sorted(groups):
            print(key, groups[key]);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        TreeMap<String, Integer> groups = new TreeMap<>();

        for (int i = 0; i < n; i++) {
            String category = sc.next();
            int amount = sc.nextInt();

            groups.put(category, groups.getOrDefault(category, 0) + amount);
        }

        for (String category : groups.keySet()) {
            System.out.println(category + " " + groups.get(category));
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        Dictionary<string, int> groups = new Dictionary<>();

        for i in range(n):
            String category = Scanner.next();
            int amount = Scanner.nextInt();

            groups[category] += amount;

        for key in sorted(groups):
            Console.WriteLine(key + " " + groups[key]);
    }
}"""
