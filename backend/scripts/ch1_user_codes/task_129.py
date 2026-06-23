PASCAL = """var n, s, d: integer;
begin
  readln(n);
  if n < 0 then n := -n;
  s := 0;
  while n > 0 do
  begin
    d := n mod 10;
    s := s + d;
    n := n div 10;
  end;
  writeln(s);
end."""

PYTHON = """n = int(input())
if n < 0:
    n = -n
s = 0
while n > 0:
    s += n % 10
    n //= 10
print(s)"""

CPP = """#include <iostream>

int main() {
    int n, s = 0;
    std::cin >> n;
    if (n < 0) n = -n;
    while (n > 0) {
        s += n % 10;
        n /= 10;
    }
    std::cout << s;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        if (n < 0) n = -n;
        int s = 0;
        while (n > 0) {
            s += n % 10;
            n /= 10;
        }
        Console.WriteLine(s);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        if (n < 0) n = -n;
        int s = 0;
        while (n > 0) {
            s += n % 10;
            n /= 10;
        }
        System.out.println(s);
    }
}"""
