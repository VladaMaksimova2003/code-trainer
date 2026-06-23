PASCAL = """var s: string;
    i: integer;
    c: char;
    count: array['a'..'z'] of integer;
begin
  readln(s);

  for c := 'a' to 'z' do
    count[c] := 0;

  for i := 1 to length(s) do
    if (s[i] >= 'a') and (s[i] <= 'z') then
      count[s[i]] := count[s[i]] + 1;

  for c := 'a' to 'z' do
    if count[c] > 0 then
      writeln(c, ' ', count[c]);
end."""

PYTHON = """s = input()
freq = {}

for ch in s:
    if ch.isalpha() and 'a' <= ch <= 'z':
        freq[ch] = freq.get(ch, 0) + 1

for ch in sorted(freq):
    print(ch, freq[ch])"""

CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::map<char, int> freq;

    for (char ch : s) {
        if (ch >= 'a' && ch <= 'z') {
            freq[ch]++;
        }
    }

    for (auto item : freq) {
        std::cout << item.first << ' ' << item.second << '\\n';
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string s = Console.ReadLine();
        SortedDictionary<char, int> freq = new SortedDictionary<char, int>();

        foreach (char ch in s) {
            if (ch >= 'a' && ch <= 'z') {
                if (!freq.ContainsKey(ch)) freq[ch] = 0;
                freq[ch]++;
            }
        }

        foreach (var item in freq) {
            Console.WriteLine($"{item.Key} {item.Value}");
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();

        TreeMap<Character, Integer> freq = new TreeMap<>();

        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);

            if (ch >= 'a' && ch <= 'z') {
                freq.put(ch, freq.getOrDefault(ch, 0) + 1);
            }
        }

        for (char ch : freq.keySet()) {
            System.out.println(ch + " " + freq.get(ch));
        }
    }
}"""
