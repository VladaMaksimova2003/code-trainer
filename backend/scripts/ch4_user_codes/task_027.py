FIXED_PASCAL = """var n, i, pos: integer;
    a: array[1..100] of integer;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  readln(pos);

  if (pos < 1) or (pos > n) then
    writeln('invalid')
  else
  begin
    for i := pos to n - 1 do
      a[i] := a[i + 1];

    for i := 1 to n - 1 do
      write(a[i], ' ');
  end;
end."""

BUGGY_PASCAL = """var n, i, pos: integer;
    a: array[1..100] of integer;
begin
  n = int(input());

  for i in range(n) do
    a[i] := int(input());

  pos := int(input());

  if pos < 0 || pos >= n then
    print('invalid')
  else
  begin
    for i := pos to n do
      a[i] = a[i + 1];

    print(*a);
  end;
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

pos = int(input())

if pos < 1 or pos > n:
    print('invalid')
else:
    del a[pos - 1]
    print(*a)"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

pos = int(input())

if pos < 1 || pos > n:
    Console.WriteLine("invalid")
else:
    a.erase(a.begin() + pos)
    print(a)"""

FIXED_CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    int pos;
    std::cin >> pos;

    if (pos < 1 || pos > n) {
        std::cout << "invalid";
    } else {
        for (int i = pos - 1; i < n - 1; i++) {
            a[i] = a[i + 1];
        }

        for (int i = 0; i < n - 1; i++) {
            std::cout << a[i] << ' ';
        }
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int main() {
    int n = int(input());

    vector<int> a = new int[n];

    for i in range(n) {
        cin >> a[i];
    }

    int pos;
    Console.ReadLine(pos);

    if pos < 1 or pos > n {
        cout << "invalid";
    } else {
        del a[pos];

        for (int x : a) {
            print(x);
        }
    }

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

        int pos = int.Parse(Console.ReadLine());

        if (pos < 1 || pos > n) {
            Console.WriteLine("invalid");
        } else {
            for (int i = pos - 1; i < n - 1; i++) {
                a[i] = a[i + 1];
            }

            for (int i = 0; i < n - 1; i++) {
                Console.Write(a[i] + " ");
            }
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

        int pos = int(input());

        if pos < 1 or pos > n {
            print("invalid");
        } else {
            a.erase(a.begin() + pos);

            foreach x in a:
                Console.Write(x + " ");
        }
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

        int pos = sc.nextInt();

        if (pos < 1 || pos > n) {
            System.out.println("invalid");
        } else {
            for (int i = pos - 1; i < n - 1; i++) {
                a[i] = a[i + 1];
            }

            for (int i = 0; i < n - 1; i++) {
                System.out.print(a[i] + " ");
            }
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

        int pos = input();

        if pos < 1 || pos > n {
            Console.WriteLine("invalid");
        } else {
            del a[pos];

            for (int x : a) {
                print(x);
            }
        }
    }
}"""

PASCAL = FIXED_PASCAL
PYTHON = FIXED_PYTHON
CPP = FIXED_CPP
CSHARP = FIXED_CSHARP
JAVA = FIXED_JAVA
