PASCAL = """var n, i: integer;
    id, query: string;
    ids, names: array[1..100] of string;
    grades: array[1..100] of integer;
    found: boolean;
begin
  readln(n);

  for i := 1 to n do
    readln(ids[i], names[i], grades[i]);

  readln(query);
  found := false;

  for i := 1 to n do
    if ids[i] = query then
    begin
      writeln(names[i], ' ', grades[i]);
      found := true;
    end;

  if not found then
    writeln('not found');
end."""

PYTHON = """n = int(input())
students = {}

for _ in range(n):
    student_id, name, grade = input().split()
    students[student_id] = (name, grade)

query = input()

if query in students:
    name, grade = students[query]
    print(name, grade)
else:
    print('not found')"""

CPP = """#include <iostream>
#include <map>
#include <string>

struct Student {
    std::string name;
    int grade;
};

int main() {
    int n;
    std::cin >> n;

    std::map<std::string, Student> students;

    for (int i = 0; i < n; i++) {
        std::string id;
        Student st;

        std::cin >> id >> st.name >> st.grade;
        students[id] = st;
    }

    std::string query;
    std::cin >> query;

    if (students.count(query)) {
        std::cout << students[query].name << ' ' << students[query].grade;
    } else {
        std::cout << "not found";
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Student {
    public string Name;
    public int Grade;
}

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Dictionary<string, Student> students = new Dictionary<string, Student>();

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            students[p[0]] = new Student {
                Name = p[1],
                Grade = int.Parse(p[2])
            };
        }

        string query = Console.ReadLine();

        if (students.ContainsKey(query)) {
            Console.WriteLine($"{students[query].Name} {students[query].Grade}");
        } else {
            Console.WriteLine("not found");
        }
    }
}"""

JAVA = """import java.util.*;

class Student {
    String name;
    int grade;

    Student(String name, int grade) {
        this.name = name;
        this.grade = grade;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        HashMap<String, Student> students = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String id = sc.next();
            String name = sc.next();
            int grade = sc.nextInt();

            students.put(id, new Student(name, grade));
        }

        String query = sc.next();

        if (students.containsKey(query)) {
            Student st = students.get(query);
            System.out.println(st.name + " " + st.grade);
        } else {
            System.out.println("not found");
        }
    }
}"""
