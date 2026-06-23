from application.curriculum.content.v4_code_format import format_reference_code
from application.curriculum.content.v4_assembly_builder import _reference_lines, line_assembly_payload

raw = "".join(
    [
        "type PNode=^TNode; TNode=record value:integer; next:PNode; end; var he",
        "ad:PNode; begin new(head); head^.value:=10; writeln(head^.value); end.",
    ]
)
formatted = format_reference_code(raw, "pascal")
print("formatted:")
print(formatted)
print("lines:", _reference_lines(formatted))
print("payload blocks:", line_assembly_payload("pascal", raw)[2])
