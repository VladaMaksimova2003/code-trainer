PASCAL = """var x, total: integer;
begin
  total := 0;
  readln(x);

  while x <> 0 do
  begin
    total := total + x;
    readln(x);
  end;

  writeln(total);
end."""

PYTHON = """total = 0
x = int(input())

while x != 0:
    total += x
    x = int(input())

print(total)"""

CPP = """#include <iostream>

int main() {
    int x, total = 0;
    std::cin >> x;

    while (x != 0) {
        total += x;
        std::cin >> x;
    }

    std::cout << total;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int total = 0;
        int x = int.Parse(Console.ReadLine());

        while (x != 0) {
            total += x;
            x = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(total);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int total = 0;
        int x = sc.nextInt();

        while (x != 0) {
            total += x;
            x = sc.nextInt();
        }

        System.out.println(total);
    }
}"""
