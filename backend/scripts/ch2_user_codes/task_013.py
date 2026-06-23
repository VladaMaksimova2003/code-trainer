FIXED_PASCAL = """var score: integer;
begin
  readln(score);

  if (score < 0) or (score > 100) then
    writeln('invalid')
  else if score >= 90 then
    writeln('excellent')
  else if score >= 70 then
    writeln('good')
  else if score >= 50 then
    writeln('satisfactory')
  else
    writeln('retry');
end."""

BUGGY_PASCAL = """var score: integer;
begin
  score = int(input());

  if score < 0 || score > 100 then
    print('invalid')
  elif score >= 90 then
    writeln('excellent')
  elif score >= 70 then
    writeln('good')
  elif score >= 50 then
    writeln('satisfactory')
  else
    writeln('retry');
end."""

FIXED_PYTHON = """score = int(input())

if score < 0 or score > 100:
    print('invalid')
elif score >= 90:
    print('excellent')
elif score >= 70:
    print('good')
elif score >= 50:
    print('satisfactory')
else:
    print('retry')"""

BUGGY_PYTHON = """score = int.Parse(input())

if score < 0 || score > 100:
    Console.WriteLine("invalid")
else if score >= 90:
    print("excellent")
else if score >= 70:
    print("good")
else if score >= 50:
    print("satisfactory")
else:
    print("retry")"""

FIXED_CPP = """#include <iostream>

int main() {
    int score;
    std::cin >> score;

    if (score < 0 || score > 100) {
        std::cout << "invalid";
    } else if (score >= 90) {
        std::cout << "excellent";
    } else if (score >= 70) {
        std::cout << "good";
    } else if (score >= 50) {
        std::cout << "satisfactory";
    } else {
        std::cout << "retry";
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int score;
    score = int(input());

    if score < 0 || score > 100 {
        std::cout << "invalid";
    } else if score >= 90 {
        print("excellent");
    } else if score >= 70 {
        std::cout << "good";
    } else if score >= 50 {
        Console.WriteLine("satisfactory");
    } else {
        std::cout << "retry";
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int score = int.Parse(Console.ReadLine());

        if (score < 0 || score > 100) {
            Console.WriteLine("invalid");
        } else if (score >= 90) {
            Console.WriteLine("excellent");
        } else if (score >= 70) {
            Console.WriteLine("good");
        } else if (score >= 50) {
            Console.WriteLine("satisfactory");
        } else {
            Console.WriteLine("retry");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int score = int(input());

        if score < 0 || score > 100 {
            Console.WriteLine("invalid");
        } else if score >= 90 {
            print("excellent");
        } else if score >= 70 {
            Console.WriteLine("good");
        } else if score >= 50 {
            cout << "satisfactory";
        } else {
            Console.WriteLine("retry");
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int score = sc.nextInt();

        if (score < 0 || score > 100) {
            System.out.println("invalid");
        } else if (score >= 90) {
            System.out.println("excellent");
        } else if (score >= 70) {
            System.out.println("good");
        } else if (score >= 50) {
            System.out.println("satisfactory");
        } else {
            System.out.println("retry");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int score = int(input());

        if score < 0 || score > 100 {
            System.out.println("invalid");
        } else if score >= 90 {
            print("excellent");
        } else if score >= 70 {
            System.out.println("good");
        } else if score >= 50 {
            Console.WriteLine("satisfactory");
        } else {
            System.out.println("retry");
        }
    }
}"""
