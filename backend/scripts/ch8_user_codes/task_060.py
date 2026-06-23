FIXED_PASCAL = """var n, i, j, temp: integer;
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
end."""

BUGGY_PASCAL = """var n, i, j, temp: integer;
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
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

for i in range(n):
    for j in range(0, n - i - 1):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]

print(*a)"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

for i in range(n):
    for j in range(0, n - i):
        if a[j] > a[j + 1]:
            swap(a[j], a[j + 1])

Console.WriteLine(a)"""

FIXED_CPP = """#include <iostream>
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
}"""

BUGGY_CPP = """#include <iostream>
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
}"""

FIXED_CSHARP = """using System;

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
}"""

BUGGY_CSHARP = """using System;

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
}"""

FIXED_JAVA = """import java.util.*;

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
}"""

BUGGY_JAVA = """import java.util.*;

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
}"""
