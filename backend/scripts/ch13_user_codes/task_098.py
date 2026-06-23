PASCAL = """type
  PNode = ^TNode;
  TNode = record
    value: integer;
    next: PNode;
  end;

var n, i, x: integer;
    head, node, cur: PNode;
begin
  readln(n);
  head := nil;

  for i := 1 to n do
  begin
    readln(x);
    new(node);
    node^.value := x;
    node^.next := head;
    head := node;
  end;

  cur := head;
  while cur <> nil do
  begin
    write(cur^.value, ' ');
    cur := cur^.next;
  end;
end."""

PYTHON = """class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

n = int(input())
head = None

for _ in range(n):
    x = int(input())
    node = Node(x)
    node.next = head
    head = node

cur = head
while cur:
    print(cur.value, end=' ')
    cur = cur.next"""

CPP = """#include <iostream>

struct Node {
    int value;
    Node* next;
};

int main() {
    int n;
    std::cin >> n;

    Node* head = nullptr;

    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;

        head = new Node{x, head};
    }

    for (Node* cur = head; cur != nullptr; cur = cur->next) {
        std::cout << cur->value << ' ';
    }

    return 0;
}"""

CSHARP = """using System;

class Node {
    public int Value;
    public Node Next;

    public Node(int value) {
        Value = value;
    }
}

int n = int.Parse(Console.ReadLine());
Node head = null;

for (int i = 0; i < n; i++) {
    int x = int.Parse(Console.ReadLine());
    Node node = new Node(x);
    node.Next = head;
    head = node;
}

for (Node cur = head; cur != null; cur = cur.Next) {
    Console.Write(cur.Value + " ");
}"""

JAVA = """import java.util.*;

class Node {
    int value;
    Node next;

    Node(int value) {
        this.value = value;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Node head = null;

        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());
            node.next = head;
            head = node;
        }

        for (Node cur = head; cur != null; cur = cur.next) {
            System.out.print(cur.value + " ");
        }
    }
}"""
