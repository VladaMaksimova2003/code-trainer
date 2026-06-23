PASCAL = """var n, i: integer;
    name, phone, query: string;
    names, phones: array[1..100] of string;
    found: boolean;
begin
  readln(n);

  for i := 1 to n do
    readln(names[i], phones[i]);

  readln(query);
  found := false;

  for i := 1 to n do
    if names[i] = query then
    begin
      writeln(phones[i]);
      found := true;
    end;

  if not found then
    writeln('not found');
end."""

PYTHON = """n = int(input())
book = {}

for _ in range(n):
    name, phone = input().split()
    book[name] = phone

query = input()

if query in book:
    print(book[query])
else:
    print('not found')"""

CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::map<std::string, std::string> book;

    for (int i = 0; i < n; i++) {
        std::string name, phone;
        std::cin >> name >> phone;
        book[name] = phone;
    }

    std::string query;
    std::cin >> query;

    if (book.count(query)) {
        std::cout << book[query];
    } else {
        std::cout << "not found";
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Dictionary<string, string> book = new Dictionary<string, string>();

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();
            book[p[0]] = p[1];
        }

        string query = Console.ReadLine();

        if (book.ContainsKey(query)) {
            Console.WriteLine(book[query]);
        } else {
            Console.WriteLine("not found");
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        HashMap<String, String> book = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String name = sc.next();
            String phone = sc.next();
            book.put(name, phone);
        }

        String query = sc.next();

        if (book.containsKey(query)) {
            System.out.println(book.get(query));
        } else {
            System.out.println("not found");
        }
    }
}"""
