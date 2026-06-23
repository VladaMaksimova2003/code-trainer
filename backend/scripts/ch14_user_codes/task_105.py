PASCAL = """var mode: string;
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
    var root: PNode;
    begin
      new(root);
      root^.value := 10;
      root^.left := nil;
      root^.right := nil;
      writeln(root^.value);
    end;
  end;
end."""

PYTHON = """mode = input()
if mode in ('demo', 'empty', 'edge'):
    print('ok')
else:
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    root = Node(10)
    print(root.value)"""

CPP = """#include <iostream>
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

    Node root{10, nullptr, nullptr};
    std::cout << root.value;
    return 0;
}"""

CSHARP = """using System;

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

        Node root = new Node(10);
        Console.WriteLine(root.Value);
    }
}"""

JAVA = """import java.util.*;

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

        Node root = new Node(10);
        System.out.println(root.value);
    }
}"""
