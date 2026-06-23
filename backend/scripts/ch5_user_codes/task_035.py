PASCAL = """var s: string;
    i: integer;
    ok: boolean;
begin
  readln(s);

  ok := true;

  for i := 1 to length(s) do
    if s[i] <> s[length(s) - i + 1] then
      ok := false;

  if ok then
    writeln('yes')
  else
    writeln('no');
end."""

PYTHON = """s = input()
print('yes' if s == s[::-1] else 'no')"""

CPP = """#include <iostream>
#include <string>
#include <algorithm>

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::string r = s;
    std::reverse(r.begin(), r.end());

    std::cout << (s == r ? "yes" : "no");
    return 0;
}"""

CSHARP = """using System;
using System.Linq;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        string r = new string(s.Reverse().ToArray());
        Console.WriteLine(s == r ? "yes" : "no");
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        String r = new StringBuilder(s).reverse().toString();

        System.out.println(s.equals(r) ? "yes" : "no");
    }
}"""
