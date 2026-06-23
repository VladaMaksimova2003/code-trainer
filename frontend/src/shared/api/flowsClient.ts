import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"

const pollExecutionJob = async (
  resultPath: string,
  jobId: string,
  { maxAttempts = 120, intervalMs = 100 }: { maxAttempts?: number; intervalMs?: number } = {},
) => {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const res = await api.get(`${resultPath}/${jobId}`)
    const payload = res.data || {}
    if (payload.status === "SUCCESS" || payload.status === "FAILED" || payload.status === "TIMEOUT") {
      return payload
    }
    if (attempt + 1 < maxAttempts) {
      await new Promise((resolve) => setTimeout(resolve, intervalMs))
    }
  }
  return { job_id: jobId, status: "TIMEOUT" }
}

export const checkFlow = async (data: Record<string, unknown>) => {
  if (isMockApiEnabled()) return mockHandlers.checkFlow(data)
  const res = await api.post("/flows/check", data)
  const initial = res.data || {}
  const jobId = initial.execution_job_id
  if (!jobId) {
    return initial
  }

  const polled = await pollExecutionJob("/flows/validate/result", jobId)
  const validation = polled.validation || polled
  return {
    ...initial,
    success: polled.success ?? (Array.isArray(validation.errors) ? validation.errors.length === 0 : initial.success),
    errors: validation.errors ?? polled.errors ?? initial.errors ?? [],
    execution_results: validation.execution_results ?? polled.execution_results ?? [],
    test_cases: validation.test_cases ?? initial.test_cases ?? [],
    semantic_checked: validation.semantic_checked ?? true,
    execution_job_id: jobId,
    status: polled.status,
    debug: validation.debug ?? initial.debug ?? null,
  }
}

/**
 * Submit block assembly solution.
 * Prefer `assembledCode` (from buildCode) for line/column placements; order/indents are legacy.
 */
export const submitBlockReorderSolution = async (
  taskId: number | string,
  {
    order = [],
    language = null,
    indents = null,
    assembledCode = null,
  }: {
    order?: unknown[]
    language?: string | null
    indents?: unknown[] | null
    assembledCode?: string | null
  } = {},
) => {
  if (isMockApiEnabled()) return mockHandlers.submitBlockReorderSolution(taskId)
  const res = await api.post(`/tasks/block-reorder/${taskId}/submit`, {
    order,
    ...(language ? { language } : {}),
    ...(Array.isArray(indents) ? { indents } : {}),
    ...(assembledCode ? { assembled_code: assembledCode } : {}),
  })
  const initial = res.data || {}
  const jobId = initial.execution_job_id
  if (!jobId) {
    return initial
  }

  const polled = await pollExecutionJob("/tasks/block-reorder/validate/result", jobId)
  const validation = polled.validation || polled
  return {
    ...initial,
    ...validation,
    correct: validation.correct ?? initial.correct,
    structural_correct:
      validation.structural_correct ?? initial.structural_correct,
    execution_results: validation.execution_results ?? [],
    pattern_errors: validation.pattern_errors ?? initial.pattern_errors ?? [],
    message: validation.message ?? initial.message,
    semantic_checked: validation.semantic_checked ?? initial.semantic_checked,
    execution_job_id: jobId,
    status: polled.status,
  }
}
