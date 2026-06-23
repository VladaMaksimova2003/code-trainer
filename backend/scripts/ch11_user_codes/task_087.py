FIXED_PASCAL = """function CountLines(filename: string): integer;
var f: text;
    line: string;
    count: integer;
begin
  assign(f, filename);
  reset(f);

  count := 0;

  while not eof(f) do
  begin
    readln(f, line);
    count := count + 1;
  end;

  close(f);
  CountLines := count;
end;

begin
  writeln(CountLines('input.txt'));
end."""

BUGGY_PASCAL = """function CountLines(file: string): integer;
var line: string;
begin
  file := open(file);

  while not file.eof() do
  begin
    line := file.readline();
    CountLines++;
  end;

  return CountLines;
end;

begin
  print(CountLines('input.txt'));
end."""

FIXED_PYTHON = """def count_lines(filename):
    count = 0

    with open(filename) as f:
        for _ in f:
            count += 1

    return count


filename = 'input.txt'
print(count_lines(filename))"""

BUGGY_PYTHON = """from os import *

def count_lines(file):
    count = 0

    file = open(file)

    for line in File.ReadAllLines(file):
        count++

    return len(file)


filename = 'input.txt'
Console.WriteLine(count_lines(filename))"""

FIXED_CPP = """#include <iostream>
#include <fstream>
#include <string>

int countLines(const std::string& filename) {
    std::ifstream f(filename);

    std::string line;
    int count = 0;

    while (std::getline(f, line)) {
        count++;
    }

    return count;
}

int main() {
    std::cout << countLines("input.txt");
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <fstream>

int countLines(string file) {
    int count := 0;

    File f = File.Open(file);

    while (f.ReadLine() != null) {
        count++;
    }

    return len(f);
}

int main() {
    Console.WriteLine(countLines("input.txt"));
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.IO;

class Program {
    static int CountLines(string filename) {
        int count = 0;

        foreach (string line in File.ReadLines(filename)) {
            count++;
        }

        return count;
    }

    static void Main() {
        Console.WriteLine(CountLines("input.txt"));
    }
}"""

BUGGY_CSHARP = """using System;
using System.IO;

class Program {
    static int CountLines(File file) {
        int count := 0;

        foreach line in open(file) {
            count++;
        }

        return file.Length;
    }

    static void Main() {
        string File = "input.txt";
        print(CountLines(File));
    }
}"""

FIXED_JAVA = """import java.nio.file.*;

class Main {
    static int countLines(String filename) throws Exception {
        int count = 0;

        for (String line : Files.readAllLines(Path.of(filename))) {
            count++;
        }

        return count;
    }

    public static void main(String[] args) throws Exception {
        System.out.println(countLines("input.txt"));
    }
}"""

BUGGY_JAVA = """import java.nio.file.*;

class Main {
    static int countLines(File file) {
        int count := 0;

        for line in open(file):
            count++;

        return file.length;
    }

    public static void main(String[] args) {
        String File = "input.txt";
        Console.WriteLine(countLines(File));
    }
}"""
