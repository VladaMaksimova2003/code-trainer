FIXED_PASCAL = """var a, b, c: integer;
begin
  readln(a, b, c);

  if (a <= 0) or (b <= 0) or (c <= 0) or
     (a + b <= c) or (a + c <= b) or (b + c <= a) then
    writeln('invalid')
  else if (a = b) and (b = c) then
    writeln('equilateral')
  else if (a = b) or (a = c) or (b = c) then
    writeln('isosceles')
  else
    writeln('scalene');
end."""

BUGGY_PASCAL = """var a, b, c: integer;
begin
  input(a, b, c);

  if a == b == c then
    writeln('equilateral')
  else if (a = b) || (a = c) || (b = c) then
    print('isosceles')
  else
    writeln('scalene');
end."""

FIXED_PYTHON = """a, b, c = map(int, input().split())

if a <= 0 or b <= 0 or c <= 0 or a + b <= c or a + c <= b or b + c <= a:
    print('invalid')
elif a == b == c:
    print('equilateral')
elif a == b or a == c or b == c:
    print('isosceles')
else:
    print('scalene')"""

BUGGY_PYTHON = """a, b, c = input().split()

if a = b = c:
    print('equilateral')
elif a == b || a == c || b == c:
    Console.WriteLine('isosceles')
else:
    print('scalene')"""

FIXED_CPP = """#include <iostream>

int main() {
    int a, b, c;
    std::cin >> a >> b >> c;

    if (a <= 0 || b <= 0 || c <= 0 ||
        a + b <= c || a + c <= b || b + c <= a) {
        std::cout << "invalid";
    } else if (a == b && b == c) {
        std::cout << "equilateral";
    } else if (a == b || a == c || b == c) {
        std::cout << "isosceles";
    } else {
        std::cout << "scalene";
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int a, b, c;
    cin >> a >> b >> c;

    if (a = b && b = c) {
        cout << "equilateral";
    } else if (a == b or a == c or b == c) {
        print("isosceles");
    } else {
        cout << "scalene";
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        string[] p = Console.ReadLine().Split();

        int a = int.Parse(p[0]);
        int b = int.Parse(p[1]);
        int c = int.Parse(p[2]);

        if (a <= 0 || b <= 0 || c <= 0 ||
            a + b <= c || a + c <= b || b + c <= a) {
            Console.WriteLine("invalid");
        } else if (a == b && b == c) {
            Console.WriteLine("equilateral");
        } else if (a == b || a == c || b == c) {
            Console.WriteLine("isosceles");
        } else {
            Console.WriteLine("scalene");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int a, b, c;
        scanf("%d %d %d", a, b, c);

        if (a = b && b = c) {
            print("equilateral");
        } else if (a == b or a == c or b == c) {
            Console.WriteLine("isosceles");
        } else {
            cout << "scalene";
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int b = sc.nextInt();
        int c = sc.nextInt();

        if (a <= 0 || b <= 0 || c <= 0 ||
            a + b <= c || a + c <= b || b + c <= a) {
            System.out.println("invalid");
        } else if (a == b && b == c) {
            System.out.println("equilateral");
        } else if (a == b || a == c || b == c) {
            System.out.println("isosceles");
        } else {
            System.out.println("scalene");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = input();
        int b = input();
        int c = input();

        if (a = b && b = c) {
            System.out.println("equilateral");
        } else if (a == b || a == c || b == c) {
            Console.WriteLine("isosceles");
        } else {
            print("scalene");
        }
    }
}"""
