PASCAL = """var n, i: integer;
begin
  readln(n);

  for i := 1 to n do
  begin
    if i > 1 then
      write(' ');
    write(n * i);
  end;
end."""

PYTHON = """n = int(input())

print(' '.join(str(n * i) for i in range(1, n + 1)))"""

CPP = """#include <iostream>

int main() {
    int n;
    std::cin >> n;

    for (int i = 1; i <= n; i++) {
        if (i > 1) {
            std::cout << ' ';
        }
        std::cout << n * i;
    }

    return 0;
}"""

CSHARP = """using System;
using System.Linq;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Console.WriteLine(string.Join(" ", Enumerable.Range(1, n).Select(i => n * i)));
    }
}"""

JAVA = """import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= n; i++) {
            if (i > 1) {
                sb.append(' ');
            }
            sb.append(n * i);
        }
        System.out.println(sb);
    }
}"""
