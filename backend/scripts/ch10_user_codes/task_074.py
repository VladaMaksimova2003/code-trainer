PASCAL = """var words: array[1..100] of string;
    values: array[1..100] of integer;
    s, token: string;
    i, j, n, posSpace: integer;
    found: boolean;
    tmpName: string;
    tmpVal: integer;
begin
  readln(s);
  n := 0;
  s := trim(s);

  while s <> '' do
  begin
    posSpace := pos(' ', s);
    if posSpace = 0 then
    begin
      token := s;
      s := '';
    end
    else
    begin
      token := copy(s, 1, posSpace - 1);
      delete(s, 1, posSpace);
      while (length(s) > 0) and (s[1] = ' ') do
        delete(s, 1, 1);
    end;

    if token = '' then
      continue;

    found := false;
    for j := 1 to n do
      if words[j] = token then
      begin
        values[j] := values[j] + 1;
        found := true;
      end;

    if not found then
    begin
      n := n + 1;
      words[n] := token;
      values[n] := 1;
    end;
  end;

  for i := 1 to n do
    for j := i + 1 to n do
      if words[j] < words[i] then
      begin
        tmpName := words[i];
        words[i] := words[j];
        words[j] := tmpName;
        tmpVal := values[i];
        values[i] := values[j];
        values[j] := tmpVal;
      end;

  for i := 1 to n do
    writeln(words[i], ' ', values[i]);
end."""

PYTHON = """words = input().split()
freq = {}

for word in words:
    freq[word] = freq.get(word, 0) + 1

for word in sorted(freq):
    print(word, freq[word])"""

CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> freq;
    std::string word;

    while (std::cin >> word) {
        freq[word]++;
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
        string[] words = Console.ReadLine().Split();
        SortedDictionary<string, int> freq = new SortedDictionary<string, int>();

        foreach (string word in words) {
            if (!freq.ContainsKey(word)) freq[word] = 0;
            freq[word]++;
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
        TreeMap<String, Integer> freq = new TreeMap<>();

        while (sc.hasNext()) {
            String word = sc.next();
            freq.put(word, freq.getOrDefault(word, 0) + 1);
        }

        for (String word : freq.keySet()) {
            System.out.println(word + " " + freq.get(word));
        }
    }
}"""
