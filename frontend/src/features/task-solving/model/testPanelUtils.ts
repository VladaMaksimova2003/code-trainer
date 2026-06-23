import type { ExecutionStatus, PanelError, TestCaseResult } from "@/shared/types/execution"
import type { TaskTestCase } from "@/shared/types/task"
import {
  formatTestInputCell,
  type TestInputDisplayContext,
} from "@/features/task-solving/model/testInputDisplay"

type StructuredIoValue = {
  type?: string
  value?: unknown
  raw?: string
  [key: string]: unknown
}

export interface TestPanelRow {
  case: number
  input: string
  expected: string
  actual: string
  status: ExecutionStatus
  message: string
  durationMs: number | null
}

export interface TestStats {
  total: number
  passed: number
  failed: number
  pending: number
}

export interface PartitionTestResults {
  testResults: TestCaseResult[]
  compilerErrors: PanelError[]
}

type PanelErrorWithMeta = PanelError & {
  source?: string
  tone?: string
  sourceLabel?: string
}

export function formatTestValue(value: unknown): string {
  if (value == null) return ""
  if (typeof value === "string") return value
  if (typeof value !== "object") return String(value)

  const structured = value as StructuredIoValue
  if (structured.type === "scalar") return String(structured.value ?? "")
  if (structured.type === "multi" && Array.isArray(structured.value)) {
    return structured.value.join("\n")
  }
  if (structured.type === "matrix" && Array.isArray(structured.value)) {
    return structured.value
      .map((row) => (Array.isArray(row) ? row.join(" ") : String(row)))
      .join("\n")
  }
  if (structured.type === "json") {
    return structured.raw ?? JSON.stringify(structured.value ?? {})
  }
  if ("value" in structured) return String(structured.value ?? "")
  return JSON.stringify(value)
}

/** Empty stdin/stdout in the test table — distinct from missing (—). */
export function formatTestIoCell(value: unknown): string {
  if (value === "") return "∅"
  const text = formatTestValue(value).trim()
  if (!text) return "—"
  return text
}

export function formatTestDuration(durationMs: unknown): string {
  const ms = Number(durationMs)
  if (!Number.isFinite(ms) || ms < 0) return "—"
  if (ms === 0) return "0 мс"
  if (ms < 1000) return `${Math.round(ms)} мс`
  return `${(ms / 1000).toFixed(2)} с`
}

/** Must match StdinLinesTestStrategy.stdin_wrapper_line_offset() in the backend. */
const STDIN_WRAPPER_LINE_OFFSET = 10

function isEmptyOutput(value: unknown): boolean {
  const text = String(value ?? "").trim()
  return !text || text === "—" || text === "-"
}

function shiftWrappedLineNumber(line: string | number, lineOffset = STDIN_WRAPPER_LINE_OFFSET): number {
  const parsed = Number(line)
  if (!Number.isFinite(parsed) || parsed <= lineOffset) return parsed
  return parsed - lineOffset
}

/** Remap only when stderr still has wrapped-file coordinates (line > offset). */
export function needsWrappedLineRemap(text: string, lineOffset = STDIN_WRAPPER_LINE_OFFSET): boolean {
  const raw = String(text || "")
  const fileLine = raw.match(/File\s+"[^"]+",\s+line\s+(\d+)/i)
  if (fileLine && Number(fileLine[1]) > lineOffset) return true
  const summaryLine = raw.match(/^Line\s+(\d+)/im)
  if (summaryLine && Number(summaryLine[1]) > lineOffset) return true
  const sourceLine = raw.match(/source\.[a-z]+:(\d+):/i)
  if (sourceLine && Number(sourceLine[1]) > lineOffset) return true
  return false
}

export function remapWrappedSourceLines(text: string, lineOffset = STDIN_WRAPPER_LINE_OFFSET): string {
  if (!text || lineOffset <= 0 || !needsWrappedLineRemap(text, lineOffset)) return text
  let result = String(text)
  result = result.replace(/(File\s+"[^"]+",\s+line\s+)(\d+)/gi, (_, prefix, line) => {
    const mapped = shiftWrappedLineNumber(line, lineOffset)
    return `${prefix}${mapped}`
  })
  result = result.replace(/^Line\s+(\d+)\b/gim, (_, line) => `Line ${shiftWrappedLineNumber(line, lineOffset)}`)
  result = result.replace(/(source\.[a-z]+:)(\d+)(:\d+)/gi, (_, prefix, line, suffix) => {
    const mapped = shiftWrappedLineNumber(line, lineOffset)
    return `${prefix}${mapped}${suffix}`
  })
  return result
}

function containsInternalCaseMarkers(value: unknown): boolean {
  return /__CT_CASE_\d+__/i.test(String(value ?? ""))
}

/** Validation/diagnostic text that must not appear in the «Тесты» table. */
export function isNonTestDiagnosticMessage(text: unknown): boolean {
  const line = String(text ?? "").trim()
  if (!line) return false
  if (/^(Отсутствует конструкция|В коде не найдена ожидаемая конструкция):/i.test(line)) {
    return true
  }
  if (/^Блоки расставлены в неверном порядке/i.test(line)) {
    return true
  }
  if (/^Не все блоки расставлены:/i.test(line)) {
    return true
  }
  return false
}

function sanitizeTestActual(
  actual: unknown,
  message: unknown,
  status: ExecutionStatus,
  expected = "",
): string {
  const rawActual = String(actual ?? "")
  let text = rawActual.trim()
  const msg = String(message ?? "").trim()
  const diagnosticBlob = normalizeDiagnosticPaths([text, msg].filter(Boolean).join("\n"))

  if (
    (status === "FAILED" || status === "ERROR") &&
    (isRuntimeErrorOutput(diagnosticBlob) || isCompileOrSyntaxOutput(diagnosticBlob))
  ) {
    return "—"
  }

  if ((status === "FAILED" || status === "ERROR") && !text && !msg) {
    return "—"
  }

  const hadMarkers = containsInternalCaseMarkers(text)
  if (hadMarkers) {
    text = text.replace(/__CT_CASE_\d+__/gi, " ").replace(/\s+/g, " ").trim()
  }
  if ((!text || hadMarkers) && msg) {
    if (isRuntimeErrorOutput(normalizeDiagnosticPaths(msg)) || isCompileOrSyntaxOutput(normalizeDiagnosticPaths(msg))) {
      return "—"
    }
    text = msg
  }
  if (isEmptyOutput(text) && (status === "FAILED" || status === "ERROR")) {
    if (hadMarkers) {
      text =
        msg ||
        "Программа завершилась с ошибкой. Проверьте типы данных (например, n = int(input()))."
    } else {
      const expectedText = String(expected ?? "").trim()
      text = msg || (expectedText ? `Нет вывода (ожидалось: ${expectedText})` : "(пустой вывод)")
    }
  }
  if (text) {
    text = humanizeExecutionMessage(text)
  }
  return text
}

export function buildTestRows(
  testCases: TaskTestCase[] | null | undefined = [],
  results: TestCaseResult[] | null | undefined = [],
  inputDisplay?: TestInputDisplayContext,
): TestPanelRow[] {
  const cases = Array.isArray(testCases) ? testCases : []
  const resultByCase = new Map(
    (Array.isArray(results) ? results : []).map((row) => [Number(row.case), row]),
  )

  return cases.map((testCase, index) => {
    const caseNum = index + 1
    const result = resultByCase.get(caseNum)
    const status = result?.status ?? "PENDING"
    const rawActual = result?.actual ?? ""
    const message = result?.message ?? ""
    const expected = formatTestValue(testCase.output ?? testCase.expected_output ?? testCase.expected)
    const actual = sanitizeTestActual(rawActual, message, status, expected)
    return {
      case: caseNum,
      input: formatTestInputCell(
        formatTestValue(testCase.inputs ?? testCase.input),
        inputDisplay,
      ),
      expected,
      actual,
      status,
      message: String(message),
      durationMs:
        result?.duration_ms ??
        result?.durationMs ??
        result?.execution_time_ms ??
        result?.time_ms ??
        null,
    }
  })
}

const IGNORABLE_REPORT_MESSAGES = [
  /^all checks passed!?$/i,
  /^found 0 errors?\.?$/i,
  /^no issues found\.?$/i,
]

export function isIgnorableReportMessage(text: unknown): boolean {
  const line = String(text || "").trim()
  if (!line) return true
  return IGNORABLE_REPORT_MESSAGES.some((pattern) => pattern.test(line))
}

export function filterReportErrors(errors: PanelError[] | null | undefined = []): PanelError[] {
  const list = errors || []
  return list.filter((err) => !isIgnorableReportMessage(err?.text))
}

const STANDARD_DIAGNOSTIC_RE =
  /^Line\s+(\d+)(?::(\d+))?\s*:\s*(?:error|warning|fatal error|fatal)\s*:\s*(.+)$/i

/** Parse unified backend lint format: Line N:Col: error: message */
export function parseStandardDiagnostic(text: unknown): {
  line: number
  column?: number
  message: string
} | null {
  const raw = String(text || "").trim()
  if (!raw) return null

  let match = raw.match(STANDARD_DIAGNOSTIC_RE)
  if (match) {
    return {
      line: Number(match[1]),
      column: match[2] ? Number(match[2]) : undefined,
      message: match[3].trim(),
    }
  }

  match = raw.match(/^Line\s+(\d+)(?::(\d+))?\s*:\s*(.+?)\s+\((error|warning|fatal)\)\s*$/i)
  if (match) {
    return {
      line: Number(match[1]),
      column: match[2] ? Number(match[2]) : undefined,
      message: match[3].trim(),
    }
  }

  match = raw.match(/^Line\s+(\d+)(?::(\d+))?\s*:\s*(.+)$/i)
  if (match) {
    return {
      line: Number(match[1]),
      column: match[2] ? Number(match[2]) : undefined,
      message: match[3].trim(),
    }
  }

  return null
}

function enrichDiagnosticError(error: PanelError): PanelError {
  if (error?.line != null) return error
  const parsed = parseStandardDiagnostic(error?.text)
  if (!parsed) return error
  return {
    ...error,
    line: parsed.line,
    column: parsed.column,
    text: parsed.message,
  }
}

function diagnosticDedupeKey(error: PanelErrorWithMeta): string {
  if (error?.line != null) {
    return `${error.source || ""}|${error.type || ""}|line:${error.line}`
  }
  return `${error?.type || ""}|${error?.source || ""}|${diagnosticPanelSignature(error.text)}`
}

const SOURCE_LABELS: Record<string, string> = {
  Compiler: "Компилятор",
  Lint: "Линтер",
  Structures: "Структуры",
  Transfer: "MPLT-подсказка",
  Algorithm: "Алгоритм",
  Runtime: "Выполнение",
  Компилятор: "Компилятор",
  Линтер: "Линтер",
  Структуры: "Структуры",
  Перенос: "MPLT-подсказка",
  "MPLT-подсказка": "MPLT-подсказка",
  Алгоритм: "Алгоритм",
  Выполнение: "Выполнение",
}

export function isTransferPitfallError(error: PanelError | null | undefined): boolean {
  return String(error?.type || "").toUpperCase() === "TRANSFER_PITFALL"
}

export function isAlgorithmFeedbackError(error: PanelError | null | undefined): boolean {
  return String(error?.type || "").toUpperCase() === "ALGORITHM"
}

export function isNonBlockingPatternWarning(error: PanelError | null | undefined): boolean {
  const type = String(error?.type || "").toUpperCase()
  return type === "CONSTRUCTION_WARNING" || type === "TRANSFER_PITFALL" || type === "ALGORITHM"
}

/** Reactive MPLT feedback rows returned by the submission pipeline. */
export function extractTransferFeedback(errors: PanelError[] | null | undefined = []): PanelError[] {
  return filterReportErrors(errors).filter(isTransferPitfallError)
}

/** AlgorithmDebug feedback rows (orthogonal to MPLT transfer pitfalls). */
export function extractAlgorithmFeedback(errors: PanelError[] | null | undefined = []): PanelError[] {
  return filterReportErrors(errors).filter(isAlgorithmFeedbackError)
}

export interface AlgorithmFeedbackSection {
  label?: string
  body: string
}

export interface AlgorithmFeedbackDisplay {
  title?: string
  sections: AlgorithmFeedbackSection[]
}

const ALGORITHM_SECTION_SPLIT_RE =
  /\s+(?=(?:Ошибка отладки:|Пример\s*\([^)]+\):|Ошибочный вариант:|Buggy:|Считаются(?:\s+[^:]{0,80})?:|Примеры в коде:))/i

const ALGORITHM_SECTION_LABEL_RE =
  /^(Ошибка отладки|Пример\s*\([^)]+\)|Ошибочный вариант|Buggy|Считаются(?:\s+[^:]+)?|Примеры в коде)\s*:\s*(.*)$/is

function localizeAlgorithmSectionLabel(label: string): string {
  const trimmed = label.trim()
  if (trimmed === "Buggy") return "Ошибочный вариант"
  return trimmed
}

function prettifyAlgorithmBody(body: string): string {
  return body
    .replace(/\s*\.\.\.\s*/g, "\n")
    .replace(/\s*->\s*/g, " → ")
    .trim()
}

function parseAlgorithmSection(chunk: string): AlgorithmFeedbackSection {
  const trimmed = chunk.trim()
  const match = trimmed.match(ALGORITHM_SECTION_LABEL_RE)
  if (match) {
    return {
      label: localizeAlgorithmSectionLabel(match[1]),
      body: prettifyAlgorithmBody(match[2]),
    }
  }
  return { body: prettifyAlgorithmBody(trimmed) }
}

/** Splits dense algorithm-debug strings into sections for the errors tab. */
export function formatAlgorithmFeedbackForDisplay(text: unknown): AlgorithmFeedbackDisplay {
  const raw = String(text ?? "").trim()
  if (!raw) return { sections: [] }

  const rest = raw
    .replace(/^Ошибка алгоритма\s*\([^)]*\):\s*/i, "")
    .replace(/^Ошибка алгоритма:\s*/i, "")
    .trim()

  const chunks = rest
    .split(ALGORITHM_SECTION_SPLIT_RE)
    .map((chunk) => chunk.trim())
    .filter(Boolean)

  if (chunks.length === 0) {
    return { sections: [{ body: prettifyAlgorithmBody(rest || raw) }] }
  }

  return {
    sections: chunks.map(parseAlgorithmSection),
  }
}

/** Mirrors backend flow_student_messages — hides answer spoilers in student UI. */
const FLOW_STUDENT_ERROR_MESSAGES: Record<string, string> = {
  FLOW_SEQUENCE_MISMATCH:
    "Проверьте общий порядок схемы: выполнение должно идти от начала к завершению без пропусков.",
  FLOW_TEXT_MISMATCH:
    "Некоторые блоки не соответствуют операциям в коде. Сравните текст блоков с программой слева.",
  FLOW_CONSTRUCTION_MISSING: "В коде есть конструкция, которую нужно отразить на схеме.",
  FLOW_LOOP_BACK_EDGE:
    "Для цикла нужна связь, которая возвращает выполнение к следующей итерации.",
}

export function formatFlowValidationError(error: PanelError): PanelError {
  const type = String(error?.type || "").toUpperCase()
  const safeText = FLOW_STUDENT_ERROR_MESSAGES[type]
  if (!safeText) return error
  return { ...error, text: safeText }
}

function isStandaloneDiagnosticLine(text: unknown): boolean {
  const line = String(text || "").trim()
  if (!line) return false
  if (/^Line\s+\d+/i.test(line)) return true
  if (/^(invalid-syntax|syntax-error|name-error|type-error|indentation-error):/i.test(line)) {
    return true
  }
  if (/^(error|fatal|warning),?\s*(строка\s+\d+)?:/i.test(line)) return true
  if (/^(error|warning|fatal error):/i.test(line)) return true
  return false
}

/** Strip ephemeral Docker temp dirs so identical errors dedupe across test cases. */
export function normalizeDiagnosticPaths(text: unknown): string {
  return String(text || "")
    .replace(/\/tmp\/home\/[a-z0-9]+\//gi, "")
    .replace(/\/tmp\/[^/\s"']+\//g, "")
}

function diagnosticPanelSignature(text: unknown): string {
  const normalized = normalizeDiagnosticPaths(text)
  return summarizeCompileOutput(normalized).replace(/\s+/g, " ").trim().toLowerCase()
}

function executionErrorSignature(text: unknown): string {
  const normalized = normalizeDiagnosticPaths(text)
  if (hasRuntimeTraceback(normalized)) {
    return runtimeErrorSignature(normalized)
  }
  return diagnosticPanelSignature(normalized)
}

/** Short student-facing compiler/linter text — strips FPC banners and toolchain noise. */
export function sanitizeDiagnosticPanelText(text: unknown): string {
  const raw = String(text || "").trim()
  if (!raw) return ""
  if (
    /Free Pascal Compiler|source\.\w+\(\d+|^Error:|^Fatal:|^Warning:|\/usr\/bin\/ppcx/i.test(raw)
  ) {
    return summarizeCompileOutput(raw)
  }
  return humanizeExecutionMessage(raw)
}

/** Склеивает фрагменты одного отчёта (ruff/gcc snippet), разбитые по строкам в API. */
function extractFirstTraceback(text: unknown): string {
  const raw = String(text || "").trim()
  if (!hasRuntimeTraceback(raw)) return raw
  const parts = raw.split(/(?=Traceback \(most recent call last\))/i)
  const first = parts.find((part) => /^Traceback/i.test(part.trim()))
  return (first || parts[0] || raw).trim()
}

function runtimeErrorSignature(text: unknown): string {
  return normalizeDiagnosticPaths(extractFirstTraceback(text)).replace(/\s+/g, " ").trim()
}

function dedupeErrors(errors: PanelErrorWithMeta[] = []): PanelErrorWithMeta[] {
  const seen = new Set<string>()
  const deduped: PanelErrorWithMeta[] = []

  for (const error of errors) {
    const isRuntime = error?.type === "RUNTIME" || error?.source === "Выполнение"
    const text = isRuntime
      ? extractFirstTraceback(error?.text)
      : sanitizeDiagnosticPanelText(error?.text)
    if (!text) continue

    const key = isRuntime
      ? `runtime:${runtimeErrorSignature(text)}`
      : diagnosticDedupeKey({ ...error, text })

    if (seen.has(key)) continue
    seen.add(key)
    deduped.push({
      ...error,
      text,
    })
  }

  return deduped
}

export function mergeSplitErrors(errors: PanelErrorWithMeta[] = []): PanelErrorWithMeta[] {
  const merged: PanelErrorWithMeta[] = []

  for (const error of errors) {
    const text = sanitizeDiagnosticPanelText(error?.text)
    if (!text) continue

    const last = merged[merged.length - 1]
    const isRuntime = error?.type === "RUNTIME" || error?.source === "Выполнение"
    const sameRuntimeSignature =
      isRuntime &&
      last &&
      (last.type === "RUNTIME" || last.source === "Выполнение") &&
      runtimeErrorSignature(last.text) === runtimeErrorSignature(text)

    if (sameRuntimeSignature) continue

    const isDiagnostic =
      error?.source === "Компилятор" ||
      error?.source === "Линтер" ||
      error?.type === "COMPILER" ||
      error?.type === "LINT" ||
      isStandaloneDiagnosticLine(text)

    if (isDiagnostic) {
      const signature = diagnosticPanelSignature(text)
      if (merged.some((row) => diagnosticPanelSignature(row.text) === signature)) {
        continue
      }
      merged.push({ ...error, text })
      continue
    }

    const sameGroup =
      last &&
      last.source === error.source &&
      (last.type || "") === (error.type || "") &&
      !isTransferPitfallError(error) &&
      !isStandaloneDiagnosticLine(text)

    if (sameGroup && last) {
      last.text = `${last.text}\n${text}`
      continue
    }

    merged.push({ ...error, text })
  }

  return merged
}

export function normalizePanelErrors(
  compilerErrors: PanelError[] = [],
  linterErrors: PanelError[] = [],
  patternErrors: PanelError[] = [],
): PanelErrorWithMeta[] {
  const rows = dedupeErrors(
    mergeSplitErrors([
      ...filterReportErrors(compilerErrors).map((err) =>
        enrichDiagnosticError({
          ...err,
          source: err?.type === "RUNTIME" || err?.source === "Выполнение" ? "Выполнение" : "Компилятор",
          tone: err?.type === "RUNTIME" ? "warning" : "danger",
        }),
      ),
      ...filterReportErrors(linterErrors).map((err) =>
        enrichDiagnosticError({
          ...err,
          source: "Линтер",
          tone: err?.type === "INTERNAL_ERROR" || err?.type === "TIMEOUT" ? "warning" : "warning",
        }),
      ),
      ...filterReportErrors(patternErrors).map((err) => {
        if (isTransferPitfallError(err)) {
          return {
            ...err,
            source: "MPLT-подсказка",
            tone: "warning",
          }
        }
        if (isAlgorithmFeedbackError(err)) {
          return {
            ...err,
            source: "Алгоритм",
            tone: "warning",
          }
        }
        return {
          ...formatFlowValidationError(err),
          source: "Структуры",
          tone:
            err?.type === "CONSTRUCTION_WARNING" || err?.type === "CONSTRUCTION"
              ? "warning"
              : "purple",
        }
      }),
    ]),
  )

  return rows.map((row) => {
    const enriched = enrichDiagnosticError(row)
    return {
      ...enriched,
      sourceLabel: SOURCE_LABELS[String(enriched.source ?? "")] || enriched.source,
      text: hasRuntimeTraceback(enriched.text)
        ? String(enriched.text)
        : sanitizeDiagnosticPanelText(enriched.text),
    }
  })
}

export function humanizeExecutionMessage(text: unknown): string {
  const raw = String(text || "").trim()
  if (!raw) return "Неизвестная ошибка"
  if (raw.includes("Docker is required for code execution")) {
    return "Для проверки кода нужен Docker и запущенный worker (docker compose: api, worker, lint_worker)."
  }
  if (raw.includes("Docker is not available")) {
    return "Docker недоступен в worker. Запустите Docker Desktop и контейнеры проекта."
  }
  if (raw.includes("Submission is still processing")) {
    return "Проверка ещё выполняется. Подождите несколько секунд и нажмите «Прогнать» снова."
  }
  if (
    raw.includes("Too many concurrent execution jobs") ||
    raw.includes("USER_CONCURRENT_LIMIT")
  ) {
    return "Слишком много зависших проверок. Запустите execution worker или подождите 1–2 минуты и нажмите «Прогнать» снова."
  }
  if (
    raw.includes("unsupported operand type(s) for %") &&
    (raw.includes("'str'") || raw.includes("str"))
  ) {
    return "input() возвращает строку. Для арифметики используйте: n = int(input())"
  }
  if (raw.includes("not all arguments converted during string formatting")) {
    return "input() возвращает строку. Для арифметики используйте: n = int(input())"
  }
  if (raw.includes("TypeError") && raw.includes("input") && raw.includes("%")) {
    return "input() возвращает строку. Для арифметики используйте: n = int(input())"
  }
  if (raw.includes("Lint queue unavailable") || raw.includes("Queue unavailable")) {
    return "Очередь проверки недоступна. Убедитесь, что Redis и worker запущены."
  }
  return raw
}

const COMPILE_OUTPUT_MARKERS = [
  /SyntaxError/i,
  /IndentationError/i,
  /NameError/i,
  /TypeError/i,
  /fatal error/i,
  /no match for 'operator/i,
  /invalid syntax/i,
  /compilation failed/i,
  /File ".*", line \d+/i,
  /\/tmp\/home\/source\.[a-z]+:\d+:\d+:/i,
  /source\.\w+\(\d+,\d+\)\s+(Error|Fatal|Warning):/i,
  /^(Error|Fatal|Warning),?\s*(строка\s+\d+)?:/im,
  /Free Pascal Compiler/i,
]

function hasRuntimeTraceback(text: unknown): boolean {
  return /Traceback \(most recent call last\)/i.test(String(text || ""))
}

export function isCompileOrSyntaxOutput(text: unknown): boolean {
  const value = String(text || "").trim()
  if (!value || hasRuntimeTraceback(value)) return false
  return COMPILE_OUTPUT_MARKERS.some((pattern) => pattern.test(value))
}

export function summarizeCompileOutput(text: unknown): string {
  const raw = normalizeDiagnosticPaths(String(text || "").trim())
  if (!raw) return "Ошибка компиляции"

  const singleLineFile = raw.match(
    /^File\s+"[^"]+",\s+line\s+(\d+)\s+(.+)$/i,
  )
  if (singleLineFile && !raw.includes("\n")) {
    const lineNo = singleLineFile[1]
    const codeHint = singleLineFile[2].trim()
    const nameError = raw.match(/NameError:\s*(.+)$/i)
    const indentError = raw.match(/IndentationError:\s*(.+)$/i)
    if (nameError) return `Строка ${lineNo}: ${nameError[1].trim()} (${codeHint})`
    if (indentError) return `Строка ${lineNo}: ${indentError[1].trim()}`
    if (/^[A-Za-z_][\w.]*(Error|Exception):/i.test(codeHint)) {
      return `Строка ${lineNo}: ${codeHint}`
    }
    return `Строка ${lineNo}: ${codeHint} — проверьте отступы и вложенность блоков`
  }

  const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)

  const parsedFpc = lines.find((line) =>
    /^(Error|Fatal|Warning),?\s*(строка\s+\d+)?:/i.test(line),
  )
  if (parsedFpc) return parsedFpc

  const inlineFpc = lines.find((line) => /source\.\w+\(\d+,\d+\)\s+(Error|Fatal|Warning):/i.test(line))
  if (inlineFpc) {
    const match = inlineFpc.match(/source\.\w+\((\d+),\d+\)\s+(Error|Fatal|Warning):\s*(.+)$/i)
    if (match) return `${match[2]}, строка ${match[1]}: ${match[3]}`
  }

  const bareFpc = lines.find((line) => /^(Error|Fatal|Warning):\s+.+/i.test(line))
  if (bareFpc) return bareFpc

  if (/^Line\s+\d+:/i.test(raw) && !/File\s+"[^"]+",\s+line\s+\d+/i.test(raw)) {
    return lines[0] || raw
  }

  const syntax = lines.find((line) => /^SyntaxError:/i.test(line))
  const fileLine = [...lines]
    .reverse()
    .find((line) => /File ".*", line \d+/i.test(line) || /source\.[a-z]+:\d+:\d+:/i.test(line))
  if (fileLine && syntax) {
    const match = fileLine.match(/line\s+(\d+)/i) || fileLine.match(/:(\d+):\d+:/)
    const message = syntax.replace(/^SyntaxError:\s*/i, "").trim()
    if (match) {
      return `Line ${match[1]}: ${message || "синтаксическая ошибка"}`
    }
  }
  const gcc = lines.find((line) => /:\d+:\d+:\s*(fatal error|error|warning):/i.test(line))
  if (gcc) {
    return gcc.replace(/^.*source\.[a-z]+:/i, "Line ").replace(/:(\d+):(\d+):/, ":$2: ")
  }

  const filtered = lines.filter(
    (line) =>
      !/^Free Pascal Compiler|^Copyright \(c\)|^Target OS:|^Compiling |^Linking |lines compiled|^Fatal: Compilation aborted|^Error: \/usr\/bin\/ppcx/i.test(
        line,
      ),
  )
  return filtered.slice(0, 2).join("\n") || "Ошибка компиляции"
}

const RUNTIME_OUTPUT_MARKERS = [
  /Traceback \(most recent call last\)/i,
  /^[A-Za-z_][\w.]*Error:/m,
  /^[A-Za-z_][\w.]*Exception:/m,
  /Segmentation fault/i,
  /runtime error/i,
  /Time limit exceeded/i,
  /division by zero/i,
  /undefined behavior/i,
  /std::exception/i,
  /terminate called/i,
  /panic:/i,
]

export function isRuntimeErrorOutput(text: unknown): boolean {
  const value = String(text || "").trim()
  if (!value) return false
  if (hasRuntimeTraceback(value)) return true
  if (isCompileOrSyntaxOutput(value)) return false
  return RUNTIME_OUTPUT_MARKERS.some((pattern) => pattern.test(value))
}

export function summarizeRuntimeOutput(text: unknown): string {
  const raw = extractFirstTraceback(text)
  if (!raw) return "Ошибка выполнения"

  const humanized = humanizeExecutionMessage(raw)
  if (humanized !== raw) return humanized

  const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  const tracebackIdx = lines.findIndex((line) => /^Traceback/i.test(line))
  if (tracebackIdx >= 0) {
    const errorLine = lines
      .slice(tracebackIdx + 1)
      .find((line) => /^[A-Za-z_][\w.]*(Error|Exception):/i.test(line))
    if (errorLine) return humanizeExecutionMessage(errorLine)
  }

  const direct = lines.find((line) => /^[A-Za-z_][\w.]*(Error|Exception):/i.test(line))
  if (direct) return humanizeExecutionMessage(direct)

  return humanizeExecutionMessage(lines.slice(0, 4).join("\n"))
}

function pushDiagnosticTestRow(
  row: TestCaseResult,
  testResults: TestCaseResult[],
): void {
  testResults.push({
    ...row,
    actual: "",
    message: "",
  })
}

export function partitionTestResults(results: TestCaseResult[] = []): PartitionTestResults {
  const testResults: TestCaseResult[] = []
  const compilerErrors: PanelError[] = []
  const seenRuntimeSignatures = new Set<string>()
  const seenCompileSignatures = new Set<string>()

  for (const row of results) {
    const blob = normalizeDiagnosticPaths(
      [row.actual, row.message].filter((part) => !isEmptyOutput(part)).join("\n"),
    )
    if (
      (row.status === "ERROR" || row.status === "FAILED") &&
      isNonTestDiagnosticMessage(blob)
    ) {
      continue
    }
    if ((row.status === "ERROR" || row.status === "FAILED") && isRuntimeErrorOutput(blob)) {
      const summary = summarizeRuntimeOutput(blob)
      const traceback = normalizeDiagnosticPaths(extractFirstTraceback(blob))
      const signature = executionErrorSignature(blob)
      if (!seenRuntimeSignatures.has(signature)) {
        seenRuntimeSignatures.add(signature)
        compilerErrors.push({
          type: "RUNTIME",
          source: "Выполнение",
          text: traceback || summary,
        })
      }
      pushDiagnosticTestRow(row, testResults)
      continue
    }

    if ((row.status === "ERROR" || row.status === "FAILED") && isCompileOrSyntaxOutput(blob)) {
      const compileSummary = summarizeCompileOutput(blob)
      const signature = executionErrorSignature(blob)
      if (!seenCompileSignatures.has(signature)) {
        seenCompileSignatures.add(signature)
        compilerErrors.push({
          type: "COMPILER",
          text: compileSummary,
        })
      }
      pushDiagnosticTestRow(row, testResults)
      continue
    }

    if (
      (row.status === "ERROR" || row.status === "FAILED") &&
      isEmptyOutput(row.actual) &&
      !isEmptyOutput(row.message) &&
      (isRuntimeErrorOutput(normalizeDiagnosticPaths(row.message)) ||
        isCompileOrSyntaxOutput(normalizeDiagnosticPaths(row.message)))
    ) {
      const signature = executionErrorSignature(row.message)
      const isRuntime = isRuntimeErrorOutput(normalizeDiagnosticPaths(row.message))
      const bucket = isRuntime ? seenRuntimeSignatures : seenCompileSignatures
      if (!bucket.has(signature)) {
        bucket.add(signature)
        compilerErrors.push({
          type: isRuntime ? "RUNTIME" : "COMPILER",
          source: isRuntime ? "Выполнение" : undefined,
          text: isRuntime
            ? normalizeDiagnosticPaths(extractFirstTraceback(row.message))
            : summarizeCompileOutput(row.message),
        })
      }
      pushDiagnosticTestRow(row, testResults)
      continue
    }

    if (
      (row.status === "ERROR" || row.status === "FAILED") &&
      isEmptyOutput(row.actual) &&
      !isEmptyOutput(row.message)
    ) {
      testResults.push({
        ...row,
        actual: row.message,
      })
      continue
    }

    testResults.push(row)
  }

  return { testResults, compilerErrors }
}

export function countTestStats(rows: TestPanelRow[] = []): TestStats {
  const total = rows.length
  const passed = rows.filter((row) => row.status === "PASSED").length
  const failed = rows.filter((row) => row.status === "FAILED" || row.status === "ERROR").length
  const pending = total - passed - failed
  return { total, passed, failed, pending }
}

interface FlowCheckDebugLike {
  detected_sequence?: string
  expected_sequence?: string
  [key: string]: unknown
}

interface FlowCheckResultLike {
  success?: boolean
  debug?: FlowCheckDebugLike | null
  execution_results?: TestCaseResult[]
}

/** Synthetic or backend test rows for flowchart structural check. */
export function buildFlowchartCheckTestResults(
  task: { test_cases?: TaskTestCase[] | null } | null | undefined,
  flowResult: FlowCheckResultLike | null | undefined,
  flowErrors: PanelError[] = [],
): TestCaseResult[] {
  const cases = Array.isArray(task?.test_cases) ? task.test_cases : []
  if (cases.length === 0) return []

  const backendResults = flowResult?.execution_results
  if (Array.isArray(backendResults) && backendResults.length > 0) {
    return backendResults.map((row, index) => ({
      ...row,
      case: row.case ?? index + 1,
    }))
  }

  const failed = flowErrors.length > 0 || flowResult?.success === false
  const debug = flowResult?.debug
  const failureText =
    flowErrors
      .map((err) => String(err?.text || "").trim())
      .filter(Boolean)
      .join(" · ") ||
    (debug?.detected_sequence && debug?.expected_sequence
      ? `Построено: ${debug.detected_sequence}. Ожидалось: ${debug.expected_sequence}.`
      : debug?.detected_sequence
        ? `Построено: ${debug.detected_sequence}`
        : "Схема не прошла проверку")

  return cases.map((testCase, index) => ({
    case: index + 1,
    status: failed ? "FAILED" : "PASSED",
    inputs: testCase.inputs ?? "",
    expected: testCase.output ?? "",
    actual: failed ? failureText : testCase.output ?? "",
    message: failed ? failureText : "Схема соответствует эталону",
  }))
}
