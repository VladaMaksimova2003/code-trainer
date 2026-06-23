PASCAL = """var f: text;
    line: string;
    count: integer;
begin
  assign(f, 'input.txt');
  reset(f);

  count := 0;

  while not eof(f) do
  begin
    readln(f, line);
    count := count + 1;
  end;

  close(f);
  writeln(count);
end."""

PYTHON = """count = 0

with open('input.txt') as f:
    for line in f:
        count += 1

print(count)"""

CPP = """#include <iostream>
#include <fstream>
#include <string>

int main() {
    std::ifstream f("input.txt");

    std::string line;
    int count = 0;

    while (std::getline(f, line)) {
        count++;
    }

    std::cout << count;
    return 0;
}"""

CSHARP = """using System;
using System.IO;

class Program {
    static void Main() {
        int count = File.ReadAllLines("input.txt").Length;
        Console.WriteLine(count);
    }
}"""

JAVA = """import java.nio.file.*;

class Main {
    public static void main(String[] args) throws Exception {
        System.out.println(Files.readAllLines(Path.of("input.txt")).size());
    }
}"""
