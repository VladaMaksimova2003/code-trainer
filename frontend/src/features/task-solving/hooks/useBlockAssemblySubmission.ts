import { useCallback } from "react"

import type { Dispatch, SetStateAction } from "react"

import { submitBlockReorderSolution } from "@/shared/api"

import { submitGuestSolution } from "@/shared/api/guestApi"

import { filterReportErrors, isNonBlockingPatternWarning, partitionTestResults } from "@/features/task-solving/model/testPanelUtils"

import { getBlockVariantForLanguage } from "@/features/task-solving/model/studentUiUtils"

import {

  assembleSlotTemplate,

  buildCode,

  deriveSubmitPayload,

  isAssemblyComplete,

  assemblyCompletionStats,

  isSlotAssemblyOrderCorrect,

  BLOCK_ORDER_ERROR_MESSAGE,

  normalizePlacements,

} from "@/domain/blockAssembly"

import { templateScaffoldIsWhitespaceOnly } from "@/domain/blockAssembly/blockScaffold"

import type { BlockPlacement } from "@/domain/blockAssembly"

import type { PanelError, SubmissionResult, TestCaseResult } from "@/shared/types/execution"

import type { TaskDto } from "@/shared/types/task"



interface BlockReorderResponse {

  structural_correct?: boolean

  status?: string

  message?: string

  execution_results?: TestCaseResult[]

  pattern_errors?: PanelError[]

  correct?: boolean

  semantic_checked?: boolean

}



interface UseBlockAssemblySubmissionOptions {

  taskId: string | undefined

  task: TaskDto | null

  guestMode: boolean

  blockLanguage: string

  userLanguage: string

  blockAssemblyCode: string

  blockPlacements: BlockPlacement[]

  setTask: Dispatch<SetStateAction<TaskDto | null>>

  setBottomTab: (tab: string) => void

  applyExecutionResult: (execution: SubmissionResult) => void

  setCompilerErrors: (errors: PanelError[]) => void

  setLinterErrors: (errors: PanelError[]) => void

  setPatternErrors: (errors: PanelError[]) => void

  setResults: (results: TestCaseResult[]) => void

}



function isBlockAssemblyOrderWrong(response: BlockReorderResponse): boolean {

  const results = response.execution_results ?? []

  if (response.semantic_checked || results.length > 0) {

    return false

  }

  if (response.structural_correct === false) return true

  if (response.correct === false) {

    const hasFailedTests = results.some(

      (row) => row.status === "FAILED" || row.status === "ERROR",

    )

    return !hasFailedTests

  }

  return false

}



function blockOrderErrors(message?: string): PanelError[] {

  return [

    {

      type: "BLOCK_ORDER",

      text: message || BLOCK_ORDER_ERROR_MESSAGE,

    },

  ]

}



function showBlockOrderFailure(

  message: string | undefined,

  setCompilerErrors: (errors: PanelError[]) => void,

  setPatternErrors: (errors: PanelError[]) => void,

  setLinterErrors: (errors: PanelError[]) => void,

  setResults: (results: TestCaseResult[]) => void,

  setBottomTab: (tab: string) => void,

) {

  setCompilerErrors([])

  setLinterErrors([])

  setPatternErrors(blockOrderErrors(message))

  setResults([])

  setBottomTab("errors")

}



/**

 * Block assembly / reorder submit path (FE-ARCH-6.6).

 */

export function useBlockAssemblySubmission({

  taskId,

  task,

  guestMode,

  blockLanguage,

  userLanguage,

  blockAssemblyCode,

  blockPlacements,

  setTask,

  setBottomTab,

  applyExecutionResult,

  setCompilerErrors,

  setLinterErrors,

  setPatternErrors,

  setResults,

}: UseBlockAssemblySubmissionOptions) {

  const runBlockAssemblySubmit = useCallback(async () => {

    if (!task) return

    const learningVariant = getBlockVariantForLanguage(task, blockLanguage || userLanguage)

    const blockList = learningVariant?.blocks ?? task.blocks ?? []

    const rawTemplate = String(learningVariant?.template ?? task.template ?? "")

    const correctOrder = (learningVariant?.correct_order ??

      task.correct_order) as number[] | undefined

    const completion = assemblyCompletionStats(

      blockPlacements,

      blockList.length,

      rawTemplate,

    )

    const hasTestCases = Array.isArray(task.test_cases) && task.test_cases.length > 0

    if (!hasTestCases) {

      setCompilerErrors([])

      setPatternErrors([])

      setLinterErrors([

        {

          type: "TEST_CASES_REQUIRED",

          text: "Для проверки этой задачи преподаватель должен добавить тестовые данные.",

        },

      ])

      setResults([])

      setBottomTab("errors")

      return

    }

    if (!isAssemblyComplete(blockPlacements, blockList.length, rawTemplate)) {

      setCompilerErrors([])

      setPatternErrors([])

      setLinterErrors([

        {

          type: "INCOMPLETE_BLOCKS",

          text: `Не все блоки расставлены: заполните все пропуски (${completion.filled} из ${completion.required}).`,

        },

      ])

      setResults([])

      setBottomTab("errors")

      return

    }

    if (

      !hasTestCases &&

      /\{\d+\}/.test(rawTemplate) &&

      !isSlotAssemblyOrderCorrect(blockPlacements, blockList, correctOrder, rawTemplate)

    ) {

      showBlockOrderFailure(

        undefined,

        setCompilerErrors,

        setPatternErrors,

        setLinterErrors,

        setResults,

        setBottomTab,

      )

      return

    }



    const normalizedPlacements = normalizePlacements(blockPlacements, blockAssemblyCode)

    const slotTemplate = /\{\d+\}/.test(rawTemplate) ? rawTemplate : ""

    const whitespaceScaffold = templateScaffoldIsWhitespaceOnly(slotTemplate)

    const assemblyBase = whitespaceScaffold ? "" : blockAssemblyCode

    const builtCode = buildCode(assemblyBase, normalizedPlacements, blockList)

    const slotAssembled = slotTemplate

      ? assembleSlotTemplate(slotTemplate, blockList, normalizedPlacements)

      : ""

    const assembledCode = slotAssembled.trim() || builtCode.trim() || builtCode

    if (guestMode) {

      const execution = (await submitGuestSolution({

        task_id: Number(taskId),

        code: assembledCode,

        language: blockLanguage || userLanguage,

      })) as SubmissionResult

      applyExecutionResult(execution)

      return

    }

    const { order, indents } = deriveSubmitPayload(normalizedPlacements, assemblyBase)

    const reorderResponse = (await submitBlockReorderSolution(Number(taskId), {

      order,

      language: blockLanguage || userLanguage,

      indents,

      assembledCode,

    })) as BlockReorderResponse

    if (reorderResponse.status === "TIMEOUT") {

      setCompilerErrors([])

      setPatternErrors([])

      setLinterErrors([

        {

          type: "EXECUTION_TIMEOUT",

          text: "Проверка заняла слишком много времени. Попробуйте ещё раз через несколько секунд.",

        },

      ])

      setResults([])

      setBottomTab("errors")

      return

    }



    const orderWrong = isBlockAssemblyOrderWrong(reorderResponse)

    if (orderWrong) {

      const apiMessage = reorderResponse.message

      const message =

        apiMessage && !/^correct/i.test(apiMessage.trim())

          ? apiMessage

          : undefined

      showBlockOrderFailure(

        message,

        setCompilerErrors,

        setPatternErrors,

        setLinterErrors,

        setResults,

        setBottomTab,

      )

      setTask((cur) =>

        cur

          ? {

              ...cur,

              attempted: true,

              solved: false,

              submissions_count: Number(cur.submissions_count || 0) + 1,

            }

          : cur,

      )

      return

    }



    setLinterErrors([])

    const reorderPatternErrors = filterReportErrors(reorderResponse.pattern_errors || [])

    setPatternErrors(reorderPatternErrors)

    let nextCompilerErrors: PanelError[] = []

    let nextResults: TestCaseResult[] = []

    if (

      Array.isArray(reorderResponse.execution_results) &&

      reorderResponse.execution_results.length > 0

    ) {

      const rawResults = reorderResponse.execution_results.map((row) => ({

        ...row,

        actual:

          row.actual ||

          (row.status === "FAILED" || row.status === "ERROR" ? row.message || "" : row.actual),

      }))

      const partitioned = partitionTestResults(rawResults)

      nextResults = partitioned.testResults

      nextCompilerErrors = partitioned.compilerErrors

    } else if (reorderResponse.correct && reorderPatternErrors.length === 0) {

      nextResults = (task.test_cases || []).map((testCase, index) => ({

        case: index + 1,

        status: "PASSED",

        inputs: testCase.inputs ?? "",

        expected: testCase.output ?? "",

        actual: testCase.output ?? "",

        message: "Correct solution.",

      }))

    } else {

      nextResults = []

    }

    setCompilerErrors(filterReportErrors(nextCompilerErrors))

    setResults(nextResults)

    const blockingPatternErrors = reorderPatternErrors.filter(
      (item) => !isNonBlockingPatternWarning(item),
    )

    const hasErrors = nextCompilerErrors.length > 0 || blockingPatternErrors.length > 0

    const allTestsPassed =

      nextResults.length > 0 && nextResults.every((row) => row.status === "PASSED")

    const isSolved =

      (Boolean(reorderResponse.correct) || allTestsPassed) &&

      blockingPatternErrors.length === 0

    setTask((cur) =>

      cur

        ? {

            ...cur,

            attempted: true,

            solved: isSolved || Boolean(cur.solved),

            submissions_count: Number(cur.submissions_count || 0) + 1,

          }

        : cur,

    )

    if (reorderPatternErrors.length > 0) {

      setBottomTab("errors")

    } else if (nextCompilerErrors.length > 0) {

      setBottomTab("errors")

    } else if (

      nextResults.some((row) => row.status === "FAILED" || row.status === "ERROR")

    ) {

      setBottomTab("case")

    } else {

      setBottomTab(hasErrors ? "errors" : "case")

    }

  }, [

    taskId,

    task,

    guestMode,

    blockLanguage,

    userLanguage,

    blockAssemblyCode,

    blockPlacements,

    setTask,

    setBottomTab,

    applyExecutionResult,

    setCompilerErrors,

    setLinterErrors,

    setPatternErrors,

    setResults,

  ])



  return { runBlockAssemblySubmit }

}


