PASCAL = """function MaxValue(a, b: integer): integer;
begin
  if a > b then
    MaxValue := a
  else
    MaxValue := b;
end;

var a, b: integer;
begin
  readln(a, b);
  writeln(MaxValue(a, b));
end."""

PYTHON = """def max_value(a, b):
    if a > b:
        return a
    return b

a, b = map(int, input().split())
print(max_value(a, b))"""

CPP = """#include <iostream>

int maxValue(int a, int b) {
    if (a > b) {
        return a;
    }
    return b;
}

int main() {
    int a, b;
    std::cin >> a >> b;

    std::cout << maxValue(a, b);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static int MaxValue(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }

    static void Main() {
        string[] p = Console.ReadLine().Split();

        int a = int.Parse(p[0]);
        int b = int.Parse(p[1]);

        Console.WriteLine(MaxValue(a, b));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static int maxValue(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int b = sc.nextInt();

        System.out.println(maxValue(a, b));
    }
}"""
