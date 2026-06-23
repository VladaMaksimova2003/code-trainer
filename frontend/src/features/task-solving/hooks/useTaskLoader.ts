import { useEffect, useRef, useState } from "react"
import type { NavigateFunction } from "react-router-dom"
import { useTaskDetail } from "@/shared/hooks/useTaskDetail"
import { readDraft, resolveDraftForTask } from "@/features/task-solving/model/taskDraftHelpers"
import { resolveTaskHydration } from "@/features/task-solving/model/taskHydrationHelpers"
import type { BlockPlacement } from "@/domain/blockAssembly"
import type { FlowPayload } from "@/shared/types/flow"
import type { TaskDto } from "@/shared/types/task"

const TASK_LOAD_ERROR = "Задача временно недоступна. Черновик сохранён."

type FlowchartSolutionMode = "code" | "flow"

function formatTaskLoadError(error: unknown): string {
  const err = error as {
    response?: { status?: number; data?: { detail?: string } }
    message?: string
  }
  const status = err?.response?.status
  const detail = err?.response?.data?.detail
  if (typeof detail === "string" && detail.trim()) {
    return detail
  }
  if (status === 404) {
    return "Задача не найдена или недоступна."
  }
  if (status === 401 || status === 403) {
    return "Нет доступа к задаче. Войдите снова."
  }
  if (status === 502 || status === 503 || status === 504) {
    return "Сервер проверки временно недоступен. Попробуйте позже."
  }
  if (err?.message?.includes("Network Error")) {
    return "Не удалось связаться с сервером. Проверьте подключение."
  }
  return TASK_LOAD_ERROR
}

/** Snapshot from `resolveTaskHydration` applied to workspace state. */
export interface TaskHydrationSnapshot {
  activeTab: string
  bottomTab: string
  code: string
  flow: FlowPayload
  blockAssemblyCode: string
  blockPlacements: BlockPlacement[]
  blockLanguage: string
  selectedExampleLanguage: string
  userLanguage: string
  flowchartSolutionMode: FlowchartSolutionMode
}

interface UseTaskLoaderOptions {
  taskId: string | undefined
  navigate: NavigateFunction
  defaultId: string
  languageOptions: string[]
  learningLanguage?: string
  sourceLanguage?: string
  userId?: number | string | null
  onLoadStarted?: () => void
  onResetWorkspace?: () => void
  onHydrate?: (hydration: TaskHydrationSnapshot) => void
}

/**
 * Task fetch + hydration (FE-ARCH-6.2).
 * Workspace field setters stay in useTaskSolver via onResetWorkspace / onHydrate callbacks.
 */
export function useTaskLoader({
  taskId,
  navigate,
  defaultId,
  languageOptions,
  learningLanguage,
  sourceLanguage,
  userId = null,
  onLoadStarted,
  onResetWorkspace,
  onHydrate,
}: UseTaskLoaderOptions) {
  const {
    data,
    isLoading,
    isFetching,
    isError,
    error,
  } = useTaskDetail(taskId, learningLanguage, userId, sourceLanguage)
  const [task, setTask] = useState<TaskDto | null>(null)
  const [loadedTaskId, setLoadedTaskId] = useState<string | null>(null)
  const loadedPairRef = useRef<{
    taskId: string | null
    learning?: string
    source?: string
  }>({ taskId: null })
  const loadedTaskIdRef = useRef<string | null>(null)
  const onLoadStartedRef = useRef(onLoadStarted)
  const onResetWorkspaceRef = useRef(onResetWorkspace)
  const onHydrateRef = useRef(onHydrate)

  useEffect(() => {
    onLoadStartedRef.current = onLoadStarted
  }, [onLoadStarted])

  useEffect(() => {
    onResetWorkspaceRef.current = onResetWorkspace
  }, [onResetWorkspace])

  useEffect(() => {
    onHydrateRef.current = onHydrate
  }, [onHydrate])

  const fetchSettled = Boolean(taskId) && !isLoading && !isFetching
  const idMismatch =
    fetchSettled &&
    Boolean(data) &&
    String((data as TaskDto).id) !== String(taskId)
  const missingPayload = fetchSettled && !isError && !data
  const loadFailed = isError || idMismatch || missingPayload

  const taskLoadError = isError
    ? formatTaskLoadError(error)
    : idMismatch
      ? "Сервер вернул некорректный ответ для задачи. Обновите страницу."
      : missingPayload
        ? "Не удалось загрузить задачу."
        : ""

  useEffect(() => {
    if (!taskId) {
      setTask(null)
      setLoadedTaskId(null)
      loadedTaskIdRef.current = null
      loadedPairRef.current = { taskId: null }
      return
    }
    onLoadStartedRef.current?.()
    onResetWorkspaceRef.current?.()
    setTask(null)
    setLoadedTaskId(null)
    loadedTaskIdRef.current = null
    loadedPairRef.current = { taskId: null }
  }, [taskId])

  useEffect(() => {
    if (!data || !taskId || String(data.id) !== String(taskId)) return

    const prev = loadedPairRef.current
    const isPairRefetch =
      prev.taskId === String(taskId) &&
      loadedTaskIdRef.current === String(taskId) &&
      (prev.learning !== learningLanguage || prev.source !== sourceLanguage)

    loadedPairRef.current = {
      taskId: String(taskId),
      learning: learningLanguage,
      source: sourceLanguage,
    }

    if (isPairRefetch) {
      setTask(data)
      return
    }

    const storedDraft = readDraft(taskId)
    const draft = resolveDraftForTask(storedDraft, data)
    const hydration = resolveTaskHydration(data, draft, {
      defaultId,
      languageOptions,
      preferLearningLanguage: learningLanguage,
    }) as TaskHydrationSnapshot
    onHydrateRef.current?.(hydration)
    setTask(data)
    const nextLoadedId = String(taskId)
    setLoadedTaskId(nextLoadedId)
    loadedTaskIdRef.current = nextLoadedId
  }, [data, taskId, defaultId, languageOptions, learningLanguage, sourceLanguage])

  const hasTaskForId = Boolean(task) && loadedTaskId === String(taskId)
  const isTaskLoading =
    Boolean(taskId) &&
    !loadFailed &&
    !hasTaskForId &&
    (isLoading || isFetching)
  const isPedagogyRefreshing = hasTaskForId && Boolean(taskId) && isFetching

  return {
    task,
    setTask,
    loadedTaskId,
    isTaskLoading,
    isPedagogyRefreshing,
    taskLoadError,
  }
}
