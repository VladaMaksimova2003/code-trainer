PASCAL = """var t: integer;
begin
  readln(t);

  if t < 0 then
    writeln('freezing')
  else if t <= 25 then
    writeln('normal')
  else if t <= 35 then
    writeln('hot')
  else
    writeln('danger');
end."""

PYTHON = """t = int(input())

if t < 0:
    print('freezing')
elif t <= 25:
    print('normal')
elif t <= 35:
    print('hot')
else:
    print('danger')"""

CPP = """#include <iostream>

int main() {
    int t;
    std::cin >> t;

    if (t < 0) {
        std::cout << "freezing";
    } else if (t <= 25) {
        std::cout << "normal";
    } else if (t <= 35) {
        std::cout << "hot";
    } else {
        std::cout << "danger";
    }

    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int t = int.Parse(Console.ReadLine());

        if (t < 0) {
            Console.WriteLine("freezing");
        } else if (t <= 25) {
            Console.WriteLine("normal");
        } else if (t <= 35) {
            Console.WriteLine("hot");
        } else {
            Console.WriteLine("danger");
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int t = sc.nextInt();

        if (t < 0) {
            System.out.println("freezing");
        } else if (t <= 25) {
            System.out.println("normal");
        } else if (t <= 35) {
            System.out.println("hot");
        } else {
            System.out.println("danger");
        }
    }
}"""
