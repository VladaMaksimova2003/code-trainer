import { useCallback } from "react"
import { getSubmission, submitSolution, mapSubmissionToExecution } from "@/shared/api"
import { submitGuestSolution } from "@/shared/api/guestApi"
import { humanizeExecutionMessage } from "@/features/task-solving/model/testPanelUtils"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import type { PanelError, SubmissionResult } from "@/shared/types/execution"
import type { TaskDto } from "@/shared/types/task"

interface ApiErrorPayload {
  response?: {
    data?: {
      detail?: string
    }
  }
}

function asApiError(error: unknown): ApiErrorPayload {
  if (typeof error === "object" && error !== null) {
    return error as ApiErrorPayload
  }
  return {}
}

interface UseCodeSubmissionOptions {
  taskId: string | undefined
  task: TaskDto | null
  guestMode: boolean
  code: string
  userLanguage: string
  applyExecutionResult: (execution: SubmissionResult) => void
  setBottomTab: (tab: string) => void
  setCompilerErrors: (errors: PanelError[]) => void
  setLinterErrors: (errors: PanelError[]) => void
  setPatternErrors: (errors: PanelError[]) => void
}

/**
 * Default code submit + guest + timeout retry (FE-ARCH-6.5).
 */
export function useCodeSubmission({
  taskId,
  task,
  guestMode,
  code,
  userLanguage,
  applyExecutionResult,
  setBottomTab,
  setCompilerErrors,
  setLinterErrors,
  setPatternErrors,
}: UseCodeSubmissionOptions) {
  const runCodeSubmit = useCallback(async () => {
    if (!userLanguage) {
      setLinterErrors([{ type: "LANGUAGE_REQUIRED", text: "Выберите язык для своего решения." }])
      setBottomTab("errors")
      return
    }

    const execution = (guestMode
      ? await submitGuestSolution({
          task_id: Number(taskId),
          code,
          language: userLanguage,
        })
      : await submitSolution({
          task_id: Number(taskId),
          code,
          language: userLanguage,
        })) as SubmissionResult
    applyExecutionResult(execution)
    const submissionId = execution?.submission_id
    const timedOut = (execution?.compiler_errors || []).some((err) => err?.type === "TIMEOUT")
    if (!guestMode && submissionId && timedOut) {
      let attempts = 0
      const retryResult = async () => {
        if (attempts >= 10) return
        attempts += 1
        try {
          const sub = (await getSubmission(submissionId)) as SubmissionResult
          if (sub?.status === "done" || sub?.status === "failed") {
            applyExecutionResult(mapSubmissionToExecution(sub, Number(taskId)) as SubmissionResult)
            return
          }
        } catch {
          /* retry */
        }
        window.setTimeout(retryResult, 200)
      }
      window.setTimeout(retryResult, 200)
    }
  }, [
    taskId,
    guestMode,
    code,
    userLanguage,
    applyExecutionResult,
    setBottomTab,
    setLinterErrors,
  ])

  const handleSubmitError = useCallback(
    (error: unknown) => {
      const backendMessage = asApiError(error).response?.data?.detail
      if (isFlowchartTask(task)) {
        setPatternErrors([
          { type: "API_ERROR", text: backendMessage || "Не удалось проверить код." },
        ])
        setBottomTab("errors")
        return
      }
      setCompilerErrors([
        {
          type: "API_ERROR",
          text: humanizeExecutionMessage(backendMessage || "Не удалось проверить код."),
        },
      ])
      setLinterErrors([])
      setBottomTab("errors")
    },
    [task, setPatternErrors, setCompilerErrors, setLinterErrors, setBottomTab],
  )

  return { runCodeSubmit, handleSubmitError }
}
