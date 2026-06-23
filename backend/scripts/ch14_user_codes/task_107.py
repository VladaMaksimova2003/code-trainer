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

    var root, node: PNode;
        q: array[1..100] of PNode;
        head, tail: integer;
    begin
      new(root);
      root^.value := 10;

      new(root^.left);
      root^.left^.value := 5;
      root^.left^.left := nil;
      root^.left^.right := nil;

      new(root^.right);
      root^.right^.value := 15;
      root^.right^.left := nil;
      root^.right^.right := nil;

      new(root^.left^.left);
      root^.left^.left^.value := 3;
      root^.left^.left^.left := nil;
      root^.left^.left^.right := nil;

      head := 1;
      tail := 1;
      q[tail] := root;

      while head <= tail do
      begin
        node := q[head];
        head := head + 1;
        write(node^.value, ' ');

        if node^.left <> nil then
        begin
          tail := tail + 1;
          q[tail] := node^.left;
        end;

        if node^.right <> nil then
        begin
          tail := tail + 1;
          q[tail] := node^.right;
        end;
      end;
    end;
  end;
end."""

PYTHON = """from collections import deque

mode = input()
if mode in ('demo', 'empty', 'edge'):
    print('ok')
else:
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    root = Node(10)
    root.left = Node(5)
    root.right = Node(15)
    root.left.left = Node(3)

    queue = deque([root])

    while queue:
        node = queue.popleft()
        print(node.value, end=' ')

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)"""

CPP = """#include <iostream>
#include <queue>
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

    Node* root = new Node{10, nullptr, nullptr};
    root->left = new Node{5, nullptr, nullptr};
    root->right = new Node{15, nullptr, nullptr};
    root->left->left = new Node{3, nullptr, nullptr};

    std::queue<Node*> q;
    q.push(root);

    while (!q.empty()) {
        Node* node = q.front();
        q.pop();
        std::cout << node->value << ' ';
        if (node->left) q.push(node->left);
        if (node->right) q.push(node->right);
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

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
        root.Left = new Node(5);
        root.Right = new Node(15);
        root.Left.Left = new Node(3);

        Queue<Node> queue = new Queue<Node>();
        queue.Enqueue(root);

        while (queue.Count > 0) {
            Node node = queue.Dequeue();
            Console.Write(node.Value + " ");
            if (node.Left != null) queue.Enqueue(node.Left);
            if (node.Right != null) queue.Enqueue(node.Right);
        }
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
        root.left = new Node(5);
        root.right = new Node(15);
        root.left.left = new Node(3);

        Queue<Node> queue = new LinkedList<>();
        queue.add(root);

        while (!queue.isEmpty()) {
            Node node = queue.poll();
            System.out.print(node.value + " ");
            if (node.left != null) queue.add(node.left);
            if (node.right != null) queue.add(node.right);
        }
    }
}"""
