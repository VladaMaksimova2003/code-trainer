# Debug task_007 — threshold_count (multiple syntax + logic errors per language)
FIXED_PASCAL = """var n, i, x, count: integer;
begin
  readln(n);
  count := 0;

  for i := 1 to n do
  begin
    readln(x);
    if x >= 50 then
      count := count + 1;
  end;

  writeln(count);
end."""

BUGGY_PASCAL = """var n, i, x, count: integer;
begin
  n := int.Parse(Console.ReadLine());
  count := 1;

  for i := 0 to n - 1 do
  begin
    readln(x);
    if x > 50 then
      count = count + 1;
  end;

  println(count);
end."""

FIXED_PYTHON = """n = int(input())
count = 0

for _ in range(n):
    x = int(input())
    if x >= 50:
        count += 1

print(count)"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
count = 1

for i := 1 to n do:
    x = int(input())
    if x > 50:
        count = count + 1

println(count)"""

FIXED_CPP = """#include <iostream>

int main() {
    int n;
    std::cin >> n;

    int count = 0;

    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;
        if (x >= 50) {
            count++;
        }
    }

    std::cout << count;
    return 0;
}"""

BUGGY_CPP = """#include iostream

int main() {
    int n;
    cin >> n;

    int count = 1;

    for (int i = 1; i <= n; i++) {
        int x;
        std::cin >> x;
        if (x > 50)
            count = count + 1;
    }

    System.out.println(count);
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int count = 0;

        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x >= 50) {
                count++;
            }
        }

        Console.WriteLine(count);
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int(input());
        int count = 1;

        for (int i = 1; i <= n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x > 50) {
                count = count + 1;
            }
        }

        Console.WriteLine(count);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int count = 0;

        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x >= 50) {
                count++;
            }
        }

        System.out.println(count);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int count = 1;

        for (int i = 1; i <= n; i++) {
            int x = sc.nextInt();
            if (x > 50) {
                count = count + 1;
            }
        }

        System.out.print(count);
    }
}"""
