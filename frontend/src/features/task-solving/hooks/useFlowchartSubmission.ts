import { useCallback, useRef } from "react"
import type { Dispatch, SetStateAction } from "react"
import { checkFlow } from "@/shared/api"
import { buildFlowchartCheckTestResults } from "@/features/task-solving/model/testPanelUtils"
import {
  getFlowDraftKey,
  getStudentFlowStarterPayload,
  isFlowEmpty,
} from "@/widgets/BlockEditor/lib/flowInitialState"
import { summarizeFlowPayload } from "@/widgets/BlockEditor/lib/flowPayload"
import { flowPayloadSignatureSafe } from "@/features/task-solving/model/flowSubmitHelpers"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import { getTaskDraftSignature, mergeDraft } from "@/features/task-solving/model/taskDraftHelpers"
import type { FlowCheckDebug, FlowCheckResult, FlowPayload } from "@/shared/types/flow"
import type { PanelError, TestCaseResult } from "@/shared/types/execution"
import type { TaskDto } from "@/shared/types/task"

type GetFlowPayload = () => FlowPayload | null | undefined

/** Debug panel payload — extends backend FlowCheckDebug with frontend diagnostics. */
interface FrontendFlowCheckDebug extends FlowCheckDebug {
  source?: string
  editor?: Record<string, unknown>
  reactState?: Record<string, unknown>
  payloadMismatch?: boolean
  request?: Record<string, unknown>
  response?: Record<string, unknown>
  validator?: FlowCheckDebug | null
}

interface UseFlowchartSubmissionOptions {
  taskId: string | undefined
  task: TaskDto | null
  flow: FlowPayload
  setFlow: (flow: FlowPayload) => void
  setTask: Dispatch<SetStateAction<TaskDto | null>>
  setBottomTab: (tab: string) => void
  applyExecutionResult: (execution: Record<string, unknown>) => void
  setCompilerErrors: (errors: PanelError[]) => void
  setPatternErrors: (errors: PanelError[]) => void
  setLinterErrors: (errors: PanelError[]) => void
  setResults: (results: TestCaseResult[]) => void
  setFlowCheckDebug: (debug: FrontendFlowCheckDebug | null) => void
}

/**
 * Flowchart editor payload + flow-mode submit (FE-ARCH-6.7).
 */
export function useFlowchartSubmission({
  taskId,
  task,
  flow,
  setFlow,
  setTask,
  setBottomTab,
  applyExecutionResult,
  setCompilerErrors,
  setPatternErrors,
  setLinterErrors,
  setResults,
  setFlowCheckDebug,
}: UseFlowchartSubmissionOptions) {
  const getFlowPayloadRef = useRef<GetFlowPayload | null>(null)

  const registerGetFlowPayload = useCallback((getter: GetFlowPayload) => {
    getFlowPayloadRef.current = getter
  }, [])

  const resetFlowDraft = useCallback(() => {
    if (!task || !isFlowchartTask(task)) return
    const starter = getStudentFlowStarterPayload(task) as FlowPayload
    setFlow(starter)
    setPatternErrors([])
    setLinterErrors([])
    setCompilerErrors([])
    setResults([])
    setBottomTab("case")
    mergeDraft(taskId, {
      taskSignature: getTaskDraftSignature(task),
      flowDraftKey: getFlowDraftKey(task),
      flow: starter,
    })
  }, [
    task,
    taskId,
    setFlow,
    setPatternErrors,
    setLinterErrors,
    setCompilerErrors,
    setResults,
    setBottomTab,
  ])

  const runFlowModeSubmit = useCallback(async () => {
    const livePayload = getFlowPayloadRef.current?.() || flow
    const stalePayload = flow
    const editorSummary = summarizeFlowPayload(livePayload)
    const stateSummary = summarizeFlowPayload(stalePayload)

    if (isFlowEmpty(livePayload)) {
      setCompilerErrors([])
      setPatternErrors([])
      setLinterErrors([
        {
          type: "FLOW_REQUIRED",
          text: "Соберите блок-схему в редакторе справа.",
        },
      ])
      setFlowCheckDebug({
        source: "frontend",
        editor: editorSummary,
        reactState: stateSummary,
        payloadMismatch:
          flowPayloadSignatureSafe(livePayload) !== flowPayloadSignatureSafe(stalePayload),
      })
      setResults([])
      setBottomTab("errors")
      return
    }

    const requestPayload = {
      task_id: Number(taskId),
      flow: livePayload?.flow || [],
      nodes: livePayload?.nodes || [],
      edges: livePayload?.edges || [],
    }

    if (import.meta.env.DEV) {
      console.group("[flow-check] POST /flows/check")
      console.log("request", requestPayload)
      console.log("editor vs react state", { editor: editorSummary, reactState: stateSummary })
    }

    const flowResult = (await checkFlow(requestPayload)) as FlowCheckResult

    if (import.meta.env.DEV) {
      console.log("response", flowResult)
      console.groupEnd()
    }

    const flowErrors = (flowResult?.errors || []).map((err) => ({
      type: err?.type || "FLOW",
      text: err?.text || "Ошибка блок-схемы",
    }))
    const flowTestResults = buildFlowchartCheckTestResults(task, flowResult, flowErrors)
    setPatternErrors(flowErrors)
    setResults(flowTestResults)
    setFlowCheckDebug({
      source: "frontend+backend",
      request: {
        nodeCount: requestPayload.nodes.length,
        edgeCount: requestPayload.edges.length,
        blockTypes: editorSummary.blockTypes,
      },
      reactState: stateSummary,
      payloadMismatch:
        flowPayloadSignatureSafe(livePayload) !== flowPayloadSignatureSafe(stalePayload),
      response: {
        success: flowResult?.success,
        errorTypes: flowErrors.map((item) => item.type),
      },
      validator: flowResult?.debug || null,
    })
    const flowSuccess =
      Boolean(flowResult?.success) &&
      flowErrors.length === 0 &&
      flowTestResults.every((row) => row.status === "PASSED")
    applyExecutionResult({
      task_id: Number(taskId),
      success: flowSuccess,
      compiler_errors: [],
      linter_errors: [],
      pattern_errors: flowErrors,
      test_results: flowTestResults,
    })
    setLinterErrors([])
    setFlow(livePayload)
    setTask((cur) =>
      cur
        ? {
            ...cur,
            attempted: true,
            solved: flowSuccess || Boolean(cur.solved),
            submissions_count: Number(cur.submissions_count || 0) + 1,
          }
        : cur,
    )
    if (flowErrors.length > 0) {
      setBottomTab("errors")
    } else if (flowTestResults.some((row) => row.status === "FAILED" || row.status === "ERROR")) {
      setBottomTab("case")
    } else {
      setBottomTab(flowSuccess ? "case" : "errors")
    }
  }, [
    taskId,
    flow,
    setFlow,
    setTask,
    setBottomTab,
    applyExecutionResult,
    setCompilerErrors,
    setPatternErrors,
    setLinterErrors,
    setResults,
    setFlowCheckDebug,
  ])

  /** Returns true when submit should abort (validation failed). */
  const validateFlowchartCodeMode = useCallback(
    (code: string, userLanguage: string) => {
      if (!task || !isFlowchartTask(task)) return false
      if (!code.trim()) {
        setCompilerErrors([])
        setPatternErrors([])
        setLinterErrors([{ type: "CODE_REQUIRED", text: "Напишите код по блок-схеме." }])
        setResults([])
        setBottomTab("errors")
        return true
      }
      if (!userLanguage) {
        setLinterErrors([{ type: "LANGUAGE_REQUIRED", text: "Выберите язык для своего решения." }])
        setBottomTab("errors")
        return true
      }
      const hasFlowTests = Array.isArray(task.test_cases) && task.test_cases.length > 0
      if (!hasFlowTests) {
        setCompilerErrors([])
        setPatternErrors([])
        setLinterErrors([
          {
            type: "TEST_CASES_REQUIRED",
            text: "Для этой задачи ещё не заданы тесты — преподаватель должен добавить эталонные ввод/вывод.",
          },
        ])
        setResults([])
        setBottomTab("errors")
        return true
      }
      return false
    },
    [task, setCompilerErrors, setPatternErrors, setLinterErrors, setResults, setBottomTab],
  )

  return {
    registerGetFlowPayload,
    resetFlowDraft,
    runFlowModeSubmit,
    validateFlowchartCodeMode,
  }
}
