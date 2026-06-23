PASCAL = """var age, income, debt, score: integer;
begin
  readln(age, income, debt, score);

  if (age >= 18) and
     (income >= 30000) and
     (debt * 10 <= income * 4) and
     (score >= 650) then
    writeln('accepted')
  else if (age >= 18) and
          (income >= 20000) and
          (debt * 10 <= income * 6) and
          (score >= 550) then
    writeln('review')
  else
    writeln('rejected');
end."""

PYTHON = """age, income, debt, score = map(int, input().split())

if age >= 18 and income >= 30000 and debt * 10 <= income * 4 and score >= 650:
    print('accepted')
elif age >= 18 and income >= 20000 and debt * 10 <= income * 6 and score >= 550:
    print('review')
else:
    print('rejected')"""

CPP = """#include <iostream>

int main() {
    int age, income, debt, score;
    std::cin >> age >> income >> debt >> score;

    if (age >= 18 &&
        income >= 30000 &&
        debt * 10 <= income * 4 &&
        score >= 650) {
        std::cout << "accepted";
    } else if (age >= 18 &&
               income >= 20000 &&
               debt * 10 <= income * 6 &&
               score >= 550) {
        std::cout << "review";
    } else {
        std::cout << "rejected";
    }

    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        string[] p = Console.ReadLine().Split();

        int age = int.Parse(p[0]);
        int income = int.Parse(p[1]);
        int debt = int.Parse(p[2]);
        int score = int.Parse(p[3]);

        if (age >= 18 &&
            income >= 30000 &&
            debt * 10 <= income * 4 &&
            score >= 650) {
            Console.WriteLine("accepted");
        } else if (age >= 18 &&
                   income >= 20000 &&
                   debt * 10 <= income * 6 &&
                   score >= 550) {
            Console.WriteLine("review");
        } else {
            Console.WriteLine("rejected");
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int age = sc.nextInt();
        int income = sc.nextInt();
        int debt = sc.nextInt();
        int score = sc.nextInt();

        if (age >= 18 &&
            income >= 30000 &&
            debt * 10 <= income * 4 &&
            score >= 650) {
            System.out.println("accepted");
        } else if (age >= 18 &&
                   income >= 20000 &&
                   debt * 10 <= income * 6 &&
                   score >= 550) {
            System.out.println("review");
        } else {
            System.out.println("rejected");
        }
    }
}"""
