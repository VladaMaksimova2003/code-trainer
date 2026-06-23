#!/usr/bin/env python3
"""One-off patch: migrate remaining _translation_spec calls to known_language_variants."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "application" / "curriculum" / "pascal_curriculum_v2_catalog.py"

PATCHES: list[tuple[str, str]] = [
    (
        'slug="fn_function_invocation_tr_cpp",\n                title_suffix="Вызов функции: перевод с C++",\n                description="Переведите программу, где функция add вызывается из main.",\n                difficulty="easy",\n                technical_concept_id="function_invocation",\n                source_language="cpp",\n                source_code=(\n                    "#include <iostream>\\nusing namespace std;\\n"\n                    "int add(int a,int b){ return a+b; }\\n"\n                    "int main(){ int x,y; cin>>x>>y; cout<<add(x,y); return 0; }"\n                ),',
        'slug="fn_function_invocation_tr_cpp",\n                title_suffix="Вызов функции",\n                description="Перенесите программу с вызовом функции add на Pascal.",\n                difficulty="easy",\n                technical_concept_id="function_invocation",\n                known_language_variants=FN_INVOCATION,',
    ),
    (
        'slug="arr_indexed_sequence_tr_python_sum3",\n                title_suffix="Массив: перевод суммы трёх элементов",\n                description="Переведите Python-код: вводятся три числа, выводится их сумма.",\n                difficulty="easy",\n                technical_concept_id="indexed_sequence",\n                source_language="python",\n                source_code="a = [int(input()), int(input()), int(input())]\\nprint(a[0] + a[1] + a[2])",',
        'slug="arr_indexed_sequence_tr_python_sum3",\n                title_suffix="Массив array",\n                description="Перенесите программу: введите три числа и выведите их сумму.",\n                difficulty="easy",\n                technical_concept_id="indexed_sequence",\n                known_language_variants=ARR_SUM3,',
    ),
    (
        'slug="str_string_sequence_tr_python_len",\n                title_suffix="Строка: перевод подсчёта длины",\n                description="Переведите Python-код: читается строка и печатается её длина.",\n                difficulty="easy",\n                technical_concept_id="string_sequence",\n                source_language="python",\n                source_code="s = input().strip()\\nprint(len(s))",',
        'slug="str_string_sequence_tr_python_len",\n                title_suffix="Строка string",\n                description="Перенесите программу подсчёта длины строки на Pascal.",\n                difficulty="easy",\n                technical_concept_id="string_sequence",\n                known_language_variants=STR_LEN,',
    ),
    (
        'slug="rec_key_value_map_tr_python_pair_sum",\n                title_suffix="Запись: перевод пары полей",\n                description="Переведите Python-фрагмент с объектом из двух полей и суммой.",\n                difficulty="medium",\n                technical_concept_id="key_value_map",\n                source_language="python",\n                source_code=(\n                    "a = int(input())\\nb = int(input())\\nitem = {\'x\': a, \'y\': b}\\nprint(item[\'x\'] + item[\'y\'])"\n                ),',
        'slug="rec_key_value_map_tr_python_pair_sum",\n                title_suffix="Запись record",\n                description="Перенесите программу с парой полей и суммой на Pascal.",\n                difficulty="medium",\n                technical_concept_id="key_value_map",\n                known_language_variants=REC_PAIR,',
    ),
    (
        'slug="mod_import_dependency_tr_python",\n                title_suffix="Модули: перевод import/uses",\n                description="Переведите фрагмент с идеей импортируемой функции (в рамках одной программы).",\n                difficulty="medium",\n                technical_concept_id="import_dependency",\n                source_language="python",\n                source_code="a = int(input())\\nb = int(input())\\nprint(a + b)",',
        'slug="mod_import_dependency_tr_python",\n                title_suffix="Модули uses",\n                description="Перенесите идею локальной функции и её вызова на Pascal.",\n                difficulty="medium",\n                technical_concept_id="import_dependency",\n                known_language_variants=MOD_IMPORT,',
    ),
    (
        'slug="recu_recursion_tr_python_fact",\n                title_suffix="Рекурсия: перевод factorial",\n                description="Переведите рекурсивный Python-код факториала на Pascal.",\n                difficulty="medium",\n                technical_concept_id="recursion",\n                source_language="python",\n                source_code=(\n                    "def fact(n):\\n    if n <= 1:\\n        return 1\\n    return n * fact(n - 1)\\n"\n                    "n = int(input())\\nprint(fact(n))"\n                ),',
        'slug="recu_recursion_tr_python_fact",\n                title_suffix="Рекурсия",\n                description="Перенесите рекурсивный factorial на Pascal.",\n                difficulty="medium",\n                technical_concept_id="recursion",\n                known_language_variants=RECU_FACT,',
    ),
    (
        'slug="alg_fold_aggregate_tr_cpp_sum_abs",\n                title_suffix="Агрегация: перевод суммы модулей",\n                description="Переведите C++-фрагмент: сумма модулей двух чисел.",\n                difficulty="medium",\n                technical_concept_id="fold_aggregate",\n                source_language="cpp",\n                source_code=(\n                    "#include <iostream>\\n#include <cstdlib>\\nusing namespace std;\\n"\n                    "int main(){ int a,b; cin>>a>>b; cout<<(abs(a)+abs(b)); return 0; }"\n                ),',
        'slug="alg_fold_aggregate_tr_cpp_sum_abs",\n                title_suffix="Агрегация fold",\n                description="Перенесите сумму модулей двух чисел на Pascal.",\n                difficulty="medium",\n                technical_concept_id="fold_aggregate",\n                known_language_variants=ALG_SUM_ABS,',
    ),
    (
        'slug="ds_linked_node_tr_python_pair",\n                title_suffix="Связный узел: перевод идеи node",\n                description="Переведите Python-фрагмент: хранение пары значений и вывод следующего.",\n                difficulty="medium",\n                technical_concept_id="linked_node",\n                source_language="python",\n                source_code="first = int(input())\\nsecond = int(input())\\nprint(second)",',
        'slug="ds_linked_node_tr_python_pair",\n                title_suffix="Связный узел",\n                description="Перенесите идею узла с двумя значениями на Pascal.",\n                difficulty="medium",\n                technical_concept_id="linked_node",\n                known_language_variants=DS_NODE,',
    ),
    (
        'slug="ds_tree_hierarchy_tr_cpp_parent_child",\n                title_suffix="Дерево: перевод parent-child проверки",\n                description="Переведите C++: прочитайте parent и child, выведите parent.",\n                difficulty="medium",\n                technical_concept_id="tree_hierarchy",\n                source_language="cpp",\n                source_code=(\n                    "#include <iostream>\\nusing namespace std;\\n"\n                    "int main(){ int p,c; cin>>p>>c; cout<<p; return 0; }"\n                ),',
        'slug="ds_tree_hierarchy_tr_cpp_parent_child",\n                title_suffix="Дерево tree",\n                description="Перенесите parent-child логику на Pascal.",\n                difficulty="medium",\n                technical_concept_id="tree_hierarchy",\n                known_language_variants=DS_TREE,',
    ),
    (
        'slug="oop_class_type_tr_python_point_sum",\n                title_suffix="Класс: перевод идеи объекта Point",\n                description="Переведите Python-фрагмент с объектом, содержащим два поля x и y.",\n                difficulty="medium",\n                technical_concept_id="class_type",\n                source_language="python",\n                source_code="x = int(input())\\ny = int(input())\\nprint(x + y)",',
        'slug="oop_class_type_tr_python_point_sum",\n                title_suffix="Класс class",\n                description="Перенесите объект с полями x, y и суммой на Pascal.",\n                difficulty="medium",\n                technical_concept_id="class_type",\n                known_language_variants=OOP_POINT,',
    ),
]


def main() -> int:
    text = CATALOG.read_text(encoding="utf-8")
    for old, new in PATCHES:
        if old not in text:
            print(f"MISSING: {old[:60]}...")
            return 1
        text = text.replace(old, new, 1)
    if "source_language=" in text:
        print("WARNING: source_language still present in catalog")
    CATALOG.write_text(text, encoding="utf-8")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
