FIXED_PASCAL = """var n, target, x, i, position: integer;
begin
  readln(n, target);
  position := 0;

  for i := 1 to n do
  begin
    readln(x);

    if x = target then
      position := i;
  end;

  writeln(position);
end."""

BUGGY_PASCAL = """var n, target, x, i, position: integer;
begin
  readln(n, target);
  position := 0;

  for i := 1 to n do
  begin
    readln(x);

    if (x = target) and (position = 0) then
      position := i;
  end;

  writeln(position);
end."""

FIXED_PYTHON = """n, target = map(int, input().split())

position = 0

for i in range(1, n + 1):
    x = int(input())

    if x == target:
        position = i

print(position)"""

BUGGY_PYTHON = """n, target = map(int, input().split())

position = 0

for i in range(1, n + 1):
    x = int(input())

    if x == target and position == 0:
        position = i

print(position)"""

FIXED_CPP = """#include <iostream>

int main() {
    int n, target;
    std::cin >> n >> target;

    int position = 0;

    for (int i = 1; i <= n; i++) {
        int x;
        std::cin >> x;

        if (x == target) {
            position = i;
        }
    }

    std::cout << position;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int n, target;
    std::cin >> n >> target;

    int position = 0;

    for (int i = 1; i <= n; i++) {
        int x;
        std::cin >> x;

        if (x == target && position == 0) {
            position = i;
        }
    }

    std::cout << position;
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();

        int n = int.Parse(first[0]);
        int target = int.Parse(first[1]);

        int position = 0;

        for (int i = 1; i <= n; i++) {
            int x = int.Parse(Console.ReadLine());

            if (x == target) {
                position = i;
            }
        }

        Console.WriteLine(position);
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();

        int n = int.Parse(first[0]);
        int target = int.Parse(first[1]);

        int position = 0;

        for (int i = 1; i <= n; i++) {
            int x = int.Parse(Console.ReadLine());

            if (x == target && position == 0) {
                position = i;
            }
        }

        Console.WriteLine(position);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int target = sc.nextInt();

        int position = 0;

        for (int i = 1; i <= n; i++) {
            int x = sc.nextInt();

            if (x == target) {
                position = i;
            }
        }

        System.out.println(position);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int target = sc.nextInt();

        int position = 0;

        for (int i = 1; i <= n; i++) {
            int x = sc.nextInt();

            if (x == target && position == 0) {
                position = i;
            }
        }

        System.out.println(position);
    }
}"""
