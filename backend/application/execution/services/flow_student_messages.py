"""Student-facing flow validation messages (no answer spoilers)."""

from __future__ import annotations

STUDENT_FLOW_ERROR_MESSAGES: dict[str, str] = {
    "FLOW_SEQUENCE_MISMATCH": (
        "Проверьте общий порядок схемы: выполнение должно идти "
        "от начала к завершению без пропусков."
    ),
    "FLOW_TEXT_MISMATCH": (
        "Некоторые блоки не соответствуют операциям в коде. "
        "Сравните текст блоков с программой слева."
    ),
    "FLOW_CONSTRUCTION_MISSING": (
        "На схеме не хватает нужного типа блока. "
        "Для Writeln — блок «Вывод», для Readln — «Ввод», "
        "для if — «Условие», для цикла — «Цикл»."
    ),
    "FLOW_LOOP_BACK_EDGE": (
        "Для цикла нужна связь, которая возвращает выполнение "
        "к следующей итерации."
    ),
}


def student_flow_error_text(error_type: str, *, fallback: str = "") -> str:
    return STUDENT_FLOW_ERROR_MESSAGES.get(error_type, fallback)
