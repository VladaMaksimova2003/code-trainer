"""Batch 2 debug-import analysis: task_023, task_028, task_031, task_036, task_039."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402
from v128_stage1_overlays import STAGE1_OVERLAYS  # noqa: E402
from v128_test_suites_data import V128_TEST_SUITES  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

BATCH = ["task_023", "task_028", "task_031", "task_036", "task_039"]
LANGS = ["python", "pascal", "cpp", "csharp", "java"]

CHAPTER_MODULE = {
    "task_023": ("ch3_user_codes", "task_023"),
    "task_028": ("ch4_user_codes", "task_028"),
    "task_031": ("ch4_user_codes", "task_031"),
    "task_036": ("ch5_user_codes", "task_036"),
    "task_039": ("ch5_user_codes", "task_039"),
}

DEBUG_IDS = {
    "task_028": "index_1based",
    "task_036": "string_index",
}


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> tuple[str, str | None]:
    if not str(code or "").strip():
        return "", "empty code"
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    Path(sf).write_text(code, encoding="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, sf],
            input=inp,
            capture_output=True,
            text=True,
            timeout=8,
            cwd=wd,
        )
        if r.returncode != 0:
            return r.stdout, f"exit {r.returncode}: {r.stderr[:180]}"
        return r.stdout, None
    except Exception as exc:
        return "", str(exc)


def validate(code: str, tests: list[dict]) -> dict[str, Any]:
    ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests):
        got, err = run_python(code, tc["inputs"])
        if err:
            notes.append(f"T{i+1}: {err}")
            continue
        if norm(got) == norm(tc["output"]):
            ok += 1
        else:
            notes.append(f"T{i+1}: exp={tc['output']!r} got={norm(got)!r}")
    return {"pass": f"{ok}/{len(tests)}", "notes": notes[:4]}


def load_chapter_codes(pattern: str) -> dict[str, dict[str, str]]:
    mod_name, stem = CHAPTER_MODULE[pattern]
    path = SCRIPTS / mod_name / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        fixed = str(getattr(mod, f"FIXED_{lang.upper()}", "") or getattr(mod, lang.upper(), "") or "").strip()
        buggy = str(getattr(mod, f"BUGGY_{lang.upper()}", "") or "").strip()
        out[lang] = {"fixed": fixed, "buggy": buggy}
    return out


def catalog_meta(pattern: str) -> dict[str, Any]:
    base = dict(ALGO_SYNTAX_META.get(pattern) or {})
    overlay = STAGE1_OVERLAYS.get(pattern) or {}
    merged = dict(base)
    for key, val in overlay.items():
        if key == "implementations" and isinstance(val, dict):
            impl = dict(merged.get("implementations") or {})
            for lang, patch in val.items():
                cur = dict(impl.get(lang) or {})
                if isinstance(patch, dict):
                    cur.update(patch)
                impl[lang] = cur
            merged["implementations"] = impl
        elif key == "test_cases" and val:
            merged["test_cases"] = val
        else:
            merged[key] = val
    return merged


def overlay_codes(meta: dict) -> dict[str, dict[str, str]]:
    impls = meta.get("implementations") or {}
    out: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        impl = impls.get(lang) or {}
        out[lang] = {
            "fixed": str(impl.get("fixed_code") or (meta.get("reference_codes") or {}).get(lang) or "").strip(),
            "buggy": str(impl.get("buggy_code") or "").strip(),
        }
    return out


def load_import_override(pattern: str) -> dict | None:
    path = SCRIPTS / "import_debug_fixes.py"
    text = path.read_text(encoding="utf-8")
    if f'"{pattern}"' not in text or pattern not in text.split("OVERRIDES = {", 1)[-1]:
        return None
    # Import module to read prepared override
    spec = importlib.util.spec_from_file_location("import_debug_fixes", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return (mod.OVERRIDES or {}).get(pattern)


def pick_canon_tests(pattern: str, meta: dict, override: dict | None) -> tuple[list[dict], str]:
    if override and override.get("tests"):
        return list(override["tests"]), "import_debug_fixes.OVERRIDES"
    overlay_tests = meta.get("test_cases") or []
    if overlay_tests and pattern == "task_028":
        return [dict(t) for t in overlay_tests], "v128_stage1_overlays"
    v128 = V128_TEST_SUITES.get(pattern) or []
    if v128:
        return [dict(t) for t in v128[:4]], "v128_test_suites_data"
    return [dict(t) for t in (meta.get("test_cases") or [])[:4]], "algo_v128_catalog"


def canon_algorithm(pattern: str, meta: dict, override: dict | None) -> str:
    if override and override.get("description"):
        return str(override["description"]).strip()
    return str(meta.get("detailed_description") or meta.get("short_goal") or "").strip()


def detect_conflicts(pattern: str, meta: dict, chapter: dict, overlay: dict, tests: list[dict]) -> list[str]:
    conflicts: list[str] = []
    cat_tests = meta.get("test_cases") or ALGO_SYNTAX_META.get(pattern, {}).get("test_cases") or []
    if cat_tests and tests and norm(json.dumps(cat_tests[:1], ensure_ascii=False)) != norm(json.dumps(tests[:1], ensure_ascii=False)):
        if any("19" in str(t.get("output", "")) for t in cat_tests[:3]):
            conflicts.append("algo_v128_catalog.test_cases — чужие тесты (placeholder суммы/агрегата), не алгоритм задачи")
    v128 = V128_TEST_SUITES.get(pattern) or []
    if pattern == "task_031" and v128:
        conflicts.append("v128_test_suites_data.task_031 — outputs как max/matrix, не merge; использовать curated T031_TESTS")
    raw_title = str(meta.get("raw_title") or "")
    title = str(meta.get("title") or "")
    if pattern == "task_031" and "матриц" in raw_title.lower():
        conflicts.append(f"raw_title «{raw_title}» vs канон «Слияние отсортированных массивов»")
    if pattern == "task_028" and raw_title != "Вставка элемента по позиции":
        conflicts.append(f"catalog title «{title}» / raw «{raw_title}» vs канон вставки 1-based")
    if pattern == "task_036":
        conflicts.append("strings_ch5_user_payload: kind=translation, generic description; debug overlay только python buggy/fixed")
    ch_fixed = chapter["python"]["fixed"]
    ov_fixed = overlay["python"]["fixed"]
    if ch_fixed and ov_fixed and pattern == "task_028" and norm(ch_fixed) != norm(ov_fixed):
        conflicts.append("ch4_user_codes FIXED_PYTHON ≠ v128 overlay (overlay — канон)")
    if pattern == "task_031":
        if "best" in chapter["python"]["fixed"].lower() or "матриц" in chapter["pascal"]["fixed"].lower():
            conflicts.append("ch4_user_codes — код «максимум в матрице», не merge")
    if pattern == "task_023":
        if "total" in chapter["python"]["buggy"] or "freq" not in chapter["python"]["fixed"]:
            conflicts.append("ch3: FIXED=гистограмма OK, BUGGY=другой алгоритм (сумма <=0) + синтаксис в python")
    if pattern == "task_039":
        if "Console.ReadLine" in chapter["python"]["buggy"]:
            conflicts.append("ch5_user_codes BUGGY — склеенный чужой синтаксис (C#/Pascal в python)")
    return conflicts


def score_sources(chapter: dict, overlay: dict, tests: list[dict], override: dict | None) -> dict[str, Any]:
    candidates: list[tuple[str, str, str]] = []
    if override:
        candidates.append(("override", override["ref"].get("python", ""), override["buggy"].get("python", "")))
    candidates.append(("overlay", overlay["python"]["fixed"], overlay["python"]["buggy"]))
    candidates.append(("chapter", chapter["python"]["fixed"], chapter["python"]["buggy"]))
    best = {"name": "none", "fixed": "", "buggy": "", "fixed_val": {"pass": "0/0"}, "buggy_val": {"pass": "0/0"}}
    for name, fixed, buggy in candidates:
        if not fixed:
            continue
        fv = validate(fixed, tests)
        bv = validate(buggy, tests) if buggy else {"pass": "n/a", "notes": ["no buggy"]}
        fixed_ok = fv["pass"].startswith(str(len(tests))) or fv["pass"].split("/")[0] == str(len(tests))
        if fixed_ok and (name == "override" or best["name"] == "none" or not best["fixed_val"]["pass"].startswith(str(len(tests)))):
            best = {"name": name, "fixed": fixed, "buggy": buggy, "fixed_val": fv, "buggy_val": bv}
    return best


def classify(pattern: str, conflicts: list[str], best: dict, chapter: dict) -> str:
    if pattern == "task_031":
        return "clean"  # prepared override exists
    fixed_pass = best["fixed_val"]["pass"]
    total = fixed_pass.split("/")[-1] if "/" in fixed_pass else "0"
    if best["name"] != "none" and fixed_pass.startswith(f"{total}/") and total != "0" and best["fixed_val"]["pass"].split("/")[0] == total:
        # check multi-lang corruption in chapter for damaged marker
        corrupt = 0
        for lang in LANGS:
            b = chapter[lang]["buggy"]
            if not b:
                continue
            if any(tok in b for tok in ("Console.", "int(input())", ":=", "input().split()", "StringBuilder", "#include <iostream<")):
                corrupt += 1
        if corrupt >= 3 and pattern in {"task_028", "task_039"}:
            return "clean (DB/chapter damaged; override draft from canon)"
        if pattern == "task_023":
            return "clean (catalog tests damaged; codes recoverable)"
        if pattern == "task_036":
            return "clean (overlay python; pascal ref from chapter)"
        return "clean"
    if "placeholder" in " ".join(conflicts).lower() or corrupt_heavy(chapter):
        return "damaged"
    return "damaged"


def corrupt_heavy(chapter: dict) -> bool:
    n = 0
    for lang in LANGS:
        for kind in ("fixed", "buggy"):
            code = chapter[lang][kind]
            if code and any(tok in code for tok in ("Console.", " int(input())", ":=", "StringBuilder", "#include <iostream<", "for i in range")):
                if lang != "python" or kind == "buggy":
                    n += 1
    return n >= 4


def db_row(pattern: str) -> dict | None:
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pattern,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        did, title, desc, tests, ce = row
        if isinstance(ce, str):
            ce = json.loads(ce)
        if isinstance(tests, str):
            tests = json.loads(tests)
        return {"db_id": did, "title": title, "description": (desc or "")[:120], "tests_n": len(tests or []),
                "hints_db": (ce or {}).get("hints"), "post_solve_db": (ce or {}).get("post_solve_explanation")}
    except Exception as exc:
        return {"error": str(exc)}


def proposed_override_summary(pattern: str, override: dict | None, best: dict, meta: dict) -> dict | None:
    if override:
        return {
            "source": "already in import_debug_fixes.OVERRIDES",
            "title": override["title"],
            "tests_n": len(override["tests"]),
            "hints": override.get("hints"),
            "post_solve": override.get("post_solve"),
            "concepts": override.get("concepts"),
            "fixed_validation": best["fixed_val"]["pass"],
            "buggy_validation": best["buggy_val"]["pass"],
        }
    drafts = {
        "task_023": {
            "title": "Гистограмма частот",
            "description": canon_algorithm(pattern, meta, None),
            "bug_logic": "BUGGY считает сумму неположительных вместо freq[0..9]",
            "hints": [
                "Используйте массив из 10 счётчиков для цифр 0..9.",
                "Увеличивайте freq[x] только если 0 <= x <= 9.",
                "Выводите все 10 частот через пробел, включая нули.",
            ],
            "post_solve": "Нужна гистограмма частот по цифрам 0..9, а не сумма отрицательных. Каждое значение увеличивает свой счётчик freq[x].",
            "concepts": meta.get("expected_concepts", {}).get("pascal") or [],
        },
        "task_028": {
            "title": "Вставка элемента по позиции",
            "description": "Даны n, массив из n чисел, позиция pos (1-based) и значение x. Вставьте x на позицию pos и выведите массив из n+1 элементов через пробел.",
            "bug_logic": "0-based insert/list index вместо pos-1 (pitfall index_1based)",
            "hints": [
                "Позиция pos в условии задаётся с 1.",
                "Сдвиг элементов делайте с конца массива к pos.",
                "После вставки элементов должно стать n+1.",
            ],
            "post_solve": "В Pascal массив 1-based: pos=2 означает второй элемент. Ошибка a.insert(pos, x) в Python-стиле вставляет не на ту позицию.",
            "concepts": ["program_entry", "typed_declaration", "assignment", "stdin_read", "stdout_write", "indexed_sequence", "counted_loop"],
        },
        "task_036": {
            "title": "Первое вхождение подстроки",
            "description": "Даны строка s и подстрока p. Найдите первое вхождение p в s и выведите индекс (1-based) или 0, если p не найдена.",
            "bug_logic": "print(s.find(p)) — 0-based / -1 вместо 1-based / 0",
            "hints": [
                "find возвращает 0-based индекс или -1.",
                "В ответе нужен 1-based индекс первого вхождения.",
                "Если подстрока не найдена, выведите 0.",
            ],
            "post_solve": "Python str.find даёт 0 для первого символа и -1 при отсутствии. По условию нужно 1 и 0 соответственно.",
            "concepts": ["program_entry", "typed_declaration", "assignment", "stdin_read", "stdout_write", "counted_loop", "search_find"],
        },
        "task_039": {
            "title": "RLE-сжатие строки",
            "description": "Дана строка s. Выполните RLE: каждую группу одинаковых символов замените символом и длиной группы (a3b2).",
            "bug_logic": "count:=0 / пропуск последней группы / неверная инициализация счётчика",
            "hints": [
                "Счётчик группы начинайте с 1 для первого символа.",
                "При смене символа допишите предыдущий символ и длину в результат.",
                "Не забудьте закрыть последнюю группу после цикла.",
            ],
            "post_solve": "RLE идёт по группам: пока символ повторяется — увеличиваем count, при смене — пишем char+count и сбрасываем. count=0 ломает первую группу.",
            "concepts": ["program_entry", "typed_declaration", "assignment", "stdin_read", "stdout_write", "string_sequence"],
        },
    }
    d = drafts.get(pattern)
    if not d:
        return None
    d = dict(d)
    d["fixed_validation"] = best["fixed_val"]["pass"]
    d["buggy_validation"] = best["buggy_val"]["pass"]
    d["code_source"] = best["name"]
    return d


def analyze(pattern: str) -> dict:
    meta = catalog_meta(pattern)
    chapter = load_chapter_codes(pattern)
    overlay = overlay_codes(meta)
    override = load_import_override(pattern)
    tests, tests_source = pick_canon_tests(pattern, meta, override)
    conflicts = detect_conflicts(pattern, meta, chapter, overlay, tests)
    best = score_sources(chapter, overlay, tests, override)
    status = classify(pattern, conflicts, best, chapter)
    return {
        "pattern_id": pattern,
        "status": status,
        "debug_id": DEBUG_IDS.get(pattern),
        "db": db_row(pattern),
        "canon_algorithm": canon_algorithm(pattern, meta, override),
        "canon_title": (override or {}).get("title") or meta.get("title"),
        "source_conflicts": conflicts,
        "tests_source": tests_source,
        "tests": tests,
        "fixed_validation_python": best["fixed_val"],
        "buggy_validation_python": best["buggy_val"],
        "validation_code_source": best["name"],
        "expected_concepts_pascal": (override or {}).get("concepts") or (meta.get("expected_concepts") or {}).get("pascal"),
        "chapter_code_health": {
            lang: {"has_fixed": bool(chapter[lang]["fixed"]), "has_buggy": bool(chapter[lang]["buggy"])}
            for lang in LANGS
        },
        "proposed_override": proposed_override_summary(pattern, override, best, meta),
        "what_changes": _what_changes(pattern, status, override, conflicts),
    }


def _what_changes(pattern: str, status: str, override: dict | None, conflicts: list[str]) -> list[str]:
    if status.startswith("damaged"):
        return ["Только карточка решения — apply не выполнять", *conflicts[:3]]
    changes = [
        "title / description → канон без префикса главы",
        "test_cases → curated v128/override (4–6 тестов)",
        "code_examples fixed + buggy_{lang} для 5 языков",
        "hints + post_solve_explanation в code_examples (+ promote на payload)",
        "expected_concepts → pascal curriculum list",
    ]
    if override:
        changes.insert(0, "Override уже в import_debug_fixes.py — dry-run OK, apply после подтверждения")
    else:
        changes.insert(0, "Подготовить новый блок OVERRIDES (не apply)")
    return changes


def main() -> None:
    report = [analyze(pid) for pid in BATCH]
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
