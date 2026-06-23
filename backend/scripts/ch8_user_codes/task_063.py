PASCAL = """type Student = record
  name: string;
  score: integer;
end;

var n, i, j: integer;
    students: array[1..100] of Student;
    temp: Student;
begin
  readln(n);

  for i := 1 to n do
    readln(students[i].name, students[i].score);

  for i := 1 to n do
    for j := i + 1 to n do
      if (students[j].score > students[i].score) or
         ((students[j].score = students[i].score) and (students[j].name < students[i].name)) then
      begin
        temp := students[i];
        students[i] := students[j];
        students[j] := temp;
      end;

  for i := 1 to n do
    writeln(students[i].name, ' ', students[i].score);
end."""

PYTHON = """n = int(input())
students = []

for _ in range(n):
    name, score = input().split()
    students.append((name, int(score)))

students.sort(key=lambda item: (-item[1], item[0]))

for name, score in students:
    print(name, score)"""

CPP = """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

struct Student {
    std::string name;
    int score;
};

int main() {
    int n;
    std::cin >> n;

    std::vector<Student> students(n);

    for (int i = 0; i < n; i++) {
        std::cin >> students[i].name >> students[i].score;
    }

    std::sort(students.begin(), students.end(), [](const Student& a, const Student& b) {
        if (a.score != b.score) {
            return a.score > b.score;
        }
        return a.name < b.name;
    });

    for (const Student& student : students) {
        std::cout << student.name << ' ' << student.score << '\n';
    }

    return 0;
}"""

CSHARP = """using System;

class Student {
    public string Name;
    public int Score;
}

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Student[] students = new Student[n];

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            students[i] = new Student {
                Name = p[0],
                Score = int.Parse(p[1])
            };
        }

        Array.Sort(students, (a, b) => {
            if (a.Score != b.Score) {
                return b.Score.CompareTo(a.Score);
            }
            return a.Name.CompareTo(b.Name);
        });

        foreach (Student student in students) {
            Console.WriteLine($"{student.Name} {student.Score}");
        }
    }
}"""

JAVA = """import java.util.*;

class Student {
    String name;
    int score;

    Student(String name, int score) {
        this.name = name;
        this.score = score;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Student[] students = new Student[n];

        for (int i = 0; i < n; i++) {
            students[i] = new Student(sc.next(), sc.nextInt());
        }

        Arrays.sort(students, (a, b) -> {
            if (a.score != b.score) {
                return b.score - a.score;
            }
            return a.name.compareTo(b.name);
        });

        for (Student student : students) {
            System.out.println(student.name + " " + student.score);
        }
    }
}"""
