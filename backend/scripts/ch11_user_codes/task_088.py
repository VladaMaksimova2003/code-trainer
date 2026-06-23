FIXED_PASCAL = """var f: text;
    level, message: string;
    errors, warnings: integer;
begin
  assign(f, 'log.txt');
  reset(f);

  errors := 0;
  warnings := 0;

  while not eof(f) do
  begin
    readln(f, level, message);

    if level = 'ERROR' then
      errors := errors + 1
    else if level = 'WARN' then
      warnings := warnings + 1;
  end;

  close(f);

  writeln(errors, ' ', warnings);
end."""

BUGGY_PASCAL = """var f: File;
    level, message: string;
    errors, warnings: integer;
begin
  f := open('log.txt');

  errors = 0;
  warnings = 0;

  while f.hasNext() do
  begin
    level := f.readline().split(' ')[1];

    if level == 'ERROR' then
      errors++
    else if level == 'WARN' then
      warnings++;
  end;

  print(errors, warnings);
end."""

FIXED_PYTHON = """errors = 0
warnings = 0

with open('log.txt') as f:
    for line in f:
        parts = line.strip().split(maxsplit=1)

        if len(parts) == 0:
            continue

        level = parts[0]

        if level == 'ERROR':
            errors += 1
        elif level == 'WARN':
            warnings += 1

print(errors, warnings)"""

BUGGY_PYTHON = """errors := 0
warnings := 0

File log = File.Open("log.txt")

for line in File.ReadAllLines(log):
    level = line.split(" ")[1]

    if level = "ERROR":
        errors++
    else if level = "WARN":
        warnings++

Console.WriteLine(errors + " " + warnings)"""

FIXED_CPP = """#include <iostream>
#include <fstream>
#include <string>

int main() {
    std::ifstream f("log.txt");

    std::string level;
    std::string message;

    int errors = 0;
    int warnings = 0;

    while (f >> level) {
        std::getline(f, message);

        if (level == "ERROR") {
            errors++;
        } else if (level == "WARN") {
            warnings++;
        }
    }

    std::cout << errors << ' ' << warnings;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <fstream>

int main() {
    File f = File.Open("log.txt");

    int errors := 0;
    int warnings := 0;

    while (f.hasNext()) {
        string line = f.readline();
        string level = line.split(" ")[1];

        if (level = "ERROR") {
            errors++;
        } else if (level = "WARN") {
            warnings++;
        }
    }

    Console.WriteLine(errors + " " + warnings);
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.IO;

class Program {
    static void Main() {
        int errors = 0;
        int warnings = 0;

        foreach (string line in File.ReadAllLines("log.txt")) {
            string[] parts = line.Split(' ', 2);

            if (parts.Length == 0) {
                continue;
            }

            string level = parts[0];

            if (level == "ERROR") {
                errors++;
            } else if (level == "WARN") {
                warnings++;
            }
        }

        Console.WriteLine($"{errors} {warnings}");
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int errors := 0;
        int warnings := 0;

        foreach line in open("log.txt") {
            string level = line.split(" ")[1];

            if (level = "ERROR") {
                errors++;
            } else if (level = "WARN") {
                warnings++;
            }
        }

        print(errors + " " + warnings);
    }
}"""

FIXED_JAVA = """import java.nio.file.*;

class Main {
    public static void main(String[] args) throws Exception {
        int errors = 0;
        int warnings = 0;

        for (String line : Files.readAllLines(Path.of("log.txt"))) {
            String[] parts = line.split(" ", 2);

            if (parts.length == 0) {
                continue;
            }

            String level = parts[0];

            if (level.equals("ERROR")) {
                errors++;
            } else if (level.equals("WARN")) {
                warnings++;
            }
        }

        System.out.println(errors + " " + warnings);
    }
}"""

BUGGY_JAVA = """import java.nio.file.*;

class Main {
    public static void main(String[] args) {
        int errors := 0;
        int warnings := 0;

        for line in open("log.txt"):
            String level = line.split(" ")[1];

            if (level == "ERROR") {
                errors++;
            } else if (level == "WARN") {
                warnings++;
            }

        Console.WriteLine(errors + " " + warnings);
    }
}"""
