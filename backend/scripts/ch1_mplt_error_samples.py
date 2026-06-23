"""Chapter-1 MPLT error samples — ATCC / FCC / AFCC for manual UI verification.

Run:
  cd backend
  python scripts/ch1_mplt_error_samples.py
  python scripts/ch1_mplt_error_samples.py --verify
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
_BACKEND = _SCRIPTS.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application.curriculum.display.atcc_idiom_engine import detect_atcc_carryover
from application.curriculum.display.pitfall_catalog import get_pitfall
from application.curriculum.display.transfer_pitfall_detector import (
    detect_afcc_pitfall,
    detect_fcc_pitfall,
    detect_transfer_pitfalls,
)

SOURCE = "python"
TARGET = "pascal"
PAIR_LABEL = f"{SOURCE} -> {TARGET}"

# slot → pattern (algo_basics ch1)
CH1_SLOTS: list[dict[str, str]] = [
    {"slot": "pas_001", "pattern": "task_002", "title": "Поиск первого товара по коду"},
    {"slot": "pas_002", "pattern": "task_005", "title": "Сумма выручки за период"},
    {"slot": "pas_003", "pattern": "task_006", "title": "Средняя загрузка сервера"},
    {"slot": "pas_004", "pattern": "task_001", "title": "Поиск максимума в массиве"},
    {"slot": "pas_005", "pattern": "task_004", "title": "Подсчёт положительных операций"},
    {"slot": "pas_006", "pattern": "task_007", "title": "Измерения не ниже порога"},
    {"slot": "pas_007", "pattern": "task_129", "title": "Сумма цифр числа"},
    {"slot": "pas_008", "pattern": "task_008", "title": "Итоговая: анализ оценок студентов"},
]

SAMPLES: list[dict[str, Any]] = [
    {
        "category": "ATCC",
        "slot": "pas_002",
        "pattern": "task_005",
        "pitfall_id": "for_range_off_by_one",
        "pair": PAIR_LABEL,
        "task_action": "сборка_программы · «Я знаю: Python» · учу Pascal",
        "trigger": "В Pascal-коде оставлена граница цикла как в Python range(n) (0..n-1).",
        "bad_code_pascal": """var n, i, sale, total: integer;
begin
  readln(n);
  total := 0;
  for i := 0 to n - 1 do
  begin
    readln(sale);
    total := total + sale;
  end;
  writeln(total);
end.""",
        "alt_bad_code_pascal": """# вставьте в редактор Python-синтаксис (сильный ATCC):
for i in range(n):
    total := total + sale""",
    },
    {
        "category": "ATCC",
        "slot": "pas_004",
        "pattern": "task_001",
        "pitfall_id": "for_range_off_by_one",
        "pair": PAIR_LABEL,
        "task_action": "сборка_программы · поиск максимума",
        "trigger": "Цикл for i := 0 to n-1 вместо for i := 1 to n.",
        "bad_code_pascal": """var n, i, score, best: integer;
begin
  readln(n);
  best := -1000000;
  for i := 0 to n - 1 do
  begin
    readln(score);
    if score > best then
      best := score;
  end;
  writeln(best);
end.""",
    },
    {
        "category": "FCC",
        "slot": "pas_003",
        "pattern": "task_006",
        "pitfall_id": "integer_division",
        "pair": PAIR_LABEL,
        "task_action": "сборка_фрагмента · среднее через div",
        "trigger": "В writeln оставлен оператор / (как в Python // или C++ int/).",
        "bad_code_pascal": """var n, i, load, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;
  writeln(total / n);
end.""",
    },
    {
        "category": "FCC",
        "slot": "pas_008",
        "pattern": "task_008",
        "pitfall_id": "integer_division",
        "pair": PAIR_LABEL,
        "task_action": "перевод_программы · итоговая",
        "trigger": "Среднее через / вместо div (вторая позиция вывода).",
        "bad_code_pascal": """var n, i, grade, best, total, passed: integer;
begin
  readln(n);
  total := 0;
  passed := 0;
  readln(best);
  total := total + best;
  if best >= 3 then passed := passed + 1;
  for i := 2 to n do
  begin
    readln(grade);
    total := total + grade;
    if grade > best then best := grade;
    if grade >= 3 then passed := passed + 1;
  end;
  writeln(best, ' ', total / n, ' ', passed);
end.""",
    },
    {
        "category": "FCC",
        "slot": "pas_001",
        "pattern": "task_002",
        "pitfall_id": "assignment_vs_compare",
        "pair": PAIR_LABEL,
        "task_action": "сборка_фрагмента · присваивание :=",
        "trigger": "Вместо := использован одиночный = (привычка из Python/C++).",
        "bad_code_pascal": """var n, i, code, target, position: integer;
begin
  readln(n);
  position = 0;
  for i := 1 to n do
  begin
    readln(code);
    if code = target then
      position = i;
  end;
  writeln(position);
end.""",
        "note": "Одиночный = вместо := (присваивание из Python/C++).",
    },
    {
        "category": "AFCC",
        "slot": "pas_001",
        "pattern": "task_002",
        "pitfall_id": "input_line_model",
        "pair": PAIR_LABEL,
        "task_action": "сборка_фрагмента · два числа в первой строке",
        "trigger": "Тесты падают: readln по одному числу, а вход «n target» в одной строке.",
        "bad_code_pascal": """var n, i, code, target, position: integer;
begin
  readln(n);
  readln(target);
  position := 0;
  for i := 1 to n do
  begin
    readln(code);
    if (code = target) and (position = 0) then
      position := i;
  end;
  writeln(position);
end.""",
        "contrast_test_index": 0,
        "first_test_input": "5 12\\n8\\n3\\n12\\n5\\n9\\n",
        "first_test_expected": "3",
    },
    {
        "category": "AFCC",
        "slot": "pas_008",
        "pattern": "task_008",
        "pitfall_id": "output_space_separated",
        "pair": PAIR_LABEL,
        "task_action": "перевод_программы · три числа в одной строке",
        "trigger": "Тесты падают: три writeln вместо одной строки с пробелами.",
        "bad_code_pascal": """var n, i, grade, best, total, passed: integer;
begin
  readln(n);
  total := 0;
  passed := 0;
  readln(best);
  total := total + best;
  if best >= 3 then passed := passed + 1;
  for i := 2 to n do
  begin
    readln(grade);
    total := total + grade;
    if grade > best then best := grade;
    if grade >= 3 then passed := passed + 1;
  end;
  writeln(best);
  writeln(total div n);
  writeln(passed);
end.""",
        "contrast_test_index": 0,
        "note": "Сначала «Прогнать» (тесты должны упасть). AFCC для output_space_separated — вторичный pitfall task_008.",
    },
]


def _simulate_afcc_test_results(*, failed: bool) -> list[dict[str, str]]:
    status = "FAILED" if failed else "PASSED"
    return [{"case": 1, "status": status, "expected": "x", "actual": "y"}]


def _predict_errors(sample: dict[str, Any]) -> list[dict[str, str]]:
    pitfall_id = str(sample["pitfall_id"])
    spec = get_pitfall(pitfall_id)
    if not spec:
        return []
    code = str(sample.get("bad_code_pascal") or "")
    category = str(sample["category"]).upper()
    concept_ids = list(spec.get("concept_ids") or [])
    errors: list[dict[str, str]] = []

    if category == "ATCC":
        errors.extend(
            detect_atcc_carryover(
                SOURCE,
                TARGET,
                code,
                expected_concepts=concept_ids,
            )
        )
        errors.extend(
            detect_transfer_pitfalls(
                pitfall_id=pitfall_id,
                transfer_type="ATCC",
                source_language=SOURCE,
                target_language=TARGET,
                code=code,
                test_results=_simulate_afcc_test_results(failed=True),
                buggy_code="",
                atcc_warnings=errors,
            )
        )
    elif category == "FCC":
        errors.extend(
            detect_fcc_pitfall(
                spec,
                target_language=TARGET,
                code=code,
                buggy_code=code,
                source_language=SOURCE,
            )
        )
    elif category == "AFCC":
        errors.extend(
            detect_afcc_pitfall(
                spec,
                target_language=TARGET,
                code=code,
                test_results=_simulate_afcc_test_results(failed=True),
                atcc_already_fired=False,
                source_language=SOURCE,
            )
        )
    return errors


def _print_sample(sample: dict[str, Any], *, verify: bool) -> None:
    category = sample["category"]
    print(f"\n{'=' * 72}")
    print(f"{category} · {sample['slot']} · {sample['pattern']} · {sample.get('title', '')}")
    print(f"Пара: {sample['pair']}")
    print(f"Задача: {sample.get('task_action', '')}")
    print(f"Pitfall: {sample['pitfall_id']}")
    print(f"Как воспроизвести: {sample['trigger']}")
    if sample.get("note"):
        print(f"Примечание: {sample['note']}")
    if sample.get("contrast_test_index") is not None:
        print(f"Контрастный тест: #{int(sample['contrast_test_index']) + 1}")
    if sample.get("first_test_input"):
        print(f"Вход теста 1: {sample['first_test_input']!r}")
    print("\n--- Код для вставки (Pascal) ---")
    print(sample["bad_code_pascal"].strip())
    if sample.get("alt_bad_code_pascal"):
        print("\n--- Альтернатива ---")
        print(str(sample["alt_bad_code_pascal"]).strip())

    if verify:
        errors = _predict_errors(sample)
        print("\n--- Ожидаемый вывод во вкладке «Ошибки» (Перенос) ---")
        if not errors:
            print("(детектор не сработал на этом сниппете — проверьте в UI вручную)")
        for err in errors:
            print(err.get("text") or err.get("feedback_ru") or json.dumps(err, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Chapter-1 MPLT error samples")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Прогнать детекторы и показать текст ошибок",
    )
    parser.add_argument(
        "--category",
        choices=["ATCC", "FCC", "AFCC"],
        help="Только одна категория",
    )
    args = parser.parse_args()

    print("MPLT — справочник ошибок для главы 1 (algo_basics)")
    print(f"Пара по умолчанию: {PAIR_LABEL}")
    print()
    print("Категории:")
    print("  ATCC — конструкции языка-примера в решении на целевом языке")
    print("  FCC  — ложная конструкция из справочника (лексема/паттерн)")
    print("  AFCC — тесты не пройдены, ATCC нет, упал контрастный тест слота")

    title_by_pattern = {row["pattern"]: row["title"] for row in CH1_SLOTS}
    for sample in SAMPLES:
        if args.category and sample["category"] != args.category:
            continue
        enriched = dict(sample)
        enriched.setdefault("title", title_by_pattern.get(sample["pattern"], ""))
        _print_sample(enriched, verify=args.verify)


if __name__ == "__main__":
    main()
