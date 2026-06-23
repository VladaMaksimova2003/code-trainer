"""Curated Pascal debug buggy/fixed pairs for v192 expansion debug slots.

Goal: keep debug tasks meaningful for Pascal track (buggy_code != fixed_code and
the bug reflects the intended pitfall).
"""

from __future__ import annotations

from typing import Dict, Tuple


PASCAL_DEBUG_PAIRS_129_192: Dict[int, Tuple[str, str]] = {
    # --- chapters 1–4 (129–144) ---
    131: (
        # BUG: real division instead of integer division
        "var n, i, x, total: integer;\n"
        "    avg: real;\n"
        "begin\n"
        "  readln(n);\n"
        "  total := 0;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(x);\n"
        "    total := total + x;\n"
        "  end;\n"
        "  avg := total / n;\n"
        "  writeln(avg);\n"
        "end.",
        # FIX: integer division, output integer
        "var n, i, x, total: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  total := 0;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(x);\n"
        "    total := total + x;\n"
        "  end;\n"
        "  writeln(total div n);\n"
        "end.",
    ),
    135: (
        # BUG: strict comparisons exclude boundaries
        "var a, b, x: integer;\n"
        "begin\n"
        "  readln(a, b, x);\n"
        "  if (a < x) and (x < b) then writeln('yes') else writeln('no');\n"
        "end.",
        # FIX: inclusive bounds
        "var a, b, x: integer;\n"
        "begin\n"
        "  readln(a, b, x);\n"
        "  if (a <= x) and (x <= b) then writeln('yes') else writeln('no');\n"
        "end.",
    ),
    139: (
        # BUG: sums non-negative (includes 0 inside stream) + stops after n values
        "var n, i, x, total: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  total := 0;\n"
        "  for i := 0 to n do\n"
        "  begin\n"
        "    readln(x);\n"
        "    if x >= 0 then total := total + x;\n"
        "  end;\n"
        "  writeln(total);\n"
        "end.",
        # FIX: read until 0, sum only positive
        "var x, total: integer;\n"
        "begin\n"
        "  total := 0;\n"
        "  readln(x);\n"
        "  while x <> 0 do\n"
        "  begin\n"
        "    if x > 0 then total := total + x;\n"
        "    readln(x);\n"
        "  end;\n"
        "  writeln(total);\n"
        "end.",
    ),
    143: (
        # BUG: prints in the same order (no reverse)
        "var n, i, x: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(x);\n"
        "    write(x, ' ');\n"
        "  end;\n"
        "end.",
        # FIX: store and print reversed (1-based array)
        "var n, i: integer;\n"
        "    a: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do readln(a[i]);\n"
        "  for i := n downto 1 do\n"
        "  begin\n"
        "    write(a[i]);\n"
        "    if i > 1 then write(' ');\n"
        "  end;\n"
        "end.",
    ),

    # --- chapters 5–16 (145–192) ---
    147: (
        # BUG: uses Pascal 1-based Pos result directly (and 0 for not found)
        "var s, c: string;\n"
        "    p: integer;\n"
        "begin\n"
        "  readln(s);\n"
        "  readln(c);\n"
        "  p := pos(c, s);\n"
        "  writeln(p);\n"
        "end.",
        # FIX: required 0-based index, -1 when not found
        "var s, c: string;\n"
        "    p: integer;\n"
        "begin\n"
        "  readln(s);\n"
        "  readln(c);\n"
        "  p := pos(c, s);\n"
        "  if p = 0 then writeln(-1) else writeln(p - 1);\n"
        "end.",
    ),
    151: (
        # BUG: computes into local variable but never returns it
        "function fact(n: integer): int64;\n"
        "var res: int64;\n"
        "begin\n"
        "  if n <= 1 then res := 1\n"
        "  else res := n * fact(n - 1);\n"
        "  { BUG: forgot to assign function result }\n"
        "end;\n"
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  writeln(fact(n));\n"
        "end.",
        # FIX: return value properly
        "function fact(n: integer): int64;\n"
        "begin\n"
        "  if n <= 1 then fact := 1\n"
        "  else fact := n * fact(n - 1);\n"
        "end;\n"
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  writeln(fact(n));\n"
        "end.",
    ),
    155: (
        # BUG: base case n==1 (n==0 breaks recursion)
        "function fact(n: integer): int64;\n"
        "begin\n"
        "  if n = 1 then fact := 1\n"
        "  else fact := n * fact(n - 1);\n"
        "end;\n"
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  writeln(fact(n));\n"
        "end.",
        # FIX: base case n<=1
        "function fact(n: integer): int64;\n"
        "begin\n"
        "  if n <= 1 then fact := 1\n"
        "  else fact := n * fact(n - 1);\n"
        "end;\n"
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  writeln(fact(n));\n"
        "end.",
    ),
    159: (
        # BUG: off-by-one bubble sort loop bounds (misses last compare)
        "var n, i, j, t: integer;\n"
        "    a: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do readln(a[i]);\n"
        "  for i := 1 to n do\n"
        "    for j := 1 to n - i - 1 do\n"
        "      if a[j] > a[j+1] then\n"
        "      begin\n"
        "        t := a[j]; a[j] := a[j+1]; a[j+1] := t;\n"
        "      end;\n"
        "  for i := 1 to n do begin write(a[i]); if i < n then write(' '); end;\n"
        "end.",
        # FIX: correct bounds
        "var n, i, j, t: integer;\n"
        "    a: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do readln(a[i]);\n"
        "  for i := 1 to n do\n"
        "    for j := 1 to n - i do\n"
        "      if a[j] > a[j+1] then\n"
        "      begin\n"
        "        t := a[j]; a[j] := a[j+1]; a[j+1] := t;\n"
        "      end;\n"
        "  for i := 1 to n do begin write(a[i]); if i < n then write(' '); end;\n"
        "end.",
    ),
    163: (
        # BUG: truncates average instead of Round()
        "var n, i, x, total: integer;\n"
        "    avg: real;\n"
        "begin\n"
        "  readln(n);\n"
        "  total := 0;\n"
        "  for i := 1 to n do begin readln(x); total := total + x; end;\n"
        "  avg := total / n;\n"
        "  writeln(trunc(avg));\n"
        "end.",
        # FIX: Round()
        "var n, i, x, total: integer;\n"
        "    avg: real;\n"
        "begin\n"
        "  readln(n);\n"
        "  total := 0;\n"
        "  for i := 1 to n do begin readln(x); total := total + x; end;\n"
        "  avg := total / n;\n"
        "  writeln(round(avg));\n"
        "end.",
    ),
    167: (
        # BUG: returns -1 when not found
        "var n, i, best, cnt, found: integer;\n"
        "    key, q: string;\n"
        "    keys: array[1..1000] of string;\n"
        "    vals: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  cnt := 0;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(key);\n"
        "    found := 0;\n"
        "    for best := 1 to cnt do\n"
        "      if keys[best] = key then begin vals[best] := vals[best] + 1; found := 1; break; end;\n"
        "    if found = 0 then begin cnt := cnt + 1; keys[cnt] := key; vals[cnt] := 1; end;\n"
        "  end;\n"
        "  readln(q);\n"
        "  for best := 1 to cnt do if keys[best] = q then begin writeln(vals[best]); halt; end;\n"
        "  writeln(-1);\n"
        "end.",
        # FIX: returns 0 when not found
        "var n, i, idx, cnt, found: integer;\n"
        "    key, q: string;\n"
        "    keys: array[1..1000] of string;\n"
        "    vals: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  cnt := 0;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(key);\n"
        "    found := 0;\n"
        "    for idx := 1 to cnt do\n"
        "      if keys[idx] = key then begin vals[idx] := vals[idx] + 1; found := 1; break; end;\n"
        "    if found = 0 then begin cnt := cnt + 1; keys[cnt] := key; vals[cnt] := 1; end;\n"
        "  end;\n"
        "  readln(q);\n"
        "  for idx := 1 to cnt do if keys[idx] = q then begin writeln(vals[idx]); halt; end;\n"
        "  writeln(0);\n"
        "end.",
    ),
    171: (
        # BUG: does not skip empty lines (may crash on empty)
        "var line, name, valS: string;\n"
        "    p, total: integer;\n"
        "begin\n"
        "  total := 0;\n"
        "  while not eof do\n"
        "  begin\n"
        "    readln(line);\n"
        "    p := pos(',', line);\n"
        "    name := copy(line, 1, p-1);\n"
        "    valS := copy(line, p+1, length(line)-p);\n"
        "    total := total + strtoint(valS);\n"
        "  end;\n"
        "  writeln(total);\n"
        "end.",
        # FIX: skip empty lines
        "uses sysutils;\n"
        "var line, valS: string;\n"
        "    p, total: integer;\n"
        "begin\n"
        "  total := 0;\n"
        "  while not eof do\n"
        "  begin\n"
        "    readln(line);\n"
        "    line := trim(line);\n"
        "    if line = '' then continue;\n"
        "    p := pos(',', line);\n"
        "    valS := copy(line, p+1, length(line)-p);\n"
        "    total := total + strtoint(valS);\n"
        "  end;\n"
        "  writeln(total);\n"
        "end.",
    ),
    175: (
        # BUG: pops from empty stack
        "var s: string;\n"
        "    st: array[1..10000] of char;\n"
        "    top, i: integer;\n"
        "    ch: char;\n"
        "function match(o, c: char): boolean;\n"
        "begin\n"
        "  match := ((o='(') and (c=')')) or ((o='[') and (c=']')) or ((o='{') and (c='}'));\n"
        "end;\n"
        "begin\n"
        "  readln(s);\n"
        "  top := 0;\n"
        "  for i := 1 to length(s) do\n"
        "  begin\n"
        "    ch := s[i];\n"
        "    if (ch='(') or (ch='[') or (ch='{') then begin top := top + 1; st[top] := ch; end\n"
        "    else begin\n"
        "      { BUG: assumes stack not empty }\n"
        "      if not match(st[top], ch) then begin writeln('no'); halt; end;\n"
        "      top := top - 1;\n"
        "    end;\n"
        "  end;\n"
        "  if top = 0 then writeln('yes') else writeln('no');\n"
        "end.",
        # FIX: check empty before pop
        "var s: string;\n"
        "    st: array[1..10000] of char;\n"
        "    top, i: integer;\n"
        "    ch: char;\n"
        "function match(o, c: char): boolean;\n"
        "begin\n"
        "  match := ((o='(') and (c=')')) or ((o='[') and (c=']')) or ((o='{') and (c='}'));\n"
        "end;\n"
        "begin\n"
        "  readln(s);\n"
        "  top := 0;\n"
        "  for i := 1 to length(s) do\n"
        "  begin\n"
        "    ch := s[i];\n"
        "    if (ch='(') or (ch='[') or (ch='{') then begin top := top + 1; st[top] := ch; end\n"
        "    else begin\n"
        "      if top = 0 then begin writeln('no'); halt; end;\n"
        "      if not match(st[top], ch) then begin writeln('no'); halt; end;\n"
        "      top := top - 1;\n"
        "    end;\n"
        "  end;\n"
        "  if top = 0 then writeln('yes') else writeln('no');\n"
        "end.",
    ),
    179: (
        # BUG: starts from 2, so cannot delete the first element
        "var n, i, v, idx: integer;\n"
        "    a: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do readln(a[i]);\n"
        "  readln(v);\n"
        "  idx := 0;\n"
        "  for i := 2 to n do if a[i] = v then begin idx := i; break; end;\n"
        "  if idx <> 0 then for i := idx to n - 1 do a[i] := a[i + 1];\n"
        "  if idx <> 0 then n := n - 1;\n"
        "  for i := 1 to n do begin write(a[i]); if i < n then write(' '); end;\n"
        "end.",
        # FIX: remove first occurrence from 1..n
        "var n, i, v, idx: integer;\n"
        "    a: array[1..1000] of integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do readln(a[i]);\n"
        "  readln(v);\n"
        "  idx := 0;\n"
        "  for i := 1 to n do if a[i] = v then begin idx := i; break; end;\n"
        "  if idx <> 0 then for i := idx to n - 1 do a[i] := a[i + 1];\n"
        "  if idx <> 0 then n := n - 1;\n"
        "  for i := 1 to n do begin write(a[i]); if i < n then write(' '); end;\n"
        "end.",
    ),
    183: (
        # BUG: treats vertices as 1-based
        "var n, m, i, u, v: integer;\n"
        "    g: array[1..1000, 1..1000] of boolean;\n"
        "    used: array[1..1000] of boolean;\n"
        "procedure dfs(x: integer);\n"
        "var y: integer;\n"
        "begin\n"
        "  used[x] := true;\n"
        "  write(x, ' ');\n"
        "  for y := 1 to n do if g[x, y] and (not used[y]) then dfs(y);\n"
        "end;\n"
        "begin\n"
        "  readln(n, m);\n"
        "  for i := 1 to m do begin readln(u, v); g[u+1, v+1] := true; g[v+1, u+1] := true; end;\n"
        "  dfs(1);\n"
        "end.",
        # FIX: 0-based vertices, start from 0
        "var n, m, i, u, v: integer;\n"
        "    g: array[0..999, 0..999] of boolean;\n"
        "    used: array[0..999] of boolean;\n"
        "procedure dfs(x: integer);\n"
        "var y: integer;\n"
        "begin\n"
        "  used[x] := true;\n"
        "  write(x);\n"
        "  write(' ');\n"
        "  for y := 0 to n - 1 do if g[x, y] and (not used[y]) then dfs(y);\n"
        "end;\n"
        "begin\n"
        "  readln(n, m);\n"
        "  for i := 1 to m do begin readln(u, v); g[u, v] := true; g[v, u] := true; end;\n"
        "  dfs(0);\n"
        "end.",
    ),
    187: (
        # BUG: allows balance to go negative
        "var dep, wd, bal: integer;\n"
        "begin\n"
        "  readln(dep);\n"
        "  readln(wd);\n"
        "  bal := dep - wd;\n"
        "  writeln(bal);\n"
        "end.",
        # FIX: clamp at 0
        "var dep, wd, bal: integer;\n"
        "begin\n"
        "  readln(dep);\n"
        "  readln(wd);\n"
        "  bal := dep - wd;\n"
        "  if bal < 0 then bal := 0;\n"
        "  writeln(bal);\n"
        "end.",
    ),
    191: (
        # BUG: missing virtual/override, always calls base speak
        "type\n"
        "  TAnimal = class\n"
        "    function Speak: string; \n"
        "  end;\n"
        "  TDog = class(TAnimal)\n"
        "    function Speak: string; \n"
        "  end;\n"
        "  TCat = class(TAnimal)\n"
        "    function Speak: string; \n"
        "  end;\n"
        "function TAnimal.Speak: string; begin Speak := '...'; end;\n"
        "function TDog.Speak: string; begin Speak := 'woof'; end;\n"
        "function TCat.Speak: string; begin Speak := 'meow'; end;\n"
        "var n, i: integer; kind: string; a: TAnimal;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(kind);\n"
        "    if kind = 'Dog' then a := TDog.Create else a := TCat.Create;\n"
        "    write(a.Speak, ' ');\n"
        "    a.Free;\n"
        "  end;\n"
        "end.",
        # FIX: virtual + override ensures polymorphic dispatch
        "type\n"
        "  TAnimal = class\n"
        "    function Speak: string; virtual;\n"
        "  end;\n"
        "  TDog = class(TAnimal)\n"
        "    function Speak: string; override;\n"
        "  end;\n"
        "  TCat = class(TAnimal)\n"
        "    function Speak: string; override;\n"
        "  end;\n"
        "function TAnimal.Speak: string; begin Speak := '...'; end;\n"
        "function TDog.Speak: string; begin Speak := 'woof'; end;\n"
        "function TCat.Speak: string; begin Speak := 'meow'; end;\n"
        "var n, i: integer; kind: string; a: TAnimal;\n"
        "begin\n"
        "  readln(n);\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    readln(kind);\n"
        "    if kind = 'Dog' then a := TDog.Create else a := TCat.Create;\n"
        "    write(a.Speak, ' ');\n"
        "    a.Free;\n"
        "  end;\n"
        "end.",
    ),
}

