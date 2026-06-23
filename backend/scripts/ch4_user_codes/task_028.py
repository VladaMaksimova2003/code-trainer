FIXED_PASCAL = """var n, i, pos, value: integer;
    a: array[1..101] of integer;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  readln(pos, value);

  if (pos < 1) or (pos > n + 1) then
    writeln('invalid')
  else
  begin
    for i := n downto pos do
      a[i + 1] := a[i];

    a[pos] := value;

    for i := 1 to n + 1 do
      write(a[i], ' ');
  end;
end."""

BUGGY_PASCAL = """var n, i, pos, value: integer;
    a: array[1..101] of integer;
begin
  n := int(input());

  for i in range(n) do
    a[i] = int(input());

  pos, value = map(int, input().split());

  if pos < 0 || pos > n then
    print('invalid')
  else
  begin
    for i := pos to n do
      a[i + 1] := a[i];

    a.insert(pos, value);
    writeln(a);
  end;
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

pos, value = map(int, input().split())

if pos < 1 or pos > n + 1:
    print('invalid')
else:
    a.insert(pos - 1, value)
    print(*a)"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
a = new int[n + 1]

for i := 1 to n do:
    a[i] = int(input())

pos, value = Console.ReadLine().Split()

if pos < 1 || pos > n + 1:
    Console.WriteLine("invalid")
else:
    for i = n downto pos:
        a[i + 1] := a[i]

    a[pos] = value
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

    int pos, value;
    std::cin >> pos >> value;

    if (pos < 1 || pos > n + 1) {
        std::cout << "invalid";
    } else {
        a.push_back(0);

        for (int i = n; i >= pos; i--) {
            a[i] = a[i - 1];
        }

        a[pos - 1] = value;

        for (int x : a) {
            std::cout << x << ' ';
        }
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int main() {
    int n = int(input());

    int[] a = new int[n + 1];

    for i in range(n):
        cin >> a[i];

    int pos, value;
    pos, value = map(int, input().split());

    if pos < 1 or pos > n + 1 {
        print("invalid");
    } else {
        for (int i = pos; i <= n; i++) {
            a[i + 1] = a[i];
        }

        a.insert(pos, value);

        Console.WriteLine(a);
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n + 1];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        string[] p = Console.ReadLine().Split();
        int pos = int.Parse(p[0]);
        int value = int.Parse(p[1]);

        if (pos < 1 || pos > n + 1) {
            Console.WriteLine("invalid");
        } else {
            for (int i = n; i >= pos; i--) {
                a[i] = a[i - 1];
            }

            a[pos - 1] = value;

            for (int i = 0; i <= n; i++) {
                Console.Write(a[i] + " ");
            }
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int(input());

        int[] a = new int[n];

        for i in range(n):
            a[i] = Console.ReadLine();

        int pos, value;
        cin >> pos >> value;

        if pos < 1 or pos > n + 1 {
            print("invalid");
        } else {
            for i := n downto pos do {
                a[i + 1] = a[i];
            }

            a.insert(pos, value);
            Console.WriteLine(a);
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n + 1];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int pos = sc.nextInt();
        int value = sc.nextInt();

        if (pos < 1 || pos > n + 1) {
            System.out.println("invalid");
        } else {
            for (int i = n; i >= pos; i--) {
                a[i] = a[i - 1];
            }

            a[pos - 1] = value;

            for (int i = 0; i <= n; i++) {
                System.out.print(a[i] + " ");
            }
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());

        int[] a = new int[n];

        for i in range(n):
            a[i] = Scanner.nextInt();

        int pos, value;
        cin >> pos >> value;

        if pos < 1 || pos > n + 1 {
            Console.WriteLine("invalid");
        } else {
            for i := n downto pos do {
                a[i + 1] = a[i];
            }

            a.insert(pos, value);
            print(a);
        }
    }
}"""
