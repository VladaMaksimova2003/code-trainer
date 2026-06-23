PASCAL = """var a, b, c, m: integer;
begin
  readln(a, b, c);
  m := a;
  if b > m then m := b;
  if c > m then m := c;
  writeln(m);
end."""

PYTHON = """a, b, c = map(int, input().split())

m = a

if b > m:
    m = b

if c > m:
    m = c

print(m)"""

CPP = """#include <iostream>

int main() {
    int a, b, c, m;
    std::cin >> a >> b >> c;

    m = a;

    if (b > m) m = b;
    if (c > m) m = c;

    std::cout << m;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        string[] p = Console.ReadLine().Split();

        int a = int.Parse(p[0]);
        int b = int.Parse(p[1]);
        int c = int.Parse(p[2]);

        int m = a;

        if (b > m) m = b;
        if (c > m) m = c;

        Console.WriteLine(m);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int b = sc.nextInt();
        int c = sc.nextInt();

        int m = a;

        if (b > m) m = b;
        if (c > m) m = c;

        System.out.println(m);
    }
}"""
