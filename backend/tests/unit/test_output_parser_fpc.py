from infrastructure.execution.output_parser import parse_diagnostics

FPC_SAMPLE = """\
Free Pascal Compiler version 3.2.2+dfsg-9ubuntu1 [2022/04/11] for x86_64
Copyright (c) 1993-2021 by Florian Klaempfl and others
Target OS: Linux for x86-64
Compiling /tmp/home/source.pas
source.pas(2,6) Error: Identifier not found "n"
"""


def test_fpc_diagnostics_filter_toolchain_noise():
    sample = """\
Free Pascal Compiler version 3.2.2+dfsg-9ubuntu1 [2022/04/11] for x86_64
Copyright (c) 1993-2021 by Florian Klaempfl and others
source.pas(3,3) Error: Illegal expression
source.pas(4,3) Fatal: Syntax error, ";" expected but "identifier N" found
Fatal: Compilation aborted
Error: /usr/bin/ppcx64 returned an error exitcode
"""
    result = parse_diagnostics(sample)
    assert result == [
        "Line 3:3: error: Illegal expression",
        'Line 4:3: fatal: Syntax error, ";" expected but "identifier N" found',
    ]
