PASCAL = """var f: text;
    x, total: integer;
begin
  assign(f, 'input.txt');
  reset(f);

  total := 0;

  while not eof(f) do
  begin
    readln(f, x);
    total := total + x;
  end;

  close(f);
  writeln(total);
end."""

PYTHON = """total = 0

with open('input.txt') as f:
    for line in f:
        total += int(line)

print(total)"""

CPP = """#include <iostream>
#include <fstream>

int main() {
    std::ifstream f("input.txt");

    int x;
    int total = 0;

    while (f >> x) {
        total += x;
    }

    std::cout << total;
    return 0;
}"""

CSHARP = """using System;
using System.IO;

class Program {
    static void Main() {
        int total = 0;

        foreach (string line in File.ReadAllLines("input.txt")) {
            total += int.Parse(line);
        }

        Console.WriteLine(total);
    }
}"""

JAVA = """import java.nio.file.*;
import java.util.*;

class Main {
    public static void main(String[] args) throws Exception {
        int total = 0;

        for (String line : Files.readAllLines(Path.of("input.txt"))) {
            total += Integer.parseInt(line);
        }

        System.out.println(total);
    }
}"""
