import { getAssignmentEditorMode } from "@/features/task-editor/domain/assignmentRules"
import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { TaskType } from "@/features/task-editor/domain/enums"

export type EditorActivityKind = "assemble" | "implement" | "debug"

export const EDITOR_ACTIVITY_OPTIONS: Array<{ kind: EditorActivityKind; label: string }> = [
  { kind: "assemble", label: "Собрать" },
  { kind: "implement", label: "Написать" },
  { kind: "debug", label: "Исправить" },
]

export function resolveEditorActivityKind(
  draft: Pick<TaskDraft, "type" | "isDebugTask">,
): EditorActivityKind {
  if (draft.isDebugTask) return "debug"
  if (getAssignmentEditorMode(draft.type) === "blocks") return "assemble"
  return "implement"
}

export function patchDraftForEditorActivity(kind: EditorActivityKind): Partial<TaskDraft> {
  switch (kind) {
    case "assemble":
      return { type: TaskType.BUILD_FROM_BLOCKS, isDebugTask: false }
    case "implement":
      return { type: TaskType.TRANSLATE_FULL_PROGRAM, isDebugTask: false }
    case "debug":
      return { type: TaskType.TRANSLATE_FULL_PROGRAM, isDebugTask: true }
  }
}

/** True when teacher selected «Исправить» in the task type dropdown. */
export function isEditorFixActivity(draft: Pick<TaskDraft, "type" | "isDebugTask">): boolean {
  return resolveEditorActivityKind(draft) === "debug"
}
