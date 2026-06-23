PASCAL = """var s: string;
    i, chars, words, vowels: integer;
    inWord: boolean;
    c: char;
begin
  readln(s);

  chars := length(s);
  words := 0;
  vowels := 0;
  inWord := false;

  for i := 1 to length(s) do
  begin
    c := s[i];

    if c <> ' ' then
    begin
      if not inWord then
        words := words + 1;

      inWord := true;

      c := LowerCase(c);

      if (c = 'a') or (c = 'e') or (c = 'i') or (c = 'o') or (c = 'u') then
        vowels := vowels + 1;
    end
    else
      inWord := false;
  end;

  writeln(chars, ' ', words, ' ', vowels);
end."""

PYTHON = """s = input()

chars = len(s)
words = 0 if s.strip() == '' else len(s.split())
vowels = sum(1 for c in s if c.lower() in 'aeiou')

print(chars, words, vowels)"""

CPP = """#include <iostream>
#include <string>
#include <sstream>
#include <cctype>

bool isVowel(char c) {
    c = std::tolower(static_cast<unsigned char>(c));
    return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
}

int main() {
    std::string s;
    std::getline(std::cin, s);

    int chars = static_cast<int>(s.size());
    int words = 0;

    if (!s.empty()) {
        std::stringstream ss(s);
        std::string word;
        while (ss >> word) {
            words++;
        }
    }

    int vowels = 0;
    for (char c : s) {
        if (isVowel(c)) {
            vowels++;
        }
    }

    std::cout << chars << ' ' << words << ' ' << vowels;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static bool IsVowel(char c) {
        c = char.ToLower(c);
        return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
    }

    static void Main() {
        string s = Console.ReadLine();

        int chars = s.Length;
        string[] words = s.Split(
            new char[] { ' ' },
            StringSplitOptions.RemoveEmptyEntries
        );
        int wordCount = words.Length;
        int vowels = 0;

        foreach (char c in s) {
            if (IsVowel(c)) {
                vowels++;
            }
        }

        Console.WriteLine($"{chars} {wordCount} {vowels}");
    }
}"""

JAVA = """import java.util.*;

class Main {
    static boolean isVowel(char c) {
        c = Character.toLowerCase(c);
        return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();

        int chars = s.length();
        String trimmed = s.trim();
        int words = trimmed.isEmpty() ? 0 : trimmed.split("\\s+").length;
        int vowels = 0;

        for (int i = 0; i < s.length(); i++) {
            if (isVowel(s.charAt(i))) {
                vowels++;
            }
        }

        System.out.println(chars + " " + words + " " + vowels);
    }
}"""
