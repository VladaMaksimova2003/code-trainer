PASCAL = """var f: text;
    event: string;
begin
  readln(event);

  assign(f, 'log.txt');
  append(f);

  writeln(f, event);

  close(f);
  writeln('logged');
end."""

PYTHON = """event = input()

with open('log.txt', 'a') as f:
    f.write(event + '\\n')

print('logged')"""

CPP = """#include <iostream>
#include <fstream>
#include <string>

int main() {
    std::string event;
    std::getline(std::cin, event);

    std::ofstream f("log.txt", std::ios::app);
    f << event << '\\n';

    std::cout << "logged";
    return 0;
}"""

CSHARP = """using System;
using System.IO;

class Program {
    static void Main() {
        string eventText = Console.ReadLine();

        File.AppendAllText("log.txt", eventText + Environment.NewLine);

        Console.WriteLine("logged");
    }
}"""

JAVA = """import java.nio.file.*;
import java.nio.charset.*;
import java.util.*;

class Main {
    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        String eventText = sc.nextLine();

        Files.writeString(
            Path.of("log.txt"),
            eventText + System.lineSeparator(),
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE,
            StandardOpenOption.APPEND
        );

        System.out.println("logged");
    }
}"""
