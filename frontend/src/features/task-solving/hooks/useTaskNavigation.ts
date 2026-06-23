import { useCallback, useEffect, useState } from "react"
import type { Location, NavigateFunction } from "react-router-dom"
import {
  fetchAllCppTaskIds,
  fetchAllCsharpTaskIds,
  fetchAllJavaTaskIds,
  fetchAllPascalTaskIds,
  fetchAllPythonTaskIds,
  fetchCurriculumCollectionNavigation,
} from "@/features/curriculum/api/curriculumApi"
import { getCatalogNavigation, getNextRecommendation } from "@/features/tasks/api/recommendationsApi"
import {
  isCppCurriculumTask,
  isCsharpCurriculumTask,
  isJavaCurriculumTask,
  isPascalCurriculumTask,
  isPythonCurriculumTask,
} from "@/features/task-solving/model/studentUiUtils"
import type { TaskDto } from "@/shared/types/task"
import {
  readNavigationContext,
  writeNavigationContext,
} from "@/features/task-solving/model/navigationContext"
import {
  buildAdaptiveNavigateState,
  buildAdaptiveNavigationContext,
  resolveMergedNavigationContext,
} from "@/features/task-solving/model/taskNavigationHelpers"

/** Route state keys for collection vs adaptive navigation (react-router `location.state`). */
type TaskNavigationMode = "adaptive" | "manual" | "curriculum" | (string & {})

interface TaskNavigationLocationState {
  navigationMode?: TaskNavigationMode
  collectionId?: number | string | null
  returnTo?: string
}

interface UseTaskNavigationOptions {
  taskId: string | undefined
  navigate: NavigateFunction
  location: Location
  taskPathPrefix?: string
  task?: TaskDto | null
}

/** API payloads that expose ordered task ids for prev/next header navigation. */
interface TaskIdsNavigationPayload {
  task_ids?: number[]
  prev_task_id?: number | null
  prev_collection_id?: string | number | null
  next_task_id?: number | null
  next_collection_id?: string | number | null
  course_completed?: boolean
  collection_id?: string | number | null
  collection_title_ru?: string
  task_index?: number
  total_tasks?: number
}

interface NextRecommendationPayload {
  task_id?: number
}

function asNavigationLocationState(state: unknown): TaskNavigationLocationState | undefined {
  if (state == null || typeof state !== "object") return undefined
  return state as TaskNavigationLocationState
}

/**
 * Solver-side task navigation (FE-ARCH-6.1).
 */
export function useTaskNavigation({
  taskId,
  navigate,
  location,
  taskPathPrefix = "/tasks",
  task = null,
}: UseTaskNavigationOptions) {
  const [navigationMode, setNavigationMode] = useState<TaskNavigationMode>("adaptive")
  const [collectionId, setCollectionId] = useState<number | string | null>(null)
  const [manualTaskIds, setManualTaskIds] = useState<number[]>([])
  const [fetchedCollectionNav, setFetchedCollectionNav] =
    useState<TaskIdsNavigationPayload | null>(null)
  const [adaptiveLoading, setAdaptiveLoading] = useState(false)

  useEffect(() => {
    const merged = resolveMergedNavigationContext(
      asNavigationLocationState(location.state),
      readNavigationContext(),
    )
    setNavigationMode(merged.mode)
    setCollectionId(merged.collectionId)
    writeNavigationContext(merged)
  }, [location.state, taskId])

  const curriculumNav = (task?.curriculum as { navigation?: { collection_id?: string | number } } | undefined)
    ?.navigation
  const effectiveCollectionId =
    collectionId ?? curriculumNav?.collection_id ?? null
  const isPascalCurriculum = isPascalCurriculumTask(task)
  const isPythonCurriculum = isPythonCurriculumTask(task)
  const isCppCurriculum = isCppCurriculumTask(task)
  const isJavaCurriculum = isJavaCurriculumTask(task)
  const isCsharpCurriculum = isCsharpCurriculumTask(task)
  const isCurriculumTask =
    isPascalCurriculum ||
    isPythonCurriculum ||
    isCppCurriculum ||
    isJavaCurriculum ||
    isCsharpCurriculum
  const effectiveNavigationMode =
    navigationMode === "curriculum" || navigationMode === "manual"
      ? navigationMode
      : curriculumNav?.collection_id || isCurriculumTask
        ? "curriculum"
        : navigationMode

  useEffect(() => {
    if (effectiveNavigationMode === "manual" && effectiveCollectionId != null) {
      let cancelled = false
      getCatalogNavigation(effectiveCollectionId, Number(taskId))
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) {
            setManualTaskIds(data?.task_ids ?? [])
            setFetchedCollectionNav(data ?? null)
          }
        })
        .catch(() => {
          if (!cancelled) {
            setManualTaskIds([])
            setFetchedCollectionNav(null)
          }
        })
      return () => {
        cancelled = true
      }
    }
    if (effectiveNavigationMode === "curriculum" && effectiveCollectionId != null) {
      let cancelled = false
      fetchCurriculumCollectionNavigation(effectiveCollectionId, Number(taskId))
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) {
            setManualTaskIds(data?.task_ids ?? [])
            setFetchedCollectionNav(data ?? null)
          }
        })
        .catch(() => {
          if (!cancelled) {
            setManualTaskIds([])
            setFetchedCollectionNav(null)
          }
        })
      return () => {
        cancelled = true
      }
    }
    if (effectiveNavigationMode === "adaptive" && isPascalCurriculum) {
      let cancelled = false
      fetchAllPascalTaskIds()
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) setManualTaskIds(data?.task_ids ?? [])
        })
        .catch(() => {
          if (!cancelled) setManualTaskIds([])
        })
      return () => {
        cancelled = true
      }
    }
    if (effectiveNavigationMode === "adaptive" && isPythonCurriculum) {
      let cancelled = false
      fetchAllPythonTaskIds()
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) setManualTaskIds(data?.task_ids ?? [])
        })
        .catch(() => {
          if (!cancelled) setManualTaskIds([])
        })
      return () => {
        cancelled = true
      }
    }
    if (effectiveNavigationMode === "adaptive" && isCppCurriculum) {
      let cancelled = false
      fetchAllCppTaskIds()
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) setManualTaskIds(data?.task_ids ?? [])
        })
        .catch(() => {
          if (!cancelled) setManualTaskIds([])
        })
      return () => {
        cancelled = true
      }
    }
    if (effectiveNavigationMode === "adaptive" && isJavaCurriculum) {
      let cancelled = false
      fetchAllJavaTaskIds()
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) setManualTaskIds(data?.task_ids ?? [])
        })
        .catch(() => {
          if (!cancelled) setManualTaskIds([])
        })
      return () => {
        cancelled = true
      }
    }
    if (effectiveNavigationMode === "adaptive" && isCsharpCurriculum) {
      let cancelled = false
      fetchAllCsharpTaskIds()
        .then((data: TaskIdsNavigationPayload | undefined) => {
          if (!cancelled) setManualTaskIds(data?.task_ids ?? [])
        })
        .catch(() => {
          if (!cancelled) setManualTaskIds([])
        })
      return () => {
        cancelled = true
      }
    }
    setManualTaskIds([])
    setFetchedCollectionNav(null)
    return undefined
  }, [
    effectiveNavigationMode,
    effectiveCollectionId,
    taskId,
    isPascalCurriculum,
    isPythonCurriculum,
    isCppCurriculum,
    isJavaCurriculum,
    isCsharpCurriculum,
  ])

  const handleAdaptiveNext = useCallback(async () => {
    setAdaptiveLoading(true)
    try {
      const recommendation = (await getNextRecommendation(
        Number(taskId),
      )) as NextRecommendationPayload | undefined
      if (recommendation?.task_id) {
        const routeState = buildAdaptiveNavigateState()
        navigate(`${taskPathPrefix}/${recommendation.task_id}`, {
          state: routeState,
        })
        writeNavigationContext(buildAdaptiveNavigationContext())
      }
    } finally {
      setAdaptiveLoading(false)
    }
  }, [taskId, navigate, taskPathPrefix])

  return {
    navigationMode: effectiveNavigationMode,
    collectionId: effectiveCollectionId,
    manualTaskIds,
    fetchedCollectionNav,
    adaptiveLoading,
    handleAdaptiveNext,
  }
}
