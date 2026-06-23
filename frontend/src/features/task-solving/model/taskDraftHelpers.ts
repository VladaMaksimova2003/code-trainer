import { getFlowDraftKey } from "@/widgets/BlockEditor/lib/flowInitialState"
import type { BlockPlacement } from "@/domain/blockAssembly"
import type { FlowPayload } from "@/shared/types/flow"
import type { TaskDto } from "@/shared/types/task"

export const TASK_DRAFT_STORAGE_PREFIX = "task-draft:"

export interface TaskDraftRecord {
  taskSignature?: string
  flowDraftKey?: string
  activeTab?: string
  bottomTab?: string
  code?: string
  flow?: FlowPayload
  blockAssemblyCode?: string
  blockPlacements?: BlockPlacement[]
  blockLanguage?: string
  selectedExampleLanguage?: string
  userLanguage?: string
  flowchartSolutionMode?: string
  [key: string]: unknown
}

export interface DraftStorage {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
}

export function getDraftStorageKey(taskId: string | number): string {
  return `${TASK_DRAFT_STORAGE_PREFIX}${taskId}`
}

export function getTaskDraftSignature(taskData: TaskDto | null | undefined): string {
  if (!taskData) return ""
  const codeExamples = taskData.code_examples as Record<string, unknown> | undefined
  const curriculum = taskData.curriculum as Record<string, unknown> | undefined
  const showcase = codeExamples?.curriculum_showcase as Record<string, unknown> | undefined
  const teacherAssemblyOverride = Boolean(
    taskData.teacher_assembly_override || codeExamples?.teacher_assembly_override,
  )
  const starters: Record<string, string> = {}
  for (const lang of ["pascal", "python", "cpp", "csharp", "java"]) {
    const buggyKey = `buggy_${lang}`
    const raw = teacherAssemblyOverride
      ? (codeExamples?.[buggyKey] ?? curriculum?.[buggyKey])
      : (codeExamples?.[buggyKey] ??
          curriculum?.[buggyKey] ??
          curriculum?.[`starter_${lang}`] ??
          showcase?.[`starter_${lang}`] ??
          (taskData as Record<string, unknown>)[`starter_${lang}`])
    if (raw != null && String(raw).trim()) {
      starters[buggyKey] = String(raw)
    }
  }
  return JSON.stringify({
    id: taskData.id,
    type: taskData.type,
    template: taskData.template ?? "",
    blocks: taskData.blocks ?? [],
    language: taskData.language ?? "",
    variants: taskData.language_variants ?? null,
    codeExamples: taskData.code_examples ?? null,
    starters,
    teacherAssemblyOverride,
    flowDraftKey: getFlowDraftKey(taskData),
  })
}

export function readDraft(
  taskId: string | number | undefined,
  storage: DraftStorage = window.localStorage,
): TaskDraftRecord | null {
  if (!taskId) return null
  try {
    const raw = storage.getItem(getDraftStorageKey(taskId))
    return raw ? (JSON.parse(raw) as TaskDraftRecord) : null
  } catch {
    return null
  }
}

export function writeDraft(
  taskId: string | number | undefined,
  payload: TaskDraftRecord,
  storage: DraftStorage = window.localStorage,
): void {
  if (!taskId) return
  try {
    storage.setItem(getDraftStorageKey(taskId), JSON.stringify(payload))
  } catch {
    /* quota errors */
  }
}

export function mergeDraft(
  taskId: string | number | undefined,
  partial: TaskDraftRecord,
  storage: DraftStorage = window.localStorage,
): void {
  const stored = readDraft(taskId, storage)
  writeDraft(
    taskId,
    {
      ...(stored && typeof stored === "object" ? stored : {}),
      ...partial,
    },
    storage,
  )
}

/** Returns draft only when taskSignature matches current task shape. */
export function resolveDraftForTask(
  storedDraft: TaskDraftRecord | null | undefined,
  task: TaskDto | null | undefined,
): TaskDraftRecord | null {
  if (!task) return null
  const taskSignature = getTaskDraftSignature(task)
  return storedDraft?.taskSignature === taskSignature ? storedDraft : null
}

export function buildDraftPayload(
  task: TaskDto,
  fields: Omit<TaskDraftRecord, "taskSignature" | "flowDraftKey">,
): TaskDraftRecord {
  return {
    taskSignature: getTaskDraftSignature(task),
    flowDraftKey: getFlowDraftKey(task),
    ...fields,
  }
}
