PASCAL = """var n, i, j: integer;
    words: array[1..100] of string;
    temp: string;
begin
  readln(n);

  for i := 1 to n do
    readln(words[i]);

  for i := 1 to n do
    for j := i + 1 to n do
      if words[j] < words[i] then
      begin
        temp := words[i];
        words[i] := words[j];
        words[j] := temp;
      end;

  for i := 1 to n do
    writeln(words[i]);
end."""

PYTHON = """n = int(input())
words = [input() for _ in range(n)]

words.sort()

for word in words:
    print(word)"""

CPP = """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

int main() {
    int n;
    std::cin >> n;
    std::cin.ignore();

    std::vector<std::string> words(n);

    for (int i = 0; i < n; i++) {
        std::getline(std::cin, words[i]);
    }

    std::sort(words.begin(), words.end());

    for (const std::string& word : words) {
        std::cout << word << '\n';
    }

    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        string[] words = new string[n];

        for (int i = 0; i < n; i++) {
            words[i] = Console.ReadLine();
        }

        Array.Sort(words);

        foreach (string word in words) {
            Console.WriteLine(word);
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = Integer.parseInt(sc.nextLine());
        String[] words = new String[n];

        for (int i = 0; i < n; i++) {
            words[i] = sc.nextLine();
        }

        Arrays.sort(words);

        for (String word : words) {
            System.out.println(word);
        }
    }
}"""
