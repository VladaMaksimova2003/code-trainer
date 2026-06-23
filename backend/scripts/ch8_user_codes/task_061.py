FIXED_PASCAL = """var n, i, j, key: integer;
    a: array[0..99] of integer;
begin
  readln(n);

  for i := 0 to n - 1 do
    readln(a[i]);

  for i := 1 to n - 1 do
  begin
    key := a[i];
    j := i - 1;

    while (j >= 0) and (a[j] > key) do
    begin
      a[j + 1] := a[j];
      j := j - 1;
    end;

    a[j + 1] := key;
  end;

  for i := 0 to n - 1 do
    write(a[i], ' ');
end."""

BUGGY_PASCAL = """var n, i, j, key: integer;
    a: array[0..99] of integer;
begin
  n := int(input());

  for i in range(n) do
    a[i] = int(input());

  for i := 1 to n do
  begin
    key = a[i];
    j := i;

    while j > 0 && a[j] > key do
    begin
      a[j] := a[j - 1];
      j--;
    end;

    a[j] := key;
  end;

  print(*a);
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

for i in range(1, n):
    key = a[i]
    j = i - 1

    while j >= 0 and a[j] > key:
        a[j + 1] = a[j]
        j -= 1

    a[j + 1] = key

print(*a)"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

for i in range(1, n):
    key := a[i]
    j = i

    while j > 0 && a[j] > key:
        a[j] = a[j - 1]
        j--

    a[j] = key

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

    for (int i = 1; i < n; i++) {
        int key = a[i];
        int j = i - 1;

        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            j--;
        }

        a[j + 1] = key;
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

    for (int i = 1; i <= n; i++) {
        int key := a[i];
        int j = i;

        while (j > 0 and a[j] > key) {
            a[j] = a[j - 1];
            j--;
        }

        a[j] = key;
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

        for (int i = 1; i < n; i++) {
            int key = a[i];
            int j = i - 1;

            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
            }

            a[j + 1] = key;
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

        for (int i = 1; i <= n; i++) {
            int key := a[i];
            int j = i;

            while (j > 0 and a[j] > key) {
                a[j] = a[j - 1];
                j--;
            }

            a[j] = key;
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

        for (int i = 1; i < n; i++) {
            int key = a[i];
            int j = i - 1;

            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
            }

            a[j + 1] = key;
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

        for (int i = 1; i <= n; i++) {
            int key := a[i];
            int j = i;

            while (j > 0 and a[j] > key) {
                a[j] = a[j - 1];
                j--;
            }

            a[j] = key;
        }

        Console.WriteLine(a);
    }
}"""
