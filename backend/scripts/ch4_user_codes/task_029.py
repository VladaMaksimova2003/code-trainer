FIXED_PASCAL = """var n, m, i: integer;
    a, b: array[1..100] of integer;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  readln(m);

  for i := 1 to m do
    readln(b[i]);

  for i := 1 to n do
    write(a[i], ' ');

  for i := 1 to m do
    write(b[i], ' ');
end."""

BUGGY_PASCAL = """var n, m, i: integer;
    a, b: array[1..100] of integer;
begin
  n = int(input());
  a = list(map(int, input().split()));

  m = int(input());
  b = list(map(int, input().split()));

  result := a + b;

  print(*result);
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

m = int(input())
b = [int(input()) for _ in range(m)]

result = a + b

print(*result)"""

BUGGY_PYTHON = """int n = int.Parse(Console.ReadLine())
int[] a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

int m = int.Parse(Console.ReadLine())
int[] b = new int[m]

for i := 1 to m do:
    b[i] = int(input())

result := a + b

Console.WriteLine(result)"""

FIXED_CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    int m;
    std::cin >> m;

    std::vector<int> b(m);
    for (int i = 0; i < m; i++) {
        std::cin >> b[i];
    }

    for (int x : a) {
        std::cout << x << ' ';
    }

    for (int x : b) {
        std::cout << x << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int n = int(input());
    int[] a = new int[n];

    for i in range(n):
        cin >> a[i];

    int m = int(input());
    int[] b = new int[m];

    for i in range(m):
        cin >> b[i];

    auto result = a + b;

    Console.WriteLine(result);
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

        int m = int.Parse(Console.ReadLine());
        int[] b = new int[m];

        for (int i = 0; i < m; i++) {
            b[i] = int.Parse(Console.ReadLine());
        }

        foreach (int x in a) {
            Console.Write(x + " ");
        }

        foreach (int x in b) {
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
            a[i] = int.Parse(Console.ReadLine());

        int m = int(input());
        int[] b = [];

        for i in range(m):
            b[i] = int.Parse(Console.ReadLine());

        int[] result = a + b;

        print(*result);
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

        int m = sc.nextInt();
        int[] b = new int[m];

        for (int i = 0; i < m; i++) {
            b[i] = sc.nextInt();
        }

        for (int x : a) {
            System.out.print(x + " ");
        }

        for (int x : b) {
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

        int m = int(input());
        int[] b = [];

        for i in range(m):
            b[i] = Scanner.nextInt();

        int[] result = a + b;

        Console.WriteLine(result);
    }
}"""

PASCAL = FIXED_PASCAL
PYTHON = FIXED_PYTHON
CPP = FIXED_CPP
CSHARP = FIXED_CSHARP
JAVA = FIXED_JAVA
