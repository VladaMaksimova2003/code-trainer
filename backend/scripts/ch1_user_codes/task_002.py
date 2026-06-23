PASCAL = """var n, i, code, target, position: integer;
begin
  readln(n, target);

  position := 0;

  for i := 1 to n do
  begin
    readln(code);

    if (code = target) and (position = 0) then
      position := i;
  end;

  writeln(position);
end."""

PYTHON = """n, target = map(int, input().split())

position = 0

for i in range(1, n + 1):
    code = int(input())

    if code == target and position == 0:
        position = i

print(position)"""

CPP = """#include <iostream>

int main() {
    int n, target, code;
    int position = 0;

    std::cin >> n >> target;

    for (int i = 1; i <= n; i++) {
        std::cin >> code;

        if (code == target && position == 0) {
            position = i;
        }
    }

    std::cout << position;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();

        int n = int.Parse(first[0]);
        int target = int.Parse(first[1]);
        int position = 0;

        for (int i = 1; i <= n; i++) {
            int code = int.Parse(Console.ReadLine());

            if (code == target && position == 0) {
                position = i;
            }
        }

        Console.WriteLine(position);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int target = sc.nextInt();

        int position = 0;

        for (int i = 1; i <= n; i++) {
            int code = sc.nextInt();

            if (code == target && position == 0) {
                position = i;
            }
        }

        System.out.println(position);
    }
}"""
