import { useCallback, useEffect, useRef, useState } from "react"
import type { Dispatch, MutableRefObject, SetStateAction } from "react"
import {
  getLatestPendingSubmission,
  getLatestSubmissionForTask,
  getSubmission,
  lintSolution,
  readPendingSubmissionId,
  clearPendingSubmission,
  mapSubmissionToExecution,
  resumeSubmissionCheck,
} from "@/shared/api"
import { getTeacherSubmissionDetail } from "@/features/analytics/api/analyticsApi"
import {
  filterReportErrors,
  isRuntimeErrorOutput,
  partitionTestResults,
} from "@/features/task-solving/model/testPanelUtils"
import { lintDebounceMs } from "@/features/task-solving/model/lintDebounce"
import { isMcqTask } from "@/features/task-solving/model/studentUiUtils"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import {
  normalizeCurriculumLearningLanguage,
} from "@/shared/config/curriculumLanguages"
import {
  writeStoredLearningLanguage,
} from "@/features/curriculum/curriculumLanguageUi"
import type { BlockPlacement } from "@/domain/blockAssembly"
import type { FlowCheckDebug } from "@/shared/types/flow"
import type { PanelError, SubmissionResult, TestCaseResult } from "@/shared/types/execution"
import type { TaskDto } from "@/shared/types/task"

type FlowchartSolutionMode = "code" | "flow"

interface TeacherReviewState {
  submissionId?: number | string
}

interface PendingSubmissionPayload {
  submission_id?: number | string
  id?: number | string
  status?: string
}

interface SubmissionStatusPayload {
  status?: string
}

interface LintSolutionResponse {
  linter_errors?: PanelError[]
}

interface UseExecutionResultStateOptions {
  taskId: string | undefined
  task: TaskDto | null
  setTask: Dispatch<SetStateAction<TaskDto | null>>
  loadedTaskId: string | null
  isTaskLoading: boolean
  guestMode: boolean
  isTeacherReview: boolean
  teacherReview: TeacherReviewState | null
  isBlockAssemblyTask: boolean
  code: string
  userLanguage: string
  flowchartSolutionMode: FlowchartSolutionMode
  blockAssemblyCode: string
  blockPlacements: BlockPlacement[]
  blockLanguage: string
  bottomTab: string
  setBottomTab: (tab: string) => void
  setUserLanguage: (language: string) => void
  setCode: (code: string) => void
  onResumeStartedRef: MutableRefObject<string | null>
}

/**
 * Execution results, errors, bottom tab, lint, pending resume (FE-ARCH-6.4).
 */
export function useExecutionResultState({
  taskId,
  task,
  setTask,
  loadedTaskId,
  isTaskLoading,
  guestMode,
  isTeacherReview,
  teacherReview,
  isBlockAssemblyTask,
  code,
  userLanguage,
  flowchartSolutionMode,
  blockAssemblyCode,
  blockPlacements,
  blockLanguage,
  bottomTab,
  setBottomTab,
  setUserLanguage,
  setCode,
  onResumeStartedRef,
}: UseExecutionResultStateOptions) {
  const [results, setResults] = useState<TestCaseResult[]>([])
  const [compilerErrors, setCompilerErrors] = useState<PanelError[]>([])
  const [linterErrors, setLinterErrors] = useState<PanelError[]>([])
  const [patternErrors, setPatternErrors] = useState<PanelError[]>([])
  const [flowCheckDebug, setFlowCheckDebug] = useState<FlowCheckDebug | null>(null)
  const [reviewSubmission, setReviewSubmission] = useState<TeacherSubmissionDetail | null>(null)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [studentSubmissionId, setStudentSubmissionId] = useState<number | string | null>(null)

  const lintRequestSeqRef = useRef(0)

  const clearExecutionPanels = useCallback(() => {
    setResults([])
    setCompilerErrors([])
    setLinterErrors([])
    setPatternErrors([])
  }, [])

  const applyExecutionResult = useCallback(
    (execution: SubmissionResult) => {
      const partitioned = partitionTestResults(execution.test_results || [])
      setResults(partitioned.testResults)
      const nextCompilerErrors = filterReportErrors([
        ...(execution.compiler_errors || []),
        ...partitioned.compilerErrors,
      ])
      const nextLinterErrors = filterReportErrors(execution.linter_errors || [])
      const nextPatternErrors = filterReportErrors(execution.pattern_errors || [])
      setCompilerErrors(nextCompilerErrors)
      setLinterErrors(nextLinterErrors)
      setPatternErrors(nextPatternErrors)
      const hasPanelErrors =
        nextCompilerErrors.length > 0 ||
        nextLinterErrors.length > 0 ||
        nextPatternErrors.length > 0
      setTask((cur) =>
        cur
          ? {
              ...cur,
              attempted: true,
              solved: Boolean(execution.success) || Boolean(cur.solved),
              submissions_count: Number(cur.submissions_count || 0) + 1,
            }
          : cur,
      )
      if (execution.success) {
        const track = normalizeCurriculumLearningLanguage(userLanguage)
        if (track) {
          writeStoredLearningLanguage(track)
        }
      }
      if (execution.submission_id) {
        setStudentSubmissionId(execution.submission_id)
      }
      const hasRuntimeFailures =
        partitioned.compilerErrors.some((err) => err?.type === "RUNTIME") ||
        partitioned.testResults.some(
          (row) =>
            (row.status === "ERROR" || row.status === "FAILED") &&
            isRuntimeErrorOutput([row.actual, row.message].filter(Boolean).join("\n")),
        )
      if (hasPanelErrors || hasRuntimeFailures) {
        setBottomTab("errors")
      } else if (partitioned.testResults.length > 0) {
        setBottomTab("case")
      } else {
        setBottomTab("case")
      }
    },
    [setTask, setBottomTab, userLanguage],
  )

  useEffect(() => {
    if (!teacherReview?.submissionId) {
      setReviewSubmission(null)
      return undefined
    }
    let cancelled = false
    setReviewLoading(true)
    getTeacherSubmissionDetail(teacherReview.submissionId)
      .then((detail: TeacherSubmissionDetail) => {
        if (cancelled) return
        setReviewSubmission(detail)
        if (detail?.code && !isBlockAssemblyTask && !isFlowchartTask(task)) setCode(detail.code)
        if (detail?.language) setUserLanguage(detail.language)
      })
      .catch(() => {
        if (!cancelled) setReviewSubmission(null)
      })
      .finally(() => {
        if (!cancelled) setReviewLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [teacherReview?.submissionId, task?.type, isBlockAssemblyTask, setCode, setUserLanguage, task])

  useEffect(() => {
    if (guestMode || isTeacherReview || !taskId) {
      setStudentSubmissionId(null)
      return undefined
    }
    let cancelled = false
    getLatestSubmissionForTask(taskId)
      .then((submissionId) => {
        if (cancelled) return
        setStudentSubmissionId(submissionId)
      })
      .catch(() => {
        if (!cancelled) setStudentSubmissionId(null)
      })
    return () => {
      cancelled = true
    }
  }, [taskId, isTeacherReview, guestMode])

  useEffect(() => {
    if (
      guestMode ||
      isTeacherReview ||
      !taskId ||
      loadedTaskId !== String(taskId) ||
      isTaskLoading
    ) {
      return undefined
    }

    if (onResumeStartedRef.current === String(taskId)) {
      return undefined
    }
    onResumeStartedRef.current = String(taskId)

    let cancelled = false

    const resolvePendingSubmission = async () => {
      let pending: PendingSubmissionPayload | null = null
      try {
        pending = (await getLatestPendingSubmission(Number(taskId))) as PendingSubmissionPayload | null
      } catch {
        pending = null
      }

      const storedId = readPendingSubmissionId(Number(taskId))
      const submissionId = pending?.submission_id ?? pending?.id ?? storedId
      if (!submissionId) {
        return null
      }

      if (pending && ["queued", "running"].includes(pending?.status ?? "")) {
        return { submissionId, status: pending.status }
      }

      if (!storedId) {
        return null
      }

      try {
        const stored = (await getSubmission(storedId)) as SubmissionStatusPayload
        if (["queued", "running"].includes(stored?.status ?? "")) {
          return { submissionId: storedId, status: stored.status }
        }
        clearPendingSubmission(Number(taskId))
      } catch {
        clearPendingSubmission(Number(taskId))
      }
      return null
    }

    const resumePending = async () => {
      const pending = await resolvePendingSubmission()
      if (!pending || cancelled) {
        return
      }

      try {
        const submission = (await getSubmission(pending.submissionId)) as SubmissionStatusPayload
        if (cancelled) return
        if (submission.status === "done" || submission.status === "failed") {
          clearPendingSubmission(Number(taskId))
          applyExecutionResult(mapSubmissionToExecution(submission, Number(taskId)) as SubmissionResult)
          return
        }
        if (!["queued", "running"].includes(submission.status ?? "")) {
          clearPendingSubmission(Number(taskId))
          return
        }
      } catch {
        clearPendingSubmission(Number(taskId))
        return
      }

      try {
        const execution = (await resumeSubmissionCheck(
          Number(taskId),
          pending.submissionId,
        )) as SubmissionResult | null
        if (!cancelled && execution) {
          applyExecutionResult(execution)
        }
      } catch {
        clearPendingSubmission(Number(taskId))
      }
    }

    resumePending()
    return () => {
      cancelled = true
    }
  }, [taskId, loadedTaskId, isTaskLoading, isTeacherReview, guestMode, applyExecutionResult, onResumeStartedRef])

  useEffect(() => {
    const trimmedCode = code.trim()
    if (guestMode || !task || isBlockAssemblyTask || !userLanguage) return
    if (isMcqTask(task)) {
      setLinterErrors([])
      return
    }
    if (isFlowchartTask(task) && flowchartSolutionMode !== "code") {
      setLinterErrors([])
      return
    }
    if (!trimmedCode) {
      setLinterErrors([])
      return
    }

    const requestSeq = ++lintRequestSeqRef.current
    const debounceMs = lintDebounceMs(userLanguage)
    const timer = setTimeout(async () => {
      try {
        const res = (await lintSolution({
          task_id: Number(taskId),
          language: userLanguage,
          code,
        })) as LintSolutionResponse
        if (requestSeq !== lintRequestSeqRef.current) return
        const nextLinterErrors = filterReportErrors(res.linter_errors || [])
        setLinterErrors(nextLinterErrors)
        if (nextLinterErrors.length > 0) setBottomTab("errors")
      } catch {
        setLinterErrors([
          {
            type: "EXECUTION",
            text: "Не удалось выполнить проверку кода. Убедитесь, что worker и runner-образы запущены на сервере.",
          },
        ])
        setBottomTab("errors")
      }
    }, debounceMs)
    return () => clearTimeout(timer)
  }, [
    task,
    taskId,
    code,
    userLanguage,
    flowchartSolutionMode,
    guestMode,
    isBlockAssemblyTask,
    setBottomTab,
  ])

  useEffect(() => {
    if (!taskId || isBlockAssemblyTask) return
    if (task && isFlowchartTask(task) && flowchartSolutionMode === "flow") return
    setCompilerErrors([])
    setPatternErrors([])
    setResults([])
    setFlowCheckDebug(null)
  }, [taskId, code, userLanguage, flowchartSolutionMode, isBlockAssemblyTask, task?.type])

  useEffect(() => {
    if (!task || !isBlockAssemblyTask) return
    setCompilerErrors([])
    setLinterErrors([])
    setPatternErrors([])
    if (bottomTab === "errors") setBottomTab("case")
  }, [task?.id, blockAssemblyCode, blockPlacements, blockLanguage, isBlockAssemblyTask])

  useEffect(() => {
    if (compilerErrors.length > 0 || linterErrors.length > 0 || patternErrors.length > 0) {
      setBottomTab("errors")
      return
    }
    if (results.length > 0) setBottomTab("case")
  }, [compilerErrors, linterErrors, patternErrors, results, setBottomTab])

  return {
    results,
    setResults,
    compilerErrors,
    setCompilerErrors,
    linterErrors,
    setLinterErrors,
    patternErrors,
    setPatternErrors,
    flowCheckDebug,
    setFlowCheckDebug,
    reviewSubmission,
    reviewLoading,
    studentSubmissionId,
    applyExecutionResult,
    clearExecutionPanels,
  }
}
