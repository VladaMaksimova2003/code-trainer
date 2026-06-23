PASCAL = """var n, i, j, count: integer;
    query: string;
    cache: array[1..100] of string;
    found: boolean;
begin
  readln(n);
  count := 0;

  for i := 1 to n do
  begin
    readln(query);
    found := false;

    for j := 1 to count do
      if cache[j] = query then
        found := true;

    if found then
      writeln('cached')
    else
    begin
      writeln('new');
      count := count + 1;
      cache[count] := query;
    end;
  end;
end."""

PYTHON = """n = int(input())
cache = {}

for _ in range(n):
    query = input()

    if query in cache:
        print('cached')
    else:
        print('new')
        cache[query] = True"""

CPP = """#include <iostream>
#include <set>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::set<std::string> cache;

    for (int i = 0; i < n; i++) {
        std::string query;
        std::cin >> query;

        if (cache.count(query)) {
            std::cout << "cached\\n";
        } else {
            std::cout << "new\\n";
            cache.insert(query);
        }
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        HashSet<string> cache = new HashSet<string>();

        for (int i = 0; i < n; i++) {
            string query = Console.ReadLine();

            if (cache.Contains(query)) {
                Console.WriteLine("cached");
            } else {
                Console.WriteLine("new");
                cache.Add(query);
            }
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = Integer.parseInt(sc.nextLine());
        HashSet<String> cache = new HashSet<>();

        for (int i = 0; i < n; i++) {
            String query = sc.nextLine();

            if (cache.contains(query)) {
                System.out.println("cached");
            } else {
                System.out.println("new");
                cache.add(query);
            }
        }
    }
}"""
