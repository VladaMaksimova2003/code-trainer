import { api } from "@/shared/api"
import type { PanelError, SubmissionResult } from "@/shared/types/execution"

interface GuestJobPayload {
  job_id?: string
  status?: string
  success?: boolean
  compiler_errors?: PanelError[]
  linter_errors?: PanelError[]
  pattern_errors?: PanelError[]
  test_results?: SubmissionResult["test_results"]
}

interface PollGuestJobOptions {
  maxAttempts?: number
  intervalMs?: number
}

const pollGuestJob = async (
  jobId: string,
  { maxAttempts = 240, intervalMs = 500 }: PollGuestJobOptions = {},
): Promise<GuestJobPayload> => {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const res = await api.get(`/guest/check/${jobId}`)
    const payload = (res.data || {}) as GuestJobPayload
    if (payload.status === "SUCCESS" || payload.status === "FAILED") {
      return payload
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }
  return {
    job_id: jobId,
    status: "TIMEOUT",
    success: false,
    compiler_errors: [{
      type: "TIMEOUT",
      text: "Проверка не завершилась вовремя.",
    }],
  }
}

export interface GuestSolutionPayload {
  task_id: number | string
  language?: string
  code?: string
}

export interface GuestSolutionResult extends SubmissionResult {
  guest: boolean
}

export const submitGuestSolution = async (data: GuestSolutionPayload): Promise<GuestSolutionResult> => {
  const queued = await api.post("/guest/check", {
    task_id: data.task_id,
    language: data.language,
    code: data.code,
  })
  const jobId = (queued.data as { job_id?: string })?.job_id
  if (!jobId) {
    throw new Error("guest job_id is missing")
  }
  const result = await pollGuestJob(jobId)
  return {
    task_id: data.task_id,
    success: Boolean(result.success),
    compiler_errors: result.compiler_errors ?? [],
    linter_errors: result.linter_errors ?? [],
    pattern_errors: result.pattern_errors ?? [],
    test_results: result.test_results ?? [],
    guest: true,
  }
}
