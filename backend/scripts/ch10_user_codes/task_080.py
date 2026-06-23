FIXED_PASCAL = """var words: array[1..100] of string;
    freq: array[1..100] of integer;
    s, token: string;
    i, j, n, posSpace, bestIndex: integer;
    found: boolean;
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
        freq[j] := freq[j] + 1;
        found := true;
      end;

    if not found then
    begin
      n := n + 1;
      words[n] := token;
      freq[n] := 1;
    end;
  end;

  bestIndex := 1;

  for i := 2 to n do
    if (freq[i] > freq[bestIndex]) or
       ((freq[i] = freq[bestIndex]) and (words[i] < words[bestIndex])) then
      bestIndex := i;

  writeln(words[bestIndex], ' ', freq[bestIndex]);
end."""

BUGGY_PASCAL = """var words: array[1..100] of string;
    freq: array[1..100] of integer;
    s, token: string;
    i, j, n, posSpace, bestIndex: integer;
    found: boolean;
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
        freq[j] := freq[j] + 1;
        found := true;
      end;

    if not found then
    begin
      n := n + 1;
      words[n] := token;
      freq[n] := 1;
    end;
  end;

  bestIndex := 1;

  for i := 1 to n do
    if freq[i] >= freq[bestIndex] then
      bestIndex := i;

  writeln(words[bestIndex], ' ', freq[bestIndex]);
end."""

FIXED_PYTHON = """words = input().split()

freq = {}

for word in words:
    freq[word] = freq.get(word, 0) + 1

best_word = ''
best_count = 0

for word in sorted(freq):
    if freq[word] > best_count:
        best_count = freq[word]
        best_word = word

print(best_word, best_count)"""

BUGGY_PYTHON = """words = input().split()

freq = {}

for word in words:
    freq[word] = 1

best_word = max(freq)

print(best_word, freq[best_word])"""

FIXED_CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> freq;
    std::string word;

    while (std::cin >> word) {
        freq[word]++;
    }

    std::string bestWord;
    int bestCount = 0;

    for (auto item : freq) {
        if (item.second > bestCount) {
            bestCount = item.second;
            bestWord = item.first;
        }
    }

    std::cout << bestWord << ' ' << bestCount;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <map>
#include <string>
#include <algorithm>

int main() {
    std::map<std::string, int> freq;
    std::string word;

    while (std::cin >> word) {
        freq[word]++;
    }

    auto best = std::max_element(freq.begin(), freq.end());

    std::cout << best->first << ' ' << best->second;
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string[] words = Console.ReadLine().Split();
        SortedDictionary<string, int> freq = new SortedDictionary<string, int>();

        foreach (string word in words) {
            if (!freq.ContainsKey(word)) freq[word] = 0;
            freq[word]++;
        }

        string bestWord = "";
        int bestCount = 0;

        foreach (var item in freq) {
            if (item.Value > bestCount) {
                bestWord = item.Key;
                bestCount = item.Value;
            }
        }

        Console.WriteLine($"{bestWord} {bestCount}");
    }
}"""

BUGGY_CSHARP = """using System;
using System.Linq;
using System.Collections.Generic;

class Program {
    static void Main() {
        var words = Console.ReadLine().Split();

        var freq = words.ToDictionary(
            x => x,
            x => 1
        );

        var best = freq.OrderByDescending(
            x => x.Key
        ).First();

        Console.WriteLine(best.Key + " " + best.Value);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        TreeMap<String, Integer> freq = new TreeMap<>();

        while (sc.hasNext()) {
            String word = sc.next();
            freq.put(word, freq.getOrDefault(word, 0) + 1);
        }

        String bestWord = "";
        int bestCount = 0;

        for (String word : freq.keySet()) {
            if (freq.get(word) > bestCount) {
                bestWord = word;
                bestCount = freq.get(word);
            }
        }

        System.out.println(bestWord + " " + bestCount);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        HashMap<String, Integer> freq = new HashMap<>();
        Scanner sc = new Scanner(System.in);

        while (sc.hasNext()) {
            String word = sc.next();
            freq.put(word, 1);
        }

        String bestWord = "";
        int bestCount = 0;

        for (String word : freq.keySet()) {
            if (word.compareTo(bestWord) > 0) {
                bestWord = word;
                bestCount = freq.get(word);
            }
        }

        System.out.println(bestWord + " " + bestCount);
    }
}"""
