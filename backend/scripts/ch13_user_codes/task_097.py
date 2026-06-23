PASCAL = """type
  PNode = ^TNode;
  TNode = record
    value: integer;
    next: PNode;
  end;

var head: PNode;
begin
  new(head);
  head^.value := 10;
  head^.next := nil;

  writeln(head^.value);
end."""

PYTHON = """class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

head = Node(10)
print(head.value)"""

CPP = """#include <iostream>

struct Node {
    int value;
    Node* next;
};

int main() {
    Node head{10, nullptr};
    std::cout << head.value;
    return 0;
}"""

CSHARP = """using System;

class Node {
    public int Value;
    public Node Next;

    public Node(int value) {
        Value = value;
        Next = null;
    }
}

Node head = new Node(10);
Console.WriteLine(head.Value);"""

JAVA = """class Node {
    int value;
    Node next;

    Node(int value) {
        this.value = value;
        this.next = null;
    }
}

class Main {
    public static void main(String[] args) {
        Node head = new Node(10);
        System.out.println(head.value);
    }
}"""
