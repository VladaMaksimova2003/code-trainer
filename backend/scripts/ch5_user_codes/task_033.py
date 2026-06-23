PASCAL = """var s: string;
begin
  readln(s);
  writeln(length(s));
end."""

PYTHON = """s = input()
print(len(s))"""

CPP = """#include <iostream>
#include <string>

int main() {
    std::string s;
    std::getline(std::cin, s);
    std::cout << s.size();
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(s.Length);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        System.out.println(s.length());
    }
}"""
