import { describe, expect, it } from "vitest"
import type { PanelError, TestCaseResult } from "@/shared/types/execution"
import type { TaskTestCase } from "@/shared/types/task"
import {
  buildTestRows,
  countTestStats,
  extractTransferFeedback,
  extractAlgorithmFeedback,
  formatAlgorithmFeedbackForDisplay,
  filterReportErrors,
  formatFlowValidationError,
  formatTestIoCell,
  humanizeExecutionMessage,
  isCompileOrSyntaxOutput,
  isIgnorableReportMessage,
  isNonTestDiagnosticMessage,
  isRuntimeErrorOutput,
  normalizePanelErrors,
  parseStandardDiagnostic,
  partitionTestResults,
  summarizeCompileOutput,
  summarizeRuntimeOutput,
} from "@/features/task-solving/model/testPanelUtils"

describe("partitionTestResults", () => {
  it("splits runtime traceback into compilerErrors and summarized test row", () => {
    const traceback = [
      "Traceback (most recent call last):",
      '  File "source.py", line 3, in <module>',
      "    print(1 / 0)",
      "ZeroDivisionError: division by zero",
    ].join("\n")

    const results: TestCaseResult[] = [
      { case: 1, status: "ERROR", actual: traceback, message: "" },
    ]

    const { testResults, compilerErrors } = partitionTestResults(results)

    expect(compilerErrors).toHaveLength(1)
    expect(compilerErrors[0]).toMatchObject({
      type: "RUNTIME",
      source: "Выполнение",
    })
    expect(compilerErrors[0]?.text).toContain("Traceback")
    expect(testResults[0]?.actual).toBe("")
  })

  it("splits syntax output into COMPILER error and empty test actual", () => {
    const syntaxBlob = 'File "source.py", line 2\nSyntaxError: invalid syntax'

    const results: TestCaseResult[] = [
      { case: 1, status: "FAILED", actual: syntaxBlob, message: "" },
    ]

    const { testResults, compilerErrors } = partitionTestResults(results)

    expect(compilerErrors).toHaveLength(1)
    expect(compilerErrors[0]).toMatchObject({ type: "COMPILER" })
    expect(compilerErrors[0]?.text).toMatch(/Line 2|SyntaxError/i)
    expect(testResults[0]).toMatchObject({
      actual: "",
      message: "",
    })
  })

  it("dedupes identical runtime errors across multiple test cases", () => {
    const blob =
      'File "/tmp/home/abc123/source.py", line 6 best = ping'
    const results: TestCaseResult[] = [1, 2, 3].map((caseNum) => ({
      case: caseNum,
      status: "ERROR" as const,
      actual: blob.replace("abc123", `hash${caseNum}`),
      message: blob.replace("abc123", `hash${caseNum}`),
    }))

    const { testResults, compilerErrors } = partitionTestResults(results)

    expect(compilerErrors).toHaveLength(1)
    expect(testResults).toHaveLength(3)
    expect(testResults.every((row) => row.actual === "")).toBe(true)
  })

  it("copies message into actual when actual is empty on failed row", () => {
    const results: TestCaseResult[] = [
      { case: 1, status: "FAILED", actual: "", message: "Wrong answer" },
    ]

    const { testResults, compilerErrors } = partitionTestResults(results)

    expect(compilerErrors).toHaveLength(0)
    expect(testResults[0]?.actual).toBe("Wrong answer")
  })

  it("passes through ordinary passed rows unchanged", () => {
    const row: TestCaseResult = { case: 1, status: "PASSED", actual: "42", message: "" }
    const { testResults, compilerErrors } = partitionTestResults([row])

    expect(compilerErrors).toHaveLength(0)
    expect(testResults).toEqual([row])
  })

  it("drops construction diagnostics from test rows", () => {
    const results: TestCaseResult[] = [
      {
        case: 1,
        status: "FAILED",
        actual: "Отсутствует конструкция: Точка входа программы",
        message: "",
      },
    ]

    const { testResults, compilerErrors } = partitionTestResults(results)

    expect(compilerErrors).toHaveLength(0)
    expect(testResults).toHaveLength(0)
  })
})

describe("countTestStats", () => {
  it("counts passed, failed, error, and pending rows", () => {
    const rows = buildTestRows(
      [{ input: "1", output: "2" }, { input: "3", output: "4" }, { input: "5", output: "6" }],
      [
        { case: 1, status: "PASSED", actual: "2" },
        { case: 2, status: "FAILED", actual: "0" },
        { case: 3, status: "ERROR", actual: "boom" },
      ],
    )

    expect(countTestStats(rows)).toEqual({
      total: 3,
      passed: 1,
      failed: 2,
      pending: 0,
    })
  })

  it("treats missing results as pending", () => {
    const rows = buildTestRows([{ input: "1", output: "2" }], [])
    expect(countTestStats(rows)).toEqual({
      total: 1,
      passed: 0,
      failed: 0,
      pending: 1,
    })
  })
})

describe("compile error formatting", () => {
  it("detects syntax/compiler output", () => {
    expect(isCompileOrSyntaxOutput('File "x.py", line 1\nSyntaxError: EOL')).toBe(true)
    expect(isCompileOrSyntaxOutput("Traceback (most recent call last):")).toBe(false)
  })

  it("summarizes SyntaxError with line number", () => {
    const raw = [
      'File "source.py", line 4',
      "    x =",
      "SyntaxError: invalid syntax",
    ].join("\n")

    expect(summarizeCompileOutput(raw)).toBe("Line 4: invalid syntax")
  })

  it("summarizes single-line python file reference with code hint", () => {
    const raw = 'File "/tmp/home/deadbeef/source.py", line 6 best = ping'
    expect(summarizeCompileOutput(raw)).toBe(
      "Строка 6: best = ping — проверьте отступы и вложенность блоков",
    )
  })

  it("normalizePanelErrors maps compiler rows to Компилятор source", () => {
    const compilerErrors: PanelError[] = [
      { type: "COMPILER", text: "Line 2: expected ':'" },
    ]

    const rows = normalizePanelErrors(compilerErrors, [], [])
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({
      source: "Компилятор",
      sourceLabel: "Компилятор",
      tone: "danger",
    })
  })
})

describe("flow / structure validation error formatting", () => {
  it("normalizePanelErrors maps construction warnings to Структуры with warning tone", () => {
    const patternErrors: PanelError[] = [
      {
        type: "CONSTRUCTION_WARNING",
        text: "В коде не найдена ожидаемая конструкция: Ввод с клавиатуры",
      },
    ]

    const rows = normalizePanelErrors([], [], patternErrors)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({
      source: "Структуры",
      sourceLabel: "Структуры",
      tone: "warning",
    })
  })

  it("normalizePanelErrors maps transfer pitfalls to MPLT hint with feedback_ru", () => {
    const patternErrors: PanelError[] = [
      {
        type: "TRANSFER_PITFALL",
        text: "Возможный перенос (FCC): div",
        feedback_ru: "Ложный перенос (FCC): оператор / в Pascal даёт вещественный результат.",
        pitfall_id: "integer_division",
      },
    ]

    const rows = normalizePanelErrors([], [], patternErrors)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({
      source: "MPLT-подсказка",
      sourceLabel: "MPLT-подсказка",
      tone: "warning",
    })
    expect(extractTransferFeedback(patternErrors)).toHaveLength(1)
  })

  it("normalizePanelErrors keeps multiple transfer pitfalls as separate hints", () => {
    const patternErrors: PanelError[] = [
      {
        type: "TRANSFER_PITFALL",
        text: "Подсказка про деление",
        pitfall_id: "integer_division",
      },
      {
        type: "TRANSFER_PITFALL",
        text: "Подсказка про цикл",
        pitfall_id: "for_range_off_by_one",
      },
    ]

    const rows = normalizePanelErrors([], [], patternErrors)
    expect(rows).toHaveLength(2)
    expect(rows.map((row) => row.text)).toEqual([
      "Подсказка про деление",
      "Подсказка про цикл",
    ])
    expect(rows.every((row) => row.sourceLabel === "MPLT-подсказка")).toBe(true)
  })

  it("normalizePanelErrors maps algorithm feedback to Алгоритм", () => {
    const patternErrors: PanelError[] = [
      {
        type: "ALGORITHM",
        text: "Ошибка алгоритма (matches_buggy): условие отбора",
        debug_id: "filter_positive",
      },
    ]

    const rows = normalizePanelErrors([], [], patternErrors)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({
      source: "Алгоритм",
      sourceLabel: "Алгоритм",
      tone: "warning",
    })
    expect(extractAlgorithmFeedback(patternErrors)).toHaveLength(1)
  })

  it("formatAlgorithmFeedbackForDisplay splits dense algorithm text into sections", () => {
    const text =
      "Ошибка алгоритма (lex): Ошибка отладки: счётчик нужно начинать с 0, а не с 1. Пример (Pascal): count := 0; ... if amount > 0 then count := count + 1. Ошибочный вариант: count := 1 — даёт лишнюю единицу. Считаются только строго положительные: amount > 0 (не >= 0). Примеры в коде: count = 1 -> нужно count = 0."

    const display = formatAlgorithmFeedbackForDisplay(text)
    expect(display.title).toBeUndefined()
    expect(display.sections).toHaveLength(5)
    expect(display.sections[0]).toMatchObject({
      label: "Ошибка отладки",
      body: "счётчик нужно начинать с 0, а не с 1.",
    })
    expect(display.sections[1]?.label).toBe("Пример (Pascal)")
    expect(display.sections[1]?.body).toContain("count := 0;")
    expect(display.sections[2]?.label).toBe("Ошибочный вариант")
    expect(display.sections[4]?.body).toContain("count = 1 → нужно count = 0.")
  })

  it("formatAlgorithmFeedbackForDisplay strips legacy algorithm prefix", () => {
    const display = formatAlgorithmFeedbackForDisplay(
      "Ошибка алгоритма (matches_buggy): Ошибка отладки: условие отбора",
    )
    expect(display.title).toBeUndefined()
    expect(display.sections[0]).toMatchObject({
      label: "Ошибка отладки",
      body: "условие отбора",
    })
  })

  it("normalizePanelErrors maps flow pattern_errors to Структуры with purple tone", () => {
    const patternErrors: PanelError[] = [
      { type: "FLOW_SEQUENCE", text: "Ожидалась последовательность: start → input → end" },
    ]

    const rows = normalizePanelErrors([], [], patternErrors)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({
      source: "Структуры",
      sourceLabel: "Структуры",
      tone: "purple",
    })
  })

  it("formatFlowValidationError replaces spoiler backend messages with student-safe text", () => {
    const spoiler = {
      type: "FLOW_SEQUENCE_MISMATCH",
      text: "Структура схемы не совпадает с ожидаемой: Начало → Ввод → Условие → Конец.",
    }

    expect(formatFlowValidationError(spoiler).text).toBe(
      "Проверьте общий порядок схемы: выполнение должно идти от начала к завершению без пропусков.",
    )
  })

  it("normalizePanelErrors sanitizes known FLOW_* spoiler texts", () => {
    const patternErrors: PanelError[] = [
      {
        type: "FLOW_TEXT_MISMATCH",
        text: 'Не найден блок «Вывод» с ожидаемым текстом.',
      },
      {
        type: "FLOW_CONSTRUCTION_MISSING",
        text: "В схеме не хватает: ветвление (блок «Условие»).",
      },
    ]

    const rows = normalizePanelErrors([], [], patternErrors)
    expect(rows[0]?.text).toBe(
      "Некоторые блоки не соответствуют операциям в коде. Сравните текст блоков с программой слева.",
    )
    expect(rows[1]?.text).toBe("В коде есть конструкция, которую нужно отразить на схеме.")
  })
})

describe("student-safe vs ignorable report filtering", () => {
  it("isIgnorableReportMessage hides empty and success-only lines", () => {
    expect(isIgnorableReportMessage("")).toBe(true)
    expect(isIgnorableReportMessage("All checks passed!")).toBe(true)
    expect(isIgnorableReportMessage("Found 0 errors.")).toBe(true)
    expect(isIgnorableReportMessage("No issues found.")).toBe(true)
  })

  it("filterReportErrors keeps real diagnostics", () => {
    const errors: PanelError[] = [
      { type: "LINT", text: "All checks passed!" },
      { type: "LINT", text: "Line 3: unused variable 'x'" },
    ]

    const filtered = filterReportErrors(errors)
    expect(filtered).toHaveLength(1)
    expect(filtered[0]?.text).toBe("Line 3: unused variable 'x'")
  })

  it("normalizePanelErrors maps linter rows and splits line/message", () => {
    const linterErrors: PanelError[] = [
      { type: "LINT", text: "found 0 errors." },
      { type: "LINT", text: "Line 3:7: error: Expected a statement" },
      { type: "LINT", text: "Line 3:12: error: Simple statements must be separated by newlines or semicolons" },
    ]

    const rows = normalizePanelErrors([], linterErrors, [])
    expect(rows).toHaveLength(1)
    expect(rows[0]?.line).toBe(3)
    expect(rows[0]?.column).toBe(7)
    expect(rows[0]?.text).toBe("Expected a statement")
    expect(rows[0]?.sourceLabel).toBe("Линтер")
  })

  it("parseStandardDiagnostic reads unified lint format", () => {
    expect(parseStandardDiagnostic("Line 4:17: error: 'input' was not declared in this scope")).toEqual({
      line: 4,
      column: 17,
      message: "'input' was not declared in this scope",
    })
  })

  it("normalizePanelErrors drops ignorable linter noise", () => {
    const linterErrors: PanelError[] = [
      { type: "LINT", text: "found 0 errors." },
      { type: "LINT", text: "Line 1: missing docstring" },
    ]

    const rows = normalizePanelErrors([], linterErrors, [])
    expect(rows).toHaveLength(1)
    expect(rows[0]?.line).toBe(1)
    expect(rows[0]?.text).toBe("missing docstring")
  })

  it("normalizePanelErrors dedupes verbose FPC compiler blobs", () => {
    const fpcBlob = `Free Pascal Compiler version 3.2.2
Copyright (c) 1993-2021
source.pas(3,1) Error: Illegal expression
source.pas(4,3) Fatal: Syntax error, ";" expected but "identifier N" found
Fatal: Compilation aborted
Error: /usr/bin/ppcx64 returned an error exitcode`

    const compilerErrors: PanelError[] = [
      { type: "COMPILER", text: fpcBlob },
      { type: "COMPILER", text: fpcBlob },
      { type: "COMPILER", text: "Error, строка 3: Illegal expression" },
    ]

    const rows = normalizePanelErrors(compilerErrors, [], [])
    expect(rows.length).toBeLessThanOrEqual(2)
    expect(rows.every((row) => !row.text.includes("Free Pascal Compiler"))).toBe(true)
    expect(rows.every((row) => !row.text.includes("ppcx64"))).toBe(true)
  })
})

describe("isNonTestDiagnosticMessage", () => {
  it("recognizes construction and block-order messages", () => {
    expect(isNonTestDiagnosticMessage("Отсутствует конструкция: Точка входа программы")).toBe(true)
    expect(
      isNonTestDiagnosticMessage("В коде не найдена ожидаемая конструкция: Ввод с клавиатуры"),
    ).toBe(true)
    expect(isNonTestDiagnosticMessage("Блоки расставлены в неверном порядке — тесты не запускались.")).toBe(
      true,
    )
    expect(isNonTestDiagnosticMessage("9")).toBe(false)
  })
})

describe("humanizeExecutionMessage — Russian texts without regression", () => {
  it("returns default for empty input", () => {
    expect(humanizeExecutionMessage("")).toBe("Неизвестная ошибка")
    expect(humanizeExecutionMessage("   ")).toBe("Неизвестная ошибка")
  })

  it("humanizes Docker/worker messages to Russian", () => {
    expect(humanizeExecutionMessage("Docker is required for code execution")).toBe(
      "Для проверки кода нужен Docker и запущенный worker (docker compose: api, worker, lint_worker).",
    )
    expect(humanizeExecutionMessage("Docker is not available")).toBe(
      "Docker недоступен в worker. Запустите Docker Desktop и контейнеры проекта.",
    )
  })

  it("humanizes input() type errors to Russian hint", () => {
    const blob =
      "unsupported operand type(s) for %: 'str' and 'int'"
    expect(humanizeExecutionMessage(blob)).toBe(
      "input() возвращает строку. Для арифметики используйте: n = int(input())",
    )
  })

  it("preserves unknown diagnostic text as-is", () => {
    const raw = "ValueError: invalid literal for int() with base 10: 'abc'"
    expect(humanizeExecutionMessage(raw)).toBe(raw)
  })

  it("summarizeRuntimeOutput applies humanization for known patterns", () => {
    const raw =
      "unsupported operand type(s) for %: 'str' and 'int'"
    expect(summarizeRuntimeOutput(raw)).toBe(
      "input() возвращает строку. Для арифметики используйте: n = int(input())",
    )
  })
})

describe("buildTestRows", () => {
  it("hides runtime diagnostics from the received column", () => {
    const testCases: TaskTestCase[] = [{ inputs: "1", output: "2" }]
    const results: TestCaseResult[] = [
      {
        case: 1,
        status: "ERROR",
        actual: 'File "/tmp/home/abc/source.py", line 6 best = ping',
        message: 'File "/tmp/home/abc/source.py", line 6 best = ping',
      },
    ]

    const rows = buildTestRows(testCases, partitionTestResults(results).testResults)
    expect(rows[0]?.actual).toBe("—")
  })

  it("formats structured test case I/O and internal marker sanitization", () => {
    const testCases: TaskTestCase[] = [
      { inputs: { type: "scalar", value: "5" }, output: { type: "scalar", value: "10" } },
    ]
    const results: TestCaseResult[] = [
      {
        case: 1,
        status: "FAILED",
        actual: "__CT_CASE_1__",
        message: "expected 10",
        duration_ms: 42,
      },
    ]

    const rows = buildTestRows(testCases, results)
    expect(rows[0]).toMatchObject({
      case: 1,
      input: "5",
      expected: "10",
      status: "FAILED",
      durationMs: 42,
    })
    expect(rows[0]?.actual).toContain("expected 10")
  })
})

describe("runtime vs compile classification", () => {
  it("isRuntimeErrorOutput detects traceback and excludes compile-only blobs", () => {
    expect(isRuntimeErrorOutput("Traceback (most recent call last):\nNameError: x")).toBe(true)
    expect(isRuntimeErrorOutput("SyntaxError: invalid syntax")).toBe(false)
  })
})

describe("formatTestIoCell", () => {
  it("preserves multiline stdin for display", () => {
    expect(formatTestIoCell("5 12\n8\n3\n12\n5\n9\n")).toBe("5 12\n8\n3\n12\n5\n9")
  })
})
