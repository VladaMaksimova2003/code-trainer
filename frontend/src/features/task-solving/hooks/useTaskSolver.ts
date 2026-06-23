import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom"
import type { NavigateFunction } from "react-router-dom"
import { filterReportErrors } from "@/features/task-solving/model/testPanelUtils"
import { useLanguages } from "@/shared/hooks/useLanguages"
import { useTaskNavigation } from "@/features/task-solving/hooks/useTaskNavigation"
import { useTaskLoader } from "@/features/task-solving/hooks/useTaskLoader"
import type { TaskHydrationSnapshot } from "@/features/task-solving/hooks/useTaskLoader"
import { useDraftState } from "@/features/task-solving/hooks/useDraftState"
import { useLanguageSelection } from "@/features/task-solving/hooks/useLanguageSelection"
import { useCurriculumMirrorLanguage } from "@/features/task-solving/hooks/useCurriculumMirrorLanguage"
import {
  canSwapParallelLanguages,
  getKnownLanguages,
  getLearningLanguages,
  getTaskPrimaryAction,
  resolveKnownLanguageWithReference,
} from "@/features/task-solving/model/studentUiUtils"
import { useExecutionResultState } from "@/features/task-solving/hooks/useExecutionResultState"
import { useFlowchartSubmission } from "@/features/task-solving/hooks/useFlowchartSubmission"
import { useBlockAssemblySubmission } from "@/features/task-solving/hooks/useBlockAssemblySubmission"
import { useCodeSubmission } from "@/features/task-solving/hooks/useCodeSubmission"
import { normalizeBottomTab } from "@/features/task-solving/model/taskHydrationHelpers"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import type { BlockPlacement } from "@/domain/blockAssembly"
import type { FlowCheckDebug, FlowPayload } from "@/shared/types/flow"
import type { PanelError, TestCaseResult } from "@/shared/types/execution"
import { resolveLearningLanguageFromNav, normalizeCurriculumLearningLanguage, isCurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import {
  readStoredLearningLanguage,
  writeStoredLearningLanguage,
} from "@/features/curriculum/curriculumLanguageUi"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import type { TaskDto } from "@/shared/types/task"

type FlowchartSolutionMode = "code" | "flow"

interface UseTaskSolverOptions {
  guestMode?: boolean
  homePath?: string
  taskPathPrefix?: string
  userId?: number | string | null
}

interface TeacherReviewContext {
  submissionId?: number | string
  [key: string]: unknown
}

interface TaskSolverLocationState {
  teacherReview?: TeacherReviewContext | null
}

/** Teacher review submission detail may include id from analytics API. */
interface ReviewSubmissionWithId {
  id?: number | string
  code?: string
  language?: string
  [key: string]: unknown
}

/** Stable public API for TaskPage / StudentTaskWorkspace — do not change keys without migration. */
export interface UseTaskSolverReturn {
  id: string | undefined
  task: TaskDto | null
  isTaskLoading: boolean
  isPedagogyRefreshing: boolean
  taskLoadError: string
  teacherReview: TeacherReviewContext | null
  isTeacherReview: boolean
  activeSubmissionId: number | string | null
  isAlgorithmTask: boolean
  isBlockAssemblyTask: boolean
  reviewSubmission: ReviewSubmissionWithId | null
  reviewLoading: boolean
  navigationMode: ReturnType<typeof useTaskNavigation>["navigationMode"]
  collectionId: ReturnType<typeof useTaskNavigation>["collectionId"]
  manualTaskIds: ReturnType<typeof useTaskNavigation>["manualTaskIds"]
  fetchedCollectionNav: ReturnType<typeof useTaskNavigation>["fetchedCollectionNav"]
  adaptiveLoading: boolean
  handleAdaptiveNext: ReturnType<typeof useTaskNavigation>["handleAdaptiveNext"]
  code: string
  setCode: (code: string) => void
  flow: FlowPayload
  setFlow: (flow: FlowPayload) => void
  resetFlowDraft: ReturnType<typeof useFlowchartSubmission>["resetFlowDraft"]
  flowchartSolutionMode: FlowchartSolutionMode
  swapFlowchartSolutionMode: ReturnType<typeof useLanguageSelection>["swapFlowchartSolutionMode"]
  blockAssemblyCode: string
  blockPlacements: BlockPlacement[]
  setBlockPlacements: (placements: BlockPlacement[]) => void
  blockLanguage: string
  setBlockLanguage: (language: string) => void
  isSubmitting: boolean
  results: TestCaseResult[]
  compilerErrors: PanelError[]
  linterErrors: PanelError[]
  patternErrors: PanelError[]
  flowCheckDebug: FlowCheckDebug | null
  registerGetFlowPayload: ReturnType<typeof useFlowchartSubmission>["registerGetFlowPayload"]
  activeTab: string
  setActiveTab: (tab: string) => void
  bottomTab: string
  setBottomTab: (tab: string) => void
  selectedExampleLanguage: string
  userLanguage: string
  languageOptions: string[]
  handleTaskLanguageChange: ReturnType<typeof useLanguageSelection>["handleTaskLanguageChange"]
  handleUserLanguageChange: ReturnType<typeof useLanguageSelection>["handleUserLanguageChange"]
  swapLanguages: ReturnType<typeof useLanguageSelection>["swapLanguages"]
  runCode: () => Promise<void>
  navigate: NavigateFunction
  guestMode: boolean
  homePath: string
  taskPathPrefix: string
}

/**
 * Student task solve facade — composes task-solving hooks (FE-ARCH-6).
 * Public return shape is stable for TaskPage / StudentTaskWorkspace.
 */
export function useTaskSolver({
  guestMode = false,
  homePath = "/",
  taskPathPrefix = "/tasks",
  userId = null,
}: UseTaskSolverOptions = {}): UseTaskSolverReturn {
  const { executableIds: languageOptions, defaultId } = useLanguages()
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const teacherReviewFromState =
    (location.state as TaskSolverLocationState | null)?.teacherReview ?? null
  const reviewSubmissionParam = searchParams.get("reviewSubmission")
  const teacherReview = useMemo(() => {
    if (teacherReviewFromState?.submissionId) return teacherReviewFromState
    if (reviewSubmissionParam) {
      return { submissionId: reviewSubmissionParam }
    }
    return null
  }, [teacherReviewFromState, reviewSubmissionParam])

  const [code, setCode] = useState("")
  const [flow, setFlow] = useState<FlowPayload>({ flow: [], nodes: [], edges: [] })
  const [blockAssemblyCode, setBlockAssemblyCode] = useState("")
  const [blockPlacements, setBlockPlacements] = useState<BlockPlacement[]>([])
  const [activeTab, setActiveTab] = useState("task")
  const [bottomTab, setBottomTab] = useState("case")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const resumedSubmissionTaskRef = useRef<string | null>(null)
  const applyTaskHydrationRef = useRef<((hydration: TaskHydrationSnapshot) => void) | null>(null)
  const clearExecutionPanelsRef = useRef<(() => void) | null>(null)

  const isTeacherReview = Boolean(teacherReview?.submissionId)

  const resetWorkspaceForTaskLoad = useCallback(() => {
    clearExecutionPanelsRef.current?.()
    setCode("")
    setFlow({ flow: [], nodes: [], edges: [] })
    setBlockAssemblyCode("")
    setBlockPlacements([])
    setActiveTab("task")
    const tabParam = searchParams.get("tab")
    if (teacherReview?.submissionId) setBottomTab("comments")
    else if (tabParam) setBottomTab(normalizeBottomTab(tabParam))
    else setBottomTab("case")
  }, [searchParams, teacherReview?.submissionId])

  const locationState = location.state as TaskSolverLocationState & {
    learningLanguage?: string
    collectionId?: string | number | null
  } | null
  const resolvedLearningLanguage = resolveLearningLanguageFromNav(locationState)
  const userLockedLearningLanguageRef = useRef<CurriculumLearningLanguage | undefined>(
    undefined,
  )

  const readLearningLanguageFromUrl = useCallback((): CurriculumLearningLanguage | undefined => {
    const fromUrl = searchParams.get("learning_language")
    return fromUrl && isCurriculumLearningLanguage(fromUrl) ? fromUrl : undefined
  }, [searchParams])

  const readSourceLanguageFromUrl = useCallback((): CurriculumLearningLanguage | undefined => {
    const fromUrl = searchParams.get("source_language")
    return fromUrl && isCurriculumLearningLanguage(fromUrl) ? fromUrl : undefined
  }, [searchParams])

  const [fetchLearningLanguage, setFetchLearningLanguage] = useState<
    CurriculumLearningLanguage | undefined
  >(
    () =>
      readLearningLanguageFromUrl() ??
      resolvedLearningLanguage ??
      readStoredLearningLanguage(),
  )

  const [fetchSourceLanguage, setFetchSourceLanguage] = useState<string | undefined>(
    () => readSourceLanguageFromUrl(),
  )

  const handleStayOnTaskLanguageChange = useCallback(
    (lang: CurriculumLearningLanguage) => {
      userLockedLearningLanguageRef.current = lang
      setFetchLearningLanguage(lang)
      writeStoredLearningLanguage(lang)
    },
    [],
  )

  useEffect(() => {
    userLockedLearningLanguageRef.current = undefined
    setFetchLearningLanguage(
      readLearningLanguageFromUrl() ??
        resolvedLearningLanguage ??
        readStoredLearningLanguage(),
    )
    setFetchSourceLanguage(readSourceLanguageFromUrl())
  }, [
    id,
    resolvedLearningLanguage,
    readLearningLanguageFromUrl,
    readSourceLanguageFromUrl,
  ])

  const {
    task,
    setTask,
    loadedTaskId,
    isTaskLoading,
    isPedagogyRefreshing,
    taskLoadError,
  } = useTaskLoader({
    taskId: id,
    navigate,
    defaultId,
    languageOptions,
    learningLanguage: fetchLearningLanguage,
    sourceLanguage: fetchSourceLanguage,
    userId: guestMode ? null : userId,
    onLoadStarted: () => {
      resumedSubmissionTaskRef.current = null
    },
    onResetWorkspace: resetWorkspaceForTaskLoad,
    onHydrate: (hydration) => applyTaskHydrationRef.current?.(hydration),
  })

  const isAlgorithmTask = task?.type === "algorithm"
  const isBlockAssemblyTask =
    getTaskPrimaryAction(task) !== "debug" &&
    (task?.type === "block_reorder" ||
      task?.type === "code_assembly" ||
      task?.type === "task_build_from_blocks")

  const {
    navigationMode,
    collectionId,
    manualTaskIds,
    fetchedCollectionNav,
    adaptiveLoading,
    handleAdaptiveNext,
  } = useTaskNavigation({
    taskId: id,
    navigate,
    location,
    taskPathPrefix,
    task,
  })

  const language = useLanguageSelection({
    task,
    isBlockAssemblyTask,
    defaultId,
    setBlockAssemblyCode,
    setBlockPlacements,
    setCode,
  })

  const syncFetchLanguagePair = useCallback((source?: string, target?: string) => {
    const resolvedSource = task && source
      ? resolveKnownLanguageWithReference(task, source)
      : source
    if (resolvedSource && isCurriculumLearningLanguage(resolvedSource)) {
      setFetchSourceLanguage(resolvedSource)
    }
    const normalizedTarget = normalizeCurriculumLearningLanguage(target)
    if (normalizedTarget) {
      setFetchLearningLanguage(normalizedTarget)
    }
  }, [task])

  const mirrorLanguage = useCurriculumMirrorLanguage({
    task,
    userLanguage: language.userLanguage,
    navigate,
    onLearningLanguageChange: language.handleUserLanguageChange,
    onKnownLanguageChange: language.handleTaskLanguageChange,
    onStayOnTaskLanguageChange: handleStayOnTaskLanguageChange,
  })

  const handleKnownLanguageChange = useCallback(
    (nextLanguage: string) => {
      mirrorLanguage.handleKnownLanguageChange(nextLanguage)
      syncFetchLanguagePair(nextLanguage, language.userLanguage)
    },
    [mirrorLanguage, language.userLanguage, syncFetchLanguagePair],
  )

  const handleUserLanguageChange = useCallback(
    (nextLanguage: string) => {
      mirrorLanguage.handleUserLanguageChange(nextLanguage)
      syncFetchLanguagePair(language.selectedExampleLanguage, nextLanguage)
    },
    [mirrorLanguage, language.selectedExampleLanguage, syncFetchLanguagePair],
  )

  const swapLanguages = useCallback(async () => {
    if (!task) {
      language.swapLanguages()
      return
    }
    const knownAvailable = getKnownLanguages(task)
    const learningAvailable = getLearningLanguages(task)
    const known = language.selectedExampleLanguage
    const learning = language.userLanguage
    if (
      !canSwapParallelLanguages(
        known,
        learning,
        knownAvailable,
        learningAvailable,
        task,
      )
    ) {
      return
    }

    language.swapLanguages()
    syncFetchLanguagePair(learning, known)
  }, [task, language, syncFetchLanguagePair])

  const execution = useExecutionResultState({
    taskId: id,
    task,
    setTask,
    loadedTaskId,
    isTaskLoading,
    guestMode,
    isTeacherReview,
    teacherReview,
    isBlockAssemblyTask,
    code,
    userLanguage: language.userLanguage,
    flowchartSolutionMode: language.flowchartSolutionMode,
    blockAssemblyCode,
    blockPlacements,
    blockLanguage: language.blockLanguage,
    bottomTab,
    setBottomTab,
    setUserLanguage: language.setUserLanguage,
    setCode,
    onResumeStartedRef: resumedSubmissionTaskRef,
  })

  clearExecutionPanelsRef.current = execution.clearExecutionPanels

  applyTaskHydrationRef.current = (hydration: TaskHydrationSnapshot) => {
    execution.clearExecutionPanels()
    const locked = userLockedLearningLanguageRef.current
    const languageHydration: TaskHydrationSnapshot = locked
      ? { ...hydration, userLanguage: locked, blockLanguage: locked }
      : hydration

    setActiveTab(languageHydration.activeTab)
    setBottomTab(languageHydration.bottomTab)
    if (!locked) {
      setCode(languageHydration.code)
      setFlow(languageHydration.flow)
      setBlockAssemblyCode(languageHydration.blockAssemblyCode)
      setBlockPlacements(languageHydration.blockPlacements)
    }
    language.applyLanguageHydration(languageHydration)
    if (!locked) {
      syncFetchLanguagePair(
        languageHydration.selectedExampleLanguage,
        languageHydration.userLanguage,
      )
    }
  }

  useDraftState({
    taskId: id,
    task,
    loadedTaskId,
    isTaskLoading,
    code,
    flow,
    blockAssemblyCode,
    blockPlacements,
    blockLanguage: language.blockLanguage,
    selectedExampleLanguage: language.selectedExampleLanguage,
    userLanguage: language.userLanguage,
    activeTab,
    bottomTab,
    flowchartSolutionMode: language.flowchartSolutionMode,
  })

  const reviewSubmission = execution.reviewSubmission as ReviewSubmissionWithId | null

  const submissionFromNotification = searchParams.get("submission")
  const activeSubmissionId =
    teacherReview?.submissionId ??
    reviewSubmission?.id ??
    (submissionFromNotification ? submissionFromNotification : null) ??
    execution.studentSubmissionId ??
    null

  const flowchart = useFlowchartSubmission({
    taskId: id,
    task,
    flow,
    setFlow,
    setTask,
    setBottomTab,
    applyExecutionResult: execution.applyExecutionResult,
    setCompilerErrors: execution.setCompilerErrors,
    setPatternErrors: execution.setPatternErrors,
    setLinterErrors: execution.setLinterErrors,
    setResults: execution.setResults,
    setFlowCheckDebug: execution.setFlowCheckDebug,
  })

  const blockSubmit = useBlockAssemblySubmission({
    taskId: id,
    task,
    guestMode,
    blockLanguage: language.blockLanguage,
    userLanguage: language.userLanguage,
    blockAssemblyCode,
    blockPlacements,
    setTask,
    setBottomTab,
    applyExecutionResult: execution.applyExecutionResult,
    setCompilerErrors: execution.setCompilerErrors,
    setLinterErrors: execution.setLinterErrors,
    setPatternErrors: execution.setPatternErrors,
    setResults: execution.setResults,
  })

  const codeSubmit = useCodeSubmission({
    taskId: id,
    task,
    guestMode,
    code,
    userLanguage: language.userLanguage,
    applyExecutionResult: execution.applyExecutionResult,
    setBottomTab,
    setCompilerErrors: execution.setCompilerErrors,
    setLinterErrors: execution.setLinterErrors,
    setPatternErrors: execution.setPatternErrors,
  })

  useEffect(() => {
    const tab = searchParams.get("tab")
    if (tab) setBottomTab(normalizeBottomTab(tab))
  }, [searchParams, id])

  useEffect(() => {
    if (isTeacherReview) setBottomTab("comments")
  }, [isTeacherReview, teacherReview?.submissionId])

  const runCode = async () => {
    setIsSubmitting(true)
    try {
      if (isFlowchartTask(task) && language.flowchartSolutionMode === "flow") {
        await flowchart.runFlowModeSubmit()
        return
      }
      if (isFlowchartTask(task)) {
        if (flowchart.validateFlowchartCodeMode(code, language.userLanguage)) return
      }
      if (isBlockAssemblyTask) {
        await blockSubmit.runBlockAssemblySubmit()
        return
      }
      await codeSubmit.runCodeSubmit()
    } catch (error: unknown) {
      codeSubmit.handleSubmitError(error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return {
    id,
    task,
    isTaskLoading,
    isPedagogyRefreshing,
    taskLoadError,
    teacherReview,
    isTeacherReview,
    activeSubmissionId,
    isAlgorithmTask,
    isBlockAssemblyTask,
    reviewSubmission,
    reviewLoading: execution.reviewLoading,
    navigationMode,
    collectionId,
    manualTaskIds,
    fetchedCollectionNav,
    adaptiveLoading,
    handleAdaptiveNext,
    code,
    setCode,
    flow,
    setFlow,
    resetFlowDraft: flowchart.resetFlowDraft,
    flowchartSolutionMode: language.flowchartSolutionMode,
    swapFlowchartSolutionMode: language.swapFlowchartSolutionMode,
    blockAssemblyCode,
    blockPlacements,
    setBlockPlacements,
    blockLanguage: language.blockLanguage,
    setBlockLanguage: language.setBlockLanguage,
    isSubmitting,
    results: execution.results,
    compilerErrors: execution.compilerErrors,
    linterErrors:
      code.trim() && (!isFlowchartTask(task) || language.flowchartSolutionMode === "code")
        ? filterReportErrors(execution.linterErrors)
        : [],
    patternErrors: execution.patternErrors,
    flowCheckDebug: execution.flowCheckDebug,
    registerGetFlowPayload: flowchart.registerGetFlowPayload,
    activeTab,
    setActiveTab,
    bottomTab,
    setBottomTab,
    selectedExampleLanguage: language.selectedExampleLanguage,
    userLanguage: language.userLanguage,
    languageOptions,
    handleTaskLanguageChange: handleKnownLanguageChange,
    handleUserLanguageChange: handleUserLanguageChange,
    swapLanguages,
    runCode,
    navigate,
    guestMode,
    homePath,
    taskPathPrefix,
  }
}
