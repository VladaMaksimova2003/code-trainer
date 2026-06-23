PASCAL = """function GCD(a, b: integer): integer;
var t: integer;
begin
  while b <> 0 do
  begin
    t := a mod b;
    a := b;
    b := t;
  end;

  GCD := a;
end;

var a, b: integer;
begin
  readln(a, b);
  writeln(GCD(a, b));
end."""

PYTHON = """def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

a, b = map(int, input().split())
print(gcd(a, b))"""

CPP = """#include <iostream>

int gcd(int a, int b) {
    while (b != 0) {
        int t = a % b;
        a = b;
        b = t;
    }

    return a;
}

int main() {
    int a, b;
    std::cin >> a >> b;

    std::cout << gcd(a, b);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static int Gcd(int a, int b) {
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }

        return a;
    }

    static void Main() {
        string[] p = Console.ReadLine().Split();

        int a = int.Parse(p[0]);
        int b = int.Parse(p[1]);

        Console.WriteLine(Gcd(a, b));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static int gcd(int a, int b) {
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }

        return a;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int b = sc.nextInt();

        System.out.println(gcd(a, b));
    }
}"""
