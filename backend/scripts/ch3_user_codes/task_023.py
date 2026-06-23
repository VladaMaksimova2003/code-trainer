FIXED_PASCAL = """var n, i, x: integer;
    freq: array[0..9] of integer;
begin
  readln(n);

  for i := 0 to 9 do
    freq[i] := 0;

  for i := 1 to n do
  begin
    readln(x);

    if (x >= 0) and (x <= 9) then
      freq[x] := freq[x] + 1;
  end;

  for i := 0 to 9 do
    write(freq[i], ' ');
end."""

BUGGY_PASCAL = """var n, i, x, total: integer
begin
  readln(n);
  total := 0;

  for i := 1 to n do
  begin
    readln(x);

    if x <= 0 then
      total := total + x;
  end;

  writeln(total);
end."""

FIXED_PYTHON = """n = int(input())

freq = [0] * 10

for _ in range(n):
    x = int(input())

    if 0 <= x <= 9:
        freq[x] += 1

print(' '.join(str(v) for v in freq), end=' ')"""

BUGGY_PYTHON = """n = int(input())
total = 0
for _ in range(n)
    x = int(input())
    if x <= 0:
        total += x
print(total)"""

FIXED_CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> freq(10, 0);

    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;

        if (x >= 0 && x <= 9) {
            freq[x]++;
        }
    }

    for (int value : freq) {
        std::cout << value << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream<
int main(){int n,x,total=0 std::cin>>n; for(int i=0;i<n;i++){std::cin>>x; if(x>=0) total+=x;} std::cout<<total;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        int[] freq = new int[10];

        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());

            if (x >= 0 && x <= 9) {
                freq[x]++;
            }
        }

        foreach (int value in freq) {
            Console.Write(value + " ");
        }
    }
}"""

BUGGY_CSHARP = """using System
class Program{static void Main(){
  int n=int.Parse(Console.ReadLine()), total=0;
  for(int i=0;i<n;i++){int x=int.Parse(Console.ReadLine()); if(x<=0) total+=x;}
  Console.WriteLine(total);
}}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] freq = new int[10];

        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();

            if (x >= 0 && x <= 9) {
                freq[x]++;
            }
        }

        for (int value : freq) {
            System.out.print(value + " ");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*
class Main{public static void main(String[] args){
  Scanner sc=new Scanner(System.in); int n=sc.nextInt(), total=0;
  for(int i=0;i<n;i++){int x=sc.nextInt(); if(x<=0) total+=x;}
  System.out.println(total);
}}"""
