import type { PanelError, TestCaseResult } from "@/shared/types/execution"

interface BuildTaskIssueContextInput {
  taskId: number | string
  language?: string | null
  activeSubmissionId?: number | string | null
  results?: TestCaseResult[]
  compilerErrors?: PanelError[]
  linterErrors?: PanelError[]
  patternErrors?: PanelError[]
  testStats?: { passed?: number; failed?: number; total?: number } | null
}

/** Compact diagnostic snapshot for a task-page support ticket. */
export function buildTaskIssueContext({
  taskId,
  language = null,
  activeSubmissionId = null,
  results = [],
  compilerErrors = [],
  linterErrors = [],
  patternErrors = [],
  testStats = null,
}: BuildTaskIssueContextInput): Record<string, unknown> {
  const failedTests = (Array.isArray(results) ? results : [])
    .filter((row: unknown) => row?.status === "FAILED" || row?.status === "ERROR")
    .slice(0, 5)
    .map((row: unknown) => ({
      case: row.case,
      status: row.status,
      message: row.message || null,
      actual: row.actual ? String(row.actual).slice(0, 200) : null,
    }))

  const pickErrors = (items: PanelError[] | unknown[]) =>
    (Array.isArray(items) ? items : [])
      .slice(0, 3)
      .map((err: unknown) => {
        const row = err as PanelError | string
        const text =
          typeof row === "string"
            ? row
            : String((row as PanelError)?.text ?? (row as { message?: string })?.message ?? row ?? "")
        return {
          line: typeof row === "object" && row != null ? (row as PanelError).line ?? null : null,
          text: text.slice(0, 300),
        }
      })
      .filter((err: unknown) => err.text)

  const context: Record<string, unknown> = {
    page_url: `/tasks/${taskId}`,
  }

  if (language) context.language = language
  if (activeSubmissionId) context.submission_id = activeSubmissionId
  if (testStats) {
    context.tests = {
      passed: testStats.passed ?? 0,
      failed: testStats.failed ?? 0,
      total: testStats.total ?? 0,
    }
  }
  if (failedTests.length) context.failed_tests = failedTests

  const errors = {
    compiler: pickErrors(compilerErrors),
    linter: pickErrors(linterErrors),
    pattern: pickErrors(patternErrors),
  }
  if (errors.compiler.length || errors.linter.length || errors.pattern.length) {
    context.errors = errors
  }

  return context
}
