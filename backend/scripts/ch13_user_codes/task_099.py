PASCAL = """type
  PNode = ^TNode;
  TNode = record
    value: integer;
    next: PNode;
  end;

var n, i, x: integer;
    head, tail, node, cur: PNode;
begin
  readln(n);
  head := nil;
  tail := nil;

  for i := 1 to n do
  begin
    readln(x);
    new(node);
    node^.value := x;
    node^.next := nil;

    if head = nil then
    begin
      head := node;
      tail := node;
    end
    else
    begin
      tail^.next := node;
      tail := node;
    end;
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
tail = None

for _ in range(n):
    node = Node(int(input()))

    if head is None:
        head = node
        tail = node
    else:
        tail.next = node
        tail = node

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
    Node* tail = nullptr;

    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;

        Node* node = new Node{x, nullptr};

        if (head == nullptr) {
            head = node;
            tail = node;
        } else {
            tail->next = node;
            tail = node;
        }
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
Node tail = null;

for (int i = 0; i < n; i++) {
    Node node = new Node(int.Parse(Console.ReadLine()));

    if (head == null) {
        head = node;
        tail = node;
    } else {
        tail.Next = node;
        tail = node;
    }
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
        Node tail = null;

        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());

            if (head == null) {
                head = node;
                tail = node;
            } else {
                tail.next = node;
                tail = node;
            }
        }

        for (Node cur = head; cur != null; cur = cur.next) {
            System.out.print(cur.value + " ");
        }
    }
}"""
