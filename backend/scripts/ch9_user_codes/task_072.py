PASCAL = """var n, i, amount, totalPaid, countPaid, maxPaid: integer;
    category, status: string;
begin
  readln(n);

  totalPaid := 0;
  countPaid := 0;
  maxPaid := 0;

  for i := 1 to n do
  begin
    readln(category, status, amount);

    if status = 'paid' then
    begin
      totalPaid := totalPaid + amount;
      countPaid := countPaid + 1;

      if amount > maxPaid then
        maxPaid := amount;
    end;
  end;

  writeln(totalPaid, ' ', countPaid, ' ', maxPaid);
end."""

PYTHON = """n = int(input())

total_paid = 0
count_paid = 0
max_paid = 0

for _ in range(n):
    category, status, amount = input().split()
    amount = int(amount)

    if status == 'paid':
        total_paid += amount
        count_paid += 1

        if amount > max_paid:
            max_paid = amount

print(total_paid, count_paid, max_paid)"""

CPP = """#include <iostream>
#include <string>

int main() {
    int n;
    std::cin >> n;

    int totalPaid = 0;
    int countPaid = 0;
    int maxPaid = 0;

    for (int i = 0; i < n; i++) {
        std::string category, status;
        int amount;

        std::cin >> category >> status >> amount;

        if (status == "paid") {
            totalPaid += amount;
            countPaid++;

            if (amount > maxPaid) {
                maxPaid = amount;
            }
        }
    }

    std::cout << totalPaid << ' ' << countPaid << ' ' << maxPaid;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        int totalPaid = 0;
        int countPaid = 0;
        int maxPaid = 0;

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            string category = p[0];
            string status = p[1];
            int amount = int.Parse(p[2]);

            if (status == "paid") {
                totalPaid += amount;
                countPaid++;

                if (amount > maxPaid) {
                    maxPaid = amount;
                }
            }
        }

        Console.WriteLine($"{totalPaid} {countPaid} {maxPaid}");
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        int totalPaid = 0;
        int countPaid = 0;
        int maxPaid = 0;

        for (int i = 0; i < n; i++) {
            String category = sc.next();
            String status = sc.next();
            int amount = sc.nextInt();

            if (status.equals("paid")) {
                totalPaid += amount;
                countPaid++;

                if (amount > maxPaid) {
                    maxPaid = amount;
                }
            }
        }

        System.out.println(totalPaid + " " + countPaid + " " + maxPaid);
    }
}"""
