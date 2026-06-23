FIXED_PASCAL = """var s: string;
    i, j, n, tmpCount: integer;
    words: array[1..100] of string;
    counts: array[1..100] of integer;
    token: string;
    posSpace: integer;
    tmp: string;
begin
  readln(s);
  n := 0;

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

    j := 0;
    for i := 1 to n do
      if words[i] = token then
      begin
        j := i;
        break;
      end;

    if j > 0 then
      counts[j] := counts[j] + 1
    else
    begin
      n := n + 1;
      words[n] := token;
      counts[n] := 1;
    end;
  end;

  for i := 1 to n do
    for j := i + 1 to n do
      if words[j] < words[i] then
      begin
        tmp := words[i];
        words[i] := words[j];
        words[j] := tmp;
        tmpCount := counts[i];
        counts[i] := counts[j];
        counts[j] := tmpCount;
      end;

  for i := 1 to n do
    writeln(words[i], ' ', counts[i]);
end."""

BUGGY_PASCAL = """var s: string;
    freq: Dictionary<string, integer>;
begin
  s := Console.ReadLine();

  for item in s.split() do
    freq[item]++;

  for key in sorted(freq) do
    print(key, freq[key]);
end."""

FIXED_PYTHON = """data = input().split()
freq = {}

for item in data:
    freq[item] = freq.get(item, 0) + 1

for key in sorted(freq):
    print(key, freq[key])"""

BUGGY_PYTHON = """data = Console.ReadLine().Split()
freq = new Dictionary<string, int>()

for item in data
    if freq.ContainsKey(item):
        freq[item]++
    else:
        freq[item] = 1

for key in freq.Keys.Sort():
    Console.WriteLine(key + " " + freq[key])"""

FIXED_CPP = """#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> freq;
    std::string x;

    while (std::cin >> x) {
        freq[x]++;
    }

    for (auto& p : freq) {
        std::cout << p.first << ' ' << p.second << '\\n';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <map>

int main() {
    Dictionary<string, int> freq;
    string x;

    while (Console.ReadLine() >> x) {
        freq[x] = freq.get(x, 0) + 1;
    }

    for key in sorted(freq):
        print(key, freq[key]);

    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        Dictionary<string, int> freq = new Dictionary<string, int>();

        foreach (string x in Console.ReadLine().Split()) {
            if (!freq.ContainsKey(x)) {
                freq[x] = 0;
            }

            freq[x]++;
        }

        List<string> keys = new List<string>(freq.Keys);
        keys.Sort();

        foreach (string key in keys) {
            Console.WriteLine($"{key} {freq[key]}");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        var data = input().split();
        var freq = {};

        for item in data:
            freq[item] = freq.get(item, 0) + 1;

        for key in sorted(freq):
            print(key, freq[key]);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        TreeMap<String, Integer> freq = new TreeMap<>();

        while (sc.hasNext()) {
            String x = sc.next();
            freq.put(x, freq.getOrDefault(x, 0) + 1);
        }

        for (String key : freq.keySet()) {
            System.out.println(key + " " + freq.get(key));
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Dictionary<string, int> freq = new Dictionary<>();

        while (Console.ReadLine() != null) {
            String x = input();
            freq[x] = freq.get(x, 0) + 1;
        }

        for key in sorted(freq):
            print(key, freq[key]);
    }
}"""
