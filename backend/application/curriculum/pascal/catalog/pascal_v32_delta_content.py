"""Seed payloads for Pascal v3.2 delta slots."""

from __future__ import annotations

V32_DEBUG_STARTER: dict[str, str] = {
    "exc_02": (
        "program Demo;\nbegin\n"
        "  try\n"
        "    raise Exception.Create('fail');\n"
        "  except on E: Integer do\n"
        "    Writeln('caught');\n"
        "end.\n"
    ),
    "exc_04": (
        "program Demo;\nbegin\n"
        "  try\n"
        "    raise Exception.Create('fail');\n"
        "  except\n"
        "    on E: Exception do\n"
        "      raise Exception.Create('lost');\n"
        "end.\n"
    ),
    "exc_05": (
        "program Demo;\nbegin\n"
        "  try\n"
        "    Writeln(1 div 0);\n"
        "  except\n"
        "  end;\n"
        "end.\n"
    ),
    "exc_07": (
        "program Demo;\nvar F: TextFile;\nbegin\n"
        "  Assign(F, 'missing.txt');\n"
        "  Reset(F);\n"
        "  CloseFile(F);\n"
        "end.\n"
    ),
    "exp_09": (
        "program Demo;\nvar n: integer;\nbegin\n"
        "  n := 2 + 3 * 4;\n"
        "  Writeln(n);\n"
        "end.\n"
    ),
    "exp_11": (
        "program Demo;\nvar x: real;\nbegin\n"
        "  x := 0.1 + 0.2;\n"
        "  if x = 0.3 then Writeln('eq');\n"
        "end.\n"
    ),
    "pit_05": (
        "program Demo;\nvar v: integer;\nbegin\n"
        "  v := 0;\n"
        "  if v then Writeln('yes')\n"
        "  else Writeln('no');\n"
        "end.\n"
    ),
    "pit_06": (
        "program Demo;\nvar A, B: array of integer;\nbegin\n"
        "  SetLength(A, 3);\n"
        "  B := A;\n"
        "  A[0] := 1;\n"
        "  Writeln(B[0]);\n"
        "end.\n"
    ),
    "pit_20": (
        "program Demo;\nvar Count: integer;\nbegin\n"
        "  count := 1;\n"
        "  Writeln(Count);\n"
        "end.\n"
    ),
    "cdg_08": (
        "program Demo;\nvar a: array[1..3] of integer;\nbegin\n"
        "  Writeln(a[4]);\n"
        "end.\n"
    ),
    "cdg_10": (
        "program Demo;\nbegin\n"
        "  var x: integer;\n"
        "  x := 1;\n"
        "end.\n"
    ),
    "dyn_12": (
        "program Demo;\nvar a: array of integer; n: integer;\nbegin\n"
        "  Readln(n);\n"
        "  SetLength(a, n - 1);\n"
        "  Writeln(Length(a));\n"
        "end.\n"
    ),
    "unt_14": (
        "unit A;\ninterface\nuses B;\nimplementation\nend.\n"
    ),
    "oop_20": (
        "type\n  TBox = class\n"
        "  private F: integer;\n"
        "  public\n"
        "    property Value write F;\n"
        "  end;\n"
    ),
    "rec_12": (
        "type\n  TRec = record\n"
        "    case Integer of\n"
        "      0: (I: integer);\n"
        "      1: (S: string);\n"
        "  end;\n"
        "var R: TRec;\nbegin\n"
        "  R.I := 1;\n"
        "  Writeln(R.S);\n"
        "end.\n"
    ),
    "fil_09": (
        "program Demo;\nvar F: TextFile; s: string;\nbegin\n"
        "  Assign(F, 'empty.txt');\n"
        "  Reset(F);\n"
        "  Readln(F, s);\n"
        "  Writeln(s);\n"
        "  CloseFile(F);\n"
        "end.\n"
    ),
}

V32_REFERENCE: dict[str, str] = {
    "exc_01": (
        "try\n"
        "  Writeln(1 div 0);\n"
        "except\n"
        "  on E: Exception do Writeln('err');\n"
        "end;"
    ),
    "exc_02": (
        "try\n"
        "  raise Exception.Create('fail');\n"
        "except\n"
        "  on E: Exception do Writeln('caught');\n"
        "end;"
    ),
    "exc_04": (
        "try\n"
        "  raise Exception.Create('fail');\n"
        "except\n"
        "  on E: Exception do\n"
        "    raise;\n"
        "end;"
    ),
    "exc_05": (
        "try\n"
        "  Writeln(1 div 0);\n"
        "except\n"
        "  on E: Exception do Writeln('handled');\n"
        "end;"
    ),
    "exc_06": (
        "type EMy = class(Exception);\n"
        "begin\n"
        "  raise EMy.Create('custom');\n"
        "end;"
    ),
    "exc_07": (
        "try\n"
        "  Assign(F, 'missing.txt'); Reset(F); CloseFile(F);\n"
        "except\n"
        "  on E: EInOutError do Writeln('no file');\n"
        "end;"
    ),
    "exc_08": (
        "try\n"
        "  Writeln(1 div 0);\n"
        "except\n"
        "  on E: Exception do Writeln('ok');\n"
        "end;"
    ),
    "exp_09": "n := 2 + (3 * 4);",
    "exp_10": "n := Trunc(r);",
    "exp_11": (
        "if Abs(x - 0.3) < 1e-9 then Writeln('eq');"
    ),
    "pit_05": "if v <> 0 then Writeln('yes') else Writeln('no');",
    "pit_06": (
        "SetLength(A, 3);\n"
        "SetLength(B, 3);\n"
        "A[0] := 1;\n"
        "Writeln(B[0]);"
    ),
    "pit_20": "Count := 1;\nWriteln(Count);",
    "cdg_08": "Writeln(a[3]);",
    "cdg_10": (
        "var x: integer;\n"
        "begin\n"
        "  x := 1;\n"
        "end."
    ),
    "oop_19": "property Name: string read FName;",
    "oop_20": "property Value: integer write F;",
    "dyn_12": "SetLength(a, n);",
    "rec_12": "R.I := 1;\nWriteln(R.I);",
    "fil_09": (
        "if not Eof(F) then Readln(F, s);\n"
        "Writeln(s);"
    ),
}

V32_TEST_CASES: dict[str, list[dict[str, str]]] = {
    "exc_01": [{"inputs": "", "output": "err"}],
    "exc_02": [{"inputs": "", "output": "caught"}],
    "exc_03": [{"inputs": "", "output": "done"}],
    "exc_04": [],
    "exc_05": [{"inputs": "", "output": "handled"}],
    "exc_06": [],
    "exc_07": [{"inputs": "", "output": "no file"}],
    "exc_08": [{"inputs": "", "output": "ok"}],
    "exp_09": [{"inputs": "", "output": "14"}],
    "exp_10": [{"inputs": "", "output": "3"}],
    "exp_11": [{"inputs": "", "output": "eq"}],
    "pit_05": [{"inputs": "", "output": "no"}],
    "pit_06": [{"inputs": "", "output": "0"}],
    "pit_20": [{"inputs": "", "output": "1"}],
    "cdg_08": [{"inputs": "", "output": "0"}],
    "cdg_10": [{"inputs": "", "output": "1"}],
    "lop_16": [{"inputs": "", "output": "1\n2\n3"}],
    "fn_13": [{"inputs": "", "output": "1"}],
    "dyn_12": [{"inputs": "3\n", "output": "3"}],
    "unt_15": [],
    "prc_14": [],
    "oop_19": [],
    "oop_20": [],
    "oop_21": [],
    "rec_12": [{"inputs": "", "output": "1"}],
    "fil_09": [{"inputs": "", "output": ""}],
}

V32_ASSEMBLY: dict[str, tuple[str, str, list[str], list[int], list[dict[str, str]]]] = {
    "exc_03": (
        "try\n  Writeln('work');\nfinally\n  Writeln('done');\nend;",
        "___",
        ["try", "  Writeln('work');", "finally", "  Writeln('done');", "end;"],
        [0, 1, 2, 3, 4],
        [{"inputs": "", "output": "work\ndone"}],
    ),
    "lop_16": (
        "for i := 1 to 3 do begin Writeln(i); end;",
        "___",
        ["for i := 1 to 3 do", "begin", "  Writeln(i);", "end;"],
        [0, 1, 2, 3],
        [{"inputs": "", "output": "1\n2\n3"}],
    ),
    "fn_13": (
        "function F: integer;\nbegin Result := 1; end;",
        "___",
        ["function F: integer;", "begin", "  Result := 1;", "end;"],
        [0, 1, 2, 3],
        [{"inputs": "", "output": "1"}],
    ),
    "unt_15": (
        "unit Utils;\ninterface\nprocedure P;\nimplementation\nprocedure P; begin end;\nend.",
        "___",
        ["unit Utils;", "interface", "procedure P;", "implementation", "procedure P; begin end;", "end."],
        [0, 1, 2, 3, 4, 5],
        [],
    ),
    "prc_14": (
        "procedure P; forward;\nprocedure P; begin end;",
        "___",
        ["procedure P; forward;", "procedure P; begin end;"],
        [0, 1],
        [],
    ),
    "oop_21": (
        "property Items[Index: integer]: integer read GetItem write SetItem;",
        "___",
        ["property Items[Index: integer]: integer read GetItem write SetItem;"],
        [0],
        [],
    ),
}

V32_KNOWN_CODE: dict[str, tuple[str, str, str, str]] = {
    "exc_01": (
        "try:\n    print(1 // 0)\nexcept Exception:\n    print('err')",
        "try { cout<<1/0; } catch(...) { cout<<\"err\"; }",
        "try { System.out.println(1/0); } catch (Exception e) { System.out.println(\"err\"); }",
        "try { Console.WriteLine(1/0); } catch { Console.WriteLine(\"err\"); }",
    ),
    "exc_02": (
        "try:\n    raise ValueError('fail')\nexcept ValueError:\n    print('caught')",
        "try { throw std::runtime_error(\"fail\"); } catch(...) { cout<<\"caught\"; }",
        "try { throw new Exception(\"fail\"); } catch (Exception e) { System.out.println(\"caught\"); }",
        "try { throw new Exception(\"fail\"); } catch { Console.WriteLine(\"caught\"); }",
    ),
    "exc_03": (
        "try:\n    print('work')\nfinally:\n    print('done')",
        "try { cout<<\"work\"; } finally { cout<<\"done\"; }",
        "try { System.out.println(\"work\"); } finally { System.out.println(\"done\"); }",
        "try { Console.WriteLine(\"work\"); } finally { Console.WriteLine(\"done\"); }",
    ),
    "exc_04": (
        "try:\n    raise RuntimeError('fail')\nexcept RuntimeError:\n    raise",
        "try { throw; } catch(...) { throw; }",
        "try { throw e; } catch (Exception ex) { throw ex; }",
        "try { throw; } catch { throw; }",
    ),
    "exc_05": (
        "try:\n    print(1/0)\nexcept ZeroDivisionError:\n    print('handled')",
        "try { } catch(...) { cout<<\"handled\"; }",
        "try { } catch (Exception e) { System.out.println(\"handled\"); }",
        "try { } catch { Console.WriteLine(\"handled\"); }",
    ),
    "exc_06": (
        "class EMy(Exception): pass\nraise EMy('custom')",
        "class EMy : public std::exception {};\nthrow EMy();",
        "class EMy extends Exception {}\nthrow new EMy();",
        "class EMy : Exception {}\nthrow new EMy();",
    ),
    "exc_07": (
        "try:\n    open('missing.txt')\nexcept FileNotFoundError:\n    print('no file')",
        "try { ifstream f(\"missing.txt\"); } catch(...) { cout<<\"no file\"; }",
        "try { Files.readAllLines(Path.of(\"missing.txt\")); } catch (IOException e) { System.out.println(\"no file\"); }",
        "try { File.ReadAllText(\"missing.txt\"); } catch { Console.WriteLine(\"no file\"); }",
    ),
    "exc_08": (
        "try:\n    risky()\nexcept Exception:\n    print('ok')",
        "try { risky(); } catch(...) { cout<<\"ok\"; }",
        "try { risky(); } catch (Exception e) { System.out.println(\"ok\"); }",
        "try { Risky(); } catch { Console.WriteLine(\"ok\"); }",
    ),
    "exp_09": (
        "n = 2 + (3 * 4)",
        "int n = 2 + (3 * 4);",
        "int n = 2 + (3 * 4);",
        "int n = 2 + (3 * 4);",
    ),
    "exp_10": (
        "n = int(r)",
        "int n = (int)r;",
        "int n = (int)r;",
        "int n = (int)r;",
    ),
    "exp_11": (
        "if abs(x - 0.3) < 1e-9: print('eq')",
        "if (fabs(x-0.3) < 1e-9) cout<<\"eq\";",
        "if (Math.abs(x-0.3) < 1e-9) System.out.println(\"eq\");",
        "if (Math.Abs(x-0.3) < 1e-9) Console.WriteLine(\"eq\");",
    ),
    "pit_05": (
        "if v != 0: print('yes')\nelse: print('no')",
        "if (v != 0) cout<<\"yes\"; else cout<<\"no\";",
        "if (v != 0) System.out.println(\"yes\"); else System.out.println(\"no\");",
        "if (v != 0) Console.WriteLine(\"yes\"); else Console.WriteLine(\"no\");",
    ),
    "pit_06": (
        "a = [0,0,0]\nb = [0,0,0]\na[0]=1\nprint(b[0])",
        "vector<int> a(3), b(3); a[0]=1; cout<<b[0];",
        "int[] a=new int[3], b=new int[3]; a[0]=1; System.out.println(b[0]);",
        "int[] a=new int[3], b=new int[3]; a[0]=1; Console.WriteLine(b[0]);",
    ),
    "pit_20": (
        "count = 1\nprint(Count)",
        "int count=1; cout<<count;",
        "int count=1; System.out.println(count);",
        "int count=1; Console.WriteLine(count);",
    ),
    "cdg_08": (
        "print(a[2])",
        "cout << a[2];",
        "System.out.println(a[2]);",
        "Console.WriteLine(a[2]);",
    ),
    "cdg_10": (
        "x = 1\nprint(x)",
        "int x=1; cout<<x;",
        "int x=1; System.out.println(x);",
        "int x=1; Console.WriteLine(x);",
    ),
    "lop_16": (
        "for i in range(1,4):\n    print(i)",
        "for (int i=1;i<=3;i++) cout<<i;",
        "for (int i=1;i<=3;i++) System.out.println(i);",
        "for (int i=1;i<=3;i++) Console.WriteLine(i);",
    ),
    "fn_13": (
        "def f():\n    return 1",
        "int f(){ return 1; }",
        "int f(){ return 1; }",
        "int F(){ return 1; }",
    ),
    "dyn_12": (
        "a = [0]*n",
        "a.resize(n);",
        "int[] a = new int[n];",
        "int[] a = new int[n];",
    ),
    "unt_14": (
        "# module A imports B, B imports A",
        "// circular include",
        "// circular import",
        "// circular reference",
    ),
    "unt_15": (
        "def p(): pass",
        "void p(){}",
        "void p(){}",
        "void P(){}",
    ),
    "prc_14": (
        "def p(): pass\n# forward declaration style",
        "void p(); void p(){}",
        "void p(); void p(){}",
        "void P(); void P(){}",
    ),
    "oop_19": (
        "@property\ndef name(self): return self._name",
        "string name() const { return _name; }",
        "String getName(){ return _name; }",
        "string Name => _name;",
    ),
    "oop_20": (
        "def set_value(self, v): self._v = v",
        "void setValue(int v){ _v=v; }",
        "void setValue(int v){ _v=v; }",
        "void set Value(int v){ _v=v; }",
    ),
    "oop_21": (
        "def __getitem__(self, i): return self._items[i]",
        "int& operator[](int i){ return _items[i]; }",
        "int get(int i){ return _items[i]; }",
        "int this[int i] => _items[i];",
    ),
    "rec_12": (
        "r = {'i': 1}\nprint(r['i'])",
        "cout << r.i;",
        "System.out.println(r.i);",
        "Console.WriteLine(r.i);",
    ),
    "fil_09": (
        "if line: print(line)",
        "if (!f.eof()) getline(f,line);",
        "if (scanner.hasNextLine()) line=scanner.nextLine();",
        "if (!reader.EndOfStream) line=reader.ReadLine();",
    ),
}

V32_EXPECTED_CONCEPT_OVERRIDES: dict[str, list[str]] = {
    "exc_01": ["exceptions"],
    "exc_02": ["exceptions"],
    "exc_03": ["exceptions"],
    "exc_04": ["exceptions"],
    "exc_05": ["exceptions"],
    "exc_06": ["exceptions"],
    "exc_07": ["exceptions"],
    "exc_08": ["exceptions"],
    "exp_09": ["arithmetic_ops"],
    "exp_10": ["arithmetic_ops"],
    "exp_11": ["arithmetic_ops"],
    "pit_05": ["assignment"],
    "pit_06": ["dynamic_array"],
    "pit_20": ["assignment"],
    "cdg_08": ["indexed_sequence"],
    "cdg_10": ["typed_declaration"],
    "oop_19": ["class_type"],
    "oop_20": ["class_type"],
    "oop_21": ["class_type"],
}
