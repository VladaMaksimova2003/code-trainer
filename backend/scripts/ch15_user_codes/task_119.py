PASCAL = """type
  TTask = class
    title: string;
    done: boolean;
    constructor Create(t: string);
    procedure Complete;
    function Status: string;
  end;

constructor TTask.Create(t: string);
begin
  title := t;
  done := false;
end;

procedure TTask.Complete;
begin
  done := true;
end;

function TTask.Status: string;
begin
  if done then
    Status := 'done'
  else
    Status := 'active';
end;

var
  task: TTask;
begin
  task := TTask.Create('homework');

  writeln(task.Status);
  task.Complete;
  writeln(task.Status);
end."""

PYTHON = """class Task:
    def __init__(self, title):
        self.title = title
        self.done = False

    def complete(self):
        self.done = True

    def status(self):
        if self.done:
            return "done"
        return "active"

task = Task("homework")
print(task.status())
task.complete()
print(task.status())"""

CPP = """#include <iostream>
#include <string>

class Task {
    std::string title;
    bool done;

public:
    Task(std::string t) {
        title = t;
        done = false;
    }

    void complete() {
        done = true;
    }

    std::string status() {
        return done ? "done" : "active";
    }
};

int main() {
    Task task("homework");

    std::cout << task.status() << '\\n';
    task.complete();
    std::cout << task.status();

    return 0;
}"""

CSHARP = """using System;

class TaskItem {
    string title;
    bool done;

    public TaskItem(string t) {
        title = t;
        done = false;
    }

    public void Complete() {
        done = true;
    }

    public string Status() {
        return done ? "done" : "active";
    }
}

TaskItem task = new TaskItem("homework");
Console.WriteLine(task.Status());
task.Complete();
Console.WriteLine(task.Status());"""

JAVA = """class Task {
    String title;
    boolean done;

    Task(String t) {
        title = t;
        done = false;
    }

    void complete() {
        done = true;
    }

    String status() {
        return done ? "done" : "active";
    }
}

class Main {
    public static void main(String[] args) {
        Task task = new Task("homework");

        System.out.println(task.status());
        task.complete();
        System.out.println(task.status());
    }
}"""
