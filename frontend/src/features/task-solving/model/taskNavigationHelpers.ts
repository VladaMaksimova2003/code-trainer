/**
 * Pure task navigation helpers (solver + header logic).
 * Used by useTaskNavigation and unit-tested without React.
 */

export interface NavigationLocationState {
  navigationMode?: string
  collectionId?: number | string | null
  returnTo?: string
}

export interface StoredNavigationContext {
  mode?: string
  collectionId?: number | string | null
}

import type {
  CurriculumCollectionNavigationDto,
  CurriculumCollectionSummary,
  CurriculumNextDto,
} from "@/shared/types/curriculum"

export type CollectionNavPayload = CurriculumCollectionNavigationDto

export type PrevTaskAction =
  | { kind: "task"; taskId: number; collectionId: number | string | null }
  | null

export type NextTaskAction =
  | { kind: "task"; taskId: number; collectionId: number | string | null }
  | { kind: "returnTo" }
  | { kind: "adaptive" }
  | { kind: "curriculumNext" }
  | null

export type CurriculumNextPayload = CurriculumNextDto

export function resolveMergedNavigationContext(
  locationState: NavigationLocationState | null | undefined,
  storedContext: StoredNavigationContext = { mode: "adaptive", collectionId: null },
): NavigationContextShape {
  const fromState = locationState?.navigationMode
  const fromCollection = locationState?.collectionId ?? null
  return {
    mode: fromState ?? storedContext.mode ?? "adaptive",
    collectionId: fromCollection ?? storedContext.collectionId ?? null,
  }
}

export interface NavigationContextShape {
  mode: string
  collectionId: number | string | null
}

export function resolveReturnTo(
  locationReturnTo: string | null | undefined,
  curriculumReturnPath: string | null | undefined,
): string | null {
  return locationReturnTo || curriculumReturnPath || null
}

export function resolveBackTarget(returnTo: string | null | undefined, fallbackPath = "/"): string {
  return returnTo || fallbackPath
}

export function resolveBackLabel(returnTo: string | null | undefined): string {
  if (returnTo?.startsWith("/learn/")) return "К сборнику"
  if (returnTo === "/" || returnTo === "") return "К списку задач"
  if (returnTo) return "Назад"
  return "Каталог"
}

export function resolveOrderedTaskIds(
  collectionNavTaskIds: number[] | null | undefined,
  manualTaskIds: number[] = [],
): number[] {
  return collectionNavTaskIds?.length ? collectionNavTaskIds : manualTaskIds
}

export function isCollectionNavigation(
  navigationMode: string,
  orderedTaskIds: number[],
  hasCurriculumTaskIds: boolean,
): boolean {
  return (
    orderedTaskIds.length > 0 &&
    (navigationMode === "manual" ||
      navigationMode === "curriculum" ||
      Boolean(hasCurriculumTaskIds))
  )
}

export function findTaskIndex(orderedTaskIds: number[], taskId: string | number): number {
  return orderedTaskIds.findIndex((itemId) => itemId === Number(taskId))
}

export function resolveHasPrev(
  isCollectionNav: boolean,
  collectionNav: CollectionNavPayload | null | undefined,
  index: number,
): boolean {
  if (collectionNav?.prev_task_id != null) return true
  return isCollectionNav && index > 0
}

export function resolveHasNext(
  isCollectionNav: boolean,
  collectionNav: CollectionNavPayload | null | undefined,
  index: number,
  orderedTaskIdsLength: number,
): boolean {
  return (
    isCollectionNav &&
    (collectionNav?.next_task_id != null ||
      (index >= 0 && index < orderedTaskIdsLength - 1) ||
      Boolean(collectionNav?.course_completed))
  )
}

/** Previous task navigation decision (matches StudentTaskHeader goPrev). */
export function resolvePrevTaskAction(
  collectionNav: CollectionNavPayload | null | undefined,
  index: number,
  orderedTaskIds: number[],
): PrevTaskAction {
  if (collectionNav?.prev_task_id != null) {
    return {
      kind: "task",
      taskId: collectionNav.prev_task_id,
      collectionId: collectionNav.prev_collection_id ?? null,
    }
  }
  if (index > 0) {
    return {
      kind: "task",
      taskId: orderedTaskIds[index - 1],
      collectionId: null,
    }
  }
  return null
}

/** Next task navigation decision before async fallbacks (matches StudentTaskHeader goNext). */
export function resolveNextTaskAction({
  collectionNav,
  index,
  orderedTaskIds,
  hasAdaptiveNext,
}: {
  collectionNav: CollectionNavPayload | null | undefined
  index: number
  orderedTaskIds: number[]
  hasAdaptiveNext: boolean
}): NextTaskAction {
  if (collectionNav?.next_task_id != null) {
    return {
      kind: "task",
      taskId: collectionNav.next_task_id,
      collectionId: collectionNav.next_collection_id ?? null,
    }
  }
  if (index >= 0 && index < orderedTaskIds.length - 1) {
    return {
      kind: "task",
      taskId: orderedTaskIds[index + 1],
      collectionId: null,
    }
  }
  if (collectionNav?.course_completed) {
    return { kind: "returnTo" }
  }
  if (hasAdaptiveNext) {
    return { kind: "adaptive" }
  }
  return { kind: "curriculumNext" }
}

/** Derive global continue payload from `/curriculum/collections` summaries. */
export function deriveGlobalCurriculumNext(
  collections: CurriculumCollectionSummary[] | null | undefined,
): CurriculumNextDto | null {
  if (!collections?.length) {
    return {
      next_task: null,
      collection: null,
      completed: true,
      button_label: "Все темы пройдены",
      progress: { total_tasks: 0, passed_tasks: 0, progress_percent: 0 },
    }
  }

  let totalTasks = 0
  let passedTasks = 0
  let firstIncomplete: CurriculumCollectionSummary | null = null

  for (const item of collections) {
    totalTasks += item.progress?.total_tasks ?? 0
    passedTasks += item.progress?.passed_tasks ?? 0
    if (!firstIncomplete && !item.completed) {
      firstIncomplete = item
    }
  }

  const progressPercent = totalTasks > 0 ? Math.round((1000 * passedTasks) / totalTasks) / 10 : 0
  const allCompleted = passedTasks >= totalTasks && totalTasks > 0
  const ref = firstIncomplete ?? collections[0]
  const buttonLabel =
    passedTasks <= 0
      ? "Начать обучение"
      : allCompleted && !firstIncomplete
        ? "Повторить обучение"
        : "Продолжить обучение"

  return {
    next_task: ref.next_task ?? null,
    collection: {
      collection_id: ref.collection_id,
      language: ref.language,
      chapter_key: ref.chapter_key,
      learning_concept_id: ref.learning_concept_id,
      title_ru: ref.title_ru,
      route_path: ref.route_path,
    },
    completed: firstIncomplete ? false : allCompleted,
    button_label: buttonLabel,
    progress: {
      total_tasks: totalTasks,
      passed_tasks: passedTasks,
      progress_percent: progressPercent,
    },
  }
}

/** After fetchCurriculumNext() response. */
export function resolveCurriculumNextAction(
  payload: CurriculumNextPayload | null | undefined,
  returnToFallback = "/",
): { kind: "returnTo"; path: string } | { kind: "task"; taskId: number; collectionId: number | string | null } | null {
  if (payload?.completed) {
    return { kind: "returnTo", path: returnToFallback }
  }
  if (payload?.next_task?.task_id) {
    return {
      kind: "task",
      taskId: payload.next_task.task_id,
      collectionId: payload?.collection?.collection_id ?? null,
    }
  }
  return null
}

export function buildTaskRouteState({
  navigationMode,
  collectionId,
  collectionNavCollectionId,
  returnTo,
  nextCollectionId = null,
}: {
  navigationMode: string
  collectionId?: number | string | null
  collectionNavCollectionId?: number | string | null
  returnTo?: string | null
  nextCollectionId?: number | string | null
}) {
  return {
    navigationMode: navigationMode === "manual" ? "manual" : "curriculum",
    collectionId: nextCollectionId || collectionId || collectionNavCollectionId || null,
    returnTo,
  }
}

export function buildAdaptiveNavigateState() {
  return { navigationMode: "adaptive", collectionId: null }
}

/** Session storage shape for writeNavigationContext. */
export function buildAdaptiveNavigationContext(): NavigationContextShape {
  return { mode: "adaptive", collectionId: null }
}
