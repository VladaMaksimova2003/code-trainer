from infrastructure.analysis.tree_sitter_gateway import parse_code


def show(code: str, lang: str = "pascal") -> None:
    t = parse_code(code, lang)
    if not t:
        print("parse fail")
        return

    def walk(n, d=0):
        if d > 5:
            return
        print("  " * d + n.type, repr(n.text.decode()[:50]))
        for c in n.children:
            walk(c, d + 1)

    walk(t.root_node)


if __name__ == "__main__":
    print("=== FOR 0..n ===")
    show("program T; var i,n: integer; begin for i := 0 to n do writeln(i); end.")
    print("=== CPP FOR ===")
    show("int main(){ for(int i=0;i<n;i++) return 0; }", "cpp")
    print("=== PASCAL == ===")
    show("program T; begin if x == 5 then writeln(x); end.")
