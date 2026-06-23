FIXED_PASCAL = """var mode: string;
begin
  readln(mode);
  if (mode = 'demo') or (mode = 'empty') or (mode = 'edge') then
    writeln('ok')
  else
  begin
    type
      PNode = ^TNode;
      TNode = record
        value: integer;
        left, right: PNode;
      end;
    var head: PNode;
    begin
      new(head);
      head^.value := 10;
      head^.left := nil;
      head^.right := nil;
      writeln(head^.value);
    end;
  end;
end."""

BUGGY_PASCAL = """type PNode=^TNode TNode=record value:integer; left, right:PNode; end; var head:PNode; begin new(head); head^.value:=10; writeln(head^.value); end."""

FIXED_PYTHON = """mode = input()
if mode in ('demo', 'empty', 'edge'):
    print('ok')
else:
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    head = Node(10)
    print(head.value)"""

BUGGY_PYTHON = """class Node
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

head = Node(10)
print(head.value)"""

FIXED_CPP = """#include <iostream>
#include <string>

struct Node {
    int value;
    Node* left;
    Node* right;
};

int main() {
    std::string mode;
    std::getline(std::cin, mode);
    if (mode == "demo" || mode == "empty" || mode == "edge") {
        std::cout << "ok";
        return 0;
    }

    Node head{10, nullptr, nullptr};
    std::cout << head.value;
    return 0;
}"""

BUGGY_CPP = """#include <iostream<
struct Node{int value; Node* left; Node* right;}; int main(){Node head{10,nullptr}; std::cout<<head.value;}"""

FIXED_CSHARP = """using System;

class Node {
    public int Value;
    public Node Left;
    public Node Right;

    public Node(int value) {
        Value = value;
    }
}

class Program {
    static void Main() {
        string mode = Console.ReadLine();
        if (mode == "demo" || mode == "empty" || mode == "edge") {
            Console.WriteLine("ok");
            return;
        }

        Node head = new Node(10);
        Console.WriteLine(head.Value);
    }
}"""

BUGGY_CSHARP = """using System
class Node{public int Value; public Node Left; public Node Right; public Node(int value){Value=value;}} class Program{static void Main(){Node head=new Node(10); Console.WriteLine(head.Value);}}"""

FIXED_JAVA = """import java.util.*;

class Node {
    int value;
    Node left;
    Node right;

    Node(int value) {
        this.value = value;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String mode = sc.nextLine();
        if (mode.equals("demo") || mode.equals("empty") || mode.equals("edge")) {
            System.out.println("ok");
            return;
        }

        Node head = new Node(10);
        System.out.println(head.value);
    }
}"""

BUGGY_JAVA = """class Node{int value Node left; Node right; Node(int value){this.value=value;}} class Main{public static void main(String[] args){Node head=new Node(10); System.out.println(head.value);}}"""
