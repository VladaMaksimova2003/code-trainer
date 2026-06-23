PASCAL = """var n, i, amount: integer;
    orderId, status: string;
begin
  readln(n);

  for i := 1 to n do
  begin
    readln(orderId, status, amount);

    if status = 'paid' then
      writeln(orderId, ' ', amount);
  end;
end."""

PYTHON = """n = int(input())

for _ in range(n):
    order_id, status, amount = input().split()

    if status == 'paid':
        print(order_id, amount)"""

CPP = """#include <iostream>
#include <string>

int main() {
    int n;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        std::string orderId, status;
        int amount;

        std::cin >> orderId >> status >> amount;

        if (status == "paid") {
            std::cout << orderId << ' ' << amount << '\\n';
        }
    }

    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            string orderId = p[0];
            string status = p[1];
            int amount = int.Parse(p[2]);

            if (status == "paid") {
                Console.WriteLine($"{orderId} {amount}");
            }
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        for (int i = 0; i < n; i++) {
            String orderId = sc.next();
            String status = sc.next();
            int amount = sc.nextInt();

            if (status.equals("paid")) {
                System.out.println(orderId + " " + amount);
            }
        }
    }
}"""
