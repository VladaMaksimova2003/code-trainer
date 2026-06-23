PASCAL = """var a, b: string;
    i: integer;
    ok: boolean;
    ca, cb: array[0..255] of integer;
begin
  readln(a);
  readln(b);

  if length(a) <> length(b) then
    writeln('no')
  else
  begin
    for i := 0 to 255 do
    begin
      ca[i] := 0;
      cb[i] := 0;
    end;

    for i := 1 to length(a) do
      ca[Ord(a[i])] := ca[Ord(a[i])] + 1;

    for i := 1 to length(b) do
      cb[Ord(b[i])] := cb[Ord(b[i])] + 1;

    ok := true;

    for i := 0 to 255 do
      if ca[i] <> cb[i] then
        ok := false;

    if ok then
      writeln('yes')
    else
      writeln('no');
  end;
end."""

PYTHON = """a = ''.join(sorted(input()))
b = ''.join(sorted(input()))

print('yes' if a == b else 'no')"""

CPP = """#include <iostream>
#include <string>
#include <algorithm>

int main() {
    std::string a, b;
    std::getline(std::cin, a);
    std::getline(std::cin, b);

    std::sort(a.begin(), a.end());
    std::sort(b.begin(), b.end());

    std::cout << (a == b ? "yes" : "no");
    return 0;
}"""

CSHARP = """using System;
using System.Linq;

class Program {
    static void Main() {
        string a = new string(Console.ReadLine().OrderBy(c => c).ToArray());
        string b = new string(Console.ReadLine().OrderBy(c => c).ToArray());

        Console.WriteLine(a == b ? "yes" : "no");
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        char[] a = sc.nextLine().toCharArray();
        char[] b = sc.nextLine().toCharArray();

        Arrays.sort(a);
        Arrays.sort(b);

        System.out.println(Arrays.equals(a, b) ? "yes" : "no");
    }
}"""
