PASCAL = """function Fib(n: integer): integer;
begin
  if n <= 1 then
    Fib := n
  else
    Fib := Fib(n - 1) + Fib(n - 2);
end;

var n: integer;
begin
  readln(n);
  writeln(Fib(n));
end."""

PYTHON = """def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

n = int(input())
print(fib(n))"""

CPP = """#include <iostream>

int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    int n;
    std::cin >> n;
    std::cout << fib(n);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static int Fib(int n) {
        if (n <= 1) return n;
        return Fib(n - 1) + Fib(n - 2);
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Console.WriteLine(Fib(n));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static int fib(int n) {
        if (n <= 1) return n;
        return fib(n - 1) + fib(n - 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(fib(n));
    }
}"""
