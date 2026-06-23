import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { toAssignmentTypeId } from "@/shared/types/taskLabels"

const DEFAULT_ALLOWED_BLOCKS = [
  "start",
  "input",
  "process",
  "decision",
  "loop",
  "output",
  "end",
]

export function hasFlowchartDiagram(draft: TaskDraft): boolean {
  const nodes = draft.flow?.nodes ?? []
  return Array.isArray(nodes) && nodes.length > 0
}

export function buildFlowchartApiFields(draft: TaskDraft) {
  const language = draft.languages[0] ?? draft.code.language
  const referenceCode = draft.code.code?.trim() ?? ""
  const exposeReferenceCode = Boolean(draft.flowchartExposeReferenceCode && referenceCode)

  const flow_spec: Record<string, unknown> = {
    allowed_blocks: DEFAULT_ALLOWED_BLOCKS,
  }
  if (exposeReferenceCode) {
    flow_spec.student_reference_languages = [language]
  }

  return {
    diagram: draft.flow ?? { flow: [], nodes: [], edges: [] },
    flow_spec,
    reference_code: referenceCode,
    expose_reference_code: exposeReferenceCode,
    language,
    task_type: toAssignmentTypeId(String(draft.type || "")),
  }
}
