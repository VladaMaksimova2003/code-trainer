/**
 * Submission, test, and panel error types from /submissions and execution polling.
 * Types only — no runtime exports.
 */

export type ExecutionStatus =
  | "PENDING"
  | "PASSED"
  | "FAILED"
  | "ERROR"
  | "queued"
  | "running"
  | "done"
  | "failed"
  | "TIMEOUT"
  | string

export type PanelErrorSource = "compiler" | "linter" | "pattern" | "structures" | "runtime" | string

/** Normalized error row shown in StudentBottomPanel. */
export interface PanelError {
  type: string
  text: string
  source?: PanelErrorSource
  line?: number
  column?: number
  [key: string]: unknown
}

export interface TestCaseResult {
  case: number
  status: ExecutionStatus
  inputs?: string
  input?: string
  expected?: string
  actual?: string
  message?: string
  duration_ms?: number | null
  durationMs?: number | null
  execution_time_ms?: number | null
  time_ms?: number | null
}

/** Mapped execution payload from applyExecutionResult / mapSubmissionToExecution. */
export interface SubmissionResult {
  task_id?: number
  success?: boolean
  submission_id?: number | string | null
  compiler_errors?: PanelError[]
  linter_errors?: PanelError[]
  pattern_errors?: PanelError[]
  test_results?: TestCaseResult[]
  status?: ExecutionStatus
  [key: string]: unknown
}

/** Request body for POST /submissions via submitSolution. */
export interface SubmitSolutionPayload {
  task_id: number | string
  code?: string
  language?: string
  [key: string]: unknown
}

/** Async job poll response from /solutions/result/:jobId or /submissions/:id. */
export interface ExecutionJobResult {
  job_id?: string
  status?: ExecutionStatus
  success?: boolean
  compiler_errors?: PanelError[]
  linter_errors?: PanelError[]
  pattern_errors?: PanelError[]
  test_results?: TestCaseResult[]
  validation?: {
    errors?: PanelError[]
    execution_results?: TestCaseResult[]
    test_cases?: Record<string, string>[]
    semantic_checked?: boolean
    debug?: Record<string, unknown>
  }
  [key: string]: unknown
}
