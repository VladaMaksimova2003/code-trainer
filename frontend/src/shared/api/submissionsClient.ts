import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"
import type { SubmissionResult, SubmitSolutionPayload } from "@/shared/types/execution"

const PENDING_SUBMISSION_STORAGE_PREFIX = "code-trainer-pending-submission:"

const pendingSubmissionStorageKey = (taskId: number | string) =>
  `${PENDING_SUBMISSION_STORAGE_PREFIX}${taskId}`

export const rememberPendingSubmission = (taskId: number | string, submissionId: number | string) => {
  if (!taskId || !submissionId) return
  window.sessionStorage.setItem(pendingSubmissionStorageKey(taskId), String(submissionId))
}

export const clearPendingSubmission = (taskId: number | string) => {
  if (!taskId) return
  window.sessionStorage.removeItem(pendingSubmissionStorageKey(taskId))
}

export const readPendingSubmissionId = (taskId: number | string): number | null => {
  if (!taskId) return null
  const raw = window.sessionStorage.getItem(pendingSubmissionStorageKey(taskId))
  if (!raw) return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : null
}

export const mapSubmissionToExecution = (
  submission: SubmissionResult | null | undefined,
  fallbackTaskId?: number | string,
): SubmissionResult => ({
  task_id: submission?.task_id ?? fallbackTaskId,
  submission_id: submission?.submission_id ?? (submission as { id?: number | string } | undefined)?.id,
  success: Boolean(submission?.success),
  compiler_errors: submission?.compiler_errors ?? [],
  linter_errors: submission?.linter_errors ?? [],
  pattern_errors: submission?.pattern_errors ?? [],
  test_results: submission?.test_results ?? [],
  status: submission?.status,
})

const SUBMIT_POLL_TOTAL_MS = 15000
const SUBMIT_POLL_GRACE_MS = 1200
const SUBMIT_POLL_QUEUED_MS = 2000
const SUBMIT_POLL_INTERVAL_MS = 80

interface PollSubmissionOptions {
  totalMs?: number
  queuedMs?: number
  intervalMs?: number
  graceMs?: number
  onStatus?: (submission: SubmissionResult) => void
}

const finalizePollResult = async (
  submissionId: number | string,
  pollResult: SubmissionResult,
  graceMs = SUBMIT_POLL_GRACE_MS,
) => {
  if (pollResult.status !== "timeout") {
    return pollResult
  }
  const graceUntil = Date.now() + graceMs
  while (Date.now() < graceUntil) {
    try {
      const latest = await getSubmission(submissionId)
      if (latest.status === "done" || latest.status === "failed") {
        return latest
      }
    } catch {
      /* retry */
    }
    await new Promise((resolve) => setTimeout(resolve, SUBMIT_POLL_INTERVAL_MS))
  }
  return pollResult
}

const pollSubmission = async (
  submissionId: number | string,
  {
    totalMs = SUBMIT_POLL_TOTAL_MS,
    queuedMs = SUBMIT_POLL_QUEUED_MS,
    intervalMs = SUBMIT_POLL_INTERVAL_MS,
    graceMs = SUBMIT_POLL_GRACE_MS,
    onStatus,
  }: PollSubmissionOptions = {},
) => {
  const deadline = Date.now() + totalMs
  let queuedSince: number | null = null

  while (Date.now() < deadline) {
    const submission = await getSubmission(submissionId)
    if (typeof onStatus === "function") {
      onStatus(submission)
    }
    if (submission.status === "done" || submission.status === "failed") {
      return submission
    }

    const now = Date.now()
    if (submission.status === "queued") {
      if (queuedSince == null) queuedSince = now
      if (now - queuedSince >= queuedMs) {
        return finalizePollResult(
          submissionId,
          {
            id: submissionId,
            status: "timeout",
            success: false,
            stale_queue: true,
          } as SubmissionResult,
          graceMs,
        )
      }
    } else {
      queuedSince = null
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }

  return finalizePollResult(
    submissionId,
    {
      id: submissionId,
      status: "timeout",
      success: false,
      stale_running: true,
    } as SubmissionResult,
    graceMs,
  )
}

export const abandonSubmission = async (submissionId: number | string) => {
  if (isMockApiEnabled()) return { released: true }
  const res = await api.post(`/submissions/${submissionId}/abandon`)
  return res.data
}

export const getLatestPendingSubmission = async (taskId: number | string) => {
  const res = await api.get("/submissions/pending/latest", { params: { task_id: taskId } })
  return res.data?.submission ?? null
}

export const getLatestSubmissionForTask = async (
  taskId: number | string,
): Promise<number | null> => {
  if (isMockApiEnabled()) return null
  const res = await api.get("/submissions/latest", { params: { task_id: taskId } })
  const submissionId = res.data?.submission_id
  if (submissionId == null) return null
  const parsed = Number(submissionId)
  return Number.isFinite(parsed) ? parsed : null
}

export interface SubmitSolutionOptions {
  onStatus?: (submission: SubmissionResult) => void
}

export const submitSolution = async (
  data: SubmitSolutionPayload,
  { onStatus }: SubmitSolutionOptions = {},
): Promise<SubmissionResult> => {
  if (isMockApiEnabled()) return mockHandlers.submitSolution(data)

  const queued = await api.post("/submissions/", {
    task_id: data.task_id,
    language: data.language,
    code: data.code,
  })
  const submissionId = queued.data?.submission_id
  if (!submissionId) {
    throw new Error("submission_id is missing")
  }

  rememberPendingSubmission(data.task_id, submissionId)

  const submission = await pollSubmission(submissionId, { onStatus })
  clearPendingSubmission(data.task_id)

  if (submission.status === "timeout") {
    if (submission.stale_queue) {
      abandonSubmission(submissionId).catch(() => {})
    }
    const timeoutText = submission.stale_queue
      ? "Сервер проверки не отвечает. Запустите Redis и execution worker (см. backend/docs/RUN_GUIDE.md), затем нажмите «Прогнать» снова."
      : "Проверка заняла слишком много времени. Подождите несколько секунд и нажмите «Прогнать» снова — результат может уже быть готов."
    return {
      ...mapSubmissionToExecution(submission, data.task_id),
      success: false,
      compiler_errors: [{
        type: "TIMEOUT",
        text: timeoutText,
      }],
      submission_id: submissionId,
    }
  }

  return mapSubmissionToExecution(submission, data.task_id)
}

export interface ResumeSubmissionCheckOptions {
  onStatus?: (submission: SubmissionResult) => void
  totalMs?: number
  graceMs?: number
}

export const resumeSubmissionCheck = async (
  taskId: number | string,
  submissionId: number | string,
  { onStatus, totalMs = 3500, graceMs = 800 }: ResumeSubmissionCheckOptions = {},
): Promise<SubmissionResult | null> => {
  const submission = await pollSubmission(submissionId, {
    onStatus,
    totalMs,
    graceMs,
  })
  if (submission.status === "done" || submission.status === "failed" || submission.status === "timeout") {
    if (submission.stale_queue) {
      abandonSubmission(submissionId).catch(() => {})
    }
    clearPendingSubmission(taskId)
  }
  if (submission.status === "timeout") {
    return null
  }
  return mapSubmissionToExecution(submission, taskId)
}

export const createSubmission = async (data: Record<string, unknown>) => {
  const res = await api.post("/submissions/", data)
  return res.data
}

export const getSubmission = async (submissionId: number | string): Promise<SubmissionResult> => {
  const res = await api.get(`/submissions/${submissionId}`)
  return res.data
}
