PASCAL = """var n, i, x: integer;
begin
  readln(n);

  for i := 1 to n do
  begin
    readln(x);

    if x > 0 then
      write(x, ' ');
  end;
end."""

PYTHON = """n = int(input())
result = []

for _ in range(n):
    x = int(input())

    if x > 0:
        result.append(x)

print(*result)"""

CPP = """#include <iostream>

int main() {
    int n, x;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        std::cin >> x;

        if (x > 0) {
            std::cout << x << ' ';
        }
    }

    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());

            if (x > 0) {
                Console.Write(x + " ");
            }
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();

            if (x > 0) {
                System.out.print(x + " ");
            }
        }
    }
}"""
