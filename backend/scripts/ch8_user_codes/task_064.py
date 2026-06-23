FIXED_PASCAL = """type Player = record
  name: string;
  score, solved: integer;
end;

var n, i, j: integer;
    players: array[1..100] of Player;
    temp: Player;
begin
  readln(n);

  for i := 1 to n do
    readln(players[i].name, players[i].score, players[i].solved);

  for i := 1 to n do
    for j := i + 1 to n do
      if (players[j].score > players[i].score) or
         ((players[j].score = players[i].score) and (players[j].solved > players[i].solved)) or
         ((players[j].score = players[i].score) and (players[j].solved = players[i].solved) and (players[j].name < players[i].name)) then
      begin
        temp := players[i];
        players[i] := players[j];
        players[j] := temp;
      end;

  for i := 1 to n do
    writeln(i, ' ', players[i].name, ' ', players[i].score, ' ', players[i].solved);
end."""

BUGGY_PASCAL = """type Player = record
  name: string;
  score, solved: integer;
end;

var n, i: integer;
    players: array[1..100] of Player;
begin
  n = int(input());

  for i in range(n) do
    readln(players[i].name, players[i].score, players[i].solved);

  players.sort(key=lambda p: (p.score, p.solved, p.name));

  for i := 0 to n do
    print(i, players[i].name, players[i].score, players[i].solved);
end."""

FIXED_PYTHON = """n = int(input())
players = []

for _ in range(n):
    name, score, solved = input().split()
    players.append((name, int(score), int(solved)))

players.sort(key=lambda item: (-item[1], -item[2], item[0]))

for i, player in enumerate(players, start=1):
    name, score, solved = player
    print(i, name, score, solved)"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
players = new List<Player>()

for i := 1 to n do:
    name, score, solved = input().split()
    players.Add((name, score, solved))

players.sort(key=lambda item: (item[1], item[2], item[0]))

for i in range(n):
    Console.WriteLine(i, players[i].name, players[i].score, players[i].solved)"""

FIXED_CPP = """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

struct Player {
    std::string name;
    int score;
    int solved;
};

int main() {
    int n;
    std::cin >> n;

    std::vector<Player> players(n);

    for (int i = 0; i < n; i++) {
        std::cin >> players[i].name >> players[i].score >> players[i].solved;
    }

    std::sort(players.begin(), players.end(), [](const Player& a, const Player& b) {
        if (a.score != b.score) {
            return a.score > b.score;
        }
        if (a.solved != b.solved) {
            return a.solved > b.solved;
        }
        return a.name < b.name;
    });

    for (int i = 0; i < n; i++) {
        std::cout << i + 1 << ' '
                  << players[i].name << ' '
                  << players[i].score << ' '
                  << players[i].solved << '\n';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

class Player {
    string name;
    int score;
    int solved;
};

int main() {
    int n = int(input());
    vector<Player> players = new Player[n];

    for i in range(n):
        cin >> players[i].name >> players[i].score >> players[i].solved;

    players.sort(key=lambda p: (p.score, p.solved, p.name));

    for (int i = 0; i <= n; i++) {
        Console.WriteLine(i, players[i].name, players[i].score, players[i].solved);
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Player {
    public string Name;
    public int Score;
    public int Solved;
}

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Player[] players = new Player[n];

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            players[i] = new Player {
                Name = p[0],
                Score = int.Parse(p[1]),
                Solved = int.Parse(p[2])
            };
        }

        Array.Sort(players, (a, b) => {
            if (a.Score != b.Score) {
                return b.Score.CompareTo(a.Score);
            }

            if (a.Solved != b.Solved) {
                return b.Solved.CompareTo(a.Solved);
            }

            return a.Name.CompareTo(b.Name);
        });

        for (int i = 0; i < n; i++) {
            Console.WriteLine($"{i + 1} {players[i].Name} {players[i].Score} {players[i].Solved}");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Player {
    string name;
    int score;
    int solved;
}

class Program {
    static void Main() {
        int n = int(input());
        Player[] players = [];

        for i in range(n):
            players[i].name, players[i].score, players[i].solved = Console.ReadLine().Split();

        players.sort(key=lambda p: (p.score, p.solved, p.name));

        for (int i = 0; i <= n; i++) {
            print(i, players[i].name, players[i].score, players[i].solved);
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Player {
    String name;
    int score;
    int solved;

    Player(String name, int score, int solved) {
        this.name = name;
        this.score = score;
        this.solved = solved;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Player[] players = new Player[n];

        for (int i = 0; i < n; i++) {
            players[i] = new Player(sc.next(), sc.nextInt(), sc.nextInt());
        }

        Arrays.sort(players, (a, b) -> {
            if (a.score != b.score) {
                return b.score - a.score;
            }

            if (a.solved != b.solved) {
                return b.solved - a.solved;
            }

            return a.name.compareTo(b.name);
        });

        for (int i = 0; i < n; i++) {
            System.out.println(
                (i + 1) + " " +
                players[i].name + " " +
                players[i].score + " " +
                players[i].solved
            );
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Player {
    string name;
    int score;
    int solved;
}

class Main {
    public static void main(String[] args) {
        int n = int(input());
        Player[] players = [];

        for i in range(n):
            players[i] = new Player(Scanner.next(), Scanner.nextInt(), Scanner.nextInt());

        players.sort(key=lambda p: (p.score, p.solved, p.name));

        for (int i = 0; i <= n; i++) {
            Console.WriteLine(i + " " + players[i].name + " " + players[i].score + " " + players[i].solved);
        }
    }
}"""
