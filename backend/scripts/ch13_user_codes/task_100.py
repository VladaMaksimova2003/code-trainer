PASCAL = """type
  PNode = ^TNode;
  TNode = record
    value: integer;
    next: PNode;
  end;

var n, i, x, target: integer;
    head, tail, node, cur: PNode;
    found: boolean;
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

  readln(target);
  found := false;
  cur := head;

  while cur <> nil do
  begin
    if cur^.value = target then
      found := true;

    cur := cur^.next;
  end;

  if found then writeln('found')
  else writeln('not found');
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
        head = tail = node
    else:
        tail.next = node
        tail = node

target = int(input())
cur = head
found = False

while cur:
    if cur.value == target:
        found = True
    cur = cur.next

print('found' if found else 'not found')"""

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

        if (!head) head = tail = node;
        else {
            tail->next = node;
            tail = node;
        }
    }

    int target;
    std::cin >> target;

    bool found = false;

    for (Node* cur = head; cur != nullptr; cur = cur->next) {
        if (cur->value == target) found = true;
    }

    std::cout << (found ? "found" : "not found");
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

int target = int.Parse(Console.ReadLine());
bool found = false;

for (Node cur = head; cur != null; cur = cur.Next) {
    if (cur.Value == target) found = true;
}

Console.WriteLine(found ? "found" : "not found");"""

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

        int target = sc.nextInt();
        boolean found = false;

        for (Node cur = head; cur != null; cur = cur.next) {
            if (cur.value == target) found = true;
        }

        System.out.println(found ? "found" : "not found");
    }
}"""
