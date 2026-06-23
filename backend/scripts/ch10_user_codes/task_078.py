PASCAL = """var n, i, j, count, tmpTotal: integer;
    category, product: string;
    names: array[1..100] of string;
    totals: array[1..100] of integer;
    found: boolean;
    tmpName: string;
begin
  readln(n);
  count := 0;

  for i := 1 to n do
  begin
    readln(category, product);
    found := false;

    for j := 1 to count do
      if names[j] = category then
      begin
        totals[j] := totals[j] + 1;
        found := true;
      end;

    if not found then
    begin
      count := count + 1;
      names[count] := category;
      totals[count] := 1;
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

PYTHON = """n = int(input())
groups = {}

for _ in range(n):
    category, product = input().split()
    groups[category] = groups.get(category, 0) + 1

for category in sorted(groups):
    print(category, groups[category])"""

CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::map<std::string, int> groups;

    for (int i = 0; i < n; i++) {
        std::string category, product;
        std::cin >> category >> product;

        groups[category]++;
    }

    for (auto item : groups) {
        std::cout << item.first << ' ' << item.second << '\\n';
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        SortedDictionary<string, int> groups = new SortedDictionary<string, int>();

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();
            string category = p[0];

            if (!groups.ContainsKey(category)) groups[category] = 0;
            groups[category]++;
        }

        foreach (var item in groups) {
            Console.WriteLine($"{item.Key} {item.Value}");
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        TreeMap<String, Integer> groups = new TreeMap<>();

        for (int i = 0; i < n; i++) {
            String category = sc.next();
            String product = sc.next();

            groups.put(category, groups.getOrDefault(category, 0) + 1);
        }

        for (String category : groups.keySet()) {
            System.out.println(category + " " + groups.get(category));
        }
    }
}"""
