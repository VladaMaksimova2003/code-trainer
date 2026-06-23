PASCAL = """type
  TEmployee = class
    function Salary: integer; virtual;
  end;

  TManager = class(TEmployee)
    function Salary: integer; override;
  end;

  TDeveloper = class(TEmployee)
    function Salary: integer; override;
  end;

function TEmployee.Salary: integer;
begin
  Salary := 0;
end;

function TManager.Salary: integer;
begin
  Salary := 80000;
end;

function TDeveloper.Salary: integer;
begin
  Salary := 70000;
end;

var
  employees: array[1..2] of TEmployee;
  i, total: integer;
begin
  employees[1] := TManager.Create;
  employees[2] := TDeveloper.Create;

  total := 0;

  for i := 1 to 2 do
    total := total + employees[i].Salary;

  writeln(total);
end."""

PYTHON = """class Employee:
    def salary(self):
        return 0


class Manager(Employee):
    def salary(self):
        return 80000


class Developer(Employee):
    def salary(self):
        return 70000


employees = [Manager(), Developer()]
total = 0

for employee in employees:
    total += employee.salary()

print(total)"""

CPP = """#include <iostream>
#include <vector>

class Employee {
public:
    virtual int salary() {
        return 0;
    }
};

class Manager : public Employee {
public:
    int salary() override {
        return 80000;
    }
};

class Developer : public Employee {
public:
    int salary() override {
        return 70000;
    }
};

int main() {
    std::vector<Employee*> employees = {new Manager(), new Developer()};
    int total = 0;

    for (Employee* employee : employees) {
        total += employee->salary();
    }

    std::cout << total;
    return 0;
}"""

CSHARP = """using System;

class Employee {
    public virtual int Salary() {
        return 0;
    }
}

class Manager : Employee {
    public override int Salary() {
        return 80000;
    }
}

class Developer : Employee {
    public override int Salary() {
        return 70000;
    }
}

Employee[] employees = { new Manager(), new Developer() };
int total = 0;

foreach (Employee employee in employees) {
    total += employee.Salary();
}

Console.WriteLine(total);"""

JAVA = """class Employee {
    int salary() {
        return 0;
    }
}

class Manager extends Employee {
    @Override
    int salary() {
        return 80000;
    }
}

class Developer extends Employee {
    @Override
    int salary() {
        return 70000;
    }
}

class Main {
    public static void main(String[] args) {
        Employee[] employees = { new Manager(), new Developer() };
        int total = 0;

        for (Employee employee : employees) {
            total += employee.salary();
        }

        System.out.println(total);
    }
}"""
