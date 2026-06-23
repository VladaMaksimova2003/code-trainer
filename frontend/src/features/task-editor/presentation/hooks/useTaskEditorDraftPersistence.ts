import { useEffect, useRef, useState } from "react"
import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { ensureDraftBlockEditor } from "@/features/task-editor/domain/blockEditor"
import { normalizeIoValue, IoValueKind } from "@/features/task-editor/domain/ioValue"
import { ensureValidAccessToken } from "@/shared/api/auth"
import { createEmptyAssignmentDraft } from "@/features/task-editor/application/use-cases/clearAssignmentDraft"

const EDIT_DRAFT_PREFIX = "task-editor-edit-draft-v1"
const EDIT_RELOAD_FLAG_PREFIX = "task-editor-edit-reloading-v1"

function editDraftKey(taskId: string): string {
  return `${EDIT_DRAFT_PREFIX}:${taskId}`
}

function editReloadFlagKey(taskId: string): string {
  return `${EDIT_RELOAD_FLAG_PREFIX}:${taskId}`
}

export function isPageReload(): boolean {
  if (typeof performance === "undefined") return false
  const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined
  if (nav?.type === "reload") return true
  const legacy = (performance as Performance & { navigation?: { type?: number } }).navigation
  return legacy?.type === 1
}

export function isMeaningfulEditDraft(draft: TaskDraft | null | undefined): boolean {
  if (!draft) return false
  return Boolean(
    draft.title?.trim() ||
      draft.description?.trim() ||
      draft.code?.code?.trim() ||
      (draft.testCases?.length ?? 0) > 0,
  )
}

export function loadEditDraftAutosave(taskId: string): TaskDraft | null {
  try {
    const raw = sessionStorage.getItem(editDraftKey(taskId))
    if (!raw) return null
    const parsed = JSON.parse(raw) as Partial<TaskDraft>
    const base = { ...createEmptyAssignmentDraft(), ...parsed }
    base.testCases = (parsed.testCases ?? base.testCases ?? []).map((tc, index) => ({
      ...tc,
      id: tc.id || `tc-${index}`,
      input: normalizeIoValue((tc as { input?: unknown }).input ?? ""),
      expectedOutput: normalizeIoValue(
        (tc as { expectedOutput?: unknown }).expectedOutput ?? "",
      ),
    }))
    base.ioSchema = parsed.ioSchema ?? base.ioSchema ?? {
      inputFormat: IoValueKind.SCALAR,
      outputFormat: IoValueKind.SCALAR,
    }
    const migrated = ensureDraftBlockEditor(base)
    return isMeaningfulEditDraft(migrated) ? migrated : null
  } catch {
    return null
  }
}

export function saveEditDraftAutosave(taskId: string, draft: TaskDraft): void {
  try {
    sessionStorage.setItem(editDraftKey(taskId), JSON.stringify(draft))
  } catch {
    /* quota / private mode */
  }
}

export function clearEditDraftAutosave(taskId: string): void {
  sessionStorage.removeItem(editDraftKey(taskId))
  sessionStorage.removeItem(editReloadFlagKey(taskId))
}

type Options = {
  isEditMode: boolean
  taskId: string | undefined
  serverDraft: TaskDraft | undefined
  draft: TaskDraft
  setDraft: (draft: TaskDraft) => void
  autosaveCreateDraft: () => void
  loadCreateDraft: () => void
}

/**
 * Create mode: localStorage autosave (existing behaviour).
 * Edit mode: sessionStorage — survives F5, cleared when leaving without save.
 */
export function useTaskEditorDraftPersistence({
  isEditMode,
  taskId,
  serverDraft,
  draft,
  setDraft,
  autosaveCreateDraft,
  loadCreateDraft,
}: Options): { isDraftHydrated: boolean } {
  const [isDraftHydrated, setIsDraftHydrated] = useState(!isEditMode)
  useEffect(() => {
    if (isEditMode) return
    loadCreateDraft()
  }, [isEditMode, loadCreateDraft])
  const hydratedRef = useRef(false)
  const taskIdRef = useRef(taskId)

  if (taskIdRef.current !== taskId) {
    taskIdRef.current = taskId
    hydratedRef.current = false
    setIsDraftHydrated(!isEditMode)
  }

  useEffect(() => {
    if (isEditMode) return
    autosaveCreateDraft()
  }, [draft, isEditMode, autosaveCreateDraft])

  useEffect(() => {
    if (!isEditMode || !taskId || !hydratedRef.current) return
    saveEditDraftAutosave(taskId, draft)
  }, [draft, isEditMode, taskId])

  useEffect(() => {
    if (!isEditMode || !taskId) {
      if (!isEditMode) {
        hydratedRef.current = false
      }
      return
    }

    if (hydratedRef.current) return

    const cached = loadEditDraftAutosave(taskId)
    if (isPageReload() && cached) {
      setDraft(cached)
      hydratedRef.current = true
      setIsDraftHydrated(true)
      return
    }

    if (serverDraft && String(serverDraft.id ?? "") === String(taskId)) {
      setDraft(serverDraft)
      hydratedRef.current = true
      setIsDraftHydrated(true)
    }
  }, [isEditMode, taskId, serverDraft, setDraft])

  useEffect(() => {
    if (!isEditMode || !taskId) return

    const markReload = () => {
      sessionStorage.setItem(editReloadFlagKey(taskId), "1")
    }
    window.addEventListener("beforeunload", markReload)

    return () => {
      window.removeEventListener("beforeunload", markReload)
      const currentTaskId = taskId
      window.setTimeout(() => {
        const reloading = sessionStorage.getItem(editReloadFlagKey(currentTaskId)) === "1"
        sessionStorage.removeItem(editReloadFlagKey(currentTaskId))
        if (!reloading) {
          clearEditDraftAutosave(currentTaskId)
        }
      }, 0)
    }
  }, [isEditMode, taskId])

  useEffect(() => {
    if (!isEditMode) return

    const refresh = () => {
      void ensureValidAccessToken().catch(() => {
        /* refreshAuthTokens handles session-expired event */
      })
    }

    refresh()
    const timer = window.setInterval(refresh, 5 * 60 * 1000)
    return () => window.clearInterval(timer)
  }, [isEditMode])

  return { isDraftHydrated }
}
