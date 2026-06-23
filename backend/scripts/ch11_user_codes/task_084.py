PASCAL = """var inputFile, outputFile: text;
    x, total: integer;
begin
  assign(inputFile, 'input.txt');
  reset(inputFile);

  total := 0;

  while not eof(inputFile) do
  begin
    readln(inputFile, x);
    total := total + x;
  end;

  close(inputFile);

  assign(outputFile, 'report.txt');
  rewrite(outputFile);
  writeln(outputFile, total);
  close(outputFile);
end."""

PYTHON = """total = 0

with open('input.txt') as f:
    for line in f:
        total += int(line)

with open('report.txt', 'w') as f:
    f.write(str(total))"""

CPP = """#include <fstream>

int main() {
    std::ifstream input("input.txt");
    std::ofstream report("report.txt");

    int x;
    int total = 0;

    while (input >> x) {
        total += x;
    }

    report << total;
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

        File.WriteAllText("report.txt", total.ToString());
    }
}"""

JAVA = """import java.nio.file.*;

class Main {
    public static void main(String[] args) throws Exception {
        int total = 0;

        for (String line : Files.readAllLines(Path.of("input.txt"))) {
            total += Integer.parseInt(line);
        }

        Files.writeString(Path.of("report.txt"), String.valueOf(total));
    }
}"""
