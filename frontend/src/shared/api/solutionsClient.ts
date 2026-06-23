import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"

const LINT_SESSION_STORAGE_KEY = "code-trainer-lint-session-id"

const getLintSessionId = () => {
  const stored = window.localStorage.getItem(LINT_SESSION_STORAGE_KEY)
  if (stored) {
    return stored
  }

  const created = window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
  window.localStorage.setItem(LINT_SESSION_STORAGE_KEY, created)
  return created
}

const pollSolutionJob = async (
  jobId: string,
  { maxAttempts = 120, intervalMs = 250 }: { maxAttempts?: number; intervalMs?: number } = {},
) => {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const res = await api.get(`/solutions/result/${jobId}`)
    const payload = res.data || {}
    const status = payload.status
    if (status === "SUCCESS" || status === "FAILED" || status === "TIMEOUT") {
      return payload
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }
  return { job_id: jobId, status: "TIMEOUT" }
}

export const lintSolution = async (data: Record<string, unknown>) => {
  if (isMockApiEnabled()) return mockHandlers.lintSolution(data)
  const queued = await api.post("/solutions/lint", {
    ...data,
    session_id: getLintSessionId(),
  })
  const jobId = queued.data?.job_id
  if (!jobId) {
    throw new Error("Lint job_id is missing")
  }

  const polled = await pollSolutionJob(jobId, { maxAttempts: 20, intervalMs: 250 })
  const output = polled.output || {}
  if (polled.status === "FAILED" && polled.errors) {
    return {
      status: "failed",
      linter_errors: [{ type: "EXECUTION", text: String(polled.errors) }],
    }
  }
  if (polled.status === "TIMEOUT") {
    return {
      status: "timeout",
      linter_errors: [
        {
          type: "TIMEOUT",
          text: "Проверка кода не успела завершиться. Убедитесь, что worker запущен и обрабатывает очередь.",
        },
      ],
    }
  }
  return {
    status: polled.status === "SUCCESS" ? "done" : polled.status?.toLowerCase?.() || "done",
    linter_errors: output.linter_errors ?? [],
  }
}

export const checkPatterns = async (data: Record<string, unknown> & { task_id?: number | string }) => {
  const queued = await api.post("/solutions/patterns", {
    ...data,
    session_id: getLintSessionId(),
  })
  const jobId = queued.data?.job_id
  if (!jobId) {
    throw new Error("Pattern job_id is missing")
  }

  const maxAttempts = 60
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const res = await api.get(`/solutions/result/${jobId}`)
    const payload = res.data || {}
    if (payload.status === "SUCCESS" || payload.status === "FAILED") {
      const output = payload.output || {}
      return {
        task_id: output.task_id ?? data.task_id,
        pattern_errors: output.pattern_errors ?? [],
        job_id: jobId,
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 200))
  }
  return { task_id: data.task_id, pattern_errors: [], job_id: jobId }
}
