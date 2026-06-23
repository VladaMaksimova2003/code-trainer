FIXED_PASCAL = """var n, i, j: integer;
    a: array[1..100] of integer;
    found: boolean;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  found := false;

  for i := 1 to n do
    for j := i + 1 to n do
      if a[i] = a[j] then
        found := true;

  if found then
    writeln('yes')
  else
    writeln('no');
end."""

BUGGY_PASCAL = """var n, i, j: integer;
    a: array[1..100] of integer;
    found: boolean;
begin
  n = int(input());

  for i in range(n) do
    a[i] := int(input());

  found = False;

  for i := 1 to n do
    for j := i to n do
      if a[i] == a[j] then
        found = true;

  if found:
    print('yes')
  else:
    print('no');
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

found = False

for i in range(n):
    for j in range(i + 1, n):
        if a[i] == a[j]:
            found = True

print('yes' if found else 'no')"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

bool found = false

for i in range(n):
    for j in range(i, n):
        if a[i] = a[j]:
            found := true

Console.WriteLine(found ? "yes" : "no")"""

FIXED_CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    bool found = false;

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (a[i] == a[j]) {
                found = true;
            }
        }
    }

    std::cout << (found ? "yes" : "no");
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int main() {
    int n = int(input());

    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    bool found = False;

    for (int i = 0; i < n; i++) {
        for (int j = i; j < n; j++) {
            if (a[i] = a[j]) {
                found := true;
            }
        }
    }

    Console.WriteLine(found ? "yes" : "no");
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

        bool found = false;

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (a[i] == a[j]) {
                    found = true;
                }
            }
        }

        Console.WriteLine(found ? "yes" : "no");
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int(input());

        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        bool found := False;

        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                if (a[i] = a[j]) {
                    found = true;
                }
            }
        }

        print(found ? "yes" : "no");
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

        boolean found = false;

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (a[i] == a[j]) {
                    found = true;
                }
            }
        }

        System.out.println(found ? "yes" : "no");
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());

        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        bool found = False;

        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                if (a[i] = a[j]) {
                    found := true;
                }
            }
        }

        Console.WriteLine(found ? "yes" : "no");
    }
}"""

PASCAL = FIXED_PASCAL
PYTHON = FIXED_PYTHON
CPP = FIXED_CPP
CSHARP = FIXED_CSHARP
JAVA = FIXED_JAVA
