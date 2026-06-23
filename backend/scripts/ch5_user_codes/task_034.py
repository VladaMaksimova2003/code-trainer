PASCAL = """var s, r: string;
    i: integer;
begin
  readln(s);
  r := '';

  for i := length(s) downto 1 do
    r := r + s[i];

  writeln(r);
end."""

PYTHON = """s = input()
print(s[::-1])"""

CPP = """#include <iostream>
#include <string>
#include <algorithm>

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::reverse(s.begin(), s.end());

    std::cout << s;
    return 0;
}"""

CSHARP = """using System;
using System.Linq;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(new string(s.Reverse().ToArray()));
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();

        System.out.println(new StringBuilder(s).reverse().toString());
    }
}"""
