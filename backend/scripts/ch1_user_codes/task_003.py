PASCAL = """var n, i, ping, best: integer;
begin
  readln(n);
  readln(best);

  for i := 2 to n do
  begin
    readln(ping);

    if ping < best then
      best := ping;
  end;

  writeln(best);
end."""

PYTHON = """n = int(input())
pings = [int(input()) for _ in range(n)]

best = pings[0]

for ping in pings:
    if ping < best:
        best = ping

print(best)"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> pings(n);

    for (int i = 0; i < n; i++) {
        std::cin >> pings[i];
    }

    int best = pings[0];

    for (int ping : pings) {
        if (ping < best) {
            best = ping;
        }
    }

    std::cout << best;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        int[] pings = new int[n];

        for (int i = 0; i < n; i++) {
            pings[i] = int.Parse(Console.ReadLine());
        }

        int best = pings[0];

        foreach (int ping in pings) {
            if (ping < best) {
                best = ping;
            }
        }

        Console.WriteLine(best);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] pings = new int[n];

        for (int i = 0; i < n; i++) {
            pings[i] = sc.nextInt();
        }

        int best = pings[0];

        for (int ping : pings) {
            if (ping < best) {
                best = ping;
            }
        }

        System.out.println(best);
    }
}"""
