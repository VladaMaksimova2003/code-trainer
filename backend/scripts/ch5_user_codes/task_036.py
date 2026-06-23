FIXED_PASCAL = """var s, p: string;
    i, pos: integer;
begin
  readln(s);
  readln(p);

  pos := 0;

  if length(p) > 0 then
    for i := 1 to length(s) - length(p) + 1 do
      if (pos = 0) and (copy(s, i, length(p)) = p) then
        pos := i;

  writeln(pos);
end."""

BUGGY_PASCAL = """var s, p: string;
    pos: integer;
begin
  readln(s);
  readln(p);

  pos := Pos(p, s);

  writeln(pos);
end."""

FIXED_PYTHON = """s = input()
p = input()

idx = s.find(p)

print(idx + 1 if idx >= 0 else 0)"""

BUGGY_PYTHON = """s = input()
p = input()

idx = s.find(p)

print(idx if idx >= 0 else 0)"""

FIXED_CPP = """#include <iostream>
#include <string>

int main() {
    std::string s, p;
    std::getline(std::cin, s);
    std::getline(std::cin, p);

    size_t idx = s.find(p);
    int pos = (idx == std::string::npos) ? 0 : (int)idx + 1;

    std::cout << pos;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <string>

int main() {
    std::string s, p;
    std::getline(std::cin, s);
    std::getline(std::cin, p);

    size_t idx = s.find(p);
    int pos = (idx == std::string::npos) ? 0 : (int)idx;

    std::cout << pos;
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        string p = Console.ReadLine();

        int idx = s.IndexOf(p);
        Console.WriteLine(idx >= 0 ? idx + 1 : 0);
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        string p = Console.ReadLine();

        int idx = s.IndexOf(p);
        Console.WriteLine(idx >= 0 ? idx : 0);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        String p = sc.nextLine();

        int idx = s.indexOf(p);
        System.out.println(idx >= 0 ? idx + 1 : 0);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        String p = sc.nextLine();

        int idx = s.indexOf(p);
        System.out.println(idx >= 0 ? idx : 0);
    }
}"""
