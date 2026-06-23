FIXED_PASCAL = """procedure SortNumbers(var a: array of integer);
var i, j, temp: integer;
begin
  for i := 0 to length(a) - 1 do
    for j := i + 1 to length(a) - 1 do
      if a[j] < a[i] then
      begin
        temp := a[i];
        a[i] := a[j];
        a[j] := temp;
      end;
end;

var f: text;
    a: array of integer;
    x, n, i: integer;
begin
  assign(f, 'input.txt');
  reset(f);

  n := 0;
  setlength(a, 0);

  while not eof(f) do
  begin
    readln(f, x);
    n := n + 1;
    setlength(a, n);
    a[n - 1] := x;
  end;

  close(f);

  SortNumbers(a);

  for i := 0 to n - 1 do
    write(a[i], ' ');
end."""

BUGGY_PASCAL = """function SortNumbers(numbers: list[int]): list[int];
begin
  numbers.sort();
  return numbers;
end;

var f: text;
    numbers: array of integer;
    line: string;
begin
  f := open('input.txt');

  while not eof(f) do
  begin
    line := f.readline();
    numbers.Add(line);
  end;

  print(SortNumbers(numbers));
end."""

FIXED_PYTHON = """def sort_numbers(numbers):
    return sorted(numbers)


numbers = []

with open('input.txt') as f:
    for line in f:
        numbers.append(int(line))

result = sort_numbers(numbers)

print(*result)"""

BUGGY_PYTHON = """def sort_numbers(int[] numbers):
    numbers.Sort()
    return numbers


numbers = new List<int>()

with open('input.txt') as f
    for line in f:
        numbers.Add(line)

result = sort_numbers(numbers)

Console.WriteLine(result)"""

FIXED_CPP = """#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>

std::vector<int> sortNumbers(std::vector<int> numbers) {
    std::sort(numbers.begin(), numbers.end());
    return numbers;
}

int main() {
    std::ifstream f("input.txt");

    std::vector<int> numbers;
    int x;

    while (f >> x) {
        numbers.push_back(x);
    }

    std::vector<int> result = sortNumbers(numbers);

    for (int value : result) {
        std::cout << value << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <fstream>

def sort_numbers(numbers):
    numbers.sort()
    return numbers

int main() {
    File f = File.Open("input.txt");

    vector<int> numbers = new vector<int>();

    while (!f.eof()) {
        string line = f.readline();
        numbers.Add(line);
    }

    auto result = sort_numbers(numbers);

    Console.WriteLine(result);
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.IO;

class Program {
    static int[] SortNumbers(int[] numbers) {
        Array.Sort(numbers);
        return numbers;
    }

    static void Main() {
        string[] lines = File.ReadAllLines("input.txt");
        int[] numbers = new int[lines.Length];

        for (int i = 0; i < lines.Length; i++) {
            numbers[i] = int.Parse(lines[i]);
        }

        int[] result = SortNumbers(numbers);

        foreach (int value in result) {
            Console.Write(value + " ");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    def sort_numbers(numbers):
        numbers.sort()
        return numbers

    static void Main() {
        var numbers = [];

        with open("input.txt") as f:
            foreach (string line in f) {
                numbers.Add(line);
            }

        var result = sort_numbers(numbers);

        print(result);
    }
}"""

FIXED_JAVA = """import java.nio.file.*;
import java.util.*;

class Main {
    static int[] sortNumbers(int[] numbers) {
        Arrays.sort(numbers);
        return numbers;
    }

    public static void main(String[] args) throws Exception {
        List<String> lines = Files.readAllLines(Path.of("input.txt"));
        int[] numbers = new int[lines.size()];

        for (int i = 0; i < lines.size(); i++) {
            numbers[i] = Integer.parseInt(lines.get(i));
        }

        int[] result = sortNumbers(numbers);

        for (int value : result) {
            System.out.print(value + " ");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    def sort_numbers(numbers):
        numbers.sort()
        return numbers

    public static void main(String[] args) {
        List<int> numbers = new List<int>();

        with open("input.txt") as f:
            for line in f:
                numbers.Add(line);

        int[] result = sort_numbers(numbers);

        Console.WriteLine(result);
    }
}"""
