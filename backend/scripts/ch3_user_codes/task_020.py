FIXED_PASCAL = """var x, total: integer;
begin
  total := 0;
  readln(x);

  while x <> 0 do
  begin
    if x >= 0 then
      total := total + x;

    readln(x);
  end;

  writeln(total);
end."""

BUGGY_PASCAL = """var n, i, x, total: integer;
begin
  readln(n);
  total := 0;

  for i := 1 to n do
  begin
    readln(x);

    if x >= 0 then
      total := total + x;
  end;

  writeln(total);
end."""

FIXED_PYTHON = """total = 0
x = int(input())

while x != 0:
    if x >= 0:
        total += x
    x = int(input())

print(total)"""

BUGGY_PYTHON = """n = int(input())
total = 0

for _ in range(n):
    x = int(input())
    if x >= 0:
        total += x

print(total)"""

FIXED_CPP = """#include <iostream>

int main() {
    int x, total = 0;
    std::cin >> x;

    while (x != 0) {
        if (x >= 0) {
            total += x;
        }
        std::cin >> x;
    }

    std::cout << total;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int n, total = 0;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;
        if (x >= 0) {
            total += x;
        }
    }

    std::cout << total;
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int total = 0;
        int x = int.Parse(Console.ReadLine());

        while (x != 0) {
            if (x >= 0) {
                total += x;
            }
            x = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(total);
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int total = 0;

        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x >= 0) {
                total += x;
            }
        }

        Console.WriteLine(total);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int total = 0;
        int x = sc.nextInt();

        while (x != 0) {
            if (x >= 0) {
                total += x;
            }
            x = sc.nextInt();
        }

        System.out.println(total);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int total = 0;

        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x >= 0) {
                total += x;
            }
        }

        System.out.println(total);
    }
}"""
