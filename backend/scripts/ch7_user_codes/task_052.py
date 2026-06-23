PASCAL = """function FastPower(a, n: integer): integer;
var half: integer;
begin
  if n = 0 then
    FastPower := 1
  else
  begin
    half := FastPower(a, n div 2);

    if n mod 2 = 0 then
      FastPower := half * half
    else
      FastPower := half * half * a;
  end;
end;

var a, n: integer;
begin
  readln(a, n);
  writeln(FastPower(a, n));
end."""

PYTHON = """def fast_power(a, n):
    if n == 0:
        return 1

    half = fast_power(a, n // 2)

    if n % 2 == 0:
        return half * half

    return half * half * a

a, n = map(int, input().split())
print(fast_power(a, n))"""

CPP = """#include <iostream>

int fastPower(int a, int n) {
    if (n == 0) return 1;

    int half = fastPower(a, n / 2);

    if (n % 2 == 0) {
        return half * half;
    }

    return half * half * a;
}

int main() {
    int a, n;
    std::cin >> a >> n;

    std::cout << fastPower(a, n);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static int FastPower(int a, int n) {
        if (n == 0) return 1;

        int half = FastPower(a, n / 2);

        if (n % 2 == 0) {
            return half * half;
        }

        return half * half * a;
    }

    static void Main() {
        string[] p = Console.ReadLine().Split();

        int a = int.Parse(p[0]);
        int n = int.Parse(p[1]);

        Console.WriteLine(FastPower(a, n));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static int fastPower(int a, int n) {
        if (n == 0) return 1;

        int half = fastPower(a, n / 2);

        if (n % 2 == 0) {
            return half * half;
        }

        return half * half * a;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int n = sc.nextInt();

        System.out.println(fastPower(a, n));
    }
}"""
