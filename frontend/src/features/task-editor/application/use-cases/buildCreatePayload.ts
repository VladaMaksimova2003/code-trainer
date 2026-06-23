import type { CreateTaskPayload, TaskDraft } from "@/features/task-editor/domain/entities"
import { TaskType } from "@/features/task-editor/domain/enums"
import { serializeIoValueForTestCase } from "@/features/task-editor/domain/ioValue"
import { getAssignmentEditorMode } from "@/features/task-editor/domain/assignmentRules"
import { buildBlockTaskApiFields } from "@/features/task-editor/application/use-cases/buildBlockTaskPayload"
import { buildFlowchartApiFields } from "@/features/task-editor/application/use-cases/buildFlowchartApiFields"

export function buildCreateTaskPayload(draft: TaskDraft): CreateTaskPayload {
  const codeText = draft.code.code

  const patterns = draft.selectedPatterns
    .filter((p) => p.approved !== false)
    .map((p) => String(p.id))

  return {
    title: draft.title.trim(),
    description: draft.description.trim(),
    type: draft.type,
    difficulty: draft.difficulty,
    languages: draft.languages,
    patterns,
    testCases: draft.testCases,
    ioSchema: draft.ioSchema,
    flow: draft.flow,
    code: codeText,
    content: draft.content,
    programSituation: draft.programSituation,
  }
}

export function buildAssignmentApiPayload(draft: TaskDraft) {
  const payload = buildCreateTaskPayload(draft)
  const apiPayload: Record<string, unknown> = {
    io_schema: {
      input_format: payload.ioSchema.inputFormat,
      output_format: payload.ioSchema.outputFormat,
    },
  }

  const mode = getAssignmentEditorMode(payload.type)

  if (mode === "blocks") {
    Object.assign(apiPayload, buildBlockTaskApiFields(draft))
  } else if (mode === "flowchart") {
    Object.assign(apiPayload, buildFlowchartApiFields(draft))
  } else if (
    payload.type === TaskType.TRANSLATE_SNIPPET ||
    payload.type === TaskType.TRANSLATE_FULL_PROGRAM
  ) {
    apiPayload.source_code = payload.code
    apiPayload.content = payload.content
    apiPayload.program_situation = payload.programSituation
  } else {
    apiPayload.original_code = payload.code
    apiPayload.content = payload.content
    apiPayload.program_situation = payload.programSituation
  }

  return {
    assignment_type: payload.type,
    difficulty: payload.difficulty,
    languages: payload.languages,
    title: payload.title,
    description: payload.description,
    patterns: payload.patterns,
    test_cases: payload.testCases.map((tc, index) => ({
      name: tc.name || `Тест ${index + 1}`,
      inputs: serializeIoValueForTestCase(tc.input),
      output: serializeIoValueForTestCase(tc.expectedOutput),
      description: tc.description,
    })),
    payload: {
      ...apiPayload,
      catalog_id: draft.catalogId ?? null,
    },
  }
}
