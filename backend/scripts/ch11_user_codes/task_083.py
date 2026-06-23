PASCAL = """var f: text;
    line, namePart, amountPart: string;
    commaPos, amount, total: integer;
begin
  assign(f, 'input.csv');
  reset(f);

  total := 0;

  while not eof(f) do
  begin
    readln(f, line);

    commaPos := pos(',', line);
    namePart := copy(line, 1, commaPos - 1);
    amountPart := copy(line, commaPos + 1, length(line));

    val(amountPart, amount);
    total := total + amount;
  end;

  close(f);
  writeln(total);
end."""

PYTHON = """total = 0

with open('input.csv') as f:
    for line in f:
        name, amount = line.strip().split(',')
        total += int(amount)

print(total)"""

CPP = """#include <iostream>
#include <fstream>
#include <string>

int main() {
    std::ifstream f("input.csv");

    std::string line;
    int total = 0;

    while (std::getline(f, line)) {
        int comma = line.find(',');
        std::string amountText = line.substr(comma + 1);
        total += std::stoi(amountText);
    }

    std::cout << total;
    return 0;
}"""

CSHARP = """using System;
using System.IO;

class Program {
    static void Main() {
        int total = 0;

        foreach (string line in File.ReadAllLines("input.csv")) {
            string[] parts = line.Split(',');
            total += int.Parse(parts[1]);
        }

        Console.WriteLine(total);
    }
}"""

JAVA = """import java.nio.file.*;

class Main {
    public static void main(String[] args) throws Exception {
        int total = 0;

        for (String line : Files.readAllLines(Path.of("input.csv"))) {
            String[] parts = line.split(",");
            total += Integer.parseInt(parts[1]);
        }

        System.out.println(total);
    }
}"""
