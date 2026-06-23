from domain.entities.learning.error_message import ErrorMessage

FPC_SAMPLE = """\
Free Pascal Compiler version 3.2.2+dfsg-9ubuntu1 [2022/04/11] for x86_64
Copyright (c) 1993-2021 by Florian Klaempfl and others
Target OS: Linux for x86-64
Compiling /tmp/home/source.pas
source.pas(2,6) Error: Identifier not found "n"
"""


def test_error_message_from_fpc_output_is_short():
    errors = ErrorMessage.from_output(FPC_SAMPLE, "LINTER")
    assert len(errors) == 1
    assert errors[0].text == 'Line 2:6: error: Identifier not found "n"'
