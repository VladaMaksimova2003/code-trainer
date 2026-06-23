PASCAL = """function Normalize(s: string): string;
begin
  Normalize := LowerCase(Trim(s));
end;

var s: string;
begin
  readln(s);
  writeln(Normalize(s));
end."""

PYTHON = """def normalize(text):
    return text.strip().lower()

s = input()
print(normalize(s))"""

CPP = """#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>

std::string normalize(std::string s) {
    while (!s.empty() && s.front() == ' ') {
        s.erase(s.begin());
    }

    while (!s.empty() && s.back() == ' ') {
        s.pop_back();
    }

    for (char& c : s) {
        c = std::tolower(c);
    }

    return s;
}

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::cout << normalize(s);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static string Normalize(string text) {
        return text.Trim().ToLower();
    }

    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(Normalize(s));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static String normalize(String text) {
        return text.trim().toLowerCase();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        System.out.println(normalize(s));
    }
}"""
